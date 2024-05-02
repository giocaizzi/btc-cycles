"""static artist module"""

from __future__ import annotations
import copy
import datetime
from importlib.metadata import version
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from .utils import ColorBar, ProgressLabels


class StaticArtist:
    """static artist

    Using `matpotlib` to plot statically.

    Args:
        bitcoin (Bitcoin): bitcoin object
        colorbar (ColorBar): color bar object
    """

    def __init__(self, bitcoin: Bitcoin):
        self.bitcoin = copy.copy(bitcoin)
        self.colorbar = ColorBar(self.bitcoin)
        self._set_colors()

    def _set_colors(self):
        """set colors

        Create a new column in the DataFrame with the color
        """
        self.bitcoin.prices["color"] = self.bitcoin.prices["distance_ath_perc"].apply(
            lambda x: mcolors.to_hex(self.colorbar.cmap(self.colorbar.norm(x)))
        )

    def plot(self):
        """plot"""
        # Create a polar subplot
        self.f, self.axes = plt.subplots(
            1, 1, subplot_kw=dict(polar=True), figsize=(10, 10)
        )

        # Plot data
        self.add_data()

        # now point
        self.add_now()

        # halving
        self.add_halving()

        # # Plot ATHs
        self.add_aths()

        # # # plot bottoms
        # self.add_bottoms()

        # format graph
        self.format_chart()

        # legend
        self.add_legend()

        # colorbar
        self.add_colorbar()

        # image creation date and copyright
        self.add_watermark()

        # necessary althought the warning
        # otherwise a savefig on the fig would cut
        self.f.tight_layout()

        # return figure
        return self.f

    def add_watermark(self) -> None:
        """add watermark to plot"""
        date = datetime.datetime.now(datetime.UTC)
        date_text = date.strftime("%Y-%m-%d %H:%M UTC")
        self.axes.annotate(
            (f"{date_text}\n" f"© giocaizzi/btc-cycles : {version('btc-cycles')}"),
            xy=(0.5, 0.33),
            xycoords="axes fraction",
            textcoords="axes fraction",
            fontsize=8,
            ha="center",
            va="center",
            color="darkgrey",
        )

    def add_data(self) -> None:
        """add data to plot"""
        self.axes.scatter(
            self.bitcoin.prices["cycle_progress"] * 2 * np.pi,
            self.bitcoin.prices["Close"].to_numpy(),
            s=3,
            # markersize=1,
            c=self.bitcoin.prices["color"],
            zorder=9,
        )

    def format_chart(self) -> None:
        """format axes"""
        # Set y-axis to logarithmic scale
        self.axes.set_rscale("log")

        # Set direction (1 for clockwise, -1 for counterclockwise)
        self.axes.set_theta_direction(-1)
        self.axes.set_theta_offset(np.pi / 2.0)

        # Set r gridlines
        self.axes.set_rgrids(
            [
                100,
                1000,
                10000,
                100000,
                1000000,
            ],
            labels=[
                "100",
                "1k",
                "10k",
                "100k",
                "1M",
            ],
        )

        # Set xticks and labels
        self.axes.set_xticks(
            np.linspace(0, 2 * np.pi, 4, endpoint=False),
        )
        self.axes.set_xticklabels(
            ProgressLabels(self.bitcoin).labels,
            fontsize=8,
        )

        # r label
        self.axes.set_rlabel_position(0)

        # y label
        self.axes.set_ylabel("Price (USD)", rotation=0)
        self.axes.yaxis.set_label_coords(0.5, 1.01)

        # ticks params
        self.axes.tick_params(axis="both", which="major", pad=30)

        # edge color
        [spine.set_edgecolor("lightgrey") for spine in self.axes.spines.values()]

    def add_bottoms(self) -> None:
        """add bottoms to plot"""
        self.axes.scatter(
            self.bitcoin.prices["cycle_progress"] * 2 * np.pi,
            self.bitcoin.prices["Close"],
            marker="o",
            c="r",
            s=20,
            zorder=10,
        )

    def add_aths(self) -> None:
        """add all time highs to plot"""
        aths = self.bitcoin.prices[self.bitcoin.prices["distance_ath_perc"] == 0]
        self.axes.scatter(
            aths["cycle_progress"] * 2 * np.pi,
            aths["Close"],
            marker="x",
            c="k",
            s=20,
            zorder=10,
        )

    def add_halving(self) -> None:
        """add halving to plot"""
        self.axes.vlines(
            0,
            100,
            1000000,
            color="lightgreen",
            linewidth=3,
            zorder=0,
        )

    def add_now(self) -> None:
        self.axes.scatter(
            self.bitcoin.prices["cycle_progress"].to_numpy()[-1] * 2 * np.pi,
            self.bitcoin.prices["Close"].to_numpy()[-1],
            marker="D",
            c=self.bitcoin.prices["color"].to_numpy()[-1],
            s=50,
            zorder=8,
        )
        # now line
        self.axes.vlines(
            self.bitcoin.prices["cycle_progress"].to_numpy()[-1] * 2 * np.pi,
            100,
            self.bitcoin.prices["Close"].to_numpy()[-1],
            color="k",
            linestyle="--",
            zorder=8,
        )

    def add_legend(self) -> None:
        """add legend and title to plot"""
        self.axes.legend(
            [
                "BTC/USD",
                "Today BTC/USD Close",
                "Today",
                "Halving day",
                "All time high (ATH)",
            ],
            loc="upper left",
            bbox_to_anchor=(-0.1, 1),
            fontsize=10,
            title="$\\bf{Legend}$",
            title_fontsize="13",
            # labelspacing=1.5,
            frameon=False,
        )

        # title
        self.axes.set_title(
            "Bitcoin price halving cycles",
            fontdict={"fontsize": 15, "fontweight": "bold"},
            pad=20,
        )

    def add_colorbar(self) -> None:
        """add colorbar to plot"""
        sm = plt.cm.ScalarMappable(cmap=self.colorbar.cmap, norm=self.colorbar.norm)
        inset_ax = inset_axes(
            self.axes,
            width="2.5%",
            height="25%",
            # loc="upper right",
            bbox_to_anchor=(0, 0, 1, 1),
            bbox_transform=self.axes.transAxes,
            borderpad=0,
        )
        cbar = self.f.colorbar(
            sm,
            cax=inset_ax,
            orientation="vertical",
            ticks=[0, -0.2, -0.4, -0.6, -0.8, -1],
        )
        cbar.ax.set_yticklabels(["ATH", "-20%", "-40%", "-60%", "-80%", "-100%"])
        inset_ax.set_title("Distance from ATH", fontdict={"fontweight": "bold"}, pad=10)
