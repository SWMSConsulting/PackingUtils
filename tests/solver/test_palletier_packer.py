import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.solver.palletier_packer import PalletierPacker


class TestPalletierPacker:  # (unittest.TestCase):
    def setUp(self):
        packer = PalletierPacker(bins=[Bin(1, 1, 1)])
        if not packer.is_packer_available():
            self.fail(
                "Py3dbpPacker requires py3dbp to be installed (pip install py3dbp)."
            )

        # Create an example order
        self.order = Order(
            "testorder",
            [Article(article_id="test", width=3, length=4, height=5, amount=1)],
        )

    def test_pack_single_item(self):
        bins = [Bin(10, 10, 10)]
        packer = PalletierPacker(bins=bins)
        variant = packer.pack_variant(self.order)

        self.assertIsInstance(variant, PackingVariant)
        self.assertEqual(len(variant.unpacked_items), 0)
        self.assertEqual(len(variant.bins), 1)
        self.assertEqual(len(variant.bins[0].packed_items), 1)

    def test_pack_multiple_items(self):
        bins = [Bin(10, 10, 10)]
        packer = PalletierPacker(bins=bins)
        self.order.articles[0].amount = 3
        variant = packer.pack_variant(self.order)

        self.assertIsInstance(variant, PackingVariant)
        self.assertEqual(len(variant.unpacked_items), 0)
        self.assertEqual(len(variant.bins), 1)
        self.assertEqual(len(variant.bins[0].packed_items), 3)

    def test_pack_invalid_items(self):
        bins = [Bin(1, 1, 1)]
        packer = PalletierPacker(bins=bins)
        self.order.articles[0].amount = 3
        variant = packer.pack_variant(
            Order(
                "test",
                [Article(article_id="t1", width=2, length=1, height=1, amount=1)],
            )
        )

        self.assertIsInstance(variant, PackingVariant)
        self.assertEqual(len(variant.unpacked_items), 1)
        self.assertEqual(len(variant.bins), 0)

    def test_pack_too_many_items(self):
        bins = [Bin(1, 1, 1)]
        packer = PalletierPacker(bins=bins)
        self.order.articles[0].amount = 3
        variant = packer.pack_variant(
            Order(
                "test",
                [Article(article_id="t1", width=1, length=1, height=1, amount=2)],
            )
        )

        self.assertIsInstance(variant, PackingVariant)
        self.assertEqual(len(variant.unpacked_items), 1)
        self.assertEqual(len(variant.bins), 1)
        self.assertEqual(len(variant.bins[0].packed_items), 1)

    def test_with_visual(self):
        return
        bins = [Bin(10, 10, 10)]
        packer = PalletierPacker(bins=bins)
        self.order.articles[0].length = 10
        self.order.articles[0].amount = 2
        variant = packer.pack_variant(self.order)

        from packutils.visual.packing_visualization import PackingVisualization

        vis = PackingVisualization()
        vis.visualize_packing_variant(variant)


if __name__ == "__main__":
    unittest.main()
