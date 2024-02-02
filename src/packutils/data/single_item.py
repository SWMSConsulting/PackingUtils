import math
from typing import List
from packutils.data.article import Article
from packutils.data.item import Item
from packutils.data.position import Position


class SingleItem(Item):
    """
    A class representing a single item to be packed in a container.
    """

    def __init__(
        self, identifier: str, width: int, length: int, height: int, weight: float = 0.0
    ):
        """
        Initializes an Item object with the specified attributes.

        Args:
            identifier (str): The identifier of the item.
            width (int): The width of the item.
            length (int): The length of the item.
            height (int): The height of the item.
            weight (float, optional): The weight of the item. Default is 0.0.
            position (Position, optional): The position of the item in the container. Default is None.

        """
        self.identifier = identifier
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight

    def flatten(self) -> List[Item]:
        return [self]

    def get_max_overhang_y(self, stability_factor) -> int:
        return int(math.floor(self.length * (1 - stability_factor)))

    def pack(self, position: "Position|None"):
        assert position is None or isinstance(
            position, Position
        ), "This method requires a Position object as input."

        self.position = position

    @classmethod
    def from_article(cls, article: Article) -> "Item":
        """
        Create an Item object from an Article object.

        Args:
            article (Article): The Article object to create the Item from.

        Returns:
            Item: The created Item object.

        Example:
            >>> article = Article(article_id=1, width=10, length=20, height=5, weight=2)
            >>> item = Item.from_article(article)
            >>> print(item)
            Item(id=1, width=10, length=20, height=5, weight=2, position=None)

        """
        return cls(
            id=article.article_id,
            width=article.width,
            length=article.length,
            height=article.height,
            weight=article.weight,
            position=None,
        )
