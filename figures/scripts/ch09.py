"""Figures for Chapter 9 — Feedback and Oscillators.

Run from the repository root:  python figures/scripts/ch09.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
from scipy import signal  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402
import schemdraw.logic as logic  # noqa: E402

from figstyle import COLORS, INK, GRID, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
GREY = "#777777"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def drawing(ax, fontsize=8, lw=1.1, unit=2.0):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=fontsize, lw=lw, unit=unit)
    return d


def finish(ax, d, pad=0.3, full=False):
    d.draw(show=False)
    if full:
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


def seg(el, p, q):
    """Place a two-terminal element from p to q by angle and length (robust for sources)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    return el.at(p).theta(np.degrees(np.arctan2(dy, dx))).length(float(np.hypot(dx, dy)))


def dot(d, p, open_=False):
    d.add(elm.Dot(open=open_).at(p))


def gnd(d, p):
    d.add(elm.Ground().at(p))


def txt(ax, x, y, s, ha="center", va="center", fs=8, color=INK, **kw):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, **kw)


def rbox(ax, x, y, w, h, text, fs=8, fc="#EEF3F8", ec=INK, color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.0, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, zorder=3)


def opamp(d, center, flip=False):
    el = elm.Opamp(leads=False).right().at(center).anchor("center")
    if flip:
        el = el.flip()
    return d.add(el)


# ----------------------------------------------------------------------------
def _block(ax, d, series_mix, shunt_sense):
    """Generic feedback block diagram on a ground rail (y = 0)."""
    fs = 7.5
    yt = 2.6
    xa = 3.3                       # left edge of the A and beta boxes
    if series_mix:
        d.add(seg(elm.SourceSin(), (0, 0), (0, yt)))
        txt(ax, -0.55, yt / 2, r"$v_s$", ha="right", fs=fs)
    else:
        d.add(seg(elm.SourceI(), (0, 0), (0, yt)))
        txt(ax, -0.55, yt / 2, r"$i_s$", ha="right", fs=fs)
    fb = r"$\beta v_o$" if shunt_sense else r"$\beta i_o$"
    if series_mix:
        wire(d, [(0, yt), (0.6, yt)])
        d.add(seg(elm.SourceControlledV(color=GREEN), (0.6, yt), (2.4, yt)))
        txt(ax, 1.5, yt + 0.55, fb, va="bottom", fs=fs, color=GREEN)
        wire(d, [(2.4, yt), (xa, yt)])
        tgt = (1.5, yt - 0.5)
    else:
        wire(d, [(0, yt), (xa, yt)])
        dot(d, (1.6, yt))
        d.add(seg(elm.SourceControlledI(color=GREEN), (1.6, yt), (1.6, 0)))
        txt(ax, 2.1, 2.05, fb, ha="left", fs=fs, color=GREEN)
        tgt = (2.1, 1.05)
    rbox(ax, xa, yt - 0.6, 1.6, 1.2, r"$A$", fs=9)
    xo = 7.6
    xs = 6.2
    wire(d, [(xa + 1.6, yt), (xo, yt)])
    if shunt_sense:
        dot(d, (xs, yt))
        wire(d, [(xs, yt), (xs, 1.05), (xa + 1.6, 1.05)])
        d.add(seg(elm.Resistor(), (xo, yt), (xo, 0)))
        txt(ax, xo + 0.35, yt / 2, r"$R_L$", ha="left", fs=fs)
        dot(d, (xo, yt))
        txt(ax, xo, yt + 0.25, r"$v_o$", va="bottom", fs=fs)
    else:
        d.add(seg(elm.Resistor(), (xo, yt), (xo, 1.3)))
        txt(ax, xo + 0.35, 1.95, r"$R_L$", ha="left", fs=fs)
        d.add(seg(elm.MeterA(), (xo, 1.3), (xo, 0)))
        ax.annotate("", xy=(7.0, yt), xytext=(5.9, yt),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=8))
        txt(ax, 6.45, yt + 0.2, r"$i_o$", va="bottom", fs=fs, color=BLUE)
        ax.plot([xo - 0.5, xs, xs, xa + 1.6], [0.65, 0.65, 1.05, 1.05], color=INK, lw=1.0, ls="--")
    rbox(ax, xa, 0.5, 1.6, 1.1, r"$\beta$", fs=9)
    cs = "angle,angleA=180,angleB=90" if series_mix else "arc3,rad=0"
    ax.annotate("", xy=tgt, xytext=(xa, 1.05),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.0, ls="--", mutation_scale=8,
                                connectionstyle=cs))
    wire(d, [(0, 0), (xo, 0)])


def _out_terminal(ax, d, p, label=r"$v_o$"):
    dot(d, p, open_=True)
    txt(ax, p[0] + 0.15, p[1], label, ha="left", fs=7.5)


def _real_a(ax, d, x0):
    """Non-inverting stage (+ input on top)."""
    op = opamp(d, (x0 + 3.0, 2.6), flip=True)
    dot(d, (x0 + 0.5, op.in2[1]), open_=True)
    wire(d, [(x0 + 0.5, op.in2[1]), op.in2])
    txt(ax, x0 + 0.3, op.in2[1], r"$v_i$", ha="right", fs=7.5)
    xn = op.in1[0] - 0.6
    yb = op.in1[1] - 0.9
    wire(d, [op.in1, (xn, op.in1[1]), (xn, yb)])
    d.add(seg(elm.Resistor(), (xn, yb), (xn, -1.4)))
    gnd(d, (xn, -1.4))
    txt(ax, xn - 0.35, (yb - 1.4) / 2, r"$R_1$", ha="right", fs=7.5)
    xo = op.out[0] + 0.4
    dot(d, (xn, yb))
    d.add(seg(elm.Resistor(), (xn, yb), (xo, yb)))
    txt(ax, (xn + xo) / 2, yb - 0.4, r"$R_f$", va="top", fs=7.5)
    wire(d, [(xo, yb), (xo, op.out[1]), op.out])
    dot(d, (xo, op.out[1]))
    wire(d, [(xo, op.out[1]), (xo + 0.6, op.out[1])])
    _out_terminal(ax, d, (xo + 0.6, op.out[1]))


