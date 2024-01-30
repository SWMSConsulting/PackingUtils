import itertools
import json
import os
import random
from typing import List, Tuple
import streamlit as st

from packutils.data.bin import Bin
from packutils.data.order import Order
from packutils.data.article import Article
from packutils.solver.palletier_wish_packer import (
    PalletierWishPacker,
    PackerConfiguration,
)
from packutils.eval.packing_evaluation import (
    PackingEvaluation,
    PackingEvaluationWeights,
)
from packutils.visual.packing_visualization import PackingVisualization
from packutils.data.packer_configuration import *

from matplotlib import pyplot as plt
import matplotlib

matplotlib.use("Agg")


@st.cache_data
def get_possible_config_params() -> Tuple[List[PackerConfiguration], int]:
    possible_default_select_strategy = [ItemSelectStrategy.LARGEST_VOLUME]
    possible_new_layer_select_strategy = [ItemSelectStrategy.LARGEST_H_W_L]

    possible_bin_stability_factor = [1.0]

    possible_allow_item_exceeds_layer = [False]
    possible_mirror_walls = [True]

    possible_direction_change_volume = [0]  # None

    padding_x = 20

    params = [
        possible_default_select_strategy,
        possible_new_layer_select_strategy,
        possible_direction_change_volume,
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
            padding_x=padding_x,
        )
        for combination in combinations
    ]


POSSIBLE_CONFIGS = get_possible_config_params()


st.write("""# Packing Visualisation""")

# logging.basicConfig(level=logging.INFO)

max_bins = 3
bins = [Bin(800, 1, 600) for _ in range(max_bins)]
packer = PalletierWishPacker(bins=bins)

with st.expander("Order", expanded=True):
    num_articles = st.number_input(
        "Number of article types", value=4, step=1, min_value=1
    )
    order = Order(
        "Test",
        articles=[
            Article(f"Article {1}", width=68, length=1, height=68, amount=21),
            Article(f"Article {2}", width=170, length=1, height=175, amount=19),
            Article(f"Article {3}", width=82, length=1, height=20, amount=19),
            Article(f"Article {4}", width=185, length=1, height=80, amount=8),
            # for idx in range(num_articles)
        ],
    )
    _c1, _c2, _c3, _c4 = st.columns(4)
    for article in order.articles:
        article.article_id = _c1.text_input(
            key=f"{article.article_id}_id",
            label="Name",
            value=article.article_id,
            disabled=True,
        )
        article.width = _c2.number_input(
            key=f"{article.article_id}_width",
            value=article.width,
            label="Width",
            min_value=10,
            max_value=500,
            step=1,
        )
        article.height = _c3.number_input(
            key=f"{article.article_id}_height",
            value=article.height,
            label="Height",
            min_value=10,
            max_value=500,
            step=1,
        )
        article.amount = _c4.number_input(
            key=f"{article.article_id}_amount",
            value=article.amount,
            label="Amount",
            step=1,
            min_value=0,
        )

    st.write(order)

    n_configs = st.number_input(
        "Amount of configurations", value=1, step=1, min_value=0
    )
    if n_configs > 0 and n_configs < len(POSSIBLE_CONFIGS):
        configurations = random.sample(POSSIBLE_CONFIGS, n_configs)
    else:
        configurations = POSSIBLE_CONFIGS
    """
    configurations = [
        PackerConfiguration(
            bin_stability_factor=1,
            default_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            new_layer_select_strategy=ItemSelectStrategy.LARGEST_VOLUME,
            direction_change_min_volume=0,
            allow_item_exceeds_layer=False,
            mirror_walls=True,
        ),
    ]
    """
    variants = packer.pack_variants(order=order, configs=configurations)

    print("Variants calculated")

vis = PackingVisualization()

if sum([a.amount for a in order.articles]) < 1:
    st.warning("No articles to pack.")
else:
    with st.expander("Scoring weights", expanded=False):
        _c1, _c2, _c3, _c4 = st.columns(4)
        item_distribution_weight = _c1.number_input(
            label="item_distribution", value=1.0
        )
        item_stacking_weight = _c2.number_input(label="item_stacking", value=1.0)
        item_grouping_weight = _c3.number_input(label="item_grouping", value=1.0)
        utilized_space_weight = _c4.number_input(label="utilized_space", value=1.0)
        weights = PackingEvaluationWeights(
            item_distribution=item_distribution_weight,
            item_stacking=item_stacking_weight,
            item_grouping=item_grouping_weight,
            utilized_space=utilized_space_weight,
        )
        st.write(weights.__dict__)

    eval = PackingEvaluation(weights)
    scored_variants = eval.evaluate_packing_variants(
        variants=variants, configs=configurations, return_scores_dict=True
    )
    scored_variants = sorted(scored_variants, key=lambda x: x[0][0], reverse=True)
    for idx, (scores, (variant, configs)) in enumerate(scored_variants):
        st.write(f"### Variant {idx+1} - Score:", scores[0])

        _c1, _c2 = st.columns(2)
        with _c1.expander("Configuration", expanded=False):
            st.write([c.__dict__ for c in configs])
        with _c2.expander("Score details", expanded=False):
            st.write(scores[1])

        for bin_idx, bin in enumerate(variant.bins):
            cols = st.columns(max_bins)
            fig = vis.visualize_bin(bin, show=False)
            cols[bin_idx].pyplot(fig)
            plt.close(fig)
