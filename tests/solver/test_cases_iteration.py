import unittest

from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.packer_configuration import PackerConfiguration
from packutils.solver.palletier_packer import PalletierPacker
from packutils.solver.palletier_wish_packer import PalletierWishPacker
from packutils.visual.packing_visualization import PackingVisualization


class TestCasesIteration(unittest.TestCase):

    def setUp(self):
        self.test_cases = TEST_CASES[4:]

    def test_compare_palletier_and_wish_palletier(self):

        show = True
        vis = PackingVisualization()

        for idx, (bins, order) in enumerate(self.test_cases):
            """
            # run palletier packer
            palletier = PalletierPacker(bins=bins)
            variant1 = palletier.pack_variant(order=order)
            packed1 = len(variant1.unpacked_items) == 0 \
                and len(variant1.bins) > 0 and len(variant1.bins) <= len(bins)

            if not packed1:
                pass
                # print(variant1)
                # vis.visualize_packing_variant(variant1, show=show)
            # self.assertTrue(packed1)
            """
            # run wish palletier packer
            wishPalletier = PalletierWishPacker(bins=bins)
            configuration = PackerConfiguration(
                item_select_strategy_index=3,
                direction_change_min_volume=1.0,
                bin_stability_factor=1.0
            )

            variant = wishPalletier.pack_variant(
                order=order, config=configuration)
            packed = len(variant.unpacked_items) == 0 \
                and len(variant.bins) > 0 and len(variant.bins) <= len(bins)

            if True:  # not packed or idx == len(self.test_cases) - 1:
                # print(variant)
                # print(len(variant.bins[0].packed_items))
                vis.visualize_packing_variant(variant, show=show)
            self.assertTrue(packed)

            if False:  # variant1 != variant2:
                print("Packing variants are not equal!")
                print("Palletier:", variant1)
                print("PalletierWish:", variant2)
                vis.visualize_packing_variant(variant1, show=show)
                vis.visualize_packing_variant(variant2, show=show)
                self.assertTrue(False)


TEST_CASES = [
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

    # AMELAND Zaun mit 8 Elementen
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order1", articles=[
            Article("AMELAND WPC Steckzaun Füllung",
                    width=274, length=1, height=153, amount=8),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=9)
        ]
    )),

    # Rhombus Zaun
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order2", articles=[
            Article("Stockholm Alu Leistenset Silber ST105",
                    width=72, length=1, height=25, amount=1),
            Article("BPC Rhombus Zaunlamellen Stockholm (einzel??)",  # sieht eher aus wie 3-4
                    width=146, length=1, height=72, amount=24),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=2)
        ]
    )),

    # Rhombus Zaun (large)
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order3", articles=[
            Article("Stockholm Alu Leistenset Silber ST105",
                    width=72, length=1, height=25, amount=1),
            Article("BPC Rhombus Zaunlamellen Stockholm (einzel)",
                    width=146, length=1, height=72, amount=48),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=6)
        ]
    )),

    # Fertigzaun (dieser überschreitet die Maximalbreite)
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order4", articles=[
            Article("Rhombus Steckzaunelement Sib. Lärche (Halbelement)",
                    width=800, length=1, height=19, amount=6),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=7)
        ]
    )),

    # Norderney WPC Steckzaunsystem mit Tor
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order5", articles=[
            Article("Universal Tor für Steckzaun 90x175 cm",
                    width=280, length=1, height=75, amount=1),
            Article("Norderney WPC Steckzaunsystem",
                    width=257, length=1, height=162, amount=4),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=5),
        ]
    )),

    # dieses sieht spannend aus
    # SCHWEDENPROFIL WPC Steckzaunfüllung
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order6", articles=[
            Article("SCHWEDENPROFIL WPC Steckzaunfüllung",
                    width=170, length=1, height=175, amount=4),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=5),
            # was bedeutet der Kommentar?
            Article("SCHWEDENPROFIL schiefergrau Torfüllung",
                    width=146, length=1, height=20, amount=6),
        ]
    )),

    # Norderney WPC Steckzaunsystem mit Tor
    ([Bin(800, 1, 500) for _ in range(2)], Order(
        order_id="real_test_order7", articles=[
            Article("Universal Tor für Steckzaun 90x175 cm",
                    width=280, length=1, height=75, amount=1),
            Article("Norderney WPC Steckzaunsystem",
                    width=257, length=1, height=162, amount=4),
            Article("Aluminium Steckzaunpfosten, silber",
                    width=68, length=1, height=68, amount=5),
        ]
    )),

]

if __name__ == '__main__':
    unittest.main()
