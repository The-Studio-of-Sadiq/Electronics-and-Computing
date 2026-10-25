"""Figures for Chapter 34 — VLSI Design.

Run from the repository root:  python figures/scripts/ch34.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, Circle, PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

RED = "#C62828"
BLUE = COLORS[0]
ORANGE = COLORS[1]
GREEN = COLORS[2]
GREY = "#777777"


# ----------------------------------------------------------------------------
# Figure 34.1 — design flow
# ----------------------------------------------------------------------------
def fig_34_1():
    fig, ax = plt.subplots(figsize=(6.8, 6.0))
    ax.set_xlim(0, 14.4)
    ax.set_ylim(0.6, 12.8)
    ax.set_aspect("equal")
    ax.axis("off")

    steps = [
        "Specification and architecture",
        "RTL (Verilog / VHDL)",
        "Logic synthesis",
        "Floorplan and power grid",
        "Placement",
        "Clock-tree synthesis",
        "Routing",
        "Parasitic extraction",
        "Sign-off STA, power, IR drop",
        "Physical verification\nDRC / LVS / antenna",
        "Tape-out\n(GDSII / OASIS to mask shop)",
    ]
    checks = {
        1: "Simulation and lint;\nformal property checks",
        2: "Logical equivalence\nRTL vs netlist",
        4: "Congestion map",
        5: "Skew report",
        6: "DRC-clean routing",
        8: "Timing at all corners",
        9: "LVS match",
    }
    x0, w, h = 3.3, 4.9, 0.8
    ys = [11.75 - 1.04 * i for i in range(len(steps))]
    for i, (s, y) in enumerate(zip(steps, ys)):
        fc = "#E3F2E1" if i == len(steps) - 1 else "#EEF3F8"
        box(ax, x0, y - h / 2, w, h, s, fc=fc, fontsize=8.2)
        if i < len(steps) - 1:
            arrow(ax, x0 + w / 2, y - h / 2, x0 + w / 2, ys[i + 1] + h / 2 + 0.02)
    # checks
    cx, cw = 9.7, 4.6
    for i, c in checks.items():
        y = ys[i]
        box(ax, cx, y - h / 2, cw, h, c, fc="#FFF6E5", ec="#B07A00", fontsize=8)
        ax.plot([x0 + w, cx], [y, y], ls=(0, (3, 2)), color="#B07A00", lw=1.0)
    ax.text(cx + cw / 2, 12.45, "Check after the step", ha="center", va="center",
            fontsize=9, color="#7A5500", weight="bold")
    ax.text(x0 + w / 2, 12.45, "Flow step", ha="center", va="center",
            fontsize=9, color=INK, weight="bold")

    # inputs to synthesis
    y = ys[2]
    box(ax, 0.85, y + 0.05, 2.12, 0.5, "Liberty .lib", fc="white", fontsize=7.1)
    box(ax, 0.85, y - 0.6, 2.12, 0.5, "SDC constraints", fc="white", fontsize=7.1)
    arrow(ax, 2.97, y + 0.3, x0, y + 0.12)
    arrow(ax, 2.97, y - 0.35, x0, y - 0.12)

    # ECO feedback loop: sign-off back to synthesis and placement
    fx = 8.75
    ys_so = ys[8]
    ax.plot([x0 + w, fx], [ys_so - 0.15, ys_so - 0.15], color=RED, lw=1.4)
    ax.plot([fx, fx], [ys_so - 0.15, ys[2] + 0.2], color=RED, lw=1.4)
    for tgt in (2, 4):
        ax.annotate("", xy=(x0 + w, ys[tgt] + 0.2), xytext=(fx, ys[tgt] + 0.2),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4,
                                    shrinkA=0, shrinkB=0, mutation_scale=11))
    ax.text(fx + 0.25, ys[7], "timing / power closure\nloop (ECO) back to\nsynthesis and placement",
            ha="left", va="center", fontsize=7.6, color=RED,
            bbox=dict(fc="white", ec=RED, lw=0.8, boxstyle="round,pad=0.25"))

    # abstraction side bar
    levels = [("Arch.", 0, 0, "#F3E5F5"), ("RTL", 1, 1, "#E3F2FD"),
              ("Gate", 2, 2, "#E8F5E9"), ("Layout", 3, 10, "#FFF3E0")]
    for name, a, b, col in levels:
        top = ys[a] + h / 2 + 0.12
        bot = ys[b] - h / 2 - 0.12
        ax.add_patch(Rectangle((0.1, bot), 0.6, top - bot, fc=col, ec=GREY, lw=0.8))
        ax.text(0.4, (top + bot) / 2, name, rotation=90, ha="center", va="center",
                fontsize=7.8, color=INK)
    ax.text(0.4, 12.45, "Level", ha="center", va="center", fontsize=8.5, color=INK,
            weight="bold")
    save(fig, "34", "fig-34-1-vlsi-design-flow")


# ----------------------------------------------------------------------------
# Figure 34.2 — SoC floorplan
# ----------------------------------------------------------------------------
def fig_34_2():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.set_xlim(-0.75, 8.1)
    ax.set_ylim(-0.75, 5.6)
    ax.set_aspect("equal")
    ax.axis("off")

    # die and pad ring
    ax.add_patch(Rectangle((0, 0), 5, 5, fc="#FAFAFA", ec=INK, lw=1.6))
    pad, pw = 0.32, 0.22
    n = 15
    for k in range(n):
        p = 0.55 + k * (3.9 / (n - 1)) - pw / 2
        for (x, y) in ((p, 0.05), (p, 5 - 0.05 - pad), (0.05, p), (5 - 0.05 - pad, p)):
            wd, ht = (pw, pad) if y in (0.05, 5 - 0.05 - pad) else (pad, pw)
            ax.add_patch(Rectangle((x, y), wd, ht, fc="#D7CCC8", ec="#6D4C41", lw=0.5))
    # side labels
    ax.text(2.5, -0.12, "pads: Ethernet  |  VDD / VSS supplies", ha="center", va="top", fontsize=8)
    ax.text(2.5, 5.12, "pads: JTAG  |  VDD / VSS supplies  |  PLL ref", ha="center", va="bottom",
            fontsize=8)
    ax.text(-0.12, 2.5, "pads: CAN-FD  |  GPIO  |  supplies", rotation=90, ha="right",
            va="center", fontsize=8)
    ax.text(5.12, 2.5, "pads: LVDS ADC interface", rotation=90, ha="left", va="center",
            fontsize=8)

    # core power ring (around the standard-cell / macro core)
    c0, c1 = 0.5, 4.5
    ax.add_patch(Rectangle((c0, c0), c1 - c0, c1 - c0, fc="none", ec="#8E24AA", lw=2.6, alpha=0.8))

    # Cortex-R5 cluster (1.5 x 1.2 mm)
    ax.add_patch(Rectangle((0.65, 3.2), 1.5, 1.2, fc="#BBDEFB", ec=INK, lw=1.0))
    ax.text(1.4, 3.8, "Cortex-R5\ncluster\n1.5 × 1.2 mm", ha="center", va="center", fontsize=8)

    # DSP standard-cell region 1.8 x 1.3 mm = 2.34 mm2 (hatched)
    dx0, dy0, dw, dh = 1.75, 1.55, 1.80, 1.30
    ax.add_patch(Rectangle((dx0, dy0), dw, dh, fc="#EEF7EE", ec="#A5D6A7", lw=0, hatch="//"))
    ax.add_patch(Rectangle((dx0, dy0), dw, dh, fc="none", ec=GREEN, lw=1.3))
    # power straps over the standard-cell region (drawn every 0.2 mm; real pitch 20 um)
    for yy in np.arange(dy0 + 0.1, dy0 + dh, 0.2):
        ax.plot([dx0, dx0 + dw], [yy, yy], color=BLUE, lw=1.0, alpha=0.85)
    for xx in np.arange(dx0 + 0.1, dx0 + dw, 0.2):
        ax.plot([xx, xx], [dy0, dy0 + dh], color=ORANGE, lw=1.0, alpha=0.85)
    # IR-drop hot spot
    hx, hy = dx0 + 1.2, dy0 + 0.45
    for r, a in ((0.30, 0.20), (0.20, 0.32), (0.10, 0.6)):
        ax.add_patch(Circle((hx, hy), r, fc=RED, ec="none", alpha=a, zorder=4))
    ax.text(dx0 + dw / 2, dy0 + dh - 0.32, "FFT / DSP engine\nstd cells, 2.3 mm²",
            ha="center", va="center", fontsize=7.2, zorder=6,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.0))

    # SRAM macros: 4 on the left edge, 4 on the bottom edge, pins facing the DSP region
    ch = 0.08          # channel (40 um, exaggerated)
    sram = []
    sh = (dh - 3 * 0.03) / 4
    for k in range(4):
        sram.append((dx0 - ch - 0.5, dy0 + k * (sh + 0.03), 0.5, sh, "v"))
    sw = (dw - 3 * 0.03) / 4
    for k in range(4):
        sram.append((dx0 + k * (sw + 0.03), dy0 - ch - 0.5, sw, 0.5, "h"))
    for (x, y, wd, ht, o) in sram:
        ax.add_patch(Rectangle((x - 0.025, y - 0.025), wd + 0.05, ht + 0.05, fc="none",
                               ec=GREY, lw=0.6, ls=(0, (2, 1.5))))
        ax.add_patch(Rectangle((x, y), wd, ht, fc="#FFE0B2", ec="#E65100", lw=0.9))
        if o == "v":
            ax.add_patch(Rectangle((x + wd - 0.05, y + 0.03), 0.05, ht - 0.06, fc="#E65100",
                                   ec="none"))
            ax.text(x + wd / 2 - 0.02, y + ht / 2, "SRAM", ha="center", va="center",
                    fontsize=6.2)
        else:
            ax.add_patch(Rectangle((x + 0.03, y + ht - 0.05), wd - 0.06, 0.05, fc="#E65100",
                                   ec="none"))
            ax.text(x + wd / 2, y + ht / 2 - 0.02, "SRAM", ha="center", va="center",
                    fontsize=6.2, rotation=90)

    # PLL with guard ring (top right)
    ax.add_patch(Rectangle((3.62, 3.72), 0.74, 0.66, fc="none", ec=INK, lw=1.0, ls="--"))
    ax.add_patch(Rectangle((3.72, 3.80), 0.54, 0.50, fc="#F8BBD0", ec=INK, lw=1.0))
    ax.text(3.99, 4.05, "PLL\nclk gen", ha="center", va="center", fontsize=7)

    # ADC interface hard macro (right edge)
    ax.add_patch(Rectangle((3.85, 1.85), 0.55, 1.5, fc="#D1C4E9", ec=INK, lw=1.0))
    ax.text(4.125, 2.6, "ADC\ninter-\nface\nhard\nmacro", ha="center", va="center", fontsize=6.4)

    # always-on domain (bottom right) with dashed power-domain boundary
    ax.add_patch(Rectangle((3.72, 0.6), 0.72, 0.8, fc="#FFF9C4", ec=RED, lw=1.2, ls="--"))
    ax.text(4.08, 1.0, "always-\non\ndomain", ha="center", va="center", fontsize=6.6)

    # key (right side)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [
        Line2D([], [], color="#8E24AA", lw=2.6, label="core power ring (VDD/VSS)"),
        Line2D([], [], color=BLUE, lw=1.2, label="M9 horizontal VDD/VSS straps,\nevery 20 µm (drawn sparser)"),
        Line2D([], [], color=ORANGE, lw=1.2, label="M8 vertical VDD/VSS straps"),
        Patch(fc="#EEF7EE", ec=GREEN, hatch="//", label="standard-cell region"),
        Patch(fc="#FFE0B2", ec="#E65100", label="SRAM macro, 8 × 512 kbit"),
        Line2D([], [], color=GREY, lw=0.8, ls=(0, (2, 1.5)), label="macro halo 10 µm"),
        Patch(fc="white", ec="white", label="channel 40 µm between\nmacros and logic"),
        Line2D([], [], color=INK, lw=1.0, ls="--", label="PLL guard ring"),
        Line2D([], [], color=RED, lw=1.2, ls="--", label="power-domain boundary"),
        Line2D([], [], color=RED, marker="o", ls="none", ms=9, alpha=0.5,
               label="IR-drop hot spot under\nDSP array (61 mV)"),
    ]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(0.695, 0.5), fontsize=7.4,
              title="die 5 mm × 5 mm, 28 nm", title_fontsize=8, labelspacing=0.75,
              handlelength=2.2)
    ax.text(5.75, -0.5, "macros, halos and channels not to scale", fontsize=7, color=GREY,
            style="italic")
    save(fig, "34", "fig-34-2-soc-floorplan")


# ----------------------------------------------------------------------------
# Figure 34.3 — H-tree and arrival-time histogram
# ----------------------------------------------------------------------------
def _buf(ax, x, y, s=0.07, color=INK):
    ax.add_patch(Polygon([(x - s, y + s * 0.8), (x + s, y + s * 0.8), (x, y - s * 0.9)],
                         closed=True, fc="white", ec=color, lw=1.0, zorder=5))


def fig_34_3():
    fig = plt.figure(figsize=(6.8, 4.5))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.12, 1], height_ratios=[1.5, 1],
                          wspace=0.32, hspace=0.5)
    ax = fig.add_subplot(gs[:, 0])
    ax.set_xlim(-0.45, 2.45)
    ax.set_ylim(-0.42, 2.75)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 2, 2, fc="#FAFAFA", ec=INK, lw=1.2))
    ax.text(1.0, -0.06, "block 2 mm × 2 mm;  16 leaf clusters × ≈ 6000 FFs",
            fontsize=7.4, va="top", ha="center")

    # PLL and trunk
    ax.add_patch(Rectangle((0.82, 2.12), 0.36, 0.22, fc="#F8BBD0", ec=INK, lw=1.0))
    ax.text(1.0, 2.23, "PLL", ha="center", va="center", fontsize=8)
    ax.plot([1, 1], [2.12, 1.0], color=BLUE, lw=3.2, solid_capstyle="butt")
    _buf(ax, 1.0, 1.9)

    def H(x, y, s, lw):
        ax.plot([x - s / 2, x + s / 2], [y, y], color=BLUE, lw=lw, solid_capstyle="butt")
        for xx in (x - s / 2, x + s / 2):
            ax.plot([xx, xx], [y - s / 2, y + s / 2], color=BLUE, lw=lw,
                    solid_capstyle="butt")
        _buf(ax, x, y)
        return [(x + dx * s / 2, y + dy * s / 2) for dx in (-1, 1) for dy in (-1, 1)]

    l1 = H(1.0, 1.0, 1.0, 2.6)
    leaves = []
    for (x, y) in l1:
        leaves += H(x, y, 0.5, 1.8)
    rng = np.random.default_rng(4)
    for (x, y) in leaves:
        for dx in (-0.06, 0.06):
            ax.plot([x, x + dx], [y, y - 0.07], color=GREEN, lw=0.8)
        pts = rng.uniform(-0.1, 0.1, (14, 2))
        ax.scatter(x + pts[:, 0], y - 0.04 + pts[:, 1] * 0.8, s=2.2, color=GREY, zorder=3)
        _buf(ax, x, y, s=0.045, color=GREEN)

    # labelled pair of leaves on opposite sides
    (xa, ya), (xb, yb) = (0.25, 0.25), (1.75, 1.75)
    ax.add_patch(Circle((xa, ya), 0.13, fc="none", ec=RED, lw=1.2, zorder=6))
    ax.add_patch(Circle((xb, yb), 0.13, fc="none", ec=RED, lw=1.2, zorder=6))
    ax.annotate("395 ps", xy=(xa - 0.12, ya + 0.05), xytext=(-0.44, 0.55), fontsize=8,
                color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.annotate("420 ps", xy=(xb + 0.1, yb + 0.08), xytext=(2.05, 2.1), fontsize=8,
                color=RED, arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax.text(1.0, 2.42, "insertion delay ≈ 420 ps at the leaves\n"
            "skew between circled leaves = 25 ps",
            ha="center", va="bottom", fontsize=7.6, color=INK)

    # histogram
    ah = fig.add_subplot(gs[0, 1])
    rng = np.random.default_rng(7)
    t = rng.normal(410, 10, 16 * 6000)
    ah.hist(t, bins=np.arange(360, 461, 2), color=BLUE, alpha=0.85, edgecolor="white", lw=0.3)
    ah.set_xlim(360, 460)
    for xv in (385, 435):
        ah.axvline(xv, ls="--", color=RED, lw=1.1)
    ymax = ah.get_ylim()[1]
    ah.set_ylim(0, ymax * 1.3)
    ah.annotate("", xy=(435, ymax * 1.12), xytext=(385, ymax * 1.12),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.0, mutation_scale=8))
    ah.text(410, ymax * 1.15, "skew target 50 ps", ha="center", va="bottom", fontsize=7.8,
            color=RED)
    ah.text(437, ymax * 0.95, "slow corner\nμ = 410 ps\n3σ = ±30 ps", fontsize=7.4, va="top")
    ah.set_xlabel("Clock arrival time at flip-flop (ps)", fontsize=9)
    ah.set_ylabel("Number of flip-flops", fontsize=9)
    ah.tick_params(labelsize=8)

    # ICG inset
    ai = fig.add_subplot(gs[1, 1])
    ai.set_xlim(-0.4, 10)
    ai.set_ylim(0, 4.3)
    ai.set_aspect("equal")
    ai.axis("off")
    ai.text(4.8, 4.25, "Clock-gating cell (ICG) on one branch", ha="center",
            va="top", fontsize=7.8)
    ai.add_patch(Rectangle((2.2, 1.2), 2.0, 2.0, fc="#EEF3F8", ec=INK, lw=1.0))
    ai.text(3.2, 2.2, "latch", ha="center", va="center", fontsize=7.5)
    ai.text(2.35, 2.75, "D", fontsize=7, va="center")
    ai.text(2.35, 1.65, "G", fontsize=7, va="center")
    ai.text(4.05, 2.75, "Q", fontsize=7, va="center", ha="right")
    ai.add_patch(Circle((2.08, 1.65), 0.12, fc="white", ec=INK, lw=1.0))
    ai.plot([0.6, 2.2], [2.75, 2.75], color=INK, lw=1.1)
    ai.text(0.5, 2.75, "EN", ha="right", va="center", fontsize=7.5)
    # AND gate
    gx, gy = 5.6, 1.6
    th = np.linspace(-np.pi / 2, np.pi / 2, 40)
    pts = [(gx, gy - 0.8), (gx + 0.7, gy - 0.8)] + \
        [(gx + 0.7 + 0.8 * np.cos(a), gy + 0.8 * np.sin(a)) for a in th] + \
        [(gx + 0.7, gy + 0.8), (gx, gy + 0.8)]
    ai.add_patch(Polygon(pts, closed=True, fc="white", ec=INK, lw=1.1))
    ai.text(gx + 0.6, gy, "AND", ha="center", va="center", fontsize=6.5)
    ai.plot([4.2, 4.9, 4.9, gx], [2.75, 2.75, gy + 0.4, gy + 0.4], color=INK, lw=1.1)
    ai.plot([0.6, 1.96], [1.65, 1.65], color=BLUE, lw=1.4)
    ai.plot([1.4, 1.4, 5.1, 5.1, gx], [1.65, 0.4, 0.4, gy - 0.4, gy - 0.4], color=BLUE, lw=1.4)
    ai.plot([1.4], [1.65], "o", ms=3, color=BLUE)
    ai.text(0.5, 1.65, "CLK", ha="right", va="center", fontsize=7.5, color=BLUE)
    ai.plot([gx + 1.5, 8.3], [gy, gy], color=BLUE, lw=1.4)
    ai.text(8.4, gy, "GCLK", ha="left", va="center", fontsize=7.5, color=BLUE)
    save(fig, "34", "fig-34-3-clock-tree")


# ----------------------------------------------------------------------------
# Figure 34.4 — setup and hold slack timing diagram
# ----------------------------------------------------------------------------
def _clk(ax, y, edges, t0, t1, h=0.6, s=10.0, color=INK, lw=1.4):
    """edges: list of (t, level) 50 % crossings."""
    lev = 0
    xs, ys = [t0], [y]
    for t, new in edges:
        xs += [t - s / 2, t + s / 2]
        ys += [y + lev * h, y + new * h]
        lev = new
    xs.append(t1)
    ys.append(y + lev * h)
    ax.plot(xs, ys, color=color, lw=lw)


def _bus(ax, y, segs, h=0.6, s=10.0, t0=None, t1=None, fs=7.5):
    for ta, tb, text, kind in segs:
        la = 0 if (t0 is not None and abs(ta - t0) < 1e-9) else s / 2
        lb = 0 if (t1 is not None and abs(tb - t1) < 1e-9) else s / 2
        pts = (([(ta, y + h / 2)] if la else []) + [(ta + la, y + h), (tb - lb, y + h)]
               + ([(tb, y + h / 2)] if lb else []) + [(tb - lb, y), (ta + la, y)])
        if kind == "hatch":
            ax.add_patch(Polygon(pts, closed=True, fc="white", ec=INK, lw=1.0, hatch="////"))
        else:
            ax.add_patch(Polygon(pts, closed=True, fc=kind, ec=INK, lw=1.2))
        if text:
            ax.text((ta + tb) / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def _bracket(ax, x0, x1, y, text, color=RED, fs=7.8, above=True):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="|-|", color=color, lw=1.2, mutation_scale=3,
                                shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + (0.08 if above else -0.08), text, ha="center",
            va="bottom" if above else "top", fontsize=fs, color=color)


def fig_34_4():
    fig = plt.figure(figsize=(6.8, 4.4))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.55, 1.05, 1.2], wspace=0.2)
    R = {"CLK": 8.0, "CLK_L": 6.4, "CLK_C": 4.8, "Q": 3.2, "D": 1.6}
    WIN1, WIN2 = "#FFCC80", "#FFE9C7"
    BROWN = "#9A5B00"

    def frame(a, x0, x1, xlabel, title, ticks):
        a.set_xlim(x0, x1)
        a.set_ylim(0.0, 9.7)
        a.set_yticks([])
        a.spines["left"].set_visible(False)
        a.set_xticks(ticks)
        a.tick_params(labelsize=8)
        a.set_xlabel(xlabel, fontsize=8.2)
        a.set_title(title, fontsize=9)

    # ---- (a) whole path, slow corner ------------------------------------------
    ax = fig.add_subplot(gs[0])
    T0, T1 = 0, 1500
    frame(ax, -330, T1 + 15, "Time (ps), SS 0.81 V 125 °C", "(a) Setup check, slow corner",
          [0, 500, 1000, 1500])
    names = {"CLK": "CLK (PLL)", "CLK_L": "CLK_L", "CLK_C": "CLK_C", "Q": "Q (launch)",
             "D": "D (capture)"}
    for k, y in R.items():
        ax.text(-25, y + 0.3, names[k], ha="right", va="center", fontsize=8)
    _clk(ax, R["CLK"], [(0, 1), (500, 0), (1000, 1)], T0, T1)
    _clk(ax, R["CLK_L"], [(420, 1), (920, 0), (1420, 1)], T0, T1, color=BLUE)
    _clk(ax, R["CLK_C"], [(395, 1), (895, 0), (1395, 1)], T0, T1, color=GREEN)
    _bus(ax, R["Q"], [(T0, 505, "old", "white"), (505, T1, "new data", "#E3F2FD")],
         t0=T0, t1=T1)
    _bus(ax, R["D"], [(T0, 505, "old", "white"), (505, 1372, "", "hatch"),
                      (1372, T1, "", "#E3F2FD")], t0=T0, t1=T1)
    for t, col in ((0, GREY), (1000, GREY), (420, BLUE), (395, GREEN), (1395, GREEN)):
        ax.axvline(t, color=col, lw=0.6, ls=":", zorder=0)
    yl, yc, yq, yd = R["CLK_L"], R["CLK_C"], R["Q"], R["D"]
    ax.annotate("", xy=(420, yl + 0.95), xytext=(0, yl + 0.95),
                arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=0.9, mutation_scale=7))
    ax.text(210, yl + 1.0, "t_L = 420 ps", ha="center", va="bottom", fontsize=7, color=BLUE)
    ax.annotate("", xy=(395, yc + 0.95), xytext=(0, yc + 0.95),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=0.9, mutation_scale=7))
    ax.text(197, yc + 1.0, "t_C = 395 ps", ha="center", va="bottom", fontsize=7, color=GREEN)
    ax.annotate("", xy=(1395, yc + 0.95), xytext=(1000, yc + 0.95),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=0.9, mutation_scale=7))
    ax.text(1197, yc + 1.0, "395 ps", ha="center", va="bottom", fontsize=7, color=GREEN)
    ax.text(1000, R["CLK"] + 0.75, "T = 1000 ps", ha="center", va="bottom", fontsize=7,
            color=GREY)
    ax.annotate("", xy=(505, yq + 0.85), xytext=(420, yq + 0.85),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=6))
    ax.text(530, yq + 0.9, "t_cq = 85 ps (Q at 505)", ha="left", va="bottom", fontsize=7)
    ax.annotate("", xy=(1372, yd + 0.85), xytext=(505, yd + 0.85),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    ax.text(938, yd + 0.9, "t_logic = 867 ps", ha="center", va="bottom", fontsize=7)
    # zoom marker
    ax.add_patch(Rectangle((1300, yd - 0.35), 120, yc + 0.95 - yd, fc="none", ec=RED, lw=0.9,
                           ls="--"))
    ax.text(1360, yd - 0.45, "zoom (b)", ha="center", va="top", fontsize=7, color=RED)

    # ---- (b) zoom of the capture edge, setup -----------------------------------
    az = fig.add_subplot(gs[1])
    Z0, Z1 = 1300, 1420
    frame(az, Z0, Z1, "Time (ps)", "(b) Setup zoom", [1300, 1350, 1400])
    _clk(az, yc, [(1395, 1)], Z0, Z1, s=2.5, color=GREEN)
    _bus(az, yd, [(Z0, 1372, "", "hatch"), (1372, Z1, "new", "#E3F2FD")], s=2.5,
         t0=Z0, t1=Z1, fs=7)
    az.add_patch(Rectangle((1330, yd - 0.3), 35, 1.2, fc=WIN1, ec="none", alpha=0.6, zorder=3))
    az.add_patch(Rectangle((1365, yd - 0.3), 30, 1.2, fc=WIN2, ec="#E0A040", lw=0.6, alpha=0.6, zorder=3))
    az.text(1347.5, yd + 1.3, "setup\n35", ha="center", va="center", fontsize=6.4, color=BROWN)
    az.text(1386, yd + 1.3, "unc.\n30", ha="center", va="center", fontsize=6.4, color=BROWN)
    az.axvline(1395, color=GREEN, lw=0.6, ls=":", zorder=0)
    az.text(1418, yc + 0.95, "capture\nedge 1395", ha="right", va="bottom", fontsize=6.4,
            color=GREEN)
    az.plot([1330, 1330], [yd - 0.4, yc + 0.6], color=RED, lw=1.0, ls="--")
    az.text(1302, yc + 0.95, "required\n1330", ha="left", va="bottom", fontsize=6.4,
            color=RED)
    az.plot([1372, 1372], [yd - 0.4, yd + 2.1], color=RED, lw=1.0, ls="--")
    az.text(1372, yd + 2.15, "arrival 1372", ha="center", va="bottom", fontsize=6.4, color=RED)
    _bracket(az, 1330, 1372, yd - 0.75, "setup slack\n−42 ps", above=False, fs=7.6)

    # ---- (c) hold check, fast corner --------------------------------------------
    ah = fig.add_subplot(gs[2])
    H0, H1 = 285, 415
    frame(ah, H0, H1, "Time (ps), FF 0.99 V −40 °C", "(c) Hold check", [300, 350, 400])
    _clk(ah, yl, [(300, 1)], H0, H1, s=2.5, color=BLUE)
    _clk(ah, yc, [(360, 1)], H0, H1, s=2.5, color=GREEN)
    _bus(ah, yq, [(H0, 345, "old", "white"), (345, H1, "new", "#E3F2FD")], s=2.5,
         t0=H0, t1=H1, fs=7)
    _bus(ah, yd, [(H0, 365, "old", "white"), (365, H1, "new", "#E3F2FD")], s=2.5,
         t0=H0, t1=H1, fs=7)
    ah.add_patch(Rectangle((360, yd - 0.3), 15, 1.2, fc=WIN1, ec="none", alpha=0.6, zorder=3))
    ah.add_patch(Rectangle((375, yd - 0.3), 20, 1.2, fc=WIN2, ec="#E0A040", lw=0.6, alpha=0.6, zorder=3))
    for t, col in ((300, BLUE), (360, GREEN)):
        ah.axvline(t, color=col, lw=0.6, ls=":", zorder=0)
    ah.text(302, yl + 0.75, "CLK_L 300", ha="left", va="bottom", fontsize=6.6, color=BLUE)
    ah.text(358, yc + 0.75, "CLK_C 360", ha="right", va="bottom", fontsize=6.6, color=GREEN)
    ah.text(343, yq + 0.75, "Q 345", ha="right", va="bottom", fontsize=6.6)
    ah.text(H0 + 2, yd + 0.95, "D at 365", ha="left", va="bottom", fontsize=6.6)
    ah.plot([395, 395], [yd - 0.4, yc + 0.6], color=RED, lw=1.0, ls="--")
    ah.text(396, yc + 0.95, "hold\nrequired\n395", ha="center", va="bottom", fontsize=6.4,
            color=RED)
    ah.text(393, yd + 1.3, "hold 15\n+ unc. 20", ha="right", va="center", fontsize=6.4,
            color=BROWN)
    _bracket(ah, 365, 395, yd - 0.75, "hold slack\n−30 ps", above=False, fs=7.6)
    save(fig, "34", "fig-34-4-setup-hold-slack")


# ----------------------------------------------------------------------------
# Figure 34.5 — yield and cost per good die
# ----------------------------------------------------------------------------
def _dpw(a, d=300.0):
    return np.floor(np.pi * (d / 2) ** 2 / a - np.pi * d / np.sqrt(2 * a))


def _y_nb(a, d0, alpha=3.0):
    return (1 + a / 100 * d0 / alpha) ** -alpha


def _y_p(a, d0):
    return np.exp(-a / 100 * d0)


def fig_34_5():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.6))
    A = np.logspace(1, np.log10(800), 400)
    for d0, col in ((0.05, BLUE), (0.10, ORANGE)):
        a1.plot(A, 100 * _y_nb(A, d0), color=col, label=f"NB α = 3, D₀ = {d0:.2f} cm⁻²")
        a1.plot(A, 100 * _y_p(A, d0), color=col, ls="--", lw=1.4,
                label=f"Poisson, D₀ = {d0:.2f} cm⁻²")
    for a, txt, dx in ((25, "97.5 %", 0), (100, "90.6 %", 0), (600, "57.9 %", -14)):
        y = 100 * _y_nb(a, 0.10)
        a1.plot(a, y, "o", color=ORANGE, ms=5, mec="white")
        a1.annotate(txt, (a, y), xytext=(dx, -9), textcoords="offset points", ha="center" if dx == 0 else "right",
                    va="top", fontsize=7.8, color=ORANGE)
    a1.set_xscale("log")
    a1.set_xlim(10, 800)
    a1.set_ylim(0, 100)
    a1.set_xlabel("Die area (mm²)")
    a1.set_ylabel("Defect-limited yield (%)")
    a1.legend(fontsize=7, loc="lower left")
    a1.grid(True, which="both", lw=0.4)

    for w, d0, col, lab in ((3000, 0.05, BLUE, "28 nm: 3000 USD wafer, D₀ = 0.05"),
                            (17000, 0.10, ORANGE, "5 nm: 17000 USD wafer, D₀ = 0.10")):
        c = w / (_dpw(A) * _y_nb(A, d0))
        a2.plot(A, c, color=col, label=lab)
        for a in (25, 100, 600):
            v = w / (_dpw(a) * _y_nb(a, d0))
            a2.plot(a, v, "o", color=col, ms=5, mec="white")
            a2.annotate(f"{v:.2f}" if v < 10 else f"{v:.1f}", (a, v), xytext=(-5, 4),
                        textcoords="offset points", ha="right", fontsize=7.2, color=col)
    cc = 4 * 17000 / (_dpw(150) * _y_nb(150, 0.10))
    a2.plot(600, cc, "D", color=GREEN, ms=6, mec="white")
    a2.annotate(f"4 × 150 mm² chiplets\n(5 nm): {cc:.0f} USD", (600, cc), xytext=(200, 5.5),
                textcoords="data", ha="left", va="center", fontsize=7.2, color=GREEN,
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    a2.set_xscale("log")
    a2.set_yscale("log")
    a2.set_xlim(10, 800)
    a2.set_ylim(0.3, 1000)
    a2.set_xlabel("Die area (mm²)")
    a2.set_ylabel("Cost per good die (USD)")
    a2.legend(fontsize=7, loc="lower right")
    a2.grid(True, which="major", lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "34", "fig-34-5-yield-versus-die-area")


if __name__ == "__main__":
    fig_34_1()
    fig_34_2()
    fig_34_3()
    fig_34_4()
    fig_34_5()
