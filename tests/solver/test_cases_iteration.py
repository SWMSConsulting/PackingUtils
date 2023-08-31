import unittest

from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.solver.palletier_packer import PalletierPacker
from packutils.solver.palletier_wish_packer import PalletierWishPacker
from packutils.visual.packing_visualization import PackingVisualization


class TestCasesIteration(unittest.TestCase):

    def setUp(self):
        self.test_cases = TEST_CASES

    def test_compare_palletier_and_wish_palletier(self):

        show = True
        vis = PackingVisualization()

        for bins, order in self.test_cases:
            # run palletier packer
            palletier = PalletierPacker(bins=bins)
            variant1 = palletier.pack_variant(order=order)
            packed1 = len(variant1.unpacked_items) == 0 \
                and len(variant1.bins) > 0 and len(variant1.bins) <= len(bins)

            if not packed1:
                # print(variant1)
                vis.visualize_packing_variant(variant1, show=show)
            self.assertTrue(packed1)

            # run wish palletier packer
            wishPalletier = PalletierWishPacker(bins=bins)
            variant2 = wishPalletier.pack_variant(order=order)
            packed2 = len(variant2.unpacked_items) == 0 \
                and len(variant2.bins) > 0 and len(variant2.bins) <= len(bins)

            if not packed2:
                # print(variant2)
                vis.visualize_packing_variant(variant2, show=show)
            self.assertTrue(packed2)

            if False:  # variant1 != variant2:
                print("Packing variants are not equal!")
                print("Palletier:", variant1)
                print("PalletierWish:", variant2)
                vis.visualize_packing_variant(variant1, show=show)
                vis.visualize_packing_variant(variant2, show=show)
                self.assertTrue(False)

    """
    # this should return 2 pallets completely filled
    ([Bin(10, 1, 10) for _ in range(2)], Order(
        order_id="test_order1", articles=[
            Article("1", width=10, length=1, height=10, amount=2)
        ]
    )),
    # this should return 1 pallet completely filled
    ([Bin(10, 1, 10)], Order(
        order_id="test_order1", articles=[
            Article("1", width=10, length=1, height=1, amount=10)
        ]
    )),
    # this should return 1 pallet completely filled
    ([Bin(10, 1, 10)], Order(
        order_id="test_order1", articles=[
            Article("1", width=1, length=1, height=1, amount=100)
        ]
    )),

    # POSSIBLE REAL ORDERS
    # AMELAND Zaun mit 2 Elementen
    ([Bin(800, 1, 500)], Order(
        order_id="real_test_order1", articles=[
            Article("AMELAND WPC Steckzaun Füllung",
                    width=274, length=1, height=153, amount=2),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=3)
        ]
    )),
    """


TEST_CASES = [
    # AMELAND Zaun mit 8 Elementen
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order1", articles=[
            Article("AMELAND WPC Steckzaun Füllung",
                    width=274, length=1, height=153, amount=8),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=9)
        ]
    )),

]

if __name__ == '__main__':
    unittest.main()