def _real_b(ax, d, x0):
    """Transimpedance amplifier with a photodiode."""
    op = opamp(d, (x0 + 3.2, 1.8))
    xn = op.in1[0] - 0.6
    wire(d, [op.in1, (xn, op.in1[1]), (xn, op.in1[1] + 1.4)])
    xo = op.out[0] + 0.4
    d.add(seg(elm.Resistor(), (xn, op.in1[1] + 1.4), (xo, op.in1[1] + 1.4)))
    txt(ax, (xn + xo) / 2, op.in1[1] + 1.8, r"$R_f$", va="bottom", fs=7.5)
    wire(d, [(xo, op.in1[1] + 1.4), (xo, op.out[1]), op.out])
    dot(d, (xo, op.out[1]))
    wire(d, [(xo, op.out[1]), (xo + 0.6, op.out[1])])
    _out_terminal(ax, d, (xo + 0.6, op.out[1]))
    dot(d, (xn, op.in1[1]))
    xp = xn - 1.3
    wire(d, [(xn, op.in1[1]), (xp, op.in1[1])])
    d.add(seg(elm.Photodiode(), (xp, -0.8), (xp, op.in1[1])))
    gnd(d, (xp, -0.8))
    wire(d, [op.in2, (op.in2[0] - 0.3, op.in2[1]), (op.in2[0] - 0.3, -0.8)])
    gnd(d, (op.in2[0] - 0.3, -0.8))


def _real_c(ax, d, x0):
    """Op-amp V-to-I converter driving a MOSFET (4-20 mA transmitter)."""
    op = opamp(d, (x0 + 2.4, 1.6), flip=True)
    dot(d, (x0 + 0.2, op.in2[1]), open_=True)
    wire(d, [(x0 + 0.2, op.in2[1]), op.in2])
    txt(ax, x0 + 0.0, op.in2[1], r"$v_i$", ha="right", fs=7.5)
    q = d.add(elm.NFet().right().reverse().at((op.out[0] + 0.6, op.out[1])).anchor("gate"))
    wire(d, [op.out, q.gate])
    s, dr = q.source, q.drain
    if s[1] > dr[1]:
        s, dr = dr, s
    ys = s[1] - 0.5
    wire(d, [s, (s[0], ys)])
    dot(d, (s[0], ys))
    d.add(seg(elm.Resistor(), (s[0], ys), (s[0], -1.2)))
    gnd(d, (s[0], -1.2))
    txt(ax, s[0] + 0.35, (ys - 1.2) / 2, r"$R_s$" + "\n100 Ω", ha="left", fs=7)
    xn = op.in1[0] - 0.5
    wire(d, [op.in1, (xn, op.in1[1]), (xn, ys), (s[0], ys)])
    ytop = dr[1] + 2.0
    d.add(seg(elm.Resistor(), (dr[0], ytop), dr))
    txt(ax, dr[0] + 0.35, (dr[1] + ytop) / 2, "load", ha="left", fs=7)
    dot(d, (dr[0], ytop), open_=True)
    txt(ax, dr[0], ytop + 0.2, "+24 V loop" + chr(10) + "(0.4–2 V → 4–20 mA)", va="bottom", fs=7)
    ax.annotate("", xy=(dr[0] - 0.4, dr[1] + 0.3), xytext=(dr[0] - 0.4, dr[1] + 1.5),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=8))
    txt(ax, dr[0] - 0.5, dr[1] + 0.9, r"$i_o$", ha="right", fs=7.5, color=BLUE)


def _real_d(ax, d, x0):
    """Two-transistor current amplifier, feedback from Q2 emitter to Q1 base."""
    q1 = d.add(elm.BjtNpn(circle=True).right().at((x0 + 1.8, 1.4)).anchor("base"))
    q2 = d.add(elm.BjtNpn(circle=True).right().at((x0 + 4.4, 3.2)).anchor("base"))
    vcc = 5.6
    yg = -1.7
    xb = x0 + 0.9
    # input current source into the Q1 base node
    xsrc = x0 - 0.3
    d.add(seg(elm.SourceI(), (xsrc, yg), (xsrc, q1.base[1])))
    gnd(d, (xsrc, yg))
    txt(ax, xsrc - 0.55, (q1.base[1] + yg) / 2, r"$i_s$", ha="right", fs=7.5)
    wire(d, [(xsrc, q1.base[1]), q1.base])
    dot(d, (xb, q1.base[1]))
    # Q1 emitter to ground, collector to RC1 and Q2 base
    wire(d, [q1.emitter, (q1.emitter[0], 0.3)])
    gnd(d, (q1.emitter[0], 0.3))
    wire(d, [q1.collector, (q1.collector[0], q2.base[1]), q2.base])
    d.add(seg(elm.Resistor(), (q1.collector[0], vcc), (q1.collector[0], q2.base[1])))
    dot(d, (q1.collector[0], q2.base[1]))
    txt(ax, q1.collector[0] - 0.35, (vcc + q2.base[1]) / 2, r"$R_{C1}$", ha="right", fs=7)
    # Q2 collector load and output current
    d.add(seg(elm.Resistor(), (q2.collector[0], vcc), q2.collector))
    txt(ax, q2.collector[0] + 0.35, (vcc + q2.collector[1]) / 2 + 0.1, "load", ha="left", fs=7)
    ax.annotate("", xy=(q2.collector[0] - 0.3, q2.collector[1] + 0.05),
                xytext=(q2.collector[0] - 0.3, q2.collector[1] + 0.75),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=8))
    txt(ax, q2.collector[0] - 0.4, q2.collector[1] + 0.4, r"$i_o$", ha="right", fs=7.5, color=BLUE)
    wire(d, [(q1.collector[0], vcc), (q2.collector[0], vcc)])
    txt(ax, (q1.collector[0] + q2.collector[0]) / 2, vcc + 0.15, r"$V_{CC}$", va="bottom", fs=7)
    # Q2 emitter: RE2 to ground, RF back to the Q1 base
    e2 = q2.emitter
    ye = e2[1] - 0.5
    wire(d, [e2, (e2[0], ye)])
    dot(d, (e2[0], ye))
    d.add(seg(elm.Resistor(), (e2[0], ye), (e2[0], yg)))
    gnd(d, (e2[0], yg))
    txt(ax, e2[0] + 0.35, (ye + yg) / 2, r"$R_{E2}$", ha="left", fs=7)
    yf = -1.0
    xr = e2[0] - 0.8
    wire(d, [(e2[0], ye), (xr, ye), (xr, yf)], color=GREEN)
    d.add(seg(elm.Resistor(color=GREEN), (xr, yf), (xb + 0.4, yf)))
    wire(d, [(xb + 0.4, yf), (xb, yf), (xb, q1.base[1])], color=GREEN)
    txt(ax, (xr + xb) / 2 + 0.2, yf - 0.4, r"$R_F$", va="top", fs=7, color=GREEN)
    txt(ax, q1.center[0] + 0.55, q1.center[1] + 0.45, r"$Q_1$", ha="left", fs=7)
    txt(ax, q2.center[0] + 0.55, q2.center[1] + 0.45, r"$Q_2$", ha="left", fs=7)


