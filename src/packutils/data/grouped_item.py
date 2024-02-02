from typing import List
from packutils.data.item import Item
from packutils.data.packer_configuration import ItemGroupingMode
from packutils.data.position import Position


class GroupedItem(Item):
    grouping_mode: ItemGroupingMode
    grouped_items: List[Item]

    def __init__(self, items_to_group: List[Item], grouping_mode: ItemGroupingMode):
        self.grouping_mode = grouping_mode
        self.grouped_items = items_to_group

        self.weight = sum(item.weight for item in items_to_group)

        self.group_items()

    def group_items(self):
        """
        Groups the items according to the specified grouping mode.
        """
        if self.grouping_mode == ItemGroupingMode.LENGTHWISE:
            self.width = self.grouped_items[0].width
            self.height = self.grouped_items[0].height

            assert all(
                item.width == self.width and item.height == self.height
                for item in self.grouped_items
            ), "All items must have the same width and height"

            self.length = sum(item.length for item in self.grouped_items)

        else:
            raise NotImplementedError(
                f"Grouping mode not implemented {self.grouping_mode}"
            )

        self.identifier = f"ItemGroup ({self.grouping_mode.value}): {len(self.grouped_items)} Items {self.width,self.length,self.height}"

    def pack(self, position: Position | None):
        self.position = position

        if self.grouping_mode == ItemGroupingMode.LENGTHWISE:
            position_offset = 0
            for item in self.grouped_items:
                pos = Position(position.x, position.y + position_offset, position.z)
                item.pack(pos)
                position_offset += item.length

        else:
            raise NotImplementedError(
                f"Grouping mode not implemented {self.grouping_mode}"
            )

    def get_max_overhang_y(self, stability_factor: "float|None") -> int:
        return min(
            item.get_max_overhang_y(stability_factor) for item in self.grouped_items
        )

    def flatten(self) -> List[Item]:
        """
        Returns the items in the group as a list.

        Returns:
            List[Item]: The items in the group.
        """
        return sum((item.flatten() for item in self.grouped_items), [])
