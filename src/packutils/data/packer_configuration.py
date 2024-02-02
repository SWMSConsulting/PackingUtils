from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ItemGroupingMode(str, ExtendedEnum):
    """
    An enumeration representing the different grouping modes for grouped items.
    """

    LENGTHWISE = "lengthwise"


class ItemSelectStrategy(str, ExtendedEnum):
    LARGEST_VOLUME = "largest_volume"
    LARGEST_H_W_L = "largest_h_w_l"
    LARGEST_W_H_L = "largest_w_h_l"
    LARGEST_L_H_W = "largest_l_h_w"
    LARGEST_L_W_H = "largest_l_w_h"

    LARGEST_W_TO_FILL = "largest_w_to_fill"
    LARGEST_W_H_TO_FILL = "largest_w_h_to_fill"


class PackerConfiguration(BaseModel):
    default_select_strategy: Optional[ItemSelectStrategy] = Field(
        description="Default strategy to select items",
        default=ItemSelectStrategy.LARGEST_L_H_W,
    )

    new_layer_select_strategy: Optional[ItemSelectStrategy] = Field(
        description="Strategy to select items when starting a new layer",
        default=ItemSelectStrategy.LARGEST_L_H_W,
    )

    direction_change_min_volume: Optional[float] = Field(
        description="Minimum volume of the item to consider changing direction",
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    bin_stability_factor: Optional[float] = Field(
        description="Stability factor of the bin", default=1.0, ge=0.0, le=1.0
    )

    allow_item_exceeds_layer: Optional[bool] = Field(
        description="Allow items to exceed the current layer height", default=False
    )

    mirror_walls: Optional[bool] = Field(
        description="Place two same items on the outher positions of a new layer",
        default=False,
    )

    padding_x: Optional[int] = Field(
        description="Padding between items along the x-axis (width)", default=0, ge=0
    )

    overhang_y_stability_factor: Optional["float|None"] = Field(
        description="Fraction of the item's length that needs to lay on the bin to be considered stable",
        default=None,
        ge=0.55,
        le=1.0,
    )

    remove_gaps: Optional[bool] = Field(
        description="Remove gaps in x-direction between item stacks", default=False
    )

    item_grouping_mode: Optional["ItemGroupingMode|None"] = Field(
        description="Grouping mode for items", default=None
    )

    def __hash__(self):
        return hash(
            (
                self.default_select_strategy,
                self.new_layer_select_strategy,
                self.direction_change_min_volume,
                self.bin_stability_factor,
                self.allow_item_exceeds_layer,
                self.mirror_walls,
                self.padding_x,
                self.overhang_y_stability_factor,
                self.remove_gaps,
            )
        )
