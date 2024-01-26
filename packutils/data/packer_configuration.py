from enum import Enum
import logging
import os
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


dotenv_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv

    print("Loading .env file")
    load_dotenv(dotenv_path)

env_default_select_strategy = os.environ.get("DEFAULT_SELECT_STRATEGY", None)
env_new_layer_select_strategy = os.environ.get("NEW_LAYER_SELECT_STRATEGY", None)
env_allow_item_exceeds_layer = os.environ.get("ALLOW_ITEM_EXCEEDS_LAYER", None)
env_mirror_walls = os.environ.get("MIRROR_WALLS", None)
env_bin_stability_factor = os.environ.get("BIN_STABILITY_FACTOR", 1.0)

print("Env variables:")
print("env_default_select_strategy", env_default_select_strategy)
print("env_new_layer_select_strategy", env_new_layer_select_strategy)
print("env_allow_item_exceeds_layer", env_allow_item_exceeds_layer)
print("env_mirror_walls", env_mirror_walls)
print("env_bin_stability_factor", env_bin_stability_factor)


class PackerConfiguration(BaseModel):
    default_select_strategy: Optional[ItemSelectStrategy] = (
        ItemSelectStrategy(env_default_select_strategy)
        if env_default_select_strategy
        else ItemSelectStrategy.LARGEST_VOLUME
    )

    new_layer_select_strategy: Optional[ItemSelectStrategy] = (
        ItemSelectStrategy(env_new_layer_select_strategy)
        if env_new_layer_select_strategy
        else ItemSelectStrategy.LARGEST_VOLUME
    )

    direction_change_min_volume: Optional[float] = 1.0

    bin_stability_factor: Optional[float] = env_bin_stability_factor

    allow_item_exceeds_layer: Optional[bool] = (
        env_allow_item_exceeds_layer if env_allow_item_exceeds_layer else False
    )

    mirror_walls: Optional[bool] = env_mirror_walls if env_mirror_walls else False

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
        default_select_stategies = (
            [ItemSelectStrategy(env_default_select_strategy)]
            if env_default_select_strategy
            else ItemSelectStrategy.list()
        )
        new_layer_select_stategies = (
            [ItemSelectStrategy(env_new_layer_select_strategy)]
            if env_new_layer_select_strategy
            else ItemSelectStrategy.list()
        )
        allow_item_exceeds_layers = (
            [env_allow_item_exceeds_layer]
            if env_allow_item_exceeds_layer != None
            else [True, False]
        )
        mirror_walls = [env_mirror_walls] if env_mirror_walls != None else [True, False]

        assert isinstance(item_volumes, List) and all(
            isinstance(x, float) for x in item_volumes
        )
        direction_change_min_volumes = [0.0, 1.0] + item_volumes

        params = [
            default_select_stategies,
            new_layer_select_stategies,
            direction_change_min_volumes,
            allow_item_exceeds_layers,
            mirror_walls
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
                bin_stability_factor=bin_stability_factor,
                allow_item_exceeds_layer=combination[3],
                mirror_walls=combination[4],
            )
            logging.info("random config:", combination, cfg)
            configs.append(cfg)
        return configs

    def __hash__(self):
        return hash(
            (
                self.default_select_strategy,
                self.new_layer_select_strategy,
                self.direction_change_min_volume,
                self.bin_stability_factor,
                self.allow_item_exceeds_layer,
                self.mirror_walls,
            )
        )
