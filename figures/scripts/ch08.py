"""Figures for Chapter 8 — Operational Amplifiers.

Run from the repository root:  python figures/scripts/ch08.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
GREY = "#777777"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def drawing(ax, fontsize=8.5, lw=1.1, unit=2.0):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=fontsize, lw=lw, unit=unit)
    return d


def finish(ax, d, pad=0.3, full=True):
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


def dot(d, p, open_=False):
    d.add(elm.Dot(open=open_).at(p))


def seg(el, p, q):
    """Place a two-terminal element from p to q by angle and length (robust for sources)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    return el.at(p).theta(np.degrees(np.arctan2(dy, dx))).length(float(np.hypot(dx, dy)))


def gnd(d, p):
    d.add(elm.Ground().at(p))


def txt(ax, x, y, s, ha="center", va="center", fs=8, color=INK, **kw):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, **kw)


def rbox(ax, x, y, w, h, text, fs=7.5, fc="#EEF3F8", ec=INK, color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=fc, ec=ec, lw=1.0, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, zorder=3)


# ----------------------------------------------------------------------------
def fig_8_1():
    """Error model of a practical op-amp."""
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    d = drawing(ax, fontsize=7.5, unit=1.6)
    fs = 7.5
    yN, yP = 2.8, -2.8
    # terminals
    dot(d, (0, yN), open_=True)
    dot(d, (0, yP), open_=True)
    txt(ax, -0.3, yN, "−IN", ha="right", fs=8.5)
    txt(ax, -0.3, yP, "+IN", ha="right", fs=8.5)
    # series input-referred voltage sources on the + path
    xs = [0.6, 3.4, 6.2, 9.0, 11.8]
    labs = [(r"$V_{OS}$" + "\n(drift " + r"$dV_{OS}/dT$" + ")", "top"), (r"$e_n$" + " (noise)", "bot"),
            (r"$V_{cm}/\mathrm{CMRR}$", "top"), (r"$\Delta V_{S}/\mathrm{PSRR}$", "bot")]
    cols = [INK, PINK, GREEN, GREEN]
    wire(d, [(0, yP), (xs[0], yP)])
    for k in range(4):
        x0, x1 = xs[k] + 0.4, xs[k + 1] - 0.4
        wire(d, [(xs[k], yP), (x0, yP)])
        d.add(seg(elm.SourceV(color=cols[k]), (x0, yP), (x1, yP)))
        wire(d, [(x1, yP), (xs[k + 1], yP)])
        lab, side = labs[k]
        xm = (xs[k] + xs[k + 1]) / 2
        if side == "top":
            txt(ax, xm, yP + 0.75, lab, va="bottom", fs=fs, color=cols[k])
        else:
            txt(ax, xm, yP - 0.75, lab, va="top", fs=fs, color=cols[k])
    # node lines
    xn = [13.6, 16.6, 19.6, 22.2]
    xd = [24.8, 27.2]
    xin = 29.4
    wire(d, [(0, yN), (xin, yN)])
    wire(d, [(xs[-1], yP), (xin, yP)])
    for x in xn + xd:
        dot(d, (x, yN))
        dot(d, (x, yP))
    ytop, ybot = yN + 2.6, yP - 2.6
    for y0, y1, sgn in ((yN, ytop, "−"), (yP, ybot, "+")):
        d.add(seg(elm.SourceI(), (xn[0], y0), (xn[0], y1)))
        d.add(seg(elm.SourceI(color=PINK), (xn[1], y0), (xn[1], y1)))
        d.add(seg(elm.Resistor(), (xn[2], y0), (xn[2], y1)))
        d.add(seg(elm.Capacitor(), (xn[3], y0), (xn[3], y1)))
        wire(d, [(xn[0], y1), (xn[3], y1)])
        ym = (y0 + y1) / 2
        txt(ax, xn[0] + 0.65, ym, r"$I_{B" + sgn + "}$", ha="left", fs=fs)
        txt(ax, xn[1] + 0.65, ym, r"$i_{n" + sgn + "}$", ha="left", fs=fs, color=PINK)
        txt(ax, xn[2] + 0.4, ym, r"$R_{cm}$", ha="left", fs=fs)
        txt(ax, xn[3] + 0.4, ym, r"$C_{cm}$", ha="left", fs=fs)
    xg = (xn[0] + xn[3]) / 2
    gnd(d, (xg, ybot))
    d.add(elm.Ground().at((xg, ytop)).theta(180))
    txt(ax, xn[0] - 0.4, ytop - 0.3, r"$I_{OS}=I_{B+}-I_{B-}$", ha="right", va="top", fs=fs)
    # differential input impedance
    d.add(seg(elm.Resistor(), (xd[0], yN), (xd[0], yP)))
    d.add(seg(elm.Capacitor(), (xd[1], yN), (xd[1], yP)))
    txt(ax, xd[0] + 0.4, 0, r"$R_d$", ha="left", fs=fs)
    txt(ax, xd[1] + 0.4, 0, r"$C_d$", ha="left", fs=fs)
    # ideal op-amp
    op = d.add(elm.Opamp(leads=False).right().at((xin + 2.4, 0)).anchor("center"))
    wire(d, [(xin, yN), (xin, op.in1[1]), op.in1])
    wire(d, [(xin, yP), (xin, op.in2[1]), op.in2])
    txt(ax, op.center[0] - 0.15, 0, r"$A(s)$", fs=8)
    txt(ax, op.center[0] + 0.5, yN + 0.3, "ideal: " + r"$A(s)=\dfrac{A_0}{1+s/\omega_p}$", va="bottom", fs=fs)
    # output chain
    out = op.out
    xr1 = out[0] + 2.6
    d.add(seg(elm.Resistor(), out, (xr1, 0)))
    txt(ax, (out[0] + xr1) / 2, 0.5, r"$R_{out}$", va="bottom", fs=fs)
    wire(d, [(xr1, 0), (xr1 + 0.5, 0)])
    rbox(ax, xr1 + 0.5, -1.5, 3.8, 3.0, "slew-rate\nlimiter\n" + r"$SR$", fs=7, fc="#FCEFE6", ec=ORANGE)
    xb2 = xr1 + 5.1
    wire(d, [(xr1 + 4.3, 0), (xb2, 0)])
    rbox(ax, xb2, -2.4, 5.6, 4.8, "output swing\n" + r"$V_-+V_{sat}$" + " to\n" + r"$V_+-V_{sat}$" +
         "\ncurrent limit\n" + r"$I_{sc}$", fs=7, fc="#FCEFE6", ec=ORANGE)
    xo = xb2 + 6.4
    wire(d, [(xb2 + 5.6, 0), (xo, 0)])
    dot(d, (xo, 0), open_=True)
    txt(ax, xo + 0.3, 0, "OUT", ha="left", fs=8.5)
    vals = (r"Typical: $A_0=10^5$–$10^7$, GBW $=A_0\,\omega_p/2\pi$;   $R_{cm}=10^9$–$10^{12}\ \Omega$,  "
            r"$C_{cm}=2$–$10$ pF;   $R_{out}=20$–$200\ \Omega$ (open loop)")
    txt(ax, 23.0, ybot - 1.6, vals, va="top", fs=7.3, color=GREY)
    finish(ax, d)
    save(fig, "08", "fig-8-1-opamp-error-model")



