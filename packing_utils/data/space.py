class Space():
    def __init__(self, x_min: int, y_min: int, x_max: int, y_max: int):
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max

        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min
        self.area = self.width * self.height

    def is_subset_of(self, other):
        return (
            self.x_min >= other.x_min and
            self.x_max <= other.x_max and
            self.y_min >= other.y_min and
            self.y_max <= other.y_max
        )

    def intersects(self, other):
        x_overlap = self.x_min <= other.x_max and self.x_max >= other.x_min
        y_overlap = self.y_min <= other.y_max and self.y_max >= other.y_min

        # If both x- and y-intervals overlap, the rectangles intersect
        if x_overlap and y_overlap:
            return True

        return False

    def __repr__(self):
        return f"Space({self.x_min}, {self.y_min}, {self.x_max}, {self.y_max})"

    def __eq__(self, other):
        if isinstance(other, Space):
            return (self.x_min, self.y_min, self.x_max, self.y_max) == (
                other.x_min, other.y_min, other.x_max, other.y_max)
        return NotImplemented

    def __hash__(self):
        return hash(tuple([self.x_min, self.y_min, self.x_max, self.y_max]))
