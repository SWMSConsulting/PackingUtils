import copy
import logging
import numpy as np
import collections
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

ScoredVariant = collections.namedtuple('ScoredVariant', ["variant", "score"])
Layer = collections.namedtuple('Layer', ['height', 'score'])


class LayerScoreStrategy(Enum):
    # for each layer candidate loop over the items and sum the absolute height differnce between item and layer
    MIN_HEIGHT_VARIANCE = 0


class PalletierWishPacker(AbstractPacker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.reset(None)

    def reset(self, config: 'PackerConfiguration | None'):
        if config is None or not isinstance(config, PackerConfiguration):
            config = PackerConfiguration()

        logging.info("Used packer config: " + str(config))
        self.config = config
        # not implemented yet
        self.allow_rotation = False  # kwargs.get("rotation", False)

        # not relevant, this was regarding to the vertical layers
        self.layer_score_strategy = LayerScoreStrategy.MIN_HEIGHT_VARIANCE

        # if a layer is closed, fill the gaps
        self.fill_gaps = False  # kwargs.get("fill_gaps", False)

        # if a new layer is opened, allow snappoints where overhang can occurr
        self.allow_overhang = True  # kwargs.get("allow_overhang", True)

        self.snappoint_direction = SnappointDirection.LEFT

    def get_params(self) -> dict:
        return {}

    def pack_variants(self, order: Order, configs: List[PackerConfiguration]) -> List[PackingVariant]:
        variants = []
        for config in configs:
            variants.append(self.pack_variant(order, config))
        return variants

    def pack_variant(self, order: Order, config: PackerConfiguration = None) -> 'PackingVariant | None':
        self.reset(config)

        items_to_pack = [
            Item(id=a.article_id, width=a.width,
                 length=a.length, height=a.height)
            for a in order.articles for _ in range(a.amount)
        ]

        variant = self._pack_variant(items_to_pack)
        return variant

    def _pack_variant(self,  items: List[Item]) -> PackingVariant:

        variant = PackingVariant()
        items_to_pack = copy.copy(items)
        for bin_index, bin in enumerate(copy.copy(self.reference_bins)):
            bin.stability_factor = self.config.bin_stability_factor
            logging.info("-"*20 + f" Bin {bin_index+1}")
            snappoints_to_ignore = []
            layer_z_min = 0
            layer_z_max = 0

            is_packing = True
            while is_packing:
                if len(items_to_pack) < 1:
                    is_packing = False

                max_snappoint_z = layer_z_max if layer_z_max != layer_z_min else bin.height
                snappoints = [point for point in bin.get_snappoints(min_z=layer_z_min)
                              if not point in snappoints_to_ignore and point.z <= max_snappoint_z]

                sorted_points = sorted(snappoints, key=lambda p: (p.z, p.x))
                # no snappoint available
                if len(sorted_points) < 2:
                    # reached top of the bin or no possible positions left
                    if layer_z_max == bin.height or layer_z_min == layer_z_max:
                        is_packing = False
                        logging.info(
                            "There are no possible positions left.")

                    else:
                        logging.info(
                            f"Starting next layer! ({layer_z_min, layer_z_max})")

                        if self.fill_gaps:
                            self._fill_gaps(bin, layer_z_min)
                        layer_z_min = layer_z_max
                    continue

                left_snappoint = [
                    p for p in sorted_points if p.direction == SnappointDirection.RIGHT][0]
                right_snappoint = [
                    p for p in sorted_points if p.direction == SnappointDirection.LEFT][0]

                logging.info("")
                logging.info("Selected snappoints: " +
                             str(left_snappoint) + ", " + str(right_snappoint))

                if self.snappoint_direction == SnappointDirection.LEFT:
                    snappoint = left_snappoint
                if self.snappoint_direction == SnappointDirection.RIGHT:
                    snappoint = right_snappoint
                logging.info(f"Selected snappoint: {snappoint}")

                unique_items = set(items_to_pack)
                best = self.get_best_item_to_pack(unique_items, bin, snappoint)
                logging.info(f"Item to pack: {best}")

                if best is None:
                    logging.info(
                        "This snappoint is unstable, checking other snappoint.")
                    snappoint = right_snappoint if snappoint == left_snappoint else left_snappoint
                    best = self.get_best_item_to_pack(
                        unique_items, bin, snappoint)

                if best is None:
                    logging.info(
                        "No item to pack on snappoints - ignoring them.")
                    snappoints_to_ignore += [left_snappoint, right_snappoint]
                    continue

                done, new_z = self.pack_item_on_snappoint(
                    bin=bin, item=best, snappoint=snappoint)
                if new_z is not None and new_z > layer_z_max:
                    layer_z_max = new_z

                if done:
                    items_to_pack.remove(best)
                    snappoints_to_ignore = []
                else:
                    logging.info(
                        "Failed to pack item - ignoring snappoints.")
                    snappoints_to_ignore += [left_snappoint, right_snappoint]

            if len(bin.packed_items) > 0:
                variant.add_bin(bin)

        for item in items_to_pack:
            variant.add_unpacked_item(item, None)

        return variant

    def _get_variant_score(self, variant: PackingVariant):
        return 0

    def can_pack_on_snappoint(
            self, bin: Bin, item: Item, snappoint: Snappoint) -> int:

        item = copy.copy(item)
        if snappoint.direction == SnappointDirection.LEFT:
            position = Position(snappoint.x - item.width,
                                snappoint.y, snappoint.z)

        if snappoint.direction == SnappointDirection.RIGHT:
            position = Position(snappoint.x, snappoint.y, snappoint.z)

        item.position = position
        can_be_packed, info = bin.can_item_be_packed(item)

        return can_be_packed

    def pack_item_on_snappoint(
            self, bin: Bin, item: Item, snappoint: Snappoint) -> int:

        item = copy.copy(item)
        if snappoint.direction == SnappointDirection.LEFT:
            position = Position(snappoint.x - item.width,
                                snappoint.y, snappoint.z)

        if snappoint.direction == SnappointDirection.RIGHT:
            position = Position(snappoint.x, snappoint.y, snappoint.z)

        item.position = position
        done, info = bin.pack_item(item)
        if info is not None:
            logging.info(f"{info} - {item}")
        if done:
            logging.info(f"Packed item {item}")
            if item.volume / bin.volume >= self.config.direction_change_min_volume:
                self.snappoint_direction = self.snappoint_direction.change()
                logging.info(
                    f"New snappoint direction: {self.snappoint_direction}")

            new_z_max = position.z + item.height
            return done, new_z_max

        return done, None

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE

    def get_best_item_to_pack(
        self, items: List[Item], bin: Bin, snappoint: Snappoint
    ) -> 'Item | None':
        """
        Get the best item to pack based on the given constraints.

        Args:

        """
        items = [copy.deepcopy(item) for item in set(items) if self.can_pack_on_snappoint(
            bin, item, snappoint)]

        if len(items) < 1:
            return None

        is_new_layer = not np.any(bin.get_height_map() > snappoint.z)
        if self.config.item_select_strategy == ItemSelectStrategy.HIGHEST_VOLUME_FOR_EMPTY_LAYER and is_new_layer or self.config.item_select_strategy == ItemSelectStrategy.ALWAYS_HIGHEST_VOLUME:
            sorted_items = sorted(items, key=lambda x: x.volume, reverse=True)
            return sorted_items[0]

        layer_height = np.max(bin.get_height_map())
        layer_height = bin.height - snappoint.z if layer_height <= snappoint.z else layer_height
        items_fit_layer_height = [
            item for item in items if item.height <= layer_height - snappoint.z]

        if len(items_fit_layer_height) > 0:
            # take the largest item fitting the gap
            sorted_items = sorted(items_fit_layer_height, key=lambda x: (
                x.length, x.width, x.height - layer_height), reverse=True)
            return sorted_items[0]

        # take the item with minimal layer height change but the largest possible
        sorted_items = sorted(items, key=lambda x: (
            x.height - layer_height, x.length, x.width), reverse=True)
        return sorted_items[0]

    def _get_item_with_dimension(self, items: List[Item], dims: Tuple[int]):
        items_same_dim = [item for item in items
                          if (item.width, item.length, item.height) == dims]
        if len(items_same_dim) < 1:
            return None

        return copy.copy(items_same_dim[0])

    def get_candidate_layers(self, items, dimension: str = "height") -> List[Layer]:
        """
        Generate candidate layers based on the heights of the items.

        Args:
            items (List[Item]): List of items to be packed.

        Returns:
            List[Layer]: Sorted list of candidate layers based on score.
        """
        candidates = []
        for item in items:
            # add the rotation here
            if dimension == "height":
                dim = item.height
            candidates.append(dim)

        layers = []
        for candidate in set(candidates):

            if self.layer_score_strategy == LayerScoreStrategy.MIN_HEIGHT_VARIANCE:
                # negative sum of the height differences (larger sum -> heigher score)
                score = - sum(abs(candidate - item.height) for item in items)

            elif self.layer_score_strategy == LayerScoreStrategy.MIN_HEIGHT_VARIANCE:
                # sum of all item surfaces with the same height
                score = sum([
                    item.surface for item in items if item.height == candidate])

            else:
                raise NotImplementedError(
                    f"LayerScoreStrategy not implemented: {self.layer_score_strategy}")
            layers.append(Layer(candidate, score))

        layers = sorted(layers, key=lambda x: x.score, reverse=True)
        return layers

    def _fill_gaps(self, bin: Bin, min_z: int):
        # detect the gap
        heightmap = bin.get_height_map() - min_z

        total_gap_width = np.count_nonzero(heightmap == 0)
        if total_gap_width <= 0:
            return False

        left_space = int(total_gap_width / 2)

        # get all items of the layer
        items_to_move = [
            item for item in bin.packed_items if item.position.z >= min_z]
        if len(items_to_move) < 1:
            return False

        # this does not work for larger stacks to move (use prev approach with items left and right of gap)
        for item in items_to_move:
            bin.packed_items.remove(item)
            bin.matrix[min_z:, :, :] = 0

        items_to_move = sorted(
            items_to_move, key=lambda x: (x.position.z, x.position.x))
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
