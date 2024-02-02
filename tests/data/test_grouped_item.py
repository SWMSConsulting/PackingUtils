import unittest
from packutils.data.position import Position
from packutils.data.single_item import SingleItem
from packutils.data.grouped_item import GroupedItem, GroupingMode


class TestGroupedItem(unittest.TestCase):
    def test_group_items_lengthwise(self):
        item1 = SingleItem(identifier="test", width=1, length=1, height=2, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=2, height=2, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=3, height=2, weight=6)
        items_to_group = [item1, item2, item3]
        grouping_mode = GroupingMode.LENGTHWISE

        grouped_item = GroupedItem(items_to_group, grouping_mode)

        self.assertEqual(grouped_item.width, 1)
        self.assertEqual(grouped_item.height, 2)
        self.assertEqual(grouped_item.length, 6)
        self.assertEqual(grouped_item.weight, 15)
        self.assertEqual(
            grouped_item.identifier, "ItemGroup (lengthwise): 3 Items (1, 2, 6)"
        )

    def test_pack_lengthwise(self):
        item1 = SingleItem(identifier="test", width=1, length=2, height=3, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=3, height=3, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=4, height=3, weight=6)
        items_to_group = [item1, item2, item3]
        grouping_mode = GroupingMode.LENGTHWISE

        grouped_item = GroupedItem(items_to_group, grouping_mode)
        position = Position(x=0, y=0, z=0)
        grouped_item.pack(position)

        self.assertEqual(item1.position, Position(x=0, y=0, z=0))
        self.assertEqual(item2.position, Position(x=0, y=2, z=0))
        self.assertEqual(item3.position, Position(x=0, y=5, z=0))

    def test_get_max_overhang_y(self):
        item1 = SingleItem(identifier="test", width=1, length=1, height=3, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=2, height=3, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=2, height=3, weight=6)
        items_to_group = [item1, item2, item3]
        grouping_mode = GroupingMode.LENGTHWISE

        grouped_item = GroupedItem(items_to_group, grouping_mode)
        stability_factor = 0.5
        max_overhang_y = grouped_item.get_max_overhang_y(stability_factor)

        self.assertEqual(max_overhang_y, 0)

    def test_flatten(self):
        item1 = SingleItem(identifier="test", width=1, length=2, height=3, weight=4)
        item2 = SingleItem(identifier="test", width=1, length=2, height=3, weight=5)
        item3 = SingleItem(identifier="test", width=1, length=2, height=3, weight=6)
        items_to_group = [item1, item2, item3]
        grouping_mode = GroupingMode.LENGTHWISE

        grouped_item = GroupedItem(items_to_group, grouping_mode)
        flattened_items = grouped_item.flatten()

        self.assertEqual(len(flattened_items), 3)
        self.assertIn(item1, flattened_items)
        self.assertIn(item2, flattened_items)
        self.assertIn(item3, flattened_items)


if __name__ == "__main__":
    unittest.main()
