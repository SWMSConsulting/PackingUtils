import unittest
import os

from packutils.data.item import Item
from packutils.data.bin import Bin
from packutils.data.position import Position
from packutils.data.packing_variant import PackingVariant
from packutils.visual.packing_visualization import PackingVisualization


class TestPackingVisualization(unittest.TestCase):
    def setUp(self):
        self.clean_up = True
        self.output_dir = os.path.join(os.path.dirname(__file__), "images")
        self.delete_dir = not os.path.exists(self.output_dir)

        self.visualization = PackingVisualization()

        self.variant = PackingVariant()
        bin = Bin(width=10, length=10, height=5)
        item1 = Item(id="item1", width=1, length=1, height=1,
                     position=Position(x=0, y=0, z=0))
        bin.pack_item(item1)
        item2 = Item(id="item2", width=1, length=1, height=1,
                     position=Position(x=1, y=0, z=0))
        bin.pack_item(item2)
        item3 = Item(id="item3", width=1, length=1, height=1,
                     position=Position(x=0, y=1, z=0))
        bin.pack_item(item3)
        item4 = Item(id="item4", width=1, length=1, height=1,
                     position=Position(x=0, y=0, z=1))
        bin.pack_item(item4)
        self.variant.add_bin(bin)

    def tearDown(self):
        # Perform cleanup or teardown operations here
        # This method will be called after all the test methods in the class have been executed
        if self.clean_up:
            import glob
            image_files = glob.glob(os.path.join(
                self.output_dir, "packing_*.png"))
            for f in image_files:
                os.remove(f)
            if self.delete_dir and os.path.exists(self.output_dir):
                os.removedirs(self.output_dir)

    def test_visualize_bin_3d(self):
        num_images_before = self._count_image_outputs()
        self.visualization.visualize_bin(
            self.variant.bins[0], title="Test", show=False, output_dir=self.output_dir)
        self.assertEqual(self._count_image_outputs(), num_images_before + 1)

    def test_visualize_packing_variant(self):
        num_images_before = self._count_image_outputs()
        self.variant.add_bin(self.variant.bins[0])
        self.visualization.visualize_packing_variant(
            self.variant, show=False, output_dir=self.output_dir)
        self.assertEqual(self._count_image_outputs(), num_images_before + 2)

    def test_visualize_bin_2d(self):
        bin = self.variant.bins[0]

        bin.width = 1
        num_images_before = self._count_image_outputs()
        self.visualization.visualize_bin(
            bin, show=False, output_dir=self.output_dir)
        self.assertEqual(self._count_image_outputs(), num_images_before + 1)
        bin.width = 10

        bin.length = 1
        num_images_before = self._count_image_outputs()
        self.visualization.visualize_bin(
            bin, show=False, output_dir=self.output_dir)
        self.assertEqual(self._count_image_outputs(), num_images_before + 1)
        bin.length = 10

        bin.height = 1
        num_images_before = self._count_image_outputs()
        self.visualization.visualize_bin(
            bin, show=False, output_dir=self.output_dir)
        self.assertEqual(self._count_image_outputs(), num_images_before + 1)
        bin.height = 10

    def test_visualize_bin_2d_with_snappoints(self):
        bin = Bin(10, 1, 10)
        bin.pack_item(Item("", 2, 1, 2, position=Position(1, 0, 0)))

        bin.length = 1
        num_images_before = self._count_image_outputs()
        self.visualization.visualize_bin(
            bin, snappoint_min_z=0,
            show=True, output_dir=self.output_dir)
        self.assertEqual(self._count_image_outputs(), num_images_before + 1)

    def _count_image_outputs(self):
        import glob
        image_files = glob.glob(os.path.join(self.output_dir, "packing_*.png"))
        return len(image_files)


if __name__ == "__main__":
    unittest.main()
