import unittest
import numpy as np

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection


class TestBin(unittest.TestCase):
    def setUp(self):
        self.bin = Bin(width=10, length=10, height=10)

    def test_pack_item_successful(self):
        item = Item(id="test", width=3, length=3, height=3, position=Position(0, 0, 0))
        result, _ = self.bin.pack_item(item)

        self.assertTrue(result)
        self.assertEqual(len(self.bin.packed_items), 1)
        self.assertEqual(np.count_nonzero(self.bin.heightmap), 9)

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
        bin.pack_item(
            Item(id="test", width=3, length=3, height=3, position=Position(0, 0, 0))
        )
        valid_item = Item(
            id="test", width=3, length=3, height=3, position=Position(0, 0, 3)
        )
        result, _ = bin.pack_item(valid_item)
        self.assertTrue(result)

        # item is placed fully on top of other item with small overhang
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            Item(id="test", width=3, length=3, height=3, position=Position(0, 0, 0))
        )
        valid_item = Item(
            id="test", width=4, length=3, height=3, position=Position(0, 0, 3)
        )
        result, _ = bin.pack_item(valid_item)
        self.assertTrue(result)

        # item is placed fully on top of other item with too much overhang
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            Item(id="test", width=3, length=3, height=3, position=Position(0, 0, 0))
        )
        too_much_overhang_item = Item(
            id="test", width=3, length=3, height=3, position=Position(2, 0, 3)
        )
        result, _ = bin.pack_item(too_much_overhang_item)
        self.assertFalse(result)

    def test_pack_item_out_of_bounds(self):
        item = Item(id="test", width=5, length=5, height=5, position=Position(7, 7, 7))
        result, _ = self.bin.pack_item(item)

        self.assertFalse(result)
        self.assertEqual(len(self.bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(self.bin.heightmap), 0)

    def test_pack_item_position_occupied(self):
        item1 = Item(id="test", width=4, length=4, height=4, position=Position(0, 0, 0))
        item2 = Item(id="test", width=2, length=2, height=2, position=Position(1, 1, 1))
        self.bin.pack_item(item1)
        result, _ = self.bin.pack_item(item2)
        self.assertFalse(result)
        self.assertEqual(len(self.bin.packed_items), 1)
        self.assertEqual(
            np.count_nonzero(self.bin.heightmap), item1.width * item1.length
        )

    def test_pack_item_with_none_position(self):
        item = Item(id="test", width=3, length=3, height=3)
        result, _ = self.bin.pack_item(item)
        self.assertFalse(result)
        self.assertEqual(len(self.bin.packed_items), 0)
        self.assertEqual(np.count_nonzero(self.bin.heightmap), 0)

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
        bin.pack_item(
            Item(
                id="test1",
                width=2,
                length=10,
                height=2,
                position=Position(x=0, y=0, z=0),
            )
        )
        bin.pack_item(
            Item(
                id="test2",
                width=3,
                length=5,
                height=2,
                position=Position(x=4, y=0, z=0),
            )
        )
        self.assertEqual(bin.get_used_volume(), 40 + 30)
        self.assertEqual(bin.get_used_volume(use_percentage=True), 7)

    def test_heightmap_empty_bin(self):
        height_map = self.bin.heightmap
        expected_height_map = np.zeros((10, 10), dtype=int)
        np.testing.assert_array_equal(height_map, expected_height_map)

    def test_heightmap_single_item(self):
        # You need to import Item class or create it if not available
        item = Item("test", width=1, length=1, height=1, position=Position(0, 0, 0))
        self.bin.pack_item(item)

        height_map = self.bin.heightmap
        expected_height_map = np.zeros((10, 10), dtype=int)
        expected_height_map[0, 0] = 1  # The packed item occupies this cell
        np.testing.assert_array_equal(height_map, expected_height_map)

    def test_heightmap_multiple_items(self):
        item1 = Item("test", 2, 2, 1, position=Position(0, 0, 0))
        item2 = Item("test", 3, 1, 2, position=Position(2, 0, 0))
        item3 = Item("test", 1, 3, 3, position=Position(0, 2, 0))
        self.bin.pack_item(item1)
        self.bin.pack_item(item2)
        self.bin.pack_item(item3)

        height_map = self.bin.heightmap

        expected_height_map = np.zeros((10, 10), dtype=int)
        expected_height_map[0:2, 0:2] = 1  # Item1
        expected_height_map[0:1, 2:5] = 2  # Item2
        expected_height_map[2:5, 0:1] = 3  # Item3

        np.testing.assert_array_equal(height_map, expected_height_map)

    # Tests for the get_center_of_gravity function
    def test_get_center_of_gravity(self):
        bin = Bin(width=10, length=10, height=10)
        item1 = Item("test", width=3, length=1, height=3, weight=1)
        item1.position = Position(x=1, y=0, z=1)  # center: 2.5, 0.5, 2.5

        item2 = Item("test", width=2, length=1, height=2, weight=1)
        item2.position = Position(x=5, y=0, z=2)  # center: 6, 0.5, 3

        bin.packed_items = [item1, item2]

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
        item1 = Item("item1", 2, 1, 2, position=Position(0, 0, 0))
        item2 = Item("item2", 2, 1, 2, position=Position(4, 0, 0))
        item3 = Item("item3", 2, 1, 2, position=Position(6, 0, 0))

        bin.pack_item(item1)
        bin.pack_item(item2)
        bin.pack_item(item3)

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
        item1 = Item("item1", 2, 1, 4, position=Position(0, 0, 0))
        item2 = Item("item2", 2, 1, 2, position=Position(4, 0, 0))
        item3 = Item("item3", 2, 1, 2, position=Position(6, 0, 0))

        bin.pack_item(item1)
        bin.pack_item(item2)
        bin.pack_item(item3)

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


if __name__ == "__main__":
    unittest.main()
