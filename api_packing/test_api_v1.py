import unittest
import pytest

from fastapi.testclient import TestClient

from api import app


@pytest.fixture
def change_dir(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir("api_packing")


class TestPackerAPI(unittest.TestCase):
    def setUp(self):

        self.client = TestClient(app)
        self.base_endpoint = "/api/v1"

        self.order = {"order_id": "test", "articles": []}

    def test_ping(self):
        response = self.client.get(self.base_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Healthy"})

    def test_packing_variants(self):
        num_variants = 2
        self.order["articles"] = [
            {"id": "test1", "width": 26, "length": 10, "height": 16, "amount": 30},
            {"id": "test2", "width": 6, "length": 10, "height": 6, "amount": 11},
        ]

        data = {"order": self.order, "num_variants": num_variants}
        response = self.client.post(f"{self.base_endpoint}/variants", json=data)
        print(response.json())

        self.assertEqual(response.status_code, 200)

    def test_packing_variants_invalid_articles(self):
        num_variants = 2
        invalid_articles = [
            {"id": "test1", "width": 0, "length": 10, "height": 10, "amount": 30},
            {"id": "test1", "width": 10, "length": 0, "height": 10, "amount": 30},
            {"id": "test1", "width": 10, "length": 10, "height": 0, "amount": 30},
            {"id": "test1", "width": 10, "length": 10, "height": 10, "amount": 0},
            {
                "id": "test1",
                "width": 10,
                "length": 10,
                "height": 10,
                "weight": -1,
                "amount": 30,
            },
        ]

        for article in invalid_articles:
            self.order["articles"] = [article]
            data = {"order": self.order, "num_variants": num_variants}
            response = self.client.post(f"{self.base_endpoint}/variants", json=data)
            self.assertEqual(response.status_code, 422)

    def test_packing_variants_invalid_colli(self):
        num_variants = 2
        invalid_collis = [
            {"width": 0, "length": 10, "height": 10, "max_collis": 10},
            {"width": 10, "length": 0, "height": 10, "max_collis": 10},
            {"width": 10, "length": 10, "height": 0, "max_collis": 10},
            {"width": 10, "length": 10, "height": 10, "max_collis": 0},
        ]

        for colli in invalid_collis:
            self.order["colli_details"] = colli

        data = {"order": self.order, "num_variants": num_variants}
        response = self.client.post(f"{self.base_endpoint}/variants", json=data)

        self.assertEqual(response.status_code, 422)

    def test_packing_variants_too_large_articles(self):
        num_variants = 2
        colli = {"width": 10, "length": 10, "height": 10, "max_collis": 10}
        self.order["colli_details"] = colli

        invalid_articles = [
            {"id": "test1", "width": 20, "length": 10, "height": 10, "amount": 1},
            # {"id": "test1", "width": 10, "length": 20, "height": 10, "amount": 1}, # length is set to max length of bin
            {"id": "test1", "width": 10, "length": 10, "height": 20, "amount": 1},
        ]

        for article in invalid_articles:
            self.order["articles"] = [article]
            data = {"order": self.order, "num_variants": num_variants}
            response = self.client.post(f"{self.base_endpoint}/variants", json=data)

            self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
