# filename: main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.bin import Bin
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
    print(variant)

    positions = [
        {
            'article_id': pack.id,
            'x': pack.position.x, 'y': pack.position.y, 'z': pack.position.z,
            'rotation': pack.position.rotation,
            'centerpoint_x': pack.centerpoint().x,
            'centerpoint_y': pack.centerpoint().y,
            'centerpoint_z': pack.centerpoint().z
        }
        for pack in variant.bins[0].packed_items
    ] if len(variant.bins) > 0 else []
    colli = {'colli': 1, 'colli_total': 1,
             'colli_dimension': {
                 "width": bin.width,
                 "length": bin.length,
                 "height": bin.height
             },
             'positions': positions}

    packed = {
        "order_id": order.order_id,
        "packing_variants": [[colli]],
        "articles": orderModel.articles,
    }

    return packed
