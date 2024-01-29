from pydantic import BaseModel, Field
from typing import List, Optional

from packutils.data.packer_configuration import PackerConfiguration


class ArticleModel(BaseModel):
    """Article to be packed."""

    id: str = Field(description="Article ID")
    width: int = Field(description="Article width", gt=0)
    length: int = Field(description="Article length", gt=0)
    height: int = Field(description="Article height", gt=0)
    weight: Optional[int] = Field(description="Article weight", ge=0, default=0)
    amount: int = Field(description="Amount of articles", gt=0)


class ColliDetailsModel(BaseModel):
    """Details of the bins to be packed."""

    width: int = Field(description="Width of the bins to be packed", gt=0)
    length: int = Field(description="Length of the bins to be packed", gt=0)
    height: int = Field(description="Height of the bins to be packed", gt=0)
    max_collis: int = Field(description="Maximum number of bins to be packed", gt=0)
    max_weight: Optional[int] = Field(
        description="Maximum weight of the bins to be packed", ge=0, default=None
    )


class OrderModel(BaseModel):
    """Order to be packed."""

    order_id: str = Field(description="Order ID")
    articles: List[ArticleModel] = Field(description="Articles to be packed")
    colli_details: Optional[ColliDetailsModel] = Field(
        description="Details of the bins to be packed", default=None
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
