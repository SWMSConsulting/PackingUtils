import unittest
from packutils.data.position import Position
from packutils.data.single_item import SingleItem
from packutils.data.grouped_item import (
    GroupedItem,
    ItemGroupingMode,
    group_items_lengthwise,
)


class TestGroupedItem(unittest.TestCase):
    def test_group_items_lengthwise(self):
        item1 = SingleItem(identifier="test", width=1, length=1, height=2, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=2, height=2, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=3, height=2, weight=6)
        items_to_group = [item1, item2, item3]

        grouped_item = group_items_lengthwise(items_to_group)

        self.assertEqual(grouped_item.width, 1)
        self.assertEqual(grouped_item.height, 2)
        self.assertEqual(grouped_item.length, 6)
        self.assertEqual(grouped_item.weight, 15)
        self.assertEqual(
            grouped_item.identifier, "ItemGroup (lengthwise): 3 Items (1, 6, 2)"
        )

    def test_pack_lengthwise(self):
        item1 = SingleItem(identifier="test", width=1, length=2, height=3, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=3, height=3, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=4, height=3, weight=6)
        items_to_group = [item1, item2, item3]

        grouped_item = group_items_lengthwise(items_to_group)
        position = Position(x=0, y=0, z=0)
        grouped_item.pack(position, 1)

        self.assertEqual(item1.position, Position(x=0, y=0, z=0))
        self.assertEqual(item2.position, Position(x=0, y=2, z=0))
        self.assertEqual(item3.position, Position(x=0, y=5, z=0))

    def test_get_max_overhang_y(self):
        item1 = SingleItem(identifier="test", width=1, length=1, height=3, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=2, height=3, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=2, height=3, weight=6)
        items_to_group = [item1, item2, item3]

        grouped_item = group_items_lengthwise(items_to_group)
        stability_factor = 0.5
        max_overhang_y = grouped_item.get_max_overhang_y(stability_factor)

        self.assertEqual(max_overhang_y, 0)

    def test_flatten(self):
        item1 = SingleItem(identifier="test", width=1, length=2, height=3, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=2, height=3, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=2, height=3, weight=6)
        items_to_group = [item1, item2, item3]

        grouped_item = group_items_lengthwise(items_to_group)
        flattened_items = grouped_item.flatten()

        self.assertEqual(len(flattened_items), 3)
        self.assertIn(item1, flattened_items)
        self.assertIn(item2, flattened_items)
        self.assertIn(item3, flattened_items)

    def test_group_with_position_offsets(self):
        item1 = SingleItem(identifier="test", width=2, length=4, height=2, weight=4)
        item2 = SingleItem(identifier="test", width=2, length=4, height=2, weight=5)
        items_to_group = [item1, item2]
        position_offsets = [Position(0, 0, 0), Position(0, 4, 0)]

        grouped_item = group_items_lengthwise(items_to_group, position_offsets)
        flattened_items = grouped_item.flatten()

        item1.pack(position_offsets[0], 1)
        item2.pack(position_offsets[1], 2)

        self.assertEqual(len(flattened_items), 2)
        packed1, packed2 = flattened_items
        self.assertEqual(item1, packed1)
        self.assertEqual(item1.position, packed1.position)
        self.assertEqual(item2, packed2)
        self.assertEqual(item2.position, packed2.position)

    def test_group_with_position_offsets_overlap(self):
        item1 = SingleItem(identifier="test", width=2, length=4, height=2, weight=4)
        item2 = SingleItem(identifier="test", width=2, length=4, height=2, weight=5)
        items_to_group = [item1, item2]
        position_offsets = [Position(0, 0, 0), Position(0, 2, 0)]

        grouped_item = group_items_lengthwise(items_to_group, position_offsets)

        self.assertIsNone(grouped_item)


if __name__ == "__main__":
    unittest.main()
