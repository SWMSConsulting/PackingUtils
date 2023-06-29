from typing import List
from packutils.data.position import Position


class Item:
    """
    Represents an item to be packed in a container.

    Attributes:
        id (str): The identifier of the item.
        width (int): The width of the item.
        length (int): The length of the item.
        height (int): The height of the item.
        weight (float): The weight of the item.
        position (Position): The position of the item in the container.

    Methods:
        __init__(id: str, width: int, length: int, height: int, weight: float = 0.0, position: Position = None):
            Initializes an Item object with the specified attributes.

        pack(position: Position):
            Sets the position of the item in the container.

        is_packed() -> bool:
            Checks if the item is packed in a position.

        __str__() -> str:
            Returns a string representation of the item.

    """

    def __init__(self, id: str, width: int, length: int, height: int, weight: float = 0.0, position: Position = None):
        """
        Initializes an Item object with the specified attributes.

        Args:
            id (str): The identifier of the item.
            width (int): The width of the item.
            length (int): The length of the item.
            height (int): The height of the item.
            weight (float, optional): The weight of the item. Default is 0.0.
            position (Position, optional): The position of the item in the container. Default is None.

        """
        self.id = id
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.position = position

    def centerpoint(self) -> Position:
        """
        Returns the centerpoint of the object.

        Returns:
            position (Position): The position of the centerpoint,

        """
        return self.position

    def pack(self, position: Position):
        """
        Sets the position of the item in the container.

        Args:
            position (Position): The position object representing the coordinates and rotation of the item.

        """
        assert isinstance(
            position, Position), "This method requires a Position object as input."

        self.position = position

    def is_packed(self) -> bool:
        """
        Checks if the item is packed in a position.

        Returns:
            bool: True if the item is packed, False otherwise.

        """
        return self.position is not None

    def __str__(self) -> str:
        """
        Returns a string representation of the item.

        Returns:
            str: The string representation of the item.

        """
        return f"{self.id}: width={self.width}, length={self.length}, height={self.height}, position={self.position}"
