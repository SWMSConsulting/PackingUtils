from typing import List
from packutils.data.packing_variant import PackingVariant


class PackedOrder:
    """
    Represents a packed order containing multiple packing variants.

    Attributes:
        order_id (str): The ID of the order.
        packing_variants (List[PackingVariant]): A list of packing variants associated with the order.
    """

    def __init__(self, order_id: str):
        """
        Initializes a new instance of the PackedOrder class.

        Args:
            order_id (str): The ID of the order.
        """
        if not isinstance(order_id, str):
            raise TypeError("order_id should be of type string.")

        self.order_id = order_id
        self.packing_variants: List[PackingVariant] = []

    def add_packing_variant(self, packing_variant: PackingVariant):
        """
        Adds a packing variant to the packed order.

        Args:
            packing_variant (PackingVariant): The packing variant to be added.
        """
        if not isinstance(packing_variant, PackingVariant):
            raise TypeError(
                "Packing variant should be of class PackingVariant.")

        self.packing_variants.append(packing_variant)
