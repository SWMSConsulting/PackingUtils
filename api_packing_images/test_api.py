import json
from PIL import Image
from io import BytesIO
from fastapi.testclient import TestClient
from api import app
import unittest


class TestPackerAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ping(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "Healthy"})

    def test_bin_image(self):
        data = {
            "packages": [
                {
                    "width": 2,
                    "length": 1,
                    "height": 2,
                    "x": 0,
                    "y": 0,
                    "z": 0
                }
            ],
            "colli_details": {
                "width": 10,
                "length": 1,
                "height": 10
            }
        }

        response = self.client.post("/bin", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")

        # Open the image using Pillow and check that it is indeed an image
        image = Image.open(BytesIO(response.content))
        assert isinstance(image, Image.Image)

    def test_bin_image_colli_invalid(self):
        data = {
            "packages": [],
            "colli_details": {
                "width": 0,
                "length": 1,
                "height": 10
            }
        }

        response = self.client.post("/bin", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.headers["content-type"], "application/json")

    def test_bin_image_package_invalid(self):
        data = {
            "packages": [
                {
                    "width": 0,
                    "length": 1,
                    "height": 2,
                    "x": 0,
                    "y": 0,
                    "z": 0
                }
            ],
            "colli_details": {
                "width": 10,
                "length": 1,
                "height": 10
            }
        }

        response = self.client.post("/bin", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.headers["content-type"], "application/json")

    def test_bin_image_position_invalid(self):
        data = {
            "packages": [
                {
                    "width": 2,
                    "length": 1,
                    "height": 2,
                    "x": 0,
                    "y": 0,
                    "z": 2
                }
            ],
            "colli_details": {
                "width": 10,
                "length": 1,
                "height": 10
            }
        }

        response = self.client.post("/bin", json=data)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.headers["content-type"], "application/json")


if __name__ == "__main__":
    unittest.main()
