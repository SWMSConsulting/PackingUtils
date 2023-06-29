import unittest
from packutils.data.packing_variant import PackingVariant
from packutils.data.packed_order import PackedOrder


class TestPackedOrder(unittest.TestCase):
    def setUp(self):
        self.order_id = "123"
        self.packed_order = PackedOrder(self.order_id)

    def test_add_packing_variant(self):
        packing_variant = PackingVariant()

        self.packed_order.add_packing_variant(packing_variant)
        self.assertEqual(len(self.packed_order.packing_variants), 1)
        self.assertEqual(
            self.packed_order.packing_variants[0], packing_variant)

    def test_add_packing_variant_multiple(self):
        packing_variant1 = PackingVariant()
        packing_variant2 = PackingVariant()
        self.packed_order.add_packing_variant(packing_variant1)
        self.packed_order.add_packing_variant(packing_variant2)

        self.assertEqual(len(self.packed_order.packing_variants), 2)
        self.assertEqual(
            self.packed_order.packing_variants[0], packing_variant1)
        self.assertEqual(
            self.packed_order.packing_variants[1], packing_variant2)

    def test_add_packing_variant_invalid_type(self):
        with self.assertRaises(TypeError):
            self.packed_order.add_packing_variant("invalid")


if __name__ == "__main__":
    unittest.main()
