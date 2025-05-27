from pydantic import BaseModel, Field
from typing import List, Optional

from packutils.data.packer_configuration import PackerConfiguration


class ArticleModel(BaseModel):
    """Article to be packed."""

    id: str = Field(description="Article ID")
    width: int = Field(description="Article width", gt=0)
    length: int = Field(description="Article length", gt=0)
    height: int = Field(description="Article height", gt=0)
    weight: Optional[float] = Field(description="Article weight", ge=0, default=0)
    amount: int = Field(description="Amount of articles", gt=0)
    pallet_group_index: Optional[int] = Field(description="Index of the pallet group", ge=0, default=0)
    packing_sequence_priority: Optional[int] = Field(description="Priority in the packing sequence", ge=0, default=0)
    allow_rotation_around_length: Optional[bool] = Field(description="Enable the rotation around the length of the article", default=False)


class ColliDetailsModel(BaseModel):
    """Details of the bins to be packed."""

    width: int = Field(description="Width of the bins to be packed", gt=0)
    length: int = Field(description="Length of the bins to be packed", ge=0)
    height: int = Field(description="Height of the bins to be packed", gt=0)
    max_length: int = Field(description="Length of the bins to be packed", gt=0)
    max_collis: int = Field(description="Maximum number of bins to be packed", gt=0)
    max_weight: Optional[float] = Field(
        description="Maximum weight of the bins to be packed", ge=0, default=None
    )
    safety_distance_smaller_articles: Optional[int] = Field(
        description="Sicherheitsabstand kleinerer Artikel", ge=0, default=0
    )
    min_article_width_no_safety_distance: Optional[int] = Field(
        description="Mindestbreite von Artikeln ohne Sicherheitsabstand",
        ge=0,
        default=0,
    )
    safety_distance_min_height_difference: Optional[int] = Field(
        description="Minimaler Höhenunterschied ab dem Sicherheitsabstand notwendig ist",
        ge=0,
        default=0,
    )
    safety_distance_lengthwise: Optional[int] = Field(
        description="Sicherheitsabstand zwischen Artikeln (längsseitig)", ge=0, default=0
    )
    allow_grouping_lengthwise: Optional[bool] = Field(
        description="Allow grouping of articles lengthwise", default=True
    )


class OrderModel(BaseModel):
    """Order to be packed."""

    order_id: str = Field(description="Order ID")
    articles: List[ArticleModel] = Field(description="Articles to be packed")
    colli_details: ColliDetailsModel = Field(
        description="Details of the bins to be packed"
    )
    # supplies: List[Supply] = []


class VariantsRequestModel(BaseModel):
    """Request model for packing variants."""

    order: OrderModel = Field(description="Order to be packed")
    num_variants: Optional[int] = Field(
        description="Number of packing variants to be generated", gt=0, default=None
    )
    config: Optional[PackerConfiguration] = Field(
        description="Configuration for the packing algorithm", default=None
    )


def validate_requested_order(
    order: OrderModel, max_w: int, max_l: int, max_h: int
) -> Optional[str]:
    """Validate the order to be packed."""
    # check if articles are valid
    for article in order.articles:
        if article.width > max_w or article.length > max_l or article.height > max_h:
            return f"Article ({article}) too large for bin {max_w, max_l, max_h}"
