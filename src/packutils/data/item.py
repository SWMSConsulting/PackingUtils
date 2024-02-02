from abc import ABC, abstractmethod
from ast import Tuple
from typing import List

from packutils.data.position import Position


class Item(ABC):
    """
    An abstract class representing an item to be packed in a container.
    """

    identifier: str
    width: int
    length: int
    height: int
    weight: float

    position: "Position|None" = None

    @abstractmethod
    def get_max_overhang_y(self, stability_factor: "float|None") -> int:
        """
        Returns the maximum overhang of the item in the y-direction.

        Args:
            stability_factor (float): The stability factor of the bin.

        Returns:
            int: The maximum overhang of the item in the y-direction.
        """
        pass

    @abstractmethod
    def pack(self, position: "Position|None"):
        """
        Sets the position of the item in the container.

        Args:
            position (Position): The position object representing the coordinates and rotation of the item.

        """
        pass

    @abstractmethod
    def flatten(self) -> List["Item"]:
        """
        Returns all items that are part of the item (group).
        """
        pass

    @property
    def centerpoint(self) -> Position:
        """
        Returns the centerpoint of the object.

        Returns:
            position (Position): The position of the centerpoint,

        """
        return (
            None
            if self.position is None
            else Position(
                x=self.position.x + self.width / 2,
                y=self.position.y + self.length / 2,
                z=self.position.z + self.height / 2,
                rotation=self.position.rotation,
            )
        )

    @property
    def is_packed(self) -> bool:
        """
        Checks if the item is packed in a position.

        Returns:
            bool: True if the item is packed, False otherwise.

        """
        return self.position is not None

    @property
    def volume(self) -> int:
        """
        Calculate the volume of the Item.

        Returns:
        int: The volume of the Item.
        """
        return int(self.width * self.length * self.height)

    @property
    def surface(self) -> int:
        """
        Calculate the surface of the Item.

        Returns:
        int: The surface of the Item.
        """
        return int(self.width * self.length)

    @property
    def dimensions(self) -> "Tuple[int, int, int]":
        """
        Returns the dimensions of the item.

        Returns:
            Tuple[int, int, int]: The dimensions of the item.

        """
        return (self.width, self.length, self.height)

    def get_rotated_dimensions_3D(self):
        if not self.is_packed:
            return self.width, self.length, self.height

        rot_type = self.position.rotation
        if rot_type == 1:
            h, w, l = self.width, self.height, self.length
        elif rot_type == 2:
            l, w, h = self.width, self.height, self.length
        elif rot_type == 3:
            l, h, w = self.width, self.height, self.length
        elif rot_type == 4:
            h, l, w = self.width, self.height, self.length
        elif rot_type == 5:
            w, l, h = self.width, self.height, self.length
        else:  # rotation None or 0
            w, h, l = self.width, self.height, self.length

        return w, l, h

    def to_position_and_dimension_2d(self, dimensions: List[str]):
        """
        Returns the 2D position and dimensions of the item based on the specified dimensions.

        Args:
            dimensions (List[str]): The dimensions to extract from the item. Should contain two strings out of ["width", "length", "height"].

        Returns:
            Tuple[Tuple[int], Tuple[int]]: The 2D position and dimension of the item based on the input dimensions. Returns None, None if the item os not packed.

        Raises:
            ValueError: If the dimensions list does not contain two valid dimension strings.

        """
        if not self.is_packed:
            return None, None

        if (
            dimensions.count("width")
            + dimensions.count("length")
            + dimensions.count("height")
            != 2
        ):
            raise ValueError(
                "dimensions should contain two strings out of [width, length, height]."
            )

        pos = []
        dim = []
        for d in dimensions:
            if d == "width":
                pos.append(self.position.x)
                dim.append(self.width)

            if d == "length":
                pos.append(self.position.y)
                dim.append(self.length)

            if d == "height":
                pos.append(self.position.z)
                dim.append(self.height)

        return tuple(pos), tuple(dim)

    def __repr__(self) -> str:
        """
        Returns a string representation of the item.

        Returns:
            str: The string representation of the item.

        """
        return f"{self.identifier}: width={self.width}, length={self.length}, height={self.height}, position={self.position}"

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(
            (
                self.width,
                self.length,
                self.height,
                self.weight,
                self.position.__hash__(),
            )
        )
