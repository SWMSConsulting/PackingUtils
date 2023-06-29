import json
from typing import List
from packutils.data.article import Article
from packutils.data.packing_variant import PackingVariant


class PackedOrder:
    """
    Represents a packed order containing multiple packing variants.

    Attributes:
        order_id (str): The ID of the order.
        packing_variants (List[PackingVariant]): A list of packing variants associated with the order.
    """

    def __init__(self, order_id: str):
        """
        Initializes a new instance of the PackedOrder class.

        Args:
            order_id (str): The ID of the order.
        """
        if not isinstance(order_id, str):
            raise TypeError("order_id should be of type string.")

        self.order_id = order_id
        self.packing_variants: List[PackingVariant] = []

    def add_packing_variant(self, packing_variant: PackingVariant):
        """
        Adds a packing variant to the packed order.

        Args:
            packing_variant (PackingVariant): The packing variant to be added.
        """
        if not isinstance(packing_variant, PackingVariant):
            raise TypeError(
                "Packing variant should be of class PackingVariant.")

        self.packing_variants.append(packing_variant)

    def get_articles_list(self) -> List[Article]:
        """
        Get a list of articles based on the packed items in the packing variants and unpacked items.

        Returns:
            List[Article]: A list of articles with aggregated information.

        Example:
            Suppose the packing variants contain the following items:
            - item1 (width=10, length=10, height=10, weight=1.0)
            - item2 (width=20, length=20, height=20, weight=2.0)
            - item1 (width=10, length=10, height=10, weight=1.0)

            The function will return the following list of articles:
            [
                Article(article_id="item1", width=10, length=10, height=10, amount=2, weight=2.0),
                Article(article_id="item2", width=20, length=20, height=20, amount=1, weight=2.0)
            ]
        """
        articles = []

        items = []
        for variant in self.packing_variants:
            for bin in variant.bins:
                for item in bin.packed_items:
                    items.append(item)
            for item in variant.unpacked_items:
                items.append(item)

        for item in items:
            filtered = list(
                filter(lambda x: x.article_id == item.id, articles))
            if len(filtered) > 0:
                index = articles.index(filtered[0])
                articles[index].amount += 1
            else:
                articles.append(
                    Article(
                        article_id=item.id,
                        width=item.width,
                        length=item.length,
                        height=item.height,
                        amount=1,
                        weight=item.weight,
                    )
                )
        return articles

    def to_json(self) -> str:
        """
        Convert the PackedOrder object to JSON format.

        Returns:
            str: JSON representation of the PackedOrder.
        """
        data = {
            "order_id": self.order_id,
            "packing_variants": [],
            "articles": [article.to_json() for article in self.get_articles_list()]
        }

        for variant in self.packing_variants:
            variant_data = []

            for idx, bin in enumerate(variant.bins):
                positions = []
                for item in bin.packed_items:
                    positions.append({
                        "article_id": item.id,
                        "centerpoint_x": item.centerpoint().x,
                        "centerpoint_y": item.centerpoint().y,
                        "centerpoint_z": item.centerpoint().z,
                        "rotation": item.centerpoint().rotation

                    })

                variant_data.append({
                    "colli": idx + 1,
                    "colli_total": len(variant.bins),
                    "colli_dimension": {
                        "width": bin.width,
                        "length": bin.length,
                        "height": bin.height
                    },
                    "positions": positions
                })

            data["packing_variants"].append(variant_data)

        return json.dumps(data, indent=4)

    def write_to_file(self, file_path: str):
        """
        Write the PackedOrder object to a JSON file.

        Args:
            file_path (str): The path of the file to write the JSON data to.
        """
        json_data = self.to_json()
        with open(file_path, "w") as file:
            file.write(json_data)
