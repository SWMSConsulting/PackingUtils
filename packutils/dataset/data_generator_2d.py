import datetime
import json
import os
import random
from typing import List
from packutils.data.article import Article
from packutils.data.bin import Bin

from packutils.data.order import Order
from packutils.solver.greedy_packer import GreedyPacker


class DataGenerator2d:
    def __init__(
        self,
        num_data: int,
        output_path: str,
        reference_bins: List[Bin],
        articles: List[Article],
        packing_solver: str = "greedy",
        **kwargs
    ):
        self.allow_rotation = False
        is_2D, self.dimensions = reference_bins[0].is_packing_2d()
        self.dimensionality = "2D"
        self.num_data = num_data

        assert is_2D == True, "DataGenerator2d can only handle 2D data"

        assert os.path.exists(output_path), "output_path not exists"
        self.output_path = output_path

        assert len(reference_bins) > 0 and isinstance(reference_bins[0], Bin), \
            "requires at least one reference Bin"
        self.reference_bins = reference_bins

        assert len(articles) > 0 and isinstance(articles[0], Article), \
            "requires at least one article"
        self.articles = articles

        self.packing_solver = packing_solver
        if packing_solver == "greedy":
            self.solver = GreedyPacker(
                bins=reference_bins, rotation=self.allow_rotation, **kwargs)
        else:
            raise ValueError(f"Solver not supported: {packing_solver}")
        self.date = datetime.datetime.now()
        date_str = self.date.strftime("%Y%m%d")
        dataset_name = f"data_{self.dimensionality}_{num_data}_{date_str}"
        self.dataset_dir = os.path.join(self.output_path, dataset_name)

        if os.path.exists(self.dataset_dir):
            raise ValueError(f"dataset already exists: {self.dataset_dir}")

        os.makedirs(self.dataset_dir, exist_ok=True)

    def generate_data(self):
        self.write_info()

        orders = []
        packed_orders = []

        while len(packed_orders) < self.num_data:
            # generate random order
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
            order = Order(f"order", articles=articles)
            if orders.count(order) > 0:
                continue

            packed = self.solver.pack_order(order)
            if len(packed.packing_variants[0].bins[0].packed_items) < 1:
                continue

            f_path = os.path.join(
                self.dataset_dir, f"order{len(packed_orders)+1}.json")
            packed.write_to_file(f_path)

            orders.append(order)
            packed_orders.append(packed)

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