def _opamp(d, center, flip=False):
    el = elm.Opamp(leads=False).right().at(center).anchor("center")
    if flip:
        el = el.flip()
    return d.add(el)


def fig_8_2():
    """(a) difference amplifier on a high-side shunt; (b) three-op-amp in-amp on a bridge."""
    fig = plt.figure(figsize=(6.8, 6.6))
    axa = fig.add_axes([0.0, 0.56, 1.0, 0.44])
    axb = fig.add_axes([0.0, 0.0, 1.0, 0.53])
    fs = 8

    # ---------------- (a) ----------------
    d = drawing(axa, fontsize=fs)
    ytop = 8.0
    d.add(elm.Battery().at((0, 0)).to((0, ytop)).reverse())
    txt(axa, -0.5, ytop / 2, "12 V\nbattery", ha="right", fs=fs)
    A, B = (3.0, ytop), (3.0, 5.4)
    wire(d, [(0, ytop), A])
    d.add(elm.Resistor().at(A).to(B))
    txt(axa, 2.65, (A[1] + B[1]) / 2, r"$R_{sh}$" + "\n1 mΩ", ha="right", fs=fs)
    axa.annotate("", xy=(3.45, B[1] + 0.5), xytext=(3.45, A[1] - 0.3),
                 arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=9))
    txt(axa, 3.55, A[1] - 0.25, r"$I\leq 20$ A", ha="left", va="top", fs=fs, color=BLUE)
    dot(d, A)
    dot(d, B)
    d.add(elm.RBox().at(B).to((3.0, 0)))
    txt(axa, 2.6, 2.6, "load", ha="right", fs=fs)
    wire(d, [(0, 0), (3.0, 0)])
    gnd(d, (1.5, 0))
    op = _opamp(d, (10.0, 6.2))
    n_in, p_in, out = op.in1, op.in2, op.out
    xj = n_in[0] - 0.7
    d.add(elm.Resistor().at(A).to((xj - 0.2, ytop)))
    txt(axa, (A[0] + xj) / 2, ytop + 0.45, r"$R_1$ 2 kΩ", va="bottom", fs=fs)
    wire(d, [(xj - 0.2, ytop), (xj, ytop), (xj, n_in[1]), n_in])
    dot(d, (xj, ytop))
    yf = ytop + 1.5
    wire(d, [(xj, ytop), (xj, yf)])
    d.add(elm.Resistor().at((xj, yf)).to((out[0] + 0.4, yf)))
    txt(axa, (xj + out[0]) / 2, yf + 0.45, r"$R_2$ 100 kΩ", va="bottom", fs=fs)
    wire(d, [(out[0] + 0.4, yf), (out[0] + 0.4, out[1]), out])
    xk = n_in[0] - 1.3
    d.add(elm.Resistor().at(B).to((xk - 0.2, B[1])))
    txt(axa, (B[0] + xk) / 2, B[1] + 0.45, r"$R_3$ 2 kΩ", va="bottom", fs=fs)
    wire(d, [(xk - 0.2, B[1]), (xk, B[1]), (xk, p_in[1]), p_in])
    dot(d, (xk, p_in[1]))
    d.add(elm.Resistor().at((xk, p_in[1])).to((xk, 1.0)))
    gnd(d, (xk, 1.0))
    txt(axa, xk + 0.35, (p_in[1] + 1.0) / 2, r"$R_4$" + "\n100 kΩ", ha="left", fs=fs)
    txt(axa, xk - 0.15, p_in[1] - 0.55, r"$V_+=11.76$ V", ha="right", va="top", fs=7.5, color=BLUE)
    xo = out[0] + 1.6
    wire(d, [(out[0] + 0.4, out[1]), (xo, out[1])])
    dot(d, (out[0] + 0.4, out[1]))
    dot(d, (xo, out[1]), open_=True)
    txt(axa, xo + 0.25, out[1], r"$v_o=G\,R_{sh}I$" + "\n(1 V at 20 A)", ha="left", fs=fs)
    txt(axa, xo + 0.25, 2.6, r"$G=R_2/R_1=50$" + "\nCMRR = 82 dB\n(0.1 % resistors)", ha="left",
        fs=fs, color=GREEN)
    txt(axa, -2.4, ytop + 1.6, "(a)", ha="left", fs=10, weight="bold")
    finish(axa, d, full=False)

    # ---------------- (b) ----------------
    d = drawing(axb, fontsize=fs)
    # bridge: excitation at left node, ground at right node, outputs at top and bottom
    cx, cy, rx, ry = 2.2, 4.0, 2.0, 2.2
    L, R_, T, Bt = (cx - rx, cy), (cx + rx, cy), (cx, cy + ry), (cx, cy - ry)
    for p, q in ((L, T), (T, R_), (L, Bt), (Bt, R_)):
        d.add(elm.Resistor().at(p).to(q))
    for p in (L, R_, T, Bt):
        dot(d, p)
    txt(axb, cx, cy, "4 × 350 Ω\nstrain\ngauges", fs=7.2, color=GREY)
    wire(d, [L, (L[0] - 0.8, cy)])
    dot(d, (L[0] - 0.8, cy), open_=True)
    txt(axb, L[0] - 1.0, cy, "+5 V", ha="right", fs=fs)
    wire(d, [R_, (R_[0], cy - 0.8)])
    gnd(d, (R_[0], cy - 0.8))
    a1 = _opamp(d, (8.4, 7.2), flip=True)    # + input on top
    a2 = _opamp(d, (8.4, 0.8))               # + input on bottom
    wire(d, [T, (cx, a1.in2[1]), a1.in2])
    wire(d, [Bt, (cx, a2.in2[1]), a2.in2])
    txt(axb, cx + 0.15, a1.in2[1] + 0.2, "≈ 2.5 V", ha="left", va="bottom", fs=7.5, color=BLUE)
    txt(axb, cx + 0.15, a2.in2[1] - 0.2, "≈ 2.5 V", ha="left", va="top", fs=7.5, color=BLUE)
    txt(axb, cx - 1.6, cy + 2.9, "10 mV full-scale\ndifference", ha="center", fs=7.2, color=BLUE)
    xg = a1.in1[0] - 0.8
    yg1, yg2 = cy + 1.25, cy - 1.25
    wire(d, [a1.in1, (xg, a1.in1[1]), (xg, yg1)])
    wire(d, [a2.in1, (xg, a2.in1[1]), (xg, yg2)])
    dot(d, (xg, yg1))
    dot(d, (xg, yg2))
    d.add(elm.Resistor().at((xg, yg1)).to((xg, yg2)))
    txt(axb, xg - 0.35, cy, r"$R_G$" + "\n249 Ω", ha="right", fs=fs)
    xf = a1.out[0] + 0.5
    d.add(elm.Resistor().at((xg, yg1)).to((xf, yg1)))
    d.add(elm.Resistor().at((xg, yg2)).to((xf, yg2)))
    txt(axb, (xg + xf) / 2, yg1 - 0.45, r"$R$ 50 kΩ", va="top", fs=fs)
    txt(axb, (xg + xf) / 2, yg2 + 0.45, r"$R$ 50 kΩ", va="bottom", fs=fs)
    wire(d, [(xf, yg1), (xf, a1.out[1]), a1.out])
    wire(d, [(xf, yg2), (xf, a2.out[1]), a2.out])
    dot(d, (xf, a1.out[1]))
    dot(d, (xf, a2.out[1]))
    txt(axb, a1.center[0] - 0.25, a1.center[1], r"$A_1$", fs=8.5)
    txt(axb, a2.center[0] - 0.25, a2.center[1], r"$A_2$", fs=8.5)
    # difference stage
    a3 = _opamp(d, (16.6, cy))
    xa = xf + 0.6
    xr = a3.in1[0] - 0.7
    wire(d, [(xf, a1.out[1]), (xa, a1.out[1]), (xa, a3.in1[1])])
    d.add(elm.Resistor().at((xa, a3.in1[1])).to((xr, a3.in1[1])))
    wire(d, [(xr, a3.in1[1]), a3.in1])
    wire(d, [(xf, a2.out[1]), (xa, a2.out[1]), (xa, a3.in2[1])])
    d.add(elm.Resistor().at((xa, a3.in2[1])).to((xr - 0.5, a3.in2[1])))
    wire(d, [(xr - 0.5, a3.in2[1]), a3.in2])
    txt(axb, (xa + xr) / 2, a3.in1[1] + 0.4, "10 kΩ", va="bottom", fs=fs)
    txt(axb, (xa + xr - 0.5) / 2, a3.in2[1] - 0.4, "10 kΩ", va="top", fs=fs)
    dot(d, (xr, a3.in1[1]))
    dot(d, (xr - 0.5, a3.in2[1]))
    yf3 = a3.in1[1] + 1.6
    xo3 = a3.out[0] + 0.4
    wire(d, [(xr, a3.in1[1]), (xr, yf3)])
    d.add(elm.Resistor().at((xr, yf3)).to((xo3, yf3)))
    txt(axb, (xr + xo3) / 2, yf3 + 0.4, "10 kΩ", va="bottom", fs=fs)
    wire(d, [(xo3, yf3), (xo3, a3.out[1]), a3.out])
    d.add(elm.Resistor().at((xr - 0.5, a3.in2[1])).to((xr - 0.5, a3.in2[1] - 2.2)))
    txt(axb, xr - 0.15, a3.in2[1] - 1.1, "10 kΩ", ha="left", fs=fs)
    yref = a3.in2[1] - 2.2
    dot(d, (xr - 0.5, yref), open_=True)
    txt(axb, xr - 0.5, yref - 0.3, "REF = 2.5 V", va="top", fs=fs)
    txt(axb, a3.center[0] - 0.25, a3.center[1], r"$A_3$", fs=8.5)
    xo = xo3 + 1.0
    wire(d, [(xo3, a3.out[1]), (xo, a3.out[1])])
    dot(d, (xo3, a3.out[1]))
    dot(d, (xo, a3.out[1]), open_=True)
    txt(axb, xo + 0.25, a3.out[1], r"$v_o$", ha="left", fs=9)
    txt(axb, a3.center[0] + 0.3, a3.out[1] - 2.6,
        r"$G=1+2R/R_G=403$" + "\n" + r"$v_o=2.5\ \mathrm{V}\pm2.01$ V" + "\n(4.03 V span, inside rails)",
        ha="left", va="top", fs=fs, color=GREEN)
    txt(axb, -1.4, 8.4, "(b)", ha="left", fs=10, weight="bold")
    finish(axb, d, full=False)
    save(fig, "08", "fig-8-2-difference-and-instrumentation-amplifiers")


