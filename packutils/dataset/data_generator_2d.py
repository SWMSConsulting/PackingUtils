import datetime
import json
import logging
import os
import random
from typing import List
from packutils.data.article import Article
from packutils.data.bin import Bin

from packutils.data.order import Order
from packutils.solver.greedy_packer import GreedyPacker
from packutils.solver.palletier_wish_packer import PalletierWishPacker
from packutils.solver.py3dbp_packer import Py3dbpPacker


class DataGenerator2d:
    def __init__(
        self,
        num_data: 'int | None',
        output_path: str,
        reference_bins: List[Bin],
        articles: List[Article],
        max_articles_per_order: int = None,
        packing_solver: str = "greedy",
        equally_dist_seq_len=False,
        one_item_per_packing=False,
        **kwargs
    ):
        self.allow_rotation = False
        is_2D, self.dimensions = reference_bins[0].is_packing_2d()
        self.dimensionality = "2D"

        if num_data is None:
            if one_item_per_packing:
                num_data = len(articles)
            else:
                raise NotImplementedError()
        self.num_data = num_data
        self.one_item_per_packing = one_item_per_packing

        assert is_2D == True, "DataGenerator2d can only handle 2D data"

        assert os.path.exists(output_path), "output_path not exists"
        self.output_path = output_path

        assert len(reference_bins) > 0 and isinstance(reference_bins[0], Bin), \
            "requires at least one reference Bin"
        self.reference_bins = reference_bins

        assert len(articles) > 0 and isinstance(articles[0], Article), \
            "requires at least one article"
        self.articles = articles
        self.max_articles_per_order = max_articles_per_order

        assert not equally_dist_seq_len or (
            equally_dist_seq_len and max_articles_per_order is not None), \
            "When using equally_dist_seq_len also define max_articles_per_order."
        self.equally_dist_seq_len = equally_dist_seq_len

        self.packing_solver = packing_solver
        if packing_solver == "greedy":
            self.solver = GreedyPacker(
                bins=reference_bins, rotation=self.allow_rotation, **kwargs)
        elif packing_solver == "palletier":
            self.solver = PalletierWishPacker(
                bins=reference_bins, rotation=self.allow_rotation, **kwargs)
        elif packing_solver == "py3dbp":
            self.solver = Py3dbpPacker(
                bins=reference_bins, rotation=self.allow_rotation, **kwargs)
        else:
            raise ValueError(f"Solver not supported: {packing_solver}")
        self.date = datetime.datetime.now()
        date_str = self.date.strftime("%Y%m%d")
        dataset_name = f"data_{self.dimensionality}_{num_data}_{date_str}"
        if kwargs.get("create_dataset_dir", True):
            self.dataset_dir = os.path.join(self.output_path, dataset_name)
        else:
            self.dataset_dir = self.output_path
        self.orders_dir = os.path.join(self.dataset_dir, "orders")
        os.makedirs(self.orders_dir, exist_ok=True)

        if os.path.exists(os.path.join(self.dataset_dir, "info.json")):
            raise ValueError(f"dataset already exists: {self.dataset_dir}")

        os.makedirs(self.dataset_dir, exist_ok=True)

    def generate_data(self):
        self.write_info()

        orders = []
        packed_orders = []

        while len(packed_orders) < self.num_data:
            # generate random order
            if self.one_item_per_packing:
                articles = [self.articles[len(packed_orders)]]

            else:
                if self.equally_dist_seq_len:
                    num_articles = random.randint(
                        1, self.max_articles_per_order)
                    articles = []
                    for _ in range(num_articles):
                        random_article = random.choice(self.articles)
                        filtered = list(filter(
                            lambda indexed: indexed[1].article_id == random_article.article_id, enumerate(articles)))
                        if len(filtered) < 1:
                            random_article.amount = 1
                            articles.append(random_article)
                        else:
                            articles[filtered[0][0]].amount += 1

                else:
                    articles = [
                        Article(
                            article_id=a.article_id,
                            width=a.width,
                            length=a.length,
                            height=a.height,
                            weight=a.weight,
                            amount=random.randint(0, a.amount)
                        )
                        for a in self.articles
                    ]
                    num_articles = 0
                    for idx, a in enumerate(articles):
                        num_articles += a.amount
                        if self.max_articles_per_order is not None and num_articles > self.max_articles_per_order:
                            articles[idx].amount = self.max_articles_per_order - \
                                (num_articles - a.amount)
                            articles = articles[0:idx+1]
                            break

            order = Order(f"order", articles=articles)
            if orders.count(order) > 0:
                continue
            try:
                packed = self.solver.pack_order(order)
                if len(packed.packing_variants) < 1 or len(packed.packing_variants[0].bins) < 1 or len(packed.packing_variants[0].bins[0].packed_items) < 1:
                    continue
                f_path = os.path.join(
                    self.orders_dir, f"order{len(packed_orders)+1}.json")
                packed.write_to_file(f_path)
                orders.append(order)
                packed_orders.append(packed)
            except Exception as e:
                logging.warning(e.with_traceback())

            logging.info(
                f"Generated packing {len(packed_orders)} of {self.num_data}")

    def write_info(self):
        info = {
            "dimensionality": self.dimensionality,
            "dimensions": self.dimensions,
            "max_rotation_type": int(self.allow_rotation),
            "solver": {
                "name": self.packing_solver,
                "params": self.solver.get_params()
            },
            "bin": [
                {
                    "width": bin.width,
                    "length": bin.length,
                    "height": bin.height
                } for bin in self.reference_bins
            ],
            "items": [
                {
                    "name": f"Item {a.width, a.length, a.height, a.weight}",
                    "width": a.width,
                    "length": a.length,
                    "height": a.height,
                    "weight": a.weight,
                    "max_amount": a.amount

                } for a in self.articles
            ],
            "created_ts": self.date.timestamp()
        }
        with open(os.path.join(self.dataset_dir, "info.json"), "w") as f:
            json_data = json.dumps(info, indent=4)
            f.write(json_data)
