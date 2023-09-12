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
        response = self.client.get("/bin")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")

        # Open the image using Pillow and check that it is indeed an image
        image = Image.open(BytesIO(response.content))
        assert isinstance(image, Image.Image)


if __name__ == "__main__":
    unittest.main()