def fig_9_1():
    """The four feedback topologies: block diagram and realisation."""
    fig = plt.figure(figsize=(6.8, 5.0))
    specs = [
        ("(a) Series–shunt: voltage sensing, voltage mixing", True, True, _real_a,
         r"$R_{in}\times(1+T)$,   $R_{out}\div(1+T)$,   gain V/V", "non-inverting stage"),
        ("(b) Shunt–shunt: voltage sensing, current mixing", False, True, _real_b,
         r"$R_{in}\div(1+T)$,   $R_{out}\div(1+T)$,   gain V/A", "transimpedance amplifier"),
        ("(c) Series–series: current sensing, voltage mixing", True, False, _real_c,
         r"$R_{in}\times(1+T)$,   $R_{out}\times(1+T)$,   gain A/V", "4–20 mA transmitter"),
        ("(d) Shunt–series: current sensing, current mixing", False, False, _real_d,
         r"$R_{in}\div(1+T)$,   $R_{out}\times(1+T)$,   gain A/A", "two-transistor current amplifier"),
    ]
    for k, (title, smix, ssense, real, props, rname) in enumerate(specs):
        r, c = divmod(k, 2)
        ax = fig.add_axes([0.005 + c * 0.5, 0.555 - r * 0.5, 0.49, 0.37])
        d = drawing(ax, fontsize=7.5, unit=1.6)
        _block(ax, d, smix, ssense)
        real(ax, d, 10.2)
        finish(ax, d)
        ax.set_xlim(-1.4, 19.2)
        ax.set_ylim(-3.1, 6.6)
        fig.text(0.02 + c * 0.5, 0.955 - r * 0.5, title, ha="left", va="center", fontsize=8.2,
                 weight="bold")
        fig.text(0.25 + c * 0.5, 0.54 - r * 0.5, props, ha="center", va="center", fontsize=8,
                 color=BLUE)
        txt(ax, 3.8, -1.2, "block diagram", fs=7, color=GREY)
        txt(ax, 14.2, -2.85, rname, fs=7, color=GREY)
    fig.add_artist(plt.Line2D([0.5, 0.5], [0.04, 0.97], color=GRID, lw=0.8))
    fig.add_artist(plt.Line2D([0.02, 0.98], [0.51, 0.51], color=GRID, lw=0.8))
    save(fig, "09", "fig-9-1-feedback-topologies")


# ----------------------------------------------------------------------------
A0, GBW, FP2, RO = 1e5, 10e6, 60e6, 50.0
WP1, WP2 = 2 * np.pi * GBW / A0, 2 * np.pi * FP2


def _loop(f, CL=None, Riso=0.0):
    s = 2j * np.pi * f
    A = A0 / ((1 + s / WP1) * (1 + s / WP2))
    if CL is None:
        return A
    return A * (1 + s * Riso * CL) / (1 + s * (RO + Riso) * CL)


def _crossing(f, L):
    i = np.argmax(np.abs(L) < 1)
    return f[i], 180 + np.degrees(np.angle(L[i]))


