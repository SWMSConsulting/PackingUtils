from enum import Enum
import logging
import random
from typing import List, Optional

from pydantic import BaseModel
import itertools


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ItemSelectStrategy(str, ExtendedEnum):
    LARGEST_H_W_L = "largest_h_w_l"
    LARGEST_VOLUME = "largest_volume"


class PackerConfiguration(BaseModel):
    default_select_strategy: Optional[
        ItemSelectStrategy
    ] = ItemSelectStrategy.LARGEST_VOLUME

    new_layer_select_strategy: Optional[ItemSelectStrategy] = default_select_strategy

    direction_change_min_volume: Optional[float] = 1.0

    bin_stability_factor: Optional[float] = 0.7

    allow_item_exceeds_layer: Optional[bool] = True

    mirror_walls: Optional[bool] = False

    @classmethod
    def generate_random_configurations(
        cls, n: int, bin_stability_factor: float, item_volumes: List[float] = []
    ) -> List["PackerConfiguration"]:
        """
        Generate a list of random PackerConfiguration objects based on the given parameters.

        Args:
            n (int): The number of random configurations to generate.
            bin_stability_factor (float): The stability factor for the bin.
            item_volumes (List[float], optional): A list of item volumes. Defaults to an empty list.

        Returns:
            List[PackerConfiguration]: A list of randomly generated PackerConfiguration objects.

        Raises:
            AssertionError: If item_volumes is not a list of floats.
        """
        default_select_stategies = ItemSelectStrategy.list()
        new_layer_select_stategies = ItemSelectStrategy.list()

        assert isinstance(item_volumes, List) and all(
            isinstance(x, float) for x in item_volumes
        )
        direction_change_min_volumes = [0.0, 1.0] + item_volumes

        allow_item_exceeds_layers = [True, False]
        params = [
            default_select_stategies,
            new_layer_select_stategies,
            direction_change_min_volumes,
            allow_item_exceeds_layers,
            # add here other possible parameter
        ]
        combinations = list(itertools.product(*params))
        if len(combinations) > n:
            combinations = random.sample(combinations, n)

        configs = []
        for combination in combinations:
            cfg = PackerConfiguration(
                default_select_strategy=combination[0],
                new_layer_select_strategy=combination[1],
                direction_change_min_volume=combination[2],
                allow_item_exceeds_layer=combination[3],
                bin_stability_factor=bin_stability_factor,
                mirror_walls=True,
            )
            logging.info("random config:", combination, cfg)
            configs.append(cfg)
        return configs

    def __hash__(self):
        return hash(
            (
                self.item_select_strategy_index,
                self.direction_change_min_volume,
                self.bin_stability_factor,
            )
        )
