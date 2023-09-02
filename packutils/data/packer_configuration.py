from enum import Enum
import logging
import random
from typing import List

from pydantic import Field, BaseModel
import itertools


class PackerConfiguration(BaseModel):

    item_select_strategy: int = Field(default=0)

    direction_change_min_volume: float = Field(default=1.0)

    bin_stability_factor: float = Field(default=0.7)

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

        params = [
            item_select_stategies,
            direction_change_min_volumes,
            # add here other possible parameter
        ]
        combinations = list(itertools.product(*params))

        if len(combinations) > n:
            combinations = random.sample(combinations, n)

        configs = []
        for combination in combinations:
            configs.append(
                PackerConfiguration(
                    item_select_stategie=combination[0],
                    direction_change_min_volume=combination[1],
                    bin_stability_factor=bin_stability_factor
                )
            )
        return configs


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
            print("Index is not valid, using default.")
            index = 0
        return [e for e in cls if e.value[0] == index][0]


class ItemSelectStrategy(ValidatedEnum):
    # for each layer candidate loop over the items and sum the absolute height differnce between item and layer
    FITTING_BEST_Y_X_Z = (0, "FITTING_BEST_Y_X_Z")
    HIGHEST_VOLUME_FOR_EMPTY_LAYER = (1, "HIGHEST_VOLUME_FOR_EMPTY_LAYER")
    ALWAYS_HIGHEST_VOLUME = (2, "ALWAYS_HIGHEST_VOLUME")
