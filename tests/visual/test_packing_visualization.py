import unittest
import os
from PIL import Image
import matplotlib.pyplot as plt

from packutils.data.item import Item
from packutils.data.bin import Bin
from packutils.data.position import Position
from packutils.data.packing_variant import PackingVariant
from packutils.visual.packing_visualization import PackingVisualization


class TestPackingVisualization(unittest.TestCase):
    def setUp(self):
        self.visualization = PackingVisualization()

        self.variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        item1 = Item(id="item1", width=1, length=1, height=1,
                     position=Position(x=0, y=0, z=0))
        bin.pack_item(item1)
        item2 = Item(id="item2", width=1, length=1, height=1,
                     position=Position(x=1, y=0, z=0))
        bin.pack_item(item2)
        item3 = Item(id="item3", width=1, length=1, height=1,
                     position=Position(x=0, y=1, z=0))
        bin.pack_item(item3)
        item4 = Item(id="item4", width=1, length=1, height=1,
                     position=Position(x=0, y=0, z=1))
        bin.pack_item(item4)
        self.variant.add_bin(bin)

    def test_visualize_bin(self):
        self.visualization.visualize_bin(self.variant.bins[0], show=False)

    def test_visualize_bin_2D(self):
        bin = self.variant.bins[0]
        bin.width = 1
        # self.visualization.visualize_bin(bin, show=True)


if __name__ == "__main__":
    unittest.main()