def fig_9_2():
    """Loop gain of a follower with capacitive load and isolation resistor."""
    f = np.logspace(4, 8, 4001)
    cases = [("unloaded", _loop(f), BLUE, "-"),
             ("1 nF cable", _loop(f, 1e-9), ORANGE, "--"),
             (r"1 nF, $R_{iso}$ = 47 Ω", _loop(f, 1e-9, 47.0), GREEN, "-.")]
    fig = plt.figure(figsize=(6.4, 5.0))
    a1 = fig.add_axes([0.11, 0.55, 0.85, 0.40])
    a2 = fig.add_axes([0.11, 0.09, 0.85, 0.40], sharex=a1)
    ff = np.logspace(3, 9, 400001)
    for lab, L, col, ls in cases:
        a1.semilogx(f, 20 * np.log10(np.abs(L)), color=col, ls=ls, label=lab)
        a2.semilogx(f, np.degrees(np.unwrap(np.angle(L))), color=col, ls=ls)
    full = [_loop(ff), _loop(ff, 1e-9), _loop(ff, 1e-9, 47.0)]
    offs = [(1.25, 10), (0.3, -16), (2.4, -30)]
    for (lab, _, col, _), Lf, off in zip(cases, full, offs):
        fc, pm = _crossing(ff, Lf)
        print(f"  {lab}: crossover {fc/1e6:.2f} MHz, PM {pm:.1f} deg")
        a1.plot(fc, 0, "o", color=col, ms=4)
        a1.annotate(f"{fc/1e6:.1f} MHz", xy=(fc, 0), xytext=(fc * off[0], off[1]), fontsize=7.5, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.7))
        ph = -180 + pm
        a2.plot([fc, fc], [-180, ph], color=col, lw=2.2)
        if pm > 75:
            a2.text(fc * 1.06, ph + 3, f"PM {pm:.1f}°", color=col, fontsize=7.5, ha="left", va="bottom")
        else:
            a2.text(fc / 1.08, (ph - 180) / 2 + (6 if pm > 50 else -8), f"PM {pm:.1f}°", color=col,
                    fontsize=7.5, ha="right", va="center")
    a1.axhline(0, color=INK, lw=0.7)
    for fx, lab, col in ((3.18e6, "pole 3.18 MHz", ORANGE), (1.64e6, "pole 1.64 MHz", GREEN),
                         (3.39e6, "zero 3.39 MHz", GREEN)):
        a1.axvline(fx, color=col, lw=0.6, ls=":")
    txt(a1, 1.55e6, 45, "pole\n1.64 MHz", ha="right", fs=7, color=GREEN)
    txt(a1, 3.6e6, 45, "pole 3.18 MHz (1 nF)\nzero 3.39 MHz (" + r"$R_{iso}$" + ")", ha="left", fs=7, color=GREY)
    a1.set_ylim(-40, 60)
    a1.set_ylabel("loop gain (dB)")
    a1.legend(loc="lower left", fontsize=7.8)
    a1.grid(True, which="major", lw=0.5)
    plt.setp(a1.get_xticklabels(), visible=False)
    a2.axhline(-180, color=INK, lw=0.8)
    a2.set_ylim(-225, -90)
    a2.set_yticks([-90, -135, -180, -225])
    a2.set_ylabel("loop phase (deg)")
    a2.set_xlabel("frequency (Hz)")
    a2.set_xlim(1e4, 1e8)
    a2.grid(True, which="major", lw=0.5)
    # inset: closed-loop step responses at the load
    ai = fig.add_axes([0.16, 0.155, 0.30, 0.16])
    t = np.linspace(0, 2e-6, 4001)
    den_a = np.polymul([1 / WP1, 1], [1 / WP2, 1])
    den1 = np.polymul(den_a, [RO * 1e-9, 1])
    y1 = signal.step(signal.TransferFunction([A0], np.polyadd(den1, [A0])), T=t)[1]
    Ri = 47.0
    numL = np.polymul([A0], [Ri * 1e-9, 1])
    denL = np.polymul(den_a, [(RO + Ri) * 1e-9, 1])
    y2 = signal.step(signal.TransferFunction(numL, np.polymul(np.polyadd(denL, numL), [Ri * 1e-9, 1])), T=t)[1]
    print(f"  step overshoot 1 nF {100*(y1.max()/y1[-1]-1):.1f} %, Riso {100*(y2.max()/y2[-1]-1):.1f} %")
    ai.plot(t * 1e6, y1, color=ORANGE, lw=1.2)
    ai.plot(t * 1e6, y2, color=GREEN, lw=1.2, ls="-.")
    ai.set_xlim(0, 2)
    ai.set_ylim(0, 1.6)
    ai.tick_params(labelsize=6.5)
    ai.set_xlabel("time (µs)", fontsize=7, labelpad=1)
    ai.set_title("closed-loop step at load", fontsize=7, pad=2)
    ai.text(0.3, 1.5, f"{100*(y1.max()/y1[-1]-1):.0f} % overshoot", fontsize=6.8, color=ORANGE, va="top")
    ai.text(1.0, 0.65, r"$R_{iso}$: " + f"{100*(y2.max()/y2[-1]-1):.1f} %", fontsize=6.8, color=GREEN)
    ai.set_facecolor("white")
    save(fig, "09", "fig-9-2-capacitive-load-loop-gain")


# ----------------------------------------------------------------------------
def _wien_sim(t_end, R1=10e3, Ra=15e3, Rb=10e3, R=15.8e3, C=10e-9):
    Is, nVT = 2.7e-9, 1.9 * 0.02585
    vb = np.linspace(-1.2, 1.2, 24001)
    i = vb / Rb + 2 * Is * np.sinh(vb / nVT)
    vp_tab = i * R1
    vo_tab = vp_tab + i * Ra + vb
    ok = np.abs(vp_tab) < 6

    def v_out(vp):
        return np.interp(vp, vp_tab[ok], vo_tab[ok])

    def rhs(t, x):
        vcs, vp = x
        ii = (v_out(vp) - vcs - vp) / R
        return [ii / C, (ii - vp / R) / C]

    T = 2 * np.pi * R * C
    sol = solve_ivp(rhs, [0, t_end], [0.0, 1e-3], max_step=T / 300, rtol=1e-8, atol=1e-10,
                    dense_output=True)
    return sol, v_out, T


