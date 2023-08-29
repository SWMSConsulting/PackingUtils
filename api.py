# filename: main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.solver.palletier_packer import PalletierPacker

app = FastAPI()


class ArticleModel(BaseModel):
    id: str
    width: int
    length: int
    height: int
    amount: int


class OrderModel(BaseModel):
    order_id: str
    articles: List[ArticleModel]
    # supplies: List[Supply] = []


@app.get("/")
async def status():
    return {"status": "Healthy"}


@app.post("/palletier")
async def get_packing(orderModel: OrderModel):

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

    bin = Bin(800, 1, 500)
    solver = PalletierPacker(bins=[bin])
    variant = solver.pack_variant(order)

    packed_order = PackedOrder(order_id=order.order_id)
    if variant != None:
        packed_order.add_variant(variant)

    return packed_order.to_json()
