import itertools
import json
import os
import random
from typing import List, Tuple
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from v1.models.variants_request_model import VariantsRequestModel

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.data.packer_configuration import ItemSelectStrategy, PackerConfiguration
from packutils.eval.packing_evaluation import (
    PackingEvaluation,
    PackingEvaluationWeights,
)
from packutils.solver.palletier_wish_packer import PalletierWishPacker


def get_possible_config_params(
    change_volumes: "List[float] | None" = None,
) -> Tuple[List[PackerConfiguration], int]:
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(dotenv_path):
        from dotenv import load_dotenv

        print("Loading .env file")
        load_dotenv(dotenv_path)

    env_default_select_strategy = os.environ.get("DEFAULT_SELECT_STRATEGY", None)
    if env_default_select_strategy is None:
        possible_default_select_strategy = ItemSelectStrategy.list()
    else:
        if env_default_select_strategy.startswith("["):
            possible_default_select_strategy = [
                ItemSelectStrategy(s) for s in json.loads(env_default_select_strategy)
            ]
        else:
            possible_default_select_strategy = [
                ItemSelectStrategy(env_default_select_strategy)
            ]

    env_new_layer_select_strategy = os.environ.get("NEW_LAYER_SELECT_STRATEGY", None)
    if env_new_layer_select_strategy is None:
        possible_new_layer_select_strategy = ItemSelectStrategy.list()
    else:
        if env_new_layer_select_strategy.startswith("["):
            possible_new_layer_select_strategy = [
                ItemSelectStrategy(s) for s in json.loads(env_new_layer_select_strategy)
            ]
        else:
            possible_new_layer_select_strategy = [
                ItemSelectStrategy(env_new_layer_select_strategy)
            ]

    env_bin_stability_factor = os.environ.get("BIN_STABILITY_FACTOR", None)
    if env_bin_stability_factor is None:
        possible_bin_stability_factor = [1.0]
    else:
        if env_bin_stability_factor.startswith("["):
            possible_bin_stability_factor = [
                float(f) for f in json.loads(env_bin_stability_factor)
            ]
        else:
            possible_bin_stability_factor = [float(env_bin_stability_factor)]

    env_allow_item_exceeds_layer = os.environ.get("ALLOW_ITEM_EXCEEDS_LAYER", None)
    if env_allow_item_exceeds_layer is None:
        possible_allow_item_exceeds_layer = [True, False]
    else:
        if env_allow_item_exceeds_layer.startswith("["):
            possible_allow_item_exceeds_layer = [
                bool(b) for b in json.loads(env_allow_item_exceeds_layer)
            ]
        else:
            possible_allow_item_exceeds_layer = [bool(env_allow_item_exceeds_layer)]

    env_mirror_walls = os.environ.get("MIRROR_WALLS", None)
    if env_mirror_walls is None:
        possible_mirror_walls = [True, False]
    else:
        if env_mirror_walls.startswith("["):
            possible_mirror_walls = [bool(b) for b in json.loads(env_mirror_walls)]
        else:
            possible_mirror_walls = [bool(env_mirror_walls)]

    env_direction_change_volumes = os.environ.get("DIRECTION_CHANGE_VOLUMES", None)
    possible_direction_change_volume = (
        None
        if env_direction_change_volumes is None
        else (
            [float(f) for f in json.loads(env_direction_change_volumes)]
            if env_direction_change_volumes.startswith("[")
            else [float(env_direction_change_volumes)]
        )
    )
    env_num_variants = os.environ.get("NUM_VARIANTS", None)
    env_num_variants = int(env_num_variants) if env_num_variants is not None else None

    if change_volumes is None:
        change_volumes = possible_direction_change_volume or [1.0]

    params = [
        possible_default_select_strategy,
        possible_new_layer_select_strategy,
        change_volumes,
        possible_bin_stability_factor,
        possible_allow_item_exceeds_layer,
        possible_mirror_walls
        # add here other possible parameter
    ]
    combinations = list(itertools.product(*params))

    possible_params = {
        "default_select_strategy": possible_default_select_strategy,
        "new_layer_select_strategy": possible_new_layer_select_strategy,
        "direction_change_volume": possible_direction_change_volume,
        "bin_stability_factor": possible_bin_stability_factor,
        "allow_item_exceeds_layer": possible_allow_item_exceeds_layer,
        "mirror_walls": possible_mirror_walls,
        "num_variants": env_num_variants,
        "num_combinations": len(combinations),
    }
    print("Possible variables:")
    for k, v in possible_params.items():
        print(f"{k :<50}: {v}")
    print("")

    return [
        PackerConfiguration(
            default_select_strategy=combination[0],
            new_layer_select_strategy=combination[1],
            direction_change_min_volume=combination[2],
            bin_stability_factor=combination[3],
            allow_item_exceeds_layer=combination[4],
            mirror_walls=combination[5],
        )
        for combination in combinations
    ], env_num_variants


