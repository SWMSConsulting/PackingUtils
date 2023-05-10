class Item():
    name = "item"
    width, height = None, None
    position_x, position_y = None, None

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def pack(self, x: int, y: int):
        self.position_x = x
        self.position_y = y

        return self

    def is_packed(self):
        return self.position_x != None and self.position_y != None

    def __repr__(self):
        """
        out = f"{self.name.upper()}[({self.width}, {self.height})"
        if self.is_packed():
            out += f", ({self.position_x}, {self.position_y})"
        out += f"]"
        """
        out = f"({self.position_x}, {self.position_y})"
        return out
