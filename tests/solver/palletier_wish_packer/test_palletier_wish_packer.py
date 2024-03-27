import copy
import unittest

from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.single_item import SingleItem
from packutils.data.order import Order
from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration
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

    def test_avoid_multiple_pallets(self):

        bin = Bin(10, 10, 10)

        config = PackerConfiguration(mirror_walls=True)

        order = Order(
            order_id="1",
            articles=[Article(article_id="1", width=8, length=10, height=1, amount=3)],
        )

        packer = PalletierWishPacker(bins=[bin])
        variant = packer.pack_variant(order=order, config=config)

        self.assertEqual(len(variant.unpacked_items), 0)
        self.assertEqual(len(variant.bins), 1)


if __name__ == "__main__":
    unittest.main()