def fig_9_3():
    """Wien-bridge oscillator with diode stabilisation and its simulated output."""
    sol, v_out, T = _wien_sim(150 * 2 * np.pi * 15.8e3 * 10e-9)
    t = np.linspace(0, 30e-3, 30001)
    vo = v_out(sol.sol(t)[1])
    # steady-state spectrum (100-150 periods)
    tt = np.linspace(100 * T, 150 * T, 60000)
    vv = v_out(sol.sol(tt)[1])
    up = np.flatnonzero((vv[:-1] < 0) & (vv[1:] >= 0))
    tz = tt[up] - vv[up] * (tt[up + 1] - tt[up]) / (vv[up + 1] - vv[up])
    f_osc = (len(tz) - 1) / (tz[-1] - tz[0])
    n = 4096
    ts = tz[0] + np.arange(n) * 40 / f_osc / n
    spec = np.abs(np.fft.rfft(v_out(sol.sol(ts)[1]))) * 2 / n
    thd = np.sqrt(np.sum(spec[80:440:40] ** 2)) / spec[40]
    h = 20 * np.log10(spec[40:440:40] / spec[40] + 1e-12)
    env = np.abs(vo)
    i90 = np.argmax(env > 0.9 * spec[40])
    print(f"  f = {f_osc:.1f} Hz, {spec[40]:.2f} V pk, THD {100*thd:.2f} %, HD3 {h[2]:.1f} dB; "
          f"90 % amplitude at {t[i90]*1e3:.1f} ms")

    fig = plt.figure(figsize=(6.8, 3.4))
    axc = fig.add_axes([0.0, 0.02, 0.42, 0.96])
    axp = fig.add_axes([0.52, 0.15, 0.44, 0.50])
    d = drawing(axc, fontsize=7.5)
    op = opamp(d, (5.2, 0.0), flip=True)          # + input on top
    xo = op.out[0] + 0.5
    wire(d, [op.out, (xo, op.out[1])])
    dot(d, (xo, 0))
    # Wien network: series R-C from output to +, parallel R || C from + to ground
    xp = op.in2[0] - 0.6
    yW = op.in2[1] + 2.2
    wire(d, [op.in2, (xp, op.in2[1]), (xp, yW)])
    wire(d, [(xo, 0), (xo, yW)])
    d.add(seg(elm.Resistor(), (xo, yW), (xo - 2.4, yW)))
    d.add(seg(elm.Capacitor(), (xo - 2.4, yW), (xp, yW)))
    txt(axc, xo - 1.2, yW + 0.4, "R 15.8 kΩ", va="bottom", fs=7)
    txt(axc, (xo - 2.4 + xp) / 2, yW + 0.4, "C 10 nF", va="bottom", fs=7)
    xq = xp - 1.0
    wire(d, [(xp, op.in2[1]), (xq - 0.9, op.in2[1])])
    dot(d, (xp, op.in2[1]))
    dot(d, (xq, op.in2[1]))
    yg = op.in2[1] - 2.4
    d.add(seg(elm.Resistor(), (xq, op.in2[1]), (xq, yg)))
    d.add(seg(elm.Capacitor(), (xq - 0.9, op.in2[1]), (xq - 0.9, yg)))
    wire(d, [(xq - 0.9, yg), (xq, yg)])
    gnd(d, (xq - 0.45, yg))
    txt(axc, xq + 0.3, op.in2[1] - 1.2, "R", ha="left", fs=7)
    txt(axc, xq - 1.2, op.in2[1] - 1.2, "C", ha="right", fs=7)
    txt(axc, xq - 0.45, yg - 1.0, "R = 15.8 kΩ\nC = 10 nF", va="top", fs=7)
    # gain network: R1 from - to ground, Ra + (Rb || diodes) from output to -
    xn = op.in1[0] - 0.4
    yF = op.in1[1] - 1.5
    yg2 = yF - 2.4
    wire(d, [op.in1, (xn, op.in1[1]), (xn, yF)])
    d.add(seg(elm.Resistor(), (xn, yF), (xn, yg2)))
    gnd(d, (xn, yg2))
    txt(axc, xn + 0.35, (yF + yg2) / 2, r"$R_1$" + "\n10 kΩ", ha="left", fs=7)
    wire(d, [(xn, yF), (xn + 0.3, yF)])
    dot(d, (xn, yF))
    xe = xo + 0.9
    xm = xe - 2.4
    d.add(seg(elm.Resistor(), (xn + 0.3, yF), (xm, yF)))
    txt(axc, (xn + 0.3 + xm) / 2, yF + 0.35, r"$R_a$ 15 kΩ", va="bottom", fs=7)
    d.add(seg(elm.Resistor(), (xm, yF), (xe, yF)))
    wire(d, [(xe, yF), (xe, 0)])
    dot(d, (xe, 0))
    yD = yF - 1.3
    wire(d, [(xm, yF), (xm, yD)])
    wire(d, [(xe, yF), (xe, yD)])
    dot(d, (xm, yF))
    dot(d, (xe, yF))
    d.add(seg(elm.Diode(), (xm, yD), (xe, yD)))
    yD2 = yD - 1.0
    wire(d, [(xm, yD), (xm, yD2)])
    wire(d, [(xe, yD), (xe, yD2)])
    d.add(seg(elm.Diode(), (xe, yD2), (xm, yD2)))
    txt(axc, (xm + xe) / 2, yF + 0.35, r"$R_b$ 10 kΩ", va="bottom", fs=7)
    txt(axc, (xm + xe) / 2, yD2 - 0.4, "2 × 1N4148", va="top", fs=7)
    wire(d, [(xo, 0), (xe + 0.8, 0)])
    dot(d, (xe + 0.8, 0), open_=True)
    txt(axc, xe + 0.9, 0.3, r"$v_o$", ha="left", va="bottom", fs=8.5)
    txt(axc, op.center[0] - 0.1, op.center[1] + 1.5, "±12 V", fs=7, color=GREY)
    finish(axc, d)
    # waveform
    axp.plot(t * 1e3, vo, color=BLUE, lw=0.7)
    axp.axhline(spec[40], color=GREY, ls="--", lw=0.8)
    axp.axhline(-spec[40], color=GREY, ls="--", lw=0.8)
    txt(axp, 30.5, spec[40], f"{spec[40]:.2f} V", ha="left", fs=7.2, color=GREY)
    axp.set_xlim(0, 30)
    axp.set_ylim(-5.5, 5.5)
    axp.set_xlabel("time (ms)")
    axp.set_ylabel(r"$v_o$ (V)")
    axp.text(0.5, -5.2, f"start from 1 mV; steady state {spec[40]:.2f} V pk at {f_osc:.1f} Hz",
             fontsize=7.2, va="bottom")
    ai = fig.add_axes([0.60, 0.76, 0.30, 0.17])
    hn = np.arange(1, 11)
    ai.bar(hn, np.maximum(h, -80) + 80, bottom=-80, color=BLUE, width=0.6)
    ai.set_ylim(-80, 5)
    ai.set_xticks([1, 3, 5, 7, 9])
    ai.tick_params(labelsize=6)
    ai.set_title("spectrum (dB re fund.)", fontsize=6.5, pad=2)
    ai.text(3.5, h[2] + 2, f"HD3 {h[2]:.1f} dB", fontsize=6.3, va="bottom", ha="left")
    ai.text(10.5, -75, f"THD {100*thd:.1f} %", fontsize=6.3, ha="right", va="bottom")
    save(fig, "09", "fig-9-3-wien-bridge-oscillator")