ENV_CONFIGS, ENV_NUM_VARIANTS = get_possible_config_params(None)

api_v1 = FastAPI()


@api_v1.get("/")
async def status():
    return {"status": "Healthy"}


@api_v1.post("/variants")
async def get_packing_variants(body: VariantsRequestModel):
    """Get packing variants for an order."""

    if body.order.colli_details is not None:
        details = body.order.colli_details
        bins = [
            Bin(details.width, 1, details.height, details.max_weight)  # details.length,
            for _ in range(details.max_collis)
        ]
    else:
        bins = [Bin(800, 1, 500)]

    bin_w = bins[0].width
    bin_h = bins[0].height
    bin_l = bins[0].length
    bin_volume = bins[0].volume

    order = Order(
        order_id=body.order.order_id,
        articles=[
            Article(
                article_id=a.id,
                width=a.width,
                length=a.length if a.length <= bin_l else bin_l,
                height=a.height,
                amount=a.amount,
            )
            for a in body.order.articles
        ],
    )
    # check if articles are valid
    for i, article in enumerate(order.articles):
        if article.width > bin_w or article.length > bin_l or article.height > bin_h:
            print("Article too large for bin")
            return JSONResponse(
                content={
                    "detail": [
                        {
                            "loc": ["body", "order", i, "articles"],
                            "msg": f"Article ({article}) too large for bin {bin_w, bin_l, bin_h}",
                            "type": "custom_error",
                        }
                    ]
                },
                status_code=422,
            )

    num_variants = ENV_NUM_VARIANTS if body.num_variants is None else body.num_variants

    if body.config is not None and body.config.direction_change_min_volume is None:
        change_volumes = [
            a.width * a.length * a.height / bin_volume for a in order.articles
        ]
        possible_configs = get_possible_config_params(change_volumes)
    else:
        possible_configs = ENV_CONFIGS

    if num_variants is None or len(possible_configs) <= num_variants:
        configs = possible_configs
    else:
        configs = [body.config] if body.config is not None else []
        configs += random.sample(possible_configs, num_variants - len(configs))

    packer = PalletierWishPacker(bins=bins)
    variants = packer.pack_variants(order, configs)

    eval = PackingEvaluation(
        PackingEvaluationWeights(
            item_distribution=1.0,
            item_stacking=1.0,
            item_grouping=1.0,
            utilized_space=3.0,
        )
    )
    scored_variants = eval.evaluate_packing_variants(variants, configs)

    sorted_variants = sorted(scored_variants, key=lambda x: x[0], reverse=True)

    variants = [variant for _, (variant, _) in sorted_variants]
    # multiple configurations may lead to same variant
    configs = [config for _, (_, config) in sorted_variants]

    packed = PackedOrder(order.order_id)
    for v in variants:
        packed.add_packing_variant(v)

    return {"packed_order": packed.to_dict(as_string=False), "configs": configs}


@api_v1.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + api_v1.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )
