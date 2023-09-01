from enum import Enum
import logging

from pydantic import Field, BaseModel


class PackerConfiguration(BaseModel):

    item_select_strategy: int = Field(default=0)

    direction_change_min_volume: float = Field(default=1.0)

    bin_stability_factor: float = Field(default=0.75)



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
