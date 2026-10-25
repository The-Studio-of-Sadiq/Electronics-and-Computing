"""Figures for Chapter 15 — Digital System Design.

Run from the repository root:  python figures/scripts/ch15.py
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


def arr2(ax, pts, col=INK, lw=1.2, ls="-", ms=9):
    """Polyline with an arrowhead at the last point."""
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=col, lw=lw, ls=ls, solid_joinstyle="miter")
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, shrinkA=0, shrinkB=0,
                                mutation_scale=ms))


# ----------------------------------------------------------------------------
def fig_15_1():
    """Design flow with paired verification activities (V-shaped)."""
    fig, ax = plt.subplots(figsize=(6.8, 5.6))
    ax.set_xlim(0, 14.2)
    ax.set_ylim(-0.2, 10.2)
    ax.set_aspect("equal")
    ax.axis("off")
    steps = ["Requirements", "Specification",
             "Architecture: datapath +\ncontrol, clock domains", "State diagrams / ASM charts",
             "RTL (Verilog / VHDL)", "Synthesis", "Place and route", "Bitstream or GDSII",
             "Hardware bring-up"]
    checks = ["Requirements review", "Spec review and test plan",
              "Architecture review with timing\nand resource estimate",
              "State-table and reachability check",
              "RTL simulation: self-checking\ntest bench and coverage",
              "Lint and CDC check",
              "Static timing analysis\n(setup, hold, recovery)",
              "Gate-level simulation (optional)", "Validation in system"]
    bh, gap = 0.78, 1.08
    lw_, rw_ = 4.6, 5.5
    ax.text(0.1 + lw_ / 2, 9.95, "Design steps", ha="center", fontsize=10, fontweight="bold",
            color=BLUE)
    ax.text(8.6 + rw_ / 2 - 0.7, 9.95, "Paired verification", ha="center", fontsize=10,
            fontweight="bold", color=COLORS[1])
    for i, (st, ck) in enumerate(zip(steps, checks)):
        y = 9.0 - i * gap
        xl = 0.1 + i * 0.18
        xr = 8.6 - i * 0.18
        box(ax, xl, y, lw_, bh, st, fc="#E3F0FA", fontsize=7.8)
        box(ax, xr, y, rw_, bh, ck, fc="#FDEEE3", fontsize=7.5)
        yc = y + bh / 2
        # dashed pairing line with feedback arrowhead pointing back at the step
        ax.annotate("", xy=(xl + lw_ + 0.05, yc), xytext=(xr - 0.05, yc),
                    arrowprops=dict(arrowstyle="-|>", color="#777777", lw=1.0, ls="--",
                                    shrinkA=0, shrinkB=0, mutation_scale=9))
        if i < len(steps) - 1:
            yn = 9.0 - (i + 1) * gap + bh
            arrow(ax, xl + 1.4, y, xl + 1.4, yn)
    ax.text(7.0, -0.1, "dashed: each check feeds back to the step it tests; failures loop back "
            "(e.g. timing → architecture)", ha="center", fontsize=7.5, color="#555555")
    save(fig, "15", "fig-15-1-design-flow")


def fig_15_2():
    """Moore state diagram of the laser interlock."""
    from matplotlib.patches import Circle, FancyArrowPatch
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    ax.set_xlim(-0.6, 14.6)
    ax.set_ylim(-0.4, 11.2)
    ax.set_aspect("equal")
    ax.axis("off")
    R = 1.2
    pos = {"SAFE": (3.5, 7.6), "ARMED": (10.5, 7.6), "FIRE": (10.5, 2.6), "FAULT": (3.5, 2.6)}
    info = {"SAFE": ("00", "outputs off"), "ARMED": ("01", "ready_lamp"),
            "FIRE": ("11", "laser_en"), "FAULT": ("10", "fault_lamp")}
    fcs = {"SAFE": "#E8F5E9", "ARMED": "#FFF8E1", "FIRE": "#FFEBEE", "FAULT": "#ECEFF1"}
    circ = {}
    for k, (x, y) in pos.items():
        c = Circle((x, y), R, fc=fcs[k], ec=INK, lw=1.4, zorder=2)
        ax.add_patch(c)
        circ[k] = c
        code, out = info[k]
        ax.text(x, y + 0.35, k, ha="center", va="center", fontsize=10, fontweight="bold",
                zorder=3)
        ax.text(x, y - 0.1, code, ha="center", va="center", fontsize=9, zorder=3)
        ax.text(x, y - 0.5, out, ha="center", va="center", fontsize=7.5, zorder=3,
                color="#333333")

    def edge(a, b, rad, col=INK, lw=1.3):
        p = FancyArrowPatch(pos[a], pos[b], patchA=circ[a], patchB=circ[b],
                            connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                            mutation_scale=12, color=col, lw=lw, shrinkA=2, shrinkB=2,
                            zorder=1)
        ax.add_patch(p)

    def loop(k, ang, col=INK):
        x, y = pos[k]
        a1, a2 = np.radians(ang + 28), np.radians(ang - 28)
        p1 = (x + R * np.cos(a1), y + R * np.sin(a1))
        p2 = (x + R * np.cos(a2), y + R * np.sin(a2))
        p = FancyArrowPatch(p1, p2, connectionstyle="arc3,rad=-1.9", arrowstyle="-|>",
                            mutation_scale=11, color=col, lw=1.2, shrinkA=0, shrinkB=0,
                            zorder=1)
        ax.add_patch(p)

    def lab(x, y, s, col=INK, ha="center"):
        ax.text(x, y, s, ha=ha, va="center", fontsize=9, color=col,
                bbox=dict(fc="white", ec="none", pad=0.15), zorder=4)

    edge("SAFE", "ARMED", -0.22)
    lab(7.0, 9.2, r"$D\,K\,\overline{E}$")
    edge("ARMED", "SAFE", -0.22)
    lab(7.0, 6.55, r"$\overline{DK}\;\overline{E}$")
    edge("ARMED", "FIRE", -0.25)
    lab(11.55, 5.1, r"$D\,K\,F\,\overline{E}$", ha="left")
    edge("FIRE", "ARMED", -0.25)
    lab(9.5, 5.1, r"$D\,K\,\overline{F}\,\overline{E}$", ha="right")
    edge("FIRE", "FAULT", -0.18)
    lab(7.0, 1.2, r"$\overline{DK}+E$")
    edge("FAULT", "SAFE", -0.25)
    lab(2.35, 5.1, r"$\overline{K}\,\overline{E}$", ha="right")
    edge("SAFE", "FAULT", -0.25, RED)
    lab(4.25, 5.4, r"$E$", RED, ha="left")
    edge("ARMED", "FAULT", 0.0, RED)
    lab(5.3, 4.2, r"$E$", RED)
    loop("SAFE", 135)
    lab(1.1, 9.55, r"$\overline{DK}\;\overline{E}$")
    loop("ARMED", 45)
    lab(12.9, 9.55, r"$D\,K\,\overline{F}\,\overline{E}$")
    loop("FIRE", -45)
    lab(12.9, 0.65, r"$D\,K\,F\,\overline{E}$")
    loop("FAULT", -135)
    lab(1.1, 0.65, r"$K+E$")
    # reset arrow
    x, y = pos["SAFE"]
    arr2(ax, [(x, y + R + 1.4), (x, y + R + 0.02)], INK, 1.3)
    ax.text(x + 0.15, y + R + 1.1, "rst_n", fontsize=9, va="center", ha="left")
    ax.text(14.6, 11.0, "D door closed, K key on, F fire request, E fault\nred: fault entry",
            fontsize=7.5, ha="right", va="top", color="#444444")
    save(fig, "15", "fig-15-2-interlock-state-diagram")


def fig_15_3():
    """System-synchronous ADC capture at 65 MHz."""
    fig = plt.figure(figsize=(6.8, 5.8))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.7, 1.5], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.3, 0.3), 6.2, 3.3, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#F3F6FA", ec=INK, lw=1.2))
    ax.text(0.5, 3.35, "FPGA", fontsize=9.5, fontweight="bold", va="center")
    box(ax, 0.7, 1.9, 1.8, 0.9, "internal\nclock", fc="white", fontsize=8)
    # clock output buffer
    ax.add_patch(Polygon([(4.4, 2.05), (4.4, 2.65), (4.95, 2.35)], closed=True, fc="white",
                         ec=INK, lw=1.1))
    ax.text(4.65, 2.8, "output clock\nbuffer", fontsize=7, ha="center", va="bottom")
    ax.plot([2.5, 4.4], [2.35, 2.35], color=INK, lw=1.2)
    ax.plot([4.95, 6.5], [2.35, 2.35], color=INK, lw=1.2)
    p = dff(ax, 3.9, 0.75, "", w=1.3, h=1.1, fs=7.5)
    ax.text(5.3, 1.3, "capture\nFFs", fontsize=7, ha="left", va="center")
    ax.plot([3.2, 3.2, p["CLK"][0]], [2.35, p["CLK"][1], p["CLK"][1]], color=INK, lw=1.1)
    ax.plot([3.2], [2.35], "o", ms=3.5, color=INK)
    # ADC
    ax.add_patch(FancyBboxPatch((11.3, 0.3), 3.6, 3.3, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#F3F6FA", ec=INK, lw=1.2))
    ax.text(11.5, 3.3, "ADC", fontsize=9.5, fontweight="bold", va="center")
    ax.text(11.5, 2.95, "12 bit, 65 MSPS", fontsize=7.5, va="center")
    ax.text(11.45, 2.35, "CLK in", fontsize=8, va="center")
    ax.text(11.45, 0.6, "D[11:0] out", fontsize=8, va="center")
    arr2(ax, [(6.5, 2.35), (11.3, 2.35)], COLORS[0], 1.4)
    ax.text(8.9, 2.45, "clock trace 10 cm, 0.6 ns", fontsize=7.5, ha="center", va="bottom",
            color=COLORS[0])
    ax.plot([11.3, 6.5], [0.6, 0.6], color=COLORS[1], lw=3.0)
    ax.annotate("", xy=(6.5, 0.6), xytext=(7.0, 0.6),
                arrowprops=dict(arrowstyle="-|>", color=COLORS[1], lw=1.4, mutation_scale=10,
                                shrinkA=0, shrinkB=0))
    ax.plot([6.5, 3.6, 3.6, p["D"][0]], [0.6, 0.6, p["D"][1], p["D"][1]], color=COLORS[1], lw=1.4)
    ax.text(8.9, 0.7, "data traces 10 cm, 0.6 ns", fontsize=7.5, ha="center", va="bottom",
            color=COLORS[1])

    # ---------------- timing ----------------
    ax = fig.add_subplot(gs[1])
    h, s = 0.5, 0.25
    T = 15.38
    names = ["CLK_int (FPGA)", "CLK at ADC pin", "D at ADC pins", "D at FPGA pins",
             "CLK_int at 100 MHz"]
    ys = [5.2, 4.0, 2.8, 1.6, 0.2]
    for k in range(0, 19, 1):
        ax.axvline(k, color=GRID, lw=0.5, zorder=0)
    wave(ax, ys[0], -0.5, 18, [(0, 1), (T / 2, 0), (T, 1)], init=0, h=h, s=s)
    wave(ax, ys[1], -0.5, 18, [(4.1, 1), (4.1 + T / 2, 0)], init=0, h=h, s=s,
         color=COLORS[0])
    bus(ax, ys[2], [(-0.5, 6.1, "sample n−1", "valid", None), (6.1, 11.1, "", "hatch", None),
                    (11.1, 18, "sample n", "valid", None)], h=h, s=s, t0=-0.5, t1=18, fs=7.5)
    bus(ax, ys[3], [(-0.5, 6.7, "sample n−1", "valid", None), (6.7, 11.7, "", "hatch", None),
                    (11.7, 18, "sample n", "valid", GREEN)], h=h, s=s, t0=-0.5, t1=18, fs=7.5)
    # setup window and slack at 65 MHz
    ax.add_patch(Rectangle((T - 2.0, ys[3] - 0.15), 2.0, ys[0] + h + 0.15 - ys[3] + 0.15,
                           fc="#FFE0B2", ec="none", zorder=0))
    ax.add_patch(Rectangle((11.7, ys[3]), T - 2.0 - 11.7, h, fc="#A5D6A7", ec="none",
                           zorder=0.5, alpha=0.8))
    dim(ax, 11.7, T - 2.0, ys[3] - 0.22, "slack 1.68 ns", GREEN, fs=7.5, above=False)
    ax.text(T - 1.0, ys[0] + h + 0.2, r"$t_{su}$ = 2.0 ns" "\n(13.38 → 15.38)", fontsize=7,
            ha="center", va="bottom", color="#B26A00")
    # delay annotations
    dim(ax, 0, 4.1, ys[1] + h + 0.1, "3.5 + 0.6 = 4.1 ns", fs=7, dy=0.04)
    dim(ax, 4.1, 11.1, ys[2] + h + 0.1, r"$t_{OD}$ max 7.0 ns", fs=7, dy=0.04)
    ax.text(6.1, ys[2] - 0.08, "6.1 (min)", fontsize=6.5, ha="center", va="top")
    ax.text(6.7, ys[3] - 0.08, "6.7 (min)", fontsize=6.5, ha="center", va="top")
    ax.text(11.7, ys[3] + h + 0.08, "11.7", fontsize=6.5, ha="center", va="bottom")
    # 100 MHz comparison
    grey = "#9E9E9E"
    wave(ax, ys[4], -0.5, 18, [(0, 1), (5, 0), (10, 1), (15, 0)], init=0, h=h, s=s, color=grey)
    ax.add_patch(Rectangle((8.0, ys[4] - 0.1), 2.0, h + 0.2, fc="#FFCDD2", ec="none", zorder=0))
    ax.plot([11.7, 11.7], [ys[4] - 0.1, ys[3] + h], color=RED, lw=0.9, ls=":")
    dim(ax, 8.0, 11.7, ys[4] - 0.22, "slack −3.7 ns", RED, fs=7.5, above=False)
    ax.text(12.0, ys[4] - 0.22, "100 MHz: edge at 10 ns falls\ninside the invalid window",
            fontsize=7, color=RED, ha="left", va="top")
    rows_axis(ax, names, ys, h, -0.8, fs=8.5)
    ax.set_xlim(-0.5, 18)
    ax.set_ylim(-0.8, ys[0] + h + 0.9)
    ax.set_xticks(range(0, 19, 2))
    ax.set_xlabel("Time from internal clock edge (ns)")
    save(fig, "15", "fig-15-3-adc-interface-timing")


def fig_15_4():
    """Static-1 hazard in a mux, and the laser decode glitch."""
    fig = plt.figure(figsize=(6.8, 5.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.62, 1.6], width_ratios=[1.15, 1.0],
                          hspace=0.06, wspace=0.12)
    # ---- schematic ----
    ax = fig.add_subplot(gs[0, 0])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=9, lw=1.1)
    a1 = place(d, logic.And, 4.6, 3.0)
    a2 = place(d, logic.And, 4.6, 1.0)
    o1 = place(d, logic.Or, 8.4, 2.2)
    inv = d.add(logic.Not().at((2.3, 2.35)).anchor("in1").scale(1.0))
    d.draw(show=False)
    wire(ax, [(0.2, 3.0), (4.6, 3.0)])
    ax.text(0.1, 3.0, "A", ha="right", va="center", fontsize=9)
    yb = a2.absanchors["in2"].y
    wire(ax, [(0.2, yb), (4.6, yb)])
    ax.text(0.1, yb, "B", ha="right", va="center", fontsize=9)
    wire(ax, [(0.2, 1.0), (4.6, 1.0)])
    ax.text(0.1, 1.0, "S", ha="right", va="center", fontsize=9)
    st = inv.absanchors["start"]
    en = inv.absanchors["end"]
    wire(ax, [(0.9, 1.0), (0.9, 2.35), (st.x, 2.35)])
    dot(ax, 0.9, 1.0)
    wire(ax, [(en.x, 2.35), (4.6, 2.35)])
    ax.text(en.x + 0.15, 2.3, r"$\overline{S}$", fontsize=8.5, va="top")
    ax.text(inv.absanchors["center"].x, 1.95, "7 ns", fontsize=7.5, ha="center", va="top",
            color=COLORS[1])
    o_a1 = a1.absanchors["out"]
    o_a2 = a2.absanchors["out"]
    wire(ax, [(o_a1.x, o_a1.y), (7.8, o_a1.y), (7.8, 2.2), (8.4, 2.2)])
    wire(ax, [(o_a2.x, o_a2.y), (7.8, o_a2.y), (7.8, o1.absanchors["in2"].y),
              (8.4, o1.absanchors["in2"].y)])
    ax.text(o_a1.x + 0.1, o_a1.y + 0.08, r"$A\overline{S}$", fontsize=8, va="bottom")
    ax.text(o_a2.x + 0.1, o_a2.y - 0.08, r"$BS$", fontsize=8, va="top")
    oo = o1.absanchors["out"]
    wire(ax, [(oo.x, oo.y), (oo.x + 0.5, oo.y)])
    ax.text(oo.x + 0.6, oo.y, "Y", va="center", fontsize=9)
    ax.text(-0.5, 4.0, "(a) static-1 hazard: 2:1 mux, A = B = 1", fontsize=9,
            fontweight="bold", va="center")
    ax.set_xlim(-0.6, 11.6)
    ax.set_ylim(0.0, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")

    # ---- mux waveforms ----
    ax = fig.add_subplot(gs[1, 0])
    h, s = 0.5, 0.8
    names = ["S", r"$\overline{S}$", r"$BS$", r"$A\overline{S}$", "Y", "Y with AB"]
    ys = [5.5, 4.4, 3.3, 2.2, 1.1, 0.0]
    wave(ax, ys[0], 0, 40, [(10, 0)], init=1, h=h, s=s)
    wave(ax, ys[1], 0, 40, [(17, 1)], init=0, h=h, s=s)
    wave(ax, ys[2], 0, 40, [(12, 0)], init=1, h=h, s=s, color=BLUE)
    wave(ax, ys[3], 0, 40, [(19, 1)], init=0, h=h, s=s, color=BLUE)
    ax.add_patch(Rectangle((12, ys[4] - 0.1), 7, h + 0.2, fc="#FFCDD2", ec="none", zorder=0))
    wave(ax, ys[4], 0, 40, [(12, 0), (19, 1)], init=1, h=h, s=s, color=RED)
    wave(ax, ys[5], 0, 40, [], init=1, h=h, s=s, color=GREEN, ls="--")
    dim(ax, 10, 17, ys[1] + h + 0.12, "7 ns", fs=7, dy=0.02)
    ax.text(21, ys[4] + 0.2, "glitch, 12–19 ns", fontsize=7.5, color=RED, va="center")
    ax.text(21, ys[5] + 0.2, "with AB: Y stays 1", fontsize=7.5, color=GREEN,
            va="center")
    for t in (10, 12, 17, 19):
        ax.plot([t, t], [-0.2, ys[0] + h + 0.1], color="#AAAAAA", lw=0.6, ls=":", zorder=0)
    rows_axis(ax, names, ys, h, -1.0, fs=8.5)
    ax.set_xlim(0, 40)
    ax.set_ylim(-0.4, ys[0] + h + 0.4)
    ax.set_xticks(range(0, 41, 10))
    ax.set_xlabel("Time (ns)")

    # ---- decode glitch ----
    ax = fig.add_subplot(gs[:, 1])
    s2 = 0.06
    names = ["CLK", r"S$_1$ (route 0.42 ns)", r"S$_0$ (route 0.95 ns)",
             r"laser_en = S$_1$S$_0$ (decoded, LUT 0.11 ns)", "laser_en (registered)"]
    ys = [7.4, 5.8, 4.2, 2.4, 0.6]
    wave(ax, ys[0], -0.3, 3, [(0, 1), (1.5, 0)], init=0, h=h, s=s2)
    wave(ax, ys[1], -0.3, 3, [(0.42, 1)], init=0, h=h, s=s2, color=BLUE)
    wave(ax, ys[2], -0.3, 3, [(0.95, 0)], init=1, h=h, s=s2, color=BLUE)
    t_on, t_off = 0.42 + 0.11, 0.95 + 0.11
    ax.add_patch(Rectangle((t_on, ys[3]), t_off - t_on, h, fc="#FFCDD2", ec="none", zorder=0))
    wave(ax, ys[3], -0.3, 3, [(t_on, 1), (t_off, 0)], init=0, h=h, s=s2, color=RED)
    wave(ax, ys[4], -0.3, 3, [], init=0, h=h, s=s2, color=GREEN)
    dim(ax, t_on, t_off, ys[3] - 0.25, "≈0.53 ns", RED, fs=7.5, above=False, dy=0.05)
    ax.text(1.25, ys[3] + 0.25, "S$_1$S$_0$ = 11:\nlooks like FIRE", fontsize=7.5, color=RED,
            va="center")
    ax.text(1.25, ys[4] + 0.12, "stays low", fontsize=7.5, color=GREEN, va="bottom")
    ax.text(0.5, ys[1] - 0.45, "ARMED (01) → FAULT (10)", fontsize=7, color="#444444",
            va="center")
    for t in (0.42, 0.95):
        ax.plot([t, t], [ys[3] - 0.1, ys[0] + h], color="#AAAAAA", lw=0.6, ls=":", zorder=0)
    for lab, y in zip(names, ys):
        ax.text(-0.3, y + h + 0.15, lab, fontsize=8, ha="left", va="bottom")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.3, 3)
    ax.set_ylim(0.2, ys[0] + h + 1.2)
    ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
    ax.set_xlabel("Time after clock edge (ns)")
    ax.text(-0.3, ys[0] + h + 1.15, "(b) laser-interlock decode glitch", fontsize=9,
            fontweight="bold", va="top")
    save(fig, "15", "fig-15-4-static-hazard-and-decode-glitch")


def fig_15_5():
    """Self-checking test bench architecture."""
    fig, ax = plt.subplots(figsize=(6.8, 4.7))
    ax.set_xlim(0, 14.6)
    ax.set_ylim(0.2, 9.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.15, 0.4), 14.3, 9.0, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#FAFAFA", ec=INK, lw=1.2, ls="--"))
    ax.text(0.4, 9.1, "tb_interlock  (test bench, not synthesised)", fontsize=9.5,
            fontweight="bold", va="center")
    box(ax, 0.5, 7.1, 2.8, 1.1, "clock generator\n100 MHz (10 ns)", fc="#E3F0FA", fontsize=8)
    box(ax, 0.5, 5.6, 2.8, 1.0, "reset generator", fc="#E3F0FA", fontsize=8)
    box(ax, 0.5, 1.2, 2.8, 3.6, "stimulus\n\ndirected\nsequence table\n+ optional\nrandom\ngenerator",
        fc="#E3F0FA", fontsize=8)
    ax.add_patch(Rectangle((5.8, 4.6), 2.8, 2.6, fc="#E8F5E9", ec=INK, lw=1.6))
    ax.text(7.2, 6.2, "DUT", fontsize=10, ha="center", fontweight="bold")
    ax.text(7.2, 5.5, "interlock", fontsize=9, ha="center", family="monospace")
    box(ax, 5.8, 1.0, 2.8, 1.9, "reference model\n(spec of\nFig. 15.2)", fc="#FFF8E1",
        fontsize=8)
    box(ax, 10.5, 1.6, 3.6, 2.8, "comparator /\nscoreboard\n\nerror counter\nprints PASS or FAIL",
        fc="#FDEEE3", fontsize=8)
    box(ax, 10.5, 5.4, 3.6, 1.3, "coverage collector\n4 states, 12 arcs", fc="#F3E5F5",
        fontsize=8)
    box(ax, 10.5, 7.3, 3.6, 1.3, "assertion monitor\nlaser_en ⇒ door_closed", fc="#F3E5F5",
        fontsize=8)
    # clock and reset to DUT
    arr2(ax, [(3.3, 7.65), (5.2, 7.65), (5.2, 6.8), (5.8, 6.8)])
    ax.text(3.45, 7.75, "clk", fontsize=7.5, va="bottom")
    arr2(ax, [(3.3, 6.1), (5.8, 6.1)])
    ax.text(3.45, 6.2, "rst_n", fontsize=7.5, va="bottom")
    # stimulus to DUT and reference model
    xb = 3.65
    arr2(ax, [(3.3, 4.0), (xb, 4.0), (xb, 5.1), (5.8, 5.1)], INK, 2.0)
    arr2(ax, [(xb, 4.0), (xb, 1.95), (5.8, 1.95)], INK, 2.0)
    ax.plot([xb], [4.0], "o", ms=4, color=INK)
    ax.text(3.85, 4.75, "door_closed\nkey_on\nfire_req\nfault", fontsize=7, va="top",
            family="monospace")
    # DUT outputs to scoreboard
    xv = 10.1
    arr2(ax, [(8.6, 5.1), (xv, 5.1), (xv, 3.6), (10.5, 3.6)], INK, 2.0)
    ax.text(8.7, 4.95, "laser_en\nready_lamp\nfault_lamp", fontsize=6.5, va="top",
            family="monospace")
    ax.text(8.7, 5.2, "actual", fontsize=7, va="bottom")
    arr2(ax, [(8.6, 1.95), (xv, 1.95), (xv, 2.4), (10.5, 2.4)], INK, 2.0)
    ax.text(8.7, 2.05, "expected", fontsize=7, va="bottom")
    # taps to coverage and assertions
    arr2(ax, [(8.6, 6.05), (10.5, 6.05)], COLORS[3], 1.2, "--")
    ax.text(9.55, 6.15, "state, inputs", fontsize=7, ha="center", va="bottom", color=COLORS[3])
    arr2(ax, [(8.6, 6.8), (xv, 6.8), (xv, 7.95), (10.5, 7.95)], COLORS[3], 1.2, "--")
    ax.text(8.7, 7.35, "laser_en,\ndoor_closed", fontsize=7, ha="left", va="center",
            color=COLORS[3])
    # result
    arr2(ax, [(12.3, 1.6), (12.3, 0.9)])
    ax.text(12.45, 0.95, "PASS / FAIL", fontsize=8, va="center", fontweight="bold")
    save(fig, "15", "fig-15-5-testbench-architecture")


if __name__ == "__main__":
    fig_15_1()
    fig_15_2()
    fig_15_3()
    fig_15_4()
    fig_15_5()
