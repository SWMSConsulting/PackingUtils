from packutils.data.item import Item
from typing import List, Tuple
import numpy as np


class Bin:
    """
    Represents a bin for packing items.

    Attributes:
        width (int): The width of the bin.
        length (int): The length of the bin.
        height (int): The height of the bin.
        max_weight (float, optional): The maximum weight limit of the bin.

    Methods:
        pack_item(item: Item) -> Tuple[bool, str]:
            Packs an item into the bin at a valid position.

    """

    def __init__(self, width: int, length: int, height: int, max_weight: float | None = None):
        """
        Initializes a Bin object with specified dimensions and optional maximum weight.

        Args:
            width (int): The width of the bin.
            length (int): The length of the bin.
            height (int): The height of the bin.
            max_weight (float, optional): The maximum weight limit of the bin.

        """
        self.width = width
        self.length = length
        self.height = height
        self.max_weight = max_weight

        self.matrix = np.zeros((height, length, width), dtype=int)
        self.packed_items: List[Item] = []

    def pack_item(self, item: Item) -> Tuple[bool, str | None]:
        """
        Packs an item into the bin at a valid position.

        Args:
            item (Item): The item to be packed.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the packing was successful
            and a string message explaining the result.

        """
        if not item.is_packed():
            return False, f"{item.id}: Position is None."
        x, y, z = item.position.x, item.position.y, item.position.z
        if (
            x < 0
            or y < 0
            or z < 0
            or x + item.width > self.width
            or y + item.length > self.length
            or z + item.height > self.height
        ):
            return False, f"{item.id}: Item is out of bounds of the bin."

        if np.any(self.matrix[z: z + item.height, y: y + item.length, x: x + item.width]):
            return False, f"{item.id}: Position is already occupied."

        self.packed_items.append(item)
        self.matrix[z: z + item.height,
                    y: y + item.length,
                    x: x + item.width] = len(self.packed_items)
        return True, None
