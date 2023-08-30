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
    max_weight: Optional[int] = None


class OrderModel(BaseModel):
    order_id: str
    articles: List[ArticleModel]
    colli_details: Optional[ColliDetailsModel] = None
    # supplies: List[Supply] = []


@app.get("/")
async def status():
    return {"status": "Healthy"}


def get_packing(SolverClass, orderModel):

    if orderModel.colli_details is not None:
        details = orderModel.colli_details
        bin = Bin(details.width, details.length,
                  details.height, details.max_weight)
    else:
        bin = Bin(800, 1, 500)
        
    solver = SolverClass(bins=[bin])

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

    packed_order = PackedOrder(order_id=order.order_id)
    if variant is not None:
        packed_order.add_packing_variant(variant)

    return packed_order.to_dict(as_string=False)

@app.post("/palletier")
async def get_packing_palletier(orderModel: OrderModel):

    return get_packing(SolverClass=PalletierPacker, orderModel=orderModel)

@app.post("/py3dbp")
async def get_packing_py3dbp(orderModel: OrderModel):

    return get_packing(SolverClass=Py3dbpPacker, orderModel=orderModel)