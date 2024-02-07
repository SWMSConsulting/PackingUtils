from collections import namedtuple
import copy
import math
from packutils.data.item import Item
from typing import List, Tuple
import numpy as np

from packutils.data.position import Position
from packutils.data.snappoint import Snappoint, SnappointDirection

# describes the percentage of the bottom area required to lay on top of other item
DEFAULT_STABILITY_FACTOR = 0.75

Gap = namedtuple("Gap", ["start_x", "end_x"])


class Bin:
    """
    Represents a bin for packing items.
    """

    # This is a Wx2 matrix representing the upper z coordinate and the length of the top layer.
    _heightmap: np.ndarray

    _packed_items: List[Item]

    def __init__(
        self,
        width: int,
        length: int,
        height: int,
        max_weight: "float | None" = None,
        stability_factor: float = DEFAULT_STABILITY_FACTOR,
        overhang_y_stability_factor: "float | None" = None,
    ):
        """
        Initializes a Bin object with specified dimensions and optional maximum weight.

        Args:
            width (int): The width of the bin.
            length (int): The length of the bin.
            height (int): The height of the bin.
            max_weight (float, optional): The maximum weight limit of the bin.

        """
        assert all(
            isinstance(dim, int) and dim > 0 for dim in [width, length, height]
        ), "Bin dimensions must be positive integers."

        self.width = width
        self.length = length
        self.height = height
        self.max_weight = max_weight

        assert stability_factor is None or (
            stability_factor >= 0 and stability_factor <= 1
        ), "Stability factor must be between 0 and 1."
        self.stability_factor = stability_factor

        assert overhang_y_stability_factor is None or (
            overhang_y_stability_factor >= 0.5 and overhang_y_stability_factor < 1
        ), "Overhang y stability factor must be between 0 and 1."
        self.allow_overhang_y = overhang_y_stability_factor != None
        self.overhang_y_stability_factor = overhang_y_stability_factor

        self._packed_items = []
        self.recreate_heightmap()

    @property
    def heightmap(self) -> np.ndarray:
        return self._heightmap[:, 0]

    @property
    def packed_items(self) -> List[Item]:
        flattened_items = sum([item.flatten() for item in self._packed_items], [])
        return flattened_items

    def can_item_be_packed(
        self, item: Item, position: Position
    ) -> Tuple[bool, "str | None"]:
        """
        Checks if an item can be packed into the bin at a specified position.

        Args:
            item (Item): The item to be packed.
            position (Position): The position to pack the item at.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the item can be packed and a string message explaining the result.
        """

        if item.is_packed:
            return False, f"{item.identifier}: Item already packed."

        x, y, z = position.x, position.y, position.z
        if (
            x < 0
            or (y < 0 and not self.allow_overhang_y)
            or z < 0
            or x + item.width > self.width
            or (y + item.length > self.length and not self.allow_overhang_y)
            or z + item.height > self.height
        ):
            return (
                False,
                f"{item.identifier}: Item is out of bounds of the bin (containment condition).",
            )

        if y < 0 and abs(y) > item.get_max_overhang_y(self.overhang_y_stability_factor):
            return (
                False,
                f"{item.identifier}: Item overhangs the bin and is not stable (stability condition).",
            )

        overhang_y = math.floor((item.length - self.length) / 2)
        if self.allow_overhang_y and overhang_y > item.get_max_overhang_y(
            self.overhang_y_stability_factor
        ):
            return (
                False,
                f"{item.identifier}: Item overhangs the bin and is not stable (stability condition).",
            )

        is_overlapping = np.any(self._heightmap[x : x + item.width, 0] > z)
        stacked_items_y = [
            i for i in self._packed_items if (x == i.position.x and z == i.position.z)
        ]
        overlapping_items_y = [
            i
            for i in stacked_items_y
            if y < i.position.y + i.length and i.position.y < y + item.length
        ]
        is_overlapping_y = len(overlapping_items_y) > 0

        if is_overlapping:
            if is_overlapping_y:
                return (
                    False,
                    f"{item.identifier}: Position is already occupied (non-overlapping condition).",
                )
            else:
                return True, None

        if not self._is_item_position_stable(item, position):
            return (
                False,
                f"{item.identifier}: Position is not stable (stability condition).",
            )

        return True, None

    def pack_item(self, item: Item, position: Position) -> Tuple[bool, "str | None"]:
        """
        Packs an item into the bin at a valid position.

        Args:
            item (Item): The item to be packed.
            position (Position): The position to pack the item at.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the packing was successful
            and a string message explaining the result.

        """
        if position is None:
            return False, f"{item.identifier}: Position is None."

        can_be_packed, info = self.can_item_be_packed(item, position)

        if can_be_packed:
            self._packed_items.append(item)
            x = position.x
            max_z = position.z + item.height
            y = max(position.y, 0)
            self._heightmap[x : x + item.width, 0] = max_z
            self._heightmap[x : x + item.width, 1] = item.length

            if item.length > self.length and self.allow_overhang_y:
                position.y -= math.floor((item.length - self.length) / 2)

            item.pack(position)
        return can_be_packed, info

    def remove_item(self, item: Item) -> Tuple[bool, "str | None"]:
        """
        Removes an item from the bin.

        Args:
            item (Item): The item to be removed.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating if the removal was successful
            and a string message explaining the result.

        """
        if not item in self._packed_items:
            return False, f"{item.identifier}: Item not found in bin."

        if np.any(
            self.heightmap[item.position.x : item.position.x + item.width]
            != item.position.z + item.height
        ):
            return (
                False,
                f"{item.identifier}: Item can not be removed because it is not on top.",
            )

        self._packed_items.remove(item)
        self.recreate_heightmap()
        item.pack(None)

        return True, None

    def recreate_heightmap(self):
        """
        Recreates the heightmap of the bin based on the items packed in it. See heightmap definition for more details.
        """
        self._heightmap = np.zeros((self.width, 2), dtype=int)
        self._heightmap[:, 1] = self.length

        for item in sorted(
            self._packed_items, key=lambda item: item.position.z, reverse=True
        ):
            x, y, z = item.position.x, item.position.y, item.position.z
            self._heightmap[x : x + item.width, 0] = z + item.height
            self._heightmap[x : x + item.width, 1] = item.length

    def get_gaps(self) -> List[Gap]:
        gaps = []

        start_x = None

        for x in range(self.width):
            if np.count_nonzero(self.heightmap[x]) == 0:
                if start_x is None:
                    start_x = x
            else:
                if start_x is not None:
                    gaps.append(Gap(start_x, x))
                    start_x = None
        return gaps

    def remove_gaps(self):
        gaps = self.get_gaps()

        for gap in sorted(gaps, key=lambda x: x.start_x, reverse=True):
            # find all items right of the gap
            items_right = [
                item for item in self._packed_items if item.position.x >= gap.end_x
            ]
            for item in items_right:
                item.position.x -= gap.end_x - gap.start_x

        # update heightmap
        self.recreate_heightmap()

    def _is_item_position_stable(self, item: Item, position: Position) -> bool:
        """
        Check if an item's position is stable based on the already packed items below it.

        Args:
            item (Item): The item to check for stability.

        Returns:
            bool: True if the item's position is stable, False otherwise.
        """

        if item.is_packed:
            return False

        # every position with z == 0 is stable
        if position.z == 0:
            return True

        unstable_positions = 0

        for x in range(position.x, position.x + item.width):
            if self.heightmap[x] != position.z:
                unstable_positions += 1

            available_length = self._heightmap[x, 1] + item.get_max_overhang_y(
                self.overhang_y_stability_factor
            )
            if available_length < item.length:
                return False

        allowed_unstable = math.floor(item.width * (1 - self.stability_factor))
        return unstable_positions <= allowed_unstable

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
        if (
            dimensions.count("width")
            + dimensions.count("length")
            + dimensions.count("height")
            != 2
        ):
            raise ValueError(
                "Dimensions should contain two strings out of [width, length, height]."
            )

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
    def max_z(self) -> int:
        """
        Calculate the maximum z value of the Bin.

        Returns:
        int: The maximum z value of the Bin.
        """
        return int(np.max(self._heightmap[:, 0]))

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
        used_volume = sum([item.volume for item in self._packed_items])

        if use_percentage:
            return int(used_volume / self.volume * 100)
        return used_volume

    def get_snappoints(self, min_z: "int | None" = None) -> List[Snappoint]:
        """
        Calculate and return the list of snap points in the bin.

        A snap point is a point in the bin where a new item could potentially be placed.
        This method calculates these points based on the current state of the bin and the items already packed.

        Note: This method is currently implemented only for 2D packing.

        Returns:
            List[Snappoint]: A list of Snappoint objects representing the snap points in the bin.

        Raises:
            NotImplementedError: If the method is called for a 3D packing scenario.
        """
        if not self.is_packing_2d():
            raise NotImplementedError("get_snappoints not implemented for 3D case.")

        heightmap = copy.deepcopy(self.heightmap).flatten()
        if min_z is not None:
            heightmap -= min_z
            heightmap[heightmap < 0] = 0
        else:
            min_z = 0

        snappoints = []
        snappoints.append(
            Snappoint(
                x=0,
                y=0,
                z=int(heightmap[0]) + min_z,
                direction=SnappointDirection.RIGHT,
            )
        )

        for index in range(1, len(heightmap)):
            last_z = int(heightmap[index - 1]) + min_z
            next_z = int(heightmap[index]) + min_z
            if last_z != next_z:
                snappoints.append(
                    Snappoint(x=index, y=0, z=last_z, direction=SnappointDirection.LEFT)
                )

                snappoints.append(
                    Snappoint(
                        x=index, y=0, z=next_z, direction=SnappointDirection.RIGHT
                    )
                )

        snappoints.append(
            Snappoint(
                x=len(heightmap),
                y=0,
                z=int(heightmap[-1]) + min_z,
                direction=SnappointDirection.LEFT,
            )
        )

        return snappoints

    def get_center_of_gravity(self, use_volume=False) -> Position:
        """
        Calculate the center of gravity for the items packed in the bin.

        Args:
            use_volume (bool, optional): Whether to calculate the center of gravity based on item volume or weight.
                                         Defaults to False, which calculates based on item weight.

        Returns:
            Position: The calculated center of gravity.
        """
        m, x, y, z = [], [], [], []

        for item in self._packed_items:
            m.append(item.volume if use_volume else item.weight)
            x.append(item.centerpoint.x)
            y.append(item.centerpoint.y)
            z.append(item.centerpoint.z)

        m, x, y, z = np.array(m), np.array(x), np.array(y), np.array(z)

        if np.sum(m) == 0:
            return Position(x=0, y=0, z=0)

        cgx = np.sum(x * m) / np.sum(m)
        cgy = np.sum(y * m) / np.sum(m)
        cgz = np.sum(z * m) / np.sum(m)
        return Position(x=int(cgx), y=int(cgy), z=int(cgz))

    def __repr__(self):
        return (
            f"Bin: {self.width} {self.length} {self.height} - Items{self._packed_items}"
        )

    def __eq__(self, other):
        return (
            self.width == other.width
            and self.length == other.length
            and self.height == other.height
            and self._packed_items == other.packed_items
        )

    def __hash__(self):
        return hash((self.width, self.length, self.height, tuple(self._packed_items)))


if __name__ == "__main__":
    bin = Bin(2, 2, 2)
    item = Item("", 1, 1, 2, position=Position(0, 0, 0))
    bin.pack_item(item)

    bin2 = Bin(2, 2, 2)
    item = Item("", 1, 1, 2, position=Position(0, 0, 0))
    bin2.pack_item(item)

    print(hash(bin) == hash(bin2))
    print(hash(bin), hash(bin2))
