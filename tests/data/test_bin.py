import unittest
import numpy as np

from packutils.data.bin import Bin
from packutils.data.single_item import SingleItem
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection


class TestBin(unittest.TestCase):

    def test_pack_item_successful(self):
        bin = Bin(width=10, length=10, height=10)
        item = SingleItem(identifier="test", width=3, length=10, height=3)
        position = Position(0, 0, 0)
        result, _ = bin.pack_item(item, position)

        self.assertTrue(result)
        self.assertEqual(len(bin.packed_items), 1)
        self.assertEqual(np.count_nonzero(bin.heightmap), 3)

    def test_pack_item_single_item(self):
        bin = Bin(width=10, length=10, height=10)
        valid_item = SingleItem(identifier="test", width=3, length=3, height=3)
        position = Position(0, 0, 0)
        result, _ = bin.pack_item(valid_item, position)
        self.assertTrue(result)

    def test_pack_item_flying_item(self):
        bin = Bin(width=10, length=10, height=10)
        item = SingleItem(identifier="test", width=3, length=3, height=3)
        flying_position = Position(0, 0, 1)
        result, _ = bin.pack_item(item, flying_position)
        self.assertFalse(result)

    def test_pack_item_stacked_items(self):
        bin = Bin(width=10, length=10, height=10)
        item1 = SingleItem(identifier="test", width=3, length=3, height=3)
        position = Position(0, 0, 0)
        bin.pack_item(item1, position)

        item2 = SingleItem(identifier="test2", width=3, length=3, height=3)
        position = Position(0, 0, 3)
        result, info = bin.pack_item(item2, position)
        print(info)
        self.assertTrue(result)

    def test_pack_item_stacked_items_allowed_overhang(self):
        bin = Bin(width=10, length=10, height=10)
        item = SingleItem(identifier="test", width=3, length=3, height=3)
        position = Position(0, 0, 0)
        bin.pack_item(item, position)

        valid_item = SingleItem(identifier="test", width=4, length=3, height=3)
        position = Position(0, 0, 3)
        result, info = bin.pack_item(valid_item, position)
        print(info)
        self.assertTrue(result)

    def test_pack_item_stacked_items_too_much_overhang(self):
        bin = Bin(width=10, length=10, height=10)
        item = SingleItem(identifier="test", width=3, length=3, height=3)
        position = Position(0, 0, 0)
        bin.pack_item(item, position)

        item = SingleItem(identifier="test", width=3, length=3, height=3)
        too_much_overhang_position = Position(2, 0, 3)
        result, _ = bin.pack_item(item, too_much_overhang_position)
        self.assertFalse(result)

    def test_pack_item_out_of_bounds(self):
        bin = Bin(width=10, length=10, height=10)
        item = SingleItem(identifier="test", width=5, length=5, height=5)
        position = Position(7, 7, 7)
        result, _ = bin.pack_item(item, position)

        self.assertFalse(result)
        self.assertEqual(len(bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(bin.heightmap), 0)

    def test_pack_item_position_occupied(self):
        bin = Bin(width=10, length=10, height=10)
        item1 = SingleItem(identifier="test", width=4, length=4, height=4)
        position = Position(0, 0, 0)
        bin.pack_item(item1, position)

        item = SingleItem(identifier="test", width=2, length=2, height=2)
        position = Position(1, 1, 1)
        result, _ = bin.pack_item(item, position)
        self.assertFalse(result)
        self.assertEqual(len(bin.packed_items), 1)
        self.assertEqual(np.count_nonzero(bin.heightmap), item1.width)

    def test_pack_item_with_none_position(self):
        bin = Bin(width=10, length=10, height=10)
        item = SingleItem(identifier="test", width=3, length=3, height=3)
        result, _ = bin.pack_item(item, None)
        self.assertFalse(result)
        self.assertEqual(len(bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(bin.heightmap), 0)

    def test_remove_item(self):
        bin = Bin(width=10, length=10, height=10)
        item1 = SingleItem(identifier="test1", width=3, length=3, height=3)
        position = Position(0, 0, 0)
        bin.pack_item(item1, position)
        expected_heightmap = bin.heightmap.copy()

        item2 = SingleItem(identifier="test2", width=4, length=3, height=1)
        position = Position(0, 0, 3)

        is_packed, _ = bin.pack_item(item2, position)
        result, info = bin.remove_item(item2)

        self.assertTrue(is_packed)
        self.assertTrue(result)
        self.assertIsNone(info)

        self.assertIsNone(item2.position)
        self.assertEqual(len(bin.packed_items), 1)
        self.assertTrue(np.array_equal(bin.heightmap, expected_heightmap))

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

    def test_get_dimension_2d(self):
        bin = Bin(width=50, length=60, height=70)

        dimensions = ["width", "length"]
        result = bin.get_dimension_2d(dimensions)
        self.assertEqual(result, [50, 60])

        dimensions = ["length", "height"]
        result = bin.get_dimension_2d(dimensions)
        self.assertEqual(result, [60, 70])

        dimensions = ["width", "height"]
        result = bin.get_dimension_2d(dimensions)
        self.assertEqual(result, [50, 70])

        with self.assertRaises(ValueError):
            dimensions = ["width", "length", "height"]
            bin.get_dimension_2d(dimensions)

        with self.assertRaises(ValueError):
            dimensions = ["width", "depth"]
            bin.get_dimension_2d(dimensions)

    def test_volume(self):
        bin = Bin(width=10, length=20, height=5)
        self.assertEqual(bin.volume, 1000)

    def test_used_volume(self):
        bin = Bin(width=10, length=20, height=5)
        bin.pack_item(
            SingleItem(
                identifier="test1",
                width=2,
                length=10,
                height=2,
            ),
            Position(x=0, y=0, z=0),
        )
        bin.pack_item(
            SingleItem(identifier="test2", width=3, length=5, height=2),
            Position(x=4, y=0, z=0),
        )
        self.assertEqual(bin.get_used_volume(), 40 + 30)
        self.assertEqual(bin.get_used_volume(use_percentage=True), 7)

    def test_heightmap_empty_bin(self):
        bin = Bin(width=10, length=10, height=10)

        expected_height_map = np.zeros((10), dtype=int)
        np.testing.assert_array_equal(bin.heightmap, expected_height_map)

    def test_heightmap_single_item(self):
        bin = Bin(width=10, length=10, height=10)
        # You need to import Item class or create it if not available
        item = SingleItem("test", width=1, length=1, height=1)
        bin.pack_item(item, Position(0, 0, 0))

        height_map = bin.heightmap
        expected_height_map = np.zeros((10), dtype=int)
        expected_height_map[0] = 1  # The packed item occupies this cell
        np.testing.assert_array_equal(height_map, expected_height_map)

    def test_heightmap_multiple_items(self):
        bin = Bin(width=10, length=10, height=10)
        item1 = SingleItem("test", 3, 10, 1)
        bin.pack_item(item1, Position(0, 0, 0))
        item2 = SingleItem("test", 3, 10, 2)
        bin.pack_item(item2, Position(3, 0, 0))
        item3 = SingleItem("test", 2, 5, 3)
        bin.pack_item(item3, Position(0, 0, 1))

        height_map = bin.heightmap

        expected_height_map = np.zeros((10), dtype=int)
        expected_height_map[0:2] = 4  # Item3 on top of Item1
        expected_height_map[2:3] = 1  # Item1
        expected_height_map[3:6] = 2  # Item2

        np.testing.assert_array_equal(height_map, expected_height_map)

    # Tests for the get_center_of_gravity function
    def test_get_center_of_gravity(self):
        bin = Bin(width=10, length=10, height=10)
        item1 = SingleItem("test", width=3, length=1, height=3, weight=1)
        item1.position = Position(x=1, y=0, z=1)  # center: 2.5, 0.5, 2.5

        item2 = SingleItem("test", width=2, length=1, height=2, weight=1)
        item2.position = Position(x=5, y=0, z=2)  # center: 6, 0.5, 3

        bin._packed_items = [item1, item2]

        cg_weight = bin.get_center_of_gravity()
        self.assertEqual(cg_weight.x, 4)  # (2.5*1 + 6*1) / (1+1) = 4.25 => 4
        self.assertEqual(cg_weight.y, 0)  # (0.5 + 0.5) / (1+1) = 0.5 => 0
        self.assertEqual(cg_weight.z, 2)  # (2.5*1 + 3*1) / (1+1) = 2.75 => 2

        cg_volume = bin.get_center_of_gravity(use_volume=True)
        self.assertEqual(cg_volume.x, 3)  # (2.5*9 + 6*4) / (9 + 4) = 3.5 => 3
        self.assertEqual(cg_volume.y, 0)  # 0.5*(9 + 4) / (9 + 4) = 0.5 => 0
        self.assertEqual(cg_volume.z, 2)  # (2.5*9 + 3*4) / (9 + 4) = 2.6 => 2

    def test_get_snappoints(self):
        bin = Bin(10, 1, 10)

        # Pack some items into the bin
        item1 = SingleItem("item1", 2, 1, 2)
        bin.pack_item(item1, Position(0, 0, 0))
        item2 = SingleItem("item2", 2, 1, 2)
        bin.pack_item(item2, Position(4, 0, 0))
        item3 = SingleItem("item3", 2, 1, 2)
        bin.pack_item(item3, Position(6, 0, 0))

        # Get the snap points
        snappoints = bin.get_snappoints()

        self.assertEqual(len(snappoints), 8)

        # Check if the snap points are as expected
        expected_snappoints = [
            Snappoint(x=0, y=0, z=2, direction=SnappointDirection.RIGHT),
            Snappoint(x=2, y=0, z=2, direction=SnappointDirection.LEFT),
            Snappoint(x=2, y=0, z=0, direction=SnappointDirection.RIGHT),
            Snappoint(x=4, y=0, z=0, direction=SnappointDirection.LEFT),
            Snappoint(x=4, y=0, z=2, direction=SnappointDirection.RIGHT),
            Snappoint(x=8, y=0, z=2, direction=SnappointDirection.LEFT),
            Snappoint(x=8, y=0, z=0, direction=SnappointDirection.RIGHT),
            Snappoint(x=10, y=0, z=0, direction=SnappointDirection.LEFT),
        ]

        self.assertEqual(snappoints, expected_snappoints)

    def test_get_snappoints_min_z(self):
        bin = Bin(10, 1, 10)

        # Pack some items into the bin
        item1 = SingleItem("item1", 2, 1, 4)
        bin.pack_item(item1, Position(0, 0, 0))
        item2 = SingleItem("item2", 2, 1, 2)
        bin.pack_item(item2, Position(4, 0, 0))
        item3 = SingleItem("item3", 2, 1, 2)
        bin.pack_item(item3, Position(6, 0, 0))

        # Get the snap points
        snappoints = bin.get_snappoints(min_z=2)

        self.assertEqual(len(snappoints), 4)

        # Check if the snap points are as expected
        expected_snappoints = [
            Snappoint(x=0, y=0, z=4, direction=SnappointDirection.RIGHT),
            Snappoint(x=2, y=0, z=4, direction=SnappointDirection.LEFT),
            Snappoint(x=2, y=0, z=2, direction=SnappointDirection.RIGHT),
            Snappoint(x=10, y=0, z=2, direction=SnappointDirection.LEFT),
        ]

        self.assertEqual(snappoints, expected_snappoints)

    def test_pack_item_with_overhang(self):
        bin = Bin(width=10, length=10, height=10, overhang_y_stability_factor=0.6)

        item = SingleItem(identifier="test", width=5, length=12, height=5)
        result, _ = bin.pack_item(item, Position(0, 0, 0))

        self.assertTrue(result)
        self.assertEqual(len(bin.packed_items), 1)
        self.assertEqual(np.count_nonzero(bin.heightmap), item.width)
        self.assertEqual(item.position.y, -1)

    def test_remove_item_with_overhang(self):
        bin = Bin(width=10, length=10, height=10, overhang_y_stability_factor=0.6)

        item = SingleItem(identifier="test", width=5, length=12, height=5)
        bin.pack_item(item, Position(0, 0, 0))
        prev_pos = item.position
        result, _ = bin.remove_item(item)

        self.assertEqual(prev_pos.y, -1)
        self.assertTrue(result)
        self.assertEqual(len(bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(bin.heightmap), 0)
        self.assertIsNone(item.position)

    def test_pack_item_too_much_overhang(self):
        bin = Bin(width=10, length=10, height=10, overhang_y_stability_factor=0.8)

        item = SingleItem(identifier="test", width=5, length=12, height=5)
        result, _ = bin.pack_item(item, Position(0, -6, 0))

        self.assertFalse(result)
        self.assertEqual(len(bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(bin.heightmap), 0)

    def test_pack_item_with_overhang_stack_multiple(self):
        bin = Bin(width=10, length=10, height=10, overhang_y_stability_factor=0.6)

        item1 = SingleItem(identifier="test", width=5, length=18, height=5)
        bin.pack_item(item1, Position(0, 0, 0))
        item2 = SingleItem(identifier="test", width=5, length=18, height=5)
        _, info = bin.pack_item(item2, Position(0, 0, 5))
        print(info)
        self.assertTrue(item1.is_packed)
        self.assertEqual(item1.position.y, -4)
        self.assertTrue(item2.is_packed)
        self.assertEqual(item2.position.y, -4)

    def test_get_gaps(self):
        bin = Bin(width=10, length=10, height=10)

        item1 = SingleItem(identifier="test1", width=2, length=10, height=2)
        bin.pack_item(item1, Position(0, 0, 0))
        item2 = SingleItem(identifier="test2", width=2, length=10, height=2)
        bin.pack_item(item2, Position(5, 0, 0))
        item2 = SingleItem(identifier="test3", width=2, length=10, height=2)
        bin.pack_item(item2, Position(5, 0, 2))

        gaps = bin.get_gaps()

        expected_gaps = [(2, 5)]

        self.assertEqual(gaps, expected_gaps)

    def test_remove_gaps(self):
        bin = Bin(width=10, length=10, height=10)

        item1 = SingleItem(identifier="test1", width=2, length=10, height=2)
        bin.pack_item(item1, Position(0, 0, 0))
        item2 = SingleItem(identifier="test2", width=2, length=10, height=2)
        bin.pack_item(item2, Position(5, 0, 0))
        item2 = SingleItem(identifier="test3", width=2, length=10, height=2)
        bin.pack_item(item2, Position(5, 0, 2))

        bin.remove_gaps()
        gaps = bin.get_gaps()

        expected_positions = {
            "test1": Position(0, 0, 0),
            "test2": Position(2, 0, 0),
            "test3": Position(2, 0, 2),
        }

        self.assertEqual(len(gaps), 0)
        self.assertEqual(len(bin.packed_items), 3)
        self.assertEqual(np.count_nonzero(bin.heightmap), 4)
        for name, pos in expected_positions.items():
            item = [i for i in bin.packed_items if i.identifier == name][0]
            self.assertEqual(item.position, pos)

    def test_pack_items(self):
        bin = Bin(width=10, length=10, height=10)

        items_and_positions = [
            (
                SingleItem(identifier="test1", width=2, length=10, height=2),
                Position(0, 0, 0),
            ),
            (
                SingleItem(identifier="test2", width=2, length=5, height=2),
                Position(2, 0, 0),
            ),
            (
                SingleItem(identifier="test3", width=2, length=5, height=2),
                Position(2, 5, 0),
            ),
        ]

        result, info = bin.pack_items(items_and_positions)

        self.assertIsNone(info)
        self.assertTrue(result)
        self.assertEqual(len(bin.packed_items), 3)
        self.assertEqual(np.count_nonzero(bin.heightmap), 4)

    def test_pack_items_overlapping_y(self):
        bin = Bin(width=10, length=10, height=10)

        items_and_positions = [
            (
                SingleItem(identifier="test1", width=2, length=10, height=2),
                Position(0, 0, 0),
            ),
            (
                SingleItem(identifier="test2", width=2, length=5, height=2),
                Position(2, 0, 0),
            ),
            (
                SingleItem(identifier="test3", width=2, length=5, height=2),
                Position(2, 4, 0),
            ),
        ]

        result, info = bin.pack_items(items_and_positions)

        self.assertIsNotNone(info)
        self.assertFalse(result)
        self.assertEqual(len(bin.packed_items), 1)


if __name__ == "__main__":
    unittest.main()
