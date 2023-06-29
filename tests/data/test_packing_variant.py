import unittest
from packutils.data.item import Item
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
        item = Item(id="test_item", width=5, length=5, height=5)
        error_message = "Item is too large for the available bins."
        variant.add_unpacked_item(item, error_message)

        self.assertEqual(len(variant.unpacked_items), 1)
        self.assertEqual(variant.unpacked_items[0], item)
        self.assertEqual(len(variant.error_messages), 1)
        self.assertEqual(variant.error_messages[0], error_message)

    def test_add_unpacked_item_without_error_message(self):
        variant = PackingVariant()
        item = Item(id="test_item", width=5, length=5, height=5)
        variant.add_unpacked_item(item, None)

        self.assertEqual(len(variant.unpacked_items), 1)
        self.assertEqual(variant.unpacked_items[0], item)
        self.assertEqual(len(variant.error_messages), 0)


if __name__ == "__main__":
    unittest.main()
