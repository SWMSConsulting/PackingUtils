import json
import os
from typing import List
from packutils.data.item import Item


class Article:
    """
    Represents an article.

    Attributes:
        article_id (str): The ID of the article.
        length (int): The length of the article.
        width (int): The width of the article.
        height (int): The height of the article.
        amount (int): The amount of the article.
        weight (float): The weight of the article.

    Methods:
        from_json(json_data: dict) -> Article:
            Creates an Article object from JSON data.

    """

    def __init__(self, article_id: str, length: int, width: int, height: int, amount: int, weight: float = 0.0):
        """
        Initializes an Article object with the specified attributes.

        Args:
            article_id (str): The ID of the article.
            length (int): The length of the article.
            width (int): The width of the article.
            height (int): The height of the article.
            amount (int): The amount of the article.
            weight (float, optional): The weight of the article. Default is 0.0.

        """
        self.article_id = article_id
        self.length = length
        self.width = width
        self.height = height
        self.amount = amount
        self.weight = weight

    @classmethod
    def from_json(cls, json_data: dict) -> 'Article':
        """
        Creates an Article object from JSON data.

        Args:
            json_data (dict): The JSON data representing the article.

        Returns:
            Article: The created Article object.

        """
        article_id = json_data["id"]
        length = json_data["length"]
        width = json_data["width"]
        height = json_data["height"]
        amount = json_data["amount"]
        weight = json_data.get("weight", 0.0)

        return cls(article_id, length, width, height, amount, weight)


class Supply:
    """
    Represents a supply.

    Attributes:
        supply_id (str): The ID of the supply.
        amount (int): The amount of the supply.

    Methods:
        from_json(json_data: dict) -> Supply:
            Creates a Supply object from JSON data.

    """

    def __init__(self, supply_id: str, amount: int):
        """
        Initializes a Supply object with the specified attributes.

        Args:
            supply_id (str): The ID of the supply.
            amount (int): The amount of the supply.

        """
        self.supply_id = supply_id
        self.amount = amount

    @classmethod
    def from_json(cls, json_data: dict) -> 'Supply':
        """
        Creates a Supply object from JSON data.

        Args:
            json_data (dict): The JSON data representing the supply.

        Returns:
            Supply: The created Supply object.

        """
        supply_id = json_data.get("id", None)
        amount = json_data.get("amount", None)

        return cls(supply_id, amount)


class Order:
    """
    Represents an order.

    Attributes:
        order_id (str): The ID of the order.
        articles (List[Article]): The list of articles in the order.
        supplies (List[Supply]): The list of supplies in the order.

    Methods:
        to_item_list() -> List[Item]:
            Converts the articles in the order to a list of Item objects.
        from_json_file(file_path: str) -> Order:
            Creates an Order object from a JSON file.
        from_json(json_data: dict) -> Order:
            Creates an Order object from JSON data.

    """

    def __init__(self, order_id: str, articles: List[Article], supplies: List[Supply] = []):
        """
        Initializes an Order object with the specified attributes.

        Args:
            order_id (str): The ID of the order.
            articles (List[Article]): The list of articles in the order.
            supplies (List[Supply], optional): The list of supplies in the order. Default is an empty list.

        """
        self.order_id = order_id
        self.articles = articles
        self.supplies = supplies

    def to_item_list(self) -> List[Item]:
        """
        Converts the articles in the order to a list of Item objects.

        Returns:
            List[Item]: The list of Item objects.

        """
        return [
            Item(
                id=article.article_id,
                width=article.width,
                length=article.length,
                height=article.height,
                weight=article.weight,
                position=None
            )
            for article in self.articles
        ]

    @classmethod
    def from_json_file(cls, file_path: str) -> 'Order':
        """
        Creates an Order object from a JSON file.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            Order: The created Order object.

        """
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as file:
            json_data = json.load(file)
        return cls.from_json(json_data)

    @classmethod
    def from_json(cls, json_data: dict) -> 'Order':
        """
        Creates an Order object from JSON data.

        Args:
            json_data (dict): The JSON data representing the order.

        Returns:
            Order: The created Order object.

        Raises:
            ValueError: If the order does not have at least one article.

        """
        order_id = json_data["order_id"]
        articles = [Article.from_json(article_data)
                    for article_data in json_data.get("articles", [])]
        supplies = [Supply.from_json(supply_data)
                    for supply_data in json_data.get("supplies", [])]

        if len(articles) < 1:
            raise ValueError("Order must have at least one article.")

        return cls(order_id, articles, supplies)
