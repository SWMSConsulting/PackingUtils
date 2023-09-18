import numpy as np

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.packing_variant import PackingVariant


class PackingEvaluationWeights():
    def __init__(
        self,
        item_distribution: float = 0.0,
        item_stacking: float = 0.0,
        item_grouping: float = 0.0
    ):
        self.item_distribution = item_distribution
        self.item_stacking = item_stacking
        self.item_grouping = item_grouping


class PackingEvaluation():
    def __init__(self, weights: PackingEvaluationWeights):
        self.weights = weights

    def evaluate_packing_variant(self, variant: PackingVariant):
        score = np.mean([self.evaluate_bin(bin) for bin in variant.bins])
        return score

    def evaluate_bin(self, bin: Bin):
        score = 0

        if self.weights.item_distribution != 0:
            score += self.weights.item_distribution * \
                self._evaluate_item_distribution(bin)

        if self.weights.item_stacking != 0:
            score += self.weights.item_stacking * \
                self._evaluate_item_stacking(bin)

        if self.weights.item_grouping != 0:
            score += self.weights.item_grouping * \
                self._evaluate_item_grouping(bin)

        return score

    def _evaluate_item_distribution(self, bin: Bin):
        """
        The goal is to put larger items on the sides of the pallet and to center the smaller items.
        This metric calculates the distance of the items to the center and scores it depending on the item volume.
        """

        scores = []

        for item in bin.packed_items:
            rel_distance_center = abs(
                item.centerpoint().x - bin.width / 2) / (bin.width / 2)
            rel_volume = item.volume / \
                bin.get_used_volume(use_percentage=False)
            scores.append(rel_distance_center * rel_volume)

        return np.mean(scores)

    def _evaluate_item_stacking(self, bin: Bin):
        """
        The goal is to put smaller items on top of larger items. Therefore the distance 
        """

        scores = []
        for item in bin.packed_items:
            rel_distance_bottom = item.position.z / bin.height
            rel_volume = item.volume / \
                bin.get_used_volume(use_percentage=False)
            scores.append(rel_distance_bottom / rel_volume)

        return np.mean(scores)

    def _distance_between_items(self, item1: Item, item2: Item):
        p1 = np.array(
            [item1.centerpoint().x, item1.centerpoint().y, item1.centerpoint().z])
        p2 = np.array(
            [item2.centerpoint().x, item2.centerpoint().y, item2.centerpoint().z])
        squared_dist = np.sum((p1-p2)**2, axis=0)
        distance = np.sqrt(squared_dist)

        return distance

    def _evaluate_item_grouping(self, bin: Bin):
        """
        The goal is to group items of same type. The score is calculated by counting touching items (direct neighbors). This number is divided by the number of other items in the group or by 4 if more than 5 items are in the group. 
        """

        scores = []

        groups = set([(item.width, item.length, item.height)
                     for item in bin.packed_items])

        for group in groups:
            group_items = [item for item in bin.packed_items if (
                item.width, item.length, item.height) == group]

            group_scores = []

            for item in group_items:
                touching_items = [other for other in group_items if (
                    abs(item.position.x - other.position.x) == item.width or
                    abs(item.position.y - other.position.y) == item.length or
                    abs(item.position.z - other.position.z) == item.height
                )]
                group_scores.append(len(touching_items) /
                                    min(max(len(group_items)-1, 1), 4))

            scores.append(np.mean(group_scores))
        return np.mean(scores)
