
import os
import shutil
import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.packed_order import PackedOrder
from packutils.dataset.data_generator_2d import DataGenerator2d
from packutils.dataset.packing_data_loader import PackingDataLoader


class DataLoaderTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = create_temporary_directory()

        self.num_data = 1
        reference_bins = [Bin(10, 1, 10)]
        self.articles = [
            Article("item1", 2, 1, 2, 4)
        ]

        self.generator = DataGenerator2d(
            num_data=self.num_data,
            output_path=self.temp_dir,
            reference_bins=reference_bins,
            articles=self.articles
        )
        self.generator.generate_data()
        self.data_loader = PackingDataLoader(self.generator.dataset_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_load_valid_dataset(self):

        # Load the dataset
        self.data_loader.load_data()

        # Check the loaded data and info
        self.assertEqual(len(self.data_loader.data), 1)
        self.assertEqual(self.data_loader.info["dimensionality"], "2D")

    def test_load_missing_dataset(self):
        with self.assertRaises(ValueError):
            data_loader = PackingDataLoader("nodirfound")
            data_loader.load_data()

    def test_load_empty_dataset(self):
        # Create an empty test dataset directory
        dataset_dir = os.path.join(self.temp_dir, "empty_dataset")
        os.makedirs(dataset_dir)

        with self.assertRaises(ValueError):
            data_loader = PackingDataLoader(dataset_dir)
            data_loader.load_data()

    def test_load_missing_info(self):

        os.remove(os.path.join(self.generator.dataset_dir, "info.json"))
        with self.assertRaises(ValueError):
            self.data_loader = PackingDataLoader(self.generator.dataset_dir)

    def test_load_with_transform_fn(self):

        def _item_dim_pos(packed_order: PackedOrder):
            data_x, data_y = [], []
            for item in packed_order.packing_variants[0].bins[0].packed_items:
                data_x.append([item.width, item.height])
                data_y.append([item.position.x, item.position.z])

            return data_x, data_y

        # Load the dataset with the transform function
        data_loader = PackingDataLoader(
            path=self.generator.dataset_dir, transform_fn=_item_dim_pos)
        data_loader.load_data()

        x, y = data_loader.data[0]
        self.assertEqual(x[0], [2, 2])
        self.assertEqual(y[0], [0, 0])


def create_temporary_directory():
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


if __name__ == "__main__":
    unittest.main()
