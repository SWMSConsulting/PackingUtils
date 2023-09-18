import unittest

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.position import Position
from packutils.eval.packing_evaluation import PackingEvaluation, PackingEvaluationWeights
from packutils.visual.packing_visualization import PackingVisualization


class TestPackingEvaluation(unittest.TestCase):

    def setUp(self):
        self.bin1 = Bin(6, 1, 6)
        self.bin1.packed_items = [
            Item("il1", width=2, length=1, height=2, position=Position(x=0, y=0, z=0)
                 ),
            Item("il2", width=2, length=1, height=2, position=Position(x=2, y=0, z=0)
                 ),
            Item("il3", width=2, length=1, height=2, position=Position(x=4, y=0, z=0)
                 ),
            Item("il4", width=2, length=1, height=2, position=Position(x=4, y=0, z=2)
                 ),
            Item("is1", width=1, length=1, height=1, position=Position(x=0, y=0, z=2)
                 ),
            Item("is2", width=1, length=1, height=1, position=Position(x=1, y=0, z=2)
                 ),
        ]

        self.bin2 = Bin(6, 1, 6)
        self.bin2.packed_items = [
            Item("il1", width=2, length=1, height=2, position=Position(x=0, y=0, z=0)
                 ),
            Item("il2", width=2, length=1, height=2, position=Position(x=2, y=0, z=0)
                 ),
            Item("il3", width=2, length=1, height=2, position=Position(x=4, y=0, z=0)
                 ),
            Item("il4", width=2, length=1, height=2, position=Position(x=4, y=0, z=2)
                 ),
            Item("is1", width=1, length=1, height=1, position=Position(x=2, y=0, z=2)
                 ),
            Item("is2", width=1, length=1, height=1, position=Position(x=3, y=0, z=2)
                 ),
        ]

        self.bin3 = Bin(6, 1, 6)
        self.bin3.packed_items = [
            Item("il1", width=2, length=1, height=2, position=Position(x=0, y=0, z=0)
                 ),
            Item("il2", width=2, length=1, height=2, position=Position(x=0, y=0, z=2)
                 ),
            Item("il3", width=2, length=1, height=2, position=Position(x=4, y=0, z=0)
                 ),
            Item("il4", width=2, length=1, height=2, position=Position(x=4, y=0, z=2)
                 ),
            Item("is1", width=1, length=1, height=1, position=Position(x=2, y=0, z=0)
                 ),
            Item("is2", width=1, length=1, height=1, position=Position(x=3, y=0, z=0)
                 ),
        ]

        self.bin4 = Bin(6, 1, 6)
        self.bin4.packed_items = [
            Item("il1", width=2, length=1, height=2, position=Position(x=0, y=0, z=0)
                 ),
            Item("il2", width=2, length=1, height=2, position=Position(x=0, y=0, z=2)
                 ),
            Item("il3", width=2, length=1, height=2, position=Position(x=2, y=0, z=0)
                 ),
            Item("il4", width=2, length=1, height=2, position=Position(x=2, y=0, z=2)
                 ),
            Item("is1", width=1, length=1, height=1, position=Position(x=4, y=0, z=0)
                 ),
            Item("is2", width=1, length=1, height=1, position=Position(x=5, y=0, z=0)
                 ),
        ]

    def test_evaluate_item_distribution(self):
        eval = PackingEvaluation(PackingEvaluationWeights(
            item_distribution=1.0
        ))
        score1 = eval.evaluate_bin(self.bin1)
        score2 = eval.evaluate_bin(self.bin2)
        score3 = eval.evaluate_bin(self.bin3)
        score4 = eval.evaluate_bin(self.bin4)

        self.assertTrue(score3 > score1 > score2 > score4)

    def test_evaluate_item_stacking(self):

        eval = PackingEvaluation(PackingEvaluationWeights(
            item_stacking=1.0
        ))
        score1 = eval.evaluate_bin(self.bin1)
        score2 = eval.evaluate_bin(self.bin2)
        score3 = eval.evaluate_bin(self.bin3)
        score4 = eval.evaluate_bin(self.bin4)

        self.assertTrue(score1 == score2 > score3 == score4)

    def test_evaluate_item_grouping(self):

        eval = PackingEvaluation(PackingEvaluationWeights(
            item_grouping=1.0
        ))
        score1 = eval.evaluate_bin(self.bin1)
        score2 = eval.evaluate_bin(self.bin2)
        score3 = eval.evaluate_bin(self.bin3)
        score4 = eval.evaluate_bin(self.bin4)

        print(score1, score2, score3, score4)

        PackingVisualization().visualize_bin(self.bin1)
        PackingVisualization().visualize_bin(self.bin2)
        PackingVisualization().visualize_bin(self.bin3)
        PackingVisualization().visualize_bin(self.bin4)

        self.assertTrue(score4 > score1 == score2 > score3)


if __name__ == '__main__':
    unittest.main()
