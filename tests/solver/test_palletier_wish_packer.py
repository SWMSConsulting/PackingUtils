import copy
import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.order import Order
from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration
from packutils.data.packing_variant import PackingVariant
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.solver.palletier_wish_packer import PalletierWishPacker
from packutils.visual.packing_visualization import PackingVisualization

import logging

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
        unpacked_item_ids = set(item.id for item in packing_variant.unpacked_items)

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
        expected_items = [
            Item("2", width=8, length=1, height=2, position=Position(0, 0, 0)),
            Item("1", width=4, length=1, height=4, position=Position(0, 0, 2)),
            Item("1", width=4, length=1, height=4, position=Position(4, 0, 2)),
        ]
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
        expected_items = [
            Item("1", width=4, length=1, height=4, position=Position(0, 0, 0)),
            Item("1", width=4, length=1, height=4, position=Position(4, 0, 0)),
            Item("2", width=7, length=1, height=2, position=Position(0, 0, 4)),
        ]
        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 3)
        self.assertEqual(expected_items, packing_variant.bins[0].packed_items)

    def test_get_best_item_to_pack_no_item_fit(self):
        bin = Bin(1, 1, 1)
        self.packer = PalletierWishPacker(bins=[bin])
        items = [
            Item(id="1", width=2, length=1, height=30),
            Item(id="2", width=3, length=1, height=35),
            Item(id="3", width=4, length=1, height=30),
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
        bin.pack_item(Item(id="", width=3, length=1, height=10), Position(0, 0, 0))
        bin.pack_item(Item(id="", width=4, length=1, height=8), Position(6, 0, 0))
        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_H_W_L,
            default_select_strategy=ItemSelectStrategy.LARGEST_H_W_L,
            allow_item_exceeds_layer=False,
        )
        packer = PalletierWishPacker(bins=[bin])
        packer.reset(config)
        items = [
            Item(id="best", width=3, length=1, height=10),
            Item(id="best2", width=2, length=1, height=9),
            Item(id="best3", width=3, length=1, height=8),
            Item(id="toolarge", width=3, length=1, height=11),
            Item(id="toolarge", width=4, length=1, height=10),
        ]

        for expected_item in copy.deepcopy(items):
            item = packer.get_best_item_to_pack(
                items=copy.deepcopy(items),
                bin=bin,
                snappoint=Snappoint(3, 0, 0, SnappointDirection.RIGHT),
                max_z=10,
            )
            ex_item = expected_item if expected_item.id.startswith("best") else None
            self.assertEqual(ex_item, item)

            items.remove(expected_item)
        # self.vis.visualize_bin(bin)

    def test_get_best_item_to_pack_largest_volume(self):
        bin = Bin(10, 1, 15)
        bin.pack_item(Item(id="", width=3, length=1, height=10), Position(0, 0, 0))
        bin.pack_item(Item(id="", width=4, length=1, height=8), Position(6, 0, 0))
        packer = PalletierWishPacker(bins=[bin])

        config = PackerConfiguration(
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            allow_item_exceeds_layer=False,
        )
        packer.reset(config)

        items = [
            Item(id="best1", width=3, length=1, height=10),
            Item(id="best2", width=3, length=1, height=8),
            Item(id="best3", width=2, length=1, height=9),
            Item(id="toolarge", width=3, length=1, height=11),
            Item(id="toolarge", width=4, length=1, height=10),
        ]

        for expected_item in copy.deepcopy(items):
            item = packer.get_best_item_to_pack(
                items=copy.deepcopy(items),
                bin=bin,
                snappoint=Snappoint(3, 0, 0, SnappointDirection.RIGHT),
                max_z=10,
            )
            ex_item = expected_item if expected_item.id.startswith("best") else None
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
            Item(id="item1", width=9, length=1, height=5),
            Item(id="item2", width=5, length=1, height=1),
            Item(id="item3", width=4, length=1, height=3),
            Item(id="item4", width=3, length=1, height=3),
            Item(id="item5", width=2, length=1, height=3),
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
            Item(id="item1", width=9, length=1, height=5),
            Item(id="item2", width=3, length=1, height=4),
            Item(id="item3", width=3, length=1, height=3),
            Item(id="item4", width=2, length=1, height=2),
            Item(id="item5", width=5, length=1, height=1),
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
        item = Item(id="1", width=5, length=1, height=5)
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

    def test_fill_gaps_no_gap(self):
        bin = Bin(width=10, length=1, height=2)
        bin.pack_item(Item("", width=5, length=1, height=1), Position(0, 0, 0))
        bin.pack_item(Item("", width=5, length=1, height=1), Position(5, 0, 0))

        packer = PalletierWishPacker(bins=[bin], fill_gaps=True)
        changed = packer._fill_gaps(bin, min_z=0)
        self.assertFalse(changed)

    def test_fill_gaps_empty_bin(self):
        bin = Bin(width=10, length=1, height=2)
        packer = PalletierWishPacker(bins=[bin], fill_gaps=True)
        changed = packer._fill_gaps(bin, min_z=0)
        self.assertFalse(changed)

    def test_fill_gaps_single_item(self):
        bin = Bin(width=10, length=1, height=2)
        bin.pack_item(Item("", width=5, length=1, height=1, position=Position(5, 0, 0)))

        packer = PalletierWishPacker(bins=[bin], fill_gaps=True)
        changed = packer._fill_gaps(bin, min_z=0)

        self.assertTrue(changed)
        self.assertEqual(bin.packed_items[0].position, Position(2, 0, 0))

    def test_fill_gaps_single_item(self):
        return
        bin = Bin(width=10, length=1, height=8)
        bin.pack_item(Item("", width=5, length=1, height=2, position=Position(0, 0, 0)))
        bin.pack_item(Item("", width=3, length=1, height=2, position=Position(5, 0, 0)))
        bin.pack_item(Item("", width=2, length=1, height=2, position=Position(0, 0, 2)))
        bin.pack_item(Item("", width=2, length=1, height=2, position=Position(6, 0, 2)))

        packer = PalletierWishPacker(bins=[bin], fill_gaps=True)
        changed = packer._fill_gaps(bin, min_z=2)
        vis = PackingVisualization()
        vis.visualize_bin(bin)

        self.assertTrue(changed)
        # staying the same
        self.assertEqual(bin.packed_items[0].position, Position(0, 0, 0))
        self.assertEqual(bin.packed_items[1].position, Position(5, 0, 0))
        # updated
        self.assertEqual(bin.packed_items[-2].position, Position(2, 0, 0))
        self.assertEqual(bin.packed_items[-1].position, Position(4, 0, 0))


if __name__ == "__main__":
    unittest.main()
