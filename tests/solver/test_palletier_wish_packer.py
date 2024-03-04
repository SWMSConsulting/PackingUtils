import copy
import unittest

from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.single_item import SingleItem
from packutils.data.order import Order
from packutils.data.packer_configuration import (
    ItemGroupingMode,
    ItemSelectStrategy,
    PackerConfiguration,
)
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.solver.palletier_wish_packer import PalletierWishPacker
from packutils.visual.packing_visualization import PackingVisualization

# import logging
# logging.basicConfig(level=logging.INFO)


class TestPalletierWishPacker(unittest.TestCase):
    def setUp(self):
        self.vis = PackingVisualization()

    def test_pack_variant_no_item_packed(self):
        # All articles are larger than the bin
        articles = [
            Article(article_id="1", width=10, length=20, height=30, amount=2),
            Article(article_id="2", width=15, length=25, height=35, amount=1),
        ]
        order = Order(order_id="", articles=articles)
        self.packer = PalletierWishPacker(bins=[Bin(1, 1, 1)])

        packing_variant = self.packer.pack_variant(order)
        self.assertIsNotNone(packing_variant, "pack_variant returned None")
        original_item_ids = set(
            a.article_id for a in order.articles for _ in range(a.amount)
        )
        unpacked_item_ids = set(
            item.identifier for item in packing_variant.unpacked_items
        )

        self.assertEqual(
            original_item_ids,
            unpacked_item_ids,
            "Not all items are present in the unpacked list",
        )

    def test_pack_variant_largest_w_h_l(self):
        articles = [
            Article(article_id="1", width=4, length=1, height=4, amount=2),
            Article(article_id="2", width=8, length=1, height=2, amount=1),
        ]
        order = Order(order_id="", articles=articles)
        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_W_H_L,
            item_select_strategy_index=ItemSelectStrategy.LARGEST_W_H_L,
            mirror_walls=False,
            allow_item_exceeds_layer=False,
        )
        packer = PalletierWishPacker(bins=[Bin(10, 1, 10)])

        packing_variant = packer.pack_variant(order, config=config)

        # self.vis.visualize_packing_variant(packing_variant)

        self.assertIsNotNone(packing_variant, "pack_variant returned None")

        item1 = SingleItem(identifier="2", width=8, length=1, height=2)
        item1.pack(position=Position(0, 0, 0), index=0)

        item2 = SingleItem(identifier="1", width=4, length=1, height=4)
        item2.pack(position=Position(0, 0, 2), index=10)

        item3 = SingleItem(identifier="1", width=4, length=1, height=4)
        item3.pack(position=Position(4, 0, 2), index=20)

        expected_items = [item1, item2, item3]

        print(packing_variant.bins[0].packed_items)
        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 3)
        self.assertEqual(expected_items, packing_variant.bins[0].packed_items)

    def test_pack_variant_largest_volume(self):
        articles = [
            Article(article_id="1", width=4, length=1, height=4, amount=2),
            Article(article_id="2", width=7, length=1, height=2, amount=1),
        ]
        order = Order(order_id="", articles=articles)
        packer = PalletierWishPacker(bins=[Bin(10, 1, 10)])
        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            item_select_strategy_index=ItemSelectStrategy.LARGEST_VOLUME,
        )
        packing_variant = packer.pack_variant(order, config=config)

        # self.vis.visualize_packing_variant(packing_variant)

        self.assertIsNotNone(packing_variant, "pack_variant returned None")

        item1 = SingleItem(identifier="1", width=4, length=1, height=4)
        item1.pack(position=Position(0, 0, 0), index=0)

        item2 = SingleItem(identifier="1", width=4, length=1, height=4)
        item2.pack(position=Position(4, 0, 0), index=10)

        item3 = SingleItem(identifier="2", width=7, length=1, height=2)
        item3.pack(position=Position(0, 0, 4), index=20)

        expected_items = [item1, item2, item3]

        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 3)
        self.assertEqual(expected_items, packing_variant.bins[0].packed_items)

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

    def test_pack_item_on_snappoint(self):
        bin = Bin(width=10, length=1, height=10)
        item = SingleItem(identifier="1", width=5, length=1, height=5)
        packer = PalletierWishPacker(bins=[bin])

        # Create a Snappoint object
        snappoint_left = Snappoint(x=0, y=0, z=0, direction=SnappointDirection.RIGHT)
        snappoint_right = Snappoint(x=5, y=0, z=0, direction=SnappointDirection.LEFT)

        # Test packing item on the left snappoint
        result_left = packer.pack_item_on_snappoint(
            bin, copy.deepcopy(item), snappoint_left
        )
        self.assertTrue(result_left, "Failed to pack item on the left snappoint")

        bin = Bin(width=10, length=1, height=10)
        # Test packing item on the right snappoint
        result_right = packer.pack_item_on_snappoint(
            bin, copy.deepcopy(item), snappoint_right
        )
        self.assertTrue(result_right, "Failed to pack item on the right snappoint")

    def test_prepare_items_to_pack_no_grouping(self):
        articles = [
            Article(article_id="1", width=2, length=8, height=3, amount=2),
            Article(article_id="2", width=3, length=12, height=1, amount=1),
        ]
        order = Order(order_id="", articles=articles)
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        items_to_pack = packer.prepare_items_to_pack(order)

        expected_items = [
            SingleItem(identifier="1", width=2, length=8, height=3),
            SingleItem(identifier="1", width=2, length=8, height=3),
            SingleItem(identifier="2", width=3, length=12, height=1),
        ]

        self.assertEqual(len(items_to_pack), len(expected_items))
        for item, expected_item in zip(items_to_pack, expected_items):
            self.assertEqual(item.identifier, expected_item.identifier)
            self.assertEqual(item.width, expected_item.width)
            self.assertEqual(item.length, expected_item.length)
            self.assertEqual(item.height, expected_item.height)

    def test_prepare_items_to_pack_with_lengthwise_grouping(self):
        articles = [
            Article(article_id="1", width=2, length=10, height=4, amount=1),
            Article(article_id="2", width=4, length=5, height=4, amount=2),
            Article(article_id="3", width=6, length=2, height=6, amount=4),
        ]
        order = Order(order_id="", articles=articles)
        config = PackerConfiguration(item_grouping_mode=ItemGroupingMode.LENGTHWISE)
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        items_to_pack = packer.prepare_items_to_pack(order, config=config)
        flattened_items = sum([i.flatten() for i in items_to_pack], [])

        self.assertEqual(len(items_to_pack), 3)
        self.assertEqual(len(flattened_items), 7)

    def test_pack_variant_with_grouping(self):
        articles = [
            Article(article_id="1", width=5, length=4, height=5, amount=2),
            Article(article_id="2", width=3, length=2, height=3, amount=2),
        ]
        order = Order(order_id="", articles=articles)
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        config = PackerConfiguration(item_grouping_mode=ItemGroupingMode.LENGTHWISE)
        items_to_pack = packer.prepare_items_to_pack(order, config=config)

        packing_variant = packer.pack_variant(order, config)
        print(packing_variant)

        item1 = SingleItem(identifier="1", width=5, length=4, height=5)
        item1.pack(position=Position(0, 0, 0), index=0)
        item2 = SingleItem(identifier="1", width=5, length=4, height=5)
        item2.pack(position=Position(0, 4, 0), index=10)

        item3 = SingleItem(identifier="2", width=3, length=2, height=3)
        item3.pack(position=Position(5, 0, 0), index=20)
        item4 = SingleItem(identifier="2", width=3, length=2, height=3)
        item4.pack(position=Position(5, 2, 0), index=30)

        expected_items = [item1, item2, item3, item4]

        self.assertEqual(len(items_to_pack), 2)  # two groups expected
        self.assertIsNotNone(packing_variant, "pack_variant returned None")

        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 4)
        self.assertEqual(packing_variant.bins[0].packed_items, expected_items)

    def test_pack_variant_with_grouping_and_overhang(self):
        articles = [
            Article(article_id="1", width=5, length=4, height=5, amount=2),
            Article(article_id="2", width=3, length=6, height=3, amount=2),
        ]
        order = Order(order_id="", articles=articles)
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        config = PackerConfiguration(
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            overhang_y_stability_factor=0.6,
            item_grouping_mode=ItemGroupingMode.LENGTHWISE,
        )
        items_to_pack = packer.prepare_items_to_pack(order, config=config)

        packing_variant = packer.pack_variant(order, config)
        print(packing_variant)

        item1 = SingleItem(identifier="1", width=5, length=4, height=5)
        item1.pack(position=Position(0, 0, 0), index=0)
        item2 = SingleItem(identifier="1", width=5, length=4, height=5)
        item2.pack(position=Position(0, 4, 0), index=10)

        item3 = SingleItem(identifier="2", width=3, length=6, height=3)
        item3.pack(position=Position(5, -1, 0), index=20)
        item4 = SingleItem(identifier="2", width=3, length=6, height=3)
        item4.pack(position=Position(5, 5, 0), index=30)

        expected_items = [item1, item2, item3, item4]

        self.assertEqual(len(items_to_pack), 2)  # two groups expected
        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.unpacked_items), 0)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 4)
        self.assertEqual(packing_variant.bins[0].packed_items, expected_items)


if __name__ == "__main__":
    unittest.main()