def fig_8_3():
    """Schmitt trigger: hysteresis loop and noisy-input response."""
    VDD, VH, VL, VC = 3.3, 1.75, 1.55, 1.65
    fig = plt.figure(figsize=(6.8, 3.6))
    gs = fig.add_gridspec(3, 2, width_ratios=[1, 1.55], height_ratios=[1.7, 1, 1],
                          wspace=0.32, hspace=0.25, left=0.09, right=0.93, bottom=0.13, top=0.95)
    a1 = fig.add_subplot(gs[:, 0])
    # transfer characteristic
    a1.plot([1.3, VH, VH, 2.0], [0, 0, VDD, VDD], color=BLUE, lw=1.8)
    a1.plot([2.0, VL, VL, 1.3], [VDD, VDD, 0, 0], color=BLUE, lw=1.8)
    a1.axvline(VC, color=ORANGE, ls="--", lw=1.0)
    txt(a1, VC + 0.01, 1.65, "no\nhysteresis\n1.65 V", ha="left", fs=7.2, color=ORANGE)
    for (x0, y0, x1, y1) in ((1.38, 0.1, 1.5, 0.1), (VH, 0.9, VH, 1.9), (1.95, VDD - 0.1, 1.83, VDD - 0.1),
                             (VL, 2.4, VL, 1.4)):
        a1.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.1, mutation_scale=10))
    txt(a1, VH + 0.02, 0.45, "1.75 V", ha="left", fs=7.5, color=BLUE)
    txt(a1, VL - 0.02, 2.85, "1.55 V", ha="right", fs=7.5, color=BLUE)
    a1.set_xlim(1.3, 2.0)
    a1.set_ylim(-0.15, 3.6)
    a1.set_xlabel(r"$v_{in}$ (V)")
    a1.set_ylabel(r"$v_{out}$ (V)")
    # noisy input in time
    rng = np.random.default_rng(7)
    fsamp = 200e3
    t = np.arange(0, 10e-3, 1 / fsamp)
    tri = 1.65 + 0.35 * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * 100 * t - np.pi / 2 + 0.6))
    raw = rng.uniform(-1, 1, t.size)
    nz = np.convolve(raw, np.ones(8) / 8, mode="same")
    nz = 0.05 * nz / np.max(np.abs(nz))          # bounded to +/- 50 mV
    vin = tri + nz
    comp = np.where(vin > VC, VDD, 0.0)
    sch = np.zeros_like(vin)
    state = vin[0] > VC
    for i, v in enumerate(vin):
        if state and v < VL:
            state = False
        elif not state and v > VH:
            state = True
        sch[i] = VDD if state else 0.0
    n_comp = np.count_nonzero(np.diff(comp))
    n_sch = np.count_nonzero(np.diff(sch))
    print(f"  comparator edges {n_comp}, Schmitt edges {n_sch}")
    tm = t * 1e3
    b1 = fig.add_subplot(gs[0, 1])
    b2 = fig.add_subplot(gs[1, 1], sharex=b1)
    b3 = fig.add_subplot(gs[2, 1], sharex=b1)
    b1.plot(tm, vin, color=INK, lw=0.8)
    for y, lab in ((VH, "1.75 V"), (VL, "1.55 V")):
        b1.axhline(y, color=BLUE, ls="--", lw=0.8)
        txt(b1, 10.1, y, lab, ha="left", fs=7, color=BLUE)
    b1.set_ylim(1.25, 2.08)
    b1.set_yticks([1.3, 1.65, 2.0])
    b1.set_ylabel(r"$v_{in}$ (V)")
    txt(b1, 0.15, 2.04, "input, 100 Hz with ±50 mV noise", ha="left", va="top", fs=7.3)
    b2.plot(tm, comp, color=ORANGE, lw=1.0)
    b2.set_ylabel("V", fontsize=8)
    txt(b2, 5.0, 1.65, f"comparator, no hysteresis: {n_comp} edges", fs=7.3, color=ORANGE,
        bbox=dict(fc="white", ec="none", pad=0.5))
    b3.plot(tm, sch, color=GREEN, lw=1.2)
    b3.set_ylabel("V", fontsize=8)
    txt(b3, 5.0, 1.65, f"Schmitt trigger: {n_sch} edges", fs=7.3, color=GREEN,
        bbox=dict(fc="white", ec="none", pad=0.5))
    for b in (b2, b3):
        b.set_ylim(-0.4, 3.7)
        b.set_yticks([0, 3.3])
    for b in (b1, b2):
        plt.setp(b.get_xticklabels(), visible=False)
    b3.set_xlim(0, 10)
    b3.set_xlabel("time (ms)")
    save(fig, "08", "fig-8-3-schmitt-trigger")


