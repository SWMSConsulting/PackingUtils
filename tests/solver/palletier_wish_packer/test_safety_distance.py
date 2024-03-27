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
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.solver.palletier_wish_packer import (
    PalletierWishPacker,
    is_safety_distance_required,
)


class TestSafetyDistance(unittest.TestCase):

    def test_pack_with_safety_distance(self):
        articles = [
            Article(article_id="1", width=5, length=10, height=5, amount=1),
            Article(article_id="2", width=3, length=10, height=3, amount=1),
        ]
        order = Order(order_id="", articles=articles)

        config = PackerConfiguration(
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            overhang_y_stability_factor=0.6,
            item_grouping_mode=ItemGroupingMode.LENGTHWISE,
        )

        packer = PalletierWishPacker(
            bins=[Bin(10, 10, 10)], safety_distance_smaller_articles=1
        )
        packer.reset(config)

        packing_variant = packer.pack_variant(order, config)

        for p in packing_variant.bins[0].packed_items:
            print(p.position.x)

        item1 = SingleItem(identifier="1", width=5, length=10, height=5)
        item1.pack(position=Position(0, 0, 0), index=0)

        item2 = SingleItem(identifier="2", width=3, length=10, height=3)
        item2.pack(position=Position(6, 0, 0), index=10)  # added padding of 1

        expected_items = [item1, item2]

        self.assertEqual(len(packing_variant.unpacked_items), 0)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 2)
        self.assertEqual(packing_variant.bins[0].packed_items, expected_items)
        self.assertEqual(
            [p.position for p in packing_variant.bins[0].packed_items],
            [p.position for p in expected_items],
        )

    def test_is_safety_distance_required_none(self):

        bin = Bin(10, 10, 10)

        item1 = SingleItem(identifier="higher", width=3, length=10, height=5)
        bin.pack_item(item1, Position(0, 0, 0))

        item2 = SingleItem(identifier="2", width=3, length=10, height=3)
        position = Snappoint(3, 0, 0, SnappointDirection.RIGHT)

        required = is_safety_distance_required(item2, position, bin, 0, 10)
        self.assertFalse(required)

    def test_is_safety_distance_required_not_needed(self):

        bin = Bin(10, 10, 10)

        item1 = SingleItem(identifier="same height", width=3, length=10, height=3)
        bin.pack_item(item1, Position(0, 0, 0))

        item2 = SingleItem(identifier="2", width=3, length=10, height=3)
        position = Snappoint(3, 0, 0, SnappointDirection.RIGHT)

        required = is_safety_distance_required(item2, position, bin, 1, 10)
        self.assertFalse(required)

    def test_is_safety_distance_required_valid(self):

        bin = Bin(10, 10, 10)

        item1 = SingleItem(identifier="higher", width=3, length=10, height=5)
        bin.pack_item(item1, Position(0, 0, 0))

        item2 = SingleItem(identifier="2", width=3, length=10, height=3)
        position = Snappoint(3, 0, 0, SnappointDirection.RIGHT)

        required = is_safety_distance_required(item2, position, bin, 1, 10)
        self.assertTrue(required)

    def test_is_safety_distance_required_valid_left(self):

        bin = Bin(10, 10, 10)

        item1 = SingleItem(identifier="higher", width=3, length=10, height=5)
        bin.pack_item(item1, Position(0, 0, 0))

        item2 = SingleItem(identifier="2", width=3, length=10, height=3)
        position = Snappoint(6, 0, 0, SnappointDirection.LEFT)

        required = is_safety_distance_required(item2, position, bin, 1, 10)
        self.assertTrue(required)

    def test_is_safety_distance_required_min_width(self):

        bin = Bin(10, 10, 10)

        item1 = SingleItem(identifier="higher", width=3, length=10, height=5)
        bin.pack_item(item1, Position(0, 0, 0))

        item2 = SingleItem(identifier="2", width=3, length=10, height=3)
        position = Snappoint(6, 0, 0, SnappointDirection.LEFT)

        required = is_safety_distance_required(item2, position, bin, 1, 3)
        self.assertFalse(required)
