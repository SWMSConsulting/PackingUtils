import unittest
from packutils.data.single_item import SingleItem
from packutils.data.position import Position


class ItemTestCase(unittest.TestCase):
    def test_item_creation(self):
        item = SingleItem(identifier="test", width=10, length=20, height=30)
        self.assertEqual(item.identifier, "test")
        self.assertEqual(item.width, 10)
        self.assertEqual(item.length, 20)
        self.assertEqual(item.height, 30)
        self.assertIsNone(item.position)

    def test_item_pack(self):
        item = SingleItem(identifier="test", width=10, length=20, height=30)
        position = Position(x=5, y=5, z=5, rotation=0)
        item.pack(position)
        self.assertEqual(item.is_packed, True)
        self.assertEqual(item.position, position)

    def test_get_max_overhang_y(self):
        item = SingleItem(identifier="test", width=10, length=20, height=30)

        self.assertEqual(item.get_max_overhang_y(0.5), 10)
        self.assertEqual(item.get_max_overhang_y(0.75), 5)
        self.assertEqual(item.get_max_overhang_y(1), 0)


if __name__ == "__main__":
    unittest.main()