def fig_8_4():
    """Two-op-amp precision full-wave rectifier with waveforms."""
    fig = plt.figure(figsize=(6.8, 4.6))
    ax = fig.add_axes([0.0, 0.30, 1.0, 0.70])
    fs = 8
    d = drawing(ax, fontsize=fs)
    yin = 3.0
    dot(d, (0, yin), open_=True)
    txt(ax, -0.25, yin, r"$v_i$", ha="right", fs=9)
    a1 = _opamp(d, (6.0, 2.4))
    N = (a1.in1[0] - 0.8, a1.in1[1])
    d.add(elm.Resistor().at((1.2, a1.in1[1])).to(N))
    wire(d, [(0, yin), (1.2, yin), (1.2, a1.in1[1])])
    dot(d, (1.2, yin))
    txt(ax, (1.2 + N[0]) / 2, a1.in1[1] + 0.4, r"$R_1$ 10 kΩ", va="bottom", fs=fs)
    wire(d, [N, a1.in1])
    dot(d, N)
    wire(d, [a1.in2, (a1.in2[0] - 0.4, a1.in2[1]), (a1.in2[0] - 0.4, a1.in2[1] - 0.6)])
    gnd(d, (a1.in2[0] - 0.4, a1.in2[1] - 0.6))
    xo1 = a1.out[0] + 0.5
    wire(d, [a1.out, (xo1, a1.out[1])])
    dot(d, (xo1, a1.out[1]))
    # D2: clamp, anode at the op-amp output, cathode at the inverting input
    yD2 = a1.in1[1] + 1.4
    wire(d, [N, (N[0], yD2)])
    d.add(elm.Diode().at((xo1, yD2)).to((N[0], yD2)))
    wire(d, [(xo1, a1.out[1]), (xo1, yD2)])
    txt(ax, (N[0] + xo1) / 2, yD2 + 0.4, r"$D_2$ 1N4148", va="bottom", fs=fs)
    # D1 and R2 to node X
    yD1 = yD2 + 1.6
    X = (xo1 + 2.6, yD1)
    wire(d, [(N[0], yD2), (N[0], yD1)])
    dot(d, (N[0], yD2))
    d.add(elm.Resistor().at((N[0], yD1)).to((xo1, yD1)))
    txt(ax, (N[0] + xo1) / 2, yD1 + 0.4, r"$R_2$ 10 kΩ", va="bottom", fs=fs)
    wire(d, [(xo1, yD1), X])
    # D1 from X (anode) to the op-amp output (cathode)
    xD1 = X[0]
    d.add(elm.Diode().at(X).to((xD1, a1.out[1])))
    wire(d, [(xD1, a1.out[1]), (xo1, a1.out[1])])
    txt(ax, xD1 + 0.35, (X[1] + a1.out[1]) / 2, r"$D_1$" + "\n1N4148", ha="left", fs=fs)
    dot(d, X)
    txt(ax, X[0] + 0.1, X[1] + 0.25, "X", ha="left", va="bottom", fs=9, color=ORANGE)
    txt(ax, a1.center[0] - 0.25, a1.center[1], r"$A_1$", fs=8.5)
    # stage 2: summing inverter
    a2 = _opamp(d, (16.2, 3.2))
    S = (a2.in1[0] - 0.8, a2.in1[1])
    ytop = yD1 + 1.6
    # R3 from vi along the top
    wire(d, [(1.2, yin), (1.2, ytop + 1.4)])
    d.add(elm.Resistor().at((1.2, ytop + 1.4)).to((S[0] - 2.0, ytop + 1.4)))
    txt(ax, 6.0, ytop + 1.8, r"$R_3$ 20 kΩ", va="bottom", fs=fs)
    wire(d, [(S[0] - 2.0, ytop + 1.4), (S[0], ytop + 1.4), (S[0], S[1])])
    # R4 from X
    d.add(elm.Resistor().at(X).to((S[0] - 0.6, X[1])))
    txt(ax, (X[0] + S[0]) / 2, X[1] + 0.4, r"$R_4$ 10 kΩ", va="bottom", fs=fs)
    wire(d, [(S[0] - 0.6, X[1]), (S[0], X[1])])
    dot(d, (S[0], X[1]))
    wire(d, [S, a2.in1])
    dot(d, S)
    wire(d, [a2.in2, (a2.in2[0] - 0.4, a2.in2[1]), (a2.in2[0] - 0.4, a2.in2[1] - 0.6)])
    gnd(d, (a2.in2[0] - 0.4, a2.in2[1] - 0.6))
    # R5 feedback
    xo2 = a2.out[0] + 0.5
    yR5 = ytop + 0.2
    dot(d, (S[0], yR5))
    d.add(elm.Resistor().at((S[0], yR5)).to((xo2, yR5)))
    txt(ax, (S[0] + xo2) / 2, yR5 + 0.4, r"$R_5$ 20 kΩ", va="bottom", fs=fs)
    wire(d, [(xo2, yR5), (xo2, a2.out[1]), a2.out])
    wire(d, [(xo2, a2.out[1]), (xo2 + 1.0, a2.out[1])])
    dot(d, (xo2, a2.out[1]))
    dot(d, (xo2 + 1.0, a2.out[1]), open_=True)
    txt(ax, xo2 + 1.25, a2.out[1], r"$v_o=|v_i|$", ha="left", fs=9)
    txt(ax, a2.center[0] - 0.25, a2.center[1], r"$A_2$", fs=8.5)
    txt(ax, S[0] + 0.6, ytop + 1.4, r"$A_1$, $A_2$: TL072 (or OPA2192)" + "\n" + r"$v_o=-(v_i+2v_X)$",
        ha="left", va="center", fs=7.5, color=GREY)
    finish(ax, d, full=False)
    # waveforms
    t = np.linspace(0, 2e-3, 2000)
    vi = 0.1 * np.sin(2 * np.pi * 1e3 * t)
    vx = np.minimum(-vi, 0)
    vo = np.abs(vi)
    for k, (y, lab, col) in enumerate(((vi, r"$v_i$", INK), (vx, r"$v_X$", ORANGE), (vo, r"$v_o$", BLUE))):
        a = fig.add_axes([0.08 + k * 0.31, 0.07, 0.25, 0.19])
        a.plot(t * 1e3, y * 1e3, color=col, lw=1.4)
        a.axhline(0, color=GRID, lw=0.7, zorder=0)
        a.set_ylim(-120, 120)
        a.set_xlim(0, 2)
        a.set_yticks([-100, 0, 100])
        a.tick_params(labelsize=7)
        a.set_xlabel("time (ms)", fontsize=7.5, labelpad=1)
        if k == 0:
            a.set_ylabel("mV", fontsize=7.5, labelpad=1)
        a.set_title(lab + ("  (1 kHz, 100 mV pk)" if k == 0 else ""), fontsize=8, pad=2)
    save(fig, "08", "fig-8-4-precision-full-wave-rectifier")


