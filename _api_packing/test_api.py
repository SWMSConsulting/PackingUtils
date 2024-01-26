import json
from fastapi.testclient import TestClient
from api import app
import unittest

from packutils.data.article import Article
from packutils.data.order import Order


class TestPackerAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ping(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Healthy"})

    def test_packing_variants(self):
        articles = [
            Article("test1", width=26, length=10, height=16, amount=30),
            Article("test2", width=6, length=10, height=6, amount=11),
        ]
        test_order = Order(order_id="test", articles=articles)

        num_variants = 2
        orderDict = test_order.to_dict()
        orderDict["colli_details"] = {
            "width": 80,
            "length": 10,
            "height": 100,
            "max_collis": 10,
        }
        data = {"order": orderDict, "num_variants": num_variants, "config": {}}
        response = self.client.post("variants", json=data)
        body = json.loads(response.text)
        self.assertEqual(response.status_code, 200)
        print(f"Response:   {body}")


if __name__ == "__main__":
    unittest.main()
