import os
import io
from matplotlib import patheffects
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from enum import Enum
from typing import Callable, List, Tuple

from matplotlib.patches import Rectangle
from PIL import Image

from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.packing_variant import PackingVariant


class Perspective(str, Enum):
    three_dimensional = "three_dimensional"
    front = "front"
    side = "side"
    top = "top"


Rect = Tuple[float, float, float, float]


def extract_rectangles_with_count(
    items: List[Item], perspective: Perspective
) -> List[Tuple[Rect, int]]:

    rectangles = []
    prev_rect = None
    count = 0

    if perspective == Perspective.front:
        items = sorted(items, key=lambda item: (item.position.z, item.position.x))
        to_rect: Callable[[Item], Rect] = lambda item: (
            item.position.x,
            item.position.z,
            item.width,
            item.height,
        )
    elif perspective == Perspective.top:
        to_rect: Callable[[Item], Rect] = lambda item: (
            item.position.x,
            item.position.y,
            item.width,
            item.length,
        )
    elif perspective == Perspective.side:
        to_rect: Callable[[Item], Rect] = lambda item: (
            item.position.y,
            item.position.z,
            item.length,
            item.height,
        )
    else:
        raise ValueError(f"Invalid perspective: {perspective}")

    for item in items:
        rect = to_rect(item)
        if prev_rect == rect:
            count += 1
        else:
            if prev_rect is not None:
                rectangles.append((prev_rect, count))
            prev_rect = rect
            count = 1

    rectangles.append((prev_rect, count))
    return rectangles


class PackingVisualization:
    def __init__(self):
        self.colors = list(mcolors.TABLEAU_COLORS.keys())

    def get_color(self, index: int) -> str:
        color = self.colors[index % len(self.colors)]
        return color

    def visualize_bin(
        self,
        bin: Bin,
        perspective: Perspective,
        snappoint_min_z: "int|None" = None,
        title: str = None,
        show: bool = True,
        output_dir: "str | None" = None,
        return_png: bool = False,
    ):
        if perspective == Perspective.three_dimensional:
            plot_fn = self._visualize_bin_3d
        else:
            plot_fn = self._visualize_bin_2d

        return plot_fn(
            bin=bin,
            perspective=perspective,
            snappoint_min_z=snappoint_min_z,
            title=title,
            show=show,
            output_dir=output_dir,
            return_png=return_png,
        )

    def visualize_packing_variant(
        self,
        variant: PackingVariant,
        perspective: Perspective,
        show: bool = True,
        output_dir: "str | None" = None,
        return_png=False,
    ):
        images = []
        for idx, bin in enumerate(variant.bins):
            img = self.visualize_bin(
                bin=bin,
                perspective=perspective,
                title=f"Bin {idx+1}",
                show=show,
                output_dir=output_dir,
                return_png=return_png,
            )
            images.append(img)
        return images

    def _visualize_bin_2d(
        self,
        bin: Bin,
        perspective: Perspective = Perspective.front,
        snappoint_min_z: "int|None" = None,
        title: str = None,
        show: bool = True,
        output_dir: "str | None" = None,
        return_png: bool = False,
    ):
        fig, ax = plt.subplots()

        if perspective == Perspective.front:
            ax.axes.set_xlim(0, bin.width)
            ax.axes.set_ylim(0, bin.height)
            ax.set_xlabel("Breite")
            ax.set_ylabel("Höhe")
        elif perspective == Perspective.top:
            snappoint_min_z = None
            ax.axes.set_xlim(0, bin.width)
            ax.axes.set_ylim(0, bin.length)
            ax.set_xlabel("Breite")
            ax.set_ylabel("Länge")
        elif perspective == Perspective.side:
            snappoint_min_z = None
            ax.axes.set_xlim(0, bin.length)
            ax.axes.set_ylim(0, bin.height)
            ax.set_xlabel("Länge")
            ax.set_ylabel("Höhe")
        else:
            raise ValueError(f"Invalid perspective: {perspective}")

        items = bin.packed_items

        rectangles = extract_rectangles_with_count(items, perspective)

        if title is not None:
            ax.set_title(title)
        ax.set_aspect("equal")

        for idx, (rect, count) in enumerate(rectangles):

            ax.add_patch(
                Rectangle(
                    (rect[0], rect[1]),
                    rect[2],
                    rect[3],
                    facecolor=self.get_color(idx),
                    edgecolor="black",
                    linewidth=2,
                )
            )
            if count > 1:
                txt = ax.text(
                    rect[0] + rect[2] / 2,
                    rect[1] + rect[3] / 2,
                    str(count),
                    ha="center",
                    va="center",
                    fontsize=12,
                    color="white",
                )
                txt.set_path_effects(
                    [patheffects.withStroke(linewidth=2, foreground="black")]
                )

        if snappoint_min_z is not None:
            snappoints = bin.get_snappoints(snappoint_min_z)

            radius = 0.2
            for point in snappoints:
                ax.add_patch(plt.Circle((point.x, point.z), radius, color="r"))

        if not output_dir is None:
            os.makedirs(output_dir, exist_ok=True)
            name = "packing_%s.png"
            number = 0
            while os.path.exists(os.path.join(output_dir, name % number)):
                number += 1
            plt.savefig(os.path.join(output_dir, name % number))

        if show:
            plt.show()

        if return_png:
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="png")
            img = Image.open(img_buf)
            img_buf.close()
            return img

        return fig

    def _visualize_bin_3d(
        self,
        bin: Bin,
        perspective: Perspective = Perspective.three_dimensional,
        snappoint_min_z: "int|None" = None,
        title: str = None,
        show: bool = True,
        output_dir: "str | None" = None,
        return_png: bool = False,
    ):
        if perspective != Perspective.three_dimensional:
            raise ValueError(f"Invalid perspective: {perspective}")

        items = bin.packed_items
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        ax.axes.set_xlim3d(0, bin.width)
        ax.axes.set_ylim3d(0, bin.length)
        ax.axes.set_zlim3d(0, bin.height)

        if title is not None:
            ax.set_title(title)

        # make the panes transparent
        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        # make the grid lines transparent
        ax.xaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
        ax.yaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)
        ax.zaxis._axinfo["grid"]["color"] = (1, 1, 1, 0)

        """
        # draw the pallet
        step = 2
        pallet_height = 0.01
        for width_step in range(0, self.container_size[0], step):
            ax.bar3d(
                width_step,
                0,
                0,
                2,
                self.container_size[1],
                pallet_height,
                color="#e7cfb4",
                edgecolor="black",
            )
        """
        for item in items:
            ax.bar3d(
                item.position.x,
                max(item.position.y, 0),
                item.position.z,
                item.width,
                item.length,
                item.height,
                alpha=0.8,
                edgecolor="black",
            )

        ax.set_xlabel("Width")
        ax.set_ylabel("Length")
        ax.set_zlabel("Height")

        if not output_dir is None:
            os.makedirs(output_dir, exist_ok=True)
            name = "packing_%s.png"
            number = 0
            while os.path.exists(os.path.join(output_dir, name % number)):
                number += 1
            plt.savefig(os.path.join(output_dir, name % number))

        if show:
            plt.show()

        if return_png:
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="png")
            img = Image.open(img_buf)
            img_buf.close()
            return img

        return fig
