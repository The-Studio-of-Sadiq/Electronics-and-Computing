"""Figures for Chapter 10 — Analog Integrated Circuits.

Run from the repository root:  python figures/scripts/ch10.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyArrowPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
RED = "#C62828"
VT = 0.02585  # thermal voltage at 300 K


# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------
def drawing(ax, fontsize=9, lw=1.1):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=fontsize, lw=lw, unit=2.0)
    return d


def finish(ax, d, pad=0.3):
    """Draw a schemdraw drawing onto ax and tidy the axis."""
    d.draw(show=False)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale_view()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_ylim(y0 - pad, y1 + pad)


def wire(d, pts, **kw):
    """Polyline of schemdraw wires through the given points."""
    for p, q in zip(pts[:-1], pts[1:]):
        d.add(elm.Line(**kw).at(p).to(q))


def dot(d, p):
    d.add(elm.Dot().at(p))


# ----------------------------------------------------------------------------
def fig_10_1():
    """BJT long-tailed pair and its large-signal transfer characteristic."""
    fig = plt.figure(figsize=(6.8, 3.4))
    axc = fig.add_axes([0.0, 0.0, 0.46, 1.0])
    axp = fig.add_axes([0.58, 0.16, 0.40, 0.76])

    d = drawing(axc, fontsize=8.5)
    # transistors: Q1 base on the left, Q2 mirrored
    q1 = d.add(elm.BjtNpn(circle=True).theta(0).at((2.0, 3.0)).anchor("center"))
    q2 = d.add(elm.BjtNpn(circle=True).reverse().theta(0).at((5.0, 3.0)).anchor("center"))
    c1, c2 = q1.collector, q2.collector
    e1, e2 = q1.emitter, q2.emitter
    vcc_y = 7.0
    d.add(elm.Resistor().at((c1[0], vcc_y)).to(c1).label(r"$R_C$" + "\n20 kΩ", loc="top", ofst=0.15))
    d.add(elm.Resistor().at((c2[0], vcc_y)).to(c2).label(r"$R_C$" + "\n20 kΩ", loc="bottom", ofst=0.15))
    wire(d, [(c1[0] - 0.4, vcc_y), (c2[0] + 0.4, vcc_y)])
    axc.text((c1[0] + c2[0]) / 2, vcc_y + 0.25, r"$V_{CC}=+15$ V", ha="center", va="bottom", fontsize=9)
    # collector outputs
    o1 = (c1[0], c1[1] + 0.35)
    o2 = (c2[0], c2[1] + 0.35)
    dot(d, o1)
    dot(d, o2)
    axc.text(o1[0] + 0.15, o1[1] + 0.05, r"$v_{C1}$", ha="left", va="bottom", fontsize=9, color=BLUE)
    axc.text(o2[0] - 0.15, o2[1] + 0.05, r"$v_{C2}$", ha="right", va="bottom", fontsize=9, color=ORANGE)
    # vod between collectors
    axc.annotate("", xy=(o2[0] - 0.05, o1[1] - 0.25), xytext=(o1[0] + 0.05, o1[1] - 0.25),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    axc.text((o1[0] + o2[0]) / 2, o1[1] - 0.32, r"$+\ v_{od}\ -$", ha="center", va="top", fontsize=9)
    # bases
    d.add(elm.Line().at(q1.base).left(0.6))
    axc.text(q1.base[0] - 0.7, q1.base[1], r"$v_{B1}$", ha="right", va="center", fontsize=9)
    d.add(elm.Line().at(q2.base).right(0.6))
    axc.text(q2.base[0] + 0.7, q2.base[1], r"$v_{B2}$", ha="left", va="center", fontsize=9)
    # emitters to tail node
    tail = ((e1[0] + e2[0]) / 2, e1[1] - 0.6)
    tail_top = tail
    wire(d, [e1, (e1[0], tail[1]), (e2[0], tail[1]), e2])
    dot(d, tail_top)
    # tail current source and REE in parallel
    wire(d, [tail, (tail[0], tail[1] - 0.9)])
    tail = (tail[0], tail[1] - 0.9)
    vee_y = tail[1] - 2.4
    xs, xr = tail[0] - 0.7, tail[0] + 0.7
    wire(d, [(xs, tail[1]), (xr, tail[1])])
    d.add(elm.SourceI().at((xs, tail[1])).down(tail[1] - vee_y)
          .label(r"$I_{EE}$" + "\n200 µA", loc="top", ofst=0.15))
    d.add(elm.Resistor().at((xr, tail[1])).to((xr, vee_y))
          .label(r"$R_{EE}$" + "\n1 MΩ", loc="bottom", ofst=0.15))
    wire(d, [(xs, vee_y), (xr, vee_y)])
    axc.text(tail[0], vee_y - 0.2, r"$V_{EE}=-15$ V", ha="center", va="top", fontsize=9)
    axc.text(q1.center[0] - 0.55, q1.center[1] + 0.55, r"$Q_1$", fontsize=9, ha="right")
    axc.text(q2.center[0] + 0.55, q2.center[1] + 0.55, r"$Q_2$", fontsize=9, ha="left")
    finish(axc, d)

    # ---- transfer characteristic ----
    vid = np.linspace(-0.2, 0.2, 801)
    x = vid / (2 * VT)
    i1 = 0.5 * (1 + np.tanh(x))
    i2 = 0.5 * (1 - np.tanh(x))
    axp.axvspan(-9e-3 * 1e3, 9e-3 * 1e3, color=GREEN, alpha=0.18, lw=0)
    axp.axhline(0, color=GRID, lw=0.8, zorder=0)
    axp.plot(vid * 1e3, i1, color=BLUE, label=r"$i_{C1}/I_{EE}$")
    axp.plot(vid * 1e3, i2, color=ORANGE, label=r"$i_{C2}/I_{EE}$")
    axp.plot(vid * 1e3, i1 - i2, color=INK, lw=1.4, ls="--",
             label=r"$(i_{C1}-i_{C2})/I_{EE}$")
    v90 = 2 * VT * np.arctanh(0.9) * 1e3
    for s in (-1, 1):
        axp.axvline(s * v90, color=GRID, lw=0.9, ls=":", zorder=0)
        axp.plot([s * v90], [s * 0.9], "o", color=INK, ms=4)
    axp.text(v90 + 6, 0.9, "90 %\nswitched\n(±76 mV)", fontsize=7.5, va="top", ha="left")
    axp.text(0, -0.93, "±9 mV:\n1 % linear", fontsize=7.5, ha="center", va="bottom", color=GREEN)
    axp.set_xlim(-200, 200)
    axp.set_ylim(-1.05, 1.05)
    axp.set_xlabel(r"$v_{id}$ (mV)")
    axp.set_ylabel("normalised collector current")
    axp.legend(fontsize=7.5, loc="lower right", handlelength=1.6, borderaxespad=0.1)
    save(fig, "10", "fig-10-1-differential-pair")


def _terminal(d, ax, p, text, up=True, color=INK):
    """Open output terminal at p with a current arrow pointing into the device below."""
    d.add(elm.Dot(open=True).at(p))
    y0 = p[1] + (0.75 if up else -0.75)
    ax.annotate("", xy=(p[0] + 0.25, p[1] - 0.05), xytext=(p[0] + 0.25, y0 - 0.25),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0, mutation_scale=9))
    ax.text(p[0] + 0.4, p[1] + 0.25, text, ha="left", va="center", fontsize=8.5, color=color)


def fig_10_2():
    """Four integrated current mirrors: basic, Widlar, Wilson and MOS cascode."""
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    d = drawing(ax, fontsize=8.5)
    gy = -2.0          # ground level
    top = 4.4          # supply rail
    fs = 8.5

    def bjt_pair(x0, diode_y=1.2, emit2_res=None):
        q1 = d.add(elm.BjtNpn(circle=True).reverse().theta(0).at((x0 + 0.8, 0)).anchor("center"))
        q2 = d.add(elm.BjtNpn(circle=True).theta(0).at((x0 + 3.0, 0)).anchor("center"))
        wire(d, [q1.base, q2.base])
        return q1, q2

    def rail(x0, x1, label):
        wire(d, [(x0, top), (x1, top)])
        ax.text((x0 + x1) / 2, top + 0.15, label, ha="center", va="bottom", fontsize=fs)

    def iref(x, y_bot, label):
        d.add(elm.SourceI().at((x, top)).down(top - y_bot))
        ax.text(x - 0.8, (top + y_bot) / 2, label
, ha="right", va="center", fontsize=fs)

    def gnd(p):
        wire(d, [p, (p[0], gy)])
        d.add(elm.Ground().at((p[0], gy)))

    # (a) basic mirror ---------------------------------------------------------
    x0 = 0.0
    q1, q2 = bjt_pair(x0)
    node = (x0 + 0.8, 1.3)
    wire(d, [q1.collector, node, (x0 + 1.9, 1.3), (x0 + 1.9, 0)])
    dot(d, node); dot(d, (x0 + 1.9, 0))
    rail(x0 + 0.3, x0 + 1.3, r"$V_{CC}$")
    iref(x0 + 0.8, 1.3, r"$I_{REF}$" + "\n100 µA")
    gnd(q1.emitter); gnd(q2.emitter)
    out = (x0 + 3.0, 2.2)
    wire(d, [q2.collector, out])
    _terminal(d, ax, out, r"$I_{OUT}$")
    # base currents
    ax.annotate("", xy=(x0 + 1.76, 0.3), xytext=(x0 + 1.76, 1.1),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.0, mutation_scale=8))
    ax.text(x0 + 1.68, 0.8, r"$2I_B$", ha="right", va="center", fontsize=8, color=ORANGE)
    ax.text(x0 + 0.15, -0.6, r"$Q_1$", fontsize=fs, ha="right")
    ax.text(x0 + 3.65, -0.6, r"$Q_2$", fontsize=fs, ha="left")

    # (b) Widlar ---------------------------------------------------------------
    x0 = 4.9
    q1, q2 = bjt_pair(x0)
    node = (x0 + 0.8, 1.3)
    wire(d, [q1.collector, node, (x0 + 1.9, 1.3), (x0 + 1.9, 0)])
    dot(d, node); dot(d, (x0 + 1.9, 0))
    rail(x0 + 0.3, x0 + 1.3, r"$V_{CC}$")
    iref(x0 + 0.8, 1.3, r"$I_{REF}$" + "\n1 mA")
    gnd(q1.emitter)
    d.add(elm.Resistor().at(q2.emitter).to((x0 + 3.0, gy)).scale(0.65)
          .label(r"$R_E$" + "\n11.9 kΩ", loc="bottom", ofst=0.1, fontsize=8))
    d.add(elm.Ground().at((x0 + 3.0, gy)))
    out = (x0 + 3.0, 2.2)
    wire(d, [q2.collector, out])
    _terminal(d, ax, out, r"$I_{OUT}$" + "\n10 µA")
    ax.text(x0 + 0.15, -0.6, r"$Q_1$", fontsize=fs, ha="right")
    ax.text(x0 + 3.65, 0.35, r"$Q_2$", fontsize=fs, ha="left")

    # (c) Wilson ---------------------------------------------------------------
    x0 = 9.8
    q1, q2 = bjt_pair(x0)
    q3 = d.add(elm.BjtNpn(circle=True).theta(0).at((x0 + 3.0, 2.1)).anchor("center"))
    fb = dict(color=ORANGE, lw=1.6)
    n1 = (x0 + 0.8, 2.1)
    wire(d, [q1.collector, n1], **fb)
    wire(d, [n1, q3.base], **fb)
    dot(d, n1)
    n2 = (x0 + 3.0, 1.05)
    wire(d, [q3.emitter, n2, q2.collector], **fb)
    wire(d, [n2, (x0 + 1.9, 1.05), (x0 + 1.9, 0)], **fb)
    wire(d, [(x0 + 1.9, 0), q1.base], **fb)
    dot(d, n2); dot(d, (x0 + 1.9, 0))
    rail(x0 + 0.3, x0 + 1.3, r"$V_{CC}$")
    iref(x0 + 0.8, 2.1, r"$I_{REF}$")
    gnd(q1.emitter); gnd(q2.emitter)
    out = (x0 + 3.0, 3.4)
    wire(d, [q3.collector, out])
    _terminal(d, ax, out, r"$I_{OUT}$")
    ax.text(x0 + 0.15, -0.6, r"$Q_1$", fontsize=fs, ha="right")
    ax.text(x0 + 3.65, -0.6, r"$Q_2$", fontsize=fs, ha="left")
    ax.text(x0 + 3.65, 1.6, r"$Q_3$", fontsize=fs, ha="left")
    ax.text(x0 + 1.5, 2.38, "feedback", fontsize=7.5, color=ORANGE, ha="center", va="bottom")

    # (d) NMOS cascode -----------------------------------------------------------
    x0 = 14.7
    m1 = d.add(elm.NMos().reverse().theta(0).at((x0 + 0.8, 0)).anchor("center"))
    m2 = d.add(elm.NMos().theta(0).at((x0 + 3.0, 0)).anchor("center"))
    m3 = d.add(elm.NMos().reverse().theta(0).at((x0 + 0.8, 2.1)).anchor("center"))
    m4 = d.add(elm.NMos().theta(0).at((x0 + 3.0, 2.1)).anchor("center"))
    wire(d, [m1.gate, m2.gate])
    wire(d, [m3.gate, m4.gate])
    n1 = (x0 + 0.8, 1.05)
    wire(d, [m1.drain, n1, m3.source])
    wire(d, [n1, (x0 + 1.9, 1.05), (x0 + 1.9, m1.gate[1])])
    dot(d, n1); dot(d, (x0 + 1.9, m1.gate[1]))
    wire(d, [m2.drain, m4.source])
    n3 = (x0 + 0.8, 3.2)
    wire(d, [m3.drain, n3, (x0 + 1.9, 3.2), (x0 + 1.9, m3.gate[1])])
    dot(d, n3); dot(d, (x0 + 1.9, m3.gate[1]))
    wire(d, [(x0 + 0.3, top), (x0 + 1.3, top)])
    ax.text(x0 + 0.8, top + 0.15, r"$V_{DD}$", ha="center", va="bottom", fontsize=fs)
    d.add(elm.SourceI().at((x0 + 0.8, top)).down(top - 3.2))
    ax.text(x0 + 0.05, 3.8, r"$I_{REF}$", ha="right"
, va="center", fontsize=fs)
    gnd(m1.source); gnd(m2.source)
    out = (x0 + 3.0, 3.4)
    wire(d, [m4.drain, out])
    _terminal(d, ax, out, r"$I_{OUT}$")
    for m, lab, dx, ha in ((m1, "$M_1$", -0.45, "right"), (m2, "$M_2$", 0.45, "left"),
                           (m3, "$M_3$", -0.45, "right"), (m4, "$M_4$", 0.45, "left")):
        ax.text(m.center[0] + dx, m.center[1] + 0.35, lab, fontsize=fs, ha=ha)
    ax.annotate(r"$R_{out}\approx g_m r_o^2$" + "\n" + r"$V_{OUT,\min}=V_{TH}+2V_{ov}$",
                xy=(x0 + 3.08, 3.3), xytext=(x0 + 3.2, 4.6),
                fontsize=8, ha="left", va="bottom", color=BLUE,
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.9, mutation_scale=8))


    finish(ax, d)
    ymin = ax.get_ylim()[0]
    for i, t in enumerate(["(a) basic", "(b) Widlar", "(c) Wilson", "(d) NMOS cascode"]):
        ax.text(1.9 + 4.9 * i, gy - 0.75, t, ha="center", va="top", fontsize=9)
    ax.set_ylim(gy - 1.25, ax.get_ylim()[1])
    save(fig, "10", "fig-10-2-current-mirrors")


def fig_10_3():
    """Two-stage CMOS op-amp with Miller compensation and its small-signal model."""
    fig = plt.figure(figsize=(6.8, 5.0))
    axs = fig.add_axes([0.0, 0.40, 1.0, 0.60])
    axm = fig.add_axes([0.0, 0.0, 1.0, 0.37])
    fs = 8.5

    # ---------------- transistor-level schematic ----------------
    d = drawing(axs, fontsize=fs)
    vdd, gnd_y = 5.4, -1.25
    m3 = d.add(elm.PMos().reverse().theta(0).at((1.0, 4.2)).anchor("center"))
    m4 = d.add(elm.PMos().theta(0).at((3.4, 4.2)).anchor("center"))
    m1 = d.add(elm.NMos().theta(0).at((1.0, 2.0)).anchor("center"))
    m2 = d.add(elm.NMos().reverse().theta(0).at((3.4, 2.0)).anchor("center"))
    m5 = d.add(elm.NMos().theta(0).at((2.2, 0.0)).anchor("center"))
    xo = 7.6
    m6 = d.add(elm.PMos().theta(0).at((xo, 4.2)).anchor("center"))
    m7 = d.add(elm.NMos().theta(0).at((xo, 0.0)).anchor("center"))
    # rails
    wire(d, [(0.4, vdd), (xo + 1.6, vdd)])
    wire(d, [(0.4, gnd_y), (xo + 1.6, gnd_y)])
    axs.text(0.3, vdd, r"$V_{DD}=3.3$ V", ha="right", va="center", fontsize=fs)
    d.add(elm.Ground().at((0.4, gnd_y)))
    for m in (m3, m4, m6):
        wire(d, [m.source, (m.source[0], vdd)])
    for m in (m5, m7):
        wire(d, [m.source, (m.source[0], gnd_y)])
    # mirror
    wire(d, [m3.gate, m4.gate])
    n3 = (1.0, 3.1)
    wire(d, [m3.drain, n3, m1.drain])
    wire(d, [n3, (2.2, 3.1), (2.2, m3.gate[1])])
    dot(d, n3); dot(d, (2.2, m3.gate[1]))
    n1 = (3.4, 3.1)
    wire(d, [m4.drain, n1, m2.drain])
    dot(d, n1)
    # tail
    wire(d, [m1.source, (1.0, 0.95), (3.4, 0.95), m2.source])
    wire(d, [(2.2, 0.95), m5.drain])
    dot(d, (2.2, 0.95))
    # node 1 to M6 gate
    xg = 5.4
    wire(d, [n1, (xg, 3.1), (xg, m6.gate[1]), m6.gate])
    dot(d, (xg, 3.1))
    axs.text(xg - 0.1, 3.2, "node 1", ha="right", va="bottom", fontsize=8, color=BLUE)
    # output
    vo = (xo, 2.0)
    wire(d, [m6.drain, vo, m7.drain])
    dot(d, vo)
    wire(d, [vo, (xo + 2.4, 2.0)])
    d.add(elm.Dot(open=True).at((xo + 2.4, 2.0)))
    axs.text(xo + 2.5, 2.0, r"$v_{out}$", ha="left", va="center", fontsize=9)
    xcl = xo + 1.5
    dot(d, (xcl, 2.0))
    d.add(elm.Capacitor().at((xcl, 2.0)).down(2.0 - gnd_y)
          .label(r"$C_L$" + "\n10 pF", loc="bottom", ofst=0.1))
    # Miller network Rz + Cc between node 1 and output
    wire(d, [(xg, 3.1), (xg, 2.0)])
    d.add(elm.Resistor().at((xg, 2.0)).right(1.0).scale(0.7).label(r"$R_z$", loc="bottom", ofst=0.08))
    d.add(elm.Capacitor().to(vo).label(r"$C_c$ = 3 pF", loc="top", ofst=0.08))
    # bias gates
    for m in (m5, m7):
        wire(d, [m.gate, (m.gate[0] - 0.35, m.gate[1])])
        axs.text(m.gate[0] - 0.42, m.gate[1], r"$V_B$", ha="right", va="center", fontsize=8)
    # inputs
    wire(d, [m1.gate, (m1.gate[0] - 0.35, m1.gate[1])])
    axs.text(m1.gate[0] - 0.42, m1.gate[1], r"$v_{-}$", ha="right", va="center", fontsize=9)
    wire(d, [m2.gate, (m2.gate[0] + 0.35, m2.gate[1])])
    axs.text(m2.gate[0] + 0.42, m2.gate[1], r"$v_{+}$", ha="left", va="center", fontsize=9)
    # names and currents
    for m, lab, dx, ha in ((m3, "$M_3$", -0.4, "right"), (m4, "$M_4$", 0.4, "left"),
                           (m1, "$M_1$", 0.4, "left"), (m2, "$M_2$", -0.4, "right"),
                           (m5, "$M_5$", 0.4, "left"), (m6, "$M_6$", 0.4, "left"),
                           (m7, "$M_7$", 0.4, "left")):
        axs.text(m.center[0] + dx, m.center[1] + 0.45, lab, fontsize=fs, ha=ha)
    axs.text(2.55, -0.8, "20 µA", fontsize=8, color=ORANGE, ha="left")
    axs.text(xo + 0.3, -0.8, "200 µA", fontsize=8, color=ORANGE, ha="left")
    finish(axs, d, pad=0.2)

    # ---------------- small-signal model ----------------
    d = drawing(axm, fontsize=fs)
    yt, yb = 2.0, 0.0
    x_n1, x_o = 3.6, 9.6

    def branch(x, kind, lab):
        if kind == "src":
            d.add(elm.SourceControlledI().at((x, yb)).up(yt - yb))
            axm.text(x - 0.6, (yt + yb) / 2, lab, ha="right", va="center", fontsize=8.5)
            return
        elif kind == "R":
            e = elm.Resistor().at((x, yt)).down(yt - yb)
        else:
            e = elm.Capacitor().at((x, yt)).down(yt - yb)
        d.add(e.label(lab, loc="bottom", ofst=0.1))

    branch(0.6, "src", r"$G_{m1}v_{id}$" + "\n188 µS")
    branch(1.8, "R", r"$R_1$")
    branch(3.0, "C", r"$C_1$")
    wire(d, [(0.6, yt), (x_n1, yt)])
    wire(d, [(0.6, yb), (x_o + 4.0, yb)])
    for x in (1.8, 3.0):
        dot(d, (x, yt)); dot(d, (x, yb))
    dot(d, (x_n1, yt))
    axm.text(x_n1, yt + 0.25, r"node 1 ($v_1$)", ha="center", va="bottom", fontsize=8, color=BLUE)
    d.add(elm.Resistor().at((x_n1, yt)).right(2.2).label(r"$R_z$", loc="top", ofst=0.05))
    d.add(elm.Capacitor().to((x_o, yt)).label(r"$C_c$ = 3 pF", loc="top", ofst=0.05))

    dot(d, (x_o, yt))
    branch(x_o + 1.6, "src", r"$G_{m2}v_1$" + "\n1.38 mS")
    branch(x_o + 2.8, "R", r"$R_2$")
    branch(x_o + 4.0, "C", r"$C_L$" + "\n10 pF")
    wire(d, [(x_o, yt), (x_o + 4.0, yt)])
    for x in (x_o + 1.6, x_o + 2.8):
        dot(d, (x, yt)); dot(d, (x, yb))
    axm.text(x_o + 0.3, yt + 0.25, r"$v_{out}$", ha="center", va="bottom", fontsize=9)
    d.add(elm.Ground().at((5.6, yb)))
    finish(axm, d, pad=0.2)
    save(fig, "10", "fig-10-3-two-stage-op-amp")


# ----------------------------------------------------------------------------
# two-stage op-amp design numbers (Section 10.5 worked example)
GBW = 10e6
CL, CC = 10e-12, 3e-12
GM2 = 2.2 * 2 * np.pi * GBW * CL        # 1.38 mS
GM1 = 2 * np.pi * GBW * CC              # 188 uS
A0 = 1e4                                # 80 dB


def _crossover(f, H):
    """Unity-gain frequency and phase margin, interpolated in log f."""
    mag = np.abs(H)
    ph = np.degrees(np.unwrap(np.angle(H)))
    i = np.where(mag < 1)[0][0]
    lf = np.log10(f[i - 1:i + 1])
    lm = np.log10(mag[i - 1:i + 1])
    t = lm[0] / (lm[0] - lm[1])
    fu = 10 ** (lf[0] + t * (lf[1] - lf[0]))
    return fu, 180 + ph[i - 1] + t * (ph[i] - ph[i - 1])


def fig_10_4():
    """Open-loop Bode plot before and after Miller compensation."""
    f = np.logspace(1, 9, 4000)
    s = 2j * np.pi * f
    # uncompensated: two poles at 20 kHz and 200 kHz
    Hu = A0 / ((1 + s / (2 * np.pi * 20e3)) * (1 + s / (2 * np.pi * 200e3)))
    p1 = GM1 / CC / A0
    p2 = GM2 / CL
    z = GM2 / CC
    Hc = A0 * (1 - s / z) / ((1 + s / p1) * (1 + s / p2))       # Rz = 0
    Hn = A0 / ((1 + s / p1) * (1 + s / p2))                      # Rz = 1/Gm2
    fu_u, pm_u = _crossover(f, Hu)
    fu_c, pm_c = _crossover(f, Hc)
    fu_n, pm_n = _crossover(f, Hn)

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True,
                                 gridspec_kw=dict(hspace=0.12, height_ratios=[1.1, 1]))
    db = lambda H: 20 * np.log10(np.abs(H))  # noqa: E731
    ph = lambda H: np.degrees(np.unwrap(np.angle(H)))  # noqa: E731
    a1.semilogx(f, db(Hu), color=ORANGE, ls="--", label="uncompensated")
    a1.semilogx(f, db(Hc), color=BLUE, label=r"compensated, $R_z=0$")
    a1.semilogx(f, db(Hn), color=GREEN, ls=":", lw=2.0, label=r"compensated, $R_z=723\ \Omega$")
    a1.axhline(0, color=GRID, lw=0.9, zorder=0)
    a1.set_ylim(-40, 100)
    a1.set_ylabel("magnitude (dB)")
    a1.set_yticks(range(-40, 101, 20))
    a1.grid(True, which="major", color=GRID, lw=0.5)
    # markers
    fp1 = p1 / 2 / np.pi
    for fx, lab, yy in ((fp1, r"$p_1$ = 1 kHz", 85), (p2 / 2 / np.pi, r"$p_2$ = 22 MHz", -12),
                        (z / 2 / np.pi, "RHP zero\n73 MHz", -12)):
        a1.axvline(fx, color=GRID, lw=0.8, ls="--", zorder=0)
        a2.axvline(fx, color=GRID, lw=0.8, ls="--", zorder=0)
    a1.annotate(r"$p_1\approx$ 1 kHz", xy=(fp1, 77), xytext=(fp1 * 2.2, 88), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    a1.text(p2 / 2 / np.pi / 1.12, 97, r"$p_2$" + "\n22 MHz", fontsize=7.5, ha="right", va="top")
    a1.text(z / 2 / np.pi * 1.12, 97, "RHP\nzero\n73 MHz", fontsize=7.5, ha="left", va="top")
    a1.plot([fu_c], [0], "o", color=BLUE, ms=4)
    a1.annotate(f"{fu_c / 1e6:.1f} MHz\n" + r"(GBW $=g_{m1}/C_c$)", xy=(fu_c, 0), xytext=(3e5, -30),
                fontsize=8, color=BLUE, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.8, mutation_scale=8))
    a1.plot([fu_u], [0], "o", color=ORANGE, ms=4)
    a1.annotate(f"{fu_u / 1e6:.1f} MHz", xy=(fu_u, 0), xytext=(fu_u * 3, 30), fontsize=8,
                color=ORANGE, arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.8, mutation_scale=8))
    a1.legend(fontsize=8, loc="lower left")

    a2.semilogx(f, ph(Hu), color=ORANGE, ls="--")
    a2.semilogx(f, ph(Hc), color=BLUE)
    a2.semilogx(f, ph(Hn), color=GREEN, ls=":", lw=2.0)
    a2.axhline(-180, color=INK, lw=0.8, ls="-.", zorder=0)
    a2.set_ylim(-275, 5)
    a2.set_yticks(range(-270, 1, 45))
    a2.set_ylabel("phase (°)")
    a2.set_xlabel("frequency (Hz)")
    a2.grid(True, which="major", color=GRID, lw=0.5)
    a2.set_xlim(10, 1e9)
    # phase margins
    for fu, pm, col in ((fu_n * 1.3, pm_n, GREEN), (fu_c, pm_c, BLUE)):
        a2.annotate("", xy=(fu, -180 + pm), xytext=(fu, -180),
                    arrowprops=dict(arrowstyle="<|-|>", color=col, lw=1.0, mutation_scale=8,
                                    shrinkA=0, shrinkB=0))
    a2.text(fu_c * 0.8, -150, f"PM = {pm_c:.1f}°\n" + r"($R_z=0$)", fontsize=8, color=BLUE,
            ha="right", va="center")
    a2.text(fu_n * 1.5, -97, f"PM = {pm_n:.1f}°\n" + r"($R_z=723\ \Omega$)", fontsize=8, color=GREEN,
            ha="left", va="center")
    a2.text(2e4, -222, f"uncompensated: PM ≈ {pm_u:.0f}°", fontsize=8, color=ORANGE,
            ha="left", va="center")

    a2.text(15, -176, "−180°", fontsize=7.5, va="bottom")
    save(fig, "10", "fig-10-4-miller-compensation-bode")
    return pm_c, pm_n, fu_c


def fig_10_5():
    """Brokaw bandgap cell and CTAT/PTAT slope cancellation."""
    from matplotlib.patches import Polygon
    fig = plt.figure(figsize=(6.8, 3.6))
    axc = fig.add_axes([0.0, 0.02, 0.40, 0.96])
    axp = fig.add_axes([0.52, 0.14, 0.46, 0.80])

    d = drawing(axc, fontsize=8.5)
    vcc, gnd_y = 6.0, -2.7
    q1 = d.add(elm.BjtNpn(circle=True).reverse().theta(0).at((1.0, 2.0)).anchor("center"))
    q2 = d.add(elm.BjtNpn(circle=True).theta(0).at((4.0, 2.0)).anchor("center"))
    wire(d, [q1.base, q2.base])
    vb = (2.5, q1.base[1])
    dot(d, vb)
    yc = 3.75
    for q, loc in ((q1, "top"), (q2, "bottom")):
        wire(d, [q.collector, (q.collector[0], yc)])
        dot(d, (q.collector[0], yc))
        d.add(elm.Resistor().at((q.collector[0], vcc)).to((q.collector[0], yc))
              .label(r"$R_L$", loc=loc, ofst=0.08))
    wire(d, [(0.5, vcc), (4.5, vcc)])
    axc.text(2.5, vcc + 0.15, r"$V_{CC}$", ha="center", va="bottom", fontsize=9)
    # op-amp: triangle pointing down, inputs on its top edge, output tip to the bases
    tx, ttop, tbot, hw = 2.5, 3.5, 2.45, 0.62
    axc.add_patch(Polygon([(tx - hw, ttop), (tx + hw, ttop), (tx, tbot)], closed=True,
                          fc="white", ec=INK, lw=1.1, zorder=3))
    axc.text(tx - 0.27, ttop - 0.2, "−", ha="center", va="center", fontsize=9, zorder=4)
    axc.text(tx + 0.27, ttop - 0.2, "+", ha="center", va="center", fontsize=9, zorder=4)
    wire(d, [(q1.collector[0], yc), (tx - 0.3, yc), (tx - 0.3, ttop)])
    wire(d, [(q2.collector[0], yc), (tx + 0.3, yc), (tx + 0.3, ttop)])
    wire(d, [(tx, tbot), vb])
    # VREF output terminal
    vout = (vb[0], 0.75)
    wire(d, [vb, vout])
    d.add(elm.Dot(open=True).at(vout))
    # emitters
    yx = -0.6
    d.add(elm.Resistor().at(q1.emitter).to((q1.emitter[0], yx))
          .label(r"$R_1$", loc="bottom", ofst=0.08))
    wire(d, [(q1.emitter[0], yx), (q2.emitter[0], yx), q2.emitter])
    xr2 = 2.5
    dot(d, (xr2, yx))
    d.add(elm.Resistor().at((xr2, yx)).to((xr2, gnd_y)).label(r"$R_2$", loc="top", ofst=0.08))
    d.add(elm.Ground().at((xr2, gnd_y)))
    finish(axc, d, pad=0.1)
    axc.text(q1.center[0] - 0.75, 2.5, r"$Q_1$" + "\n(area 8)", ha="right", va="bottom", fontsize=8)
    axc.text(q2.center[0] + 0.75, 2.5, r"$Q_2$" + "\n(area 1)", ha="left", va="bottom", fontsize=8)
    axc.text(vout[0], vout[1] - 0.2, r"$V_{REF}$" + "\n1.25 V", ha="center", va="top", fontsize=8.5,
             color=BLUE)
    axc.text(q1.emitter[0] - 0.25, 0.3, r"$\Delta V_{BE}$" + "\n53.8 mV", ha="right", va="center",
             fontsize=8, color=ORANGE)
    axc.text(xr2 + 0.3, -1.65, r"$R_2/R_1$" + "\n= 5.58", ha="left", va="center", fontsize=8)
    for x in (q1.collector[0] + 0.18, q2.collector[0] - 0.18):
        axc.annotate("", xy=(x, 2.85), xytext=(x, 3.45),
                     arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9, mutation_scale=7))
    axc.text(2.5, 4.9, r"equal $I_C$", ha="center", va="center", fontsize=8, color=GREEN)
    x0, x1 = axc.get_xlim()
    axc.set_xlim(x0 - 0.7, x1 + 0.7)
    # ---------------- temperature plot ----------------
    k_q = 86.17e-6
    n = 8
    T0 = 300.0
    TC = np.linspace(-40, 125, 400)
    T = TC + 273.15
    slope_ptat = k_q * np.log(n)                 # V/K
    K = 2.0e-3 / slope_ptat                      # 11.2
    a = 2.0e-3 / np.max(T * np.log(T / T0) - (T - T0))   # curvature scaled to 2 mV p-p
    curv = -a * (T * np.log(T / T0) - (T - T0))
    vbe = 0.650 - 2.0e-3 * (T - T0) + curv
    ptat = K * slope_ptat * T
    vref = vbe + ptat
    axp.plot(TC, vbe, color=BLUE)
    axp.plot(TC, ptat, color=ORANGE)
    axp.plot(TC, vref, color=INK, lw=2.0)
    axp.text(124, 0.565, r"$V_{BE}$ (CTAT)" + "\n−2.0 mV/K", color=BLUE,
             fontsize=8, ha="right", va="bottom")
    axp.text(-37, 0.33, r"$K\Delta V_{BE}$ (PTAT)" + "\n+2.0 mV/K, $K$ = 11.2",
             color=ORANGE, fontsize=8, ha="left", va="bottom")
    axp.text(-35, 1.27, r"$V_{REF}=V_{BE}+K\Delta V_{BE}\approx1.25$ V", fontsize=8, ha="left", va="bottom")
    axp.set_xlim(-40, 125)
    axp.set_ylim(0.3, 1.55)
    axp.set_xlabel("temperature (°C)")
    axp.set_ylabel("voltage (V)")
    # inset: magnified VREF
    ins = axp.inset_axes([0.47, 0.42, 0.50, 0.30])
    dv = (vref - vref.max()) * 1e3 + 0.0
    corr = 0.2 * curv * 1e3 + 0.06 * np.sin((TC + 40) / 165 * 2 * np.pi) * 0
    ins.plot(TC, (vref - 1.25) * 1e3, color=INK, lw=1.4)
    ins.plot(TC, corr + (vref.max() - 1.25) * 1e3, color=GREEN, ls=":", lw=1.6)
    lo, hi = (vref.min() - 1.25) * 1e3, (vref.max() - 1.25) * 1e3
    ins.add_patch(Rectangle((-40, lo), 165, hi - lo, fill=False, ec=RED, lw=0.8, ls="--"))
    ins.set_xlim(-45, 130)
    ins.set_ylim(lo - 0.5, hi + 1.0)
    ins.tick_params(labelsize=6.5, length=2)
    ins.set_ylabel(r"$V_{REF}-1.25$ V" + "\n(mV)", fontsize=6.5)
    ppm = (hi - lo) * 1e-3 / (1.25 * 165) * 1e6
    ins.text(42, lo + 0.1, f"{hi - lo:.1f} mV p-p, box ≈ {ppm:.0f} ppm/°C", fontsize=6.5,
             ha="center", va="bottom", color=RED)
    ins.text(42, hi + 0.3, "curvature-corrected ≈ 0.4 mV", fontsize=6.5, ha="center",
             va="bottom", color=GREEN)
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    _ = dv
    save(fig, "10", "fig-10-5-bandgap-reference")
    return K, vref


def _sar_trials(vin=1.234, vref=3.3, nbits=12):
    code, rows = 0, []
    for bit in reversed(range(nbits)):
        trial = code | (1 << bit)
        vdac = trial * vref / 2 ** nbits
        keep = vin >= vdac
        if keep:
            code = trial
        rows.append((nbits - bit, vdac, keep))
    return code, rows


def fig_10_6():
    """R-2R ladder DAC, SAR ADC block diagram and its binary search."""
    from matplotlib.patches import Polygon
    fig = plt.figure(figsize=(6.8, 5.0))
    axl = fig.add_axes([0.0, 0.50, 0.50, 0.50])
    axs = fig.add_axes([0.52, 0.50, 0.48, 0.50])
    axp = fig.add_axes([0.10, 0.08, 0.86, 0.36])

    # ---------------- R-2R ladder ----------------
    d = drawing(axl, fontsize=8)
    yt, ypole, yref, ygnd = 4.0, 1.75, 0.75, 0.15
    xs = [1.4, 3.4, 5.4, 7.4]          # b0 .. b3 nodes
    bits = [1, 1, 0, 1]                 # illustrative code 1011
    xt = xs[0] - 1.3
    d.add(elm.Resistor().at((xt, yt)).down(yt - ygnd).label("2R", loc="top", ofst=0.08))
    wire(d, [(xt, yt), (xs[0], yt)])
    for k in range(3):
        d.add(elm.Resistor().at((xs[k], yt)).right(xs[k + 1] - xs[k]).label("R", loc="top", ofst=0.08))
    for k, x in enumerate(xs):
        dot(d, (x, yt))
        d.add(elm.Resistor().at((x, yt)).down(yt - ypole - 0.05).label("2R", loc="bottom", ofst=0.08))
        # SPDT switch drawn by hand
        cl, cr = (x - 0.35, ypole - 0.55), (x + 0.35, ypole - 0.55)
        tgt = cl if bits[k] else cr
        axl.plot([x, tgt[0]], [ypole - 0.05, tgt[1] + 0.05], color=INK, lw=1.1)
        for c in (cl, cr):
            axl.plot(*c, "o", ms=3, mfc="white", mec=INK, zorder=4)
        wire(d, [cl, (cl[0], yref)])
        wire(d, [cr, (cr[0], ygnd)])
        axl.text(x + 0.5, ypole - 0.1, f"$b_{k}$", fontsize=8, ha="left", va="center", color=BLUE)
    wire(d, [(xs[0] - 0.6, yref), (xs[-1] + 0.6, yref)])
    wire(d, [(xt, ygnd), (xs[-1] + 0.6, ygnd)])
    axl.text(xs[-1] + 0.7, yref, r"$V_{REF}$", fontsize=8, ha="left", va="center")
    d.add(elm.Ground().at((xt, ygnd)))
    # output buffer
    op = d.add(elm.Opamp(leads=False).theta(0).at((9.6, yt + 0.9)).anchor("in2").scale(0.6))
    wire(d, [(xs[-1], yt), (8.6, yt), (8.6, op.in2[1]), op.in2])
    o = op.out
    wire(d, [o, (o[0] + 0.5, o[1])])
    wire(d, [(o[0] + 0.25, o[1]), (o[0] + 0.25, o[1] + 1.0), (op.in1[0] - 0.3, o[1] + 1.0),
             (op.in1[0] - 0.3, op.in1[1]), op.in1])
    dot(d, (o[0] + 0.25, o[1]))
    finish(axl, d, pad=0.1)
    axl.text(o[0] + 0.55, o[1], r"$v_{out}$", fontsize=8.5, ha="left", va="center")
    axl.text(4.4, ygnd - 1.0, r"R = 10 kΩ, 2R = 20 kΩ;  $v_{out}=V_{REF}\,D/16$",
             fontsize=8, ha="center", va="top")
    x0, x1 = axl.get_xlim()
    axl.set_xlim(x0, x1 + 0.6)
    y0, y1 = axl.get_ylim()
    axl.set_ylim(y0 - 0.6, y1)

    # ---------------- SAR block diagram ----------------
    axs.set_xlim(0, 10)
    axs.set_ylim(0, 7.4)
    axs.set_aspect("equal")
    axs.axis("off")
    box(axs, 0.2, 4.6, 2.2, 1.3, "track-\nand-hold", fontsize=8)
    # comparator triangle
    cx, cy = 3.6, 5.25
    axs.add_patch(Polygon([(cx, cy + 0.8), (cx, cy - 0.8), (cx + 1.4, cy)], closed=True,
                          fc="#EEF3F8", ec=INK, lw=1.0))
    axs.text(cx + 0.2, cy + 0.42, "+", fontsize=8, va="center")
    axs.text(cx + 0.2, cy - 0.42, "−", fontsize=8, va="center")
    axs.text(cx + 0.55, cy + 1.0, "comparator", fontsize=7.5, ha="center")
    box(axs, 6.0, 4.6, 3.6, 1.3, "SAR register\n(12 bits)", fontsize=8)
    box(axs, 3.0, 1.2, 4.6, 1.6, "12-bit capacitive DAC\nC, 2C, 4C, … , 2048C", fontsize=8)
    arrow(axs, -0.3, 5.25, 0.2, 5.25)
    axs.text(-0.3, 5.45, r"$v_{in}$", fontsize=8.5, ha="left", va="bottom")
    arrow(axs, 2.4, 5.65, cx, 5.65)
    arrow(axs, cx + 1.4, cy, 6.0, cy)
    # SAR -> DAC (12 lines)
    arrow(axs, 6.8, 4.6, 6.8, 2.8)
    axs.plot([6.6, 7.0], [3.6, 3.9], color=INK, lw=0.9)
    axs.text(7.05, 3.7, "12", fontsize=7.5, va="center")
    # DAC -> comparator (-)
    axs.plot([3.3, 3.3, cx - 0.2], [2.8, cy - 0.42, cy - 0.42], color=INK, lw=1.1)
    axs.annotate("", xy=(cx, cy - 0.42), xytext=(cx - 0.2, cy - 0.42),
                 arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=10,
                                 shrinkA=0, shrinkB=0))
    axs.text(3.2, 3.5, r"$v_{DAC}$", fontsize=8, ha="right")
    # VREF into DAC
    arrow(axs, 5.3, 0.25, 5.3, 1.2)
    axs.text(5.45, 0.4, r"$V_{REF}$ = 3.3 V", fontsize=8, ha="left", va="center")
    # output code
    arrow(axs, 9.0, 4.6, 9.0, 3.5)
    axs.text(9.0, 3.4, "code\n$D_{11}…D_0$", fontsize=7.5, ha="center", va="top")

    # ---------------- binary search ----------------
    code, rows = _sar_trials()
    steps = [r[0] for r in rows]
    v = [r[1] for r in rows]
    keep = [r[2] for r in rows]
    axp.step(steps, v, where="mid", color=GRID, lw=1.0, zorder=1)
    axp.plot(steps, v, color=BLUE, lw=1.0, zorder=2)
    for st, vv, kp in rows:
        axp.plot(st, vv, "o" if kp else "X", color=GREEN if kp else RED, ms=6, zorder=3)
    axp.axhline(1.234, color=INK, ls="--", lw=1.0)
    axp.text(12.4, 1.255, r"$v_{in}$ = 1.234 V", fontsize=8, va="bottom", ha="right")
    for (st, vv, kp), txt in zip(rows[:4], ("1.650", "0.825", "1.2375", "1.031")):
        low = st in (2, 4)
        axp.text(st + 0.15, vv + (-0.03 if low else 0.03), txt, fontsize=7.5,
                 va="top" if low else "bottom", ha="left", color=GREEN if kp else RED)
    axp.set_xlim(0.5, 12.5)
    axp.set_xticks(range(1, 13))
    axp.set_ylim(0.75, 1.75)
    axp.set_xlabel("decision step (bit tested: 11 → 0)")
    axp.set_ylabel("DAC trial voltage (V)")
    axp.plot([], [], "o", color=GREEN, label=r"kept ($v_{in}\geq v_{DAC}$)")
    axp.plot([], [], "X", color=RED, label="rejected")
    axp.legend(fontsize=7.5, loc="lower right", ncol=2)
    # zoom inset on the last steps
    ins = axp.inset_axes([0.47, 0.63, 0.36, 0.36])
    ins.plot(steps[5:], v[5:], color=BLUE, lw=1.0)
    for st, vv, kp in rows[5:]:
        ins.plot(st, vv, "o" if kp else "X", color=GREEN if kp else RED, ms=4.5)
    ins.axhline(1.234, color=INK, ls="--", lw=0.8)
    ins.set_xlim(5.6, 12.4)
    ins.set_ylim(1.180, 1.240)
    ins.set_xticks(range(6, 13))
    ins.tick_params(labelsize=6.5, length=2)
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    ins.text(12.2, 1.1835, f"code {code} (0x{code:03X})\n= {code * 3.3 / 4096:.5f} V",
             fontsize=6.8, ha="right", va="bottom")
    save(fig, "10", "fig-10-6-r2r-dac-sar-adc")
    return code


if __name__ == "__main__":
    fig_10_1()
    fig_10_2()
    fig_10_3()
    fig_10_4()
    fig_10_5()
    fig_10_6()
