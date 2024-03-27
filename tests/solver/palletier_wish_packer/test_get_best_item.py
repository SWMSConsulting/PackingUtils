import copy
import unittest

from packutils.data.bin import Bin
from packutils.data.single_item import SingleItem
from packutils.data.packer_configuration import (
    ItemSelectStrategy,
    PackerConfiguration,
)
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.solver.palletier_wish_packer import PalletierWishPacker


class TestGetBestItem(unittest.TestCase):

    def test_get_best_item_to_pack_no_item_fit(self):
        bin = Bin(1, 1, 1)
        self.packer = PalletierWishPacker(bins=[bin])
        items = [
            SingleItem(identifier="1", width=2, length=1, height=30),
            SingleItem(identifier="2", width=3, length=1, height=35),
            SingleItem(identifier="3", width=4, length=1, height=30),
        ]

        item = self.packer.get_best_item_to_pack(
            items=items,
            bin=bin,
            snappoint=Snappoint(0, 0, 0, SnappointDirection.RIGHT),
            max_z=100,
        )

        self.assertIsNone(item)

    def test_get_best_item_to_pack_largest_volume_for_gap(self):
        bin = Bin(10, 1, 15)
        bin.pack_item(
            SingleItem(identifier="", width=3, length=1, height=10), Position(0, 0, 0)
        )
        bin.pack_item(
            SingleItem(identifier="", width=4, length=1, height=8), Position(6, 0, 0)
        )
        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_H_W_L,
            default_select_strategy=ItemSelectStrategy.LARGEST_H_W_L,
            allow_item_exceeds_layer=False,
        )
        packer = PalletierWishPacker(bins=[bin])
        packer.reset(config)
        items = [
            SingleItem(identifier="best", width=3, length=1, height=10),
            SingleItem(identifier="best2", width=2, length=1, height=9),
            SingleItem(identifier="best3", width=3, length=1, height=8),
            SingleItem(identifier="toolarge", width=3, length=1, height=11),
            SingleItem(identifier="toolarge", width=4, length=1, height=10),
        ]

        for expected_item in copy.deepcopy(items):
            item = packer.get_best_item_to_pack(
                items=copy.deepcopy(items),
                bin=bin,
                snappoint=Snappoint(3, 0, 0, SnappointDirection.RIGHT),
                max_z=10,
            )
            ex_item = (
                expected_item if expected_item.identifier.startswith("best") else None
            )
            self.assertEqual(ex_item, item)

            items.remove(expected_item)
        # self.vis.visualize_bin(bin)

    def test_get_best_item_to_pack_largest_volume(self):
        bin = Bin(10, 1, 15)
        bin.pack_item(
            SingleItem(identifier="", width=3, length=1, height=10), Position(0, 0, 0)
        )
        bin.pack_item(
            SingleItem(identifier="", width=4, length=1, height=8), Position(6, 0, 0)
        )
        packer = PalletierWishPacker(bins=[bin])

        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            allow_item_exceeds_layer=False,
        )
        packer.reset(config)

        items = [
            SingleItem(identifier="best1", width=3, length=1, height=10),
            SingleItem(identifier="best2", width=3, length=1, height=8),
            SingleItem(identifier="best3", width=2, length=1, height=9),
            SingleItem(identifier="toolarge", width=3, length=1, height=11),
            SingleItem(identifier="toolarge", width=4, length=1, height=10),
        ]

        for expected_item in copy.deepcopy(items):
            item = packer.get_best_item_to_pack(
                items=copy.deepcopy(items),
                bin=bin,
                snappoint=Snappoint(3, 0, 0, SnappointDirection.RIGHT),
                max_z=10,
            )
            ex_item = (
                expected_item if expected_item.identifier.startswith("best") else None
            )
            self.assertEqual(ex_item, item)

            items.remove(expected_item)
        # self.vis.visualize_bin(bin)

    def test_get_best_item_to_pack_largest_w_h_l(self):
        bin = Bin(10, 1, 15)
        packer = PalletierWishPacker(bins=[bin])
        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_W_H_L,
        )
        packer.reset(config)

        items = [
            SingleItem(identifier="item1", width=9, length=1, height=5),
            SingleItem(identifier="item2", width=5, length=1, height=1),
            SingleItem(identifier="item3", width=4, length=1, height=3),
            SingleItem(identifier="item4", width=3, length=1, height=3),
            SingleItem(identifier="item5", width=2, length=1, height=3),
        ]

        for expected_item in copy.deepcopy(items):
            item = packer.get_best_item_to_pack(
                items=copy.deepcopy(items),
                bin=bin,
                snappoint=Snappoint(0, 0, 0, SnappointDirection.RIGHT),
                max_z=100,
            )
            self.assertEqual(expected_item, item)

            items.remove(expected_item)
        # self.vis.visualize_bin(bin)

    def test_get_best_item_to_pack_largest_h_w_l(self):
        bin = Bin(10, 1, 15)
        packer = PalletierWishPacker(bins=[bin])
        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_H_W_L,
        )
        packer.reset(config)

        items = [
            SingleItem(identifier="item1", width=9, length=1, height=5),
            SingleItem(identifier="item2", width=3, length=1, height=4),
            SingleItem(identifier="item3", width=3, length=1, height=3),
            SingleItem(identifier="item4", width=2, length=1, height=2),
            SingleItem(identifier="item5", width=5, length=1, height=1),
        ]

        for expected_item in copy.deepcopy(items):
            item = packer.get_best_item_to_pack(
                items=copy.deepcopy(items),
                bin=bin,
                snappoint=Snappoint(0, 0, 0, SnappointDirection.RIGHT),
                max_z=100,
            )
            self.assertEqual(expected_item, item)

            items.remove(expected_item)
        # self.vis.visualize_bin(bin)
