import random
import unittest

from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration


class TestGenerateRandomConfigurations(unittest.TestCase):
    def test_generate_only_possible_number_of_configurations(self):
        n = 100
        bin_stability_factor = 0.75
        item_volumes = []

        configs = PackerConfiguration.generate_random_configurations(
            n, bin_stability_factor, item_volumes)

        self.assertEqual(len(configs), 2 *
                         len(ItemSelectStrategy.indicies_list()))
        for config in configs:
            self.assertIsInstance(config, PackerConfiguration)
            self.assertIn(config.item_select_strategy.index,
                          ItemSelectStrategy.indicies_list())
            self.assertIn(config.direction_change_min_volume, [0.0, 1.0])
            self.assertEqual(config.bin_stability_factor, bin_stability_factor)

    def test_generate_random_configurations(self):
        n = 4
        bin_stability_factor = 0.75
        item_volumes = [0.5, 0.6]

        configs = PackerConfiguration.generate_random_configurations(
            n, bin_stability_factor, item_volumes)
        configs = list(set(configs))

        self.assertEqual(len(configs), n)
        for config in configs:
            self.assertIsInstance(config, PackerConfiguration)
            self.assertIn(config.item_select_strategy.index,
                          ItemSelectStrategy.indicies_list())
            self.assertIn(config.direction_change_min_volume,
                          [0.0, 1.0] + item_volumes)
            self.assertEqual(config.bin_stability_factor, bin_stability_factor)


if __name__ == '__main__':
    unittest.main()
