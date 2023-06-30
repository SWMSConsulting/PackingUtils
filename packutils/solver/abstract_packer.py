from abc import ABC, abstractmethod
import logging
from packutils.data.bin import Bin

from packutils.data.order import Order
from packutils.data.packed_order import PackedOrder
from packutils.data.packing_variant import PackingVariant

default_bin = Bin(width=10, length=10, height=10, max_weight=None)


class AbstractPacker(ABC):
    def __init__(self, *args, **kwargs):
        if "bins" not in kwargs:
            self.reference_bins = [default_bin]
            logging.info(
                f"No bin provided for packer, using default bin: {default_bin}.")
        else:
            self.reference_bins = kwargs.get('bins')

    def pack_order(self, order: Order) -> PackedOrder:
        variant = self.pack(order)
        packed = PackedOrder(order_id=order.order_id)
        packed.add_packing_variant(variant)
        return packed

    @abstractmethod
    def pack_variant(self, order: Order) -> PackingVariant:
        pass

    @abstractmethod
    def is_packer_available(self) -> bool:
        pass
