"""Figures for Chapter 12 — Boolean Algebra and Logic Gates.

Run from the repository root:  python figures/scripts/ch12.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Circle  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402
import schemdraw.logic as logic  # noqa: E402
from schemdraw.segments import SegmentText  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
RED = "#C62828"
MONO = "DejaVu Sans Mono"


def line(ax, pts, color=INK, lw=1.1, **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="miter", **kw)


def dot(ax, x, y, color=INK):
    ax.plot([x], [y], "o", ms=3.2, color=color, zorder=5)


def place(d, cls, x, y, anchor="in1", scale=0.8, **kw):
    return d.add(cls(**kw).theta(0).at((x, y)).anchor(anchor).scale(scale))


def A(g, name):
    p = g.absanchors[name]
    return p.x, p.y


# ----------------------------------------------------------------------------
def _iec(ax, x, y, q, ninputs=2, bubble=False, w=0.8, h=0.9):
    """IEC 60617-12 rectangular symbol with qualifier q; (x, y) = left-centre."""
    ax.add_patch(Rectangle((x, y - h / 2), w, h, fc="white", ec=INK, lw=1.1))
    ax.text(x + w / 2, y + h / 2 - 0.08, q, ha="center", va="top", fontsize=8.5)
    ys = [y + 0.22, y - 0.22] if ninputs == 2 else [y]
    for yy in ys:
        line(ax, [(x - 0.3, yy), (x, yy)])
    r = 0.07
    if bubble:
        ax.add_patch(Circle((x + w + r, y), r, fc="white", ec=INK, lw=1.0))
        line(ax, [(x + w + 2 * r, y), (x + w + 0.35, y)])
    else:
        line(ax, [(x + w, y), (x + w + 0.35, y)])


def fig_12_1():
    """Gate symbols (IEEE distinctive shape and IEC rectangular) with truth tables."""
    fig = plt.figure(figsize=(6.8, 5.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.1, 13.4)
    ax.set_ylim(-2.75, 9.6)
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(lw=1.1, fontsize=8)
    rows = [("BUFFER", logic.Buf, "1", False, "$A$", lambda a, b: a, 1),
            ("NOT", logic.Not, "1", True, r"$\overline{A}$", lambda a, b: 1 - a, 1),
            ("AND", logic.And, "&", False, "$AB$", lambda a, b: a & b, 2),
            ("NAND", logic.Nand, "&", True, r"$\overline{AB}$", lambda a, b: 1 - (a & b), 2),
            ("OR", logic.Or, "≥1", False, "$A+B$", lambda a, b: a | b, 2),
            ("NOR", logic.Nor, "≥1", True, r"$\overline{A+B}$", lambda a, b: 1 - (a | b), 2),
            ("XOR", logic.Xor, "=1", False, r"$A\oplus B$", lambda a, b: a ^ b, 2),
            ("XNOR", logic.Xnor, "=1", True, r"$\overline{A\oplus B}$", lambda a, b: 1 - (a ^ b), 2)]
    xs_tt = [10.3, 11.0, 11.7, 12.4]
    ytop = 9.0
    hdr = [(0.1, "gate", "left"), (2.9, "IEEE Std 91", "center"), (5.6, "IEC 60617-12", "center"),
           (8.3, "expression", "center")]
    for x, t, ha in hdr:
        ax.text(x, ytop, t, ha=ha, va="center", fontsize=8.5, weight="bold")
    ax.text(11.35, ytop + 0.25, "output for AB =", ha="center", va="bottom", fontsize=7.5)
    for x, ab in zip(xs_tt, ("00", "01", "10", "11")):
        ax.text(x, ytop - 0.05, ab, ha="center", va="center", fontsize=8.5, weight="bold", family=MONO)
    line(ax, [(0, ytop - 0.45), (13.1, ytop - 0.45)], lw=0.8)
    for k, (name, cls, q, inv, expr, fn, nin) in enumerate(rows):
        y = ytop - 1.0 - k * 0.98
        if k % 2 == 1:
            ax.add_patch(Rectangle((0, y - 0.49), 13.1, 0.98, fc="#F4F6F8", ec="none", zorder=0))
        ax.text(0.1, y, name, ha="left", va="center", fontsize=8.5)
        if nin == 2:
            g = place(d, cls, 2.2, y + 0.2, scale=0.8)
            line(ax, [(1.9, y + 0.2), (2.2, y + 0.2)])
            line(ax, [(1.9, y - 0.2), (2.2, y - 0.2)])
        else:
            g = place(d, cls, 3.3, y, anchor="out", scale=0.9)
            line(ax, [(1.9, y), A(g, "in1")])
        o = A(g, "out")
        line(ax, [o, (3.9, y)])
        _iec(ax, 5.2, y, q, ninputs=nin, bubble=inv)
        ax.text(8.3, y, expr, ha="center", va="center", fontsize=10)
        for x, (a, b) in zip(xs_tt, ((0, 0), (0, 1), (1, 0), (1, 1))):
            v = fn(a, b)
            ax.text(x, y, str(v), ha="center", va="center", fontsize=9.5, family=MONO,
                    color=BLUE if v else "#777777", weight="bold" if v else None)
    yb = ytop - 1.0 - 8 * 0.98 + 0.45
    line(ax, [(0, yb), (13.1, yb)], lw=0.8)
    # extra row: tri-state buffer and open-drain wired-AND
    ye = yb - 1.75
    ax.text(0.1, ye + 0.2, "tri-state\nbuffer", ha="left", va="center", fontsize=8.5)
    tb = place(d, logic.Tristate, 2.2, ye + 0.2, scale=0.95, outputnot=False)
    line(ax, [(1.8, ye + 0.2), (2.2, ye + 0.2)])
    o = A(tb, "out")
    line(ax, [o, (4.1, o[1])])
    c = A(tb, "c")
    line(ax, [c, (c[0], c[1] + 0.35)])
    ax.text(c[0], c[1] + 0.4, "EN", ha="center", va="bottom", fontsize=7.5)
    ax.text(4.2, o[1], "Y", ha="left", va="center", fontsize=8)
    ax.text(2.6, ye - 0.65, "Y = A if EN = 1;  Z (high impedance) if EN = 0", ha="left", va="center",
            fontsize=7.5)
    # open drain
    ax.text(5.5, ye + 0.2, "open-drain\nwired-AND", ha="left", va="center", fontsize=8.5)
    xl = 9.6
    yline = ye + 0.6
    for i, xm in enumerate((8.6, 10.6)):
        m = d.add(elm.NMos().theta(0).at((xm, ye)).anchor("center").scale(0.55))
        line(ax, [A(m, "drain"), (xm, yline)])
        line(ax, [A(m, "source"), (xm, ye - 0.75)])
        gx, gy = A(m, "gate")
        line(ax, [(gx - 0.3, gy), (gx, gy)])
        ax.text(gx - 0.33, gy, f"$\\overline{{Y_{i + 1}}}$", ha="right", va="center", fontsize=7.5)
        dot(ax, xm, yline)
    line(ax, [(8.6, yline), (12.0, yline)])
    line(ax, [(8.6, ye - 0.75), (10.6, ye - 0.75)])
    d.add(elm.Ground().at((9.6, ye - 0.75)).scale(0.5))
    d.add(elm.Resistor().at((11.6, yline)).up(0.9).scale(0.4))
    dot(ax, 11.6, yline)
    line(ax, [(11.35, yline + 0.9), (11.85, yline + 0.9)])
    ax.text(11.95, yline + 0.9, "$V_{DD}$", ha="left", va="center", fontsize=7.5)
    ax.text(11.85, yline + 0.45, "pull-up", ha="left", va="center", fontsize=7)
    ax.text(12.05, yline, r"$Y_1Y_2$", ha="left", va="center", fontsize=8)
    d.draw(show=False)
    _ = xl
    save(fig, "12", "fig-12-1-gate-symbols")


# ----------------------------------------------------------------------------
def fig_12_2():
    """Logic levels and noise margins of LVC, HC and HCT, and the failing 3.3 V to 5 V HC link."""
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.set_xlim(-1.3, 11.6)
    ax.set_ylim(-0.25, 5.75)
    for sp in ("top", "right", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.set_xticks([])
    ax.set_ylabel("voltage (V)")
    ax.set_yticks(np.arange(0, 5.1, 0.5))
    bw = 1.1
    hi_c, lo_c, und_c = "#BFE3CF", "#F3C4C4", "#D9D9D9"
    bars = [  # x, title, vcc, kind, hi threshold, lo threshold
        (0.0, "74LVC output\n(3.3 V supply)", 3.3, "out", 3.1, 0.2),
        (3.2, "74HC input\n(5 V)", 5.0, "in", 3.5, 1.5),
        (6.6, "74HCT input\n(5 V)", 5.0, "in", 2.0, 0.8),
        (9.6, "74HC output\n(5 V)", 5.0, "out", 4.4, 0.1),
    ]
    for x, title, vcc, kind, vh, vl in bars:
        ax.add_patch(Rectangle((x, vh), bw, vcc - vh, fc=hi_c, ec=INK, lw=0.8))
        ax.add_patch(Rectangle((x, 0), bw, vl, fc=lo_c, ec=INK, lw=0.8))
        ax.add_patch(Rectangle((x, vl), bw, vh - vl, fc=und_c if kind == "in" else "white",
                               ec=INK, lw=0.8))
        ax.text(x + bw / 2, 5.25, title, ha="center", va="bottom", fontsize=8.5)
        nh, nl = ("V_{OH}", "V_{OL}") if kind == "out" else ("V_{IH}", "V_{IL}")
        if x == 0.0:
            lx, lha = x - 0.06, "right"
        else:
            lx, lha = x + bw + 0.06, "left"
        ax.text(lx, vh, f"${nh}$ {vh:g} V", ha=lha, va="center", fontsize=7.5)
        ax.text(lx, vl + (0.06 if vl < 0.3 else 0), f"${nl}$ {vl:g} V", ha=lha,
                va="bottom" if vl < 0.3 else "center", fontsize=7.5)
        if kind == "in":
            ax.text(x + bw / 2, (vh + vl) / 2, "undefined", ha="center", va="center", fontsize=7,
                    rotation=90, bbox=dict(fc=und_c, ec="none", pad=1))
            ax.text(x + bw / 2, (vh + vcc) / 2, "reads 1", ha="center", va="center", fontsize=7)
            ax.text(x + bw / 2, vl / 2, "reads 0", ha="center", va="center", fontsize=7)
        else:
            ax.text(x + bw / 2, (vh + vcc) / 2 if vcc - vh > 0.3 else vcc + 0.1, "drives 1" if vcc - vh > 0.3 else "",
                    ha="center", va="center", fontsize=7)
    # LVC output levels extended to the inputs
    for v in (3.1, 0.2):
        ax.plot([1.1, 7.7], [v, v], color=BLUE, lw=0.9, ls="--", zorder=0)
    # failing NMH into HC
    ax.annotate("", xy=(2.95, 3.5), xytext=(2.95, 3.1),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.3, mutation_scale=9,
                                shrinkA=0, shrinkB=0))
    ax.text(2.85, 3.75, "$NM_H$ = 3.1 − 3.5\n= −0.4 V: fails", ha="right", va="bottom",
            fontsize=7.5, color=RED)
    # HCT margins
    ax.annotate("", xy=(6.35, 3.1), xytext=(6.35, 2.0),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=1.3, mutation_scale=9,
                                shrinkA=0, shrinkB=0))
    ax.text(6.25, 2.55, "$NM_H$ = 3.1 − 2.0\n= 1.1 V", ha="right", va="center", fontsize=7.5,
            color=GREEN)
    ax.annotate("", xy=(6.35, 0.8), xytext=(6.35, 0.2),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=1.3, mutation_scale=9,
                                shrinkA=0, shrinkB=0))
    ax.text(6.25, 0.75, "$NM_L$ = 0.8 − 0.2\n= 0.6 V", ha="right", va="bottom", fontsize=7.5,
            color=GREEN)
    ax.axhline(0, color=INK, lw=0.8)
    save(fig, "12", "fig-12-2-logic-levels-noise-margins")


# ----------------------------------------------------------------------------
def fig_12_3():
    """AND-OR to NAND-NAND by bubble pushing, and the warning output W in NAND form."""
    fig = plt.figure(figsize=(6.8, 4.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.4, 15.4)
    ax.set_ylim(-5.4, 5.2)
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(lw=1.1, fontsize=8)
    s = 0.75
    titles = ["1. AND–OR", "2. insert a bubble pair\n    on each wire", "3. NAND–NAND"]
    for k in range(3):
        x0 = k * 5.2
        ya, yb = 3.4, 1.4
        g1cls = logic.And if k == 0 else logic.Nand
        g1 = place(d, g1cls, x0 + 0.5, ya, scale=s)
        g2 = place(d, g1cls, x0 + 0.5, yb, scale=s)
        if k == 0:
            g3 = place(d, logic.Or, x0 + 2.75, 2.6, scale=s)
        elif k == 1:
            g3 = place(d, logic.Or, x0 + 2.75, 2.6, scale=s, inputnots=[1, 2])
        else:
            g3 = place(d, logic.Nand, x0 + 2.75, 2.6, scale=s)
        for g, (l1, l2) in ((g1, ("A", "B")), (g2, ("C", "D"))):
            for an, lab in (("in1", l1), ("in2", l2)):
                p = A(g, an)
                line(ax, [(x0, p[1]), p])
                ax.text(x0 - 0.08, p[1], f"${lab}$", ha="right", va="center", fontsize=8.5)
        o1, o2 = A(g1, "out"), A(g2, "out")
        i1, i2 = A(g3, "in1"), A(g3, "in2")
        xm = (o1[0] + i1[0]) / 2
        line(ax, [o1, (xm, o1[1]), (xm, i1[1]), i1])
        line(ax, [o2, (xm, o2[1]), (xm, i2[1]), i2])
        o3 = A(g3, "out")
        line(ax, [o3, (o3[0] + 0.3, o3[1])])
        ax.text(o3[0] + 0.35, o3[1], "$F$", ha="left", va="center", fontsize=9)
        ax.text(x0 + 2.0, 4.65, titles[k], ha="center", va="center", fontsize=8.5, weight="bold")
        if k == 1:
            for oo, ii in ((o1, i1), (o2, i2)):
                for p in (oo, ii):
                    ax.add_patch(Circle((p[0] - (0.1 if p is oo else -0.33), p[1]), 0.17, fill=False,
                                        ec=ORANGE, lw=1.2))
            ax.text(x0 + 2.2, 0.45, "bubble pairs cancel:\nfunction unchanged", ha="center",
                    va="top", fontsize=7.5, color=ORANGE)
        if k < 2:
            ax.annotate("", xy=(x0 + 5.0, 4.1), xytext=(x0 + 4.4, 4.1),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4, mutation_scale=12))
    ax.text(2.2, 0.45, r"$F=AB+CD$", ha="center", va="top", fontsize=9)
    ax.text(12.6, 0.45, r"$\overline{\overline{X}\cdot\overline{Y}}=X+Y$" + "\n" +
            r"$F=\overline{\overline{AB}\cdot\overline{CD}}$", ha="center", va="top", fontsize=9)
    line(ax, [(-0.3, -0.75), (15.3, -0.75)], color=GRID, lw=0.8)

    # ---- bottom: warning lamp output ----
    yK, yI, yF = -2.0, -2.9, -4.2
    ax.text(0.15, -1.25, "warning output in NAND form", fontsize=8.5, weight="bold", ha="left")
    n1 = place(d, logic.Not, 1.6, yI, scale=s)
    nd = place(d, logic.Nand, 4.0, yK, scale=s)
    n2 = place(d, logic.Not, 1.6, yF, scale=s)
    og = place(d, logic.Or, 8.0, A(nd, "out")[1], scale=s, inputnots=[1, 2])
    for y, lab in ((yK, "K"), (yI, "I"), (yF, "F")):
        ax.text(0.35, y, f"${lab}$", ha="right", va="center", fontsize=9)
    line(ax, [(0.7, yK), A(nd, "in1")])
    line(ax, [(0.7, yI), A(n1, "in1")])
    line(ax, [A(n1, "out"), (3.3, yI), (3.3, A(nd, "in2")[1]), A(nd, "in2")])
    ax.text(2.75, yI + 0.12, r"$\overline{I}$", ha="center", va="bottom", fontsize=8.5)
    line(ax, [(0.7, yF), A(n2, "in1")])
    i1, i2 = A(og, "in1"), A(og, "in2")
    line(ax, [A(nd, "out"), (7.2, A(nd, "out")[1]), (7.2, i1[1]), i1])
    ax.text(6.3, A(nd, "out")[1] + 0.12, r"$\overline{K\overline{I}}$", ha="center", va="bottom",
            fontsize=8.5)
    line(ax, [A(n2, "out"), (7.5, yF), (7.5, i2[1]), i2])
    ax.text(3.2, yF + 0.12, r"$\overline{F}$", ha="center", va="bottom", fontsize=8.5)
    oo = A(og, "out")
    line(ax, [oo, (oo[0] + 0.4, oo[1])])
    ax.text(oo[0] + 0.45, oo[1], "$W$", ha="left", va="center", fontsize=9.5)
    ax.text(10.9, -3.6, r"$W=\overline{\overline{F}\cdot\overline{K\overline{I}}}=F+K\overline{I}$",
            ha="left", va="center", fontsize=9.5)
    ax.text(10.9, -4.35, "second NAND drawn as an OR\nwith bubbled inputs (mixed logic)",
            ha="left", va="top", fontsize=7.5, color="#555555")
    d.draw(show=False)
    save(fig, "12", "fig-12-3-bubble-pushing")


# ----------------------------------------------------------------------------
def _rename_kmap_labels(kmap, mapping):
    for seg in kmap.segments:
        if isinstance(seg, SegmentText) and seg.text in mapping:
            seg.text = mapping[seg.text]


def fig_12_4():
    """K-maps: full-adder carry (with sum inset) and BCD segment a with don't-cares."""
    fig = plt.figure(figsize=(6.8, 3.9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(lw=1.1)
    # 3-variable carry map: columns B Cin, rows A; key order is (B, Cin, A)
    tt3 = [(f"{b}{c}{a}", int(a + b + c >= 2)) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    k3 = d.add(logic.Kmap(names="BCA", truthtable=tt3,
                          groups={"1.1": {"color": BLUE, "lw": 1.6},
                                  ".11": {"color": ORANGE, "lw": 1.6},
                                  "11.": {"color": GREEN, "lw": 1.6}}).at((0, 2.4)))
    _rename_kmap_labels(k3, {"BC": "$BC_{in}$"})
    # sum map inset
    tts = [(f"{b}{c}{a}", (a + b + c) % 2) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    ks = d.add(logic.Kmap(names="BCA", truthtable=tts).at((0, -1.6)).scale(0.6))
    _rename_kmap_labels(ks, {"BC": "$BC_{in}$"})
    for seg in ks.segments:
        if isinstance(seg, SegmentText):
            seg.fontsize = (seg.fontsize or 12) * 0.75
    # 4-variable segment-a map: columns CD, rows AB; key order is (C, D, A, B)
    on = {0, 2, 3, 5, 6, 7, 8, 9}
    tt4 = []
    for m in range(16):
        a, b, c, dd = (m >> 3) & 1, (m >> 2) & 1, (m >> 1) & 1, m & 1
        v = "X" if m >= 10 else int(m in on)
        tt4.append((f"{c}{dd}{a}{b}", v))
    k4 = d.add(logic.Kmap(names="CDAB", truthtable=tt4,
                          groups={"..1.": {"color": RED, "lw": 1.6, "fill": "#C6282812"},
                                  "1...": {"color": BLUE, "lw": 1.6},
                                  ".1.1": {"color": GREEN, "lw": 1.6},
                                  ".0.0": {"color": PINK, "lw": 1.6}}).at((8.6, 0.0)))
    d.draw(show=False)
    # annotations
    ax.text(2.0, 4.85 + 0.1, "", fontsize=1)
    ax.text(4.35, 3.4, "$AB$", color=BLUE, fontsize=9, ha="left", va="center")
    ax.text(4.35, 2.95, "$AC_{in}$", color=ORANGE, fontsize=9, ha="left", va="center")
    ax.text(4.35, 2.5, "$BC_{in}$", color=GREEN, fontsize=9, ha="left", va="center")
    ax.text(2.0, 1.95, r"$C_{out}=AB+AC_{in}+BC_{in}$", ha="center", va="top", fontsize=9.5)
    ax.text(2.7, -0.95, "sum: no adjacent 1s\n" + r"$S=A\oplus B\oplus C_{in}$", ha="left",
            va="center", fontsize=8.5)
    ax.text(12.85, 3.55, "$A$", color=RED, fontsize=9, ha="left")
    ax.text(12.85, 3.05, "$C$", color=BLUE, fontsize=9, ha="left")
    ax.text(12.85, 2.55, "$BD$", color=GREEN, fontsize=9, ha="left")
    ax.text(12.85, 2.05, r"$\overline{B}\,\overline{D}$" + "\n(corners)", color=PINK, fontsize=9,
            ha="left", va="top")
    ax.text(10.6, -0.45, r"$a=A+C+BD+\overline{B}\,\overline{D}$", ha="center", va="top",
            fontsize=9.5)
    ax.text(10.6, -0.95, "X = don't care (codes 10–15)", ha="center", va="top", fontsize=7.5,
            color="#555555")
    ax.autoscale_view()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - 0.3, max(x1, 14.2) + 0.2)
    ax.set_ylim(y0 - 0.3, y1 + 0.2)
    _ = (k3, ks, k4)
    save(fig, "12", "fig-12-4-karnaugh-maps")


# ----------------------------------------------------------------------------
def fig_12_5():
    """Hardware contactor interlock of an EV battery pack in NAND gates."""
    fig = plt.figure(figsize=(6.8, 4.9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(lw=1.0, fontsize=7.5)
    s = 0.6
    fs = 8
    # ---- inputs and complement rails ----
    yK, yI, yIb, yF, yP, yPb = 12.4, 11.6, 10.8, 9.9, 8.7, 7.9
    rx = dict(K=3.0, I=3.4, Ib=3.8, Fb=4.2, P=4.6, Pb=5.0)
    ybot = 1.3
    labels = [(yK, "K", "key-on request"), (yI, "I", "HV interlock loop\n(pull-down: open = 0)"),
              (yF, "F", "fault\n(pull-up: lost = 1)"), (yP, "P", "precharge done")]
    for y, nm, desc in labels:
        d.add(elm.Dot(open=True).at((0.0, y)).scale(0.8))
        ax.text(-0.15, y, f"${nm}$", ha="right", va="center", fontsize=9)
        ax.text(-0.15, y - 0.2, desc, ha="right", va="top", fontsize=6.5, color="#555555")
    # K
    line(ax, [(0.0, yK), (rx["K"], yK), (rx["K"], ybot)])
    # I and I-bar
    line(ax, [(0.0, yI), (rx["I"], yI), (rx["I"], ybot)])
    dot(ax, 1.0, yI)
    n_i = place(d, logic.Not, 1.6, yIb, scale=s)
    line(ax, [(1.0, yI), (1.0, yIb), A(n_i, "in1")])
    line(ax, [A(n_i, "out"), (rx["Ib"], yIb), (rx["Ib"], ybot)])
    ax.text(rx["Ib"] - 0.1, yIb + 0.08, r"$\overline{I}$", ha="right", va="bottom", fontsize=fs)
    # pull-down on I
    dot(ax, 0.45, yI)
    d.add(elm.Resistor().at((0.45, yI)).down(0.55).scale(0.35))
    d.add(elm.Ground().at((0.45, yI - 0.55)).scale(0.45))
    # F -> F-bar (with pull-up)
    n_f = place(d, logic.Not, 1.6, yF, scale=s)
    line(ax, [(0.0, yF), A(n_f, "in1")])
    line(ax, [A(n_f, "out"), (rx["Fb"], yF), (rx["Fb"], ybot)])
    ax.text(rx["Fb"] - 0.1, yF + 0.08, r"$\overline{F}$", ha="right", va="bottom", fontsize=fs)
    dot(ax, 0.45, yF)
    d.add(elm.Resistor().at((0.45, yF)).up(0.5).scale(0.35))
    line(ax, [(0.25, yF + 0.5), (0.65, yF + 0.5)])
    ax.text(0.75, yF + 0.52, "$V_{CC}$", ha="left", va="center", fontsize=6.5)
    # P and P-bar
    line(ax, [(0.0, yP), (rx["P"], yP), (rx["P"], ybot)])
    dot(ax, 1.0, yP)
    n_p = place(d, logic.Not, 1.6, yPb, scale=s)
    line(ax, [(1.0, yP), (1.0, yPb), A(n_p, "in1")])
    line(ax, [A(n_p, "out"), (rx["Pb"], yPb), (rx["Pb"], ybot)])
    ax.text(rx["Pb"] - 0.1, yPb + 0.08, r"$\overline{P}$", ha="right", va="bottom", fontsize=fs)

    def tap(rail, y, x_to):
        line(ax, [(rx[rail], y), (x_to, y)])
        dot(ax, rx[rail], y)

    # ---- T = K I F' ----
    g1 = place(d, logic.Nand, 6.0, 7.0, scale=s, inputs=3)
    tap("K", A(g1, "in1")[1], 6.0)
    tap("I", A(g1, "in2")[1], 6.0)
    tap("Fb", A(g1, "in3")[1], 6.0)
    i1 = place(d, logic.Not, A(g1, "out")[0] + 0.2, A(g1, "out")[1], scale=s)
    line(ax, [A(g1, "out"), A(i1, "in1")])
    xT = 9.2
    yT = A(i1, "out")[1]
    line(ax, [A(i1, "out"), (xT, yT), (xT, 3.3)])
    dot(ax, xT, yT)
    ax.text(A(i1, "out")[0] + 0.1, yT + 0.08, "$T$", ha="left", va="bottom", fontsize=9, color=BLUE)
    # ---- R = T P', M = T P ----
    g2 = place(d, logic.Nand, 9.8, 5.45, scale=s)
    g3 = place(d, logic.Nand, 9.8, 3.9, scale=s)
    for g, rail in ((g2, "Pb"), (g3, "P")):
        line(ax, [(xT, A(g, "in1")[1]), A(g, "in1")])
        dot(ax, xT, A(g, "in1")[1])
        tap(rail, A(g, "in2")[1], A(g, "in2")[0])
    i2 = place(d, logic.Not, A(g2, "out")[0] + 0.2, A(g2, "out")[1], scale=s)
    i3 = place(d, logic.Not, A(g3, "out")[0] + 0.2, A(g3, "out")[1], scale=s)
    line(ax, [A(g2, "out"), A(i2, "in1")])
    line(ax, [A(g3, "out"), A(i3, "in1")])
    # ---- W = NAND(F', NAND(K, I')) ----
    g4 = place(d, logic.Nand, 6.0, 2.55, scale=s)
    tap("K", A(g4, "in1")[1], 6.0)
    tap("Ib", A(g4, "in2")[1], 6.0)
    g5 = place(d, logic.Nand, 9.8, 2.15, scale=s)
    line(ax, [A(g4, "out"), (A(g4, "out")[0] + 0.3, A(g4, "out")[1]),
              (A(g4, "out")[0] + 0.3, A(g5, "in1")[1]), A(g5, "in1")])
    tap("Fb", A(g5, "in2")[1], A(g5, "in2")[0])
    # ---- drivers: AND with MCU enable, then a low-side NPN ----
    xa = 13.2
    outs = [("N", yT, None), ("R", A(i2, "out")[1], i2), ("M", A(i3, "out")[1], i3)]
    coil = {"N": r"$K_N$", "R": r"$K_R$", "M": r"$K_M$"}
    for nm, ysig, inv in outs:
        ga = place(d, logic.And, xa, ysig, scale=s)
        src = (xT, yT) if inv is None else A(inv, "out")
        line(ax, [src, A(ga, "in1")])
        ax.text(12.3, ysig + 0.06, f"${nm}$", ha="center", va="bottom", fontsize=8.5, color=BLUE)
        line(ax, [(12.1, A(ga, "in2")[1]), A(ga, "in2")])
        ax.text(12.1, A(ga, "in2")[1] - 0.1, f"MCU EN$_{nm}$", ha="left", va="top", fontsize=6,
                color="#555555")
        yd = A(ga, "out")[1]
        q = d.add(elm.BjtNpn().theta(0).at((A(ga, "out")[0] + 0.55, yd)).anchor("base").scale(0.5))
        line(ax, [A(ga, "out"), A(q, "base")])
        e = A(q, "emitter")
        line(ax, [e, (e[0], e[1] - 0.15)])
        d.add(elm.Ground().at((e[0], e[1] - 0.15)).scale(0.35))
        c = A(q, "collector")
        line(ax, [c, (c[0], c[1] + 0.15)])
        ax.text(c[0] + 0.1, c[1] + 0.12, "coil " + coil[nm], ha="left", va="center", fontsize=6.5)
    # W lamp output
    wo = A(g5, "out")
    line(ax, [wo, (wo[0] + 0.5, wo[1])])
    ax.text(wo[0] + 0.55, wo[1], "$W$ (warning lamp)", ha="left", va="center", fontsize=8,
            color=BLUE)
    ax.text(7.5, 0.6, r"$T=KI\overline{F}$,  $N=T$,  $R=T\overline{P}$,  $M=TP$,  "
            r"$W=F+K\overline{I}$", ha="center", va="center", fontsize=8.5)
    # ---- power circuit ----
    xb, xc = 17.3, 20.6
    ytop, ylow = 7.4, 2.4
    d.add(elm.Battery().at((xb, ylow)).up(ytop - ylow).scale(0.8)
          .label("400 V\npack", loc="top", ofst=0.15))
    d.add(elm.Switch().at((xb, ytop)).right(xc - xb).scale(0.8))
    ax.text((xb + xc) / 2, ytop - 0.25, "main + ($M$)", ha="center", va="top", fontsize=7)
    ypc = ytop + 1.3
    line(ax, [(xb, ytop), (xb, ypc)])
    dot(ax, xb, ytop)
    d.add(elm.Switch().at((xb, ypc)).right(1.5).scale(0.6))
    d.add(elm.Resistor().at((xb + 1.5, ypc)).right(xc - xb - 1.5).scale(0.6))
    line(ax, [(xc, ypc), (xc, ytop)])
    dot(ax, xc, ytop)
    ax.text(xb + 0.75, ypc + 0.3, "precharge ($R$)", ha="center", va="bottom", fontsize=7)
    ax.text(xb + 1.5 + (xc - xb - 1.5) / 2, ypc - 0.3, "47 Ω", ha="center", va="top", fontsize=7)
    d.add(elm.Capacitor().at((xc, ytop)).down(ytop - ylow).scale(0.8)
          .label("DC link\n500 µF", loc="bottom", ofst=0.15))
    d.add(elm.Switch().at((xb, ylow)).right(xc - xb).scale(0.8))
    ax.text((xb + xc) / 2, ylow - 0.25, "main − ($N$)", ha="center", va="top", fontsize=7)
    dot(ax, xc, ylow)
    line(ax, [(xc, ytop), (xc + 0.6, ytop)])
    line(ax, [(xc, ylow), (xc + 0.6, ylow)])
    ax.text(xc + 0.65, ytop + 0.15, "to inverter", ha="left", va="bottom", fontsize=7)
    d.draw(show=False)
    ax.autoscale_view()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - 1.9, x1 + 0.3)
    ax.set_ylim(y0 - 0.2, y1 + 0.2)
    save(fig, "12", "fig-12-5-contactor-interlock")


if __name__ == "__main__":
    fig_12_1()
    fig_12_2()
    fig_12_3()
    fig_12_4()
    fig_12_5()
