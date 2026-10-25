"""Figures for Chapter 18 — Memory and Programmable Logic.

Run from the repository root:  python figures/scripts/ch18.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch, Circle, Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4], COLORS[5]
LUT_FC = "#DCEBF7"
FF_FC = "#E3F2E6"
HARD_FC = "#FBE7D3"
DSP_FC = "#F1EAF6"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def wire(ax, pts, color=INK, lw=1.2, ls="-", **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt",
            solid_joinstyle="miter", **kw)


def wire_arrow(ax, pts, color=INK, lw=1.2, ls="-", ms=9, both=False):
    if len(pts) > 2:
        wire(ax, pts[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def dot(ax, x, y, color=INK, ms=3.5):
    ax.plot([x], [y], "o", ms=ms, color=color, zorder=5)


def rect(ax, x, y, w, h, fc="white", ec=INK, lw=1.0, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))


def dim(ax, x0, x1, y, text, color=INK, fs=7, above=True, dy=0.08):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.9, shrinkA=0, shrinkB=0,
                                mutation_scale=7))
    ax.text((x0 + x1) / 2, y + (dy if above else -dy), text, ha="center",
            va="bottom" if above else "top", fontsize=fs, color=color)


def mux2(ax, x, y, w=0.35, h=0.7, fc="white", lw=0.9):
    """2:1 mux trapezoid pointing right, centre at (x, y). Returns in0, in1, out, sel."""
    ax.add_patch(Polygon([(x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2 - 0.15 * h),
                          (x + w / 2, y - h / 2 + 0.15 * h)], closed=True, fc=fc, ec=INK, lw=lw))
    return (x - w / 2, y + h / 4), (x - w / 2, y - h / 4), (x + w / 2, y), (x, y - h / 2 + 0.075 * h)


# ----------------------------------------------------------------------------
def fig_18_1():
    """(a) 6T SRAM cell, (b) 1T1C DRAM cell with bit-line sensing."""
    fig, ax = schematic(6.8, 4.6, xlim=(-0.6, 16.6), ylim=(-0.5, 11.0))
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7, lw=1.1, unit=1.6)
    # ---------------- (a) 6T SRAM ----------------
    xq, xqb, yv, yg = 2.6, 5.6, 7.6, 2.4
    xbl, xblb, ywl = 0.6, 7.6, 8.7
    p1 = d.add(elm.PFet().at((xq, yv)).anchor("source"))
    n1 = d.add(elm.NFet().at((xq, yg + 1.5)).anchor("drain"))
    p2 = d.add(elm.PFet().reverse().at((xqb, yv)).anchor("source"))
    n2 = d.add(elm.NFet().reverse().at((xqb, yg + 1.5)).anchor("drain"))
    a1 = d.add(elm.NFet().theta(90).at((xbl + 0.25, 5.0)).anchor("drain"))
    a2 = d.add(elm.NFet().theta(90).at((xqb + 0.25, 5.0)).anchor("drain"))
    # ---------------- (b) DRAM ----------------
    xb, xn, yd = 10.0, 12.3, 6.0
    acc = d.add(elm.NFet().theta(90).at((xb, yd)).anchor("drain"))
    cs = d.add(elm.Capacitor().down().at((xn, yd)).to((xn, 4.2)))
    cbl = d.add(elm.Capacitor().down().at((9.0, 3.9)).to((9.0, 2.5)))
    d.add(elm.Ground().at((9.0, 2.5)))
    d.draw(show=False)

    # rails and nodes (a)
    wire(ax, [(xq - 0.4, yv), (xqb + 0.4, yv)], lw=1.3)
    wire(ax, [(xq - 0.4, yg), (xqb + 0.4, yg)], lw=1.3)
    ax.text(4.1, yv + 0.12, "$V_{DD}$", ha="center", va="bottom", fontsize=7.5)
    ax.text(4.1, yg - 0.12, "GND", ha="center", va="top", fontsize=7)
    for x in (xq, xqb):
        wire(ax, [(x, yv - 1.5), (x, yg + 1.5)])
        dot(ax, x, yv)
        dot(ax, x, yg)
    g1x, g2x = p1.absanchors["gate"].x, p2.absanchors["gate"].x
    gy_p, gy_n = p1.absanchors["gate"].y, n1.absanchors["gate"].y
    wire(ax, [(g1x, gy_p), (g1x, gy_n)])
    wire(ax, [(g2x, gy_p), (g2x, gy_n)])
    # cross coupling
    wire(ax, [(g1x, 4.55), (xqb, 4.55)])
    dot(ax, g1x, 4.55)
    dot(ax, xqb, 4.55)
    wire(ax, [(xq, 5.45), (g2x, 5.45)])
    dot(ax, xq, 5.45)
    dot(ax, g2x, 5.45)
    # access transistors
    wire(ax, [(a1.absanchors["source"].x, 5.0), (xq, 5.0)])
    dot(ax, xq, 5.0)
    wire(ax, [(xbl, 5.0), (xbl + 0.25, 5.0)])
    dot(ax, xbl, 5.0)
    wire(ax, [(xqb, 5.0), (xqb + 0.25, 5.0)])
    dot(ax, xqb, 5.0)
    wire(ax, [(a2.absanchors["source"].x, 5.0), (xblb, 5.0)])
    dot(ax, xblb, 5.0)
    for a in (a1, a2):
        g = a.absanchors["gate"]
        wire(ax, [(g.x, g.y), (g.x, ywl)])
        dot(ax, g.x, ywl)
    wire(ax, [(xbl - 0.4, ywl), (xblb + 0.4, ywl)], color=BLUE, lw=1.4)
    ax.text(xblb + 0.5, ywl, "WL", fontsize=7.5, va="center", color=BLUE)
    for x, lab in ((xbl, "BL"), (xblb, r"$\overline{\rm BL}$")):
        wire(ax, [(x, 1.15), (x, 9.6)], lw=1.4)
        ax.text(x, 9.68, lab, ha="center", va="bottom", fontsize=7.5)
    # labels
    ax.text(xq + 0.12, 6.85, "P1", fontsize=7, va="center", ha="left") if False else None
    ax.text(xq - 0.15, 6.85, "P1", fontsize=7, va="center", ha="right")
    ax.text(xq - 0.15, 3.15, "N1", fontsize=7, va="center", ha="right")
    ax.text(xqb + 0.15, 6.85, "P2", fontsize=7, va="center", ha="left")
    ax.text(xqb + 0.15, 3.15, "N2", fontsize=7, va="center", ha="left")
    ax.text((xbl + xq) / 2 - 0.1, 4.65, "A1", fontsize=7, va="top", ha="center")
    ax.text((xqb + xblb) / 2 + 0.1, 4.65, "A2", fontsize=7, va="top", ha="center")
    ax.text(xq - 0.12, 5.25, "Q", fontsize=7.5, ha="right", va="bottom", color=ORANGE, weight="bold")
    ax.text(xqb + 0.12, 5.25, r"$\overline{\rm Q}$", fontsize=7.5, ha="left", va="bottom", color=ORANGE)
    box(ax, xbl - 0.3, 0.05, xblb - xbl + 0.6, 1.1, "precharge to $V_{DD}$  +  sense amplifier",
        fc="#F4F4F4", fontsize=7)
    ax.text(4.1, -0.15, "cell ratio N1/A1 ≈ 2 (read stability)", ha="center", va="top", fontsize=6.8)
    ax.text(-0.5, 10.75, "(a) 6T SRAM cell", fontsize=8.5, weight="bold", va="center")

    # (b) DRAM wiring
    wire(ax, [(xb, 1.15), (xb, 9.6)], lw=1.4)
    ax.text(xb, 9.68, "BL", ha="center", va="bottom", fontsize=7.5)
    dot(ax, xb, yd)
    wire(ax, [(acc.absanchors["source"].x, yd), (xn, yd)])
    g = acc.absanchors["gate"]
    wire(ax, [(g.x, g.y), (g.x, ywl)])
    dot(ax, g.x, ywl)
    wire(ax, [(9.5, ywl), (13.2, ywl)], color=BLUE, lw=1.4)
    ax.text(13.3, ywl, "WL", fontsize=7.5, va="center", color=BLUE)
    wire(ax, [(xn - 0.5, 4.2), (xn + 0.5, 4.2)], lw=1.3)
    ax.text(xn + 0.6, 4.2, "plate", fontsize=6.8, va="center")
    ax.text(xn + 0.45, 5.1, "$C_s$ = 10 fF", fontsize=7, va="center")
    ax.text(xn - 0.1, yd + 0.15, "storage\nnode", fontsize=6.3, ha="center", va="bottom")
    wire(ax, [(xb, 3.9), (9.0, 3.9)])
    dot(ax, xb, 3.9)
    ax.text(8.5, 3.2, "$C_{BL}$\n= 80 fF", fontsize=6.8, ha="right", va="center")
    # reference bit line and precharge
    xref = 15.2
    wire(ax, [(xref, 1.15), (xref, 9.6)], lw=1.4, ls=(0, (4, 2)))
    ax.text(xref, 9.68, "reference BL", ha="center", va="bottom", fontsize=7)
    ax.text(xref - 0.15, 6.6, "0.6 V", fontsize=7, ha="right", va="center")
    ax.text(13.25, 7.7, "BL and reference BL\nprecharged to $V_{DD}/2$ = 0.6 V", fontsize=6.6,
            ha="center", va="bottom")
    box(ax, xb - 0.3, 0.05, xref - xb + 0.6, 1.1, "cross-coupled sense amplifier\n(BL vs reference BL)",
        fc="#F4F4F4", fontsize=6.6)
    ax.text(12.6, 2.75, r"$\Delta V = 0.6\,\mathrm{V}\times\dfrac{10}{10+80} = 67\ \mathrm{mV}$",
            fontsize=8, ha="center", va="center",
            bbox=dict(fc="#FFF4D6", ec=INK, lw=0.8, boxstyle="round,pad=0.35"))
    ax.text(8.9, 10.75, "(b) 1T1C DRAM cell", fontsize=8.5, weight="bold", va="center")
    save(fig, "18", "fig-18-1-sram-dram-cells")


# ----------------------------------------------------------------------------
def fig_18_2():
    """DDR4-3200 read with a row miss: PRE, ACT, READ, burst; and a row hit."""
    tck = 0.625
    T = 80
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    rows = {"CK": 5.0, "command": 3.9, "address": 2.8, "DQS": 1.7, "DQ": 0.6}
    h = 0.6
    # clock
    t = np.arange(0, T + 0.5, 0.5)
    ck = np.tile([1, 0], len(t) // 2 + 1)[:len(t)]
    ax.step(t, rows["CK"] + ck * h, where="post", color=INK, lw=0.7)
    # command bus
    def bus(y, segs, dashed_idx=()):
        yb = rows[y]
        ax.plot([0, T], [yb + h / 2] * 2, color="#888888", lw=0.9)
        for i, (t0, t1, lab, c) in enumerate(segs):
            ls = (0, (3, 2)) if i in dashed_idx else "-"
            ax.add_patch(Polygon([(t0, yb + h / 2), (t0 + 0.3, yb + h), (t1 - 0.3, yb + h), (t1, yb + h / 2),
                                  (t1 - 0.3, yb), (t0 + 0.3, yb)], closed=True, fc=c + "40", ec=c, lw=1.1, ls=ls))
            ax.text((t0 + t1) / 2, yb + h + 0.06, lab, ha="center", va="bottom", fontsize=6.5, color=c)
    bus("command", [(0, 1, "PRE", ORANGE), (22, 23, "ACT", GREEN), (44, 45, "READ", BLUE),
                    (52, 53, "READ", "#777777")], dashed_idx=(3,))
    bus("address", [(0, 1, "BA0", ORANGE), (22, 23, "BA0, row r", GREEN), (44, 45, "BA0, col c", BLUE),
                    (52, 53, "col c+8", "#777777")], dashed_idx=(3,))
    ax.text(33, rows["command"] + h / 2, "NOP / DES", fontsize=6, color="#888888", ha="center", va="center",
            bbox=dict(fc="white", ec="none", pad=0.3))
    # DQS: hi-Z then preamble and toggling
    yq = rows["DQS"]
    ax.plot([0, 65], [yq + h / 2] * 2, color="#888888", lw=0.9)
    ax.plot([70, T], [yq + h / 2] * 2, color="#888888", lw=0.9)
    xs, ys = [65, 65], [yq + h / 2, yq]
    ys_ = [yq]
    tt = np.arange(66, 70.01, 0.5)
    xs = [65, 65, 66]
    ys = [yq + h / 2, yq, yq]
    lev = 0
    for tk in tt[:-1]:
        lev = 1 - lev
        xs += [tk, tk + 0.5]
        ys += [yq + lev * h, yq + lev * h]
    xs += [70, 70]
    ys += [yq + lev * h, yq + h / 2]
    ax.plot(xs, ys, color=BLUE, lw=1.0)
    ax.text(65.5, yq - 0.05, "preamble", fontsize=5.8, ha="center", va="top", color=BLUE)
    # DQ beats
    ydq = rows["DQ"]
    ax.plot([0, 66], [ydq + h / 2] * 2, color="#888888", lw=0.9)
    ax.plot([70, 74], [ydq + h / 2] * 2, color="#888888", lw=0.9)
    ax.plot([78, T], [ydq + h / 2] * 2, color="#888888", lw=0.9)
    for k in range(8):
        t0 = 66 + 0.5 * k
        ax.add_patch(Polygon([(t0, ydq + h / 2), (t0 + 0.08, ydq + h), (t0 + 0.42, ydq + h), (t0 + 0.5, ydq + h / 2),
                              (t0 + 0.42, ydq), (t0 + 0.08, ydq)], closed=True, fc=BLUE + "55", ec=BLUE, lw=0.7))
        t1 = 74 + 0.5 * k
        ax.add_patch(Polygon([(t1, ydq + h / 2), (t1 + 0.08, ydq + h), (t1 + 0.42, ydq + h), (t1 + 0.5, ydq + h / 2),
                              (t1 + 0.42, ydq), (t1 + 0.08, ydq)], closed=True, fc="white", ec="#777777",
                             lw=0.7, ls=(0, (2, 1))))
    ax.text(68, ydq - 0.05, "BL8 (64 B)", fontsize=6.3, ha="center", va="top", color=BLUE)
    ax.text(76, ydq - 0.05, "row hit", fontsize=6.3, ha="center", va="top", color="#777777")
    # intervals
    yd = 6.05
    dim(ax, 0, 22, yd, f"$t_{{RP}}$ = 22 $t_{{CK}}$ = {22 * tck:.2f} ns", ORANGE, fs=6.8)
    dim(ax, 22, 44, yd, f"$t_{{RCD}}$ = 22 $t_{{CK}}$ = {22 * tck:.2f} ns", GREEN, fs=6.8)
    dim(ax, 44, 66, yd, f"CL = 22 $t_{{CK}}$ = {22 * tck:.2f} ns", BLUE, fs=6.8)
    dim(ax, 66, 70, yd, "", INK)
    ax.text(70.6, yd, f"burst 4 $t_{{CK}}$\n= {4 * tck:.1f} ns", fontsize=6.3, va="center")
    dim(ax, 0, 70, yd + 0.75, f"row miss: {66 * tck:.2f} ns to first data, {70 * tck:.2f} ns to last beat",
        INK, fs=7.2)
    dim(ax, 52, 74, -0.35, f"row hit: CL only = {22 * tck:.2f} ns", "#555555", fs=6.6, above=False)
    for tv in (0, 22, 44, 66, 70):
        ax.axvline(tv, color=GRID, lw=0.6, ls=(0, (3, 3)), zorder=0)
    ax.set_yticks([v + h / 2 for v in rows.values()])
    ax.set_yticklabels(list(rows.keys()), fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.5, T)
    ax.set_ylim(-1.0, 7.6)
    ax.set_xlabel("clock cycles ($t_{CK}$ = 0.625 ns, CK = 1.6 GHz, 3200 MT/s on DQ)")
    ax.set_xticks(range(0, T + 1, 10))
    save(fig, "18", "fig-18-2-ddr4-read-timing")


# ----------------------------------------------------------------------------
def flash_cell(ax, x, y, h=0.6, gate="left", lead=0.2, lw=1.0, color=INK):
    """Floating-gate transistor symbol: channel vertical at x, centre y."""
    s = -1 if gate == "left" else 1
    wire(ax, [(x, y - h / 2), (x, y + h / 2)], lw=lw, color=color)
    wire(ax, [(x + s * 0.1, y - h * 0.4), (x + s * 0.1, y + h * 0.4)], lw=lw, color=color)   # floating gate
    wire(ax, [(x + s * 0.2, y - h * 0.4), (x + s * 0.2, y + h * 0.4)], lw=lw, color=color)   # control gate
    wire(ax, [(x, y + h / 2), (x, y + h / 2 + lead)], lw=lw, color=color)
    wire(ax, [(x, y - h / 2), (x, y - h / 2 - lead)], lw=lw, color=color)
    return (x + s * 0.2, y)


def nmos_sym(ax, x, y, h=0.5, gate="left", lead=0.2, lw=1.0):
    s = -1 if gate == "left" else 1
    wire(ax, [(x, y - h / 2), (x, y + h / 2)], lw=lw)
    wire(ax, [(x + s * 0.12, y - h * 0.4), (x + s * 0.12, y + h * 0.4)], lw=lw)
    wire(ax, [(x, y + h / 2), (x, y + h / 2 + lead)], lw=lw)
    wire(ax, [(x, y - h / 2), (x, y - h / 2 - lead)], lw=lw)
    return (x + s * 0.12, y)


def fig_18_3():
    """Floating-gate cell, threshold distributions, NOR and NAND arrays."""
    fig = plt.figure(figsize=(6.8, 6.0))
    # ---------- cross-section ----------
    ax = fig.add_axes([0.0, 0.5, 0.56, 0.48])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0.05, 7.05, "(a) Floating-gate transistor", fontsize=8.5, weight="bold", va="top")
    rect(ax, 0.3, 0.3, 9.4, 2.6, fc="#F3E3E3", lw=0.8)
    ax.text(5.0, 0.75, "p-substrate", ha="center", va="center", fontsize=7.5)
    for x0, lab in ((0.8, "n+ source"), (6.9, "n+ drain")):
        ax.add_patch(FancyBboxPatch((x0, 2.0), 2.3, 0.9, boxstyle="round,pad=0,rounding_size=0.35",
                                    fc="#C9DDF0", ec=INK, lw=0.8))
        ax.text(x0 + 1.15, 2.4, lab, ha="center", va="center", fontsize=7)
    gx0, gx1 = 2.7, 7.3
    rect(ax, gx0, 2.9, gx1 - gx0, 0.18, fc="#FFFFFF", lw=0.7)                   # tunnel oxide
    rect(ax, gx0, 3.08, gx1 - gx0, 0.75, fc="#B9B9B9", lw=0.8)                  # floating gate
    rect(ax, gx0, 3.83, gx1 - gx0, 0.35, fc="#F2E6B3", lw=0.7)                  # ONO
    rect(ax, gx0, 4.18, gx1 - gx0, 0.8, fc="#8C8C8C", lw=0.8)                   # control gate
    ax.text(5.0, 4.58, "control gate (poly)", ha="center", va="center", fontsize=7, color="white")
    ax.text(5.0, 4.0, "ONO inter-poly dielectric", ha="center", va="center", fontsize=6)
    for xe in np.linspace(3.3, 6.7, 7):
        ax.add_patch(Circle((xe, 3.45), 0.17, fc="white", ec=BLUE, lw=0.8))
        ax.text(xe, 3.45, "−", ha="center", va="center", fontsize=6.5, color=BLUE)
    ax.text(gx1 + 0.15, 3.65, "floating gate\n(stored electrons)", fontsize=6.3, va="center")
    ax.annotate("tunnel oxide\n≈ 8 nm", xy=(2.8, 2.99), xytext=(0.35, 3.45), fontsize=6.3,
                va="center", arrowprops=dict(arrowstyle="-", lw=0.7))
    wire(ax, [(5.0, 4.98), (5.0, 5.5)])
    ax.text(5.0, 5.55, "CG", ha="center", va="bottom", fontsize=6.5)
    # program (hot-electron injection near drain) and erase (FN tunnelling)
    ax.annotate("", xy=(6.4, 3.1), xytext=(6.5, 2.15),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.5, mutation_scale=9))
    ax.text(8.2, 5.3, "program:\nhot-electron injection\n(channel → FG, near drain)", fontsize=6.3,
            color=ORANGE, ha="center", va="center")
    wire(ax, [(6.6, 2.6), (7.6, 4.8)], color=ORANGE, lw=0.6)
    ax.annotate("", xy=(3.6, 2.15), xytext=(3.6, 3.15),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.5, mutation_scale=9))
    ax.text(1.6, 5.3, "erase:\nFowler–Nordheim\ntunnelling (FG → Si)", fontsize=6.3, color=GREEN,
            ha="center", va="center")
    wire(ax, [(3.5, 2.6), (2.0, 4.75)], color=GREEN, lw=0.6)
    ax.text(5.0, 1.65, "channel", ha="center", va="center", fontsize=6.3, style="italic")

    # ---------- threshold distributions ----------
    v = np.linspace(-4, 6.5, 1200)
    g = lambda m, s: np.exp(-0.5 * ((v - m) / s) ** 2)
    axs1 = fig.add_axes([0.62, 0.80, 0.36, 0.15])
    axs1.fill_between(v, g(-2, 0.55), color=GREEN, alpha=0.35, lw=0)
    axs1.plot(v, g(-2, 0.55), color=GREEN, lw=1.2)
    axs1.fill_between(v, g(3, 0.55), color=ORANGE, alpha=0.35, lw=0)
    axs1.plot(v, g(3, 0.55), color=ORANGE, lw=1.2)
    axs1.axvline(0.5, color=INK, ls=(0, (3, 2)), lw=0.9)
    axs1.text(0.65, 0.55, "$V_{read}$", fontsize=6.5, va="center")
    axs1.text(-2, 1.08, "erased '1'", fontsize=6.5, ha="center", va="bottom", color=GREEN)
    axs1.text(3, 1.08, "programmed '0'", fontsize=6.5, ha="center", va="bottom", color=ORANGE)
    axs1.set_title("(b) Threshold-voltage distributions — SLC", fontsize=8, loc="left", pad=12,
                   weight="bold")
    axs2 = fig.add_axes([0.62, 0.57, 0.36, 0.15])
    means = np.linspace(-2.0, 4.6, 8)
    for i, m in enumerate(means):
        c = plt.cm.viridis(i / 7)
        axs2.fill_between(v, g(m, 0.2), color=c, alpha=0.4, lw=0)
        axs2.plot(v, g(m, 0.2), color=c, lw=1.0)
    for a, b in zip(means[:-1], means[1:]):
        axs2.axvline((a + b) / 2, color=INK, ls=(0, (2, 2)), lw=0.6)
    axs2.set_title("TLC: 8 narrower states, 7 read levels", fontsize=7, loc="left", pad=3)
    for a_ in (axs1, axs2):
        a_.set_xlim(-4, 6.5)
        a_.set_ylim(0, 1.35)
        a_.set_yticks([])
        a_.spines["left"].set_visible(False)
        a_.tick_params(labelsize=7)
    axs1.set_xticklabels([])
    axs2.set_xlabel("threshold voltage $V_T$ (V)", fontsize=7.5)

    # ---------- NOR array ----------
    axn = fig.add_axes([0.0, 0.0, 0.42, 0.47])
    axn.set_xlim(0, 7)
    axn.set_ylim(0, 8)
    axn.set_aspect("equal")
    axn.axis("off")
    axn.text(0.05, 7.85, "(c) NOR array (cells in parallel)", fontsize=8.5, weight="bold", va="top")
    bls = [2.4, 5.0]
    wl_y = [6.2, 4.9, 3.0, 1.7]
    sl_y = [5.55 + 0.0, 2.35]
    for xb in bls:
        wire(axn, [(xb, 0.7), (xb, 7.0)], lw=1.3)
        axn.text(xb, 7.05, f"BL{bls.index(xb)}", ha="center", va="bottom", fontsize=7)
    for k, yw in enumerate(wl_y):
        xg = [xb + 0.55 - 0.2 for xb in bls]
        wire(axn, [(0.6, yw), (xg[0], yw)], color=BLUE, lw=1.0)
        wire(axn, [(xg[0] + 0.3, yw), (xg[1], yw)], color=BLUE, lw=1.0)
        wire(axn, [(xg[1] + 0.3, yw), (6.4, yw)], color=BLUE, lw=1.0)
        axn.text(0.55, yw, f"WL{k}", ha="right", va="center", fontsize=6.5, color=BLUE)
    for ys in (5.55, 2.35):
        wire(axn, [(0.6, ys), (6.4, ys)], color=GREEN, lw=1.0)
        axn.text(6.45, ys, "SL", va="center", fontsize=6.5, color=GREEN)
    # cells: drain shared contact at BL between pairs
    for xb in bls:
        xc = xb + 0.55
        for (ya, yb_, ys, ycont) in ((6.2, 4.9, 5.55, None),):
            pass
        # pair 1 (WL0 upper cell, WL1 lower cell share source line 5.55); contacts at 6.85 and 4.25
        for yw, yc, ysrc in ((6.2, 6.85, 5.55), (4.9, 4.25, 5.55), (3.0, 3.65, 2.35), (1.7, 1.05, 2.35)):
            gpt = flash_cell(axn, xc, yw, h=0.5, gate="left", lead=0.0)
            sgn = 1 if yc > yw else -1
            wire(axn, [(xc, yw + sgn * 0.25), (xc, yc), (xb, yc)])
            wire(axn, [(xc, yw - sgn * 0.25), (xc, ysrc)])
            dot(axn, xc, ysrc, ms=2.5)
            dot(axn, xb, yc, ms=3)
            wire(axn, [gpt, (gpt[0] - 0.15, yw)], color=BLUE)
    axn.text(3.7, 0.25, "contact to BL shared by two cells; any word readable directly", fontsize=6.2,
             ha="center", va="center")

    # ---------- NAND string ----------
    axs = fig.add_axes([0.45, 0.0, 0.55, 0.47])
    axs.set_xlim(0, 9.5)
    axs.set_ylim(0, 8)
    axs.set_aspect("equal")
    axs.axis("off")
    axs.text(0.05, 7.85, "(d) NAND strings (32 cells in series)", fontsize=8.5, weight="bold", va="top")
    xs_ = [3.4, 5.1, 6.8]
    labels = ["WL31", "WL30", "WL29", None, "WL1", "WL0"]
    ycells = [5.55, 4.95, 4.35, None, 2.95, 2.35]
    for xs in xs_:
        wire(axs, [(xs, 7.0), (xs, 6.55)], lw=1.2)
        nmos_sym(axs, xs, 6.25, h=0.4, lead=0.1)
        wire(axs, [(xs, 5.95), (xs, 5.85)])
        for yc, lab in zip(ycells, labels):
            if yc is None:
                axs.text(xs, 3.65, "⋮", ha="center", va="center", fontsize=9)
                continue
            flash_cell(axs, xs, yc, h=0.42, lead=0.09)
        wire(axs, [(xs, 2.05), (xs, 1.95)])
        nmos_sym(axs, xs, 1.65, h=0.4, lead=0.1)
        wire(axs, [(xs, 1.35), (xs, 0.9)])
        axs.text(xs, 7.05, "BL", ha="center", va="bottom", fontsize=6.5)
    wire(axs, [(2.3, 0.9), (7.6, 0.9)], color=GREEN, lw=1.2)
    axs.text(7.65, 0.9, "source line", fontsize=6.3, va="center", color=GREEN)
    # gate lines across strings
    for yy, lab, col in [(6.25, "BL select (SSL)", INK), (1.65, "ground select (GSL)", INK)] + \
            [(yc, l, BLUE) for yc, l in zip(ycells, labels) if yc is not None]:
        off = 0.12 if "select" in lab else 0.2
        xprev = 2.3
        for xs in xs_:
            wire(axs, [(xprev, yy), (xs - off, yy)], color=col, lw=0.9)
            xprev = xs + 0.08
        axs.text(2.25, yy, lab, ha="right", va="center", fontsize=6.0, color=col)
    # page and block
    axs.add_patch(Rectangle((2.35, 4.35 - 0.24), 4.75, 0.48, fc=ORANGE, alpha=0.18, ec=ORANGE, lw=0.8))
    axs.text(7.65, 4.35, "page = one WL\nacross all strings", fontsize=6.2, va="center", color=ORANGE)
    axs.annotate("", xy=(8.7, 1.4), xytext=(8.7, 6.55),
                 arrowprops=dict(arrowstyle="-", lw=0.9, color=PINK))
    for yy in (1.4, 6.55):
        wire(axs, [(8.55, yy), (8.7, yy)], color=PINK, lw=0.9)
    axs.text(8.8, 2.6, "block =\nall pages\nof these\nstrings\n(erase\nunit)", fontsize=6.0, va="center",
             color=PINK)
    save(fig, "18", "fig-18-3-flash-cell-nor-nand")


# ----------------------------------------------------------------------------
def fig_18_4():
    """Island-style FPGA with hard-block columns and a switch-box inset."""
    fig, ax = schematic(6.8, 5.0, xlim=(-0.3, 17.6), ylim=(-0.9, 11.2))
    cols = ["CLB", "CLB", "CLB", "BRAM", "CLB", "CLB", "DSP", "CLB", "BRAM", "CLB"]
    nrow = 8
    p = 1.05                      # tile pitch
    x0, y0 = 1.3, 0.8
    cw = 0.56                     # CLB size
    # routing channels
    for i in range(len(cols) + 1):
        xc = x0 + i * p - (p - cw) / 2 - 0.0
        for k in (-0.06, 0.06):
            wire(ax, [(x0 + i * p - p / 2 + k + p / 2 - (p - cw) / 2 - 0.0, y0 - 0.25),
                      (x0 + i * p - p / 2 + k + p / 2 - (p - cw) / 2 - 0.0, y0 + nrow * p - 0.25)],
                 color="#9AA9B8", lw=0.5)
    for j in range(nrow + 1):
        for k in (-0.06, 0.06):
            yy = y0 + j * p - (p - cw) / 2 + k
            wire(ax, [(x0 - 0.25, yy), (x0 + len(cols) * p - 0.25, yy)], color="#9AA9B8", lw=0.5)
    # tiles
    for i, c in enumerate(cols):
        xt = x0 + i * p
        if c == "CLB":
            for j in range(nrow):
                if i in (0, 1, 2) and j >= nrow - 3:
                    continue                                   # processor corner
                yt = y0 + j * p
                rect(ax, xt, yt, cw, cw, fc=LUT_FC, lw=0.7)
                # connection boxes on the left and bottom channel
                rect(ax, xt - 0.2, yt + cw / 2 - 0.07, 0.1, 0.14, fc="#FFFFFF", lw=0.5)
                rect(ax, xt + cw / 2 - 0.07, yt - 0.2, 0.14, 0.1, fc="#FFFFFF", lw=0.5)
        elif c in ("BRAM", "DSP"):
            fc = HARD_FC if c == "BRAM" else DSP_FC
            for j in range(0, nrow, 2):
                yt = y0 + j * p
                rect(ax, xt, yt, cw, cw + p, fc=fc, lw=0.8)
                ax.text(xt + cw / 2, yt + (cw + p) / 2, c, rotation=90, ha="center", va="center",
                        fontsize=5.8)
    # switch boxes at channel intersections
    for i in range(len(cols) + 1):
        for j in range(nrow + 1):
            xs = x0 + i * p - (p - cw) / 2
            ys = y0 + j * p - (p - cw) / 2
            if i in (1, 2, 3) and j >= nrow - 2:
                continue
            ax.add_patch(Polygon([(xs - 0.11, ys), (xs, ys + 0.11), (xs + 0.11, ys), (xs, ys - 0.11)],
                                 closed=True, fc="#4A6A8A", ec="none"))
    # processor subsystem in the top-left corner
    xps0, yps0 = x0 - 0.1, y0 + (nrow - 3) * p - 0.1
    ax.add_patch(FancyBboxPatch((xps0, yps0), 3 * p - 0.25, 3 * p - 0.1, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="#FFF4D6", ec=INK, lw=1.0, zorder=3))
    ax.text(xps0 + 1.45, yps0 + 1.85, "hard processor\nsubsystem", ha="center", va="center",
            fontsize=6.8, weight="bold", zorder=4)
    ax.text(xps0 + 1.45, yps0 + 1.0, "dual Cortex-A9 or\nquad Cortex-A53", ha="center", va="center",
            fontsize=6.0, zorder=4)
    ax.annotate("", xy=(xps0 + 3 * p + 0.35, yps0 + 0.9), xytext=(xps0 + 3 * p - 0.25, yps0 + 0.9),
                arrowprops=dict(arrowstyle="<|-|>", lw=1.1, mutation_scale=7, color=ORANGE), zorder=4)
    ax.text(xps0 + 3 * p - 0.2, yps0 + 0.55, "AXI", fontsize=6, color=ORANGE, zorder=4)
    for j in (0, 3):
        pass
    # remove the column label 'PS' column: use for clock management instead
    xcm = x0 - 0.1
    for j in range(0, nrow - 3, 1):
        pass
    # I/O ring
    W = len(cols) * p
    Hh = nrow * p
    xr0, yr0 = x0 - 0.9, y0 - 0.85
    xr1, yr1 = x0 + W + 0.2, y0 + Hh + 0.1
    for xi in np.arange(xr0 + 0.55, xr1 - 0.3, 0.42):
        rect(ax, xi, yr1, 0.3, 0.3, fc="#E6E6E6", lw=0.5)
        rect(ax, xi, yr0 - 0.3, 0.3, 0.3, fc="#E6E6E6", lw=0.5)
    for yi in np.arange(yr0 + 0.1, yr1 - 0.1, 0.42):
        rect(ax, xr0 - 0.3, yi, 0.3, 0.3, fc="#E6E6E6", lw=0.5)
    ax.text((xr0 + xr1) / 2 - 2.0, yr1 + 0.45, "I/O bank (1.8 V)", ha="center", va="bottom", fontsize=6.8)
    ax.text((xr0 + xr1) / 2 + 2.2, yr1 + 0.45, "I/O bank (3.3 V)", ha="center", va="bottom", fontsize=6.8)
    wire(ax, [((xr0 + xr1) / 2 + 0.1, yr1 - 0.05), ((xr0 + xr1) / 2 + 0.1, yr1 + 0.65)], lw=1.0, ls=(0, (2, 1)))
    ax.text((xr0 + xr1) / 2, yr0 - 0.4, "I/O blocks (IOBs) grouped into banks", ha="center", va="top",
            fontsize=6.6)
    # transceivers on the right edge
    for yi in np.arange(y0, y0 + Hh - 0.2, 1.1):
        rect(ax, xr1 + 0.05, yi, 0.45, 0.85, fc="#D5EDDA", lw=0.6)
    ax.text(xr1 + 0.75, y0 + Hh / 2, "multi-gigabit transceivers", rotation=90, ha="center", va="center",
            fontsize=6.6)
    # clock management tiles (left of fabric, inside I/O ring) and global clock tree
    for yi in (y0 + 0.3, y0 + 2.6):
        rect(ax, xr0 + 0.08, yi, 0.5, 1.75, fc="#F6D6E4", lw=0.7)
        ax.text(xr0 + 0.33, yi + 0.87, "CMT: PLL/MMCM", rotation=90, ha="center", va="center", fontsize=5.2)
    yclk = y0 + 2.2
    wire(ax, [(xr0 + 0.58, y0 + 1.1), (xr0 + 0.75, y0 + 1.1), (xr0 + 0.75, yclk)], color=PINK, lw=1.2)
    wire(ax, [(xr0 + 0.75, yclk), (x0 + W - 0.4, yclk)], color=PINK, lw=1.2)
    for xc in np.arange(x0 + 3.5 * p - 0.25, x0 + W - 0.3, 2 * p):
        wire(ax, [(xc, y0 - 0.1), (xc, y0 + 4.6)], color=PINK, lw=0.7)
    ax.text(x0 + 4.8, yclk + 0.08, "global clock tree", fontsize=6, color=PINK, va="bottom",
            bbox=dict(fc="white", ec="none", pad=0.2))

    # inset: switch box
    ix0, iy0 = 13.9, 3.0
    ax.add_patch(FancyBboxPatch((ix0 - 0.35, iy0 - 1.05), 3.9, 5.65, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="white", ec=INK, lw=0.9))
    ax.text(ix0 + 1.6, iy0 + 4.45, "switch box (zoom)", ha="center", va="center", fontsize=7, weight="bold")
    cx, cy = ix0 + 1.6, iy0 + 2.0
    # four wire segments (W, E, N, S) that end short of the centre
    wire(ax, [(ix0, cy), (cx - 1.1, cy)], lw=1.3)
    wire(ax, [(cx + 1.1, cy), (ix0 + 3.2, cy)], lw=1.3)
    wire(ax, [(cx, cy + 1.1), (cx, iy0 + 3.9)], lw=1.3)
    wire(ax, [(cx, cy - 1.1), (cx, iy0 + 0.1)], lw=1.3)
    for tx, ty, t in ((ix0 + 0.05, cy + 0.12, "W"), (ix0 + 3.15, cy + 0.12, "E"),
                      (cx + 0.12, iy0 + 3.75, "N"), (cx + 0.12, iy0 + 0.25, "S")):
        ax.text(tx, ty, t, fontsize=6, ha="left" if t != "E" else "right", va="center")
    # pass transistors joining adjacent segments, each gated by an SRAM cell M
    for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        px, py = cx + sx * 0.6, cy + sy * 0.6
        wire(ax, [(cx + sx * 1.1, cy), (px + sx * 0.0, cy), (px, py - sy * 0.2)], lw=0.8, color="#555555") \
            if False else None
        wire(ax, [(cx + sx * 1.1, cy), (cx + sx * 1.1, py), (px + sx * 0.2, py)], lw=0.8, color="#555555")
        wire(ax, [(cx, cy + sy * 1.1), (px, cy + sy * 1.1), (px, py + sy * 0.2)], lw=0.8, color="#555555")
        ax.add_patch(Rectangle((px - 0.2, py - 0.2), 0.4, 0.4, fc="#DCEBF7", ec=INK, lw=0.7))
        ax.text(px, py, "PT", ha="center", va="center", fontsize=4.8)
        mx_, my_ = px + sx * 0.45, py + sy * 0.45
        wire(ax, [(px + sx * 0.2, py + sy * 0.2), (mx_, my_)], lw=0.6, color=PINK)
        ax.add_patch(Rectangle((mx_ - 0.14, my_ - 0.14), 0.28, 0.28, fc="#FFF4D6", ec=INK, lw=0.6))
        ax.text(mx_, my_, "M", ha="center", va="center", fontsize=4.5)
        dot(ax, cx + sx * 1.1, cy, ms=2.3)
        dot(ax, cx, cy + sy * 1.1, ms=2.3)
    ax.text(ix0 + 1.6, iy0 - 0.12, "each pass transistor (PT)\nis switched by one\nconfiguration SRAM cell (M)",
            ha="center", va="top", fontsize=5.9)
    # connector from a fabric switch box to inset
    sx_, sy_ = x0 + 9 * p - (p - cw) / 2, y0 + 5 * p - (p - cw) / 2
    ax.add_patch(Circle((sx_, sy_), 0.22, fc="none", ec=ORANGE, lw=1.1))
    wire(ax, [(sx_ + 0.22, sy_), (ix0 - 0.2, iy0 + 3.2)], color=ORANGE, lw=0.8, ls=(0, (3, 2)))
    # legend
    handles = [Patch(fc=LUT_FC, ec=INK, lw=0.7, label="CLB"),
               Patch(fc="white", ec=INK, lw=0.7, label="connection box"),
               Line2D([], [], marker="D", color="#4A6A8A", ls="none", ms=4, label="switch box"),
               Patch(fc=HARD_FC, ec=INK, lw=0.7, label="block RAM 36 Kb"),
               Patch(fc=DSP_FC, ec=INK, lw=0.7, label="DSP: 25×18 mult + 48-bit acc")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=5, fontsize=6.5,
              handlelength=1.2, columnspacing=1.0)
    save(fig, "18", "fig-18-4-fpga-island-architecture")


# ----------------------------------------------------------------------------
def fig_18_5():
    """4-input LUT as a mux tree (INIT = 0x8FF8) and a 6-LUT logic slice."""
    fig, ax = schematic(6.8, 5.2, xlim=(-0.2, 16.6), ylim=(-1.3, 12.2))
    init = 0x8FF8
    # SRAM bits
    ytop, dy = 10.3, 0.62
    ys = [ytop - i * dy for i in range(16)]
    for i, y in enumerate(ys):
        b = (init >> i) & 1
        rect(ax, 0.6, y - 0.24, 0.55, 0.48, fc="#FFF4D6" if b else "white", lw=0.7)
        ax.text(0.875, y, str(b), ha="center", va="center", fontsize=7, family="DejaVu Sans Mono")
        ax.text(0.5, y, f"{i}", ha="right", va="center", fontsize=5.6, color="#666666")
    ax.text(0.875, ytop + 0.45, "INIT\n16'h8FF8", ha="center", va="bottom", fontsize=6.5)
    # mux tree
    levels = [8, 4, 2, 1]
    xs_l = [2.0, 3.1, 4.2, 5.3]
    sel = ["a", "b", "c", "d"]
    prev = [(1.15, y) for y in ys]
    outs = None
    for L, (n, xm) in enumerate(zip(levels, xs_l)):
        cur = []
        for k in range(n):
            ya, yb = prev[2 * k][1], prev[2 * k + 1][1]
            yc = (ya + yb) / 2
            hgt = max(0.55, (ya - yb) * 0.75)
            in0, in1, out, s = mux2(ax, xm, yc, w=0.32, h=hgt)
            wire(ax, [prev[2 * k], (xm - 0.35, ya), (xm - 0.35, in0[1]), in0], lw=0.8)
            wire(ax, [prev[2 * k + 1], (xm - 0.35, yb), (xm - 0.35, in1[1]), in1], lw=0.8)
            ax.text(in0[0] + 0.03, in0[1], "0", fontsize=4.5, va="center")
            ax.text(in1[0] + 0.03, in1[1], "1", fontsize=4.5, va="center")
            cur.append(out)
            # select stub
            wire(ax, [s, (s[0], s[1] - 0.18)], lw=0.7, color=BLUE)
        prev = cur
        ax.text(xm, -0.05, sel[L], ha="center", va="center", fontsize=8, color=BLUE, weight="bold")
        # select bus line
        wire(ax, [(xm, 0.15), (xm, 0.35)], color=BLUE, lw=0.7)
    for xm in xs_l:
        ax.add_patch(Polygon([(xm - 0.1, 0.35), (xm + 0.1, 0.35), (xm, 0.5)], closed=True, fc=BLUE, ec="none"))
        ax.plot([xm, xm], [0.5, 10.5], color=BLUE, lw=0.4, ls=(0, (1, 2)), zorder=0)
    wire_arrow(ax, [prev[0], (6.2, prev[0][1])], ms=7)
    ax.text(6.25, prev[0][1], "F", fontsize=9, va="center", weight="bold")
    ax.text(3.6, -0.55, "select inputs (a drives the first level)", ha="center", va="center", fontsize=6.5,
            color=BLUE)
    ax.text(3.2, 11.85, "(a) 4-input LUT: 16 SRAM bits + mux tree", ha="center", va="center",
            fontsize=8, weight="bold")

    # ---------------- slice ----------------
    sx0, sx1, sy0, sy1 = 7.3, 16.4, 0.0, 10.9
    ax.add_patch(FancyBboxPatch((sx0, sy0), sx1 - sx0, sy1 - sy0, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#FAFAFA", ec=INK, lw=1.0, zorder=0))
    ax.text((sx0 + sx1) / 2, 11.85, "(b) Logic slice (7-series style)", ha="center", va="center",
            fontsize=8, weight="bold")
    lut_h, lut_w = 1.7, 1.6
    xl = 8.2
    ylut = [8.6, 6.1, 3.6, 1.1]
    names = "DCBA"
    xc = 10.75                       # carry column centre
    xff = 14.1
    for k, y in enumerate(ylut):
        rect(ax, xl, y, lut_w, lut_h, fc=LUT_FC)
        ax.text(xl + lut_w / 2, y + lut_h / 2 + 0.2, f"LUT6 {names[k]}", ha="center", va="center", fontsize=7)
        ax.text(xl + lut_w / 2, y + lut_h / 2 - 0.3, "or 2 × LUT5", ha="center", va="center", fontsize=5.8)
        for q in range(6):
            yy = y + 0.2 + q * (lut_h - 0.4) / 5
            wire(ax, [(xl - 0.35, yy), (xl, yy)], lw=0.6)
        ax.text(xl - 0.4, y + lut_h / 2, "6", fontsize=5.8, ha="right", va="center")
        ax.text(xl + lut_w - 0.05, y + 1.4, "O6", fontsize=5.5, ha="right", va="center")
        ax.text(xl + lut_w - 0.05, y + 0.3, "O5", fontsize=5.5, ha="right", va="center")
        # O6 and O5 run through the carry logic to the two flip-flops of this LUT
        wire(ax, [(xl + lut_w, y + 1.4), (xff, y + 1.4)], lw=0.8, zorder=1)
        wire(ax, [(xl + lut_w, y + 0.3), (xff, y + 0.3)], lw=0.8, zorder=1)
        for yo in (y + 1.15, y + 0.05):
            rect(ax, xff, yo, 0.95, 0.5, fc=FF_FC, lw=0.8)
            ax.text(xff + 0.475, yo + 0.25, "FF", fontsize=6, ha="center", va="center")
            wire_arrow(ax, [(xff + 0.95, yo + 0.25), (sx1 - 0.12, yo + 0.25)], ms=5)
    # carry chain column (drawn over the LUT output wires)
    ax.add_patch(Rectangle((xc - 0.45, 0.55), 0.9, 10.0, fc="#F3F7EC", ec=INK, lw=0.8, zorder=2))
    ax.text(xc, 10.32, "CARRY4", fontsize=5.6, ha="center", va="center", zorder=3)
    ax.plot([xc, xc], [0.55, 10.55], color=GREEN, lw=1.0, zorder=2.5, alpha=0.7)
    for y in ylut:
        ym = y + lut_h / 2
        ax.add_patch(Polygon([(xc - 0.28, ym + 0.08), (xc + 0.28, ym + 0.08), (xc + 0.17, ym + 0.42),
                              (xc - 0.17, ym + 0.42)], closed=True, fc="white", ec=INK, lw=0.7, zorder=3))
        ax.text(xc, ym + 0.25, "MUXCY", fontsize=3.8, ha="center", va="center", zorder=4)
        ax.add_patch(Circle((xc, ym - 0.3), 0.17, fc="white", ec=INK, lw=0.7, zorder=3))
        ax.text(xc, ym - 0.3, "⊕", fontsize=6, ha="center", va="center", zorder=4)
    wire_arrow(ax, [(xc, -0.45), (xc, 0.55)], ms=6, color=GREEN)
    ax.text(xc + 0.12, -0.35, "CIN", fontsize=6, va="center", color=GREEN)
    wire_arrow(ax, [(xc, 10.55), (xc, 11.25)], ms=6, color=GREEN)
    ax.text(xc + 0.12, 11.1, "COUT", fontsize=6, va="center", color=GREEN)
    # F7 / F8 wide-function multiplexers fed from the O6 outputs
    xf = 12.3
    f7a = mux2(ax, xf, (ylut[0] + ylut[1]) / 2 + lut_h / 2, w=0.4, h=0.9)
    f7b = mux2(ax, xf, (ylut[2] + ylut[3]) / 2 + lut_h / 2, w=0.4, h=0.9)
    f8 = mux2(ax, xf + 0.85, (ylut[1] + ylut[2]) / 2 + lut_h / 2, w=0.4, h=0.9)
    for (ytop_, ybot_, m) in ((ylut[0] + 1.4, ylut[1] + 1.4, f7a), (ylut[2] + 1.4, ylut[3] + 1.4, f7b)):
        wire(ax, [(11.55, ytop_), (11.55, m[0][1]), m[0]], lw=0.7)
        wire(ax, [(11.8, ybot_), (11.8, m[1][1]), m[1]], lw=0.7)
        dot(ax, 11.55, ytop_, ms=2.4)
        dot(ax, 11.8, ybot_, ms=2.4)
    ax.text(xf, f7a[2][1] + 0.55, "F7", fontsize=6, ha="center")
    ax.text(xf, f7b[2][1] + 0.55, "F7", fontsize=6, ha="center")
    ax.text(xf + 0.85, f8[2][1] + 0.55, "F8", fontsize=6, ha="center")
    wire(ax, [f7a[2], (xf + 0.42, f7a[2][1]), (xf + 0.42, f8[0][1]), f8[0]], lw=0.7)
    wire(ax, [f7b[2], (xf + 0.42, f7b[2][1]), (xf + 0.42, f8[1][1]), f8[1]], lw=0.7)
    wire_arrow(ax, [f8[2], (xff - 0.15, f8[2][1])], lw=0.8, ms=5)
    ax.text(f8[2][0] + 0.08, f8[2][1] + 0.1, "F8 out", fontsize=5.2, va="bottom")
    # bypass from LUT D straight to a slice output
    yD = ylut[0] + 1.4
    wire(ax, [(13.75, yD), (13.75, sy1 - 0.35), (sx1 - 0.12, sy1 - 0.35)], lw=0.9, color=ORANGE,
         ls=(0, (3, 2)))
    dot(ax, 13.75, yD, color=ORANGE, ms=2.4)
    ax.text(13.85, sy1 - 0.25, "bypass (combinational out)", fontsize=5.6, color=ORANGE, va="bottom")
    ax.text(xff + 0.475, -0.05, "CE, SR, CLK\nto all 8 FFs", fontsize=5.6, ha="center", va="top")
    # SLICEM note
    ax.text(7.45, -0.12, "SLICEM: each LUT\nalso usable as 64×1\nRAM or 32-bit shift\nregister (SRL32)",
            fontsize=5.8, ha="left", va="top", color="#555555")
    save(fig, "18", "fig-18-5-lut-and-slice")


# ----------------------------------------------------------------------------
def fig_18_6():
    """CPLD architecture: function blocks around a global interconnect matrix."""
    fig, ax = schematic(6.8, 5.2, xlim=(-0.2, 16.4), ylim=(-0.5, 12.6))
    # interconnect matrix
    mx0, mx1, my0, my1 = 7.2, 8.8, 3.95, 11.7
    rect(ax, mx0, my0, mx1 - mx0, my1 - my0, fc="#FBE7D3", lw=1.1)
    ax.text((mx0 + mx1) / 2, (my0 + my1) / 2, "programmable interconnect matrix", rotation=90,
            ha="center", va="center", fontsize=7.5)
    ax.text((mx0 + mx1) / 2, my1 + 0.1, "all I/O pins and\nmacrocell feedback in", ha="center",
            va="bottom", fontsize=6.3)
    # function blocks
    fbw, fbh = 6.4, 3.75
    fbs = [(0.3, 7.95, "FB 1"), (0.3, 3.95, "FB 2"), (9.7, 7.95, "FB 3"), (9.7, 3.95, "FB 4")]
    for (fx, fy, name) in fbs:
        right = fx > 8
        ax.add_patch(FancyBboxPatch((fx, fy), fbw, fbh, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#F7F7F7", ec=INK, lw=1.0))
        ax.text(fx + 0.15, fy + fbh - 0.12, name, fontsize=7, weight="bold", va="top")
        # AND array grid
        gx, gy, gw, gh = fx + 0.3, fy + 0.6, 2.6, 2.2
        rect(ax, gx, gy, gw, gh, fc="white", lw=0.7)
        for i in range(9):
            wire(ax, [(gx + 0.15 + i * 0.29, gy), (gx + 0.15 + i * 0.29, gy + gh)], lw=0.4, color="#7A8FA6")
        for j in range(7):
            wire(ax, [(gx, gy + 0.15 + j * 0.315), (gx + gw, gy + 0.15 + j * 0.315)], lw=0.4, color="#7A8FA6")
        rng = np.random.default_rng(len(name) + int(fx) + int(fy))
        for i in range(9):
            for j in range(7):
                if rng.random() < 0.28:
                    ax.text(gx + 0.15 + i * 0.29, gy + 0.15 + j * 0.315, "×", fontsize=6, ha="center",
                            va="center", color=BLUE)
        ax.text(gx + gw / 2, gy - 0.08, "AND array: 40 inputs × 56 PTs", fontsize=5.8, ha="center",
                va="top")
        # PT allocator and macrocells
        rect(ax, fx + 3.1, gy, 1.0, gh, fc="#E3F2E6", lw=0.8)
        ax.text(fx + 3.6, gy + gh / 2, "PT\nalloc-\nator", fontsize=6, ha="center", va="center")
        rect(ax, fx + 4.3, gy, 1.9, gh, fc="#DCEBF7", lw=0.8)
        for j in range(6):
            rect(ax, fx + 4.42, gy + 0.1 + j * 0.34, 1.66, 0.27, fc="white", lw=0.4)
        ax.text(fx + 5.25, gy - 0.08, "16 macrocells", fontsize=5.8, ha="center", va="top")
        wire_arrow(ax, [(gx + gw, gy + gh / 2), (fx + 3.1, gy + gh / 2)], ms=6)
        wire_arrow(ax, [(fx + 4.1, gy + gh / 2), (fx + 4.3, gy + gh / 2)], ms=6)
        # connections to the matrix: 40 inputs in, macrocell feedback out
        yin = fy + fbh - 0.45
        xin = fx + 1.6
        xm_side = mx0 if not right else mx1
        wire(ax, [(xm_side, yin), (xin, yin)], color=BLUE, lw=1.0)
        wire_arrow(ax, [(xin, yin), (xin, gy + gh)], color=BLUE, ms=6)
        ax.text((xm_side + (fx + fbw if not right else fx)) / 2, yin + 0.06, "40", fontsize=5.6, color=BLUE,
                ha="center", va="bottom")
        yfb = gy + 0.45
        if not right:
            wire_arrow(ax, [(fx + 6.2, yfb), (mx0, yfb)], ms=6, color=GREEN)
        else:
            wire(ax, [(fx + 6.2, yfb), (fx + 6.32, yfb), (fx + 6.32, fy + 0.12), (mx1 + 0.3, fy + 0.12),
                      (mx1 + 0.3, yfb)], color=GREEN, lw=1.0)
            wire_arrow(ax, [(mx1 + 0.3, yfb), (mx1, yfb)], ms=6, color=GREEN)
    # macrocell zoom
    zy = 0.2
    ax.add_patch(FancyBboxPatch((0.3, zy - 0.35), 15.8, 3.55, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="white", ec=INK, lw=0.9))
    ax.text(0.45, zy + 3.05, "one macrocell (zoom)", fontsize=7, weight="bold", va="center")
    # product terms in
    for k in range(5):
        wire(ax, [(0.6, zy + 0.6 + k * 0.38), (1.9, zy + 0.6 + k * 0.38)], lw=0.8)
    ax.text(0.6, zy + 0.25, "5 local PTs", fontsize=5.8, va="center")
    wire(ax, [(0.6, zy + 2.45), (1.95, zy + 2.45)], lw=0.8, ls=(0, (3, 2)))
    ax.text(0.5, zy + 2.5, "borrowed PTs", fontsize=5.3, va="bottom")
    # OR gate (simple shape)
    ox, oy = 1.9, zy + 1.45
    t = np.linspace(0, 1, 30)
    top = [(ox + s * 1.2, oy + 1.35 * (1 - s ** 2)) for s in t]
    bot = [(ox + s * 1.2, oy - 1.35 * (1 - s ** 2)) for s in t[::-1]]
    back = [(ox + 0.3 * (1 - u ** 2), oy + u * 1.35) for u in np.linspace(-1, 1, 30)]
    ax.add_patch(Polygon(top + bot + back, closed=True, fc="white", ec=INK, lw=1.0))
    ax.text(ox + 0.6, oy, "OR", fontsize=6.5, ha="center", va="center")
    # XOR polarity
    xx = 4.0
    wire(ax, [(ox + 1.2, oy), (xx, oy)])
    ax.add_patch(Circle((xx + 0.35, oy), 0.35, fc="white", ec=INK, lw=1.0))
    ax.text(xx + 0.35, oy, "⊕", fontsize=9, ha="center", va="center")
    ax.text(xx + 0.35, oy - 0.55, "polarity", fontsize=5.8, ha="center", va="top")
    # flip-flop
    fx_ = 5.6
    wire(ax, [(xx + 0.7, oy), (fx_, oy)])
    rect(ax, fx_, zy + 0.3, 2.0, 2.4, fc=FF_FC)
    ax.text(fx_ + 1.0, zy + 2.3, "D/T FF", fontsize=7, ha="center", va="center", weight="bold")
    ax.text(fx_ + 0.1, oy, "D/T", fontsize=5.8, va="center")
    ax.text(fx_ + 1.9, oy, "Q", fontsize=5.8, va="center", ha="right")
    ax.text(fx_ + 1.0, zy + 0.55, "S   R", fontsize=5.8, ha="center", va="center")
    ax.add_patch(Polygon([(fx_, zy + 0.85), (fx_ + 0.18, zy + 1.0), (fx_, zy + 1.15)], closed=True, fc="none",
                         ec=INK, lw=0.8))
    wire(ax, [(fx_ - 0.35, zy + 0.0), (fx_ - 0.35, zy + 1.0), (fx_, zy + 1.0)], lw=0.8)
    ax.text(fx_ - 0.45, zy + 0.02, "GCK or PT clock", fontsize=5.6, ha="right", va="center")
    # bypass mux and output enable
    mxx = 8.3
    in0, in1, out, s = mux2(ax, mxx, oy, w=0.4, h=1.0)
    wire(ax, [(fx_ + 2.0, oy), (mxx - 0.45, oy), (mxx - 0.45, in0[1]), in0], lw=0.9)
    wire(ax, [(xx + 0.85, oy), (xx + 0.85, zy + 2.85), (mxx - 0.6, zy + 2.85), (mxx - 0.6, in1[1] + 0.0),
              (mxx - 0.2, in1[1] + 0.0)], lw=0.8, ls=(0, (3, 2)))
    dot(ax, xx + 0.85, oy, ms=2.5)
    ax.text(mxx - 0.6, zy + 2.95, "combinational bypass", fontsize=5.6, va="bottom")
    # tri-state buffer
    bx = 9.5
    wire(ax, [out, (bx, oy)])
    ax.add_patch(Polygon([(bx, oy - 0.45), (bx, oy + 0.45), (bx + 0.8, oy)], closed=True, fc="white", ec=INK,
                         lw=1.0))
    wire(ax, [(bx + 0.4, oy + 0.23), (bx + 0.4, oy + 0.9)], lw=0.8)
    ax.text(bx + 0.45, oy + 0.95, "output enable", fontsize=5.8, va="bottom")
    wire(ax, [(bx + 0.8, oy), (11.3, oy)])
    rect(ax, 11.3, oy - 0.3, 0.6, 0.6, fc="#D9D9D9")
    ax.text(12.0, oy, "I/O pin", fontsize=6.5, va="center")
    # feedback
    wire_arrow(ax, [(10.9, oy), (10.9, zy - 0.05), (13.1, zy - 0.05)], ms=6, color=GREEN)
    dot(ax, 10.9, oy, ms=2.5)
    ax.text(13.15, zy - 0.05, "feedback to matrix", fontsize=5.8, va="center", color=GREEN)
    # annotation box
    ax.text(15.95, zy + 1.45, "pin-to-pin $t_{PD}$ ≈ 5 ns\n(placement-independent)\n\nnon-volatile flash\n"
            "configuration: instant-on\n\n64–512 macrocells", fontsize=5.9, ha="right", va="center",
            bbox=dict(fc="#FFF4D6", ec=INK, lw=0.7, boxstyle="round,pad=0.35"))
    save(fig, "18", "fig-18-6-cpld-architecture")


if __name__ == "__main__":
    fig_18_1()
    fig_18_2()
    fig_18_3()
    fig_18_4()
    fig_18_5()
    fig_18_6()
