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
from packutils.solver.palletier_packer import PalletierPacker
from packutils.solver.palletier_wish_packer import PalletierWishPacker
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


class VariantsRequestModel(BaseModel):
    order: OrderModel
    num_variants: int
    config: PackerConfiguration


@app.get("/")
async def status():
    return {"status": "Healthy"}


@app.post("/variants")
async def get_packing_palletier(
    params: VariantsRequestModel
):
    print(params)
    order_model = params.order
    num_variants = params.num_variants
    config = None
    # generate configurations
    if config is None:
        config = PackerConfiguration()
    configs = _generate_random_configurations(
        order_model, config, num_variants)
    print(configs)
    variants = []
    for cfg in configs:
        variants.append(_get_packing(PalletierWishPacker, order_model, cfg))

    return variants


def _generate_random_configurations(
        order: OrderModel,
        config: PackerConfiguration,
        num_variants: int
):
    configs = [config]
    failed_counter = 0
    while len(configs) < num_variants or failed_counter > 5:
        new_config = copy.copy(config)

        bin_volume = order.colli_details.width * \
            order.colli_details.length * order.colli_details.height
        possibilities = [a.width * a.length *
                         a.height / bin_volume for a in order.articles]
        possibilities += [0.0, 1.0]
        new_value = random.choice(possibilities)
        new_config.direction_change_min_volume = new_value

        possibilities = ItemSelectStrategy.all_entities()
        new_value = random.choice(possibilities)
        new_config.item_select_strategy = possibilities

        if configs.count(new_config) > 0:
            failed_counter += 1
        else:
            failed_counter = 0
            configs.append(new_config)

    print(configs)
    return configs


"""
@app.post("/palletier")
async def get_packing_palletier(orderModel: OrderModel):

    return _get_packing(PackerClass=PalletierPacker, orderModel=orderModel)

@app.post("/py3dbp")
async def get_packing_py3dbp(orderModel: OrderModel):

    return _get_packing(PackerClass=Py3dbpPacker, orderModel=orderModel)
"""


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
