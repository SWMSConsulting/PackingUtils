import copy
import logging
import time
import numpy as np
import collections
import multiprocessing
from enum import Enum
from typing import List, Tuple

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.order import Order
from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration
from packutils.data.packing_variant import PackingVariant
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.solver.abstract_packer import AbstractPacker

PACKER_AVAILABLE = True

ScoredVariant = collections.namedtuple("ScoredVariant", ["variant", "score"])
Layer = collections.namedtuple("Layer", ["height", "score"])


class LayerScoreStrategy(Enum):
    # for each layer candidate loop over the items and sum the absolute height differnce between item and layer
    MIN_HEIGHT_VARIANCE = 0


class PalletierWishPacker(AbstractPacker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def get_params(self) -> dict:
        return {}

    def pack_variants(
        self, order: Order, configs: List[PackerConfiguration]
    ) -> List[PackingVariant]:
        variants = []
        for config in configs:
            logging.info(f"Using config: {config}")
            variants.append(self.pack_variant(order, config))
        return variants

    def pack_variant(
        self, order: Order, config: PackerConfiguration = None
    ) -> "PackingVariant | None":
        self.reset(config)

        items_to_pack = [
            Item(
                id=a.article_id,
                width=a.width + config.padding_x,
                length=a.length,
                height=a.height,
            )
            for a in order.articles
            for _ in range(a.amount)
        ]

        variant = self._pack_variant(items_to_pack)
        return variant

    def _pack_variant(self, items: List[Item]) -> PackingVariant:
        variant = PackingVariant()
        items_to_pack = copy.deepcopy(items)
        for bin_index, bin in enumerate(copy.deepcopy(self.reference_bins)):
            bin.stability_factor = self.config.bin_stability_factor
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

                if is_new_layer:
                    sorted_points = sorted(snappoints, key=lambda p: p.x)
                else:
                    sorted_points = sorted(snappoints, key=lambda p: (p.z, p.x))

                # no snappoint available
                if len(sorted_points) < 2:
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
                        self.snappoint_direction = SnappointDirection.RIGHT
                    continue

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

        item.position = position
        done, info = bin.pack_item(item)
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

        possible_items = [
            copy.deepcopy(item)
            for item in items
            if can_pack_on_snappoint(bin, item, snappoint, max_z)
        ]

        if len(possible_items) < 1:
            return None

        new_layer_item = select_item_from_list(
            possible_items, self.config.new_layer_select_strategy, None
        )

        is_new_layer = not np.any(bin.get_height_map() > snappoint.z)
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
                possible_items.remove(new_layer_item)

        next_item = select_item_from_list(
            possible_items, self.config.default_select_strategy, self.prev_item
        )
        return next_item

    def _fill_gaps(self, bin: Bin, min_z: int):
        # detect the gap
        heightmap = bin.get_height_map() - min_z

        total_gap_width = np.count_nonzero(heightmap == 0)
        if total_gap_width <= 0:
            return False

        left_space = int(total_gap_width / 2)

        # get all items of the layer
        items_to_move = [item for item in bin.packed_items if item.position.z >= min_z]
        if len(items_to_move) < 1:
            return False

        # this does not work for larger stacks to move (use prev approach with items left and right of gap)
        for item in items_to_move:
            bin.packed_items.remove(item)
            bin.matrix[min_z:, :, :] = 0

        items_to_move = sorted(
            items_to_move, key=lambda x: (x.position.z, x.position.x)
        )
        current_x = left_space
        current_z = min_z
        for item in items_to_move:
            if current_z != item.position.z:
                current_z = item.position.z
                current_x = left_space

            item.position.x = current_x
            current_x += item.width
            done, info = bin.pack_item(item)
            if not done:
                logging.info(info, item)
        return True


## Helper functions


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

    item.position = position
    can_be_packed, _ = bin.can_item_be_packed(item)

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