# ----------------------------------------------------------------------------
def fig_9_4():
    """(a) CE Colpitts oscillator; (b) Pierce crystal oscillator."""
    fig = plt.figure(figsize=(6.8, 3.7))
    axa = fig.add_axes([0.0, 0.02, 0.54, 0.92])
    axb = fig.add_axes([0.56, 0.02, 0.44, 0.92])
    fs = 7.5
    # ---------- (a) Colpitts ----------
    d = drawing(axa, fontsize=fs)
    vcc = 8.0
    q = d.add(elm.BjtNpn(circle=True).right().at((4.2, 3.6)).anchor("base"))
    b, c, e = q.base, q.collector, q.emitter
    xb = 2.8
    wire(d, [(xb, vcc), (c[0], vcc)])
    txt(axa, (xb + c[0]) / 2, vcc + 0.2, "+3.3 V", va="bottom", fs=fs)
    # bias divider
    d.add(seg(elm.Resistor(), (xb, vcc), (xb, b[1])))
    d.add(seg(elm.Resistor(), (xb, b[1]), (xb, 0)))
    txt(axa, xb + 0.35, (vcc + b[1]) / 2, r"$R_{B1}$", ha="left", fs=fs)
    txt(axa, xb + 0.35, b[1] / 2 + 0.3, r"$R_{B2}$", ha="left", fs=fs)
    wire(d, [(xb, b[1]), b])
    dot(d, (xb, b[1]))
    # RF choke in the collector supply
    yc = c[1] + 1.0
    d.add(seg(elm.Inductor2(loops=3), (c[0], vcc), (c[0], yc)))
    txt(axa, c[0] + 0.35, (vcc + yc) / 2, "RFC", ha="left", fs=fs)
    wire(d, [(c[0], yc), c])
    dot(d, (c[0], yc))
    # emitter degeneration with bypass
    ye = e[1] - 0.5
    wire(d, [e, (e[0], ye)])
    dot(d, (e[0], ye))
    d.add(seg(elm.Resistor(), (e[0], ye), (e[0], 0)))
    txt(axa, e[0] - 0.35, ye / 2, r"$R_E$", ha="right", fs=fs)
    wire(d, [(e[0], ye), (e[0] + 1.0, ye)])
    d.add(seg(elm.Capacitor(), (e[0] + 1.0, ye), (e[0] + 1.0, 0)))
    txt(axa, e[0] + 1.3, ye / 2, r"$C_{E}$", ha="left", fs=fs)
    # tank: C2 from collector to ground, C1 from base to ground, L collector -> base (via C_B)
    xt = c[0] + 2.8
    wire(d, [(c[0], yc), (xt, yc)])
    d.add(seg(elm.Capacitor(), (xt, yc), (xt, 0)))
    txt(axa, xt + 0.3, yc / 2, r"$C_2$" + "\n510 pF", ha="left", fs=fs)
    dot(d, (xt, yc))
    ytop = vcc + 1.4
    xc1 = 1.0
    wire(d, [(xt, yc), (xt, ytop)])
    d.add(seg(elm.Inductor2(loops=4), (xt, ytop), (xc1 + 2.6, ytop)))
    wire(d, [(xc1 + 2.6, ytop), (xc1, ytop)])
    txt(axa, (xt + xc1 + 2.6) / 2, ytop + 0.35, r"$L$ = 1 µH  ($Q$ = 100, $R_s$ = 0.63 Ω)", va="bottom", fs=fs)
    d.add(seg(elm.Capacitor(), (xc1, ytop), (xc1, b[1] + 1.4)))
    txt(axa, xc1 - 0.3, (ytop + b[1] + 1.4) / 2, r"$C_B$" + "\n(DC\nblock)", ha="right", fs=6.8)
    wire(d, [(xc1, b[1] + 1.4), (xc1, b[1])])
    wire(d, [(xc1, b[1]), (xb, b[1])])
    dot(d, (xc1, b[1]))
    d.add(seg(elm.Capacitor(), (xc1, b[1]), (xc1, 0)))
    txt(axa, xc1 - 0.3, b[1] / 2, r"$C_1$" + "\n510 pF", ha="right", fs=fs)
    wire(d, [(xc1, 0), (xt, 0)])
    for x in (xb, e[0], e[0] + 1.0):
        dot(d, (x, 0))
    gnd(d, ((xc1 + xb) / 2, 0))
    # output coupling
    d.add(seg(elm.Capacitor(), (xt, yc), (xt + 1.8, yc)))
    dot(d, (xt + 1.8, yc), open_=True)
    txt(axa, xt + 0.9, yc + 0.3, "1 pF", va="bottom", fs=fs)
    txt(axa, xt + 1.95, yc, "out", ha="left", fs=fs)
    txt(axa, q.center[0] + 0.6, q.center[1] + 0.1, "BFR92A\n" + r"$I_C$ = 0.1 mA", ha="left", va="center",
        fs=6.8)
    txt(axa, 4.4, -1.1, r"$f_0$ = 10 MHz,  $|R_{neg}|=g_m/\omega^2C_1C_2$ = 3.8 Ω,  start-up margin 6",
        va="top", fs=7.3, color=GREEN)
    txt(axa, -0.9, ytop + 0.9, "(a)", ha="left", fs=10, weight="bold")
    finish(axa, d)
    # ---------- (b) Pierce ----------
    d = drawing(axb, fontsize=fs)
    yi = 4.6
    inv = d.add(logic.Not().right().at((2.6, yi)).anchor("in1"))
    xL, xR = 1.4, inv.out[0] + 1.2
    wire(d, [(xL, yi), inv.in1])
    wire(d, [inv.out, (xR, yi)])
    yr = yi + 1.4
    wire(d, [(xL, yi), (xL, yr)])
    wire(d, [(xR, yi), (xR, yr)])
    d.add(seg(elm.Resistor(), (xL, yr), (xR, yr)))
    txt(axb, (xL + xR) / 2, yr + 0.35, r"$R_f$ 1 MΩ (internal)", va="bottom", fs=fs)
    dot(d, (xL, yi))
    dot(d, (xR, yi))
    yp = yi - 1.0
    axb.add_patch(Rectangle((xL - 0.9, yp), xR - xL + 1.8, yr - yp + 1.1, fill=False, ls="--", ec=GREY, lw=0.9))
    txt(axb, xL - 0.8, yr + 1.0, "MCU", ha="left", va="top", fs=7.5, color=GREY)
    # pins
    yx = yp - 2.4
    wire(d, [(xL, yi), (xL, yx)])
    wire(d, [(xR, yi), (xR, yp - 0.3)])
    dot(d, (xL, yp), open_=True)
    dot(d, (xR, yp), open_=True)
    txt(axb, xL - 0.2, yp - 0.1, "OSC_IN", ha="right", va="top", fs=6.8)
    txt(axb, xR + 0.2, yp + 0.1, "OSC_OUT", ha="left", va="bottom", fs=6.8)
    d.add(seg(elm.Resistor(), (xR, yp - 0.3), (xR, yx)))
    txt(axb, xR + 0.35, (yp - 0.3 + yx) / 2, r"$R_d$" + "\n(optional)", ha="left", fs=6.8)
    xm = (xL + xR) / 2
    d.add(seg(elm.Crystal(), (xR, yx), (xL, yx)))
    txt(axb, xm, yx - 0.45, "16 MHz", va="top", fs=fs)
    dot(d, (xL, yx))
    dot(d, (xR, yx))
    # stray capacitance across the crystal (dashed), above it
    yS = yx + 1.0
    xs1 = xR - 0.7
    ax_ = axb
    ax_.plot([xL, xL + 0.7], [yS, yS], ls="--", color=GREY, lw=1.0)
    d.add(seg(elm.Capacitor(ls="--", color=GREY), (xL + 0.7, yS), (xs1 - 0.5, yS)))
    ax_.plot([xs1 - 0.5, xs1, xs1], [yS, yS, yx], ls="--", color=GREY, lw=1.0)
    dot(d, (xL, yS))
    txt(axb, (xL + xs1) / 2, yS + 0.35, r"$C_s$ ≈ 3 pF (stray)", va="bottom", fs=6.8, color=GREY)
    yg = yx - 2.4
    d.add(seg(elm.Capacitor(), (xL, yx), (xL, yg)))
    d.add(seg(elm.Capacitor(), (xR, yx), (xR, yg)))
    txt(axb, xL - 0.3, (yx + yg) / 2, r"$C_1$" + "\n18 pF", ha="right", fs=fs)
    txt(axb, xR + 0.3, (yx + yg) / 2, r"$C_2$" + "\n18 pF", ha="left", fs=fs)
    wire(d, [(xL, yg), (xR, yg)])
    gnd(d, (xm, yg))
    txt(axb, xm, yg - 1.0, r"$C_L=\dfrac{C_1C_2}{C_1+C_2}+C_s=12$ pF", va="top", fs=7.5, color=GREEN)
    txt(axb, xL - 1.6, yr + 1.6, "(b)", ha="left", fs=10, weight="bold")
    finish(axb, d)
    save(fig, "09", "fig-9-4-colpitts-and-pierce")


