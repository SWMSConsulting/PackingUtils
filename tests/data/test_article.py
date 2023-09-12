import unittest
from packutils.data.article import Article


class ArticleTests(unittest.TestCase):
    def setUp(self):
        self.article_id = "article123"
        self.length = 10
        self.width = 20
        self.height = 30
        self.amount = 5
        self.weight = 2.5

        self.article = Article(
            article_id=self.article_id,
            width=self.width,
            length=self.length,
            height=self.height,
            amount=self.amount,
            weight=self.weight
        )

    def test_to_json(self):
        expected_json = {
            "id": "article123",
            "length": self.length,
            "width": self.width,
            "height": self.height,
            "weight": self.weight,
            "amount": self.amount,
        }

        json_data = self.article.to_dict()
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {
            "id": "article123",
            "width": 10,
            "length": 20,
            "height": 30,
            "weight": 2.5,
            "amount": 5,
        }

        article = Article.from_json(json_data)

        self.assertEqual(article.article_id, "article123")
        self.assertEqual(article.width, 10)
        self.assertEqual(article.length, 20)
        self.assertEqual(article.height, 30)
        self.assertEqual(article.weight, 2.5)
        self.assertEqual(article.amount, 5)


if __name__ == "__main__":
    unittest.main()
