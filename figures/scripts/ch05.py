"""Figures for Chapter 5 — Advanced Semiconductor Devices.

Run from the repository root:  python figures/scripts/ch05.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, AMBER, SKY = COLORS[:6]
GREY = "#888888"
C_N = "#DCEBF7"
C_NP = "#9EC5E8"
C_NM = "#EEF5FB"
C_P = "#F7E1D3"
C_PP = "#EDB896"
C_OX = "#FFF7C2"
C_POLY = "#B8B8B8"
C_MET = "#8C8C8C"


def rect(ax, x, y, w, h, fc, ec=INK, lw=0.8, **kw):
    p = Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw)
    ax.add_patch(p)
    return p


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ms=9, style="-|>", **kw):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0,
                                mutation_scale=ms, **kw))


def blank(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def line(d, a, b, **kw):
    return d.add(elm.Line(**kw).at(a).to(b))


def dot(d, p):
    d.add(elm.Dot().at(p))


# ----------------------------------------------------------------------------
# Figure 5.1 — thyristor structure, two-transistor model, I-V characteristic
# ----------------------------------------------------------------------------
def fig_5_1():
    fig = plt.figure(figsize=(6.8, 3.9))
    # ---- PNPN stack ----
    a1 = fig.add_axes([0.0, 0.04, 0.2, 0.9])
    blank(a1, (-0.2, 3.0), (-0.6, 6.4))
    layers = [("P", 4.9, 0.8, C_PP), ("N1", 2.2, 2.7, C_NM), ("P2", 1.2, 1.0, C_P),
              ("N", 0.5, 0.7, C_NP)]
    x0, w = 0.5, 1.6
    for name, y, h, c in layers:
        rect(a1, x0, y, w, h, c)
    a1.text(x0 + w / 2, 5.3, "P", ha="center", va="center", fontsize=9)
    a1.text(x0 + w / 2, 3.55, "N1\nthick,\nlightly\ndoped", ha="center", va="center", fontsize=7.5)
    a1.text(x0 + w / 2 - 0.25, 1.7, "P2", ha="center", va="center", fontsize=9)
    a1.text(x0 + w / 2 - 0.25, 0.85, "N", ha="center", va="center", fontsize=9)
    # cathode N only under part of the P2 surface; gate contact on P2
    rect(a1, x0 + 1.15, 0.5, 0.45, 0.7, C_P)
    rect(a1, x0, 0.35, 1.0, 0.15, C_MET)
    rect(a1, x0 + 1.2, 1.05, 0.4, 0.15, C_MET)   # gate contact drawn on the P2 step
    rect(a1, x0, 5.7, w, 0.15, C_MET)
    a1.plot([x0 + 0.5, x0 + 0.5], [0.35, -0.05], color=INK, lw=1.0)
    a1.text(x0 + 0.5, -0.12, "K", ha="center", va="top", fontsize=10, weight="bold")
    a1.plot([x0 + 1.6, x0 + 2.05], [1.12, 1.12], color=INK, lw=1.0)
    a1.text(x0 + 2.12, 1.12, "G", ha="left", va="center", fontsize=10, weight="bold")
    a1.plot([x0 + w / 2] * 2, [5.85, 6.1], color=INK, lw=1.0)
    a1.text(x0 + w / 2, 6.15, "A", ha="center", va="bottom", fontsize=10, weight="bold")
    for y, j in ((4.9, "J1"), (2.2, "J2"), (1.2, "J3")):
        a1.plot([x0 - 0.15, x0], [y, y], color=ORANGE, lw=1.2)
        a1.text(x0 - 0.2, y, j, ha="right", va="center", fontsize=8, color=ORANGE)

    # ---- two-transistor model ----
    a2 = fig.add_axes([0.19, 0.04, 0.25, 0.9])
    a2.set_aspect("equal")
    a2.axis("off")
    d = schemdraw.Drawing(canvas=a2, show=False)
    d.config(fontsize=8.5, unit=2)
    q1 = d.add(elm.BjtPnp(circle=True).right().reverse().at((0, 0)).anchor("base"))
    d.add(elm.Label().at((q1.center[0] - 0.95, q1.center[1] + 0.15)).label("Q1 PNP\n(P, N1, P2)\n$\\alpha_1$", fontsize=7.8))
    q2 = d.add(elm.BjtNpn(circle=True).right().at((q1.base[0] - 0.9, q1.collector[1] - 1.6)).anchor("base"))
    d.add(elm.Label().at((q2.center[0] - 1.55, q2.emitter[1] - 0.7)).label("Q2 NPN\n(N1, P2, N)\n$\\alpha_2$", fontsize=7.8))
    # anode
    line(d, q1.emitter, (q1.emitter[0], q1.emitter[1] + 0.9))
    d.add(elm.Dot(open=True).at((q1.emitter[0], q1.emitter[1] + 0.9)).label("A", loc="top"))
    # cathode
    line(d, q2.emitter, (q2.emitter[0], q2.emitter[1] - 0.9))
    d.add(elm.Dot(open=True).at((q2.emitter[0], q2.emitter[1] - 0.9)).label("K", loc="bottom"))
    # Q1 collector -> Q2 base
    pc = (q1.collector[0], q2.base[1])
    line(d, q1.collector, pc)
    line(d, pc, q2.base)
    dot(d, pc)
    # Q2 collector -> Q1 base
    pb = (q2.collector[0], q1.base[1])
    line(d, q2.collector, pb)
    line(d, pb, q1.base)
    dot(d, pb)
    # gate into Q2 base node
    g = (pc[0] - 1.3, pc[1])
    line(d, pc, g)
    d.add(elm.Dot(open=True).at(g).label("G", loc="left"))
    d.add(elm.Arrow().at((g[0] + 0.15, g[1] + 0.25)).to((g[0] + 0.85, g[1] + 0.25)).color(ORANGE)
          .label("$I_G$", loc="top", color=ORANGE))
    d.draw(show=False)

    # ---- I-V characteristic (broken current axis) ----
    axt = fig.add_axes([0.53, 0.62, 0.45, 0.31])
    axb = fig.add_axes([0.53, 0.13, 0.45, 0.45], sharex=axt)
    # forward blocking branches
    def blocking(vbo, ileak_max):
        v = np.linspace(0, vbo, 300)
        return v, ileak_max * (v / vbo) ** 6 + 0.4 * v / vbo
    cols = (INK, BLUE, GREEN)
    for (vbo, ig), col in zip(((650, 0), (450, 5), (260, 10)), cols):
        v, i = blocking(vbo, 3.5)
        axb.plot(v, i, color=col)
        # negative-resistance region back to the on-state branch
        vv = np.linspace(vbo, 2.0, 50)
        ii = i[-1] + (25 - i[-1]) * ((vbo - vv) / (vbo - 2.0)) ** 1.5
        axb.plot(vv, ii, color=col, ls="--", lw=1.1)
        axb.plot(vbo, i[-1], "o", ms=3.5, color=col)
        if ig == 0:
            axb.text(698, 6.0, "$V_{BO}$ = 650 V\n($I_G$ = 0)", fontsize=7.0, color=col,
                     ha="right", va="bottom")
        else:
            axb.text(vbo, -2.0, f"$I_G$ = {ig}\nmA", fontsize=7.0, color=col, ha="center",
                     va="top")
    # reverse branch: leakage to VRRM = 600 V, avalanche beyond about 660 V
    vr = np.linspace(0, -660, 300)
    ir = -0.4 * (-vr / 600) - 0.6 * (-vr / 660) ** 12
    va = np.linspace(-660, -668, 30)
    ia = -1.0 - (np.abs(va) - 660) * 1.6
    axb.plot(np.r_[vr, va], np.r_[ir, ia], color=INK)
    axb.axvline(-600, color=GREY, ls=":", lw=0.9)
    axb.text(-600, 32, "$V_{RRM}$\n600 V", ha="center", fontsize=7.3, color="#555555")
    axb.text(-640, -11.5, "avalanche", ha="left", fontsize=7.3)
    axb.text(-320, 3, "reverse blocking", ha="center", fontsize=7.5)
    axb.text(450, 30, "forward blocking", ha="center", fontsize=7.5)
    # on-state branch: knee plus slope resistance (about 1.5 V at 10 A)
    i_on = np.linspace(0.02, 12, 400)
    v_on = 0.8 + 0.07 * np.log10(i_on / 0.02) + 0.05 * i_on
    for a in (axt, axb):
        a.plot(v_on, i_on * (1 if a is axt else 1e3), color=ORANGE, lw=2.0)
    v_h = np.interp([0.02, 0.04], i_on, v_on)
    axb.plot(v_h, [20, 40], "o", color=ORANGE, ms=4.5)
    axb.annotate("$I_L$ = 40 mA (latching)", xy=(v_h[1], 40), xytext=(-420, 46), fontsize=7.3,
                 color=ORANGE, va="center", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    axb.annotate("$I_H$ = 20 mA (holding)", xy=(v_h[0], 20), xytext=(-420, 22), fontsize=7.3,
                 color=ORANGE, va="center", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    axt.annotate("on state:\nabout 1.5 V at 10 A", xy=(1.5, 10), xytext=(60, 7.5), fontsize=7.3,
                 color=ORANGE, va="center", arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    for a in (axt, axb):
        a.axvline(0, color=GREY, lw=0.6)
        a.grid(True, lw=0.4)
    axb.axhline(0, color=GREY, lw=0.6)
    axt.set_ylim(0.06, 12)
    axt.set_ylabel("$i_A$ (A)")
    axb.set_ylim(-14, 55)
    axb.set_ylabel("$i_A$ (mA)")
    axb.set_xlim(-700, 700)
    axb.set_xlabel("anode-cathode voltage $v_{AK}$ (V)")
    plt.setp(axt.get_xticklabels(), visible=False)
    axt.spines["bottom"].set_visible(False)
    axt.tick_params(axis="x", length=0)
    # break marks
    for a, y in ((axt, 0), (axb, 1)):
        a.plot([-0.012, 0.012], [y - 0.03, y + 0.03], transform=a.transAxes, color=INK, lw=1,
               clip_on=False)
    axt.set_title("Static characteristic (scale break at 55 mA)", fontsize=9.5)
    save(fig, "05", "fig-5-1-thyristor-structure-iv")


# ----------------------------------------------------------------------------
# Figure 5.2 — DIAC-TRIAC dimmer
# ----------------------------------------------------------------------------
def fig_5_2():
    fig = plt.figure(figsize=(6.8, 5.4))
    ac = fig.add_axes([0.02, 0.6, 0.96, 0.39])
    ac.set_aspect("equal")
    ac.axis("off")
    d = schemdraw.Drawing(canvas=ac, show=False)
    d.config(fontsize=8.5, unit=2.2)
    src = d.add(elm.SourceSin().up().at((0, 0)))
    d.add(elm.Label().at((src.center[0] - 1.1, src.center[1])).label("230 V\n50 Hz"))
    d.add(elm.Line().up(0.4).at(src.end))
    d.add(elm.Line().right(0.6))
    lamp = d.add(elm.Lamp().right().label("lamp\n100 W", loc="top"))
    t_top = d.add(elm.Line().right(1.4))
    n_mt2 = t_top.end
    dot(d, n_mt2)
    # triac, vertical, MT2 at top
    tri = d.add(elm.Triac().down().at(n_mt2))
    d.add(elm.Label().at((tri.start[0] - 0.55, tri.start[1] - 0.45)).label("MT2", fontsize=7.5))
    d.add(elm.Label().at((tri.end[0] - 0.55, tri.end[1] + 0.45)).label("MT1", fontsize=7.5))
    ybot = tri.end[1] - 0.4
    line(d, tri.end, (tri.end[0], ybot))
    line(d, (src.start[0], ybot), (tri.end[0], ybot))
    line(d, src.start, (src.start[0], ybot))
    d.add(elm.Label().at((2.2, ybot + 0.3)).label("neutral", fontsize=7.5))
    # timing network: R (pot + fixed, 100 k) from MT2 down to node J, C 100 nF from J to MT1
    xr = n_mt2[0] + 2.6
    line(d, n_mt2, (xr, n_mt2[1]))
    dot(d, (xr, n_mt2[1]))
    rr = d.add(elm.Potentiometer().down().at((xr, n_mt2[1])).toy(tri.gate[1])
               .label("pot + fixed\n= 100 kΩ", loc="bottom", ofst=(0.25, 0)))
    nJ = rr.end
    dot(d, nJ)
    d.add(elm.Capacitor().down().at(nJ).toy(ybot).label("100 nF", loc="bottom"))
    dot(d, (xr, ybot))
    line(d, (tri.end[0], ybot), (xr, ybot))
    # DIAC from node J to the triac gate
    diac = d.add(elm.Diac().left().at(nJ).tox(tri.gate[0] + 0.3)
                 .label("DIAC DB3\n$V_{BO}$ = 32 V", loc="top"))
    line(d, diac.end, tri.gate)
    # RC snubber across the triac
    sx = xr + 3.3
    line(d, (xr, n_mt2[1]), (sx, n_mt2[1]))
    rs = d.add(elm.Resistor().down().at((sx, n_mt2[1])).length(1.7).label("100 Ω", loc="bottom"))
    cs = d.add(elm.Capacitor().down().at(rs.end).toy(ybot).label("47 nF", loc="bottom"))
    line(d, (xr, ybot), (sx, ybot))
    d.add(elm.Label().at((sx + 1.7, (n_mt2[1] + ybot) / 2)).label("RC\nsnubber", fontsize=8))
    d.draw(show=False)

    # ---- waveforms ----
    f, Vm = 50.0, 230 * math.sqrt(2)
    w = 2 * math.pi * f
    R, C, Vbo = 100e3, 100e-9, 32.0
    x = w * R * C
    Vc = Vm / math.sqrt(1 + x * x)
    lag = math.atan(x)
    alpha = lag + math.asin(Vbo / Vc)
    t = np.linspace(0, 20e-3, 4000)
    vs = Vm * np.sin(w * t)
    vc = Vc * np.sin(w * t - lag)
    th = (w * t) % math.pi
    vl = np.where(th >= alpha, vs, 0.0)
    tf1 = alpha / w
    tf2 = tf1 + 10e-3
    tm = t * 1e3

    g1 = fig.add_axes([0.1, 0.37, 0.86, 0.19])
    g2 = fig.add_axes([0.1, 0.195, 0.86, 0.145], sharex=g1)
    g3 = fig.add_axes([0.1, 0.07, 0.86, 0.1], sharex=g1)
    g1.plot(tm, vs, color=GREY, lw=1.2, ls="--", label="mains (325 V peak)")
    g1.fill_between(tm, 0, vl, color=AMBER, alpha=0.35, lw=0)
    g1.plot(tm, vl, color=ORANGE, lw=1.8, label="lamp voltage")
    g1.set_ylabel("V")
    g1.set_ylim(-370, 370)
    g1.legend(loc="upper right", fontsize=7.5, ncol=2, bbox_to_anchor=(1.0, 1.18))
    g1.text(tf1 * 1e3 + 0.25, -200, fr"fires at $\alpha$ = {math.degrees(alpha):.1f}°",
            fontsize=7.8, color=ORANGE)
    g2.plot(tm, vc, color=BLUE, label="capacitor voltage")
    for s in (1, -1):
        g2.axhline(s * Vbo, color=PINK, ls="--", lw=1.0)
    g2.text(19.9, 37, "+32 V", color=PINK, fontsize=7.3, ha="right", va="bottom")
    g2.text(19.9, -37, "−32 V", color=PINK, fontsize=7.3, ha="right", va="top")
    g2.text(0.3, 70, f"$v_C$: {Vc:.1f} V peak, lagging {math.degrees(lag):.0f}°", fontsize=7.8,
            color=BLUE)
    g2.set_ylim(-120, 120)
    g2.set_ylabel("$v_C$ (V)")
    # gate current pulses (DIAC breakback dumping C into the gate)
    ig = (np.exp(-((t - tf1) / 25e-6) ** 2) * (t >= tf1 - 1e-4)
          - np.exp(-((t - tf2) / 25e-6) ** 2))
    g3.plot(tm, ig, color=GREEN)
    g3.set_ylim(-1.4, 1.4)
    g3.set_yticks([])
    g3.set_ylabel("$i_G$", rotation=0, ha="right", va="center")
    g3.text(tf1 * 1e3 + 0.2, 0.6, f"{tf1 * 1e3:.2f} ms", fontsize=7.5, color=GREEN)
    g3.text(tf2 * 1e3 + 0.2, -1.0, f"{tf2 * 1e3:.2f} ms", fontsize=7.5, color=GREEN)
    g3.set_xlabel("time (ms)")
    g3.set_xlim(0, 20)
    for g in (g1, g2, g3):
        for tf in (tf1, tf2):
            g.axvline(tf * 1e3, color=GREY, lw=0.7, ls=":")
        g.axhline(0, color=GREY, lw=0.5)
    for g in (g1, g2):
        plt.setp(g.get_xticklabels(), visible=False)
    save(fig, "05", "fig-5-2-diac-triac-dimmer")


# ----------------------------------------------------------------------------
# Figure 5.3 — field-stop trench IGBT
# ----------------------------------------------------------------------------
def fig_5_3():
    fig = plt.figure(figsize=(6.8, 4.6))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    blank(ax, (-0.6, 5.0), (-0.5, 7.6))
    x0, W = 0.4, 3.2
    # layers (thickness not to scale)
    rect(ax, x0, 0.0, W, 0.22, C_MET)                  # collector metal
    rect(ax, x0, 0.22, W, 0.35, C_PP)                  # p+ collector
    rect(ax, x0, 0.57, W, 0.45, "#BFD8EE")             # n field stop
    rect(ax, x0, 1.02, W, 4.0, C_NM)                   # n- drift
    rect(ax, x0, 5.02, W, 0.75, C_P)                   # p body
    # plasma region
    ax.add_patch(FancyBboxPatch((x0 + 0.2, 1.3), W - 0.4, 3.0,
                                boxstyle="round,pad=0,rounding_size=0.4",
                                fc="#E9D8F0", ec="none", alpha=0.8))
    ax.text(x0 + W / 2, 2.8, "electron-hole\nplasma\n(conductivity\nmodulation)", ha="center",
            va="center", fontsize=7.3, color="#6A3D7A")
    # trench gate in the middle
    tx0, tx1 = x0 + W / 2 - 0.35, x0 + W / 2 + 0.35
    rect(ax, tx0, 4.55, tx1 - tx0, 1.22, C_OX)
    rect(ax, tx0 + 0.08, 4.63, tx1 - tx0 - 0.16, 1.14, C_POLY)
    ax.text(x0 + W / 2, 5.15, "gate", rotation=90, ha="center", va="center", fontsize=7)
    # n+ emitters next to trench
    rect(ax, tx0 - 0.5, 5.45, 0.5, 0.32, C_NP)
    rect(ax, tx1, 5.45, 0.5, 0.32, C_NP)
    # channel
    for xx in (tx0 - 0.05, tx1):
        rect(ax, xx, 5.02, 0.05, 0.43, "#1F3A5F", ec="none")
    # cap oxide + emitter metal
    rect(ax, tx0 - 0.08, 5.77, tx1 - tx0 + 0.16, 0.2, C_OX)
    pts = [(x0, 5.77), (tx0 - 0.08, 5.77), (tx0 - 0.08, 5.97), (tx1 + 0.08, 5.97),
           (tx1 + 0.08, 5.77), (x0 + W, 5.77), (x0 + W, 6.4), (x0, 6.4)]
    ax.add_patch(Polygon(pts, closed=True, fc=C_MET, ec=INK, lw=0.8))
    ax.text(x0 + W / 2, 6.2, "emitter metal (E)", ha="center", va="center", fontsize=7.3,
            color="white")
    ax.text(x0 + W / 2, 0.11, "collector metal (C)", ha="center", va="center", fontsize=7,
            color="white")
    # labels at right
    lx = x0 + W + 0.1
    for y, t in ((5.6, "n+ emitter"), (5.2, "p body"), (3.0, "n− drift\n≈120 µm\n(1200 V)"),
                 (0.8, "n field stop"), (0.4, "p+ collector")):
        ax.text(lx, y, t, ha="left", va="center", fontsize=7.3)
    ax.text(x0 + 0.35, 5.25, "p", ha="center", va="center", fontsize=7)
    ax.annotate("MOS channel", xy=(tx0 - 0.03, 5.2), xytext=(x0 - 0.5, 6.75), fontsize=7.3,
                color="#1F3A5F", arrowprops=dict(arrowstyle="-", color="#1F3A5F", lw=0.7))
    # carrier flows
    for xx in (tx0 - 0.2, tx1 + 0.2):
        arr(ax, xx, 5.05, xx, 3.2, color=BLUE, lw=1.4)
    ax.text(tx0 - 0.25, 4.6, "e⁻", color=BLUE, fontsize=9, ha="right")
    for xx in (x0 + 0.45, x0 + W - 0.45):
        arr(ax, xx, 0.6, xx, 2.4, color=ORANGE, lw=1.4)
    ax.text(x0 + 0.55, 0.95, "h⁺", color=ORANGE, fontsize=9, ha="left")
    # body resistance path (lateral hole current under the n+ emitter)
    ax.plot([x0 + 0.25, tx0 - 0.25], [5.3, 5.3], color=PINK, lw=1.0, ls="--")
    ax.text(x0 + 0.15, 4.9, "$R_{body}$", color=PINK, fontsize=7.5, ha="left")
    ax.text(x0 + W / 2, 7.3, "Field-stop trench IGBT cell (≈10 µm wide, not to scale)",
            ha="center", fontsize=8.5, weight="bold")

    # ---- equivalent circuit ----
    a2 = fig.add_axes([0.52, 0.02, 0.46, 0.94])
    a2.set_aspect("equal")
    a2.axis("off")
    d = schemdraw.Drawing(canvas=a2, show=False)
    d.config(fontsize=8.5, unit=2)
    q1 = d.add(elm.BjtPnp(circle=True).right().reverse().at((0, 0)).anchor("base"))
    d.add(elm.Label().at((q1.center[0] - 1.0, q1.center[1])).label("PNP", fontsize=8))
    ctop = (q1.emitter[0], q1.emitter[1] + 1.0)
    line(d, q1.emitter, ctop)
    d.add(elm.Dot(open=True).at(ctop).label("C (collector)", loc="top"))
    # base node N (n- drift) to the right
    nN = (q1.base[0] + 1.9, q1.base[1])
    line(d, q1.base, nN)
    dot(d, nN)
    # p-body node P below the PNP collector
    nP = (q1.collector[0], q1.collector[1] - 1.3)
    line(d, q1.collector, nP)
    dot(d, nP)
    # parasitic NPN: base at P, collector to N, emitter to E (dashed)
    q2 = d.add(elm.BjtNpn(circle=True).right().at((nP[0] + 1.0, nP[1])).anchor("base").linestyle("--")
               .color(PINK))
    line(d, nP, q2.base, ls="--", color=PINK)
    line(d, q2.collector, (q2.collector[0], nN[1]), ls="--", color=PINK)
    dot(d, (q2.collector[0], nN[1]))
    # MOSFET: drain to N, source to E bus, gate on the right
    mx = nN[0] + 1.6
    line(d, nN, (mx, nN[1]))
    m = d.add(elm.NFet().right().at((mx, nN[1])).anchor("drain"))
    # bus E
    yE = q2.emitter[1] - 1.9
    rb = d.add(elm.Resistor().down().at(nP).toy(yE + 0.0).linestyle("--").color(PINK)
               .label("$R_{body}$", loc="bottom", color=PINK))
    line(d, q2.emitter, (q2.emitter[0], yE), ls="--", color=PINK)
    line(d, m.source, (m.source[0], yE))
    line(d, (nP[0], yE), (m.source[0], yE))
    dot(d, (q2.emitter[0], yE))
    eE = ((nP[0] + m.source[0]) / 2, yE - 0.8)
    line(d, (eE[0], yE), eE)
    dot(d, (eE[0], yE))
    d.add(elm.Dot(open=True).at(eE).label("E (emitter)", loc="bottom"))
    line(d, m.gate, (m.gate[0] + 0.6, m.gate[1]))
    d.add(elm.Dot(open=True).at((m.gate[0] + 0.6, m.gate[1])).label("G", loc="right"))
    d.add(elm.Label().at((m.center[0] + 0.4, m.center[1] + 1.05)).label("n-ch\nMOSFET", fontsize=8))
    d.add(elm.Label().at((q2.center[0] + 0.95, q2.center[1] - 0.25))
          .label("parasitic\nNPN", fontsize=7.8, color=PINK))
    # latch-up loop annotation
    d.add(elm.Label().at((nP[0] - 1.6, nP[1] - 1.75))
          .label("latch-up path:\nPNP + parasitic NPN\n= parasitic thyristor", fontsize=7.3,
                 color=PINK))
    d.add(elm.Label().at((nN[0], nN[1] + 0.4)).label("n− drift", fontsize=7.3))
    d.add(elm.Label().at((nP[0] - 0.55, nP[1] + 0.3)).label("p body", fontsize=7.3))
    d.draw(show=False)
    save(fig, "05", "fig-5-3-igbt-structure")


# ----------------------------------------------------------------------------
# Figure 5.4 — IGBT vs SiC MOSFET conduction
# ----------------------------------------------------------------------------
def fig_5_4():
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    i = np.linspace(0, 300, 600)
    # IGBT 25 C: soft knee near 0.8 V, 1.75 V at 200 A
    a, Is, V0 = 0.05, 0.5, 0.6
    r25 = (1.75 - V0 - a * math.log(1 + 200 / Is)) / 200
    v_ig25 = V0 + a * np.log(1 + i / Is) + r25 * i
    v_ig25[0] = V0
    v_ig150 = 0.9 + 5.5e-3 * i
    v_sic25 = 8e-3 * i
    v_sic150 = 13.5e-3 * i
    ax.plot(np.r_[0, v_ig25], np.r_[0, i], color=BLUE, lw=1.6, ls="--", label="Si IGBT, 25 °C")
    ax.plot(np.r_[0, v_ig150], np.r_[0, i], color=BLUE, label="Si IGBT, 150 °C")
    ax.plot(v_sic25, i, color=ORANGE, lw=1.6, ls="--", label="SiC MOSFET, 25 °C (8 mΩ)")
    ax.plot(v_sic150, i, color=ORANGE, label="SiC MOSFET, 150 °C (13.5 mΩ)")
    ic = 0.9 / 8e-3
    vc = 13.5e-3 * ic
    ib = np.linspace(0, ic, 200)
    ax.fill_betweenx(ib, 13.5e-3 * ib, np.where(ib > 0, 0.9 + 5.5e-3 * ib, 0.9), color=GREEN,
                     alpha=0.15, lw=0)
    ax.annotate("MOSFET lower drop", xy=(0.95, 62), xytext=(0.05, 132),
                color="#1D6B4F", fontsize=8.5, ha="left",
                arrowprops=dict(arrowstyle="-|>", color="#1D6B4F", lw=0.8, mutation_scale=8))
    ax.plot(vc, ic, "o", color=INK, ms=6, zorder=5)
    ax.annotate(f"150 °C crossover\n{ic:.1f} A, {vc:.2f} V", xy=(vc, ic), xytext=(1.9, 70),
                fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.7))
    ax.axhline(200, color=GREY, lw=0.7, ls=":")
    ax.text(3.45, 203, "200 A rated", ha="right", va="bottom", fontsize=7.5, color="#555555")
    for v, lbl in ((1.75, "1.75"), (2.0, "2.0"), (1.6, "1.6"), (2.7, "2.7")):
        ax.plot(v, 200, "o", ms=3.5, color=INK)
    ax.text(1.57, 207, "1.6", fontsize=7, ha="right")
    ax.text(1.77, 194, "1.75", fontsize=7, ha="left", va="top")
    ax.text(2.03, 194, "2.0", fontsize=7, ha="left", va="top")
    ax.text(2.72, 186, "2.7 V", fontsize=7, ha="left", va="top")
    ax.set_xlim(0, 3.5)
    ax.set_ylim(0, 300)
    ax.set_xlabel("forward voltage $v_{CE}$ or $v_{DS}$ (V)")
    ax.set_ylabel("current (A)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, lw=0.5)
    save(fig, "05", "fig-5-4-igbt-vs-sic-output")


# ----------------------------------------------------------------------------
# Figure 5.5 — GaN HEMT structures
# ----------------------------------------------------------------------------
def hemt(ax, x0, pgan=False):
    W = 4.6
    layers = [(0.0, 0.65, "#D9D9D9", "Si(111) substrate"),
              (0.65, 0.25, "#C9C3E6", "AlN nucleation"),
              (0.9, 0.6, "#E3DFF3", ""),
              (1.5, 0.8, "#E8F4E8", ""),
              (2.3, 0.18, "#CDE9CD", "")]
    for y, h, c, t in layers:
        rect(ax, x0, y, W, h, c, lw=0.6)
        if t:
            ax.text(x0 + W / 2, y + h / 2, t, ha="center", va="center", fontsize=6.8)
    ax.text(x0 + W - 0.08, 1.2, "AlGaN/GaN strain-relief\nbuffer (C-doped)", ha="right",
            va="center", fontsize=6.5)
    ax.text(x0 + W + 0.05, 1.8, "GaN channel", ha="left", va="center", fontsize=6.5)
    ax.text(x0 + W + 0.05, 2.39, "AlGaN barrier\n15–20 nm", ha="left", va="center", fontsize=6.5)
    y2 = 2.25
    xs, xg, xd = x0 + 0.25, x0 + 1.25, x0 + W - 0.75
    # 2DEG
    if pgan:
        ax.plot([x0 + 0.05, xg - 0.02], [y2, y2], color=BLUE, lw=1.6, ls=(0, (4, 2)))
        ax.plot([xg + 0.62, x0 + W - 0.05], [y2, y2], color=BLUE, lw=1.6, ls=(0, (4, 2)))
    else:
        ax.plot([x0 + 0.05, x0 + W - 0.05], [y2, y2], color=BLUE, lw=1.6, ls=(0, (4, 2)))
    ax.text(x0 + W - 0.08, y2 - 0.07, "2DEG", color=BLUE, fontsize=7, ha="right", va="top")
    # contacts
    ytop = 2.48
    rect(ax, xs, ytop, 0.5, 0.35, C_MET)
    rect(ax, xd, ytop, 0.5, 0.35, C_MET)
    ax.text(xs + 0.25, ytop + 0.5, "S", ha="center", fontsize=9, weight="bold")
    ax.text(xd + 0.25, ytop + 0.5, "D", ha="center", fontsize=9, weight="bold")
    if pgan:
        rect(ax, xg, ytop, 0.6, 0.18, "#F2B8A0", lw=0.6)
        rect(ax, xg + 0.05, ytop + 0.18, 0.5, 0.25, C_MET)
        ax.text(xg + 0.3, ytop + 0.55, "G", ha="center", fontsize=9, weight="bold")
        ax.annotate("p-GaN", xy=(xg + 0.6, ytop + 0.09), xytext=(xg + 0.95, ytop + 0.62),
                    fontsize=6.6, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6))
        ax.text(xg + 0.3, y2 - 0.07, "2DEG depleted", fontsize=6.3, ha="center", va="top",
                color=BLUE)
        ax.text(x0 + W - 0.05, 3.8, "$V_{th}$ = +1.5 V (normally off)", ha="right",
                fontsize=7.5, color=GREEN)
    else:
        rect(ax, xg, ytop, 0.5, 0.35, C_MET)
        ax.text(xg + 0.25, ytop + 0.5, "G", ha="center", fontsize=9, weight="bold")
        ax.annotate("Schottky gate", xy=(xg + 0.5, ytop + 0.25), xytext=(xg + 0.95, ytop + 0.62),
                    fontsize=6.6, ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6))
        ax.text(x0 + W - 0.05, 3.8, "$V_{th}$ < 0 (normally on)", ha="right", fontsize=7.5,
                color=ORANGE)
    # field plate from source over the gate toward the drain
    gx1 = xg + (0.6 if pgan else 0.5)
    ax.plot([xs + 0.5, xs + 0.5, gx1 + 1.25, gx1 + 1.25],
            [ytop + 0.35, ytop + 1.0, ytop + 1.0, ytop + 0.8], color=INK, lw=1.2)
    ax.text(gx1 + 1.35, ytop + 0.95, "source field plate", fontsize=6.5, ha="left", va="center")
    # gate-drain spacing
    arr(ax, gx1, ytop + 0.12, xd, ytop + 0.12, style="<|-|>", lw=0.7, ms=5)
    ax.text((gx1 + xd) / 2, ytop + 0.17, "$L_{GD}$ ≈ 15 µm", fontsize=6.5, ha="center",
            va="bottom")
    # reverse conduction through the channel (drain pulled below source)
    arr(ax, x0 + 3.9, 2.0, xs + 0.3, 2.0, color=PINK, lw=1.0, ms=7)
    ax.text(x0 + 0.12, 1.72, "reverse conduction via channel;\nno body diode, $Q_{rr}$ = 0",
            fontsize=6.3, color=PINK, ha="left", va="center")


def fig_5_5():
    fig = plt.figure(figsize=(6.8, 5.0))
    a = fig.add_axes([0.0, 0.5, 0.56, 0.5])
    blank(a, (-0.1, 5.9), (-0.2, 4.45))
    hemt(a, 0.0)
    a.text(2.3, 4.2, "(a) depletion-mode HEMT", ha="center", fontsize=8.5, weight="bold")
    b = fig.add_axes([0.0, 0.0, 0.56, 0.5])
    blank(b, (-0.1, 5.9), (-0.2, 4.45))
    hemt(b, 0.0, pgan=True)
    b.text(2.3, 4.2, "(b) p-GaN gate HEMT (enhancement mode)", ha="center", fontsize=8.5,
           weight="bold")
    c = fig.add_axes([0.6, 0.1, 0.39, 0.8])
    c.set_aspect("equal")
    c.axis("off")
    d = schemdraw.Drawing(canvas=c, show=False)
    d.config(fontsize=8.5, unit=2)
    g = d.add(elm.AnalogNFet().right().at((0, 4)).anchor("drain"))
    d.add(elm.Label().at((-1.45, 3.3)).label("GaN HEMT\n650 V,\nnormally on", fontsize=8))
    dtop = (g.drain[0], g.drain[1] + 0.8)
    line(d, g.drain, dtop)
    d.add(elm.Dot(open=True).at(dtop).label("D", loc="top"))
    mid = (g.source[0], g.source[1] - 0.7)
    line(d, g.source, mid)
    dot(d, mid)
    m = d.add(elm.NFet().right().reverse().at(mid).anchor("drain"))
    d.add(elm.Label().at((-1.5, m.source[1] - 0.25)).label("Si MOSFET\n30 V", fontsize=8))
    sbot = (m.source[0], m.source[1] - 1.0)
    line(d, m.source, sbot)
    nS = (m.source[0], m.source[1] - 0.5)
    dot(d, nS)
    d.add(elm.Dot(open=True).at(sbot).label("S", loc="bottom"))
    # HEMT gate tied to the MOSFET source (= package source S)
    gx = g.gate[0] + 0.8
    line(d, g.gate, (gx, g.gate[1]))
    line(d, (gx, g.gate[1]), (gx, nS[1]))
    line(d, (gx, nS[1]), nS)
    d.add(elm.Label().at((gx + 0.15, (g.gate[1] + nS[1]) / 2)).label("HEMT gate\ntied to S",
                                                                     fontsize=7.5, halign="left"))
    # external gate of the MOSFET
    line(d, m.gate, (m.gate[0] - 0.8, m.gate[1]))
    d.add(elm.Dot(open=True).at((m.gate[0] - 0.8, m.gate[1])).label("G", loc="left"))
    d.add(elm.Label().at((-1.6, mid[1] + 0.05)).label("±20 V gate,\n$V_{th}$ ≈ 4 V", fontsize=7.3))
    d.draw(show=False)
    c.set_xlim(-3.4, 3.6)
    c.set_ylim(-1.6, 5.4)
    c.set_title("(c) cascode", fontsize=8.5, weight="bold")
    save(fig, "05", "fig-5-5-gan-hemt-structures")


# ----------------------------------------------------------------------------
# Figure 5.6 — technology map
# ----------------------------------------------------------------------------
def fig_5_6():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.set_xscale("log")
    ax.set_yscale("log")
    regions = [
        ("SCR (line commutated)", [(50, 100), (60, 100), (60, 8500), (50, 8500)], "#7F7F7F"),
        ("IGCT / GTO", [(200, 2500), (1e3, 2500), (1e3, 6500), (200, 6500)], PINK),
        ("Si IGBT", [(1e3, 600), (30e3, 600), (30e3, 3300), (3e3, 3300), (3e3, 6500),
                     (1e3, 6500)], BLUE),
        ("SiC MOSFET", [(10e3, 650), (500e3, 650), (500e3, 3300), (10e3, 3300)], ORANGE),
        ("Si superjunction", [(20e3, 500), (300e3, 500), (300e3, 900), (20e3, 900)], AMBER),
        ("Si MOSFET", [(10e3, 20), (5e6, 20), (5e6, 250), (10e3, 250)], GREEN),
        ("GaN HEMT", [(100e3, 40), (10e6, 40), (10e6, 650), (100e3, 650)], SKY),
    ]
    for name, pts, col in regions:
        from matplotlib.colors import to_rgba
        ax.add_patch(Polygon(pts, closed=True, fc=to_rgba(col, 0.16), ec=to_rgba(col, 0.75),
                             lw=1.2))
    lbl = {"SCR (line commutated)": (75, 300, "left"), "IGCT / GTO": (215, 4200, "left"),
           "Si IGBT": (1.1e3, 1500, "left"), "SiC MOSFET": (110e3, 2500, "left"),
           "Si superjunction": (21e3, 435, "left"), "Si MOSFET": (11e3, 28, "left"),
           "GaN HEMT": (9e6, 400, "right")}
    for name, pts, col in regions:
        x, y, ha = lbl[name]
        ax.text(x, y, name, color=col if col != AMBER else "#9A6B00", fontsize=8.5,
                weight="bold", ha=ha, va="center")
    apps = [("phone charger GaN 65 W", 300e3, 650, (1.3e6, 1200)),
            ("server PSU totem-pole PFC", 65e3, 650, (2.6e3, 780)),
            ("EV traction inverter SiC", math.sqrt(10e3 * 20e3), 1200, (50e3, 1500)),
            ("industrial drive IGBT", 4e3, 1200, (2.2e3, 2000)),
            ("HVDC thyristor valve", 50, 8500, (85, 8500))]
    for name, f, v, (tx, ty) in apps:
        ax.plot(f, v, "o", ms=6.5, mfc="white", mec=INK, mew=1.5, zorder=6)
        ax.annotate(name, xy=(f, v), xytext=(tx, ty), fontsize=7.5, va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.6, color=INK), zorder=7)
    ax.plot([10e3, 20e3], [1200, 1200], color=INK, lw=2.2, zorder=5)
    ax.annotate("", xy=(58, 300), xytext=(74, 300),
                arrowprops=dict(arrowstyle="-", color="#7F7F7F", lw=0.8))
    ax.set_xlim(50 * 0.85, 10e6 * 1.1)
    ax.set_ylim(10, 10e3)
    ax.set_xlabel("switching frequency (Hz)")
    ax.set_ylabel("device blocking voltage (V)")
    ax.grid(True, which="major", lw=0.5)
    ax.set_xticks([1e2, 1e3, 1e4, 1e5, 1e6, 1e7])
    ax.set_xticklabels(["100 Hz", "1 kHz", "10 kHz", "100 kHz", "1 MHz", "10 MHz"])
    ax.set_yticks([10, 100, 1e3, 1e4])
    ax.set_yticklabels(["10 V", "100 V", "1 kV", "10 kV"])
    save(fig, "05", "fig-5-6-device-technology-map")


if __name__ == "__main__":
    fig_5_1()
    fig_5_2()
    fig_5_3()
    fig_5_4()
    fig_5_5()
    fig_5_6()
