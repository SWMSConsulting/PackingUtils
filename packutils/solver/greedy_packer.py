import copy
from packutils.data.bin import Bin
from packutils.data.item import Item
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

        if len(self.reference_bins) != 1:
            raise ValueError("GreedyPacker can only handle one reference bin.")

        reference_bin = self.reference_bins[0]
        is_2d, dims = reference_bin.is_packing_2d()
        if not is_2d or (
            dims.count("width") + dims.count("length") +
            dims.count("height") != 2
        ):
            raise ValueError("GreedyPacker can only handle 2D packings.")

        self.dimensions = dims
        self.rotation = kwargs.get("rotation", False)
        self.wastemap = kwargs.get("wastemap", True)
        self.heuristic = kwargs.get("heuristic", "best_width_fit")
        self.pack_algo = kwargs.get("pack_algo", "shelf")

        if self.dimensions == ["width", "length"]:
            self.bin_dim = (reference_bin.width, reference_bin.length)
        elif self.dimensions == ["width", "height"]:
            self.bin_dim = (reference_bin.width, reference_bin.height)
        elif self.dimensions == ["length", "height"]:
            self.bin_dim = (reference_bin.length, reference_bin.height)

    def pack_variant(self, order: Order) -> 'PackingVariant | None':
        if not self.is_packer_available():
            raise ImportError(
                "GreedyPacker requires Python 3.8 and greedypacker to be installed (pip install greedypacker)")

        packer = greedypacker.BinManager(
            self.bin_dim[0],
            self.bin_dim[1],
            pack_algo=self.pack_algo,
            heuristic=self.heuristic,
            wastemap=self.wastemap,
            rotation=self.rotation
        )

        greedy_items = []
        for article in order.articles:
            for _ in range(article.amount):
                w, l, h = article.width, article.length, article.height
                if self.dimensions == ["width", "length"]:
                    greedy_items.append(greedypacker.Item(w, l))
                elif self.dimensions == ["width", "height"]:
                    greedy_items.append(greedypacker.Item(w, h))
                elif self.dimensions == ["length", "height"]:
                    greedy_items.append(greedypacker.Item(l, h))

        packer.add_items(*greedy_items)
        packer.execute()

        variant = PackingVariant()
        for b in packer.bins:
            bin = copy.deepcopy(self.reference_bins[0])

            for s in b.shelves:
                for i in s.items:
                    if self.dimensions == ["width", "length"]:
                        w, l, h = i.width, i.height, 1
                    elif self.dimensions == ["width", "height"]:
                        w, l, h = i.width, 1, i.height
                    elif self.dimensions == ["length", "height"]:
                        w, l, h = 1, i.width, i.height

                    if self.dimensions == ["width", "length"]:
                        pos = Position(x=i.x, y=i.y, z=0)
                    elif self.dimensions == ["width", "height"]:
                        pos = Position(x=i.x, y=i.y, z=0)
                    elif self.dimensions == ["length", "height"]:
                        pos = Position(x=i.x, y=i.y, z=0)

                    item = Item(
                        id=f"Item {len(bin.packed_items)}",
                        width=w,
                        length=l,
                        height=h,
                        position=pos
                    )
                    bin.pack_item(item)

            variant.add_bin(bin)
        return variant

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE
