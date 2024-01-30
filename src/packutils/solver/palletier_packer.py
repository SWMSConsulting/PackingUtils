import copy
from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.order import Order
from packutils.data.packing_variant import PackingVariant
from packutils.data.position import Position
from packutils.solver.abstract_packer import AbstractPacker

try:
    import palletier

    PACKER_AVAILABLE = True
except ImportError as e:
    PACKER_AVAILABLE = False


class PalletierPacker(AbstractPacker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.allow_rotation = kwargs.get("rotation", False)

    def get_params(self) -> dict:
        return {}

    def pack_variant(self, order: Order) -> "PackingVariant | None":
        bin_dimensions = [(b.width, b.length, b.height) for b in self.reference_bins]

        if not self.is_packer_available():
            raise ImportError(
                "PalletierPacker requires palletier to be installed (pip install -r requirements_palletier.txt)"
            )

        pallets = []
        for idx, bin in enumerate(self.reference_bins):
            pallets.append(
                palletier.Pallet(
                    dims=(bin.width, bin.length, bin.height),
                    max_weight=int(bin.max_weight) if bin.max_weight is not None else 0,
                    name=f"Bin {idx+1}",
                )
            )

        boxes = []
        for article in order.articles:
            for idx in range(article.amount):
                box = palletier.Box(
                    dims=(article.width, article.length, article.height),
                    name=article.article_id,
                )
                boxes.append(box)

        packer = palletier.Solver(
            pallets=pallets, boxes=boxes, allow_rotation=self.allow_rotation
        )

        try:
            packer.pack()
        except:
            return PackingVariant()

        variant = PackingVariant()
        for p in packer.packed_pallets:
            if not tuple(p.pallet.dims) in bin_dimensions:
                for box in p.boxes:
                    variant.add_unpacked_item(
                        Item(
                            id=box.name,
                            width=int(box.dims[0]),
                            length=int(box.dims[1]),
                            height=int(box.dims[2]),
                            position=None,
                        ),
                        "Palletier found no feasible position.",
                    )
                continue

            bin = Bin(
                # id=b.name,
                width=int(p.pallet.dims[0]),
                length=int(p.pallet.dims[1]),
                height=int(p.pallet.dims[2]),
                max_weight=p.pallet.max_weight,
            )
            bin_dimensions.remove(tuple(p.pallet.dims))

            for box in p.boxes:
                pos = Position(
                    x=int(box.pos[0]),
                    y=int(box.pos[1]),
                    z=int(box.pos[2]),
                    rotation=self._get_rotation_type(box),
                )
                item = Item(
                    id=box.name,
                    width=int(box.dims[0]),
                    length=int(box.dims[1]),
                    height=int(box.dims[2]),
                    position=pos,
                )
                is_packed, error_msg = bin.pack_item(item)
                if not is_packed:
                    variant.add_unpacked_item(item, error_msg)

            if len(variant.bins) < len(self.reference_bins):
                variant.add_bin(bin)
            else:
                for item in bin.packed_items:
                    variant.add_unpacked_item(item, "Too many bins used")

        return variant

    def _get_rotation_type(self, box):
        if box.orientation == box.dims:
            return 0
        raise NotImplementedError()

    def is_packer_available(self) -> bool:
        return PACKER_AVAILABLE
