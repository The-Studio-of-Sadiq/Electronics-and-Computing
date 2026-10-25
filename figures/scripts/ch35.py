"""Figures for Chapter 35 — Hardware–Software Co-Design.

Run from the repository root:  python figures/scripts/ch35.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

RED = "#C62828"
BLUE = COLORS[0]
ORANGE = COLORS[1]
GREEN = COLORS[2]
PINK = COLORS[3]
YELLOW = COLORS[4]
SKY = COLORS[5]
GREY = "#777777"


def _canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# ----------------------------------------------------------------------------
# Figure 35.1 — task graph mapped onto an MCU + NPU SoC
# ----------------------------------------------------------------------------
def fig_35_1():
    fig, ax = _canvas(6.8, 5.0, (0, 14), (0, 10.3))

    ax.text(0.1, 10.05, "Task graph (one inference)", fontsize=9, weight="bold", va="center")
    tasks = [
        ("ADC\nacquisition\n4096\nsamples\n8 kB", "#E3F2FD"),
        ("window +\nFFT\n1024-point\n1.2 ms\non CPU", "#FFE0B2"),
        ("log-mel\nspectro-\ngram\n49 × 40 int8\n2 kB", "#FFE0B2"),
        ("CNN\ninference\n2.7 M MAC\n0.21 ms\non NPU", "#E8F5E9"),
        ("classifier\ndecision", "#FFE0B2"),
        ("radio\npacket\nBLE, 20 B", "#FFE0B2"),
    ]
    tw, th, ty = 1.62, 1.95, 7.55
    gap = (14 - 0.2 - 6 * tw) / 5
    tx = [0.1 + i * (tw + gap) for i in range(6)]
    for (t, fc), x in zip(tasks, tx):
        box(ax, x, ty, tw, th, t, fc=fc, fontsize=6.7)
    edges = ["8 kB", "≈1 kB\n/frame", "2 kB", "scores\n(bytes)", "20 B"]
    for i, e in enumerate(edges):
        x0, x1 = tx[i] + tw, tx[i + 1]
        arrow(ax, x0, ty + th / 2, x1, ty + th / 2)
        ax.text((x0 + x1) / 2, ty + th / 2 + 0.1, e, ha="center", va="bottom", fontsize=6.3)

    # SoC
    ax.add_patch(FancyBboxPatch((0.05, 0.25), 13.9, 4.6, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#FAFAFA", ec=GREY, lw=1.0))
    ax.text(0.25, 4.6, "Microcontroller SoC", fontsize=9, weight="bold", va="center")
    res = [
        ("ADC\nperipheral", "#E3F2FD"),
        ("DMA\ncontroller", "#E3F2FD"),
        ("Cortex-M\nCPU, DSP\ninstr., 16 kB\nI-cache", "#FFE0B2"),
        ("NPU\n128–256\nMAC/cycle", "#E8F5E9"),
        ("SRAM\n512 kB\n(banked)", "#EDE7F6"),
        ("Flash 2 MB\n(CNN\nweights)", "#EDE7F6"),
        ("BLE\nradio", "#FCE4EC"),
    ]
    rw, rh, ry = 1.6, 1.55, 2.35
    rgap = (13.6 - 7 * rw) / 6
    rx = [0.2 + i * (rw + rgap) for i in range(7)]
    for (t, fc), x in zip(res, rx):
        box(ax, x, ry, rw, rh, t, fc=fc, fontsize=6.7)
        ax.plot([x + rw / 2, x + rw / 2], [ry, 1.35], color=INK, lw=1.4)
    ax.add_patch(Rectangle((0.2, 0.75), 13.6, 0.6, fc="#CFD8DC", ec=INK, lw=0.9))
    ax.text(7.0, 1.05, "AXI / AHB interconnect", ha="center", va="center", fontsize=8)

    # mapping arrows
    def cx(i):
        return tx[i] + tw / 2

    def rx_(j):
        return rx[j] + rw / 2

    maps = [
        (0, 0, BLUE, -0.25), (0, 1, BLUE, 0.25),
        (1, 2, ORANGE, -0.3), (2, 2, ORANGE, 0.0), (4, 2, ORANGE, 0.3),
        (3, 3, GREEN, 0.0),
        (5, 2, PINK, 0.45), (5, 6, PINK, 0.25),
    ]
    for (i, j, col, off) in maps:
        x0 = cx(i) + (off if i in (0, 5) else 0)
        x1 = rx_(j) + (off if j == 2 else 0)
        ax.annotate("", xy=(x1, ry + rh + 0.02), xytext=(x0, ty - 0.02),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.2, ls=(0, (4, 2.5)),
                                    shrinkA=0, shrinkB=0, mutation_scale=10))
    ax.text(10.0, 4.55, "Amdahl: FFT on CPU now dominates\n(1.2 ms of 1.5 ms)",
            ha="center", va="center", fontsize=7.6, color=RED,
            bbox=dict(fc="white", ec=RED, lw=0.8, boxstyle="round,pad=0.3"))
    save(fig, "35", "fig-35-1-task-graph-partitioning")


# ----------------------------------------------------------------------------
# Figure 35.2 — energy per operation
# ----------------------------------------------------------------------------
def fig_35_2():
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    items = [
        ("8-bit int add", 0.03, None, "a"),
        ("32-bit int add", 0.1, None, "a"),
        ("8-bit int multiply", 0.2, None, "a"),
        ("16-bit FP multiply", 1.1, None, "a"),
        ("32-bit int multiply", 3.1, None, "a"),
        ("32-bit FP multiply", 3.7, None, "a"),
        ("64-bit read, 8 kB SRAM", 10, None, "s"),
        ("64-bit read, 32 kB SRAM", 20, None, "s"),
        ("64-bit read, 1 MB SRAM", 100, None, "s"),
        ("64-bit DRAM access (45 nm era)", 1300, 2600, "d"),
        ("64-bit LPDDR5 / HBM (modern)", 200, 500, "m"),
    ]
    col = {"a": BLUE, "s": GREEN, "d": ORANGE, "m": ORANGE}
    base = 0.01
    n = len(items)
    for k, (name, v, v2, kind) in enumerate(items):
        y = n - 1 - k
        if kind == "m":
            ax.barh(y, v2 - v, left=v, height=0.62, fc="white", ec=ORANGE, hatch="////",
                    lw=1.0)
            ax.text(v2 * 1.25, y, f"{v:g}–{v2:g}", va="center", fontsize=8)
        elif v2:
            ax.barh(y, v - base, left=base, height=0.62, color=col[kind])
            ax.barh(y, v2 - v, left=v, height=0.62, color=col[kind], alpha=0.4)
            ax.text(v2 * 1.25, y, f"{v:g}–{v2:g}", va="center", fontsize=8)
        else:
            ax.barh(y, v - base, left=base, height=0.62, color=col[kind])
            ax.text(v * 1.25, y, f"{v:g}", va="center", fontsize=8)
    ax.set_yticks(range(n))
    ax.set_yticklabels([it[0] for it in items][::-1], fontsize=8.2)
    ax.set_xscale("log")
    ax.set_xlim(0.01, 10000)
    ax.set_xlabel("Energy per operation (pJ, log scale)")
    ax.grid(True, axis="x", which="major", lw=0.5)
    ax.set_axisbelow(True)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="arithmetic"),
                       Patch(color=GREEN, label="SRAM access"),
                       Patch(color=ORANGE, label="DRAM access (light = range)"),
                       Patch(fc="white", ec=ORANGE, hatch="////", label="modern DRAM interface")],
              loc="upper right", fontsize=7.6)
    ax.text(0.99, 1.01, "45 nm, 0.9 V (after Horowitz, ISSCC 2014)", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7.6, color=GREY)
    fig.tight_layout()
    save(fig, "35", "fig-35-2-energy-per-operation")


# ----------------------------------------------------------------------------
# Figure 35.3 — roofline
# ----------------------------------------------------------------------------
def _ops_fmt(v, _pos=None):
    if v >= 1e12:
        return f"{v / 1e12:g} TOPS"
    if v >= 1e9:
        return f"{v / 1e9:g} GOPS"
    return f"{v / 1e9:g} GOPS"


def fig_35_3():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    I = np.logspace(np.log10(0.5), np.log10(2000), 400)
    plats = [
        ("Data-centre GPU: 2.0 TB/s, 624 TOPS", 624e12, 2.0e12, BLUE, 2.0),
        ("MCU-class NPU: 4 GB/s, 256 GOPS", 256e9, 4e9, GREEN, 2.0),
        ("Cortex-M4 MCU: 0.32 GOPS", 0.32e9, 0.32e9, GREY, 1.1),
    ]
    for name, pk, bw, c, lw in plats:
        P = np.minimum(pk, bw * I)
        ax.plot(I, P, color=c, lw=lw, label=name)
        ridge = pk / bw
        if ridge > 2:
            Ir = I[I <= ridge]
            ax.fill_between(Ir, 1e8, bw * Ir, color=c, alpha=0.08, lw=0)
            ax.plot([ridge], [pk], "o", ms=4, color=c)
            ax.annotate(f"ridge {ridge:g} ops/B", (ridge, pk), xytext=(-6, 5),
                        textcoords="offset points", fontsize=7.4, color=c, ha="right")
    ax.text(0.6, 3e11, "memory-bound\n(GPU)", fontsize=7.4, color=BLUE, va="center")
    ax.text(2.6, 1.6e9, "memory-bound (NPU)", fontsize=7.4, color=GREEN, va="center")
    kernels = [("GEMV\nbatch 1", 2.0), ("depthwise\nconv", 9.0), ("3×3 conv\n64 ch", 528.0),
               ("GEMM\n1024³", 683.0)]
    for kname, ai in kernels:
        ax.axvline(ai, color=GREY, lw=0.8, ls="--", zorder=0)
        for _, pk, bw, c, _lw in plats:
            ax.plot(ai, min(pk, bw * ai), "o", ms=5, color=c, mec="white", mew=0.8, zorder=5)
    # kernel labels at the top
    for kname, ai in kernels:
        ha = "right" if ai == 528.0 else "left"
        dx = 0.92 if ha == "right" else 1.08
        ax.text(ai * dx, 3.2e14 if ai != 683.0 else 3.2e14, kname, ha=ha, va="top",
                fontsize=7.2, color=INK)
    # call-outs
    ax.annotate("GEMV on GPU: 4 TOPS\n(0.6 % of peak)", (2.0, 4e12), xytext=(0.56, 2.2e13),
                fontsize=7.4, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate("GEMV on NPU:\n8 GOPS (3.1 %)", (2.0, 8e9), xytext=(0.56, 3.5e10),
                fontsize=7.4, color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ax.annotate("depthwise on NPU:\n36 GOPS (14 %)", (9.0, 36e9), xytext=(13, 3.5e9),
                fontsize=7.4, color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.5, 2000)
    ax.set_ylim(1e8, 1e15)
    ticks = [1e8, 1e9, 1e10, 1e11, 1e12, 1e13, 1e14, 1e15]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_major_formatter(FuncFormatter(_ops_fmt))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v:g}"))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.tick_params(labelsize=8)
    ax.set_xlabel("Arithmetic intensity (ops per byte from main memory)")
    ax.set_ylabel("Attainable throughput (int8 ops/s)")
    ax.grid(True, which="major", lw=0.4)
    ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.37), fontsize=7.4)
    fig.tight_layout()
    save(fig, "35", "fig-35-3-roofline")


# ----------------------------------------------------------------------------
# Figure 35.4 — int8 quantised layer
# ----------------------------------------------------------------------------
def _numline(ax, x0, x1, y, rlab, qlab, rticks, qticks, title):
    ax.plot([x0, x1], [y, y], color=INK, lw=1.2)
    ax.plot([x0, x1], [y - 1.0, y - 1.0], color=INK, lw=1.2)
    for (pos, r), (_, q) in zip(rticks, qticks):
        xx = x0 + pos * (x1 - x0)
        ax.plot([xx, xx], [y - 0.08, y + 0.08], color=INK, lw=1)
        ax.plot([xx, xx], [y - 1.08, y - 0.92], color=INK, lw=1)
        ax.plot([xx, xx], [y - 0.12, y - 0.88], color=GREY, lw=0.6, ls=":")
        ax.text(xx, y + 0.15, r, ha="center", va="bottom", fontsize=6.8)
        ax.text(xx, y - 1.15, q, ha="center", va="top", fontsize=6.8)
    ax.text(x0 - 0.1, y, rlab, ha="right", va="center", fontsize=7, color=BLUE)
    ax.text(x0 - 0.1, y - 1.0, qlab, ha="right", va="center", fontsize=7, color=ORANGE)
    ax.text((x0 + x1) / 2, y + 0.75, title, ha="center", va="bottom", fontsize=7.4)


def fig_35_4():
    fig = plt.figure(figsize=(6.8, 5.0))
    ax = fig.add_axes([0.0, 0.0, 0.70, 1.0])
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 11)
    ax.set_aspect("equal")
    ax.axis("off")

    # left: affine mappings
    ax.text(2.0, 10.6, "Affine mapping r = S (q − Z)", ha="center", fontsize=8, weight="bold")
    _numline(ax, 0.75, 3.3, 8.6, "r", "q",
             [(0, "−0.52"), (0.5, "0"), (1, "+0.52")], [(0, "−127"), (0.5, "0"), (1, "+127")],
             "weights (example layer): symmetric, Z = 0\nS_w = 0.0041")
    _numline(ax, 0.75, 3.3, 5.2, "r", "q",
             [(0, "0"), (0.5, "1.0"), (1, "2.0")], [(0, "0"), (0.5, "128"), (1, "255")],
             "activations: asymmetric\nS_x = 2/255")
    ax.text(2.0, 2.5, "integer arithmetic only:\nproducts exact in int32;\n"
            "rescale by\nM = S_w S_x / S_y\n= M0 · 2^-31 · 2^-n", ha="center", va="center",
            fontsize=7, color=INK,
            bbox=dict(fc="#F5F5F5", ec=GREY, lw=0.6, boxstyle="round,pad=0.3"))

    # centre: datapath
    cx0, cw = 4.75, 4.3
    ax.text(cx0 + cw / 2, 10.6, "Datapath of one output", ha="center", fontsize=8,
            weight="bold")
    box(ax, cx0, 9.55, 2.05, 0.7, "int8 activations\nq_x", fc="#E3F2FD", fontsize=6.5)
    box(ax, cx0 + 2.25, 9.55, 2.05, 0.7, "int8 weights\nq_w", fc="#FFE0B2", fontsize=6.5)
    steps = [
        ("subtract zero point: q_x − Z_x", "#EEF3F8"),
        ("8 × 8-bit multipliers", "#EEF3F8"),
        ("int32 accumulator  Σ", "#E8F5E9"),
        ("× M0 = 1 803 199 070 (Q31)", "#FFF3E0"),
        ("rounding right shift by 9", "#FFF3E0"),
        ("+ output zero point Z_y", "#EEF3F8"),
        ("saturate to int8 [−128, 127]", "#EEF3F8"),
    ]
    sh, sy0, step = 0.68, 8.45, 1.08
    ys = [sy0 - i * step for i in range(len(steps))]
    for (t, fc), y in zip(steps, ys):
        box(ax, cx0, y, cw, sh, t, fc=fc, fontsize=6.8)
    xa = cx0 + 1.0
    arrow(ax, xa, 9.55, xa, ys[0] + sh)
    # weights skip the zero-point subtraction (Z_w = 0) and go straight to the multipliers
    xw = cx0 + 3.27
    ax.plot([xw, xw], [9.55, ys[0] + sh + 0.12], color=INK, lw=1.1)
    ax.plot([xw, cx0 + cw + 0.25, cx0 + cw + 0.25], [ys[0] + sh + 0.12] * 2 +
            [ys[1] + sh / 2], color=INK, lw=1.1)
    arrow(ax, cx0 + cw + 0.25, ys[1] + sh / 2, cx0 + cw, ys[1] + sh / 2)
    ax.text(cx0 + cw + 0.35, ys[0] + sh / 2 - 0.05, "Z_w = 0", fontsize=6.5, color=GREY,
            va="center")
    for i in range(len(steps) - 1):
        arrow(ax, cx0 + cw / 2, ys[i], cx0 + cw / 2, ys[i + 1] + sh)
    # bias input (right side)
    arrow(ax, cx0 + cw + 0.55, ys[2] + sh / 2, cx0 + cw, ys[2] + sh / 2)
    ax.text(cx0 + cw + 0.6, ys[2] + sh / 2, "bias\n(int32)", ha="left", va="center",
            fontsize=6.6)
    # next layer
    ax.text(cx0 + cw / 2, ys[-1] - 0.3, "int8 output → next layer", ha="center", va="top",
            fontsize=7)
    arrow(ax, cx0 + cw / 2, ys[-1], cx0 + cw / 2, ys[-1] - 0.28)
    ax.text(cx0 + cw + 0.12, (ys[3] + ys[4]) / 2 + sh / 2, "e.g. acc\n12345 → 20\n(exact\n20.25)",
            fontsize=6.3, color=GREY, va="center")

    # right: bar chart
    bx = fig.add_axes([0.775, 0.17, 0.215, 0.6])
    labels = ["output\nSQNR", "worst-\nchannel\nweight\nSQNR"]
    pt = [40.8, 15.3]
    pc = [46.5, 43.0]
    x = np.arange(2)
    w = 0.38
    b1 = bx.bar(x - w / 2, pt, w, color=GREY, label="per-tensor")
    b2 = bx.bar(x + w / 2, pc, w, color=BLUE, label="per-channel")
    for bars in (b1, b2):
        for b in bars:
            bx.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8, f"{b.get_height():.1f}",
                    ha="center", va="bottom", fontsize=6.6)
    bx.set_xticks(x)
    bx.set_xticklabels(labels, fontsize=6.8)
    bx.set_ylabel("SQNR (dB)", fontsize=8)
    bx.set_ylim(0, 62)
    bx.tick_params(axis="y", labelsize=7)
    bx.legend(fontsize=6.8, loc="upper left", bbox_to_anchor=(0.0, 1.0))
    bx.set_title("Weight scales", fontsize=8, weight="bold", pad=8)
    save(fig, "35", "fig-35-4-int8-quantised-layer")


# ----------------------------------------------------------------------------
# Figure 35.5 — pipelined camera latency
# ----------------------------------------------------------------------------
STAGES = [("ISP", 8.0), ("DMA", 1.2), ("NPU inference", 14.0), ("CPU tracking", 3.0),
          ("CAN-FD", 1.0)]
FCOL = [BLUE, GREEN, PINK]


def _pipeline(ax, npu=(14.0, 14.0, 14.0), highlight=None, title=""):
    lanes = {name: 4 - i for i, (name, _) in enumerate(STAGES)}
    period = 100.0 / 3.0
    ends = []
    for f in range(3):
        t = f * period
        for (name, d) in STAGES:
            if name == "NPU inference":
                d = npu[f]
            y = lanes[name]
            red = highlight == f
            ec = RED if (red and name == "NPU inference") else INK
            lw = 1.6 if (red and name == "NPU inference") else 0.6
            ax.add_patch(Rectangle((t, y - 0.34), d, 0.68, fc=FCOL[f], ec=ec, lw=lw,
                                   alpha=0.85 if (highlight is None or red) else 0.35))
            if d > 2.5:
                ax.text(t + d / 2, y, f"F{f + 1}" + (f" {d:g} ms" if d >= 8 else ""),
                        ha="center", va="center", fontsize=6.8, color="white", weight="bold")
            t += d
        ends.append(t)
        dl = (f + 1) * period
        ax.plot([dl, dl], [-0.55, 4.5], color=RED if red else GREY, lw=1.0, ls="--")
    for name, y in lanes.items():
        ax.text(-1.2, y, name, ha="right", va="center", fontsize=7.6)
    for k in range(3):
        ax.plot([k * period] * 2, [-0.55, -0.3], color=INK, lw=1.2)
    ax.set_xlim(0, 101)
    ax.set_ylim(-0.75, 6.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 33.3, 66.7, 100])
    ax.tick_params(labelsize=8, labelbottom=True)
    ax.set_title(title, fontsize=9, loc="left")
    return ends


def fig_35_5():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.0), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.98, hspace=0.38, top=0.95, bottom=0.09)
    ends = _pipeline(a1, title="(a) Nominal: frame every 33.3 ms (30 fps)")
    # brackets
    a1.annotate("", xy=(ends[0], 4.85), xytext=(0, 4.85),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=7))
    a1.text(ends[0] / 2, 4.9, f"latency {ends[0]:.1f} ms", ha="center", va="bottom", fontsize=7.6)
    p = 100 / 3
    a1.annotate("", xy=(p, 5.5), xytext=(0, 5.5),
                arrowprops=dict(arrowstyle="<|-|>", color=GREY, lw=0.9, mutation_scale=7))
    a1.text(0.5 * p, 5.55, "frame period 33.3 ms", ha="center", va="bottom", fontsize=7.6,
            color=GREY)
    a1.text(p - 0.4, 4.25, "deadline F1", fontsize=6.6, color=GREY, ha="right")
    a1.text(2 * p - 0.4, 4.25, "deadline F2", fontsize=6.6, color=GREY, ha="right")
    a1.text(99.4, 4.25, "deadline F3", fontsize=6.6, color=GREY, ha="right")

    ends2 = _pipeline(a2, npu=(14.0, 14.0, 20.0), highlight=2,
                      title="(b) DRAM contention: F3 inference stretched to 20 ms")
    a2.annotate("", xy=(ends2[2], 4.85), xytext=(2 * p, 4.85),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.9, mutation_scale=7))
    a2.text(2 * p + (ends2[2] - 2 * p) / 2, 4.9,
            f"F3 latency {ends2[2] - 2 * p:.1f} ms: 0.1 ms before its deadline",
            ha="center", va="bottom", fontsize=7.6, color=RED)
    a2.text(99.4, 4.25, "deadline F3", fontsize=6.6, color=RED, ha="right")
    a2.set_xlabel("Time (ms)")
    save(fig, "35", "fig-35-5-pipelined-camera-latency")


# ----------------------------------------------------------------------------
# Figure 35.6 — virtual prototype with RTL co-simulation
# ----------------------------------------------------------------------------
def fig_35_6():
    fig = plt.figure(figsize=(6.8, 5.0))
    ax = fig.add_axes([0.0, 0.3, 1.0, 0.7])
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7.3)
    ax.set_aspect("equal")
    ax.axis("off")

    def panel(x, y, w, h, title, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.2",
                                    fc=fc, ec=INK, lw=1.1))
        ax.text(x + w / 2, y + h - 0.3, title, ha="center", va="center", fontsize=8.2,
                weight="bold")

    # virtual prototype
    panel(0.1, 0.2, 5.2, 6.9, "Virtual prototype\n(SystemC TLM-2.0)", "#EEF3F8")
    box(ax, 0.4, 4.85, 4.6, 1.15, "CPU instruction-set simulator\nrunning Linux driver\n+ application",
        fc="white", fontsize=7.4)
    ax.add_patch(Rectangle((0.4, 3.85), 4.6, 0.5, fc="#CFD8DC", ec=INK, lw=0.9))
    ax.text(2.7, 4.1, "TLM interconnect", ha="center", va="center", fontsize=7.4)
    ax.plot([2.7, 2.7], [4.85, 4.35], color=INK, lw=1.2)
    box(ax, 0.4, 2.4, 1.4, 0.95, "memory\nmodel", fc="white", fontsize=7.2)
    box(ax, 1.95, 2.4, 1.4, 0.95, "UART /\ntimer\nmodels", fc="white", fontsize=7.0)
    box(ax, 3.5, 2.4, 1.5, 0.95, "accelerator\nproxy\nsocket", fc="#FFF3E0", fontsize=7.0)
    for xx in (1.1, 2.65, 4.25):
        ax.plot([xx, xx], [3.85, 3.35], color=INK, lw=1.2)
    ax.text(2.7, 1.2, "fast: boots Linux in ~10 s;\nregister-accurate, untimed",
            ha="center", va="center", fontsize=7, color=GREY)

    # HDL simulator
    panel(6.0, 1.6, 3.6, 5.5, "HDL simulator", "#E8F5E9")
    box(ax, 6.3, 3.95, 3.0, 1.6, "accelerator RTL\n(NPU, or FIR of\nListing 35.1)", fc="white",
        fontsize=7.4)
    box(ax, 6.3, 2.0, 3.0, 1.0, "AXI transactor", fc="white", fontsize=7.4)
    ax.annotate("", xy=(7.8, 3.95), xytext=(7.8, 3.0),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.0, mutation_scale=8))
    ax.text(7.9, 3.47, "AXI bursts", fontsize=6.8, va="center")
    # bridge
    box(ax, 4.85, 0.35, 1.9, 0.8, "TLM-to-AXI\nbridge", fc="#FFF3E0", fontsize=7.0)
    ax.plot([4.25, 4.25, 4.85], [2.4, 0.75, 0.75], color=ORANGE, lw=1.3)
    ax.plot([6.75, 7.8, 7.8], [0.75, 0.75, 2.0], color=ORANGE, lw=1.3)
    ax.text(3.0, 0.5, "register writes,\nDMA descriptors", fontsize=6.8, color=ORANGE,
            ha="center", va="center")

    # golden reference
    panel(10.3, 0.2, 4.6, 6.9, "Golden reference", "#FFF8E1")
    box(ax, 10.6, 4.75, 4.0, 1.25, "Python / NumPy bit-exact\nint8 model (as Listing 35.3)",
        fc="white", fontsize=7.2)
    box(ax, 10.6, 3.2, 4.0, 1.05, "C reference model\ncalled through DPI-C", fc="white",
        fontsize=7.2)
    box(ax, 10.6, 1.2, 4.0, 1.4, "scoreboard: compare\nevery output tensor\n(bit-exact, pass/fail)",
        fc="#FFE0B2", fontsize=7.2)
    arrow(ax, 12.6, 4.75, 12.6, 4.25)
    ax.annotate("", xy=(12.6, 2.6), xytext=(12.6, 3.2),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=10))
    ax.text(12.7, 2.9, "expected outputs", fontsize=6.8, va="center")
    # RTL outputs to scoreboard
    ax.plot([9.3, 9.95, 9.95], [4.4, 4.4, 1.9], color=GREEN, lw=1.2)
    arrow(ax, 9.95, 1.9, 10.6, 1.9, color=GREEN)
    ax.text(10.08, 3.15, "actual outputs", fontsize=6.8, color=GREEN, ha="center",
            va="center", rotation=90)

    # speed strip
    sx = fig.add_axes([0.08, 0.1, 0.88, 0.14])
    pts = [(500, "RTL simulation\n500 Hz", "46 days"),
           (1e6, "emulation\n1 MHz", "33 min"),
           (20e6, "FPGA\nprototype\n20 MHz", "100 s"),
           (200e6, "virtual\nprototype\n200 MIPS", "10 s")]
    sx.set_xscale("log")
    sx.set_xlim(100, 2e9)
    sx.set_ylim(0, 1)
    sx.set_yticks([])
    for s in ("left", "right", "top"):
        sx.spines[s].set_visible(False)
    sx.add_patch(Rectangle((100, 0.45), 2e9 - 100, 0.25, fc="#ECEFF1", ec="none"))
    cols = [RED, ORANGE, GREEN, BLUE]
    for (v, lab, boot), c in zip(pts, cols):
        sx.plot(v, 0.575, "o", ms=8, color=c, zorder=3)
        sx.text(v, 0.82, lab, ha="center", va="bottom", fontsize=7.2)
        sx.text(v, 0.25, f"boot {boot}", ha="center", va="center", fontsize=7.2, color=c,
                weight="bold")
    sx.set_xticks([1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9])
    sx.tick_params(labelsize=7.5)
    sx.set_xlabel("Simulated speed (cycles or instructions per second); Linux boot ≈ 2 × 10⁹ instructions",
                  fontsize=8)
    save(fig, "35", "fig-35-6-virtual-prototype-cosimulation")


if __name__ == "__main__":
    fig_35_1()
    fig_35_2()
    fig_35_3()
    fig_35_4()
    fig_35_5()
    fig_35_6()
