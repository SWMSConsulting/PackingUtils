import os
import json
import unittest
from unittest.mock import MagicMock

from packutils.data.packed_order import PackedOrder


class DataLoader:
    """
    A class for loading packed order data from a dataset.

    Attributes:
        transform_fn (callable): A function to transform the loaded packed order data (optional).
        info (dict): Information about the loaded dataset.
        data (list): List of loaded PackedOrder objects.
    """

    def __init__(self, transform_fn=None):
        """
        Initializes a new instance of the DataLoader class.

        Args:
            transform_fn (callable): A function to transform the loaded packed order data (optional).
        """
        self.transform_fn = transform_fn
        self.info = None
        self.data = []

    def load(self, path):
        """
        Load packed order data from a dataset.

        Args:
            path (str): Path to the dataset directory.

        Raises:
            ValueError: If the dataset directory or required files are not found.

        """
        if not os.path.exists(path):
            raise ValueError("Could not find dataset")

        self._load_info(path)
        self._load_data(path)

    def _load_data(self, path):
        """
        Load packed order data from individual order files.

        Args:
            path (str): Path to the dataset directory.

        Raises:
            ValueError: If the dataset is empty or order files are not found.

        """
        if not os.path.exists(os.path.join(path, "order1.json")):
            raise ValueError("Dataset is empty")

        order_files = [f for f in os.listdir(path) if f.startswith("order")]
        for order_path in order_files:
            packed = PackedOrder.load_from_file(os.path.join(path, order_path))
            if self.transform_fn:
                packed = self.transform_fn(packed)
            self.data.append(packed)

    def _load_info(self, path):
        """
        Load dataset information from the info.json file.

        Args:
            path (str): Path to the dataset directory.

        Raises:
            ValueError: If the info.json file is not found.

        """
        info_path = os.path.join(path, "info.json")
        if not os.path.exists(info_path):
            raise ValueError("Could not find dataset info")

        with open(info_path, "r") as f:
            json_data = json.load(f)
            self.info = json_data
