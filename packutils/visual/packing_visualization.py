import os
import io
import matplotlib.pyplot as plt

from PIL import Image

from packutils.data.bin import Bin


class PackingVisualization():
    def __init__(self):
        pass

    def visualize_bin(
        self, bin: Bin, show: bool = True, output_dir: str | None = None
    ):
        print(bin)
        if bin.width <= 1 or bin.length <= 1 or bin.height <= 1:
            return self._visualize_bin_2d(bin, show, output_dir)
        else:
            return self._visualize_bin_3d(bin, show, output_dir)

    def visualize_packing_variant():
        pass

    def _visualize_bin_2d(
        self, bin: Bin, show: bool = True, output_dir: str | None = None
    ):
        raise NotImplementedError()
        items = bin.packed_items
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        ax.axes.set_xlim3d(0, bin.width)
        ax.axes.set_ylim3d(0, bin.length)
        ax.axes.set_zlim3d(0, bin.height)

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
                item.position.y,
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

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img = Image.open(img_buf)
        img.show(title="My Image")
        img_buf.close()

        return img

    def _visualize_bin_3d(
        self, bin: Bin, show: bool = True, output_dir: str | None = None
    ):
        items = bin.packed_items
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        ax.axes.set_xlim3d(0, bin.width)
        ax.axes.set_ylim3d(0, bin.length)
        ax.axes.set_zlim3d(0, bin.height)

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
                item.position.y,
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

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img = Image.open(img_buf)
        img_buf.close()

        return img
