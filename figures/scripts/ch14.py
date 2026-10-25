"""Figures for Chapter 14 — Sequential Digital Systems.

Run from the repository root:  python figures/scripts/ch14.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.logic as logic  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

schemdraw.use("matplotlib")

RED = "#C62828"
GREEN = "#2E7D32"
BLUE = COLORS[0]


# ----------------------------------------------------------------------------
# timing-diagram helpers (self-contained copy for this chapter)
# ----------------------------------------------------------------------------
def wave(ax, y, t0, t1, edges, init=0, h=0.7, s=0.8, color=INK, lw=1.4, **kw):
    """Digital waveform. edges = [(t, level), ...]; 50 % crossing at t."""
    lev = init
    xs, ys = [t0], [y + lev * h]
    for t, new in edges:
        if new == lev:
            continue
        xs += [t - s / 2, t + s / 2]
        ys += [y + lev * h, y + new * h]
        lev = new
    xs.append(t1)
    ys.append(y + lev * h)
    ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="miter", **kw)


def bus(ax, y, segs, h=0.7, s=0.8, t0=None, t1=None, fs=8.5):
    """Bus waveform. segs = [(ta, tb, text, kind, color)], kind in valid/hatch/z."""
    for ta, tb, text, kind, col in segs:
        la = 0 if (t0 is not None and abs(ta - t0) < 1e-9) else s / 2
        lb = 0 if (t1 is not None and abs(tb - t1) < 1e-9) else s / 2
        pts = (([(ta, y + h / 2)] if la else []) + [(ta + la, y + h), (tb - lb, y + h)]
               + ([(tb, y + h / 2)] if lb else []) + [(tb - lb, y), (ta + la, y)])
        if kind == "hatch":
            ax.add_patch(Polygon(pts, closed=True, fc="white", ec=col or INK, lw=1.0,
                                 hatch="////", joinstyle="miter"))
        elif kind == "z":
            ax.plot([ta, tb], [y + h / 2] * 2, color=col or INK, lw=1.2)
        else:
            fc = "white"
            if col:
                fc = col + "22" if col.startswith("#") and len(col) == 7 else col
            ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=col or INK, lw=1.3,
                                 joinstyle="miter"))
        if text:
            bb = dict(fc="white", ec="none", pad=0.6) if kind == "hatch" else None
            ax.text((ta + tb) / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                    color=col or INK, bbox=bb)


def dim(ax, x0, x1, y, text, color=INK, fs=8, above=True, dy=0.08):
    """Horizontal dimension arrow with label."""
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.0, shrinkA=0, shrinkB=0,
                                mutation_scale=8))
    ax.text((x0 + x1) / 2, y + (dy if above else -dy), text, ha="center",
            va="bottom" if above else "top", fontsize=fs, color=color)


def place(d, cls, x, y, scale=1.3, **kw):
    """Add a schemdraw logic gate with its in1 anchor at (x, y)."""
    return d.add(cls(**kw).at((x, y)).anchor("in1").scale(scale))


def wire(ax, pts, color=INK, lw=1.2, **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", **kw)


def dot(ax, x, y, color=INK):
    ax.plot([x], [y], "o", ms=3.5, color=color)


def rows_axis(ax, labels, ys, h, x_lab, fs=9):
    for lab, y in zip(labels, ys):
        ax.text(x_lab, y + h / 2, lab, ha="right", va="center", fontsize=fs)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)


def dff(ax, x, y, name, w=1.6, h=1.8, clr=False, fs=8.5):
    """D flip-flop symbol, lower-left (x, y). Returns pin coordinates."""
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=INK, lw=1.2))
    ax.text(x + w / 2, y + h + 0.12, name, ha="center", va="bottom", fontsize=fs,
            fontweight="bold")
    ax.text(x + 0.12, y + h * 0.72, "D", va="center", fontsize=fs)
    ax.text(x + w - 0.12, y + h * 0.72, "Q", va="center", ha="right", fontsize=fs)
    ck = y + h * 0.28
    ax.plot([x, x + 0.22, x], [ck + 0.17, ck, ck - 0.17], color=INK, lw=1.1)
    pins = {"D": (x, y + h * 0.72), "Q": (x + w, y + h * 0.72), "CLK": (x, ck)}
    if clr:
        ax.add_patch(plt.Circle((x + w / 2, y - 0.08), 0.08, fc="white", ec=INK, lw=1.1))
        ax.text(x + w / 2, y + 0.12, "CLR", ha="center", va="bottom", fontsize=7)
        pins["CLR"] = (x + w / 2, y - 0.16)
    return pins


# ----------------------------------------------------------------------------
def fig_14_1():
    """NOR SR latch; D latch vs positive-edge D flip-flop."""
    fig = plt.figure(figsize=(6.6, 5.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.55], hspace=0.12)
    ax = fig.add_subplot(gs[0])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=9, lw=1.2)
    n1 = place(d, logic.Nor, 2.0, 3.0)
    n2 = place(d, logic.Nor, 2.0, 1.0)
    d.draw(show=False)
    q = n1.absanchors["out"]
    qb = n2.absanchors["out"]
    xt = q.x + 0.5
    s_y = n2.absanchors["in2"].y
    r2_y = n1.absanchors["in2"].y
    wire(ax, [(0.6, 3.0), (2.0, 3.0)])
    wire(ax, [(0.6, s_y), (2.0, s_y)])
    ax.text(0.5, 3.0, "R", ha="right", va="center", fontsize=10)
    ax.text(0.5, s_y, "S", ha="right", va="center", fontsize=10)
    wire(ax, [(q.x, q.y), (xt + 1.2, q.y)])
    wire(ax, [(qb.x, qb.y), (xt + 1.2, qb.y)])
    ax.text(xt + 1.3, q.y, "Q", va="center", fontsize=10)
    ax.text(xt + 1.3, qb.y, r"$\overline{Q}$", va="center", fontsize=10)
    # cross-coupling
    wire(ax, [(xt, q.y), (xt, 2.05), (1.5, 1.6), (1.5, 1.0), (2.0, 1.0)])
    dot(ax, xt, q.y)
    wire(ax, [(xt, qb.y), (xt, 1.3), (1.15, 1.95), (1.15, r2_y), (2.0, r2_y)])
    dot(ax, xt, qb.y)
    ax.text(8.2, 2.3, r"$Q^{+}=S+\overline{R}\,Q,\qquad SR=0$", fontsize=10.5, va="center")
    ax.text(8.2, 1.5, "S = R = 0: hold    S = 1: set    R = 1: reset", fontsize=8.5,
            va="center", color="#444444")
    ax.text(-0.4, 3.9, "(a) NOR SR latch", fontsize=9.5, fontweight="bold")
    ax.set_xlim(-0.6, 16.5)
    ax.set_ylim(-0.1, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")

    # ---------------- timing ----------------
    ax = fig.add_subplot(gs[1])
    h, s = 0.6, 0.9
    names = ["CLK", "D", r"Q$_{latch}$ (D latch)", r"Q$_{ff}$ (edge-triggered)"]
    ys = [4.5, 3.0, 1.5, 0.0]
    tsu, th = 2.0, 1.0
    rising = [10, 30, 50, 70, 90]
    for tr in rising:
        ax.add_patch(Rectangle((tr - tsu, -0.3), tsu + th, ys[0] + h + 0.5, fc="#FFE0B2",
                               ec="none", zorder=0))
        ax.plot([tr, tr], [-0.3, ys[0] + h + 0.2], color="#999999", lw=0.7, ls=":", zorder=0)
        ax.add_patch(Rectangle((tr, ys[2] - 0.15), 10, h + 0.3, fc="#E3F2FD", ec="none",
                               zorder=0))
    clk = []
    for tr in rising:
        clk += [(tr, 1)] + ([(tr + 10, 0)] if tr + 10 < 100 else [])
    wave(ax, ys[0], 0, 100, clk, init=0, h=h, s=s)
    dedges = [(14, 1), (22, 0), (26, 1), (44, 0), (63, 1)]
    wave(ax, ys[1], 0, 100, dedges, init=0, h=h, s=s, color=BLUE)
    # D latch: transparent while CLK high, 3 ns delay
    wave(ax, ys[2], 0, 100, [(17, 1), (53, 0), (73, 1)], init=0, h=h, s=s, color=COLORS[1])
    wave(ax, ys[3], 0, 100, [(33, 1), (53, 0), (73, 1)], init=0, h=h, s=s, color=COLORS[2])
    dim(ax, 14, 17, ys[2] + h + 0.12, "3 ns", fs=7.5)
    dim(ax, 30, 33, ys[3] + h + 0.12, "3 ns", fs=7.5)
    ax.text(100, ys[0] + h + 0.95, r"orange: setup ($t_{su}$) + hold ($t_h$) window",
            fontsize=7.5, ha="right", va="bottom", color="#B26A00")
    ax.text(100, ys[0] + h + 0.5, "blue: latch transparent (CLK high)", fontsize=7.5, ha="right",
            va="bottom", color="#1565C0")
    rows_axis(ax, names, ys, h, -2)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, ys[0] + h + 1.4)
    ax.set_xticks(range(0, 101, 10))
    ax.set_xlabel("Time (ns)")
    ax.text(0, ys[0] + h + 0.7, "(b) D latch vs positive-edge D flip-flop", fontsize=9.5,
            fontweight="bold", ha="left", va="bottom")
    save(fig, "14", "fig-14-1-latch-vs-flip-flop")


def fig_14_2():
    """Ripple vs synchronous counter, 7 -> 8."""
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    h, s = 0.5, 1.2
    dy = 0.85
    names = ["CLK", "Q0", "Q1", "Q2", "Q3", "count", "decode (count = 0)",
             "Q0", "Q1", "Q2", "Q3", "count"]
    ys = []
    y = 11.6
    for i in range(len(names)):
        if i == 7:
            y -= 0.6
        ys.append(y)
        y -= dy
    for t in range(0, 81, 10):
        ax.axvline(t, color=GRID, lw=0.6, zorder=0)
    ax.axvline(10, color="#888888", lw=0.9, ls=":", zorder=0)
    wave(ax, ys[0], 0, 80, [(10, 1), (35, 0), (60, 1)], init=0, h=h, s=s)
    # ripple
    t_r = [22, 34, 46, 58]
    for k in range(4):
        new = 1 if k == 3 else 0
        wave(ax, ys[1 + k], 0, 80, [(t_r[k], new)], init=1 - new, h=h, s=s, color=BLUE)
    segs = [(0, 22, "7", "valid", None), (22, 34, "6", "valid", RED), (34, 46, "4", "valid", RED),
            (46, 58, "0", "valid", RED), (58, 80, "8", "valid", None)]
    bus(ax, ys[5], segs, h=h, s=s, t0=0, t1=80)
    wave(ax, ys[6], 0, 80, [(46, 1), (58, 0)], init=0, h=h, s=s, color=RED)
    ax.text(60, ys[6] + h / 2, "glitch (false count 0)", ha="left", va="center", fontsize=8,
            color=RED)
    for k in range(4):
        dim(ax, (10 if k == 0 else t_r[k - 1]), t_r[k], ys[1 + k] + h + 0.08, "12 ns", fs=7,
            dy=0.0)
    # synchronous
    for k in range(4):
        new = 1 if k == 3 else 0
        wave(ax, ys[7 + k], 0, 80, [(30, new)], init=1 - new, h=h, s=s, color=COLORS[2])
    bus(ax, ys[11], [(0, 30, "7", "valid", None), (30, 80, "8", "valid", None)], h=h, s=s,
        t0=0, t1=80)
    dim(ax, 10, 30, ys[7] + h + 0.1, r"$t_{cq}$ = 20 ns", fs=7.5, dy=0.0)
    rows_axis(ax, names, ys, h, -1.5)
    ax.text(-27, (ys[1] + ys[6] + h) / 2, "Ripple counter\n(74HC393-like)", rotation=90,
            ha="center", va="center", fontsize=9, color=BLUE, fontweight="bold")
    ax.text(-27, (ys[7] + ys[11] + h) / 2, "Synchronous\n(74HC163-like)", rotation=90,
            ha="center", va="center", fontsize=9, color=COLORS[2], fontweight="bold")
    ax.plot([-31, 80], [ys[6] - 0.32] * 2, color="#AAAAAA", lw=0.8, clip_on=False)
    ax.set_xlim(0, 80)
    ax.set_ylim(ys[-1] - 0.4, ys[0] + h + 0.3)
    ax.set_xticks(range(0, 81, 10))
    ax.set_xlabel("Time (ns); clock edge at 10 ns")
    save(fig, "14", "fig-14-2-ripple-vs-synchronous-counter")


def fig_14_3():
    """FSM structure, Moore and Mealy."""
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ax.set_xlim(-0.2, 15.7)
    ax.set_ylim(0.6, 7.1)
    ax.set_aspect("equal")
    ax.axis("off")

    def arr(pts, col=INK, lw=1.3, ls="-"):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, ls=ls)
        ax.annotate("", xy=pts[-1], xytext=pts[-2],
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, shrinkA=0, shrinkB=0,
                                    mutation_scale=10))

    box(ax, 1.3, 3.4, 3.2, 2.0, "Next-state logic\n(combinational)", fontsize=8)
    ax.add_patch(Rectangle((5.9, 3.4), 2.8, 2.0, fc="#E8F5E9", ec=INK, lw=1.1))
    ax.text(7.3, 4.6, "State register\nk D flip-flops", ha="center", va="center", fontsize=8.5)
    ax.plot([7.05, 7.3, 7.55], [3.4, 3.65, 3.4], color=INK, lw=1.1)
    box(ax, 9.8, 3.4, 3.0, 2.0, "Output logic\n(combinational)", fontsize=8)
    ax.add_patch(FancyBboxPatch((13.2, 3.6), 1.8, 1.6, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="white", ec=INK, lw=1.1, ls="--"))
    ax.text(14.1, 4.4, "output\nregister\n(optional)", ha="center", va="center", fontsize=7.5)
    ax.text(14.1, 3.35, "registered outputs\n(Moore, glitch-free)", ha="center", va="top",
            fontsize=7.5, color="#444444")
    # inputs X
    arr([(0.0, 4.9), (1.3, 4.9)], lw=2.2)
    ax.text(-0.2, 5.05, "inputs X", fontsize=8, va="bottom")
    # NS bus (red: timing path)
    arr([(4.5, 4.4), (5.9, 4.4)], RED, 2.2)
    ax.text(5.2, 4.55, "NS[k−1:0]", fontsize=7.5, ha="center", va="bottom", color=RED)
    # PS out
    ax.plot([8.7, 9.2], [4.4, 4.4], color=RED, lw=2.2)
    arr([(9.2, 4.4), (9.8, 4.4)], INK, 2.2)
    ax.plot([9.2], [4.4], "o", ms=4.5, color=RED)
    ax.text(9.2, 4.55, "PS", fontsize=8.5, ha="center", va="bottom", color=RED)
    # feedback
    arr([(9.2, 4.4), (9.2, 2.3), (0.8, 2.3), (0.8, 3.9), (1.3, 3.9)], RED, 2.2)
    # outputs
    arr([(12.8, 4.4), (13.2, 4.4)], INK, 2.2)
    arr([(15.0, 4.4), (15.6, 4.4)], INK, 2.2)
    ax.text(15.6, 4.55, "Z", fontsize=10, ha="right", va="bottom")
    # Mealy dashed path
    ax.plot([0.4], [4.9], "o", ms=4, color=COLORS[1])
    arr([(0.4, 4.9), (0.4, 6.3), (11.3, 6.3), (11.3, 5.4)], COLORS[1], 1.3, "--")
    ax.text(5.8, 6.4, "Mealy only: inputs reach the output logic directly", fontsize=8.5,
            color=COLORS[1], ha="center", va="bottom")
    # clock and reset
    arr([(7.0, 1.4), (7.0, 3.4)], INK, 1.1)
    arr([(7.9, 1.4), (7.9, 3.4)], INK, 1.1)
    ax.text(6.9, 1.3, "CLK", fontsize=8.5, ha="right", va="center")
    ax.text(8.0, 1.3, "RST_n", fontsize=8.5, ha="left", va="center")
    ax.text(3.4, 2.15, r"register-to-register path (red):" "\n"
            r"$t_{cq}+t_{pd,\,\mathrm{next\ state}}+t_{su}\leq T$",
            fontsize=8.5, color=RED, ha="center", va="top")
    save(fig, "14", "fig-14-3-fsm-structure")


def fig_14_4():
    """Setup and hold at 250 MHz."""
    fig = plt.figure(figsize=(6.8, 5.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.75, 1.5], width_ratios=[2.6, 1.0],
                          hspace=0.12, wspace=0.08)
    ax = fig.add_subplot(gs[0, :])
    ax.set_xlim(-1.6, 16)
    ax.set_ylim(-0.4, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    p1 = dff(ax, 1.4, 1.1, "FF1")
    p2 = dff(ax, 12.0, 1.1, "FF2")
    xs = [4.3, 6.4, 8.5]
    yl = p1["Q"][1]
    for i, x in enumerate(xs):
        box(ax, x, yl - 0.45, 1.3, 0.9, f"LUT{i + 1}", fontsize=8.5)
    arrow(ax, p1["Q"][0], yl, xs[0], yl)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(ax, a + 1.3, yl, b, yl)
    arrow(ax, xs[2] + 1.3, yl, p2["D"][0], yl)
    ax.text(7.05, yl + 0.6, "3 LUT levels, 4 routed nets", ha="center",
            fontsize=8, va="bottom")
    # clock buffer
    bx, by = -0.6, 0.3
    ax.add_patch(Polygon([(bx, by - 0.3), (bx, by + 0.3), (bx + 0.55, by)], closed=True,
                         fc="white", ec=INK, lw=1.1))
    ax.text(bx - 0.1, by, "clock\nbuffer", fontsize=7.5, va="center", ha="right")
    ax.plot([bx + 0.55, 11.5], [by, by], color=INK, lw=1.1)
    ax.plot([0.8, 0.8, p1["CLK"][0]], [by, p1["CLK"][1], p1["CLK"][1]], color=COLORS[0], lw=1.4)
    ax.plot([11.5, 11.5, p2["CLK"][0]], [by, p2["CLK"][1], p2["CLK"][1]], color=COLORS[1],
            lw=1.4)
    ax.plot([0.8], [by], "o", ms=3.5, color=INK)
    ax.text(0.7, 1.15, "launch\nclock", fontsize=7.5, ha="right", va="center", color=COLORS[0])
    ax.text(11.35, 0.95, "capture clock\n(skew: 0.05 ns early)", fontsize=7.5, ha="right",
            va="center", color=COLORS[1])

    # ---------------- main timing ----------------
    ax = fig.add_subplot(gs[1, 0])
    h, s = 0.55, 0.12
    names = ["CLK_launch", "CLK_capture", "Q1", "D2"]
    ys = [4.2, 3.0, 1.8, 0.6]
    wave(ax, ys[0], -0.4, 9, [(0, 1), (2, 0), (4, 1), (6, 0), (8, 1)], init=0, h=h, s=s,
         color=COLORS[0])
    sk = -0.05
    wave(ax, ys[1], -0.4, 9, [(sk, 1), (2 + sk, 0), (4 + sk, 1), (6 + sk, 0), (8 + sk, 1)],
         init=0, h=h, s=s, color=COLORS[1])
    q1 = []
    t = -0.4
    for e in (0, 4, 8):
        q1 += [(t, e + 0.30, "", "valid", None), (e + 0.30, e + 0.42, "", "hatch", None)]
        t = e + 0.42
    q1.append((t, 9, "", "valid", None))
    bus(ax, ys[2], q1, h=h, s=s, t0=-0.4, t1=9)
    d2 = [(-0.4, 0.42, "", "valid", None), (0.42, 2.55, "changing", "hatch", None),
          (2.55, 4.42, "stable", "valid", GREEN), (4.42, 6.55, "changing", "hatch", None),
          (6.55, 8.42, "stable", "valid", None), (8.42, 9, "", "hatch", None)]
    bus(ax, ys[3], d2, h=h, s=s, t0=-0.4, t1=9, fs=7.5)
    ylo, yhi = ys[3] - 0.3, ys[0] + h + 0.15
    for e in (0, 4, 8):
        ax.plot([e, e], [ylo, yhi], color="#999999", lw=0.7, ls=":", zorder=0)
    ax.add_patch(Rectangle((3.80, ylo), 0.15, yhi - ylo, fc="#FFCDD2", ec="none", zorder=0))
    ax.plot([3.80, 3.80], [ylo, yhi], color=RED, lw=1.0, ls="--")
    ax.text(3.85, yhi + 0.05, "required\n3.80 ns", ha="left", va="bottom", fontsize=7.5,
            color=RED)
    ax.text(2.5, yhi + 0.05, "arrival\n2.55 ns", ha="right", va="bottom", fontsize=7.5,
            color=GREEN)
    ax.plot([2.55, 2.55], [ylo, yhi], color=GREEN, lw=1.0, ls="--")
    dim(ax, 2.55, 3.80, ys[3] - 0.3, "setup slack +1.25 ns", GREEN, fs=7.5, above=False)
    ax.text(0.5, ys[2] + h + 0.1, r"$t_{ccq}$ = 0.30, $t_{cq}$ = 0.42 ns", fontsize=7,
            va="bottom")
    ax.text(4.3, ys[3] - 0.85, "required = 4 − 0.05 skew − 0.10 uncertainty − 0.05 setup",
            fontsize=7, ha="center", va="top", color="#444444")
    rows_axis(ax, names, ys, h, -0.55, fs=8.5)
    ax.set_xlim(-0.4, 9)
    ax.set_ylim(-1.3, ys[0] + h + 1.6)
    ax.set_xticks(range(0, 10))
    ax.set_xlabel("Time (ns)")
    ax.text(-0.4, ys[0] + h + 1.6, "(a) setup check, worst path", fontsize=8.5,
            fontweight="bold", va="top")

    # ---------------- hold zoom ----------------
    ax = fig.add_subplot(gs[1, 1])
    s2 = 0.02
    ysz = [4.2, 3.0, 1.8]
    wave(ax, ysz[0], -0.1, 0.8, [(0, 1)], init=0, h=h, s=s2, color=COLORS[0])
    wave(ax, ysz[1], -0.1, 0.8, [(0.30, 1)], init=0, h=h, s=s2, color=COLORS[1])
    bus(ax, ysz[2], [(-0.1, 0.42, "old", "valid", None), (0.42, 0.8, "new", "valid", RED)],
        h=h, s=s2, t0=-0.1, t1=0.8, fs=7.5)
    yhi = ysz[0] + h + 0.15
    ax.add_patch(Rectangle((0.30, ysz[2] - 0.1), 0.15, yhi - ysz[2] + 0.1, fc="#FFCDD2",
                           ec="none", zorder=0))
    ax.text(0.375, yhi + 0.05, "hold\nwindow", ha="center", va="bottom", fontsize=7.5,
            color=RED)
    ax.text(0.43, ysz[2] - 0.15, "−0.03 ns", ha="center", va="top", fontsize=8, color=RED,
            fontweight="bold")
    dim(ax, 0.0, 0.30, ysz[1] - 0.2, "+0.30 skew", fs=7, above=False)
    ax.text(0.35, 0.95, "shortest path:\narrives 0.30 + 0.12\n= 0.42 ns; needs\n0.30 + 0.15"
            " = 0.45 ns", ha="center", va="top", fontsize=7, color="#444444")
    ax.set_xlim(-0.1, 0.8)
    ax.set_ylim(-1.3, ys[0] + h + 1.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks([0, 0.3, 0.6])
    ax.set_xlabel("Time (ns)")
    for lab, y in zip(["launch", "capture (hold path)", "D2, short path"], ysz):
        ax.text(0.79, y + h + 0.04, lab, ha="right", va="bottom", fontsize=6.5, color="#444444")
    ax.text(-0.08, ys[0] + h + 1.6, "(b) hold check", fontsize=8.5, fontweight="bold",
            va="top")
    save(fig, "14", "fig-14-4-setup-hold-timing")


def fig_14_5():
    """Metastable resolution and synchronizer MTBF."""
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.5))
    ax = axs[0]
    tau = 20e-12
    vdd = 0.9
    vm = vdd / 2
    t = np.linspace(0, 1.5e-9, 3001)
    tres = [0.12, 0.25, 0.4, 0.55, 0.72, 0.9, 1.1, 1.3]
    x_end = np.arctanh(0.4 / 0.45)
    for i, tr in enumerate(tres):
        sgn = 1 if i % 2 == 0 else -1
        v = vm + sgn * vm * np.tanh(x_end * np.exp((t - tr * 1e-9) / tau))
        ax.plot(t * 1e9, v, color=COLORS[i % 2], lw=1.3)
    env = vm * x_end * np.exp((t - 1.3e-9) / tau)
    m = env < 0.6
    ax.plot(t[m] * 1e9, vm + env[m], color="#777777", ls="--", lw=1.0)
    ax.plot(t[m] * 1e9, vm - env[m], color="#777777", ls="--", lw=1.0)
    ax.annotate(r"envelope $\propto e^{t/\tau}$, $\tau$ = 20 ps", xy=(1.25, 0.56),
                xytext=(0.15, 0.66), fontsize=8,
                arrowprops=dict(arrowstyle="-", color="#777777", lw=0.8))
    ax.set_xlim(0, 1.5)
    ax.set_ylim(-0.05, 0.98)
    ax.set_xlabel("Time after clock edge (ns)")
    ax.set_ylabel("Flip-flop output (V)")
    ax.set_title(r"Metastable resolution, $V_{DD}$ = 0.9 V", fontsize=10)
    ax.axhline(vm, color=GRID, lw=0.8, zorder=0)
    ax.text(0.02, 0.43, r"$V_{DD}/2$", fontsize=7.5, ha="left", va="top", color="#777777")

    ax = axs[1]
    t0, fclk, fdata = 100e-12, 125e6, 12.5e6
    tr = np.linspace(0, 2e-9, 801)
    for ta, ls, lab in ((20e-12, "-", r"$\tau$ = 20 ps"), (40e-12, "--", r"$\tau$ = 40 ps")):
        mt = np.exp(tr / ta) / (t0 * fclk * fdata)
        ax.semilogy(tr * 1e9, mt, ls=ls, color=COLORS[0], label=lab)
    for tt, val in ((0.3, 20.9), (1.0, 3.32e16)):
        ax.plot([tt], [val], "o", color=COLORS[1], ms=4.5)
    ax.annotate("20.9 s", (0.3, 20.9), xytext=(-6, 4), textcoords="offset points", fontsize=8,
                color=COLORS[1], va="bottom", ha="right")
    ax.annotate(r"3.3$\times10^{16}$ s", (1.0, 3.32e16), xytext=(6, -3),
                textcoords="offset points", fontsize=8, color=COLORS[1], va="top")
    ax.axhline(3.16e7, color=COLORS[2], lw=1.0, ls=":")
    ax.text(1.98, 3.16e7 * 2.0, "1 year", fontsize=8, ha="right", color=COLORS[2])
    ax.axhline(4.4e17, color=COLORS[3], lw=1.0, ls=":")
    ax.text(0.03, 4.4e17 * 2.0, "age of the universe", fontsize=8, ha="left", color=COLORS[3])
    ax.set_ylim(1, 1e30)
    ax.set_xlim(0, 2)
    ax.set_xlabel(r"Resolution time $t_r$ (ns)")
    ax.set_ylabel("MTBF (s)")
    ax.set_title("Synchronizer MTBF", fontsize=10)
    ax.set_yticks([1, 1e5, 1e10, 1e15, 1e20, 1e25, 1e30])
    ax.grid(True, which="major", alpha=0.5)
    ax.legend(loc="lower right", fontsize=8)
    ax.text(0.03, 0.97, r"$T_0$ = 100 ps, $f_{clk}$ = 125 MHz" "\n" r"$f_{data}$ = 12.5 MHz",
            transform=ax.transAxes, fontsize=7.5, ha="left", va="top")
    fig.tight_layout()
    save(fig, "14", "fig-14-5-metastability-resolution")


def fig_14_6():
    """Reset synchronizer and waveforms."""
    fig = plt.figure(figsize=(6.8, 5.8))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.9, 1.4], hspace=0.1)
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(-1.6, 16)
    ax.set_ylim(-0.1, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")
    pa = dff(ax, 3.2, 1.4, "FF_A", clr=True)
    pb = dff(ax, 7.2, 1.4, "FF_B", clr=True)
    # VCC to D of FF_A
    ax.plot([2.4, pa["D"][0]], [pa["D"][1]] * 2, color=INK, lw=1.2)
    ax.plot([2.4, 2.4], [pa["D"][1], pa["D"][1] + 0.5], color=INK, lw=1.2)
    ax.plot([2.15, 2.65], [pa["D"][1] + 0.5] * 2, color=INK, lw=1.4)
    ax.text(2.4, pa["D"][1] + 0.6, "VCC", ha="center", va="bottom", fontsize=8.5)
    # FF_A Q -> FF_B D
    ax.plot([pa["Q"][0], pb["D"][0]], [pa["Q"][1]] * 2, color=INK, lw=1.2)
    ax.text((pa["Q"][0] + pb["D"][0]) / 2, pa["Q"][1] + 0.08, "r1", ha="center", va="bottom",
            fontsize=8)
    # CLK
    yck = pa["CLK"][1]
    ax.plot([0.5, pa["CLK"][0]], [yck, yck], color=INK, lw=1.2)
    ax.plot([2.0, 2.0, 6.6, 6.6, pb["CLK"][0]], [yck, 0.95, 0.95, yck, yck], color=INK, lw=1.2)
    ax.plot([2.0], [yck], "o", ms=3.5, color=INK)
    ax.text(0.4, yck, "CLK", ha="right", va="center", fontsize=8.5)
    # reset
    yr = 0.35
    ax.plot([0.5, pb["CLR"][0]], [yr, yr], color=RED, lw=1.2)
    for p in (pa, pb):
        ax.plot([p["CLR"][0], p["CLR"][0]], [yr, p["CLR"][1]], color=RED, lw=1.2)
        ax.plot([p["CLR"][0]], [yr], "o", ms=3.5, color=RED)
    ax.text(0.4, yr, "RST_EXT_n", ha="right", va="center", fontsize=8.5, color=RED)
    # output and buffer tree
    yq = pb["Q"][1]
    ax.plot([pb["Q"][0], 11.0], [yq, yq], color=GREEN, lw=1.4)
    ax.text(9.9, yq + 0.1, "RST_SYNC_n", ha="center", va="bottom", fontsize=8, color=GREEN)

    def buf(x, y):
        ax.add_patch(Polygon([(x, y - 0.25), (x, y + 0.25), (x + 0.5, y)], closed=True,
                             fc="white", ec=INK, lw=1.1))
    buf(11.0, yq)
    ax.plot([11.5, 12.0], [yq, yq], color=INK, lw=1.2)
    for yy in (yq + 0.8, yq, yq - 0.8):
        ax.plot([12.0, 12.0, 12.4], [yq, yy, yy], color=INK, lw=1.2)
        buf(12.4, yy)
        ax.plot([12.9, 13.3], [yy, yy], color=INK, lw=1.2)
    ax.text(13.4, yq, "buffer tree\nto the design", va="center", fontsize=8.5)
    ax.text(-1.6, 4.25, "(a) Reset synchronizer: asynchronous assert, synchronous deassert",
            fontsize=9.5, fontweight="bold", va="top")

    # ---------------- timing ----------------
    ax = fig.add_subplot(gs[1])
    h, s = 0.55, 0.9
    names = ["CLK", "RST_EXT_n", "FF_A Q (r1)", "RST_SYNC_n"]
    ys = [4.0, 2.75, 1.5, 0.25]
    ce = []
    for k in range(0, 13):
        ce += [(10 * k, 1), (10 * k + 5, 0)]
    for k in range(0, 13):
        ax.axvline(10 * k, color=GRID, lw=0.6, zorder=0)
    wave(ax, ys[0], -2, 120, ce, init=0, h=h, s=s)
    ax.add_patch(Rectangle((56, ys[3] - 0.1), 4, ys[0] + h + 0.2 - ys[3], fc="#FFE0B2",
                           ec="none", zorder=0))
    ax.add_patch(Rectangle((60, ys[3] - 0.1), 2, ys[0] + h + 0.2 - ys[3], fc="#FFCDD2",
                           ec="none", zorder=0))
    ax.text(57.5, ys[0] + h + 0.15, "recovery", ha="right", va="bottom", fontsize=7.5,
            color="#B26A00")
    ax.text(60.5, ys[0] + h + 0.15, "removal", ha="left", va="bottom", fontsize=7.5, color=RED)
    wave(ax, ys[1], -2, 120, [(12, 0), (57, 1)], init=1, h=h, s=s, color=RED)
    # FF_A: async clear at 13, release resolves at 61 or 71
    wave(ax, ys[2], -2, 120, [(13, 0), (71, 1)], init=1, h=h, s=s, color=BLUE)
    ax.add_patch(Polygon([(61, ys[2]), (61, ys[2] + h), (71, ys[2] + h), (71, ys[2])],
                         closed=True, fc="none", ec=BLUE, hatch="////", lw=0.0))
    ax.text(66, ys[2] - 0.08, "may leave reset\nat the 60 ns edge", fontsize=7, ha="center",
            va="top", color=BLUE)
    wave(ax, ys[3], -2, 120, [(13, 0), (81, 1)], init=1, h=h, s=s, color=GREEN, lw=1.8)
    ax.add_patch(Polygon([(71, ys[3]), (71, ys[3] + h), (81, ys[3] + h), (81, ys[3])],
                         closed=True, fc="none", ec=GREEN, hatch="////", lw=0.0))
    ax.annotate("asynchronous assert\n(13 ns, no clock needed)", xy=(13.4, ys[3] + h / 2),
                xytext=(20, ys[3] + 0.75), fontsize=7.5, va="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=8))
    ax.annotate("release at 57 ns,\ninside recovery window", xy=(56.6, ys[1] + h / 2),
                xytext=(38, ys[1] + h / 2 + 0.1), fontsize=7.5, va="center", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8, mutation_scale=8),
                color=RED)
    dim(ax, 60, 80, ys[3] - 0.22, "two-cycle release latency", GREEN, fs=7.5, above=False)
    ax.text(84, ys[3] + h / 2, "released on the\n80 ns clock edge", fontsize=7.5, va="center",
            color=GREEN)
    rows_axis(ax, names, ys, h, -4, fs=8.5)
    ax.set_xlim(-2, 120)
    ax.set_ylim(-0.95, ys[0] + h + 0.6)
    ax.set_xticks(range(0, 121, 10))
    ax.set_xlabel("Time (ns)")
    save(fig, "14", "fig-14-6-reset-synchronizer")


if __name__ == "__main__":
    fig_14_1()
    fig_14_2()
    fig_14_3()
    fig_14_4()
    fig_14_5()
    fig_14_6()
