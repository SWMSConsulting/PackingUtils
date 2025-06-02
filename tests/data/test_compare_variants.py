import unittest

from packutils.data.bin import Bin
from packutils.data.packing_variant import PackingVariant
from packutils.data.single_item import SingleItem

class TestCompareVariants(unittest.TestCase):

    def test_compare_items(self):
        from src.packutils.data.item import Item
        from src.packutils.data.position import Position

        item1 = SingleItem(
            identifier="item1",
            width=10,
            length=20,
            height=30,
        )
        item1.pallet_group_index = 1

        bin1 = Bin(
            width=100,
            length=200,
            height=300,
        )
        bin1.pack_item(item1, Position(x=0, y=0, z=0))

        variant1 = PackingVariant()
        variant1.add_bin(bin1)

        item2 = SingleItem(
            identifier="item1",
            width=10,
            length=20,
            height=30,
        )
        item2.pallet_group_index = 0

        bin2 = Bin(
            width=100,
            length=200,
            height=300,
        )
        bin2.pack_item(item2, Position(x=0, y=0, z=0))

        variant2 = PackingVariant()
        variant2.add_bin(bin2)

        self.assertEqual(item1, item2)
        self.assertEqual(bin1, bin2)
        self.assertEqual(variant1, variant2)

        unique_variants = set([variant1, variant2])
        self.assertEqual(len(unique_variants), 1, "Variants should be considered equal based on item properties.")
        
if __name__ == "__main__":
    unittest.main()
