# filename: main.py

import copy
import random
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration
from packutils.solver.palletier_wish_packer import PalletierWishPacker

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


class VariantsRequestModel(BaseModel):
    order: OrderModel
    num_variants: int
    config: PackerConfiguration


@app.get("/")
async def status():
    return {"status": "Healthy"}


@app.post("/variants")
async def get_packing_variants(
    body: VariantsRequestModel
):
    print("PARAMS", body)
    order = Order(
        order_id=body.order.order_id,
        articles=[
            Article(article_id=a.id, width=a.width, length=a.length,
                    height=a.height, amount=a.amount)
            for a in body.order.articles
        ])
    num_variants = body.num_variants
    config = None

    bin_volume = body.order.colli_details.width * \
        body.order.colli_details.length * body.order.colli_details.height
    item_volumes = [a.width * a.length * a.height /
                    bin_volume for a in order.articles]

    config = PackerConfiguration() if config is None else config
    configs = [config]

    random_configs = PackerConfiguration.generate_random_configurations(
        n=num_variants,
        bin_stability_factor=config.bin_stability_factor,
        item_volumes=item_volumes,
    )

    for cfg in random_configs:
        if cfg not in configs:
            configs.append(cfg)
        if len(configs) >= num_variants:
            break

    if body.order.colli_details is not None:
        details = body.order.colli_details
        bins = [
            Bin(details.width, details.length,
                details.height, details.max_weight)
            for _ in range(details.max_collis)
        ]
    else:
        bins = [Bin(800, 1, 500)]

    packer = PalletierWishPacker(bins=bins)
    variants = packer.pack_variants(order, configs)

    packed = PackedOrder(order.order_id)
    for v in variants:
        packed.add_packing_variant(v)

    return {
        "packed_order": packed.to_dict(as_string=False),
        "configs": configs
    }

"""
@app.post("/palletier")
async def get_packing_palletier(orderModel: OrderModel):

    return _get_packing(PackerClass=PalletierPacker, orderModel=orderModel)

@app.post("/py3dbp")
async def get_packing_py3dbp(orderModel: OrderModel):

    return _get_packing(PackerClass=Py3dbpPacker, orderModel=orderModel)


def _get_packing(
    PackerClass: AbstractPacker,
    orderModel: OrderModel,
    configution: PackerConfiguration = None
):

    if orderModel.colli_details is not None:
        details = orderModel.colli_details
        bins = [
            Bin(details.width, details.length,
                details.height, details.max_weight)
            for _ in range(details.max_collis)
        ]
    else:
        bins = [Bin(800, 1, 500)]

    solver = PackerClass(bins=bins, configution=configution)

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
    # print(variant)
    packed_order = PackedOrder(order_id=order.order_id)
    if variant is not None:
        packed_order.add_packing_variant(variant)

    return packed_order.to_dict(as_string=False)

"""
