from typing import List
import numpy as np

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.packer_configuration import PackerConfiguration
from packutils.data.packing_variant import PackingVariant


class PackingEvaluationWeights:
    def __init__(
        self,
        item_distribution: float = 0.0,
        item_stacking: float = 0.0,
        item_grouping: float = 0.0,
        utilized_space: float = 3.0,
    ):
        self.item_distribution = item_distribution
        self.item_stacking = item_stacking
        self.item_grouping = item_grouping
        self.utilized_space = utilized_space

    @property
    def total(self):
        return (
            self.item_distribution
            + self.item_stacking
            + self.item_grouping
            + self.utilized_space
        )


class PackingEvaluation:
    def __init__(self, weights: PackingEvaluationWeights):
        self.weights = weights

    def evaluate_packing_variants(
        self,
        variants: List[PackingVariant],
        configs: List[PackerConfiguration],
        return_scores_dict=False,
    ):
        unique_variants = list(set(variants))
        grouped_configs = [[] for _ in range(len(unique_variants))]
        for variant, config in zip(variants, configs):
            grouped_configs[unique_variants.index(variant)].append(config)

        if return_scores_dict:
            scores = [self.evaluate_packing_variant(v) for v in unique_variants]
        else:
            scores = [self.evaluate_packing_variant(v)[0] for v in unique_variants]

        scored_variants = zip(scores, zip(unique_variants, grouped_configs))
        return scored_variants

    def evaluate_packing_variant(self, variant: PackingVariant):
        scores = [self.evaluate_bin(bin) for bin in variant.bins]
        score = np.mean([s[0] for s in scores])
        score_details = {}
        for idx, (_, s) in enumerate(scores):
            score_details[f"Bin {idx+1}"] = s
        return score, score_details

    def evaluate_bin(self, bin: Bin):
        score = 0
        details = {}

        item_distribution_score = (
            self.weights.item_distribution * self._evaluate_item_distribution(bin)
        )
        details["item_distribution"] = item_distribution_score
        score += item_distribution_score

        item_stacking_score = self.weights.item_stacking * self._evaluate_item_stacking(
            bin
        )
        details["item_stacking"] = item_stacking_score
        score += item_stacking_score

        item_grouping_score = self.weights.item_grouping * self._evaluate_item_grouping(
            bin
        )
        details["item_grouping"] = item_grouping_score
        score += item_grouping_score

        utilized_space_score = (
            self.weights.utilized_space * bin.get_used_volume() / bin.volume
        )

        details["utilized_space"] = utilized_space_score
        score += utilized_space_score

        score /= self.weights.total
        return score, details

    def _evaluate_item_distribution(self, bin: Bin):
        """
        The goal is to put larger items on the sides of the pallet and to center the smaller items.
        This metric calculates the distance of the items to the center and scores it depending on the item volume.
        """
        scores = [
            1
            - (
                min(item.position.x, bin.width - item.position.x - item.width)
                / (bin.width / 2)
            )
            * item.volume
            / bin.get_used_volume()
            for item in bin.packed_items
        ]
        return np.mean(scores)

    def _evaluate_item_stacking(self, bin: Bin):
        """
        The goal is to put smaller items on top of larger items. Therefore the distance
        """

        seen_items = []
        scores = []

        for item in bin.packed_items:
            items_below = [
                other
                for other in seen_items
                if (
                    abs(other.centerpoint().x - item.centerpoint().x)
                    < max(item.width, other.width) / 2
                    and abs(other.centerpoint().y - item.centerpoint().y)
                    < max(item.length, other.length) / 2
                )
            ]
            seen_items.append(item)

            if len(items_below) < 1:
                scores.append(1)
                continue

            smaller_items_below = [
                other for other in items_below if (other.volume < item.volume)
            ]
            scores.append(1 - len(smaller_items_below) / len(items_below))

        return np.mean(scores)

    def _distance_between_items(self, item1: Item, item2: Item):
        p1 = np.array(
            [item1.centerpoint().x, item1.centerpoint().y, item1.centerpoint().z]
        )
        p2 = np.array(
            [item2.centerpoint().x, item2.centerpoint().y, item2.centerpoint().z]
        )
        squared_dist = np.sum((p1 - p2) ** 2, axis=0)
        distance = np.sqrt(squared_dist)

        return distance

    def _evaluate_item_grouping(self, bin: Bin):
        """
        The goal is to group items of same type. The score is calculated by counting touching items (direct neighbors). This number is divided by the number of other items in the group or by 4 if more than 5 items are in the group.
        """

        scores = []

        groups = set(
            [(item.width, item.length, item.height) for item in bin.packed_items]
        )

        for group in groups:
            group_items = [
                item
                for item in bin.packed_items
                if (item.width, item.length, item.height) == group
            ]

            group_scores = []
            if len(group_items) < 2:
                continue
            for item in group_items:
                touching_items = [
                    other
                    for other in group_items
                    if (
                        abs(item.position.x - other.position.x),
                        abs(item.position.y - other.position.y),
                        abs(item.position.z - other.position.z),
                    )
                    in [
                        (item.width, 0, 0),
                        (0, item.length, 0),
                        (0, 0, item.height),
                    ]
                ]
                group_scores.append(
                    len(touching_items) / min(max(len(group_items) - 1, 1), 4)
                )

            scores.append(np.mean(group_scores))
        return np.mean(scores) if len(scores) > 0 else 1
