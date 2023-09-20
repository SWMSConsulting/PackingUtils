from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.eval.packing_evaluation import PackingEvaluation, PackingEvaluationWeights
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
            Article(article_id=a.id, width=a.width, length=1,  # a.length,
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
            Bin(details.width, 1,  # details.length,
                details.height, details.max_weight)
            for _ in range(details.max_collis)
        ]
    else:
        bins = [Bin(800, 1, 500)]

    packer = PalletierWishPacker(bins=bins)
    variants = packer.pack_variants(order, configs)

    eval = PackingEvaluation(
        PackingEvaluationWeights(
            item_distribution=1.0,
            item_stacking=1.0,
            item_grouping=1.0,
            utilized_space=3.0
        )
    )
    scored_variants = eval.evaluate_packing_variants(variants, configs)

    sorted_variants = sorted(
        scored_variants, key=lambda x: x[0], reverse=True)

    variants = [variant for _, (variant, _) in sorted_variants]
    # multiple configurations may lead to same variant
    configs = [config for _, (_, config) in sorted_variants]

    packed = PackedOrder(order.order_id)
    for v in variants:
        packed.add_packing_variant(v)

    return {
        "packed_order": packed.to_dict(as_string=False),
        "configs": configs
    }