def _mfb_lowpass(f0, Q, K, C2, C1):
    w0 = 2 * np.pi * f0
    P = 1 / (w0**2 * C1 * C2)
    S = 1 / (w0 * Q * C2)
    R3 = (S - np.sqrt(S**2 - 4 * (1 + K) * P)) / (2 * (1 + K))
    R2 = P / R3
    return R2 / K, R2, R3


def _e96(r):
    base = np.round(np.logspace(0, 2, 97)[:-1], 2)
    dec = 10 ** np.floor(np.log10(r))
    return dec * base[np.argmin(abs(base - r / dec))]


def _mfb_H(f, R1, R2, R3, C1, C2):
    s = 2j * np.pi * f
    return -(R2 / R1) / (s**2 * C1 * C2 * R2 * R3 + s * C2 * (R2 + R3 + R2 * R3 / R1) + 1)


def fig_8_5():
    """Fourth-order MFB Butterworth anti-aliasing filter response."""
    parts = []
    for Q, C1 in ((0.5412, 3.3e-9), (1.3066, 15e-9)):
        R = [_e96(r) for r in _mfb_lowpass(10e3, Q, 1.0, 1e-9, C1)]
        parts.append((*R, C1, 1e-9))
    f = np.logspace(2, np.log10(2e5), 3000)
    h1 = 20 * np.log10(abs(_mfb_H(f, *parts[0])))
    h2 = 20 * np.log10(abs(_mfb_H(f, *parts[1])))
    ht = h1 + h2
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.semilogx(f, h1, color=ORANGE, ls="--", label="section 1 (Q = 0.541)")
    ax.semilogx(f, h2, color=GREEN, ls=":", lw=2.2, label="section 2 (Q = 1.307)")
    ax.semilogx(f, ht, color=BLUE, label="overall, 4th-order Butterworth")
    ax.axhline(-96, color=PINK, ls="--", lw=1.0)
    txt(ax, 130, -93.5, "16-bit target (−96 dB)", ha="left", fs=7.8, color=PINK)
    for fx, lab in ((10e3, "10 kHz\npassband edge"), (25.6e3, "25.6 kHz\nNyquist"),
                    (41.2e3, "41.2 kHz\nalias of 10 kHz")):
        ax.axvline(fx, color=GREY, lw=0.8, ls="-.")
    txt(ax, 9.3e3, -75, "10 kHz\npassband\nedge", ha="right", fs=7.2, color=GREY)
    txt(ax, 24e3, -60, "25.6 kHz\nNyquist", ha="right", fs=7.2, color=GREY)
    txt(ax, 44e3, -75, "41.2 kHz\nalias of\n10 kHz", ha="left", fs=7.2, color=GREY)
    fpk = f[np.argmax(h2)]
    marks = [(fpk, h2.max(), f"+{h2.max():.1f} dB at {fpk/1e3:.1f} kHz", GREEN, (1.3e3, 6.5))]
    for fx in (10e3, 20e3, 25.6e3, 41.2e3):
        val = 20 * np.log10(abs(np.prod([_mfb_H(fx, *p) for p in parts])))
        marks.append((fx, val, (f"{val:.2f} dB" if fx == 10e3 else f"{val:.1f} dB"), BLUE, None))
    for fx, val, lab, col, pos in marks:
        ax.plot(fx, val, "o", color=col, ms=4, zorder=5)
        if pos:
            ax.annotate(lab, xy=(fx, val), xytext=pos, fontsize=7.5, color=col,
                        arrowprops=dict(arrowstyle="-", color=col, lw=0.7))
        else:
            ax.text(fx / 1.08, val - 0.5, lab, fontsize=7.5, color=col, ha="right", va="top",
                    bbox=dict(fc="white", ec="none", pad=0.4))
    ax.set_xlim(100, 2e5)
    ax.set_ylim(-100, 10)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("gain (dB)")
    ax.grid(True, which="major", lw=0.5)
    ax.legend(loc="center left", fontsize=7.8, bbox_to_anchor=(0.0, 0.42))
    save(fig, "08", "fig-8-5-mfb-anti-alias-response")


