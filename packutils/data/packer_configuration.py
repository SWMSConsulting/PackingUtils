from enum import Enum
import logging

from pydantic import Field, BaseModel, field_validator


class PackerConfiguration(BaseModel):

    item_select_strategy: int = Field(default=None)

    direction_change_min_volume: float = Field(default=1.0)

    bin_stability_factor: float = Field(default=0.75)

    @field_validator("direction_change_min_volume", "bin_stability_factor")
    def check_in_range(cls, v):
        if v < 0:
            v = 0.0
            logging.info("Value must be greater than or equal 0")
        if v > 1:
            v = 1.0
            logging.info("Value must be smaller than or equal 1")
        return v


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


print(PackerConfiguration(bin_stability_factor=2.0))
