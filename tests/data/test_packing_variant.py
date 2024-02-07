import unittest
from packutils.data.position import Position
from packutils.data.single_item import SingleItem
from packutils.data.bin import Bin
from packutils.data.packing_variant import PackingVariant


class TestPackingVariant(unittest.TestCase):
    def test_add_bin(self):
        variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        variant.add_bin(bin)

        self.assertEqual(len(variant.bins), 1)
        self.assertEqual(variant.bins[0], bin)
        self.assertEqual(len(variant.unpacked_items), 0)

    def test_add_unpacked_item(self):
        variant = PackingVariant()
        item = SingleItem(identifier="test_item", width=5, length=5, height=5)
        error_message = "Item is too large for the available bins."
        variant.add_unpacked_item(item, error_message)

        self.assertEqual(len(variant.unpacked_items), 1)
        self.assertEqual(variant.unpacked_items[0], item)
        self.assertEqual(len(variant.error_messages), 1)
        self.assertEqual(variant.error_messages[0], error_message)

    def test_add_unpacked_item_without_error_message(self):
        variant = PackingVariant()
        item = SingleItem(identifier="test_item", width=5, length=5, height=5)
        variant.add_unpacked_item(item, None)

        self.assertEqual(len(variant.unpacked_items), 1)
        self.assertEqual(variant.unpacked_items[0], item)
        self.assertEqual(len(variant.error_messages), 0)

    def test_compare(self):
        variant1 = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        variant1.add_bin(bin)

        variant2 = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        variant2.add_bin(bin)

        self.assertEqual(variant1, variant2)

    def test_compare_variants_same(self):
        variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="test_item", width=5, length=5, height=5),
            Position(0, 0, 0),
        )
        variant.add_bin(bin)

        same_variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="test_item", width=5, length=5, height=5),
            Position(0, 0, 0),
        )
        same_variant.add_bin(bin)

        self.assertEqual(variant, same_variant)

    def test_compare_variants_different_position(self):
        variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="test_item", width=5, length=5, height=5),
            Position(0, 0, 0),
        )
        variant.add_bin(bin)

        other_variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="test_item", width=5, length=5, height=5),
            Position(10, 0, 0),
        )
        other_variant.add_bin(bin)

        self.assertNotEqual(variant, other_variant)

    def test_compare_variants_different_articles(self):
        variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="test_item", width=5, length=5, height=5),
            Position(0, 0, 0),
        )
        variant.add_bin(bin)

        other_variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="another_identifier", width=5, length=5, height=5),
            Position(0, 0, 0),
        )
        other_variant.add_bin(bin)

        self.assertNotEqual(variant, other_variant)

    def test_compare_variants_different_unpacked_articles(self):
        variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        bin.pack_item(
            SingleItem(identifier="test_item", width=5, length=5, height=5),
            Position(0, 0, 0),
        )
        variant.add_bin(bin)

        different_variant = PackingVariant()
        bin = Bin(width=10, length=10, height=10)
        different_variant.add_bin(bin)
        different_variant.add_unpacked_item(
            SingleItem(identifier="test_item", width=2, length=5, height=5),
            error_message="",
        )

        self.assertNotEqual(variant, different_variant)


if __name__ == "__main__":
    unittest.main()
