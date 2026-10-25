"""Figures for Chapter 7 — Transistor Amplifiers.

Run from the repository root:  python figures/scripts/ch07.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
GREY = "#777777"

# ----------------------------------------------------------------------------
# Worked example 7.1 parameters (2N3904, divider bias)
# ----------------------------------------------------------------------------
VT, BETA, VA, IC = 0.02585, 150, 100.0, 1.152e-3
GM, RPI, RO = IC / VT, BETA * VT / IC, VA / IC
RX, CMU, FT = 50.0, 2.5e-12, 200e6
CPI = GM / (2 * np.pi * FT) - CMU
RS, RB, RC, RL, CL = 600.0, 8.246e3, 4.7e3, 10e3, 10e-12
RE = 1.2e3


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def drawing(ax, fontsize=9, lw=1.1):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=fontsize, lw=lw, unit=2.0)
    return d


def finish(ax, d, pad=0.3):
    d.draw(show=False)
    ax.set_position([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale_view()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_ylim(y0 - pad, y1 + pad)


def wire(d, pts, **kw):
    for p, q in zip(pts[:-1], pts[1:]):
        d.add(elm.Line(**kw).at(p).to(q))


def dot(d, p, open_=False):
    d.add(elm.Dot(open=open_).at(p))


def gnd(d, p):
    d.add(elm.Ground().at(p))


def node_tag(ax, p, n, dx=0.0, dy=0.45):
    ax.text(p[0] + dx, p[1] + dy, str(n), ha="center", va="center", fontsize=8.5, color=BLUE,
            bbox=dict(boxstyle="circle,pad=0.18", fc="white", ec=BLUE, lw=0.9), zorder=5)


def nodal(n, elements, vccs, inj):
    """Solve Y v = i.  elements: (a, b, y); vccs: (from, to, cp, cn, g); inj: {node: current}."""
    Y = np.zeros((n, n), complex)
    for a, b, y in elements:
        if a:
            Y[a - 1, a - 1] += y
        if b:
            Y[b - 1, b - 1] += y
        if a and b:
            Y[a - 1, b - 1] -= y
            Y[b - 1, a - 1] -= y
    for fr, to, cp, cn, g in vccs:
        for node, sgn in ((fr, 1), (to, -1)):
            if not node:
                continue
            if cp:
                Y[node - 1, cp - 1] += sgn * g
            if cn:
                Y[node - 1, cn - 1] -= sgn * g
    i = np.zeros(n, complex)
    for k, v in inj.items():
        i[k - 1] = v
    return np.linalg.solve(Y, i)


def ce_gain(f, C1=10e-6, CE=470e-6, C2=4.7e-6, Rs=RS, cascode=False):
    """|vo/vs| of the full CE stage (1 V source) including coupling, bypass and device capacitances.

    Nodes: 1 source side of C1, 2 base pin, 3 internal base b', 4 emitter, 5 collector of Q1,
    6 output (RL), 7 collector of the cascode device Q2 (cascode only).
    """
    s = 2j * np.pi * f
    el = [(1, 0, 1 / Rs), (1, 2, s * C1), (2, 0, 1 / RB), (2, 3, 1 / RX),
          (3, 4, 1 / RPI + s * CPI), (3, 5, s * CMU), (4, 0, 1 / RE + s * CE),
          (5, 4, 1 / RO), (6, 0, 1 / RL)]
    vc = [(5, 4, 3, 4, GM)]
    if not cascode:
        el += [(5, 0, 1 / RC + s * CL), (5, 6, s * C2)]
        n, out = 6, 6
    else:
        # Q2 common base (base at AC ground), same bias current
        el += [(5, 0, 1 / RPI + s * CPI), (7, 0, s * CMU + 1 / RC + s * CL), (7, 5, 1 / RO),
               (7, 6, s * C2)]
        vc += [(7, 5, 0, 5, GM)]
        n, out = 7, 6
    return abs(nodal(n, el, vc, {1: 1 / Rs})[out - 1])


def corners(f, A):
    mid = A.max()
    above = A >= mid / np.sqrt(2)
    idx = np.flatnonzero(above)
    return f[idx[0]], f[idx[-1]], mid


# ----------------------------------------------------------------------------
def fig_7_1():
    """Hybrid-pi small-signal equivalent of the CE stage (Listing 7.1)."""
    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    d = drawing(ax, fontsize=8.5)
    top, bot = 3.0, 0.0
    fs = 8.5

    def vlabel(x, text, side="right"):
        ax.text(x + (0.42 if side == "right" else -0.75), 1.5, text,
                ha="left" if side == "right" else "right", va="center", fontsize=fs)

    # source
    d.add(elm.SourceSin().at((0, bot)).up(top))
    vlabel(0, r"$v_s$" + "\n1 V", "left")
    n1, n2, xcp, n3 = (3.4, top), (6.8, top), (9.4, top), (12.6, top)
    d.add(elm.Resistor().at((0, top)).to(n1).label(r"$R_s$ 600 Ω", loc="top", ofst=0.1))
    dot(d, n1)
    d.add(elm.Resistor().at(n1).down(top))
    vlabel(n1[0], r"$R_B$" + "\n8.25 kΩ")
    d.add(elm.Resistor().at(n1).to(n2).label(r"$r_x$ 50 Ω", loc="top", ofst=0.1))
    dot(d, n2)
    d.add(elm.Resistor().at(n2).down(top))
    vlabel(n2[0], r"$r_\pi$" + "\n3.37 kΩ")
    wire(d, [n2, xcp])
    dot(d, xcp)
    d.add(elm.Capacitor().at(xcp).down(top))
    vlabel(xcp[0], r"$C_\pi$" + "\n33.0 pF")
    # v_pi marking (left of r_pi)
    xv = n2[0] - 0.55
    ax.text(xv, 2.45, "+", ha="center", va="center", fontsize=11, color=ORANGE)
    ax.text(xv, 0.5, "−", ha="center", va="center", fontsize=11, color=ORANGE)
    ax.text(xv, 1.5, r"$v_\pi$", ha="center", va="center", fontsize=10, color=ORANGE)
    # C_mu bridge
    yb = 4.4
    wire(d, [xcp, (xcp[0], yb)])
    d.add(elm.Capacitor().at((xcp[0], yb)).to((n3[0], yb)).label(r"$C_\mu$ 2.5 pF", loc="top", ofst=0.1))
    wire(d, [(n3[0], yb), n3])
    dot(d, n3)
    # collector-side elements
    xs = [n3[0], 15.9, 18.7, 21.5, 24.3]
    wire(d, [n3, (xs[-1], top)])
    for x in xs[1:-1]:
        dot(d, (x, top))
    d.add(elm.SourceControlledI().at(n3).down(top))
    vlabel(xs[0] + 0.2, r"$g_m v_\pi$" + "\n44.6 mS")
    labels = [r"$r_o$" + "\n86.8 kΩ", r"$R_C$" + "\n4.7 kΩ", r"$R_L$" + "\n10 kΩ"]
    for x, lab in zip(xs[1:4], labels):
        d.add(elm.Resistor().at((x, top)).down(top))
        vlabel(x, lab)
    d.add(elm.Capacitor().at((xs[4], top)).down(top))
    vlabel(xs[4], r"$C_L$" + "\n10 pF")
    # ground rail
    wire(d, [(0, bot), (xs[-1], bot)])
    for x in (n1[0], n2[0], xcp[0], n3[0], 15.9, 18.7, 21.5):
        dot(d, (x, bot))
    gnd(d, (11.0, bot))
    ax.text(11.0, -0.95, "E (emitter, AC ground via bypass)", ha="center", va="top", fontsize=8, color=GREY)
    dot(d, (xs[-1], top), open_=True)
    ax.text(xs[-1] + 0.2, top + 0.25, r"$v_o$", ha="left", va="bottom", fontsize=10)
    node_tag(ax, n1, 1, dy=0.55)
    node_tag(ax, n2, 2, dy=0.55)
    node_tag(ax, n3, 3, dx=0.5, dy=0.55)
    ax.text(n1[0], top + 1.15, "B", ha="center", va="center", fontsize=8, color=GREY)
    ax.text(n2[0], top + 1.15, "B′", ha="center", va="center", fontsize=8, color=GREY)
    ax.text(n3[0] + 0.5, top + 1.15, "C", ha="center", va="center", fontsize=8, color=GREY)
    finish(ax, d)
    save(fig, "07", "fig-7-1-ce-hybrid-pi")


def _ce_stage(d, ax, fs=8.5, show_vce=True):
    """Draw the divider-biased CE stage of Worked example 7.1; returns key points."""
    vcc, yb = 9.0, 4.6
    xin, bx = 0.0, 4.6
    q = d.add(elm.BjtNpn(circle=True).at((bx + 1.6, yb)).anchor("base"))
    b, c, e = q.base, q.collector, q.emitter
    wire(d, [(bx, vcc), (c[0], vcc)])
    # divider
    d.add(elm.Resistor().at((bx, vcc)).to((bx, yb)))
    ax.text(bx - 0.4, (vcc + yb) / 2, r"$R_1$" + "\n47 kΩ", ha="right", va="center", fontsize=fs)
    d.add(elm.Resistor().at((bx, yb)).to((bx, 0)))
    ax.text(bx - 0.4, yb / 2, r"$R_2$" + "\n10 kΩ", ha="right", va="center", fontsize=fs)
    wire(d, [(bx, yb), b])
    dot(d, (bx, yb))
    # collector resistor
    cy = c[1] + 0.9
    d.add(elm.Resistor().at((c[0], vcc)).to((c[0], cy)))
    ax.text(c[0] + 0.4, (vcc + cy) / 2, r"$R_C$" + "\n4.7 kΩ", ha="left", va="center", fontsize=fs)
    wire(d, [(c[0], cy), c])
    dot(d, (c[0], cy))
    # emitter network
    ey = e[1] - 0.6
    wire(d, [e, (e[0], ey)])
    dot(d, (e[0], ey))
    xc = e[0] + 1.5
    wire(d, [(e[0], ey), (xc, ey)])
    d.add(elm.Resistor().at((e[0], ey)).to((e[0], 0)))
    ax.text(e[0] - 0.4, ey / 2 - 0.2, r"$R_E$" + "\n1.2 kΩ", ha="right", va="center", fontsize=fs)
    d.add(elm.Capacitor(polar=True).at((xc, ey)).to((xc, 0)))
    ax.text(xc + 0.5, ey / 2, r"$C_E$" + "\n470 µF", ha="left", va="center", fontsize=fs)
    ax.text(q.center[0] + 0.6, q.center[1] + 0.05, r"$Q_1$" + "\n2N3904", ha="left",
            va="center", fontsize=fs - 0.5)
    # input
    d.add(elm.SourceSin().at((xin, 0)).to((xin, yb)))
    ax.text(xin - 0.6, yb / 2, r"$v_s$", ha="right", va="center", fontsize=fs + 1)
    d.add(elm.Resistor().at((xin, yb)).to((2.6, yb)))
    ax.text(1.3, yb + 0.45, r"$R_s$ 600 Ω", ha="center", va="bottom", fontsize=fs)
    d.add(elm.Capacitor(polar=True).at((2.6, yb)).to((bx, yb)))
    ax.text(3.6, yb + 0.45, r"$C_1$ 10 µF", ha="center", va="bottom", fontsize=fs)
    # DC annotations common to both figures
    dc = dict(fontsize=8, color=BLUE)
    ax.text(bx - 0.15, yb - 0.35, r"$V_B=2.04$ V", ha="right", va="top", **dc)
    ax.text(e[0] - 0.15, ey + 0.1, r"$V_E=1.39$ V", ha="right", va="bottom", **dc)
    ax.annotate("", xy=(c[0] - 0.35, vcc - 1.9), xytext=(c[0] - 0.35, vcc - 0.6),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=9))
    ax.text(c[0] - 0.45, vcc - 1.25, r"$I_C$" + "\n1.15 mA", ha="right", va="center", **dc)
    if show_vce:
        ax.text(q.center[0] + 0.6, q.center[1] - 0.85, r"$V_{CE}=5.19$ V", ha="left", va="center", **dc)
    return dict(q=q, vcc=vcc, b=b, c=c, e=e, cy=cy, bx=bx, xc=xc, ey=ey, xin=xin, dc=dc)


def fig_7_2():
    """Discrete CE amplifier with divider bias and emitter bypass."""
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    d = drawing(ax, fontsize=8.5)
    fs = 8.5
    P = _ce_stage(d, ax)
    vcc, c, cy, dc = P["vcc"], P["c"], P["cy"], P["dc"]
    xo = c[0] + 3.8
    d.add(elm.Capacitor(polar=True).at((c[0], cy)).to((xo, cy)))
    ax.text((c[0] + xo) / 2, cy + 0.45, r"$C_2$ 4.7 µF", ha="center", va="bottom", fontsize=fs)
    d.add(elm.Resistor().at((xo, cy)).to((xo, 0)))
    ax.text(xo + 0.4, cy / 2, r"$R_L$" + "\n10 kΩ", ha="left", va="center", fontsize=fs)
    dot(d, (xo, cy))
    ax.text(xo + 0.15, cy + 0.2, r"$v_o$", ha="left", va="bottom", fontsize=fs + 1)
    wire(d, [(P["xin"], 0), (xo, 0)])
    gnd(d, (P["bx"], 0))
    for x in (P["bx"], P["e"][0], P["xc"]):
        dot(d, (x, 0))
    ax.text((P["bx"] + c[0]) / 2, vcc + 0.2, r"$V_{CC}=12$ V", ha="center", va="bottom",
            fontsize=fs + 0.5)
    ax.text(c[0] + 0.15, cy - 0.15, r"$V_C=6.58$ V", ha="left", va="top", **dc)
    # degenerated variant (dashed inset)
    x0, y0 = xo + 2.6, 0.6
    g = dict(ls="--", color=GREY)
    ax.add_patch(Rectangle((x0 - 0.7, y0 - 0.6), 4.4, 5.6, fill=False, ls="--", ec=GREY, lw=0.9))
    ax.text(x0 + 1.5, y0 + 5.2, "degenerated variant\n(replaces " + r"$R_E\parallel C_E$" + ")",
            ha="center", va="bottom", fontsize=7.5, color=GREY)
    e_top = (x0, y0 + 4.5)
    ax.text(e_top[0], e_top[1] + 0.05, "E", ha="center", va="bottom", fontsize=8, color=GREY)
    mid = (x0, y0 + 2.4)
    d.add(elm.Resistor(**g).at(e_top).to(mid))
    ax.text(x0 + 0.4, y0 + 3.45, r"$R_{E1}$ 100 Ω" + "\n(unbypassed)", ha="left", va="center",
            fontsize=7.5, color=GREY)
    xcap = x0 + 2.0
    wire(d, [mid, (xcap, mid[1])], **g)
    d.add(elm.Resistor(**g).at(mid).to((x0, y0)))
    d.add(elm.Capacitor(polar=True, **g).at((xcap, mid[1])).to((xcap, y0)))
    wire(d, [(x0, y0), (xcap, y0)], **g)
    ax.text(x0 + 0.4, y0 + 1.2, "1.1 kΩ", ha="left", va="center", fontsize=7.5, color=GREY)
    ax.text(xcap + 0.35, y0 + 1.2, "470 µF", ha="left", va="center", fontsize=7.5, color=GREY)
    gnd(d, (x0 + 1.0, y0))
    finish(ax, d)
    save(fig, "07", "fig-7-2-ce-amplifier")


def fig_7_3():
    """CE stage direct-coupled to an emitter follower driving 1 kOhm."""
    fig, ax = plt.subplots(figsize=(6.8, 4.9))
    d = drawing(ax, fontsize=8.5)
    fs = 8.5
    P = _ce_stage(d, ax, show_vce=False)
    vcc, c, cy, dc = P["vcc"], P["c"], P["cy"], P["dc"]
    q2 = d.add(elm.BjtNpn(circle=True).at((c[0] + 2.8, cy)).anchor("base"))
    wire(d, [(c[0], cy), q2.base])
    wire(d, [(c[0], vcc), (q2.collector[0], vcc), q2.collector])
    dot(d, (c[0], vcc))
    ax.text(q2.center[0] + 0.6, q2.center[1] + 0.1, r"$Q_2$" + "\n2N3904", ha="left", va="center",
            fontsize=fs - 0.5)
    e2 = q2.emitter
    ey2 = e2[1] - 0.6
    wire(d, [e2, (e2[0], ey2)])
    dot(d, (e2[0], ey2))
    d.add(elm.Resistor().at((e2[0], ey2)).to((e2[0], 0)))
    ax.text(e2[0] + 0.4, ey2 / 2, r"$R_{E2}$" + "\n1.2 kΩ", ha="left", va="center", fontsize=fs)
    xo = e2[0] + 3.4
    d.add(elm.Capacitor(polar=True).at((e2[0], ey2)).to((xo, ey2)))
    ax.text((e2[0] + xo) / 2 + 0.2, ey2 + 0.45, "47 µF", ha="center", va="bottom", fontsize=fs)
    d.add(elm.Resistor().at((xo, ey2)).to((xo, 0)))
    ax.text(xo + 0.4, ey2 / 2, r"$R_L$" + "\n1 kΩ", ha="left", va="center", fontsize=fs)
    dot(d, (xo, ey2))
    ax.text(xo + 0.15, ey2 + 0.2, r"$v_o$", ha="left", va="bottom", fontsize=fs + 1)
    wire(d, [(P["xin"], 0), (xo, 0)])
    gnd(d, (P["bx"], 0))
    for x in (P["bx"], P["e"][0], P["xc"], e2[0]):
        dot(d, (x, 0))
    ax.text((P["bx"] + q2.collector[0]) / 2, vcc + 0.2, r"$V_{CC}=12$ V", ha="center", va="bottom",
            fontsize=fs + 0.5)
    ax.text(c[0] + 0.15, cy - 0.15, r"$V_{C1}=V_{B2}$" + "\n= 6.43 V", ha="left", va="top", **dc)
    ax.text(e2[0] - 0.15, ey2 + 0.1, r"$V_{E2}=5.78$ V", ha="right", va="bottom", **dc)
    ax.annotate("", xy=(e2[0] - 0.35, ey2 - 1.6), xytext=(e2[0] - 0.35, ey2 - 0.3),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=9))
    ax.text(e2[0] - 0.45, ey2 - 0.95, r"$I_{E2}$" + "\n4.82 mA", ha="right", va="center", **dc)
    # alternative: RL directly at the Q1 collector
    bx0, by0, bw, bh = e2[0] + 1.0, vcc - 2.25, 3.6, 1.75
    ax.add_patch(Rectangle((bx0, by0), bw, bh, fill=False, ls="--", ec=ORANGE, lw=1.0))
    ax.text(bx0 + bw / 2, by0 + bh / 2, "alternative: " + r"$R_L$" + " = 1 kΩ\nwired directly to the\n"
            + r"$Q_1$" + " collector: " + r"$A_v=-36$", ha="center", va="center", fontsize=7.4,
            color=ORANGE)
    ax.annotate("", xy=(c[0] + 0.08, cy + 0.08), xytext=(bx0, by0 + 0.35),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.9, ls="--", mutation_scale=8,
                                connectionstyle="arc3,rad=0.15"))
    # small-signal summary
    txt = (r"$R_{in2}=83$ kΩ     $A_{v1}=-189$     $A_{v2}=0.990$" + "\n" +
           r"$A_v=A_{v1}A_{v2}=-187$ (45.4 dB)     $R_{out}=34\ \Omega$")
    ax.text((P["xin"] + xo) / 2, -1.0, txt, ha="center", va="top", fontsize=8.5, color=GREEN,
            bbox=dict(boxstyle="round,pad=0.35", fc="#F2F8F5", ec=GREEN, lw=0.8))
    finish(ax, d)
    save(fig, "07", "fig-7-3-ce-cc-cascade")



def fig_7_4():
    """Magnitude response of the CE stage, 1 Hz to 100 MHz."""
    f = np.logspace(0, 8, 4001)
    A = np.array([ce_gain(x) for x in f])
    A100 = np.array([ce_gain(x, CE=100e-6) for x in f])
    Acas = np.array([ce_gain(x, cascode=True) for x in f])
    fl, fh, mid = corners(f, A)
    fl100, _, _ = corners(f, A100)
    _, fhc, midc = corners(f, Acas)
    print(f"  midband {20*np.log10(mid):.2f} dB, fL = {fl:.1f} Hz, fH = {fh/1e3:.0f} kHz")
    print(f"  CE=100uF: fL = {fl100:.1f} Hz; cascode fH = {fhc/1e6:.2f} MHz, mid {20*np.log10(midc):.2f} dB")
    for cex in (350e-6, 470e-6, 508e-6):
        a = np.array([ce_gain(x, CE=cex) for x in f[:2000]])
        print(f"  CE={cex*1e6:.0f}uF exact fL = {f[np.flatnonzero(a >= mid/np.sqrt(2))[0]]:.1f} Hz")
    a50 = np.array([ce_gain(x, Rs=50.0) for x in f])
    print(f"  Rs=50: fH = {corners(f, a50)[1]/1e6:.2f} MHz")

    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    dB = lambda x: 20 * np.log10(x)  # noqa: E731
    ax.semilogx(f, dB(A), color=BLUE, label=r"$C_E=470$ µF (design)")
    ax.semilogx(f, dB(A100), color=ORANGE, ls="--", label=r"$C_E=100$ µF")
    ax.semilogx(f, dB(Acas), color=GREEN, ls=":", lw=2.2, label="cascode")
    ax.axhline(dB(mid) - 3, color=GRID, lw=0.9, zorder=0)
    ax.text(1.3, dB(mid) - 3.4, "−3 dB", fontsize=7.5, color=GREY, va="top")
    # pole markers
    for fp, lab in ((2.3, r"$C_2$"), (5.3, r"$C_1$"), (13.3, r"$C_E$")):
        ax.plot([fp, fp], [0, 1.6], color=INK, lw=1.2)
        ax.text(fp, 1.9, lab, ha="center", va="bottom", fontsize=7.5, zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.3))
    ax.text(30, 1.0, "individual poles: " + r"$C_2$" + " 2.3 Hz, " + r"$C_1$" + " 5.3 Hz, "
            + r"$C_E$" + " 13.3 Hz", fontsize=7.5, va="bottom", ha="left")
    for fx in (680e3, 814e3):
        ax.axvline(fx, color=PINK, lw=0.9, ls="-.", ymax=12 / 45)
    ax.text(600e3, 6.0, "OCTC\n680 kHz", fontsize=7.2, color=PINK, ha="right", va="bottom")
    ax.text(930e3, 6.0, "Miller\n814 kHz", fontsize=7.2, color=PINK, ha="left", va="bottom")
    # corner annotations
    ax.plot([fl, fh], [dB(mid) - 3] * 2, "o", color=BLUE, ms=4)
    ax.annotate(f"$f_L$ = {fl:.0f} Hz\n(SCTC sum 21 Hz)", xy=(fl, dB(mid) - 3), xytext=(40, 27),
                fontsize=7.8, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate(f"$f_H$ = {fh/1e3:.0f} kHz", xy=(fh, dB(mid) - 3), xytext=(5e3, 30),
                fontsize=7.8, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate(f"{fl100:.0f} Hz\n(SCTC sum 70 Hz)", xy=(fl100, dB(mid) - 3), xytext=(250, 31.5),
                fontsize=7.8, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.annotate(f"{fhc/1e6:.1f} MHz\n(OCTC est. 2.7 MHz)", xy=(fhc, dB(mid) - 3), xytext=(6e6, 40.5),
                fontsize=7.8, color=GREEN, arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ax.text(3e3, dB(mid) + 0.6, f"midband {dB(mid):.1f} dB", fontsize=7.8, ha="center", va="bottom")
    ax.set_xlim(1, 1e8)
    ax.set_ylim(0, 45)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel(r"$|v_o/v_s|$ (dB)")
    ax.grid(True, which="major", lw=0.5)
    ax.legend(loc="center", fontsize=7.8, ncol=1, bbox_to_anchor=(0.5, 0.3))
    save(fig, "07", "fig-7-4-ce-frequency-response")


def _large_signal(v_in_pk, RE1, N=4096):
    RLp = 3.084e3
    t = np.arange(N) / N
    v_in = v_in_pk * np.sin(2 * np.pi * t)
    x = np.zeros(N)
    for _ in range(60):
        ic = IC * np.exp(x / VT)
        fx = x + (ic - IC) * RE1 - v_in
        x -= fx / (1 + ic * RE1 / VT)
    vo = -(IC * np.exp(x / VT) - IC) * RLp
    H = np.abs(np.fft.rfft(vo)) / (N / 2)
    return t, vo, H


def fig_7_5():
    """Output waveform and harmonic spectrum, bypassed and degenerated."""
    t, vb, Hb = _large_signal(7.3e-3, 0.0)
    _, vd, Hd = _large_signal(38.5e-3, 100.0)
    hb = 20 * np.log10(Hb[2:6] / Hb[1])
    hd = 20 * np.log10(Hd[2:6] / Hd[1])
    print(f"  bypassed peaks {vb.min():.3f} / {vb.max():.3f} V; HD2..5 = {np.round(hb, 1)}")
    print(f"  degenerated peaks {vd.min():.3f} / {vd.max():.3f} V; HD2..5 = {np.round(hd, 1)}")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.2), gridspec_kw=dict(width_ratios=[1.35, 1]))
    tm = t * 1.0  # ms at 1 kHz
    a1.plot(tm, -np.sin(2 * np.pi * t), color=GREY, ls="--", lw=1.1, label="ideal sine (1 V)")
    a1.plot(tm, vb, color=ORANGE, label=r"bypassed, $v_{in}$ = 7.3 mV")
    a1.plot(tm, vd, color=BLUE, label=r"$R_{E1}$ = 100 Ω, $v_{in}$ = 38.5 mV")
    a1.axhline(0, color=GRID, lw=0.8, zorder=0)
    a1.annotate(f"{vb.min():.2f} V", xy=(0.25, vb.min()), xytext=(0.36, -1.12), fontsize=7.8,
                color=ORANGE, va="center")
    a1.text(0.75, vb.max() - 0.1, f"+{vb.max():.2f} V", fontsize=7.8, color=ORANGE, va="top",
            ha="center")
    a1.set_xlim(0, 1)
    a1.set_ylim(-1.2, 1.2)
    a1.set_xlabel("time (ms)")
    a1.set_ylabel(r"$v_o$ (V)")
    a1.legend(fontsize=7, loc="upper left", handlelength=1.6, borderaxespad=0.1)
    n = np.arange(2, 6)
    w = 0.36
    floor = -120
    a2.bar(n - w / 2, hb - floor, w, bottom=floor, color=ORANGE, label="bypassed")
    a2.bar(n + w / 2, hd - floor, w, bottom=floor, color=BLUE, label=r"$R_{E1}$ = 100 Ω")
    for k in range(4):
        fmt = "{:.1f}" if k < 2 else "{:.0f}"
        a2.text(n[k] - w / 2, hb[k] + 1.5, fmt.format(hb[k]), ha="center", va="bottom", fontsize=6.6,
                color=ORANGE)
        a2.text(n[k] + w / 2, hd[k] + 1.5, fmt.format(hd[k]), ha="center", va="bottom", fontsize=6.6,
                color=BLUE)
    a2.set_ylim(floor, 0)
    a2.set_xticks(n)
    a2.set_xticklabels(["HD2", "HD3", "HD4", "HD5"])
    a2.set_ylabel("level re fundamental (dB)")
    a2.legend(fontsize=7.5, loc="upper right")
    fig.tight_layout(w_pad=1.5)
    save(fig, "07", "fig-7-5-ce-distortion")


if __name__ == "__main__":
    print(f"Cpi = {CPI*1e12:.1f} pF, gm = {GM*1e3:.1f} mS, rpi = {RPI:.0f}, ro = {RO:.0f}")
    fig_7_1()
    fig_7_2()
    fig_7_3()
    fig_7_4()
    fig_7_5()
