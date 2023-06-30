
import unittest
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.solver.abstract_packer import AbstractPacker


class SubClassWithNoImplementations(AbstractPacker):
    pass


class SubClassWithAllImplementations(AbstractPacker):
    def pack_variant(self, order: Order) -> PackingVariant:
        pass

    def is_packer_available(self) -> bool:
        pass


class AbstractClassTest(unittest.TestCase):
    def test_missing_implementation(self):
        # Create an instance of AnotherSubClass
        with self.assertRaises(TypeError):
            SubClassWithNoImplementations()
        try:
            SubClassWithAllImplementations()
        except TypeError:
            self.fail("Missing implementation of SubClassWithAllImplementations")