def fig_9_5():
    """Reactance of a 16 MHz AT-cut crystal near resonance."""
    Lm, Cm, Rm, C0 = 9.9e-3, 10e-15, 40.0, 3e-12
    fs_ = 1 / (2 * np.pi * np.sqrt(Lm * Cm))
    fa = fs_ * np.sqrt(1 + Cm / C0)
    ppm = np.linspace(-500, 2500, 60001)
    f = fs_ * (1 + ppm * 1e-6)
    w = 2 * np.pi * f
    Zm = Rm + 1j * (w * Lm - 1 / (w * Cm))
    Z0 = 1 / (1j * w * C0)
    Z = Zm * Z0 / (Zm + Z0)
    X = Z.imag

    def fl(CL):
        Ct = Cm * (C0 + CL) / (Cm + C0 + CL)
        return (1 / (2 * np.pi * np.sqrt(Lm * Ct)) / fs_ - 1) * 1e6

    pa = (fa / fs_ - 1) * 1e6
    p12, p9 = fl(12e-12), fl(9e-12)
    print(f"  fs = {fs_/1e6:.5f} MHz, fa = +{pa:.0f} ppm, fL(12 pF) = +{p12:.0f} ppm, fL(9 pF) = +{p9:.0f} ppm")
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.axvspan(0, pa, color=GREEN, alpha=0.10, lw=0)
    txt(ax, pa / 2 + 300, -15.5, "inductive:\nparallel-mode operating region", fs=7.8, color=GREEN)
    Xk = X / 1e3
    # draw the two branches separately so that the curve leaves the axes at the pole
    for m in (ppm < pa, ppm > pa):
        xb, yb = ppm[m], Xk[m]
        keep = np.abs(yb) < 40
        ax.plot(xb[keep], yb[keep], color=BLUE)
    ax.axhline(0, color=INK, lw=0.7)
    marks = [(0, r"$f_s$" + "\n0 ppm", -9), (p12, r"$f_L$ ($C_L$ = 12 pF)" + f"\n+{p12:.0f} ppm", 9),
             (p9, r"$f_L$ ($C_L$ = 9 pF)" + f"\n+{p9:.0f} ppm", 16), (pa, r"$f_a$" + f"\n+{pa:.0f} ppm", 9)]
    for p, lab, y in marks:
        ax.axvline(p, color=GREY, lw=0.8, ls="--")
        ax.text(p + 25, y, lab, fontsize=7.5, ha="left", va="center",
                bbox=dict(fc="white", ec="none", pad=0.5))
    ax.set_xlim(-500, 2500)
    ax.set_ylim(-20, 20)
    ax.set_xlabel(r"frequency offset from $f_s$ (ppm),  $f_s$ = " + f"{fs_/1e6:.4f} MHz")
    ax.set_ylabel(r"reactance $X$ (kΩ)")
    txt(ax, -480, -18.5, "capacitive (−)", ha="left", fs=7.2, color=GREY)
    # inset: Butterworth-Van Dyke model
    ai = fig.add_axes([0.79, 0.50, 0.16, 0.30])
    d = drawing(ai, fontsize=7, unit=1.4)
    d.add(seg(elm.Inductor2(loops=3), (0, 2), (1.7, 2)))
    d.add(seg(elm.Capacitor(), (1.7, 2), (3.2, 2)))
    d.add(seg(elm.Resistor(), (3.2, 2), (4.9, 2)))
    wire(d, [(0, 2), (0, 0.5)])
    wire(d, [(4.9, 2), (4.9, 0.5)])
    wire(d, [(0, 0.5), (1.8, 0.5)])
    d.add(seg(elm.Capacitor(), (1.8, 0.5), (3.1, 0.5)))
    wire(d, [(3.1, 0.5), (4.9, 0.5)])
    wire(d, [(-0.6, 1.25), (0, 1.25)])
    wire(d, [(4.9, 1.25), (5.5, 1.25)])
    dot(d, (0, 1.25))
    dot(d, (4.9, 1.25))
    txt(ai, 0.85, 2.45, r"$L_m$", va="bottom", fs=7)
    txt(ai, 2.45, 2.45, r"$C_m$", va="bottom", fs=7)
    txt(ai, 4.05, 2.45, r"$R_m$", va="bottom", fs=7)
    txt(ai, 2.45, 0.0, r"$C_0$", va="top", fs=7)
    finish(ai, d)
    ai.set_title("BVD model", fontsize=7, pad=7)
    save(fig, "09", "fig-9-5-crystal-reactance")


