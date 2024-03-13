from dataclasses import dataclass


@dataclass
class Position:
    """
    Represents a position in 3D space.

    Attributes:
        x (int): The X-coordinate of the position.
        y (int): The Y-coordinate of the position.
        z (int): The Z-coordinate of the position.
        rotation (int): The rotation value of the position.

    Methods:
        __init__(x: int, y: int, z: int, rotation: int = 0):
            Initializes a Position object with the specified coordinates and rotation.

    """

    def __init__(self, x: int, y: int, z: int, rotation: int = 0):
        """
        Initializes a Position object with the specified coordinates and rotation.

        Args:
            x (int): The X-coordinate of the position.
            y (int): The Y-coordinate of the position.
            z (int): The Z-coordinate of the position.
            rotation (int, optional): The rotation value of the position. Default is 0.

        """
        self.x = x
        self.y = y
        self.z = z
        self.rotation = rotation

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z, self.rotation))

    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y}, z={self.z}, rotation={self.rotation})"
