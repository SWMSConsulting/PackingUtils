import glob
import os
import json
from typing import List
from packutils.data.packed_order import PackedOrder
from packutils.data.bin import Bin


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
        self._bin_list = []

        if not os.path.exists(path):
            raise ValueError("Could not find dataset")

        self.path = path
        self.orders_path = path
        if os.path.isdir(os.path.join(self.orders_path, "orders")):
            self.orders_path = os.path.join(self.orders_path, "orders")

        self._load_info()

    def get_bin_list(self) -> List[Bin]:
        if len(self._bin_list) < 1:
            self._bin_list = []
            for data in self.data:
                for bin in data.packing_variants[0].bins:
                    self._bin_list.append(bin)
        return self._bin_list

    def load_data(self):
        """
        Load packed order data from individual order files.

        Raises:
            ValueError: If the dataset is empty or order files are not found.

        """
        self._bin_list = []

        order_files = glob.glob(os.path.join(self.orders_path, "order*.json"))
        if len(order_files) < 1:
            raise ValueError("Dataset is empty")

        for order_path in order_files:
            packed = PackedOrder.load_from_file(order_path)
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
