import copy
from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.data.position import Position
from packutils.solver.abstract_packer import AbstractPacker

try:
    import py3dbp
    PACKER_AVAILABLE = True
except ImportError as e:
    PACKER_AVAILABLE = False


class Py3dbpPacker(AbstractPacker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.larger_first = kwargs.get("larger_first", True)

    def get_params(self) -> dict:
        return {}

    def pack_variant(self, order: Order) -> 'PackingVariant | None':
        if not self.is_packer_available():
            raise ImportError(
                "Py3dbpPacker requires py3dbp to be installed (pip install py3dbp)")

        packer = py3dbp.Packer()

        for idx, bin in enumerate(self.reference_bins):
            packer.add_bin(
                py3dbp.Bin(
                    name=f"Bin {idx+1}",
                    width=bin.width,
                    height=bin.height,
                    depth=bin.length,
                    max_weight=int(
                        bin.max_weight) if bin.max_weight is not None and bin.max_weight != 0.0 else 1000
                )
            )

        for article in order.articles:
            for idx in range(article.amount):
                packer.add_item(
                    py3dbp.Item(
                        name=f"{article.article_id} ({idx+1})",
                        width=int(article.width),
                        height=int(article.height),
                        depth=int(article.length),
                        weight=int(article.weight)
                    )
                )
        packer.pack(larger_first=self.larger_first)

        variant = PackingVariant()
        for b in packer.bins:
            bin = Bin(
                # id=b.name,
                width=int(b.width),
                length=int(b.depth),
                height=int(b.height),
                max_weight=b.max_weight
            )

            for idx, packed in enumerate(b.items):
                pos = Position(
                    x=int(packed.position[0]),
                    y=int(packed.position[1]),
                    z=int(packed.position[2]),
                    rotation=int(packed.rotation_type),
                )
                item = Item(
                    id=f"Item {idx+1}",
                    width=int(packed.width),
                    length=int(packed.depth),
                    height=int(packed.height),
                    position=pos
                )
                is_packed, error_msg = bin.pack_item(item)
                if not is_packed:
                    variant.add_unpacked_item(item, error_msg)

            variant.add_bin(bin)
        return variant

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE
