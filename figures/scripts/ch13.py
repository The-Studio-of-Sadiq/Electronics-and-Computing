"""Figures for Chapter 13 — Combinational Digital Systems.

Run from the repository root:  python figures/scripts/ch13.py
"""
import math
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


# ----------------------------------------------------------------------------
def fig_13_1():
    """Full adder in G/P form and 4-bit ripple-carry adder with its critical path."""
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=9, lw=1.2)

    # ---------------- top: full adder at gate level ----------------
    yA, yB, yC = 10.0, 9.35, 11.0
    xin = 0.6
    x1 = 2.8            # first gate column
    x2 = 7.4            # second gate column
    xor1 = place(d, logic.Xor, x1, yA)                  # P = A xor B
    and1 = place(d, logic.And, x1, 8.0)                 # G = AB
    p_y = xor1.absanchors["out"].y
    xor2 = place(d, logic.Xor, x2, p_y + 0.65)          # S = P xor Cin  (in1=Cin, in2=P)
    and2 = place(d, logic.And, x2, 8.65)                # P Cin (in1=P, in2=Cin)
    g_y = and1.absanchors["out"].y
    pc_y = and2.absanchors["out"].y
    xo = 10.8
    or1 = place(d, logic.Or, xo, pc_y)                  # Cout = G + P Cin
    d.draw(show=False)

    # inputs
    for lab, y in (("A", yA), ("B", yB), (r"$C_{in}$", yC)):
        ax.text(xin - 0.15, y, lab, ha="right", va="center", fontsize=10)
    wire(ax, [(xin, yA), (x1, yA)])
    wire(ax, [(xin, yB), (x1, yB)])
    # taps to AND1
    wire(ax, [(1.4, yA), (1.4, 8.0), (x1, 8.0)]); dot(ax, 1.4, yA)
    wire(ax, [(1.9, yB), (1.9, 7.35), (x1, 7.35)]); dot(ax, 1.9, yB)
    # P to XOR2 and AND2
    po = xor1.absanchors["out"]
    wire(ax, [(po.x, po.y), (x2, po.y)])
    ax.text(po.x + 0.05, po.y + 0.1, "P", fontsize=10, color=BLUE, va="bottom")
    xp = 5.8
    wire(ax, [(xp, po.y), (xp, 8.65), (x2, 8.65)]); dot(ax, xp, po.y)
    # Cin
    xc = 6.6
    wire(ax, [(xin, yC), (xc, yC), (xc, p_y + 0.65), (x2, p_y + 0.65)])
    wire(ax, [(xc, p_y + 0.65), (xc, 8.0), (x2, 8.0)]); dot(ax, xc, p_y + 0.65)
    # G and P Cin to OR
    go = and1.absanchors["out"]
    wire(ax, [(go.x, go.y), (xo - 0.6, go.y), (xo - 0.6, or1.absanchors["in2"].y),
              (xo, or1.absanchors["in2"].y)])
    ax.text(go.x + 0.05, go.y + 0.1, "G", fontsize=10, color=BLUE, va="bottom")
    a2o = and2.absanchors["out"]
    wire(ax, [(a2o.x, a2o.y), (xo, a2o.y)])
    # outputs
    so = xor2.absanchors["out"]
    wire(ax, [(so.x, so.y), (13.6, so.y)])
    ax.text(13.75, so.y, r"$S=P\oplus C_{in}$", va="center", fontsize=9.5)
    oo = or1.absanchors["out"]
    wire(ax, [(oo.x, oo.y), (13.6, oo.y)])
    ax.text(13.75, oo.y, r"$C_{out}=G+P\,C_{in}$", va="center", fontsize=9.5)
    # one gate delay per gate
    for g in (xor1, and1, xor2, and2, or1):
        c = g.absanchors["out"]
        ax.text(c.x - 1.15, c.y + 0.5, r"$t_g$", ha="center", va="bottom", fontsize=8.5,
                color=COLORS[1])
    ax.text(0.0, 12.0, "(a) Full adder, generate–propagate form (each gate = one delay $t_g$)",
            fontsize=9.5, fontweight="bold", va="center")

    # ---------------- bottom: 4-bit ripple-carry adder ----------------
    ax.text(0.0, 6.2, "(b) 4-bit ripple-carry adder: worst-case path A$_0$ → carry chain → S$_3$",
            fontsize=9.5, fontweight="bold", va="center")
    bw, bh, by = 2.0, 1.7, 2.3
    xs = [1.4, 4.9, 8.4, 11.9]
    yc = by + 0.55
    for i, x in enumerate(xs):
        ax.add_patch(FancyBboxPatch((x, by), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#EEF3F8", ec=INK, lw=1.1))
        ax.text(x + 1.3, by + bh - 0.42, f"FA{i}", ha="center", va="center", fontsize=10)
        xa, xb = x + 0.55, x + 1.45
        ca = RED if i == 0 else INK
        wire(ax, [(xa, 5.2), (xa, by + bh)], color=ca, lw=2.0 if i == 0 else 1.2)
        wire(ax, [(xb, 5.2), (xb, by + bh)])
        ax.text(xa, 5.3, f"A$_{i}$", ha="center", va="bottom", fontsize=9.5, color=ca)
        ax.text(xb, 5.3, f"B$_{i}$", ha="center", va="bottom", fontsize=9.5)
        cs = RED if i == 3 else INK
        wire(ax, [(x + bw / 2, by), (x + bw / 2, 1.0)], color=cs, lw=2.0 if i == 3 else 1.2)
        ax.text(x + bw / 2, 0.88, f"S$_{i}$", ha="center", va="top", fontsize=9.5, color=cs)
    # carries
    wire(ax, [(0.4, yc), (xs[0], yc)])
    ax.text(0.3, yc, "C$_0$", ha="right", va="center", fontsize=9.5)
    for i in range(3):
        x0, x1_ = xs[i] + bw, xs[i + 1]
        ax.annotate("", xy=(x1_, yc), xytext=(x0, yc),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.0, mutation_scale=10,
                                    shrinkA=0, shrinkB=0))
        ax.text((x0 + x1_) / 2, yc + 0.12, f"C$_{i + 1}$", ha="center", va="bottom", fontsize=9.5,
                color=RED)
        ax.text((x0 + x1_) / 2, yc - 0.15, f"{3 + 2 * i} $t_g$", ha="center", va="top",
                fontsize=9, color=RED, fontweight="bold")
    ax.annotate("", xy=(xs[3] + bw + 1.0, yc), xytext=(xs[3] + bw, yc),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2, mutation_scale=10,
                                shrinkA=0, shrinkB=0))
    ax.text(xs[3] + bw + 1.1, yc + 0.1, "C$_4$", va="bottom", fontsize=9.5)
    ax.text(xs[3] + bw + 1.1, yc - 0.1, "9 $t_g$", va="top", fontsize=8.5, color="#666666")
    # internal red path segments
    x = xs[0]
    wire(ax, [(x + 0.55, by + bh), (x + 0.55, yc), (x + bw, yc)], color=RED, lw=1.6, ls="--")
    ax.text(x + 0.45, by + bh + 0.45, "1 $t_g$ (P,G)", ha="right", va="center", fontsize=8.5,
            color=RED)
    for x in xs[1:3]:
        wire(ax, [(x, yc), (x + bw, yc)], color=RED, lw=1.6, ls="--")
    x = xs[3]
    wire(ax, [(x, yc), (x + bw / 2, yc), (x + bw / 2, by)], color=RED, lw=1.6, ls="--")
    ax.text(xs[3] + bw / 2 + 0.12, 1.45, "8 $t_g$", ha="left", va="center", fontsize=9,
            color=RED, fontweight="bold")
    ax.text(7.4, -0.15, r"$t_{ripple}\approx 2n\,t_g$  (n = 4: S$_3$ valid after 8 $t_g$)",
            ha="center", va="center", fontsize=9)

    ax.set_xlim(-0.6, 17.6)
    ax.set_ylim(-0.5, 12.4)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, "13", "fig-13-1-full-adder-ripple-carry")


def fig_13_2():
    """Delay and cell count of ripple, Brent-Kung and Kogge-Stone adders."""
    ns = np.array([4, 8, 16, 32, 64])
    L = np.log2(ns)
    delay = {"Ripple carry": 2 * ns, "Brent–Kung": 2 * (2 * L - 1) + 2, "Kogge–Stone": 2 * L + 2}
    cells = {"Ripple carry": ns, "Brent–Kung": 2 * ns - 2 - L, "Kogge–Stone": ns * L - ns + 1}
    marks = {"Ripple carry": "o", "Brent–Kung": "s", "Kogge–Stone": "^"}
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.6))
    for ax, data, ylab, title in ((axs[0], delay, r"Worst-case delay ($t_g$)", "Delay"),
                                  (axs[1], cells, "Prefix / carry cells", "Carry-cell count")):
        for (name, v), c in zip(data.items(), COLORS):
            ax.plot(ns, v, marker=marks[name], color=c, label=name, ms=5)
            ax.annotate(f"{v[-1]:.0f}", (ns[-1], v[-1]), xytext=(5, 0), textcoords="offset points",
                        va="center", fontsize=8.5, color=c)
        ax.set_xscale("log", base=2)
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns])
        ax.set_xlabel("Word length n (bits)")
        ax.set_ylabel(ylab)
        ax.set_title(title)
        ax.grid(True, which="major", alpha=0.6)
        ax.set_xlim(3.4, 90)
        ax.set_ylim(0, None)
    axs[0].legend(loc="upper left", fontsize=8.5)
    axs[1].legend(loc="upper left", fontsize=8.5)
    fig.tight_layout()
    save(fig, "13", "fig-13-2-adder-delay-vs-width")


def fig_13_3():
    """Read cycle with 74HC138 vs 74LVC138 address decoder."""
    fig, ax = plt.subplots(figsize=(6.8, 3.9))
    t0, t1 = 0, 110
    h = 0.6
    rows = ["CLK", "ADDR[15:13]", "CS_n (74HC138)", "DATA (74HC138)", "CS_n (74LVC138)",
            "DATA (74LVC138)"]
    ys = {r: (len(rows) - 1 - i) * 1.25 for i, r in enumerate(rows)}
    for t in range(0, 111, 10):
        ax.axvline(t, color=GRID, lw=0.7, zorder=0)
    s = 1.5
    wave(ax, ys["CLK"], -4, t1, [(0, 1), (50, 0), (100, 1)], init=0, h=h, s=s)
    bus(ax, ys["ADDR[15:13]"], [(-4, 8, "", "hatch", None), (8, 110, "address valid", "valid", None)],
        h=h, s=s, t0=-4, t1=t1)
    wave(ax, ys["CS_n (74HC138)"], -4, t1, [(46, 0)], init=1, h=h, s=s, color=RED)
    bus(ax, ys["DATA (74HC138)"], [(-4, 46, "", "z", RED), (101, 110, "", "valid", RED)],
        h=h, s=s, t0=-4, t1=t1)
    bus(ax, ys["DATA (74HC138)"], [(46, 101, "access in progress", "hatch", RED)], h=h, s=s)
    wave(ax, ys["CS_n (74LVC138)"], -4, t1, [(15, 0)], init=1, h=h, s=s, color=GREEN)
    bus(ax, ys["DATA (74LVC138)"], [(-4, 15, "", "z", GREEN), (15, 70, "access in progress", "hatch",
                                    GREEN), (70, 110, "valid", "valid", GREEN)],
        h=h, s=s, t0=-4, t1=t1)
    # sample line
    ax.axvline(90, color=INK, ls="--", lw=1.1)
    ax.text(90, ys["CLK"] + h + 0.25, "processor\nsamples data", ha="center", va="bottom",
            fontsize=8.5)
    # dimension arrows
    y = ys["CS_n (74HC138)"] + h + 0.12
    dim(ax, 8, 46, y, "38 ns decoder delay (max, 85 °C)", RED, fs=8)
    y = ys["DATA (74HC138)"] + h + 0.12
    dim(ax, 46, 101, y, r"$t_{ACS}$ = 55 ns", RED, fs=8)
    y = ys["DATA (74HC138)"] - 0.18
    dim(ax, 90, 101, y, "−11 ns", RED, fs=8, above=False)
    y = ys["CS_n (74LVC138)"] + h + 0.12
    dim(ax, 8, 15, y, "7 ns", GREEN, fs=8)
    y = ys["DATA (74LVC138)"] + h + 0.12
    dim(ax, 15, 70, y, r"$t_{ACS}$ = 55 ns", GREEN, fs=8)
    y = ys["DATA (74LVC138)"] - 0.18
    dim(ax, 70, 90, y, "slack +20 ns", GREEN, fs=8, above=False)
    for r, y in ys.items():
        ax.text(-6, y + h / 2, r, ha="right", va="center", fontsize=9)
    ax.set_xlim(-4, t1)
    ax.set_ylim(-0.75, ys["CLK"] + h + 1.2)
    ax.set_xticks(range(0, 111, 10))
    ax.set_xlabel("Time from start of bus cycle (ns)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    save(fig, "13", "fig-13-3-address-decoder-timing")


def fig_13_4():
    """8-bit ALU block diagram."""
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    ax.set_xlim(-0.1, 14.3)
    ax.set_ylim(-0.1, 10.8)
    ax.set_aspect("equal")
    ax.axis("off")

    def arr(x0, y0, x1, y1, col=INK, lw=1.1, ls="-"):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, ls=ls, shrinkA=0,
                                    shrinkB=0, mutation_scale=9))

    def line(pts, col=INK, lw=1.1, ls="-"):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=lw, ls=ls, solid_joinstyle="miter")

    def tap(x, y, col=INK):
        ax.plot([x], [y], "o", ms=3.5, color=col)

    def block(x, y, w, h, fc="#EEF3F8"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=fc, ec=INK, lw=1.1))

    yA, yB = 10.0, 9.5
    ax.plot([1.0, 12.2], [yA, yA], color=INK, lw=2.6)
    ax.plot([1.0, 12.2], [yB, yB], color=INK, lw=2.6)
    ax.text(0.9, yA, "A[7:0]", ha="right", va="center", fontsize=9)
    ax.text(0.9, yB, "B[7:0]", ha="right", va="center", fontsize=9)
    ax.text(1.0, 10.35, "red: critical path B$_0$ → XOR → carry chain → mux → Z NOR tree",
            fontsize=8.5, color=RED, ha="left", va="bottom")

    # ---- adder-subtractor ----
    top = 8.8
    block(1.0, 5.0, 4.4, top - 5.0)
    box(ax, 4.2, 7.3, 1.0, 0.6, r"$\oplus$", fc="white", fontsize=11)
    box(ax, 1.25, 5.85, 3.95, 0.95, "8-bit adder\ncarry chain C$_0$→C$_8$", fc="white", fontsize=8.5)
    ax.text(1.2, 5.35, "Adder–subtractor", ha="left", va="center", fontsize=9, fontweight="bold")
    tap(1.5, yA)
    arr(1.5, yA, 1.5, 6.8)
    ax.text(1.6, 8.0, "A", fontsize=8.5)
    tap(4.7, yB, RED)
    arr(4.7, yB, 4.7, 7.9, RED, 1.7)
    ax.text(4.8, 8.3, "B", fontsize=8.5, color=RED)
    arr(4.7, 7.3, 4.7, 6.8, RED, 1.7)
    ax.text(2.4, 7.6, "SUB", fontsize=8.5, color=COLORS[1], ha="right", va="center")
    arr(2.45, 7.6, 4.2, 7.6, COLORS[1])
    tap(3.2, 7.6, COLORS[1])
    arr(3.2, 7.6, 3.2, 6.8, COLORS[1])
    ax.text(3.12, 7.05, "C$_0$", fontsize=7.5, color=COLORS[1], va="center", ha="right")
    # carry outs (left side of adder)
    line([(1.25, 6.6), (0.55, 6.6), (0.55, 2.2), (1.2, 2.2)])
    line([(1.25, 6.05), (0.8, 6.05), (0.8, 2.0), (1.2, 2.0)])
    ax.text(0.5, 6.65, "C$_8$", fontsize=8, ha="right", va="bottom")
    ax.text(1.03, 6.1, "C$_7$", fontsize=7, ha="center", va="bottom")

    # ---- logic unit ----
    block(6.0, 5.6, 2.7, top - 5.6)
    ax.text(7.35, 8.35, "Logic unit", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(7.35, 6.85, "A AND B\nA OR B\nA XOR B\nNOT A", ha="center", va="center",
            fontsize=8.5, linespacing=1.25)
    tap(6.6, yA)
    arr(6.6, yA, 6.6, top)
    tap(8.1, yB)
    arr(8.1, yB, 8.1, top)

    # ---- shifter ----
    block(9.4, 5.6, 2.8, top - 5.6)
    ax.text(10.8, 8.35, "Shifter (by 1)", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(10.8, 6.85, "shift left\nshift right logical\nshift right arith.", ha="center",
            va="center", fontsize=8.5, linespacing=1.25)
    tap(10.8, yA)
    arr(10.8, yA, 10.8, top)

    # ---- result multiplexer ----
    mx0, mx1, my0, my1 = 1.2, 12.2, 3.5, 4.5
    ax.add_patch(Polygon([(mx0, my1), (mx1, my1), (mx1 - 0.5, my0), (mx0 + 0.5, my0)],
                         closed=True, fc="#FFF4E0", ec=INK, lw=1.1))
    ax.text(6.7, 3.78, "8-input result multiplexer", ha="center", va="center", fontsize=9)
    ins = [("SUM", 4.7, 5.85, RED), ("AND", 6.4, 5.6, INK), ("OR", 7.05, 5.6, INK),
           ("XOR", 7.7, 5.6, INK), ("NOT", 8.35, 5.6, INK), ("SHL", 10.0, 5.6, INK),
           ("SHR", 10.8, 5.6, INK), ("SAR", 11.6, 5.6, INK)]
    for lab, x, y0, col in ins:
        arr(x, y0, x, my1, col, 1.7 if col == RED else 1.0)
        ax.text(x, my1 - 0.08, lab, fontsize=6.5, ha="center", va="top", color=col)
    ax.text(13.0, 4.0, "OP[2:0]", fontsize=8.5, ha="left", va="center", color=COLORS[1])
    arr(12.95, 4.0, mx1 - 0.25, 4.0, COLORS[1])

    # ---- result bus ----
    xr = 6.7
    line([(xr, my0), (xr, 2.75)], RED, 1.7)
    tap(xr, 3.1)
    ax.plot([xr, 12.6], [3.1, 3.1], color=INK, lw=2.6)
    arr(12.6, 3.1, 13.0, 3.1)
    ax.text(13.05, 3.1, "RESULT\n[7:0]", fontsize=8.5, va="center")

    # ---- flag logic ----
    block(1.2, 0.7, 11.0, 2.05, fc="#F2F2F2")
    ax.text(1.4, 2.5, "Flag logic", ha="left", va="center", fontsize=9, fontweight="bold")
    fl = [("Z", "NOR of R[7:0]\n3-level tree", 3.6, 2.4, RED),
          ("N", "N = R[7]", 5.9, 1.6, INK),
          ("C", "C = C$_8$\n(adder ops)", 8.0, 1.9, INK),
          ("V", r"V = C$_8\oplus$C$_7$", 10.5, 2.1, INK)]
    for name, txt, x, w, col in fl:
        box(ax, x - w / 2, 0.95, w, 0.85, txt, fc="white", fontsize=7.5)
        arr(x, 0.95, x, 0.25, col, 1.7 if col == RED else 1.0)
        ax.text(x + 0.12, 0.2, name, fontsize=9.5, va="center", ha="left", color=col,
                fontweight="bold")
    # result to Z and N
    line([(xr, 2.75), (xr, 2.45), (3.6, 2.45)], RED, 1.7)
    arr(3.6, 2.45, 3.6, 1.8, RED, 1.7)
    tap(5.9, 2.45, RED)
    arr(5.9, 2.45, 5.9, 1.8)
    ax.text(6.0, 2.5, "R[7]", fontsize=7, va="bottom")
    # C8 to C and V, C7 to V
    line([(1.2, 2.2), (10.2, 2.2)])
    tap(8.0, 2.2)
    arr(8.0, 2.2, 8.0, 1.8)
    arr(10.2, 2.2, 10.2, 1.8)
    line([(1.2, 2.0), (10.8, 2.0)])
    arr(10.8, 2.0, 10.8, 1.8)
    ax.text(12.4, 0.5, "flags", fontsize=8.5, va="center", ha="left")
    save(fig, "13", "fig-13-4-alu-block-diagram")


def fig_13_5():
    """Propagation-delay definitions."""
    vcc = 3.3
    fig = plt.figure(figsize=(6.6, 5.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 0.9], hspace=0.55)
    axA = fig.add_subplot(gs[0])
    axY = fig.add_subplot(gs[1], sharex=axA)
    axB = fig.add_subplot(gs[2])

    t = np.linspace(0, 16, 3201)

    def ramp(t, t50, tt, rising):
        """Linear 0-100 % edge whose 10-90 % time is tt, 50 % crossing at t50."""
        full = tt / 0.8
        x = np.clip((t - (t50 - full / 2)) / full, 0, 1)
        return x if rising else 1 - x

    # input A: rise at 2 ns, fall at 9 ns, 10-90 % = 0.6 ns
    a = vcc * np.where(t < 5.5, ramp(t, 2.0, 0.6, True), ramp(t, 9.0, 0.6, False))
    tphl, tplh, tf, tr = 1.1, 1.5, 1.2, 1.6
    y = vcc * np.where(t < 5.5, ramp(t, 2.0 + tphl, tf, False), ramp(t, 9.0 + tplh, tr, True))
    for ax, v, name in ((axA, a, "A (input)"), (axY, y, "Y (inverter output)")):
        for frac, lab in ((0.1, "10 %"), (0.5, "50 %"), (0.9, "90 %")):
            ax.axhline(frac * vcc, color=GRID, lw=0.9, ls="--", zorder=0)
            ax.text(16.1, frac * vcc, lab, fontsize=7.5, va="center", color="#666666")
        ax.plot(t, v, color=BLUE if ax is axA else COLORS[1], lw=1.8)
        ax.set_yticks([0, 3.3])
        ax.set_ylabel("V", rotation=0, labelpad=8)
        ax.text(0.2, 2.6, name, fontsize=9)
    plt.setp(axA.get_xticklabels(), visible=False)
    axY.set_xlabel("Time (ns)")
    axA.set_xlim(0, 16)
    # vertical 50 % markers
    for tc in (2.0, 9.0):
        for ax in (axA, axY):
            ax.axvline(tc, color="#888888", lw=0.8, ls=":")
    for tc in (2.0 + tphl, 9.0 + tplh):
        for ax in (axA, axY):
            ax.axvline(tc, color="#888888", lw=0.8, ls=":")
    dim(axY, 2.0, 2.0 + tphl, 3.6, r"$t_{PHL}$", fs=9, dy=0.05)
    dim(axY, 9.0, 9.0 + tplh, 3.6, r"$t_{PLH}$", fs=9, dy=0.05)
    # tf, tr between 10 and 90 % points, drawn below the trace
    f90, f10 = 2.0 + tphl - tf / 2, 2.0 + tphl + tf / 2
    r10, r90 = 9.0 + tplh - tr / 2, 9.0 + tplh + tr / 2
    for tc, v in ((f90, 0.9), (f10, 0.1), (r10, 0.1), (r90, 0.9)):
        axY.plot([tc, tc], [-0.75, v * vcc], color="#888888", lw=0.8, ls=":")
    dim(axY, f90, f10, -0.6, "", fs=9)
    axY.text(f10 + 0.15, -0.6, r"$t_f$", fontsize=9, va="center")
    dim(axY, r10, r90, -0.6, "", fs=9)
    axY.text(r90 + 0.15, -0.6, r"$t_r$", fontsize=9, va="center")
    axY.set_ylim(-0.9, 4.3)
    axA.set_ylim(-0.3, 3.9)
    axA.text(5.6, 1.2, r"$V_{CC}$ = 3.3 V", fontsize=8.5)

    # ---- lower panel: multi-input block, tcd and tpd ----
    ax = axB
    tcd, tpd = 1.2, 4.5
    h = 0.6
    s = 0.25
    bus(ax, 1.75, [(-2, 0, "old", "valid", None), (0, 8, "new input", "valid", None)], h=h, s=s,
        t0=-2, t1=8)
    bus(ax, 0.0, [(-2, tcd, "old output", "valid", None), (tcd, tpd, "", "hatch", RED),
                  (tpd, 8, "new output valid", "valid", None)], h=h, s=s, t0=-2, t1=8)
    # glitch sketch
    gx = [tcd + 0.6, tcd + 0.8, tcd + 1.4, tcd + 1.6]
    ax.plot([gx[0], gx[1], gx[2], gx[3]], [h + 0.05, h + 0.4, h + 0.4, h + 0.05], color=RED, lw=1.2)
    ax.text(tcd + 1.1, h + 0.5, "possible glitch", fontsize=7.5, color=RED, ha="center",
            va="bottom")
    ax.axvline(0, color="#888888", lw=0.8, ls=":")
    dim(ax, 0, tcd, -0.35, r"$t_{cd}$ = 1.2 ns", fs=8.5, above=False)
    dim(ax, 0, tpd, -1.05, r"$t_{pd}$ = 4.5 ns", fs=8.5, above=False)
    ax.text(-2.2, 1.75 + h / 2, "IN", ha="right", va="center", fontsize=9)
    ax.text(-2.2, h / 2, "OUT", ha="right", va="center", fontsize=9)
    ax.set_xlim(-2, 8)
    ax.set_ylim(-1.75, 2.5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Time after input change (ns)")
    save(fig, "13", "fig-13-5-propagation-delay-definitions")


if __name__ == "__main__":
    fig_13_1()
    fig_13_2()
    fig_13_3()
    fig_13_4()
    fig_13_5()
