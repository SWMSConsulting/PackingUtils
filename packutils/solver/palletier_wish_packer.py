import collections
import copy
from enum import Enum
import logging
from typing import List, Tuple

import numpy as np

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.order import Order
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


class ItemSelectStrategy(Enum):
    # for each layer candidate loop over the items and sum the absolute height differnce between item and layer
    FITTING_BEST_Y_X_Z = 0
    HIGHEST_VOLUME_FOR_EMPTY_LAYER = 1
    ALWAYS_HIGHEST_VOLUME = 2


class PalletierWishPacker(AbstractPacker):

    snappoint_direction = SnappointDirection.LEFT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # not implemented yet
        self.allow_rotation = kwargs.get("rotation", False)

        # not relevant, this was regarding to the vertical layers
        self.layer_score_strategy = kwargs.get(
            "layer_score_strategy", LayerScoreStrategy.MIN_HEIGHT_VARIANCE)

        #
        self.item_select_strategy = kwargs.get(
            "item_select_strategy", ItemSelectStrategy.FITTING_BEST_Y_X_Z)

        # lambda function taking a item and returning a boolean indicating whether the snappoint direction should change
        self.direction_change_condition = kwargs.get(
            "direction_change_condition", None)

        # if a layer is closed, fill the gaps
        self.fill_gaps = kwargs.get("fill_gaps", False)

        # if a new layer is opened, allow snappoints where overhang can occurr
        self.allow_overhang = kwargs.get("allow_overhang", True)

    def get_params(self) -> dict:
        return {}

    def pack_variant(self, order: Order) -> 'PackingVariant | None':
        variant = PackingVariant()

        items_to_pack = [
            Item(id=a.article_id, width=a.width,
                 length=a.length, height=a.height)
            for a in order.articles for _ in range(a.amount)
        ]

        variants = self._pack_variants(items_to_pack)
        # failed to pack any variant
        if len(variants) < 1:
            variant = PackingVariant()
            for item in items_to_pack:
                variant.add_unpacked_item(item, None)
            return variant

        variants = sorted(variants, key=lambda x: x.score, reverse=True)
        best_variant = variants[0].variant
        return best_variant

    def _pack_variants(self, items: List[Item]) -> List[ScoredVariant]:
        all_variants = []

        variant = PackingVariant()
        items_to_pack = copy.copy(items)
        for bin_index, bin in enumerate(copy.copy(self.reference_bins)):

            snappoints_to_ignore = []
            layer_z_min = 0
            layer_z_max = 0

            is_packing = True
            while is_packing:
                if len(items_to_pack) < 1:
                    is_packing = False

                max_snappoint_z = layer_z_max if layer_z_max != layer_z_min else bin.height
                snappoints = [point for point in bin.get_snappoints(min_z=layer_z_min)
                              if not point in snappoints_to_ignore and point.z < max_snappoint_z]

                sorted_points = sorted(snappoints, key=lambda p: (p.z, p.x))
                # no snappoint available
                if len(sorted_points) < 2:
                    # reached top of the bin or no possible positions left
                    if layer_z_max == bin.height or layer_z_min == layer_z_max:
                        is_packing = False
                        logging.info(
                            "There are no possible positions left.")

                    else:
                        print(
                            f"Starting next layer! ({layer_z_min, layer_z_max})")

                        if self.fill_gaps:
                            self._fill_gaps(bin, layer_z_min)
                        layer_z_min = layer_z_max
                    continue

                left_snappoint = [
                    p for p in sorted_points if p.direction == SnappointDirection.RIGHT][0]
                right_snappoint = [
                    p for p in sorted_points if p.direction == SnappointDirection.LEFT][0]

                unique_items = set(items_to_pack)

                max_len_x = right_snappoint.x-left_snappoint.x
                max_len_z = bin.height - layer_z_min
                gap_len_z = layer_z_max - \
                    layer_z_min if layer_z_max != layer_z_min else max_len_z
                best, other_best = self.get_best_item_to_pack(
                    items=unique_items, bin_len_x=bin.width, max_len_x=max_len_x,
                    max_len_z=max_len_z, gap_len_z=gap_len_z)

                if best is None and other_best is None:
                    snappoints_to_ignore += [left_snappoint, right_snappoint]
                    continue

                if self.snappoint_direction == SnappointDirection.LEFT:
                    snappoint = left_snappoint
                if self.snappoint_direction == SnappointDirection.RIGHT:
                    snappoint = right_snappoint

                if best is not None:
                    item_to_pack = best
                elif other_best is not None:
                    item_to_pack = other_best

                items_to_pack.remove(item_to_pack)
                new_z = self.pack_item_on_snappoint(
                    bin=bin, item=item_to_pack, snappoint=snappoint)
                if new_z is not None and new_z > layer_z_max:
                    layer_z_max = new_z

            if len(bin.packed_items) > 0:
                variant.add_bin(bin)

        for item in items_to_pack:
            variant.add_unpacked_item(item, None)
        all_variants.append(variant)

        scored_variants = [
            ScoredVariant(variant, self._get_variant_score(variant)) for variant in all_variants
        ]

        return scored_variants

    def _get_variant_score(self, variant: PackingVariant):
        return 0

    def pack_item_on_snappoint(
            self, bin: Bin, item: Item, snappoint: Snappoint) -> int:

        if snappoint.direction == SnappointDirection.LEFT:
            position = Position(snappoint.x - item.width,
                                snappoint.y, snappoint.z)

        if snappoint.direction == SnappointDirection.RIGHT:
            position = Position(snappoint.x, snappoint.y, snappoint.z)

        item.position = position
        done, _ = bin.pack_item(item)

        if done:
            if self.direction_change_condition is not None and self.direction_change_condition(item):
                self.snappoint_direction = self.snappoint_direction.change()
                logging.info(
                    f"New snappoint direction: {self.snappoint_direction}")

            new_z_max = position.z + item.height
            return new_z_max

        return None

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE

    def get_best_item_to_pack(
        self, items,
        bin_len_x, max_len_x,
        max_len_z, gap_len_z,
        max_len_y=1, gap_len_y=1  # not relevant for now
    ):
        """
        Get the best item to pack based on the given constraints.

        Args:
            items (List[Item]): List of items to be considered for packing.
            max_len_x (float): Maximum length available along the x-axis.
            max_len_z (float): Maximum length available along the z-axis.
            gap_len_z (float): Gap length along the z-axis.
            max_len_y (float, optional): Maximum length available along the y-axis. Defaults to 1.
            gap_len_y (float, optional): Gap length along the y-axis. Defaults to 1.

        Returns:
            Tuple[Item, Item]: A tuple containing the best fit item with a lower height and the best fit item with a larger height than the gap.
        """
        unique_dims = set((item.width, item.length, item.height)
                          for item in items)

        dims_that_fit = []
        for dims in unique_dims:
            # you can include rotation here
            for w, l, h in [dims]:
                if w <= max_len_x and l <= max_len_y and h <= max_len_z:
                    dims_that_fit.append(dims)

        if len(dims_that_fit) < 1:
            return None, None

        best_fit = None
        other_best_fit = None
        min_y_diff = min_x_diff = min_z_diff = 99999
        other_y_diff = other_x_diff = other_z_diff = 99999

        for w, l, h in dims_that_fit:
            if self.item_select_strategy == ItemSelectStrategy.HIGHEST_VOLUME_FOR_EMPTY_LAYER and max_len_x == bin_len_x or self.item_select_strategy == ItemSelectStrategy.ALWAYS_HIGHEST_VOLUME:
                sorted_items = sorted(
                    items, key=lambda x: x.volume, reverse=True)
                if len(sorted_items) > 1:
                    return sorted_items[0], None

            # item has smaller or same height
            if h <= gap_len_z:
                x_diff = max_len_x - w
                y_diff = 1  # gap_len_y - l
                z_diff = gap_len_z - h

                if (y_diff, x_diff, z_diff) < (min_y_diff, min_x_diff, min_z_diff):
                    min_x_diff = x_diff
                    min_y_diff = y_diff
                    min_z_diff = z_diff
                    best_fit = (w, l, h)

            # item doesn't quite fit the layer height
            else:
                x_diff = max_len_x - w
                y_diff = 1  # abs(gap_len_y - l)
                z_diff = h - gap_len_z
                if (y_diff, x_diff, z_diff) < (other_y_diff, other_x_diff, other_z_diff):
                    other_y_diff = y_diff
                    other_x_diff = x_diff
                    other_z_diff = z_diff
                    other_best_fit = (w, l, h)

        best_fit = self._get_item_with_dimension(items, best_fit)
        other_best_fit = self._get_item_with_dimension(items, other_best_fit)
        return best_fit, other_best_fit

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
        print(total_gap_width)
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
            failed, info = bin.pack_item(item)
            if not failed:
                print(item.position)
                print(info)
        return True
