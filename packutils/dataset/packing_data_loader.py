import os
import json
from packutils.data.packed_order import PackedOrder


class PackingDataLoader:
    """
    A class for loading packed order data from a dataset.

    Attributes:
        transform_fn (callable): A function to transform the loaded packed order data (optional).
        info (dict): Information about the loaded dataset.
        data (list): List of loaded PackedOrder objects.
    """

    def __init__(self, path: str, transform_fn=None):
        """
        Initializes a new instance of the DataLoader class.

        Args:
            transform_fn (callable): A function to transform the loaded packed order data (optional).
            path (str): Path to the dataset directory.

        Raises:
            ValueError: If the dataset directory or required files are not found.
        """
        self.transform_fn = transform_fn
        self.info = None
        self.data = []

        if not os.path.exists(path):
            raise ValueError("Could not find dataset")

        self.path = path
        self._load_info()

    def load_data(self):
        """
        Load packed order data from individual order files.

        Raises:
            ValueError: If the dataset is empty or order files are not found.

        """
        if not os.path.exists(os.path.join(self.path, "order1.json")):
            raise ValueError("Dataset is empty")

        order_files = [f for f in os.listdir(
            self.path) if f.startswith("order")]
        for order_path in order_files:
            packed = PackedOrder.load_from_file(
                os.path.join(self.path, order_path))
            if self.transform_fn:
                packed = self.transform_fn(packed)
            self.data.append(packed)

    def _load_info(self):
        """
        Load dataset information from the info.json file.

        Raises:
            ValueError: If the info.json file is not found.

        """
        info_path = os.path.join(self.path, "info.json")
        if not os.path.exists(info_path):
            raise ValueError("Could not find dataset info")

        with open(info_path, "r") as f:
            json_data = json.load(f)
            self.info = json_data
