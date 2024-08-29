import itertools
import json
import os
import random
from typing import List, Tuple
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from v1.models.variants_request_model import (
    VariantsRequestModel,
    validate_requested_order,
)

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.data.packer_configuration import (
    ItemGroupingMode,
    ItemSelectStrategy,
    PackerConfiguration,
)
from packutils.eval.packing_evaluation import (
    PackingEvaluation,
    PackingEvaluationWeights,
)
from packutils.solver.palletier_wish_packer import PalletierWishPacker


def to_bool(value: str) -> bool:
    print(value)
    return value.lower() in ("yes", "true", "t", "1")


def get_possible_config_params(
    change_volumes: "List[float] | None" = None,
) -> Tuple[List[PackerConfiguration], int]:
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(dotenv_path):
        from dotenv import load_dotenv

        print("Loading .env file")
        load_dotenv(dotenv_path)

    # fixed parameters
    bin_stability_factor = float(os.environ.get("BIN_STABILITY_FACTOR", 1.0))

    overhang_y_stability_factor = float(
        os.environ.get("OVERHANG_Y_STABILITY_FACTOR", 1.0)
    )

    padding_between_items = int(os.environ.get("PADDING_BETWEEN_ITEMS", 0))

    env_num_variants = os.environ.get("NUM_VARIANTS", None)

    # variable parameters
    env_default_select_strategy = os.environ.get("DEFAULT_SELECT_STRATEGY", None)
    if env_default_select_strategy is None:
        possible_default_select_strategy = ItemSelectStrategy.list()
    else:
        if env_default_select_strategy.startswith("["):
            possible_default_select_strategy = [
                ItemSelectStrategy(s)
                for s in json.loads(env_default_select_strategy.replace("'", '"'))
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
                ItemSelectStrategy(s)
                for s in json.loads(env_new_layer_select_strategy.replace("'", '"'))
            ]
        else:
            possible_new_layer_select_strategy = [
                ItemSelectStrategy(env_new_layer_select_strategy)
            ]

    env_allow_item_exceeds_layer = os.environ.get("ALLOW_ITEM_EXCEEDS_LAYER", None)
    if env_allow_item_exceeds_layer is None:
        possible_allow_item_exceeds_layer = [True, False]
    else:
        if env_allow_item_exceeds_layer.startswith("["):
            possible_allow_item_exceeds_layer = [
                to_bool(b) for b in json.loads(env_allow_item_exceeds_layer)
            ]
        else:
            possible_allow_item_exceeds_layer = [to_bool(env_allow_item_exceeds_layer)]

    env_mirror_walls = os.environ.get("MIRROR_WALLS", None)
    if env_mirror_walls is None:
        possible_mirror_walls = [True, False]
    else:
        if env_mirror_walls.startswith("["):
            possible_mirror_walls = [to_bool(b) for b in json.loads(env_mirror_walls)]
        else:
            possible_mirror_walls = [to_bool(env_mirror_walls)]

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

    env_item_grouping_mode = os.environ.get("ITEM_GROUPING_MODE", None)
    if env_item_grouping_mode is None:
        possible_item_grouping_mode = [None]
    else:
        if env_item_grouping_mode.startswith("["):
            possible_item_grouping_mode = [
                ItemGroupingMode(s) for s in json.loads(env_item_grouping_mode)
            ]
        else:
            possible_item_grouping_mode = [ItemGroupingMode(env_item_grouping_mode)]

    env_group_narrow_items_w = os.environ.get("GROUP_NARROW_ITEMS_W", None)
    if env_group_narrow_items_w is None:
        possible_group_narrow_items_w = [0]
    else:
        if env_group_narrow_items_w.startswith("["):
            possible_group_narrow_items_w = [
                int(f) for f in json.loads(env_group_narrow_items_w)
            ]
        else:
            possible_group_narrow_items_w = [int(env_group_narrow_items_w)]

    if change_volumes is None:
        change_volumes = possible_direction_change_volume or [1.0]

    params = [
        possible_default_select_strategy,
        possible_new_layer_select_strategy,
        change_volumes,
        possible_allow_item_exceeds_layer,
        possible_mirror_walls,
        possible_item_grouping_mode,
        possible_group_narrow_items_w,
        # add here other possible parameter
    ]
    combinations = list(itertools.product(*params))
    num_variants = (
        len(combinations) if env_num_variants is None else int(env_num_variants)
    )

    fixed_params = {
        "bin_stability_factor": bin_stability_factor,
        "overhang_y_stability_factor": overhang_y_stability_factor,
        "padding_between_items": padding_between_items,
        "num_variants": num_variants,
        "num_combinations": len(combinations),
    }
    print("Fixed parameters:")
    for k, v in fixed_params.items():
        print(f"{k :<50}: {v}")
    print("")

    changable_params = {
        "default_select_strategy": possible_default_select_strategy,
        "new_layer_select_strategy": possible_new_layer_select_strategy,
        "direction_change_volume": possible_direction_change_volume,
        "allow_item_exceeds_layer": possible_allow_item_exceeds_layer,
        "mirror_walls": possible_mirror_walls,
        "item_grouping_mode": possible_item_grouping_mode,
        "group_narrow_items_w": possible_group_narrow_items_w,
    }
    print("Variable parameters:")
    for k, v in changable_params.items():
        print(f"{k :<50}: {v}")
    print("")

    return [
        PackerConfiguration(
            bin_stability_factor=bin_stability_factor,
            overhang_y_stability_factor=overhang_y_stability_factor,
            padding_between_items=padding_between_items,
            # variable parameters
            default_select_strategy=combination[0],
            new_layer_select_strategy=combination[1],
            direction_change_min_volume=combination[2],
            allow_item_exceeds_layer=combination[3],
            mirror_walls=combination[4],
            item_grouping_mode=combination[5],
            group_narrow_items_w=combination[6],
        )
        for combination in combinations
    ], num_variants


ENV_CONFIGS, ENV_NUM_VARIANTS = get_possible_config_params(None)

ALLOW_OVERHANG_Y = True

api_v1 = FastAPI()


@api_v1.get("/")
def status():
    return {"status": "Healthy"}


@api_v1.post("/variants")
def get_packing_variants(body: VariantsRequestModel):
    """Get packing variants for an order."""

    details = body.order.colli_details
    bins = [
        Bin(
            details.width,
            details.length,
            details.height,
            details.max_length,
            details.max_weight,
        )
        for _ in range(details.max_collis)
    ]

    bin_volume = min([b.volume for b in bins])

    error_msg = validate_requested_order(
        body.order, details.width, details.max_length, details.height
    )
    if error_msg is not None:
        return JSONResponse(
            content={
                "detail": [
                    {
                        "loc": ["body", "order", "articles"],
                        "msg": error_msg,
                        "type": "custom_error",
                    }
                ]
            },
            status_code=422,
        )

    order = Order(
        order_id=body.order.order_id,
        articles=[
            Article(
                article_id=a.id,
                width=a.width,
                length=a.length,
                height=a.height,
                weight=a.weight,
                amount=a.amount,
            )
            for a in body.order.articles
        ],
    )
    print(order)
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
        configs += list(random.sample(possible_configs, num_variants - len(configs)))

    packer = PalletierWishPacker(
        bins=bins,
        safety_distance_smaller_articles=details.safety_distance_smaller_articles,
        min_article_width_no_safety_distance=details.min_article_width_no_safety_distance,
        safety_distance_lengthwise=details.safety_distance_lengthwise,
    )

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
