import math
from packutils.data.item import Item
from packutils.data.position import Position


class SingleItem(Item):
    """
    A class representing a single item to be packed in a container.
    """

    def get_max_overhang_y(self, stability_factor) -> int:
        return int(math.floor(self.length * (1 - stability_factor)))

    def pack(self, position: "Position|None"):
        assert position is None or isinstance(
            position, Position
        ), "This method requires a Position object as input."

        self.position = position
