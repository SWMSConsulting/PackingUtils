import copy
import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection
from packutils.solver.palletier_wish_packer import Layer, LayerScoreStrategy, PalletierWishPacker
from packutils.visual.packing_visualization import PackingVisualization


class TestPalletierWishPacker(unittest.TestCase):

    def test_pack_variant_no_item_packed(self):

        # All articles are larger than the bin
        articles = [
            Article(article_id='1', width=10, length=20, height=30, amount=2),
            Article(article_id='2', width=15, length=25, height=35, amount=1)
        ]
        order = Order(order_id="", articles=articles)
        self.packer = PalletierWishPacker(bins=[Bin(1, 1, 1)])

        packing_variant = self.packer.pack_variant(order)
        self.assertIsNotNone(packing_variant, "pack_variant returned None")
        original_item_ids = set(
            a.article_id for a in order.articles for _ in range(a.amount))
        unpacked_item_ids = set(
            item.id for item in packing_variant.unpacked_items)

        self.assertEqual(original_item_ids, unpacked_item_ids,
                         "Not all items are present in the unpacked list")

    def test_pack_variant(self):

        articles = [
            Article(article_id='1', width=4, length=1, height=4, amount=2),
            Article(article_id='2', width=7, length=1, height=2, amount=1)
        ]
        order = Order(order_id="", articles=articles)
        self.packer = PalletierWishPacker(bins=[Bin(10, 1, 10)])

        packing_variant = self.packer.pack_variant(order)

        self.assertIsNotNone(packing_variant, "pack_variant returned None")
        expected_items = [
            Item("2", width=7, length=1, height=2, position=Position(0, 0, 0)),
            Item("1", width=4, length=1, height=4, position=Position(0, 0, 2)),
            Item("1", width=4, length=1, height=4, position=Position(4, 0, 2)),
        ]
        self.assertEqual(len(packing_variant.bins), 1)
        self.assertEqual(len(packing_variant.bins[0].packed_items), 3)
        self.assertEqual(expected_items, packing_variant.bins[0].packed_items)

    def test_get_candidate_layers(self):

        self.packer = PalletierWishPacker(
            bins=[Bin(1, 1, 1)],
            layer_score_strategy=LayerScoreStrategy.MIN_HEIGHT_VARIANCE
        )
        items = [
            Item(id='1', width=1, length=1, height=30),
            Item(id='2', width=1, length=1, height=35),
            Item(id='3', width=1, length=1, height=30)
        ]

        expected_candidates = [Layer(30, -5), Layer(35, -10)]
        layers = self.packer.get_candidate_layers(items)

        self.assertEqual(expected_candidates, layers)

        scores = [layer.score for layer in layers]
        self.assertEqual(scores, sorted(scores, reverse=True),
                         "Layers are not sorted by score")

    def test_get_best_item_to_pack_no_item_fit(self):

        self.packer = PalletierWishPacker(
            bins=[Bin(1, 1, 1)],
            layer_score_strategy=LayerScoreStrategy.MIN_HEIGHT_VARIANCE
        )
        items = [
            Item(id='1', width=2, length=1, height=30),
            Item(id='2', width=3, length=1, height=35),
            Item(id='3', width=4, length=1, height=30)
        ]

        item, _ = self.packer.get_best_item_to_pack(
            items,
            max_len_x=1,
            max_len_z=3,
            gap_len_z=2)

        self.assertIsNone(item)

    def test_get_best_item_to_pack(self):
        packer = PalletierWishPacker(
            bins=[Bin(1, 1, 1)],
            layer_score_strategy=LayerScoreStrategy.MIN_HEIGHT_VARIANCE
        )
        items = [
            Item(id='best', width=3, length=1, height=10),
            Item(id='other', width=3, length=1, height=11),
            Item(id='1', width=2, length=1, height=8),
            Item(id='2', width=3, length=1, height=9),
            Item(id='3', width=4, length=1, height=10)
        ]

        item, other = packer.get_best_item_to_pack(
            items,
            max_len_x=3,
            max_len_z=12,
            gap_len_z=10)

        self.assertEqual(items[0], item)
        self.assertEqual(items[1], other)

    def test_pack_item_on_snappoint(self):

        bin = Bin(width=10, length=1, height=10)
        item = Item(id='1', width=5, length=1, height=5)
        packer = PalletierWishPacker(bins=[bin])

        # Create a Snappoint object
        snappoint_left = Snappoint(
            x=0, y=0, z=0, direction=SnappointDirection.RIGHT)
        snappoint_right = Snappoint(
            x=5, y=0, z=0, direction=SnappointDirection.LEFT)

        # Test packing item on the left snappoint
        result_left = packer.pack_item_on_snappoint(
            bin, copy.copy(item), snappoint_left)
        self.assertTrue(
            result_left, "Failed to pack item on the left snappoint")

        bin = Bin(width=10, length=1, height=10)
        # Test packing item on the right snappoint
        result_right = packer.pack_item_on_snappoint(
            bin, copy.copy(item), snappoint_right)
        self.assertTrue(
            result_right, "Failed to pack item on the right snappoint")

    def test_fill_gaps_no_gap(self):

        bin = Bin(width=10, length=1, height=2)
        bin.pack_item(Item("", width=5, length=1, height=1,
                      position=Position(0, 0, 0)))
        bin.pack_item(Item("", width=5, length=1, height=1,
                      position=Position(5, 0, 0)))

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
        bin.pack_item(Item("", width=5, length=1, height=1,
                      position=Position(5, 0, 0)))

        packer = PalletierWishPacker(bins=[bin], fill_gaps=True)
        changed = packer._fill_gaps(bin, min_z=0)

        self.assertTrue(changed)
        self.assertEqual(bin.packed_items[0].position, Position(2, 0, 0))

    def test_fill_gaps_single_item(self):
        bin = Bin(width=10, length=1, height=8)
        bin.pack_item(Item("", width=5, length=1, height=2,
                      position=Position(0, 0, 0)))
        bin.pack_item(Item("", width=3, length=1, height=2,
                      position=Position(5, 0, 0)))
        bin.pack_item(Item("", width=2, length=1, height=2,
                      position=Position(0, 0, 2)))
        bin.pack_item(Item("", width=2, length=1, height=2,
                      position=Position(6, 0, 2)))

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


if __name__ == '__main__':
    unittest.main()
