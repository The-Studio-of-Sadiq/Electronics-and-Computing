"""Figures for Chapter 19 — Hardware Description Languages.

Run from the repository root:  python figures/scripts/ch19.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, Circle, FancyArrowPatch  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
RED = "#C0392B"
VER_FC = "#E3F2E6"     # verification stream tint
IMP_FC = "#DCEBF7"     # implementation stream tint
SRC_FC = "#FFF4D6"     # source / constraints tint


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def wire(ax, pts, color=INK, lw=1.2, ls="-", **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", **kw)


def wire_arrow(ax, pts, color=INK, lw=1.2, ls="-", ms=10):
    if len(pts) > 2:
        wire(ax, pts[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def digital(ax, y, t0, t1, edges, init=0, h=0.6, color=INK, lw=1.4):
    """Digital waveform at baseline y between t0 and t1, toggling at the given edge times."""
    xs, ys = [t0], [y + h * init]
    lev = init
    for t in edges:
        xs += [t, t]
        ys += [y + h * lev, y + h * (1 - lev)]
        lev = 1 - lev
    xs.append(t1)
    ys.append(y + h * lev)
    ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="miter")


def bus(ax, y, segs, h=0.6, s=0.12, color=INK, fs=8):
    """Bus waveform: segs = [(t0, t1, kind, label)], kind 'valid' or 'x' (hatched)."""
    for t0, t1, kind, lab in segs:
        top, bot = y + h, y
        poly = [(t0, y + h / 2), (t0 + s, top), (t1 - s, top), (t1, y + h / 2),
                (t1 - s, bot), (t0 + s, bot)]
        if kind == "x":
            ax.add_patch(Polygon(poly, closed=True, fc="#EEEEEE", ec=INK, lw=1.0,
                                 hatch="////"))
        else:
            ax.add_patch(Polygon(poly, closed=True, fc="white", ec=INK, lw=1.2))
        if lab:
            ax.text((t0 + t1) / 2, y + h / 2, lab, ha="center", va="center", fontsize=fs)


def dim(ax, x0, x1, y, text, color=INK, fs=8, above=True):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=1.0,
                                shrinkA=0, shrinkB=0, mutation_scale=7))
    ax.text((x0 + x1) / 2, y + (0.07 if above else -0.07), text, ha="center",
            va="bottom" if above else "top", fontsize=fs, color=color)


# ----------------------------------------------------------------------------
# Figure 19.1 — HDL design flow
# ----------------------------------------------------------------------------
def fig_19_1():
    fig, ax = schematic(6.8, 5.4, xlim=(0, 11.0), ylim=(0, 8.75))
    # top source and constraints
    box(ax, 3.2, 7.75, 4.2, 0.8, "RTL source\n(SystemVerilog / VHDL)", fc=SRC_FC, fontsize=9)
    box(ax, 8.2, 7.8, 2.4, 0.7, "Constraints\n(SDC / XDC)", fc=SRC_FC, fontsize=8.5)

    lx, rx, wl, wr, h = 1.95, 7.95, 3.3, 3.9, 0.72
    left = ["Test bench +\nreference model", "RTL simulation",
            "Assertions and coverage", "Regression"]
    ly = [6.3, 4.95, 3.6, 2.25]
    right = ["Synthesis", "Technology mapping\n(LUT, FF, CARRY, DSP, BRAM)",
             "Place and route", "Static timing analysis\n(WNS, WHS)", "Bitstream or GDSII"]
    ry = [6.3, 5.2, 4.1, 3.0, 1.9]
    for t, y in zip(left, ly):
        box(ax, lx - wl / 2, y - h / 2, wl, h, t, fc=VER_FC, fontsize=8.5)
    for t, y in zip(right, ry):
        box(ax, rx - wr / 2, y - h / 2, wr, h, t, fc=IMP_FC, fontsize=8.5)
    for a, b in zip(ly[:-1], ly[1:]):
        wire_arrow(ax, [(lx, a - h / 2), (lx, b + h / 2)])
    for a, b in zip(ry[:-1], ry[1:]):
        wire_arrow(ax, [(rx, a - h / 2), (rx, b + h / 2)])
    # RTL source to both streams, constraints to implementation
    wire_arrow(ax, [(4.3, 7.75), (4.3, 7.2), (lx, 7.2), (lx, ly[0] + h / 2)])
    wire_arrow(ax, [(6.3, 7.75), (6.3, 7.2), (rx - 0.4, 7.2), (rx - 0.4, ry[0] + h / 2)])
    wire_arrow(ax, [(9.4, 7.8), (9.4, 7.2), (rx + 0.4, 7.2), (rx + 0.4, ry[0] + h / 2)])

    # dashed cross-links
    xa, xb = lx + wl / 2, rx - wr / 2
    ax.annotate("", xy=(xa, 4.95), xytext=(xb, 4.95),
                arrowprops=dict(arrowstyle="<|-|>", color=PINK, lw=1.2, ls="--",
                                mutation_scale=9, shrinkA=0, shrinkB=0))
    ax.text((xa + xb) / 2, 5.05, "formal equivalence /\ngate-level\nsimulation",
            ha="center", va="bottom", fontsize=7.8, color=PINK)
    xm = (xa + xb) / 2
    wire(ax, [(xb, 1.9), (xm, 1.9), (xm, 2.25)], ls="--", color=PINK, lw=1.2)
    ax.annotate("", xy=(xa, 2.25), xytext=(xm, 2.25),
                arrowprops=dict(arrowstyle="-|>", color=PINK, lw=1.2, ls="--",
                                mutation_scale=9, shrinkA=0, shrinkB=0))
    ax.text(xm, 1.75, "on-chip debug\n(ILA)", ha="center", va="top", fontsize=7.8,
            color=PINK)
    # run times
    for y, t in [(6.3, "2-10 min"), (4.1, "5-60 min")]:
        ax.text(rx + wr / 2 + 0.08, y, t, fontsize=7.5, va="center",
                color="#555555", style="italic")
    ax.text(lx, 0.85, "Verification stream", ha="center", fontsize=9.5,
            fontweight="bold", color=GREEN)
    ax.text(rx, 0.85, "Implementation stream", ha="center", fontsize=9.5,
            fontweight="bold", color=BLUE)
    ax.text(5.5, 0.15, "typical run times (italic): synthesis 2-10 min, place and route 5-60 min",
            ha="center", fontsize=7.5, color="#555555")
    save(fig, "19", "fig-19-1-hdl-design-flow")


# ----------------------------------------------------------------------------
# Figure 19.2 — quadrature decoder
# ----------------------------------------------------------------------------
def _ff(ax, x, y, w=0.8, h=1.0, label="FF"):
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=INK, lw=1.1))
    ax.text(x + 0.12, y + h - 0.22, "D", fontsize=7, va="center")
    ax.text(x + w - 0.12, y + h - 0.22, "Q", fontsize=7, va="center", ha="right")
    ax.add_patch(Polygon([(x, y + 0.12), (x + 0.14, y + 0.22), (x, y + 0.32)],
                         closed=True, fill=False, ec=INK, lw=0.9))
    ax.text(x + w / 2, y - 0.08, label, fontsize=6.5, ha="center", va="top")


def fig_19_2():
    fig = plt.figure(figsize=(6.8, 5.2))
    ax_s = fig.add_axes([0.0, 0.40, 0.42, 0.58])
    ax_f = fig.add_axes([0.44, 0.38, 0.56, 0.62])
    ax_w = fig.add_axes([0.08, 0.04, 0.88, 0.30])

    # --- synchronisers
    ax = ax_s
    ax.set_xlim(0, 6.2)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(3.1, 5.6, "Two-flip-flop synchronisers\n(ASYNC_REG, 100 MHz clk)",
            ha="center", va="center", fontsize=8.5)
    for yb, sig, out in [(3.6, "enc_a", "a_sync[1]"), (1.6, "enc_b", "b_sync[1]")]:
        _ff(ax, 1.4, yb, label="")
        _ff(ax, 3.0, yb, label="")
        wire_arrow(ax, [(0.4, yb + 0.78), (1.4, yb + 0.78)], ms=7)
        ax.text(0.35, yb + 0.78, sig, ha="right", va="center", fontsize=7.5)
        wire_arrow(ax, [(2.2, yb + 0.78), (3.0, yb + 0.78)], ms=7)
        wire(ax, [(3.8, yb + 0.78), (4.3, yb + 0.78)])
        ax.text(4.35, yb + 0.78, out, ha="left", va="center", fontsize=7.5)
        wire(ax, [(1.05, yb + 0.22), (1.4, yb + 0.22)], lw=0.9)
        wire(ax, [(2.65, yb + 0.22), (3.0, yb + 0.22)], lw=0.9)
    wire(ax, [(1.05, 3.82), (1.05, 0.9)], lw=0.9)
    wire(ax, [(2.65, 3.82), (2.65, 0.9)], lw=0.9)
    wire(ax, [(0.5, 0.9), (2.65, 0.9)], lw=0.9)
    for x in (1.05, 2.65):
        ax.plot([x], [0.9], "o", ms=2.5, color=INK)
    ax.text(0.45, 0.9, "clk", fontsize=7.5, ha="right", va="center")
    ax.text(3.1, 0.2, "ab = {a_sync[1], b_sync[1]}  (state input)", fontsize=8,
            ha="center", va="center", fontweight="bold")

    # --- state diagram
    ax = ax_f
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.85, 1.95)
    ax.set_aspect("equal")
    ax.axis("off")
    r = 0.33
    pos = {"S00": (-0.95, 0.95), "S01": (0.95, 0.95), "S11": (0.95, -0.95),
           "S10": (-0.95, -0.95)}
    for n, (x, y) in pos.items():
        ax.add_patch(Circle((x, y), r, fc="#EEF3F8", ec=INK, lw=1.3, zorder=3))
        ax.text(x, y, n, ha="center", va="center", fontsize=9, zorder=4)

    def edge(a, b, off, color, text, tpos, ls="-", ha="center"):
        (x0, y0), (x1, y1) = pos[a], pos[b]
        d = np.array([x1 - x0, y1 - y0])
        L = np.hypot(*d)
        u = d / L
        nrm = np.array([-u[1], u[0]])
        p0 = np.array([x0, y0]) + u * r * 1.02 + nrm * off
        p1 = np.array([x1, y1]) - u * r * 1.02 + nrm * off
        # keep the start on the circle
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=11,
                                     color=color, lw=1.3, ls=ls, zorder=2))
        if text:
            ax.text(*tpos, text, fontsize=7.5, color=color, ha=ha, va="center")

    cw = [("S00", "S01"), ("S01", "S11"), ("S11", "S10"), ("S10", "S00")]
    # clockwise arrows on the outside, counter-clockwise inside
    edge("S00", "S01", 0.11, BLUE, "position+1", (0, 1.22))
    edge("S01", "S11", 0.11, BLUE, "position+1", (1.22, 0), ha="left")
    edge("S11", "S10", 0.11, BLUE, "position+1", (0, -1.22))
    edge("S10", "S00", 0.11, BLUE, "position+1", (-1.22, 0), ha="right")
    edge("S01", "S00", 0.11, ORANGE, "position-1", (0, 0.68))
    edge("S11", "S01", 0.11, ORANGE, "position-1", (0.67, 0), ha="right")
    edge("S10", "S11", 0.11, ORANGE, "position-1", (0, -0.68))
    edge("S00", "S10", 0.11, ORANGE, "position-1", (-0.67, 0), ha="left")
    _ = cw
    # fix labels on vertical edges (rotate)
    for t in ax.texts:
        if t.get_text() in ("position+1", "position-1") and abs(t.get_position()[1]) < 0.01:
            t.set_rotation(90)
            t.set_ha("center")
    # dashed red diagonals
    for a, b in [("S00", "S11"), ("S01", "S10")]:
        (x0, y0), (x1, y1) = pos[a], pos[b]
        d = np.array([x1 - x0, y1 - y0]) / np.hypot(x1 - x0, y1 - y0)
        p0 = np.array([x0, y0]) + d * r
        p1 = np.array([x1, y1]) - d * r
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<|-|>", mutation_scale=10,
                                     color=RED, lw=1.2, ls="--", zorder=1))
    ax.text(0, 0, "error <= 1", color=RED, fontsize=7.5, ha="center", va="center",
            bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="none"), zorder=6)
    # self loops on outer corners
    for n, (x, y) in pos.items():
        sx, sy = np.sign(x), np.sign(y)
        cx, cy = x + sx * 0.36, y + sy * 0.36
        ax.add_patch(FancyArrowPatch((x + sx * r * 0.95, y + sy * 0.12),
                                     (x + sx * 0.12, y + sy * r * 0.95),
                                     connectionstyle=f"arc3,rad={1.6 * sx * sy}",
                                     arrowstyle="-|>", mutation_scale=8, color="#666666",
                                     lw=1.0, zorder=4))
        ax.text(x + sx * 0.66, y + sy * 0.2, "no\nchange", fontsize=6.5,
                color="#666666", ha="center", va="center")

    # --- waveform: B leads A -> 00 01 11 10 00 (count up)
    ax = ax_w
    ax.set_xlim(-0.6, 5.2)
    ax.set_ylim(-0.95, 2.4)
    ax.axis("off")
    digital(ax, 1.55, 0, 5, [2, 4], h=0.55)
    digital(ax, 0.75, 0, 5, [1, 3], h=0.55)
    ax.text(-0.1, 1.82, "A", ha="right", va="center", fontsize=9)
    ax.text(-0.1, 1.02, "B", ha="right", va="center", fontsize=9)
    for k, s in enumerate(["00", "01", "11", "10", "00"]):
        ax.text(k + 0.5, 0.3, s, ha="center", va="center", fontsize=9,
                fontweight="bold", color=BLUE)
    ax.text(-0.1, 0.3, "ab", ha="right", va="center", fontsize=9)
    for t in range(1, 5):
        ax.plot([t, t], [0.15, 2.2], ls=":", color="#999999", lw=0.8)
    dim(ax, 1, 2, -0.2, "1 µs", fs=8)
    ax.text(2.7, -0.55, "B leads A by 90°: states 00 → 01 → 11 → 10 → 00, "
            "position +1 at each edge (1.0 M counts/s)", fontsize=8, ha="center",
            va="center")
    save(fig, "19", "fig-19-2-quadrature-decoder-fsm")


# ----------------------------------------------------------------------------
# Figure 19.3 — blocking vs non-blocking
# ----------------------------------------------------------------------------
def fig_19_3():
    fig, ax = new_fig(6.4, 4.4)
    t0, t1 = 5, 88
    rows = [("clk", None), ("d", None), ("q1", "nb"), ("q2", "nb"), ("q3", "nb"),
            ("q1", "b"), ("q2", "b"), ("q3", "b")]
    ys = [9.0, 7.9, 6.3, 5.3, 4.3, 2.6, 1.6, 0.6]
    h = 0.6
    clk_edges = []
    for k in range(1, 9):
        clk_edges += [10 * k, 10 * k + 5]
    digital(ax, ys[0], t0, t1, clk_edges, init=0, h=h)
    digital(ax, ys[1], t0, t1, [12, 32], h=h, color=INK)
    digital(ax, ys[2], t0, t1, [20, 40], h=h, color=BLUE)
    digital(ax, ys[3], t0, t1, [30, 50], h=h, color=BLUE)
    digital(ax, ys[4], t0, t1, [40, 60], h=h, color=BLUE)
    for y in ys[5:]:
        digital(ax, y, t0, t1, [20, 40], h=h, color=ORANGE)
    for (name, _), y in zip(rows, ys):
        ax.text(t0 - 1.5, y + h / 2, name, ha="right", va="center", fontsize=9.5)
    for k in range(1, 9):
        ax.plot([10 * k] * 2, [0.3, 9.75], ls="--", color="#AAAAAA", lw=0.7, zorder=0)
    ax.text(t0 - 18.5, 5.3 + h / 2, "non-\nblocking\n(<=)", ha="center", va="center",
            fontsize=8.5, color=BLUE)
    ax.text(t0 - 18.5, 1.6 + h / 2, "blocking\n(=)", ha="center", va="center",
            fontsize=8.5, color=ORANGE)
    ax.plot([t0 - 8.5] * 2, [4.2, 7.0], color=BLUE, lw=1)
    ax.plot([t0 - 8.5] * 2, [0.5, 3.3], color=ORANGE, lw=1)
    ax.text(62, 7.2, "staggered: one clock\nper stage (three flip-flops)", fontsize=8,
            color=BLUE, va="center", bbox=dict(fc="white", ec="none", pad=1))
    ax.text(45, 3.45, "three names, one flip-flop:\nq3 follows d after one clock",
            fontsize=8, color=ORANGE, va="center", bbox=dict(fc="white", ec="none", pad=1))
    ax.set_xlim(t0 - 26, t1)
    ax.set_ylim(-0.2, 10.0)
    ax.spines["bottom"].set_bounds(t0, t1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xticks(range(10, 90, 10))
    ax.set_xlabel("time (ns)")
    save(fig, "19", "fig-19-3-blocking-vs-nonblocking")


# ----------------------------------------------------------------------------
# Figure 19.4 — input delay timing
# ----------------------------------------------------------------------------
def _clock(ax, y, t0, t1, first_edge, T, h=0.5, color=INK):
    edges = []
    t = first_edge
    while t - T / 2 > t0:
        t -= T
    while t < t1:
        if t > t0:
            edges.append(t)
        if t + T / 2 > t0 and t + T / 2 < t1:
            edges.append(t + T / 2)
        t += T
    edges = sorted(edges)
    # level at t0: high if t0 in [edge, edge+T/2)
    phase = (t0 - first_edge) % T
    init = 1 if phase < T / 2 else 0
    digital(ax, y, t0, t1, edges, init=init, h=h, color=color)


def fig_19_4():
    fig = plt.figure(figsize=(6.8, 6.8))
    ax_i = fig.add_axes([0.02, 0.80, 0.96, 0.19])
    ax_a = fig.add_axes([0.17, 0.47, 0.80, 0.28])
    ax_b = fig.add_axes([0.17, 0.07, 0.80, 0.31])

    # --- board inset
    ax = ax_i
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 2.4)
    ax.set_aspect("equal")
    ax.axis("off")
    box(ax, 0.3, 0.75, 2.0, 0.9, "125 MHz\noscillator", fc=SRC_FC, fontsize=8)
    box(ax, 4.6, 1.35, 2.0, 0.85, "ADC\n14-bit", fc=IMP_FC, fontsize=8)
    box(ax, 9.3, 0.2, 2.4, 2.0, "", fc=VER_FC)
    ax.text(10.5, 1.95, "FPGA", ha="center", va="center", fontsize=9, fontweight="bold")
    wire_arrow(ax, [(2.3, 1.35), (3.3, 1.35), (3.3, 1.78), (4.6, 1.78)], ms=8)
    ax.text(3.95, 1.86, "0.5 ns", fontsize=7.5, ha="center", va="bottom")
    wire_arrow(ax, [(2.3, 1.05), (3.3, 1.05), (3.3, 0.55), (9.3, 0.55)], ms=8)
    ax.text(6.3, 0.47, "clock trace 0.3 ns", fontsize=7.5, ha="center", va="top")
    for dy in (0.0, 0.08, 0.16):
        wire(ax, [(6.6, 1.7 + dy), (9.3, 1.7 + dy)], lw=0.9)
    ax.annotate("", xy=(9.3, 1.78), xytext=(9.0, 1.78),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1, mutation_scale=8))
    ax.text(7.95, 1.6, "14 data traces\n0.8-0.9 ns", fontsize=7.5, ha="center",
            va="top")
    ax.text(10.5, 1.0, "IOB register\n$t_{su}$ 0.1 ns, $t_h$ 0.2 ns", fontsize=7,
            ha="center", va="center")

    def panel(ax, T, shifts, title):
        ax.set_ylim(-0.4, 6.4)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_xlabel("time from launching clock edge at FPGA pin (ns)", fontsize=8.5)
        ax.set_title(title, fontsize=9.5, loc="left")

    # --- panel (a): 125 MHz
    ax = ax_a
    T = 8.0
    t0, t1 = -1.0, 13.5
    ax.set_xlim(t0, t1)
    panel(ax, T, None, "(a) 125 MHz, T = 8 ns")
    _clock(ax, 5.3, t0, t1, 0.0, T)
    bus(ax, 3.7, [(t0, 3.0, "valid", ""), (3.0, 6.5, "x", ""),
                  (6.5, 11.0, "valid", "valid"), (11.0, 14.5, "x", "")], h=0.6)
    bus(ax, 2.1, [(t0, 4.0, "valid", ""), (4.0, 7.7, "x", ""),
                  (7.7, 12.0, "valid", "valid"), (12.0, 15.7, "x", "")], h=0.6)
    for lab, y in [("clock at\nFPGA pin", 5.55), ("data at pin", 4.0),
                   ("data at\nregister", 2.4)]:
        ax.text(t0 - 0.3, y, lab, ha="right", va="center", fontsize=8,
                transform=ax.transData, clip_on=False)
    for x in (0.0, 8.0):
        ax.axvline(x, color="#999999", ls="--", lw=0.8, zorder=0)
    ax.text(4.75, 4.42, "$t_{in}$ 3.0-6.5 ns", fontsize=7.5, ha="center")
    ax.text(5.85, 2.82, "+1.0-1.2 ns pin-to-reg", fontsize=7.5, ha="center")
    # setup
    ax.axvspan(7.9, 8.0, ymin=0.05, ymax=0.62, color=BLUE, alpha=0.25, lw=0)
    dim(ax, 7.7, 7.9, 1.55, "", color=GREEN)
    ax.text(7.1, 1.05, "setup slack\n+0.2 ns", fontsize=7.5, color=GREEN, ha="center",
            va="center")
    # hold at edge 8: hold requirement until 8.2, next change at 12.0
    ax.axvspan(8.0, 8.2, ymin=0.05, ymax=0.62, color=ORANGE, alpha=0.3, lw=0)
    dim(ax, 8.2, 12.0, 1.55, "", color=GREEN)
    ax.text(10.1, 1.05, "hold slack +3.8 ns", fontsize=7.5, color=GREEN, ha="center",
            va="center")
    ax.text(8.35, 0.25, "shaded: $t_{su}$ and $t_h$ windows", fontsize=7, ha="left", color="#555555")

    # --- panel (b): 160 MHz
    ax = ax_b
    T = 6.25
    t0, t1 = -1.0, 13.5
    ax.set_xlim(t0, t1)
    panel(ax, T, None, "(b) 160 MHz, T = 6.25 ns")
    _clock(ax, 5.3, t0, t1, 0.0, T)
    bus(ax, 3.85, [(t0, 4.0, "valid", ""), (4.0, 7.7, "x", ""),
                   (7.7, 10.25, "valid", "valid"), (10.25, 13.95, "x", "")], h=0.6)
    _clock(ax, 2.35, t0, t1, 2.0, T, color=BLUE)
    for lab, y in [("clock at\nFPGA pin", 5.55), ("data at\nregister", 4.15),
                   ("capture clk\nshifted +2.0 ns", 2.6)]:
        ax.text(t0 - 0.3, y, lab, ha="right", va="center", fontsize=8, clip_on=False)
    ax.axvline(6.25, color=RED, ls="--", lw=0.9, ymin=0.55, ymax=0.97)
    ax.axvline(8.25, color=BLUE, ls="--", lw=0.9, ymin=0.05, ymax=0.68)
    ax.axvline(2.0, color=BLUE, ls=":", lw=0.8, ymin=0.05, ymax=0.68)
    dim(ax, 6.15, 7.7, 4.85, "", color=RED)
    ax.text(6.0, 4.85, "setup slack -1.55 ns", fontsize=7.5, color=RED, ha="right",
            va="center")
    dim(ax, 7.7, 8.15, 1.6, "", color=GREEN)
    ax.text(7.2, 1.05, "setup\n+0.45 ns", fontsize=7.5, color=GREEN, ha="center",
            va="center")
    dim(ax, 8.45, 10.25, 1.6, "", color=GREEN)
    ax.text(9.35, 1.05, "hold +1.8 ns", fontsize=7.5, color=GREEN, ha="center",
            va="center")
    ax.text(11.9, 0.3, "next data launched\nat 6.25 ns changes\nat 10.25 ns",
            fontsize=7, ha="center", va="bottom", color="#555555")
    save(fig, "19", "fig-19-4-input-delay-timing")


# ----------------------------------------------------------------------------
# Figure 19.5 — FPGA implementation flow
# ----------------------------------------------------------------------------
def fig_19_5():
    fig, ax = schematic(6.8, 5.2, xlim=(0, 13.6), ylim=(0, 10.4))
    cx, w, h = 3.0, 4.6, 0.68
    steps = ["Netlist + XDC", "opt_design", "place_design", "phys_opt_design",
             "route_design", "report_timing_summary\n(WNS, TNS, WHS)"]
    ys = [9.7, 8.7, 7.7, 6.7, 5.7, 4.55]
    for i, (t, y) in enumerate(zip(steps, ys)):
        hh = h if i < 5 else 0.95
        box(ax, cx - w / 2, y - hh / 2, w, hh, t,
            fc=SRC_FC if i == 0 else IMP_FC, fontsize=9)
    for i in range(5):
        y0 = ys[i] - h / 2
        y1 = ys[i + 1] + (h / 2 if i + 1 < 5 else 0.475)
        wire_arrow(ax, [(cx, y0), (cx, y1)])
    # diamond
    dy, dh, dw = 2.75, 0.85, 2.7
    ax.add_patch(Polygon([(cx, dy + dh), (cx + dw, dy), (cx, dy - dh), (cx - dw, dy)],
                         closed=True, fc="#FFF4D6", ec=INK, lw=1.0))
    ax.text(cx, dy, "WNS ≥ 0 and\nWHS ≥ 0 ?", ha="center", va="center", fontsize=9)
    wire_arrow(ax, [(cx, ys[5] - 0.475), (cx, dy + dh)])
    # yes path along the bottom
    by = 0.75
    wire_arrow(ax, [(cx, dy - dh), (cx, by + h / 2)])
    ax.text(cx + 0.15, dy - dh - 0.3, "yes", fontsize=8.5, color=GREEN, va="center")
    bot = [("write_bitstream", cx, 4.0), ("program\nJTAG / QSPI flash", 7.6, 3.2),
           ("ILA debug and\nhardware test", 11.5, 3.6)]
    for t, x, bw in bot:
        box(ax, x - bw / 2, by - 0.45, bw, 0.9, t, fc=VER_FC, fontsize=8.5)
    wire_arrow(ax, [(cx + 2.0, by), (7.6 - 1.6, by)])
    wire_arrow(ax, [(7.6 + 1.6, by), (11.5 - 1.8, by)])
    # no path
    fx, fy, fw, fh = 9.7, 4.7, 5.4, 1.6
    wire_arrow(ax, [(cx + dw, dy), (fx, dy), (fx, fy - fh / 2)])
    ax.text(cx + dw + 0.2, dy + 0.12, "no", fontsize=8.5, color=RED, va="bottom")
    box(ax, fx - fw / 2, fy - fh / 2, fw, fh,
        "pipeline, use DSP/BRAM registers,\nreplicate fan-out, fix constraints,\n"
        "floorplan", fc="#FBE2DF", fontsize=8.5)
    wire_arrow(ax, [(fx, fy + fh / 2), (fx, 8.7), (cx + w / 2, 8.7)], color=RED)
    ax.text(fx - 0.15, 6.9, "re-run implementation\n(re-synthesise if RTL changed)",
            fontsize=7.5, color=RED, ha="right", va="center")
    # example annotation
    ax.text(6.4, 10.05, "Example, 250 MHz FIR filter: target 4.000 ns,", fontsize=8,
            va="center")
    ax.text(6.4, 9.55, "WNS -2.800 ns before pipelining, +1.845 ns after", fontsize=8,
            va="center")
    save(fig, "19", "fig-19-5-fpga-implementation-flow")


# ----------------------------------------------------------------------------
# Figure 19.6 — coverage closure
# ----------------------------------------------------------------------------
def fig_19_6():
    B = 256
    n = np.arange(0, 2001)
    cov = 100 * (1 - (1 - 1 / B) ** n)
    H = np.sum(1 / np.arange(1, B + 1))
    n_full = B * H
    fig, ax = new_fig(6.4, 3.8)
    ax.axhspan(95, 102, color=GREEN, alpha=0.12, lw=0)
    ax.text(30, 97.6, "closure by directed tests", ha="left", va="center",
            fontsize=8.5, color=GREEN)
    ax.plot(n, cov, color=BLUE, label="expected coverage, 100[1-(1-1/256)$^n$]")
    n95 = np.log(0.05) / np.log(1 - 1 / B)
    for nx, lab, dx, dyy in [(100, "(100, 32.4 %)", 40, -6),
                             (256, "(256, 63.3 %)", 40, -6),
                             (n95, "(766, 95 %)", 40, -9)]:
        y = 100 * (1 - (1 - 1 / B) ** nx)
        ax.plot([nx, nx], [0, y], ls=":", color="#777777", lw=0.9)
        ax.plot([0, nx], [y, y], ls=":", color="#777777", lw=0.9)
        ax.plot(nx, y, "o", color=ORANGE, ms=5, zorder=5)
        ax.text(nx + dx, y + dyy, lab, fontsize=8.5, va="center")
    ax.axvline(n_full, color=INK, ls="--", lw=1)
    ax.text(n_full + 25, 45, f"mean tests to full coverage\n256 $H_{{256}}$ = {n_full:.0f}",
            fontsize=8.5, va="center")
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 102)
    ax.set_xlabel("number of random tests $n$")
    ax.set_ylabel("functional coverage (%)")
    ax.legend(loc="lower right", fontsize=8.5)
    save(fig, "19", "fig-19-6-coverage-closure")


if __name__ == "__main__":
    fig_19_1()
    fig_19_2()
    fig_19_3()
    fig_19_4()
    fig_19_5()
    fig_19_6()
