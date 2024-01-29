from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ItemSelectStrategy(str, ExtendedEnum):
    LARGEST_H_W_L = "largest_h_w_l"
    LARGEST_W_H_L = "largest_w_h_l"
    LARGEST_VOLUME = "largest_volume"


class PackerConfiguration(BaseModel):
    default_select_strategy: Optional[
        ItemSelectStrategy
    ] = ItemSelectStrategy.LARGEST_H_W_L

    new_layer_select_strategy: Optional[
        ItemSelectStrategy
    ] = ItemSelectStrategy.LARGEST_H_W_L

    direction_change_min_volume: Optional[float] = 1.0

    bin_stability_factor: Optional[float] = 1.0

    allow_item_exceeds_layer: Optional[bool] = False

    mirror_walls: Optional[bool] = False

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
