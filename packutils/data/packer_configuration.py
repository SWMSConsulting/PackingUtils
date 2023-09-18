from enum import Enum
import logging
import random
from typing import List, Optional

from pydantic import Field, BaseModel
import itertools


class PackerConfiguration(BaseModel):

    item_select_strategy_index: Optional[int] = 0

    direction_change_min_volume: Optional[float] = 1.0

    bin_stability_factor: Optional[float] = 0.7

    allow_item_exceeds_layer: Optional[bool] = True

    @property
    def item_select_strategy(self):
        strategy = ItemSelectStrategy.get_validated_entity(
            self.item_select_strategy_index)
        return strategy

    @classmethod
    def generate_random_configurations(
        cls,
        n: int,
        bin_stability_factor: float,
        item_volumes: List[float] = []
    ) -> List['PackerConfiguration']:
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
        item_select_stategies = ItemSelectStrategy.indicies_list()

        assert isinstance(item_volumes, List) and all(
            isinstance(x, float) for x in item_volumes)
        direction_change_min_volumes = [0.0, 1.0] + item_volumes

        allow_item_exceeds_layers = [True, False]
        params = [
            item_select_stategies,
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
                item_select_strategy_index=combination[0],
                direction_change_min_volume=combination[1],
                allow_item_exceeds_layer=combination[2],
                bin_stability_factor=bin_stability_factor
            )
            logging.info("random config:", combination, cfg)
            configs.append(cfg)
        return configs

    def __hash__(self):
        return hash((
            self.item_select_strategy_index,
            self.direction_change_min_volume,
            self.bin_stability_factor
        ))


class ValidatedEnum(Enum):
    @classmethod
    def all_entities(cls):
        return [entity for entity in cls]

    @classmethod
    def indicies_list(cls):
        return [entity.value[0] for entity in cls]

    @classmethod
    def names_list(cls):
        return [entity.value[1] for entity in cls]

    @classmethod
    def get_validated_entity(cls, index: int):
        if not isinstance(index, int) or not index in cls.indicies_list():
            logging.info("Index is not valid, using default.")
            index = 0
        return [e for e in cls if e.index == index][0]

    @property
    def index(self):
        return self.value[0]

    @property
    def name(self):
        return self.value[1]


class ItemSelectStrategy(ValidatedEnum):
    # for each layer candidate loop over the items and sum the absolute height differnce between item and layer
    FITTING_BEST_Y_X_Z = (0, "FITTING_BEST_Y_X_Z")
    HIGHEST_VOLUME_FOR_EMPTY_LAYER = (1, "HIGHEST_VOLUME_FOR_EMPTY_LAYER")
    ALWAYS_HIGHEST_VOLUME = (2, "ALWAYS_HIGHEST_VOLUME")
    MAX_AREA_FOR_EMPTY_LAYER = (3, "MAX_AREA_FOR_EMPTY_LAYER")
