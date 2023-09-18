import numpy as np

from packutils.data.bin import Bin
from packutils.data.packing_variant import PackingVariant

class PackingEvaluationWeights():
    def __init__(
        self,
        item_distribution: float = 0.0
    ):
        self.item_distribution = item_distribution
        
        

class PackingEvaluation():
    def __init__(self, weights: PackingEvaluationWeights):
        self.weights = weights

    def evaluate_packing_variant(self, variant: PackingVariant):
        score = np.mean([self.evaluate_bin(bin) for bin in variant.bins])
        return score 

    
    def evaluate_bin(self, bin: Bin):
        score = 0
        
        if self.weights.item_distribution != 0:
            score += self.weights.item_distribution * self._evaluate_item_distribution(bin)

    def _evaluate_item_distribution(self, bin: Bin):
        """
        The goal is to put larger items on the sides of the pallet and to center the smaller items.
        This metric calculates the distance of the items to the center and scores it depending on the item volume.
        """

        scores = []

        for item in bin.packed_items:
            rel_distance_center =  abs(item.centerpoint().x - bin.width / 2) / (bin.width / 2)
            rel_volume = item.volume / bin.get_used_volume(use_percentage=False)
            scores.append(rel_distance_center * rel_volume)

        print(scores)
        return np.mean(scores)