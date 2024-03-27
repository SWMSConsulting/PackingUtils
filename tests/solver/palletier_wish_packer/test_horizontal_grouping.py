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


class TestHorizontalGrouping(unittest.TestCase):

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

    def test_prepare_items_to_pack_with_horizontal_grouping(self):
        articles = [
            Article(article_id="1", width=2, length=10, height=4, amount=2),
            Article(article_id="2", width=4, length=10, height=4, amount=1),
        ]
        order = Order(order_id="", articles=articles)
        config = PackerConfiguration(group_narrow_items_w=3)
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        items_to_pack = packer.prepare_items_to_pack(order, config=config)
        flattened_items = sum([i.flatten() for i in items_to_pack], [])

        self.assertEqual(len(items_to_pack), 2)
        self.assertEqual(len(flattened_items), 3)

    def test_prepare_items_to_pack_with_horizontal_and_lengthwise_grouping(self):
        articles = [
            Article(article_id="1", width=2, length=5, height=4, amount=4),
        ]
        order = Order(order_id="", articles=articles)
        config = PackerConfiguration(
            item_grouping_mode=ItemGroupingMode.LENGTHWISE, group_narrow_items_w=3
        )
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        items_to_pack = packer.prepare_items_to_pack(order, config=config)
        flattened_items = sum([i.flatten() for i in items_to_pack], [])

        self.assertEqual(len(items_to_pack), 1)
        self.assertEqual(len(flattened_items), 4)

    def test_pack_items_with_horizontal_grouping(self):
        articles = [
            Article(article_id="1", width=2, length=10, height=4, amount=2),
        ]
        order = Order(order_id="", articles=articles)
        config = PackerConfiguration(
            item_grouping_mode=ItemGroupingMode.LENGTHWISE, group_narrow_items_w=3
        )
        packer = PalletierWishPacker(bins=[Bin(10, 10, 10)])

        items_to_pack = packer.prepare_items_to_pack(order, config=config)

        group = items_to_pack[0]
        group.pack(Position(2, 0, 0), 1)

        item1 = SingleItem(identifier="1", width=2, length=10, height=4)
        item1.pack(Position(2, 0, 0), 1)

        item2 = SingleItem(identifier="1", width=2, length=10, height=4)
        item2.pack(Position(4, 0, 0), 1)

        self.assertEqual(len(items_to_pack), 1)
        self.assertTrue(group.flatten().count(item1) == 1)
        self.assertTrue(group.flatten().count(item2) == 1)
