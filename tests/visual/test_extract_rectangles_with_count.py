from packutils.data.single_item import SingleItem
from packutils.data.position import Position
from packutils.visual.packing_visualization import (
    Perspective,
    extract_rectangles_with_count,
)


def test_extract_rectangles_front_no_grouping():
    item1 = SingleItem("", width=2, length=2, height=2)
    item1.pack(position=Position(x=0, y=0, z=0))
    item2 = SingleItem("", width=2, length=2, height=2)
    item2.pack(position=Position(x=2, y=0, z=0))
    item3 = SingleItem("", width=2, length=2, height=2)
    item3.pack(position=Position(x=0, y=0, z=2))
    item4 = SingleItem("", width=2, length=2, height=2)
    item4.pack(position=Position(x=2, y=0, z=2))
    items = [item1, item2, item3, item4]

    rectangles = extract_rectangles_with_count(items, Perspective.front)
    print(rectangles)

    assert len(rectangles) == 4
    assert rectangles == [
        ((0, 0, 2, 2), 1),
        ((2, 0, 2, 2), 1),
        ((0, 2, 2, 2), 1),
        ((2, 2, 2, 2), 1),
    ]


def test_extract_rectangles_front_with_grouping():
    item1 = SingleItem("", width=2, length=2, height=2)
    item1.pack(position=Position(x=0, y=0, z=0))
    item2 = SingleItem("", width=2, length=2, height=2)
    item2.pack(position=Position(x=2, y=0, z=0))
    item3 = SingleItem("", width=2, length=2, height=2)
    item3.pack(position=Position(x=0, y=2, z=0))
    item4 = SingleItem("", width=2, length=2, height=2)
    item4.pack(position=Position(x=2, y=2, z=0))
    items = [item1, item2, item3, item4]

    rectangles = extract_rectangles_with_count(items, Perspective.front)
    print(rectangles)

    assert len(rectangles) == 2
    assert rectangles == [
        ((0, 0, 2, 2), 2),
        ((2, 0, 2, 2), 2),
    ]
