import json
import os
import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.packing_variant import PackingVariant
from packutils.data.packed_order import PackedOrder
from packutils.data.position import Position


class TestPackedOrder(unittest.TestCase):
    def setUp(self):
        self.order_id = "123"
        self.packed_order = PackedOrder(self.order_id)

    def test_add_packing_variant(self):
        packing_variant = PackingVariant()

        self.packed_order.add_packing_variant(packing_variant)
        self.assertEqual(len(self.packed_order.packing_variants), 1)
        self.assertEqual(
            self.packed_order.packing_variants[0], packing_variant)

    def test_add_packing_variant_multiple(self):
        packing_variant1 = PackingVariant()
        packing_variant2 = PackingVariant()
        self.packed_order.add_packing_variant(packing_variant1)
        self.packed_order.add_packing_variant(packing_variant2)

        self.assertEqual(len(self.packed_order.packing_variants), 2)
        self.assertEqual(
            self.packed_order.packing_variants[0], packing_variant1)
        self.assertEqual(
            self.packed_order.packing_variants[1], packing_variant2)

    def test_add_packing_variant_invalid_type(self):
        with self.assertRaises(TypeError):
            self.packed_order.add_packing_variant("invalid")

    def test_get_articles_list(self):
        packed_order = PackedOrder(order_id="xyz")
        item1 = Item(
            id="item1", width=1, length=1, height=1,
            weight=1.0, position=Position(x=0, y=0, z=0))
        item2 = Item(
            id="item2", width=1, length=1, height=1,
            weight=1.0, position=Position(x=2, y=2, z=2))
        item3 = Item(
            id="item1", width=1, length=1, height=1,
            weight=1.0, position=Position(x=0, y=0, z=0))
        item4 = Item(id="item3", width=1, length=1, height=1, weight=1.0)

        bin1 = Bin(width=10, length=10, height=10)
        bin1.pack_item(item1)
        bin1.pack_item(item2)
        variant1 = PackingVariant()
        variant1.add_bin(bin1)
        packed_order.add_packing_variant(variant1)

        bin2 = Bin(width=15, length=15, height=15)
        bin2.pack_item(item3)
        variant2 = PackingVariant()
        variant2.add_bin(bin2)
        variant2.add_unpacked_item(item4, error_message=None)
        packed_order.add_packing_variant(variant2)

        expected_articles = [
            Article(article_id="item1", width=1, length=1,
                    height=1, amount=2, weight=1.0),
            Article(article_id="item2", width=1, length=1,
                    height=1, amount=1, weight=1.0),
            Article(article_id="item3", width=1, length=1,
                    height=1, amount=1, weight=1.0),
        ]

        articles = packed_order.get_articles_list()

        self.assertEqual(len(articles), len(expected_articles))
        for article, expected_article in zip(articles, expected_articles):
            self.assertEqual(article.article_id, expected_article.article_id)
            self.assertEqual(article.width, expected_article.width)
            self.assertEqual(article.length, expected_article.length)
            self.assertEqual(article.height, expected_article.height)
            self.assertEqual(article.amount, expected_article.amount)
            self.assertEqual(article.weight, expected_article.weight)

    def test_to_json(self):
        packed_order = PackedOrder("order123")

        variant1 = PackingVariant()
        variant2 = PackingVariant()

        bin1 = Bin(10, 10, 10)
        bin2 = Bin(20, 20, 20)

        item1 = Item("item1", 1, 1, 1, 1.0, Position(x=0, y=0, z=0))
        item2 = Item("item2", 1, 1, 1, 2.0, Position(x=0, y=0, z=0))
        item3 = Item("item1", 1, 1, 1, 1.0, Position(x=1, y=0, z=0))

        bin1.pack_item(item1)
        bin2.pack_item(item2)
        bin2.pack_item(item3)

        variant1.add_bin(bin1)
        variant2.add_bin(bin2)

        packed_order.add_packing_variant(variant1)
        packed_order.add_packing_variant(variant2)

        expected_json = {
            "order_id": "order123",
            "packing_variants": [
                [
                    {
                        "colli": 1,
                        "colli_total": 1,
                        "colli_dimension": {
                            "width": 10,
                            "length": 10,
                            "height": 10
                        },
                        "positions": [
                            {
                                "article_id": "item1",
                                "centerpoint_x": 0,
                                "centerpoint_y": 0,
                                "centerpoint_z": 0,
                                "rotation": 0.0
                            }
                        ]
                    }
                ],
                [
                    {
                        "colli": 1,
                        "colli_total": 1,
                        "colli_dimension": {
                            "width": 20,
                            "length": 20,
                            "height": 20
                        },
                        "positions": [
                            {
                                "article_id": "item2",
                                "centerpoint_x": 0,
                                "centerpoint_y": 0,
                                "centerpoint_z": 0.0,
                                "rotation": 0.0
                            },
                            {
                                "article_id": "item1",
                                "centerpoint_x": 1,
                                "centerpoint_y": 0,
                                "centerpoint_z": 0,
                                "rotation": 0.0
                            }
                        ]
                    }
                ]
            ],
            "articles": [
                {
                    "id": "item1",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "amount": 2,
                    "weight": 1.0
                },
                {
                    "id": "item2",
                    "length": 1,
                    "width": 1,
                    "height": 1,
                    "amount": 1,
                    "weight": 2.0
                }
            ]
        }

        path = os.path.join(os.path.dirname(__file__), "testPackingBins.json")
        packed_order.write_to_file(path)
        with open(path, "r") as f:
            parsed_json = json.load(f)

        self.assertTrue(os.path.exists(path))
        self.assertEqual(parsed_json["order_id"], expected_json["order_id"])
        self.assertEqual(parsed_json["articles"], expected_json["articles"])
        self.assertEqual(parsed_json["packing_variants"],
                         expected_json["packing_variants"])

        os.remove(path)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
