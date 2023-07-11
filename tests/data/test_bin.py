import unittest
import numpy as np

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.position import Position


class TestBin(unittest.TestCase):
    def setUp(self):
        self.bin = Bin(width=10, length=10, height=10)

    def test_pack_item_successful(self):
        item = Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 0)
        )
        result, _ = self.bin.pack_item(item)

        self.assertTrue(result)
        self.assertEqual(len(self.bin.packed_items), 1)
        self.assertEqual(np.count_nonzero(self.bin.matrix), 27)

    def test_pack_item_stability_check(self):

        # item is flying
        bin = Bin(width=10, length=10, height=10)
        flying_item = Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 1)
        )
        result, _ = bin.pack_item(flying_item)
        self.assertFalse(result)

        # item is packed on the bottom of container
        bin = Bin(width=10, length=10, height=10)
        valid_item = Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 0)
        )
        result, _ = bin.pack_item(valid_item)
        self.assertTrue(result)

        # item is placed fully on top of other item
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 0)
        ))
        valid_item = Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 3)
        )
        result, _ = bin.pack_item(valid_item)
        self.assertTrue(result)

        # item is placed fully on top of other item with small overhang
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 0)
        ))
        valid_item = Item(
            id="test", width=4, length=3, height=3, position=Position(0, 0, 3)
        )
        result, _ = bin.pack_item(valid_item)
        self.assertTrue(result)

        # item is placed fully on top of other item with too much overhang
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 0)
        ))
        too_much_overhang_item = Item(
            id="test", width=3, length=3, height=3, position=Position(2, 0, 3)
        )
        result, _ = bin.pack_item(too_much_overhang_item)
        self.assertFalse(result)

    def test_pack_item_out_of_bounds(self):
        item = Item(
            id="test", width=5, length=5, height=5, position=Position(7, 7, 7))
        result, _ = self.bin.pack_item(item)

        self.assertFalse(result)
        self.assertEqual(len(self.bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(self.bin.matrix), 0)

    def test_pack_item_position_occupied(self):
        item1 = Item(
            id="test", width=4, length=4, height=4, position=Position(0, 0, 0)
        )
        item2 = Item(
            id="test", width=2, length=2, height=2, position=Position(1, 1, 1)
        )
        self.bin.pack_item(item1)
        result, _ = self.bin.pack_item(item2)
        self.assertFalse(result)
        self.assertEqual(len(self.bin.packed_items), 1)
        self.assertEqual(
            np.count_nonzero(self.bin.matrix),
            item1.width * item1.length * item1.height)

    def test_pack_item_with_none_position(self):
        item = Item(id="test", width=3, length=3, height=3)
        result, _ = self.bin.pack_item(item)
        self.assertFalse(result)
        self.assertEqual(len(self.bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(self.bin.matrix), 0)

    def test_is_packing_2d(self):
        bin1 = Bin(width=1, length=10, height=10)
        result, dimensions = bin1.is_packing_2d()
        self.assertTrue(result)
        self.assertEqual(dimensions, ["length", "height"])

        bin2 = Bin(width=10, length=1, height=10)
        result, dimensions = bin2.is_packing_2d()
        self.assertTrue(result)
        self.assertEqual(dimensions, ["width", "height"])

        bin3 = Bin(width=10, length=10, height=1)
        result, dimensions = bin3.is_packing_2d()
        self.assertTrue(result)
        self.assertEqual(dimensions, ["width", "length"])

        result, dimensions = self.bin.is_packing_2d()
        self.assertFalse(result)
        self.assertEqual(dimensions, [])

    def test_get_dimension_2d(self):
        self.bin.width = 50
        self.bin.length = 60
        self.bin.height = 70

        dimensions = ["width", "length"]
        result = self.bin.get_dimension_2d(dimensions)
        self.assertEqual(result, [50, 60])

        dimensions = ["length", "height"]
        result = self.bin.get_dimension_2d(dimensions)
        self.assertEqual(result, [60, 70])

        dimensions = ["width", "height"]
        result = self.bin.get_dimension_2d(dimensions)
        self.assertEqual(result, [50, 70])

        with self.assertRaises(ValueError):
            dimensions = ["width", "length", "height"]
            self.bin.get_dimension_2d(dimensions)

        with self.assertRaises(ValueError):
            dimensions = ["width", "depth"]
            self.bin.get_dimension_2d(dimensions)

    def test_volume(self):
        bin = Bin(width=10, length=20, height=5)
        self.assertEqual(bin.volume, 1000)

    def test_used_volume(self):
        bin = Bin(width=10, length=20, height=5)
        bin.pack_item(Item(id="test1", width=2, length=10,
                      height=2, position=Position(x=0, y=0, z=0)))
        bin.pack_item(Item(id="test2", width=3, length=5,
                      height=2, position=Position(x=4, y=0, z=0)))
        self.assertEqual(bin.get_used_volume(), 40 + 30)
        self.assertEqual(bin.get_used_volume(use_percentage=True), 7)


if __name__ == '__main__':
    unittest.main()
