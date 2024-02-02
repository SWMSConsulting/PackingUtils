import copy
import logging
from packutils.data.single_item import SingleItem
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.data.position import Position
from packutils.solver.abstract_packer import AbstractPacker

try:
    import greedypacker
    import sys

    PACKER_AVAILABLE = sys.version.startswith("3.8")
except ImportError as e:
    PACKER_AVAILABLE = False


class GreedyPacker(AbstractPacker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if (
            len(
                set(
                    map(
                        lambda x: tuple([x.width, x.length, x.height, x.max_weight]),
                        self.reference_bins,
                    )
                )
            )
            != 1
        ):
            raise ValueError("GreedyPacker can only handle one type of reference bin.")

        reference_bin = self.reference_bins[0]
        is_2d, dims = reference_bin.is_packing_2d()
        if not is_2d:
            raise ValueError("GreedyPacker can only handle 2D packings.")
        if dims != ["width", "length"]:
            raise ValueError(
                "GreedyPacker does not fullfil stability condition required for handling height dimension."
            )
        self.max_bins = len(self.reference_bins)

        self.dimensions = dims
        self.bin_algo = kwargs.get("bin_algo", "bin_best_fit")
        self.pack_algo = kwargs.get("pack_algo", "maximal_rectangle")
        self.heuristic = kwargs.get("heuristic", "default")
        self.split_heuristic = kwargs.get("split_heuristic", "default")
        self.rotation = kwargs.get("rotation", False)
        self.wastemap = kwargs.get("wastemap", True)
        self.rectangle_merge = kwargs.get("rectangle_merge", True)
        self.sorting = kwargs.get("sorting", False)

        if self.pack_algo == "shelf":
            supported_heuristics = [
                "next_fit",
                "first_fit",
                "best_width_fit",
                "best_height_fit",
                "best_area_fit",
                "worst_width_fit",
                "worst_height_fit",
                "worst_area_fit",
            ]
        elif self.pack_algo == "guillotine":
            supported_heuristics = [
                "best_shortside",
                "best_longside",
                "best_area",
                "worst_shortside",
                "worst_longside",
                "worst_area",
            ]
        elif self.pack_algo == "maximal_rectangle":
            supported_heuristics = [
                "best_shortside",
                "best_longside",
                "best_area",
                "worst_shortside",
                "worst_longside",
                "worst_area",
                "bottom_left",
                "contact_point",
            ]
        elif self.pack_algo == "skyline":
            supported_heuristics = ["bottom_left", "best_fit"]
        else:
            raise ValueError(f"Unsupported pack_algo: {self.pack_algo}")

        if self.heuristic == "default":
            self.heuristic = supported_heuristics[0]
        assert (
            self.heuristic in supported_heuristics
        ), f"Heuristic not supported: {self.heuristic} (expected one of {supported_heuristics})"

        logging.info(f"\nUsing GreedyPacker with:")
        params = self.get_params()
        for key in params.keys():
            logging.info(f"  {key} = {params[key]}")

        if self.dimensions == ["width", "length"]:
            self.bin_dim = (reference_bin.width, reference_bin.length)
        """
        elif self.dimensions == ["width", "height"]:
            self.bin_dim = (reference_bin.width, reference_bin.height)
        elif self.dimensions == ["length", "height"]:
            self.bin_dim = (reference_bin.length, reference_bin.height)
        """

    def get_params(self) -> dict:
        return {
            "bin_algo": self.bin_algo,
            "pack_algo": self.pack_algo,
            "heuristic": self.heuristic,
            "split_heuristic": self.split_heuristic,
            "rotation": self.rotation,
            "wastemap": self.wastemap,
            "rectangle_merge": self.rectangle_merge,
            "sorting": self.sorting,
        }

    def pack_variant(self, order: Order) -> "PackingVariant | None":
        if not self.is_packer_available():
            raise ImportError(
                "GreedyPacker requires Python 3.8 and greedypacker to be installed (pip install greedypacker)"
            )

        packer = greedypacker.BinManager(
            self.bin_dim[0],
            self.bin_dim[1],
            bin_algo=self.bin_algo,
            pack_algo=self.pack_algo,
            heuristic=self.heuristic,
            split_heuristic=self.split_heuristic,
            rotation=self.rotation,
            rectangle_merge=self.rectangle_merge,
            wastemap=self.wastemap,
            sorting=self.sorting,
        )

        greedy_items = []
        for article in order.articles:
            for _ in range(article.amount):
                w, l, h = article.width, article.length, article.height
                if self.dimensions == ["width", "length"]:
                    greedy_items.append(greedypacker.Item(w, l))
                """
                elif self.dimensions == ["width", "height"]:
                    greedy_items.append(greedypacker.Item(w, h))
                elif self.dimensions == ["length", "height"]:
                    greedy_items.append(greedypacker.Item(l, h))
                """
        packer.add_items(*greedy_items)
        packer.execute()

        variant = PackingVariant()
        for idx, b in enumerate(packer.bins):
            bin = copy.deepcopy(self.reference_bins[idx % len(self.reference_bins)])

            bin_items = []
            if self.pack_algo == "shelf":
                for s in b.shelves:
                    for i in s.items:
                        bin_items.append(i)
            else:
                bin_items = b.items

            for i in bin_items:
                if self.dimensions == ["width", "length"]:
                    w, l, h = i.width, i.height, 1
                    pos = Position(x=i.x, y=i.y, z=0)
                elif self.dimensions == ["width", "height"]:
                    w, l, h = i.width, 1, i.height
                    pos = Position(x=i.x, y=0, z=i.y)
                elif self.dimensions == ["length", "height"]:
                    w, l, h = 1, i.width, i.height
                    pos = Position(x=0, y=i.x, z=i.y)

                item = SingleItem(
                    identifier=f"Item {w, l, h, 0.0}",
                    width=w,
                    length=l,
                    height=h,
                    weight=0.0,
                )
                is_packed, error_msg = bin.pack_item(
                    item=item,
                    position=pos,
                )
                if not is_packed:
                    variant.add_unpacked_item(item, error_msg)

            variant.add_bin(bin)
            if len(variant.bins) == self.max_bins:
                return variant

        return variant

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE
