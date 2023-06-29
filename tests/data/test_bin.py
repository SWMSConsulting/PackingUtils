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


if __name__ == '__main__':
    unittest.main()
