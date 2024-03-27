import unittest

from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.packer_configuration import (
    ItemGroupingMode,
    ItemSelectStrategy,
    PackerConfiguration,
)
from packutils.data.position import Position
from packutils.data.single_item import SingleItem
from packutils.solver.palletier_wish_packer import PalletierWishPacker


class TestLengthwiseGrouping(unittest.TestCase):

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
        item1.pack(position=Position(0, 1, 0), index=0)
        item2 = SingleItem(identifier="1", width=5, length=4, height=5)
        item2.pack(position=Position(0, 5, 0), index=10)

        item3 = SingleItem(identifier="2", width=3, length=2, height=3)
        item3.pack(position=Position(5, 3, 0), index=20)
        item4 = SingleItem(identifier="2", width=3, length=2, height=3)
        item4.pack(position=Position(5, 5, 0), index=30)

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

        config = PackerConfiguration(
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            overhang_y_stability_factor=0.6,
            item_grouping_mode=ItemGroupingMode.LENGTHWISE,
        )
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10, max_length=12)])
        packer.reset(config)

        items_to_pack = packer.prepare_items_to_pack(order, config=config)

        packing_variant = packer.pack_variant(order, config)

        item1 = SingleItem(identifier="1", width=5, length=4, height=5)
        item1.pack(position=Position(0, 1, 0), index=0)
        item2 = SingleItem(identifier="1", width=5, length=4, height=5)
        item2.pack(position=Position(0, 5, 0), index=10)

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

    def test_pack_variant_with_grouping_max_length_reached(self):
        articles = [
            Article(article_id="1", width=5, length=6, height=5, amount=3),
        ]
        order = Order(order_id="", articles=articles)

        config = PackerConfiguration(
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            overhang_y_stability_factor=0.6,
            item_grouping_mode=ItemGroupingMode.LENGTHWISE,
        )
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10, max_length=12)])
        packer.reset(config)

        items_to_pack = packer.prepare_items_to_pack(order, config=config)

        packing_variant = packer.pack_variant(order, config)

        item1 = SingleItem(identifier="1", width=5, length=6, height=5)
        item1.pack(position=Position(0, -1, 0), index=0)
        item2 = SingleItem(identifier="1", width=5, length=6, height=5)
        item2.pack(position=Position(0, 5, 0), index=10)
        item3 = SingleItem(identifier="1", width=5, length=6, height=5)
        item3.pack(position=Position(5, 2, 0), index=20)

        expected_items = [item1, item2, item3]

        self.assertEqual(len(items_to_pack), 2)  # two groups expected
        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.unpacked_items), 0)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 3)
        self.assertEqual(packing_variant.bins[0].packed_items, expected_items)
