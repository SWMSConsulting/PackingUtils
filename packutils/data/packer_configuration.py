from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PackerConfiguration(BaseModel):
    item_select_strategy: int = Field(default=None)
    direction_change_min_volume: float = Field(default=2.0)


class ValidatedEnum(Enum):
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


print(PackerConfiguration(item_select_strategy=2))

# > number=[2, 8]
