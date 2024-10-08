import copy
import logging
import numpy as np
import multiprocessing

from typing import List, Tuple
from collections import namedtuple

from packutils.data.bin import Bin
from packutils.data.grouped_item import (
    GroupedItem,
    ItemGroupingMode,
    group_items_horizontally,
    group_items_lengthwise,
)
from packutils.data.item import Item
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.position import Position
from packutils.data.single_item import SingleItem
from packutils.data.packing_variant import PackingVariant
from packutils.solver.abstract_packer import AbstractPacker
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration

PACKER_AVAILABLE = True

ScoredVariant = namedtuple("ScoredVariant", ["variant", "score"])


class PalletierWishPacker(AbstractPacker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.safety_distance_smaller_articles = kwargs.get(
            "safety_distance_smaller_articles", 0
        )
        self.min_article_width_no_safety_distance = kwargs.get(
            "min_article_width_no_safety_distance", 999999
        )

        self.safety_distance_lengthwise = kwargs.get("safety_distance_lengthwise", 0)

        self.reset(None)

    def reset(self, config: "PackerConfiguration | None"):
        if config is None or not isinstance(config, PackerConfiguration):
            config = PackerConfiguration()
        # logging.info("Used packer config: " + str(config))
        self.config = config

        # not implemented yet
        self.allow_rotation = False  # kwargs.get("rotation", False)

        self.snappoint_direction = SnappointDirection.RIGHT

        self.prev_item = None

        self.reference_bins = [
            Bin(
                width=b.width,
                length=b.length,
                height=b.height,
                max_length=b.max_length,
                max_weight=b.max_weight,
                stability_factor=config.bin_stability_factor,
                overhang_y_stability_factor=config.overhang_y_stability_factor,
            )
            for b in self.reference_bins
        ]

    def get_params(self) -> dict:
        return {}

    def pack_variants(
        self, order: Order, configs: List[PackerConfiguration]
    ) -> List[PackingVariant]:
        variants = []

        _order = copy.deepcopy(order)

        default_config = PackerConfiguration()
        default_config.mirror_walls = any([c.mirror_walls for c in configs])

        # check if a article can fill a complete bin
        additional_bins = []
        for article in _order.articles:
            if self.can_fill_complete_bin(article):
                bins = self.pack_complete_bin(article, default_config)
                additional_bins.extend(bins)
                packed = sum([len(b.packed_items) for b in bins])
                article.amount -= packed

        for config in configs:
            logging.info(f"Using config: {config}")
            variant = self.pack_variant(_order, config)
            if variant is not None:
                variants.append(variant)
                for b in additional_bins:
                    variant.add_bin(b)

        if len(variants) < 1:
            variant = PackingVariant()
            for b in additional_bins:
                variant.add_bin(b)
            variants.append(variant)

        return variants

    def get_max_articles_for_bin(self, bin: Bin, article: Article) -> int:
        """
        Get the maximum amount of articles that can be packed into a bin.

        Args:
            bin (Bin): The bin to pack the articles into.
            article (Article): The article to pack.

        Returns:
            int: The maximum amount of articles that can be packed into the bin.
        """
        bin_width = self.reference_bins[0].width
        bin_height = self.reference_bins[0].height
        bin_max_weight = self.reference_bins[0].max_weight

        max_articles_in_row = bin_width // article.width
        max_rows = bin_height // article.height

        return min(max_articles_in_row * max_rows, (bin_max_weight // article.weight if article.weight > 0 else 10000))

    def can_fill_complete_bin(self, article: Article) -> bool:
        """
        Check if a article can fill a complete bin.

        Args:
            article (Article): The article to check.

        Returns:
            bool: True if the article can fill the bin, False otherwise.
        """
        max_articles = self.get_max_articles_for_bin(self.reference_bins[0], article)

        return article.amount >= max_articles

    def pack_complete_bin(self, article: Article, config: PackerConfiguration) -> List[Bin]:
        """
        Pack a complete bin with a single article.

        Args:
            article (Article): The article to pack the bin with.

        Returns:
            List[Bin]: The list of bins filled with the article.
        """
        _article = copy.deepcopy(article)

        bins = []

        max_articles_per_bin = self.get_max_articles_for_bin(self.reference_bins[0], _article)
        n_bins = _article.amount // max_articles_per_bin

        _article.amount = max_articles_per_bin

        variant = self.pack_variant(Order("", articles=[_article]), config)
        return [variant.bins[0] for _ in range(n_bins)]

    def prepare_items_to_pack(
        self, order: Order, config: PackerConfiguration = None
    ) -> List[Item]:
        """
        Prepare the items to be packed based on the given order and configuration.

        Args:
            order (Order): The order to be packed.
            config (PackerConfiguration, optional): The configuration to use for packing. Defaults to None.

        Returns:
            List[Item]: The items to be packed.
        """

        items_to_pack = [
            SingleItem(
                identifier=a.article_id,
                width=a.width + (config.padding_between_items_x if config is not None else 0),
                length=a.length,
                height=a.height,
                weight=a.weight,
            )
            for a in order.articles
            for _ in range(a.amount)
        ]

        if config is None:
            return items_to_pack

        # group items lengthwise
        if config.item_grouping_mode == ItemGroupingMode.LENGTHWISE:
            allowed_length = self.reference_bins[0].max_length

            groupable_items = [
                item for item in items_to_pack if item.length < allowed_length
            ]

            while len(groupable_items) > 0:
                current_item = groupable_items[0]
                same_items = [
                    item
                    for item in groupable_items
                    if (item.width, item.height)
                    == (current_item.width, current_item.height)
                ]

                if len(same_items) < 2:
                    groupable_items.remove(current_item)
                    continue

                item_group = []
                item_group_length = 0
                for item in same_items:
                    if item_group_length + item.length <= allowed_length:
                        item_group.append(item)
                        item_group_length += item.length + self.safety_distance_lengthwise
                        groupable_items.remove(item)

                for item in item_group:
                    items_to_pack.remove(item)
                items_to_pack.append(
                    group_items_lengthwise(
                        item_group, padding_between_items=self.safety_distance_lengthwise
                    )
                )

        # group items horizontally
        if config.group_narrow_items_w > 0:
            groupable_items = [
                item
                for item in items_to_pack
                if item.width <= config.group_narrow_items_w
            ]

            while len(groupable_items) > 0:
                current_item = groupable_items.pop(0)
                same_items = [
                    item
                    for item in groupable_items
                    if (item.length, item.height)
                    == (current_item.length, current_item.height)
                ]

                if len(same_items) < 1:
                    continue
                same_item = same_items[0]
                groupable_items.remove(same_item)

                item_group = [current_item, same_item]
                for item in item_group:
                    items_to_pack.remove(item)

                items_to_pack.append(
                    group_items_horizontally(item_group, padding_between_items=0)
                )

        return items_to_pack

    def pack_variant(
        self, order: Order, config: PackerConfiguration = None
    ) -> "PackingVariant | None":
        items_to_pack = self.prepare_items_to_pack(order, config)
        self.reset(config)
        return self._pack_variant(items_to_pack)

    def _pack_variant(self, items: List[Item]) -> "PackingVariant | None":
        variant = PackingVariant()
        items_to_pack = copy.deepcopy(items)
        for bin_index, bin in enumerate(copy.deepcopy(self.reference_bins)):

            logging.info("-" * 20 + f" Bin {bin_index+1}")
            snappoints_to_ignore = []
            layer_z_max = bin.height

            is_packing = True
            while is_packing:
                if len(items_to_pack) < 1:
                    is_packing = False
                    break

                is_new_layer = layer_z_max == bin.height

                snappoints = [
                    point
                    for point in bin.get_snappoints()
                    if not point in snappoints_to_ignore and point.z < layer_z_max
                ]

                # no snappoint available
                if len(snappoints) < 2:
                    # reached top of the bin or no possible positions left
                    if layer_z_max == bin.height:
                        is_packing = False
                        logging.info("There are no possible positions left.")

                    else:
                        logging.info(f"Starting next layer! ({layer_z_max})")

                        # if self.fill_gaps:
                        #    self._fill_gaps(bin, layer_z_min)
                        snappoints_to_ignore = []
                        layer_z_max = bin.height
                    continue

                if is_new_layer:
                    self.snappoint_direction = SnappointDirection.RIGHT

                    sorted_points = sorted(snappoints, key=lambda p: p.x)

                    # check if the first snappoint is at the edge of the bin
                    if sorted_points[0].x != 0 and layer_z_max == bin.height:
                        logging.info("First snappoint is not at the edge of the bin.")
                        is_packing = False
                        break

                else:
                    sorted_points = sorted(snappoints, key=lambda p: (p.z, p.x))

                left_snappoint = [
                    p for p in sorted_points if p.direction == SnappointDirection.RIGHT
                ][0]
                right_snappoint = [
                    p for p in sorted_points if p.direction == SnappointDirection.LEFT
                ][0]

                logging.info("")
                logging.info(
                    f"Selected snappoints: {left_snappoint}, {right_snappoint}"
                )

                snappoint = (
                    right_snappoint
                    if self.snappoint_direction == SnappointDirection.LEFT
                    else left_snappoint
                )
                logging.info(f"Selected snappoint: {snappoint}")

                allowed_max_z = (
                    bin.height if self.config.allow_item_exceeds_layer else layer_z_max
                )
                best = self.get_best_item_to_pack(
                    items_to_pack, bin, snappoint, allowed_max_z
                )
                logging.info(f"Item to pack: {best}")

                if best is None:
                    # if self.config.mirror_walls and snappoint.x == 0:
                    #    is_packing = False
                    #    break

                    logging.info(
                        f"This snappoint is invalid, checking other snappoint. {snappoint}"
                    )
                    snappoints_to_ignore.append(snappoint)
                    snappoint = (
                        right_snappoint
                        if snappoint == left_snappoint
                        else left_snappoint
                    )
                    best = self.get_best_item_to_pack(
                        items_to_pack, bin, snappoint, allowed_max_z
                    )

                if best is None:
                    logging.info(f"This snappoint is invalid too. {snappoint}")
                    snappoints_to_ignore.append(snappoint)
                    continue

                done, _ = self.pack_item_on_snappoint(
                    bin=bin, item=best, snappoint=snappoint
                )

                if not done:
                    continue

                layer_z_max = bin.max_z
                items_to_pack.remove(best)
                snappoints_to_ignore = []

                # check if the placement can be mirrored
                if self.config.mirror_walls and snappoint.x == 0:
                    logging.info("Mirroring walls")

                    mirror_snappoint = Snappoint(
                        x=bin.width,
                        y=snappoint.y,
                        z=snappoint.z,
                        direction=SnappointDirection.LEFT,
                    )
                    mirror_item = get_item_with_dimension(
                        items_to_pack, best.dimensions
                    )
                    if mirror_item is not None:
                        logging.info("No item with same dimensions found.")

                        done, _ = self.pack_item_on_snappoint(
                            bin=bin, item=mirror_item, snappoint=mirror_snappoint
                        )
                        if done:
                            items_to_pack.remove(mirror_item)

            if len(bin.packed_items) > 0:
                if self.config.remove_gaps:
                    bin.remove_gaps()
                variant.add_bin(bin)

        for item in items_to_pack:
            variant.add_unpacked_item(item, None)

        return variant

    def _get_variant_score(self, variant: PackingVariant):
        return 0

    def pack_item_on_snappoint(self, bin: Bin, item: Item, snappoint: Snappoint) -> int:
        """
        Pack an item on a given snappoint of a bin.

        Args:
            bin (Bin): The bin to pack the item into.
            item (Item): The item to be packed.
            snappoint (Snappoint): The snappoint on the bin to pack the item on.

        Returns:
            bool: True if the item could be packed, False otherwise.
            int: The new maximum z value of the bin.
        """

        item = copy.deepcopy(item)
        if snappoint.direction == SnappointDirection.LEFT:
            position = Position(snappoint.x - item.width, snappoint.y, snappoint.z)

        if snappoint.direction == SnappointDirection.RIGHT:
            position = Position(snappoint.x, snappoint.y, snappoint.z)

        if is_safety_distance_required(
            item,
            position,
            bin,
            self.safety_distance_smaller_articles,
            self.min_article_width_no_safety_distance,
        ):
            position.x += self.safety_distance_smaller_articles

        done, info = bin.pack_item(item, position)
        if info is not None:
            logging.info(f"{info} - {item}")
        if done:
            logging.info(f"Packed item {item}")
            self.prev_item = item
            if item.volume / bin.volume >= self.config.direction_change_min_volume:
                self.snappoint_direction = self.snappoint_direction.change()
                logging.info(f"New snappoint direction: {self.snappoint_direction}")

            new_z_max = position.z + item.height
            return done, new_z_max

        return done, None

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE

    def get_best_item_to_pack(
        self, items: List[Item], bin: Bin, snappoint: Snappoint, max_z: int
    ) -> "Item | None":
        """
        Get the best item to pack based on the given constraints.

        Args:
            items (List[Item]): List of items to be packed.
            bin (Bin): The bin to pack the items into.
            snappoint (Snappoint): The snappoint to pack the item on.
            max_z (int): The maximum z value for the item.

        Returns:
            Item: The best item to pack or None if no item can be packed.
        """

        if self.config.mirror_walls and snappoint.x == 0:
            mirror_snappoint = Snappoint(
                x=bin.width,
                y=snappoint.y,
                z=snappoint.z,
                direction=SnappointDirection.LEFT,
            )
            possible_items = [
                copy.deepcopy(item)
                for item in items
                if can_pack_on_snappoint(bin, item, snappoint, max_z)
                and can_pack_on_snappoint(bin, item, mirror_snappoint, max_z)
            ]
        else:
            possible_items = [
                copy.deepcopy(item)
                for item in items
                if can_pack_on_snappoint(bin, item, snappoint, max_z)
            ]

        if self.safety_distance_smaller_articles > 0:
            for item in [
                i
                for i in possible_items
                if is_safety_distance_required(
                    i,
                    snappoint,
                    bin,
                    self.safety_distance_smaller_articles,
                    self.min_article_width_no_safety_distance,
                )
            ]:
                larger_item = copy.deepcopy(item)
                larger_item.width += self.safety_distance_smaller_articles
                if not can_pack_on_snappoint(bin, larger_item, snappoint, max_z):
                    possible_items.remove(item)

        if len(possible_items) < 1:
            return None

        new_layer_item = select_item_from_list(
            possible_items, self.config.new_layer_select_strategy, None
        )

        is_new_layer = not np.any(bin.heightmap > snappoint.z)
        if is_new_layer:
            return new_layer_item

        # save two items for the next layer
        only_two_left = count_same_dimensions(possible_items, new_layer_item) == 2
        if self.config.mirror_walls and only_two_left:
            doubled_item_w = copy.deepcopy(new_layer_item)
            doubled_item_w.width *= 2

            doubled_item_h = copy.deepcopy(new_layer_item)
            doubled_item_h.height *= 2
            can_both_fit = can_fit_in_layer(
                bin, doubled_item_w, snappoint.z, max_z
            ) or can_fit_in_layer(bin, doubled_item_w, snappoint.z, max_z)

            if not can_both_fit:
                possible_items.remove(new_layer_item)
                same_item = get_item_with_dimension(
                    possible_items, new_layer_item.dimensions
                )
                possible_items.remove(same_item)

        next_item = select_item_from_list(
            possible_items, self.config.default_select_strategy, self.prev_item
        )
        return next_item


## Helper functions


def is_safety_distance_required(
    item: Item,
    snappoint: "Position|Snappoint",
    bin: Bin,
    safety_distance: int,
    min_article_width_no_safety_distance: int,
) -> bool:
    """
    Determines whether a safety distance is required for an item at a given snappoint in a bin.

    Args:
        item (Item): The item to check for.
        snappoint (Snappoint): The snappoint to place the item.
        bin (Bin): The bin to pack the item into.
        safety_distance (int): The safety distance to check for.
        min_article_width_no_safety_distance (int): The minimum width of an article without a safety distance.

    Returns:
        bool: True if a safety distance is required, False otherwise.
    """
    if safety_distance < 1:
        return False

    if item.width >= min_article_width_no_safety_distance:
        return False

    if isinstance(snappoint, Snappoint):
        position = (
            Position(snappoint.x, snappoint.y, snappoint.z)
            if snappoint.direction == SnappointDirection.RIGHT
            else Position(snappoint.x - item.width, snappoint.y, snappoint.z)
        )
    else:
        position = snappoint

    if position.x < 1:
        return False

    maxY = max(bin.heightmap[max(0, position.x - safety_distance) : position.x])

    return maxY > position.z + item.height


def can_fit_in_layer(bin: Bin, item: Item, min_z: int, max_z: int):
    """
    Checks whether an item can be packed in a layer of a bin.

    Args:
        bin (Bin): The bin to pack the item into.
        item (Item): The item to be packed.
        min_z (int): The minimum z value of the layer.
        max_z (int): The maximum z value of the layer.

    Returns:
        bool: True if the item can be packed in the layer, False otherwise.
    """

    snappoints = [p for p in bin.get_snappoints() if p.z == min_z]

    for point in snappoints:
        if can_pack_on_snappoint(bin, item, point, max_z):
            return True
    return False


def can_pack_on_snappoint(
    bin: Bin, item: Item, snappoint: Snappoint, max_z: int
) -> bool:
    """
    Determines whether an item can be packed on a given snappoint of a bin.

    Args:
        bin (Bin): The bin to pack the item into.
        item (Item): The item to be packed.
        snappoint (Snappoint): The snappoint on the bin to pack the item on.
        max_z (int): The maximum height allowed for the packed item.

    Returns:
        bool: True if the item can be packed on the snappoint, False otherwise.
    """
    
    item = copy.deepcopy(item)
    if snappoint.direction == SnappointDirection.LEFT:
        position = Position(snappoint.x - item.width, snappoint.y, snappoint.z)

    if snappoint.direction == SnappointDirection.RIGHT:
        position = Position(snappoint.x, snappoint.y, snappoint.z)

    can_be_packed, info = bin.can_item_be_packed(item, position)
    exceeds_height = item.height + snappoint.z > max_z if max_z is not None else False

    return can_be_packed and not exceeds_height


def get_item_with_dimension(items: List[Item], dims: "Tuple[int, int, int]"):
    """
    Get an item with the specified dimensions from a list of items.

    Args:
        items (List[Item]): The list of items to search from.
        dims (Tuple[int]): The dimensions (width, length, height) of the item to find.

    Returns:
        Item: The item with the specified dimensions, or None if not found.
    """
    items_same_dim = [item for item in items if item.dimensions == dims]
    if len(items_same_dim) < 1:
        return None

    return copy.deepcopy(items_same_dim[0])


def count_same_dimensions(items: List[Item], item: Item) -> int:
    """
    Counts the number of occurrences of items with the same dimensions as the given item.

    Args:
        items (List[Item]): The list of items to search in.
        item (Item): The item to count occurrences of.

    Returns:
        int: The number of occurrences of the item in the list.
    """
    same_dimensional_items = [i for i in items if i.dimensions == item.dimensions]
    return len(same_dimensional_items)


def select_item_from_list(
    items: List[Item],
    strategy: ItemSelectStrategy,
    prev_item: "Item | None",
) -> "Item | None":
    """
    Selects a item based on the specified strategy.

    Args:
        items (List[Item]): The list of items to select from.
        strategy (ItemSelectStrategy): The strategy to use for selecting the item.

    Returns:
        Item: The best item to pack or None if no item can be packed.
    """
    if len(items) < 1:
        return None
    """
    if prev_item is not None and count_same_dimensions(items, prev_item) > 0:
        same_dimensional_items = [
            i for i in items if i.dimensions == prev_item.dimensions
        ]
        return same_dimensional_items[0]
    """

    if strategy == ItemSelectStrategy.LARGEST_VOLUME:
        sorted_items = sorted(items, key=lambda x: x.volume, reverse=True)
        return sorted_items[0]

    if strategy == ItemSelectStrategy.LARGEST_H_W_L:
        sorted_items = sorted(
            items, key=lambda x: (x.height, x.width, x.length), reverse=True
        )
        return sorted_items[0]

    if strategy == ItemSelectStrategy.LARGEST_W_H_L:
        sorted_items = sorted(
            items, key=lambda x: (x.width, x.height, x.length), reverse=True
        )
        return sorted_items[0]

    if strategy == ItemSelectStrategy.LARGEST_L_H_W:
        sorted_items = sorted(
            items, key=lambda x: (x.length, x.height, x.width), reverse=True
        )
        return sorted_items[0]

    if strategy == ItemSelectStrategy.LARGEST_L_W_H:
        sorted_items = sorted(
            items, key=lambda x: (x.length, x.width, x.height), reverse=True
        )
        return sorted_items[0]

    if strategy == ItemSelectStrategy.LARGEST_W_TO_FILL:
        unique_items = set(items)
        largest_w = 0
        best_item = None

        for item in unique_items:
            item_count = count_same_dimensions(items, item)
            if item_count * item.width > largest_w:
                largest_w = item_count * item.width
                best_item = item
        return best_item

    if strategy == ItemSelectStrategy.LARGEST_W_H_TO_FILL:
        unique_items = set(items)
        largest_w_h = 0
        best_item = None

        for item in unique_items:
            item_count = count_same_dimensions(items, item)
            if item_count * item.width * item.height > largest_w_h:
                largest_w_h = item_count * item.width * item.height
                best_item = item
        return best_item

    raise NotImplementedError(f"ItemSelectStrategy not implemented: {strategy}")
