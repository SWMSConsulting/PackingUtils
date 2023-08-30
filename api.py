# filename: main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.solver.palletier_packer import PalletierPacker
from packutils.solver.py3dbp_packer import Py3dbpPacker
from packutils.solver.abstract_packer import AbstractPacker

app = FastAPI()


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


@app.get("/")
async def status():
    return {"status": "Healthy"}


@app.post("/palletier")
async def get_packing_palletier(orderModel: OrderModel):

    return _get_packing(PackerClass=PalletierPacker, orderModel=orderModel)

"""
@app.post("/py3dbp")
async def get_packing_py3dbp(orderModel: OrderModel):

    return _get_packing(PackerClass=Py3dbpPacker, orderModel=orderModel)
"""


def _get_packing(PackerClass: AbstractPacker, orderModel: OrderModel):

    if orderModel.colli_details is not None:
        details = orderModel.colli_details
        bins = [
            Bin(details.width, details.length,
                details.height, details.max_weight)
            for _ in range(details.max_collis)
        ]
    else:
        bins = [Bin(800, 1, 500)]

    solver = PackerClass(bins=bins)

    order = Order(
        order_id=orderModel.order_id,
        articles=[
            Article(
                article_id=a.id,
                width=a.width,
                length=a.length,
                height=a.height,
                amount=a.amount
            ) for a in orderModel.articles
        ]
    )
    variant = solver.pack_variant(order)
    print(variant)
    packed_order = PackedOrder(order_id=order.order_id)
    if variant is not None:
        packed_order.add_packing_variant(variant)

    return packed_order.to_dict(as_string=False)
