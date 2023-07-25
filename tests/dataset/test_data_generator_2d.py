import shutil
import os
import unittest
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.packed_order import PackedOrder
from packutils.dataset.data_generator_2d import DataGenerator2d
from packutils.visual.packing_visualization import PackingVisualization


class TestDataGenerator2d(unittest.TestCase):

    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = create_temporary_directory()

        self.num_data = 5
        self.reference_bins = [Bin(10, 20, 1)]
        self.articles = [
            Article("item1", 2, 5, 1, 8),
            Article("item2", 3, 6, 1, 8),
            Article("item3", 4, 7, 1, 8)
        ]

    def tearDown(self):
        remove_temporary_directory(self.temp_dir)

    def test_generate_data_greedy(self):
        return
        for pack_algo in ["guillotine"]:
            generator = DataGenerator2d(
                num_data=self.num_data,
                output_path=self.temp_dir,
                reference_bins=self.reference_bins,
                articles=self.articles,
                pack_algo=pack_algo
            )
            # Generate data
            generator.generate_data()

            # Check if the dataset directory exists
            self.assertTrue(os.path.exists(generator.dataset_dir))

            # Check if the orders are correctly generated
            order_files = [f for f in os.listdir(
                generator.dataset_dir) if f.startswith("order")]
            self.assertEqual(len(order_files), self.num_data)

            # Check if the generated orders can be loaded and have packing variants
            for order_file in order_files:
                order_file_path = os.path.join(
                    generator.dataset_dir, order_file)
                packed_order = PackedOrder.load_from_file(order_file_path)
                self.assertIsInstance(packed_order, PackedOrder)
                self.assertTrue(len(packed_order.packing_variants) > 0)
                self.assertLessEqual(
                    len(packed_order.packing_variants[0].bins), len(self.reference_bins))

            remove_temporary_directory(generator.dataset_dir)

    def test_generate_data_palletier(self):
        reference_bins = [Bin(10, 1, 20)]
        articles = [
            Article("item1", 2, 1, 5, 8),
            Article("item2", 3, 1, 6, 8),
            Article("item3", 4, 1, 7, 8)
        ]
        generator = DataGenerator2d(
            num_data=self.num_data,
            output_path=self.temp_dir,
            reference_bins=reference_bins,
            articles=articles,
            packing_solver="palletier"
        )
        # Generate data
        generator.generate_data()

        # Check if the dataset directory exists
        self.assertTrue(os.path.exists(generator.dataset_dir))

        # Check if the orders are correctly generated
        order_files = [f for f in os.listdir(
            generator.dataset_dir) if f.startswith("order")]
        self.assertEqual(len(order_files), self.num_data)

        # Check if the generated orders can be loaded and have packing variants
        for order_file in order_files:
            order_file_path = os.path.join(generator.dataset_dir, order_file)
            packed_order = PackedOrder.load_from_file(order_file_path)
            PackingVisualization().visualize_packing_variant(
                packed_order.packing_variants[0])
            self.assertIsInstance(packed_order, PackedOrder)
            self.assertTrue(len(packed_order.packing_variants) > 0)
            self.assertLessEqual(
                len(packed_order.packing_variants[0].bins), len(self.reference_bins))

        remove_temporary_directory(generator.dataset_dir)

    def test_generate_data_py3dbp(self):
        generator = DataGenerator2d(
            num_data=self.num_data,
            output_path=self.temp_dir,
            reference_bins=self.reference_bins,
            articles=self.articles,
            packing_solver="py3dbp"
        )
        # Generate data
        generator.generate_data()

        # Check if the dataset directory exists
        self.assertTrue(os.path.exists(generator.dataset_dir))

        # Check if the orders are correctly generated
        order_files = [f for f in os.listdir(
            generator.dataset_dir) if f.startswith("order")]
        self.assertEqual(len(order_files), self.num_data)

        # Check if the generated orders can be loaded and have packing variants
        for order_file in order_files:
            order_file_path = os.path.join(
                generator.dataset_dir, order_file)
            packed_order = PackedOrder.load_from_file(order_file_path)
            self.assertIsInstance(packed_order, PackedOrder)
            self.assertTrue(len(packed_order.packing_variants) > 0)
            self.assertLessEqual(
                len(packed_order.packing_variants[0].bins), len(self.reference_bins))

        remove_temporary_directory(generator.dataset_dir)


def create_temporary_directory():
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def remove_temporary_directory(directory):
    shutil.rmtree(directory)


if __name__ == '__main__':
    unittest.main()