def fig_8_6():
    """Op-amp relaxation oscillator: circuit and waveforms."""
    R, C, Vs, beta = 45.3e3, 10e-9, 5.0, 0.5
    tau = R * C
    dt = 1e-7
    t = np.arange(0, 3e-3, dt)
    vc = np.zeros_like(t)
    vo = np.zeros_like(t)
    out = Vs
    v = 0.0
    edges = []
    for i, ti in enumerate(t):
        vc[i], vo[i] = v, out
        v += (out - v) * dt / tau
        if out > 0 and v >= beta * Vs:
            out = -Vs
            edges.append(ti)
        elif out < 0 and v <= -beta * Vs:
            out = Vs
            edges.append(ti)
    T = 2 * tau * np.log((1 + beta) / (1 - beta))
    print(f"  period {T*1e3:.4f} ms, f = {1/T:.1f} Hz; simulated half-period {np.diff(edges).mean()*1e3:.4f} ms")
    fig = plt.figure(figsize=(6.8, 3.2))
    axc = fig.add_axes([0.0, 0.05, 0.36, 0.9])
    axp = fig.add_axes([0.45, 0.16, 0.53, 0.78])
    d = drawing(axc, fontsize=8)
    op = _opamp(d, (3.0, 0))
    xo = op.out[0] + 0.5
    wire(d, [op.out, (xo, 0)])
    dot(d, (xo, 0))
    # R to inverting input, C to ground
    yR = op.in1[1] + 1.4
    xn = op.in1[0] - 0.6
    wire(d, [op.in1, (xn, op.in1[1]), (xn, yR)])
    d.add(elm.Resistor().at((xo, yR)).to((xn, yR)))
    wire(d, [(xo, 0), (xo, yR)])
    txt(axc, (xo + xn) / 2, yR + 0.4, r"$R$ 45.3 kΩ", va="bottom", fs=8)
    xc = xn - 1.2
    wire(d, [(xn, op.in1[1]), (xc, op.in1[1])])
    dot(d, (xn, op.in1[1]))
    d.add(elm.Capacitor().at((xc, op.in1[1])).to((xc, op.in1[1] - 2.2)))
    gnd(d, (xc, op.in1[1] - 2.2))
    txt(axc, xc - 0.35, op.in1[1] - 1.1, r"$C$" + "\n10 nF", ha="right", fs=8)
    txt(axc, xc, op.in1[1] + 0.2, r"$v_C$", va="bottom", fs=8, color=ORANGE)
    # divider R1, R2 from output to + input
    yd = op.in2[1] - 1.4
    xp = op.in2[0] - 0.6
    wire(d, [op.in2, (xp, op.in2[1]), (xp, yd)])
    d.add(elm.Resistor().at((xo, yd)).to((xp, yd)))
    wire(d, [(xo, 0), (xo, yd)])
    txt(axc, (xo + xp) / 2, yd - 0.4, r"$R_1$ 10 kΩ", va="top", fs=8)
    dot(d, (xp, yd))
    d.add(elm.Resistor().at((xp, yd)).to((xp, yd - 2.2)))
    gnd(d, (xp, yd - 2.2))
    txt(axc, xp - 0.35, yd - 1.1, r"$R_2$" + "\n10 kΩ", ha="right", fs=8)
    wire(d, [(xo, 0), (xo + 0.8, 0)])
    dot(d, (xo + 0.8, 0), open_=True)
    txt(axc, xo + 0.9, 0.25, r"$v_o$", ha="left", va="bottom", fs=9, color=BLUE)
    txt(axc, 2.6, yd - 3.3, "rail-to-rail, ±5 V\n" + r"$\beta=R_2/(R_1+R_2)=0.5$", fs=7.5, color=GREY)
    finish(axc, d, full=False)
    tm = t * 1e3
    axp.plot(tm, vo, color=BLUE, lw=1.4, label=r"$v_o$")
    axp.plot(tm, vc, color=ORANGE, lw=1.6, label=r"$v_C$")
    for y in (2.5, -2.5):
        axp.axhline(y, color=GREY, ls="--", lw=0.8)
    txt(axp, 3.02, 2.5, "+2.5 V", ha="left", fs=7.2, color=GREY)
    txt(axp, 3.02, -2.5, "−2.5 V", ha="left", fs=7.2, color=GREY)
    e1, e2, e3 = edges[0] * 1e3, edges[1] * 1e3, edges[2] * 1e3
    axp.annotate("", xy=(e2, 5.7), xytext=(e1, 5.7),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    txt(axp, (e1 + e2) / 2, 5.85, f"T/2 = {T/2*1e3:.3f} ms", va="bottom", fs=7.5)
    axp.annotate("", xy=(e3, -5.9), xytext=(e1, -5.9),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    txt(axp, (e1 + e3) / 2, -6.05, f"T = {T*1e3:.3f} ms  (f = {1/T:.0f} Hz)", va="top", fs=7.5)
    axp.set_xlim(0, 3)
    axp.set_ylim(-7.4, 7.2)
    axp.set_xlabel("time (ms)")
    axp.set_ylabel("voltage (V)")
    axp.legend(loc="upper right", fontsize=7.5, ncol=2, bbox_to_anchor=(1.0, 0.93))
    save(fig, "08", "fig-8-6-relaxation-oscillator")


if __name__ == "__main__":
    fig_8_1()
    fig_8_2()
    fig_8_3()
    fig_8_4()
    fig_8_5()
    fig_8_6()