# ----------------------------------------------------------------------------
def fig_9_6():
    """Triangle-square function generator and its waveforms."""
    R, C, R1, R2, Vsat = 49.9e3, 10e-9, 10e3, 20e3, 10.0
    th = Vsat * R1 / R2
    slope = Vsat / (R * C)
    dt = 2e-7
    t = np.arange(0, 3e-3, dt)
    vt = np.zeros_like(t)
    vs = np.zeros_like(t)
    sq, v = Vsat, 0.0
    edges = []
    for i, ti in enumerate(t):
        vt[i], vs[i] = v, sq
        v -= sq / (R * C) * dt          # inverting integrator
        if sq > 0 and v <= -th:
            sq = -Vsat
            edges.append(ti)
        elif sq < 0 and v >= th:
            sq = Vsat
            edges.append(ti)
    T = 4 * R1 * R * C / R2
    print(f"  period {T*1e6:.1f} us, slope {slope/1e3:.2f} V/ms")
    fig = plt.figure(figsize=(6.8, 3.3))
    axc = fig.add_axes([0.0, 0.05, 0.40, 0.9])
    axp = fig.add_axes([0.49, 0.16, 0.49, 0.78])
    d = drawing(axc, fontsize=7.5)
    # integrator
    a1 = opamp(d, (3.2, 0))
    xi = a1.in1[0] - 0.5
    d.add(seg(elm.Resistor(), (xi - 2.2, a1.in1[1]), (xi, a1.in1[1])))
    wire(d, [(xi, a1.in1[1]), a1.in1])
    dot(d, (xi, a1.in1[1]))
    txt(axc, xi - 1.1, a1.in1[1] + 0.4, "R 49.9 kΩ", va="bottom", fs=7)
    yC = a1.in1[1] + 1.3
    x1o = a1.out[0] + 0.4
    wire(d, [(xi, a1.in1[1]), (xi, yC)])
    d.add(seg(elm.Capacitor(), (xi, yC), (x1o, yC)))
    txt(axc, (xi + x1o) / 2, yC + 0.4, "C 10 nF", va="bottom", fs=7)
    wire(d, [(x1o, yC), (x1o, a1.out[1]), a1.out])
    dot(d, (x1o, 0))
    wire(d, [a1.in2, (a1.in2[0] - 0.3, a1.in2[1]), (a1.in2[0] - 0.3, a1.in2[1] - 0.5)])
    gnd(d, (a1.in2[0] - 0.3, a1.in2[1] - 0.5))
    # Schmitt (non-inverting): input via R1 to +, R2 from output to +, - to ground
    a2 = opamp(d, (9.4, 0), flip=True)
    xs = a2.in2[0] - 0.6
    wire(d, [(x1o, 0), (x1o + 0.4, 0), (x1o + 0.4, a2.in2[1])])
    d.add(seg(elm.Resistor(), (x1o + 0.4, a2.in2[1]), (xs, a2.in2[1])))
    txt(axc, (x1o + 0.4 + xs) / 2, a2.in2[1] + 0.4, r"$R_1$ 10 kΩ", va="bottom", fs=7)
    wire(d, [(xs, a2.in2[1]), a2.in2])
    dot(d, (xs, a2.in2[1]))
    x2o = a2.out[0] + 0.4
    yR2 = a2.in2[1] + 1.4
    wire(d, [(xs, a2.in2[1]), (xs, yR2)])
    d.add(seg(elm.Resistor(), (xs, yR2), (x2o, yR2)))
    txt(axc, (xs + x2o) / 2, yR2 + 0.4, r"$R_2$ 20 kΩ", va="bottom", fs=7)
    wire(d, [(x2o, yR2), (x2o, a2.out[1]), a2.out])
    dot(d, (x2o, 0))
    wire(d, [a2.in1, (a2.in1[0] - 0.3, a2.in1[1]), (a2.in1[0] - 0.3, a2.in1[1] - 0.5)])
    gnd(d, (a2.in1[0] - 0.3, a2.in1[1] - 0.5))
    # feedback of the square wave to the integrator input
    yb = -2.6
    wire(d, [(x2o, 0), (x2o, yb), (xi - 2.2, yb), (xi - 2.2, a1.in1[1])])
    txt(axc, x1o + 0.15, -0.3, "triangle", ha="left", va="top", fs=7, color=ORANGE)
    txt(axc, x2o + 0.15, 0.25, "square", ha="left", va="bottom", fs=7, color=BLUE)
    txt(axc, 6.5, yb - 0.4, "±12 V supplies, outputs saturate at ±10 V", va="top", fs=6.8, color=GREY)
    finish(axc, d)
    tm = t * 1e3
    axp.plot(tm, vs, color=BLUE, lw=1.3, label="square (Schmitt output)")
    axp.plot(tm, vt, color=ORANGE, lw=1.6, label="triangle (integrator output)")
    for y in (th, -th):
        axp.axhline(y, color=GREY, ls="--", lw=0.8)
    txt(axp, 3.03, th, "+5 V", ha="left", fs=7.2, color=GREY)
    txt(axp, 3.03, -th, "−5 V", ha="left", fs=7.2, color=GREY)
    e = [x * 1e3 for x in edges]
    axp.annotate("", xy=(e[2], -11.6), xytext=(e[0], -11.6),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    txt(axp, (e[0] + e[2]) / 2, -11.8, f"T = {T*1e6:.0f} µs", va="top", fs=7.5)
    tmid = (e[0] + e[1]) / 2
    txt(axp, tmid, 7.0, f"+{slope/1e3:.2f}\nV/ms", fs=7.0, color=ORANGE)
    axp.set_xlim(0, 3)
    axp.set_ylim(-13.8, 14)
    axp.set_xlabel("time (ms)")
    axp.set_ylabel("voltage (V)")
    axp.legend(loc="upper center", fontsize=7.2, ncol=2, bbox_to_anchor=(0.5, 1.02))
    save(fig, "09", "fig-9-6-triangle-square-generator")


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    fig_9_1()
    fig_9_2()
    fig_9_3()
    fig_9_4()
    fig_9_5()
    fig_9_6()
