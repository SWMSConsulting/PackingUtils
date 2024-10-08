from typing import List, Tuple
from packutils.data.item import Item
from packutils.data.packer_configuration import ItemGroupingMode
from packutils.data.position import Position


def group_items_horizontally(
    items_to_group: List[Item],
    position_offsets: "List[Position]| None" = None,
    padding_between_items: int = 0,
) -> "GroupedItem|None":

    height = items_to_group[0].height
    assert all(
        item.height == height for item in items_to_group
    ), "All items must have the same height"

    assert position_offsets is None or all(
        p.y == 0 and p.z == 0 for p in position_offsets
    ), "When grouping horizontally, only x offsets are allowed"

    if position_offsets is None:
        position_offsets = []
        grouped_items: List[Item] = []
        x_offset = 0
        for item in sorted(items_to_group, key=lambda item: item.width):
            grouped_items.append(item)
            position_offsets.append(Position(x_offset, 0, 0))
            x_offset += item.width + padding_between_items

    else:
        grouped_items = items_to_group
        x_offset = -1e5
        for item, position_offset in sorted(
            zip(items_to_group, position_offsets), key=lambda x: x[1].x
        ):
            if x_offset > position_offset.x:
                return None  # two items overlap
            x_offset = position_offset.x + item.width

    return GroupedItem(grouped_items, ItemGroupingMode.HORIZONTAL, position_offsets)


def group_items_vertically(
    items_to_group: List[Item]
) -> "GroupedItem|None":

    width = items_to_group[0].width
    assert all(
        item.width == width for item in items_to_group
    ), "All items must have the same width"

    position_offsets = []
    grouped_items: List[Item] = []
    z_offset = 0
    for item in sorted(items_to_group, key=lambda item: item.width):
        grouped_items.append(item)
        position_offsets.append(Position(0, 0, z_offset))
        z_offset += item.height

    return GroupedItem(grouped_items, ItemGroupingMode.VERTICAL, position_offsets)


def group_items_lengthwise(
    items_to_group: List[Item],
    position_offsets: "List[Position]| None" = None,
    padding_between_items: int = 0,
) -> "GroupedItem|None":

    width = items_to_group[0].width
    height = items_to_group[0].height
    assert all(
        item.width == width and item.height == height for item in items_to_group
    ), "All items must have the same width and height"

    assert position_offsets is None or all(
        p.x == 0 and p.z == 0 for p in position_offsets
    ), "When grouping lengthwise, only y offsets are allowed"

    if position_offsets is None:
        position_offsets = []
        grouped_items: List[Item] = []
        y_offset = 0
        for item in sorted(items_to_group, key=lambda item: item.length):
            grouped_items.append(item)
            position_offsets.append(Position(0, y_offset, 0))
            y_offset += item.length + padding_between_items

    else:
        grouped_items = items_to_group
        y_offset = -1e5
        for item, position_offset in sorted(
            zip(items_to_group, position_offsets), key=lambda x: x[1].y
        ):
            if y_offset > position_offset.y:
                return None  # two items overlap
            y_offset = position_offset.y + item.length

    return GroupedItem(grouped_items, ItemGroupingMode.LENGTHWISE, position_offsets)


class GroupedItem(Item):
    grouping_mode: ItemGroupingMode
    grouped_items: List[Item]
    position_offsets: List[Position]

    def __init__(
        self,
        grouped_items: List[Item],
        grouping_mode: ItemGroupingMode,
        position_offsets: List[Position],
    ):
        self.grouping_mode = grouping_mode
        self.grouped_items = grouped_items
        self.position_offsets = position_offsets

        if self.grouping_mode == ItemGroupingMode.LENGTHWISE:
            self.width = grouped_items[0].width
            self.height = grouped_items[0].height
            self.length = max(
                p.y + i.length
                for i, p in zip(self.grouped_items, self.position_offsets)
            ) - min(p.y for p in position_offsets)

        elif self.grouping_mode == ItemGroupingMode.HORIZONTAL:
            self.height = grouped_items[0].height
            self.length = max([i.length for i in grouped_items])
            self.width = max(
                p.x + i.width for i, p in zip(self.grouped_items, self.position_offsets)
            ) - min(p.x for p in position_offsets)

        elif self.grouping_mode == ItemGroupingMode.VERTICAL:
            self.width = grouped_items[0].width
            self.length = max([i.length for i in grouped_items])
            self.height = sum([i.height for i in grouped_items])

        else:
            raise ValueError(f"Unknown grouping mode: {self.grouping_mode}")

        self.weight = sum(item.weight for item in grouped_items)
        self.identifier = f"ItemGroup ({self.grouping_mode.value}): {len(self.grouped_items)} Items {self.width,self.length,self.height}"
        self.index = -1

    def pack(self, position: "Position | None", index: int) -> None:
        self.position = position
        self.index = index

        for item, offset in zip(self.grouped_items, self.position_offsets):
            pos = Position(
                position.x + offset.x, position.y + offset.y, position.z + offset.z
            )
            item.pack(pos, index)
        index += 10

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
