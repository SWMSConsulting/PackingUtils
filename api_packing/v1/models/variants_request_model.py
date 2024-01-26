from pydantic import BaseModel
from typing import List, Optional

from packutils.data.packer_configuration import PackerConfiguration


class ArticleModel(BaseModel):
    id: str
    width: int
    length: int
    height: int
    amount: int


class ColliDetailsModel(BaseModel):
    width: int
    length: int
    height: int
    max_collis: int
    max_weight: Optional[int] = None


class OrderModel(BaseModel):
    order_id: str
    articles: List[ArticleModel]
    colli_details: Optional[ColliDetailsModel] = None
    # supplies: List[Supply] = []


class VariantsRequestModel(BaseModel):
    order: OrderModel
    num_variants: Optional[int]
    config: Optional[PackerConfiguration]
