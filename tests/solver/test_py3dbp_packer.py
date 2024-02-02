import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.solver.py3dbp_packer import Py3dbpPacker


class TestPy3dbpPacker(unittest.TestCase):

    def setUp(self):
        packer = Py3dbpPacker(bins=[Bin(1, 1, 1)])
        if not packer.is_packer_available():

            self.fail(
                "Py3dbpPacker requires py3dbp to be installed (pip install py3dbp).")

        # Create an example order
        self.order = Order("testorder", [
            Article(article_id="test", width=3, length=4, height=5, amount=1)
        ])

    def test_pack_single_item(self):

        bins = [Bin(10, 10, 10)]
        packer = Py3dbpPacker(bins=bins)
        variant = packer.pack_variant(self.order)

        self.assertIsInstance(variant, PackingVariant)
        self.assertEqual(len(variant.unpacked_items), 0)
        self.assertEqual(len(variant.bins), 1)
        self.assertEqual(len(variant.bins[0].packed_items), 1)

    def test_pack_multiple_items(self):
        bins = [Bin(10, 10, 10)]
        packer = Py3dbpPacker(bins=bins)
        self.order.articles[0].amount = 3
        variant = packer.pack_variant(self.order)

        self.assertIsInstance(variant, PackingVariant)
        self.assertEqual(len(variant.unpacked_items), 0)
        self.assertEqual(len(variant.bins), 1)
        self.assertEqual(len(variant.bins[0].packed_items), 3)


if __name__ == '__main__':
    unittest.main()
