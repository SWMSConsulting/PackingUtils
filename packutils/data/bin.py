from packutils.data.item import Item
from typing import List, Tuple
import numpy as np

# describes the percentage of the bottom area required to lay on top of other item
STABILITY_FACTOR = 0.75


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

    def __init__(self, width: int, length: int, height: int, max_weight: 'float | None' = None):
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

    def pack_item(self, item: Item) -> Tuple[bool, 'str | None']:
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
            return False, f"{item.id}: Item is out of bounds of the bin (containment condition)."

        if np.any(self.matrix[z: z + item.height, y: y + item.length, x: x + item.width]):
            return False, f"{item.id}: Position is already occupied (non-overlapping condition)."

        if not self._is_item_position_stable(item):
            return False, f"{item.id}: Position is not stable (stability condition)."

        self.packed_items.append(item)
        self.matrix[z: z + item.height,
                    y: y + item.length,
                    x: x + item.width] = len(self.packed_items)
        return True, None

    def _is_item_position_stable(self, item: Item):
        # every position with z == 0 is stable
        if item.position.z == 0:
            return True

        if not item.is_packed():
            return False

        positions_below = self.matrix[item.position.z - 1,
                                      item.position.y: item.position.y + item.length,
                                      item.position.x: item.position.x + item.width]

        if np.count_nonzero(positions_below) < item.width * item.length * STABILITY_FACTOR:
            return False

        return True

    def is_packing_2d(self) -> Tuple[bool, List[str]]:
        """
        Checks if the bin is packed in 2D.

        Returns:
            Tuple[bool, List[str]]: A tuple containing a boolean indicating if the bin is packed in 2D and a string list of the two dimensions being packed.

        """
        if self.width <= 1:
            return True, ["length", "height"]
        elif self.length <= 1:
            return True, ["width", "height"]
        elif self.height <= 1:
            return True, ["width", "length"]
        return False, []

    def get_dimension_2d(self, dimensions: List[str]) -> List[int]:
        """
        Retrieves the dimensions of the bin for the specified 2D packing dimensions.

        Args:
            dimensions (List[str]): The two dimensions for the 2D packing. Should contain two strings out of ["width", "length", "height"].

        Returns:
            List[int]: A list containing the corresponding dimensions of the bin.

        Raises:
            ValueError: If the dimensions list does not contain two valid dimension strings.

        """
        if dimensions.count("width") + dimensions.count("length") + dimensions.count("height") != 2:
            raise ValueError(
                "Dimensions should contain two strings out of [width, length, height].")

        dim = []
        for d in dimensions:
            if d == "width":
                dim.append(self.width)
            if d == "length":
                dim.append(self.length)
            if d == "height":
                dim.append(self.height)
        return dim

    @property
    def volume(self) -> int:
        """
        Calculate the volume of the Bin.

        Returns:
        int: The volume of the Bin.
        """
        return int(self.width * self.length * self.height)

    def get_used_volume(self, use_percentage=False):
        """
        Calculate the used volume of the Bin.

        Args:
            use_percentage (bool, optional): Whether to return the used volume as a percentage of the total volume. 
                                            Defaults to False.

        Returns:
            float: The used volume of the Bin.
        """
        used_volume = sum([item.volume for item in self.packed_items])

        if use_percentage:
            return int(used_volume / self.volume * 100)
        return used_volume

    def __repr__(self):
        return f"Bin: {self.width} {self.length} {self.height} - Items{self.packed_items}"

    def __eq__(self, other):
        return self.width == other.width and self.length == other.length and self.height == other.height and self.packed_items == other.packed_items
