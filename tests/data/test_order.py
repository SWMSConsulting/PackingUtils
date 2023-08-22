from packutils.data.order import Article, Order
import unittest


class TestImports(unittest.TestCase):

    def test_load_from_json_file(self):
        order = Order.from_json_file("tests/test_order.json")

        self.assertEqual(order.order_id, "xyz", "Failed to load order_id")
        self.assertEqual(len(order.articles), 1, "Failed to load articles")
        self.assertEqual(len(order.supplies), 1, "Failed to load supplies")

    def test_convert_to_item(self):
        article = Article(
            article_id="test_article", length=20,
            width=20, height=20, weight=0.0, amount=20)
        order = Order(order_id="test", articles=[article])
        items = order.to_item_list()

        self.assertEqual(len(items), 1, "Failed to convert")
        self.assertEqual(items[0].width, article.width,
                         "Failed to convert order to items list (wrong width)")
        self.assertEqual(items[0].length, article.length,
                         "Failed to convert order to items list (wrong length)")
        self.assertEqual(items[0].height, article.height,
                         "Failed to convert order to items list (wrong height)")
        self.assertEqual(items[0].weight, article.weight,
                         "Failed to convert order to items list (wrong weight)")
        self.assertEqual(items[0].position, None,
                         "Failed to convert order to items list (wrong position)")

    def test_to_json(self):
        # Create an Order object for testing
        articles = [Article("article1", width=10, length=1,
                            height=20, amount=5, weight=100)]
        supplies = []
        order = Order("123", articles, supplies)

        # Convert Order object to JSON dictionary
        order_json = order.to_dict()

        # Define the expected JSON dictionary
        expected_json = {
            "order_id": "123",
            "articles": [{
                "id": "article1",
                "width": 10,
                "length": 1,
                "height": 20,
                "amount": 5,
                "weight": 100
            }],
            "supplies": []
        }

        # Compare the generated JSON with the expected JSON
        self.assertEqual(order_json, expected_json)
        self.assertEqual(order, Order.from_json(expected_json))


if __name__ == '__main__':
    unittest.main()
