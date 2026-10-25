"""Figures for Chapter 30 — DC–DC Converters.

Run from the repository root:  python figures/scripts/ch30.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, save, schematic  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def drawing(ax, fontsize=7.5, lw=1.1, unit=1.6):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=fontsize, lw=lw, unit=unit)
    return d


def finish(ax, d, pad=0.3, xlim=None, ylim=None):
    d.draw(show=False)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.autoscale_view()
    if xlim is None:
        x0, x1 = ax.get_xlim()
        xlim = (x0 - pad, x1 + pad)
    if ylim is None:
        y0, y1 = ax.get_ylim()
        ylim = (y0 - pad, y1 + pad)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def wire(d, pts, **kw):
    for p, q in zip(pts[:-1], pts[1:]):
        d.add(elm.Line(**kw).at(p).to(q))


def dot(d, p):
    d.add(elm.Dot().at(p))


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False):
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0,
                                mutation_scale=10))


def tri_wave(t, Ts, D, i_lo, i_hi):
    """Triangular inductor current: rises during D*Ts, falls during the rest."""
    ph = (t % Ts) / Ts
    up = i_lo + (i_hi - i_lo) * ph / D
    dn = i_hi - (i_hi - i_lo) * (ph - D) / (1 - D)
    return np.where(ph < D, up, dn), ph < D


def cap_ripple(t, i_c, C, esr):
    """Output-voltage ripple from capacitor current (zero-mean integral) plus ESR drop."""
    dt = t[1] - t[0]
    q = np.cumsum(i_c - i_c.mean()) * dt / C
    q -= q.mean()
    return q + esr * (i_c - i_c.mean())


# ----------------------------------------------------------------------------
# Figure 30.1 — synchronous buck and its waveforms
# ----------------------------------------------------------------------------
def draw_buck(ax):
    d = drawing(ax, fontsize=7.0, unit=1.6)
    top, bot = 6.0, 0.0
    d.add(elm.SourceV().at((-3.0, bot)).to((-3.0, top)).label("12 V", loc="top", ofst=0.15))
    wire(d, [(-3.0, top), (2.4, top)])
    wire(d, [(-3.0, bot), (11.6, bot)])
    d.add(elm.Capacitor().at((0.0, top)).to((0.0, bot)).label("$C_{in}$\n2×10 µF\n(≈12 µF)", loc="top", ofst=0.1))
    dot(d, (0.0, top))
    dot(d, (0.0, bot))
    xs = 2.4
    q1 = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xs, 4.5)))
    q2 = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xs, 1.5)))
    wire(d, [q1.drain, (xs, top)])
    wire(d, [q1.source, (xs, 3.0)])
    wire(d, [(xs, 3.0), q2.drain])
    wire(d, [q2.source, (xs, bot)])
    ax.text(xs + 0.15, 4.9, "HS\n8 mΩ", fontsize=6.6, ha="left", va="center")
    ax.text(xs + 0.15, 1.9, "LS\n4 mΩ", fontsize=6.6, ha="left", va="center")
    dot(d, (xs, 3.0))
    ax.text(xs + 0.15, 2.85, "SW", fontsize=6.8, ha="left", va="top")
    wire(d, [(xs, 3.0), (3.8, 3.0)])
    d.add(elm.Inductor2(loops=3).at((3.8, 3.0)).to((5.8, 3.0)).label("3.3 µH\nDCR 8 mΩ", loc="top", ofst=0.05))
    wire(d, [(5.8, 3.0), (11.6, 3.0)])
    d.add(elm.Capacitor().at((7.4, 3.0)).to((7.4, bot))
          .label("$C_{out}$ 3×47 µF\n≈90 µF eff.,\n1 mΩ ESR", loc="top", ofst=0.1))
    d.add(elm.Resistor().at((9.6, 3.0)).to((9.6, bot)).label("load\n0.66 Ω", loc="bottom", ofst=0.08))
    d.add(elm.Resistor().at((11.6, 3.0)).to((11.6, 1.5)).scale(0.75))
    d.add(elm.Resistor().at((11.6, 1.5)).to((11.6, bot)).scale(0.75))
    for p in ((7.4, 3.0), (9.6, 3.0), (7.4, bot), (9.6, bot), (11.6, 1.5)):
        dot(d, p)
    wire(d, [(11.6, 1.5), (12.2, 1.5)])
    ax.text(12.25, 1.5, "FB\n0.6 V", fontsize=6.6, ha="left", va="center")
    ax.text(10.6, 3.2, "$V_o$ = 3.3 V", fontsize=7, ha="center", va="bottom")
    finish(ax, d, pad=0.2)


def fig_30_1():
    Vin, Vo, Io, f, L = 12.0, 3.3, 5.0, 500e3, 3.3e-6
    D, Ts = Vo / Vin, 1 / f
    dI = (Vin - Vo) * D / (f * L)
    td, n = 20e-9, 20000
    t = np.linspace(0, 2 * Ts, n, endpoint=False)
    iL, on = tri_wave(t, Ts, D, Io - dI / 2, Io + dI / 2)
    ph = (t % Ts)
    vsw = np.where(on, Vin, -iL * 5.2e-3)
    dead = (ph >= D * Ts) & (ph < D * Ts + td) | (ph >= Ts - td)
    vsw = np.where(dead, -0.8, vsw)
    ihs = np.where(on, iL, 0.0)
    icin = ihs - D * Io
    vout = Vo + cap_ripple(t, iL - Io, 90e-6, 1e-3)
    fig = plt.figure(figsize=(6.8, 5.0))
    axc = fig.add_axes([0.02, 0.69, 0.75, 0.31])
    draw_buck(axc)
    axc.text(0.02, 1.02, "(a)", transform=axc.transAxes, fontsize=9, weight="bold")
    tu = t * 1e6
    sigs = [("$v_{SW}$ (V)", vsw, BLUE), ("$i_L$ (A)", iL, ORANGE), ("$i_{HS}$ (A)", ihs, GREEN),
            ("$i_{Cin}$ (A)", icin, PINK), ("$v_{out}$ (V)", vout, BLUE)]
    axs = []
    h, y0 = 0.105, 0.075
    for k, (lab, y, c) in enumerate(sigs):
        ax = fig.add_axes([0.12, y0 + (4 - k) * (h + 0.01), 0.86, h], sharex=axs[0] if axs else None)
        ax.plot(tu, y, color=c, lw=1.3)
        ax.set_ylabel(lab, fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, color=GRID, lw=0.5)
        if k < 4:
            ax.tick_params(labelbottom=False)
        axs.append(ax)
    axs[0].set_title("(b) steady-state CCM waveforms", fontsize=8.5, loc="left", weight="bold")
    axs[0].set_ylim(-2, 14)
    axs[0].set_yticks([0, 12])
    axs[0].annotate("", xy=(D * Ts * 1e6, 13.2), xytext=(0, 13.2),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=INK, mutation_scale=7))
    axs[0].text(D * Ts * 1e6 + 0.05, 13.2, "$DT_s$ = 0.55 µs", fontsize=6.8, va="center")
    axs[0].annotate("", xy=(2.0, 6.0), xytext=(0, 6.0),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=GREY, mutation_scale=7))
    axs[0].text(1.25, 6.4, "$T_s$ = 2 µs", fontsize=6.8, va="bottom", color=GREY)
    axs[0].text(3.98, 1.2, "dead time −0.8 V", fontsize=6.4, ha="right", va="bottom", color=GREY)
    axs[1].set_ylim(4.0, 6.0)
    axs[1].set_yticks([4.275, 5.725])
    axs[1].set_yticklabels(["4.275", "5.725"])
    axs[1].text(0.02, 5.55, "+2.64 A/µs", fontsize=6.6, color=ORANGE, rotation=0)
    axs[1].text(1.0, 5.3, "−1.0 A/µs", fontsize=6.6, color=ORANGE)
    axs[2].set_ylim(-0.5, 6.5)
    axs[2].set_yticks([0, 5])
    axs[3].set_ylim(-2.2, 5.2)
    axs[3].set_yticks([-1.375, 0, 3.625])
    axs[3].set_yticklabels(["−1.4", "0", "+3.6"])
    rms = np.sqrt(np.mean(icin ** 2))
    axs[3].text(3.98, 4.2, f"rms {rms:.2f} A", fontsize=6.6, ha="right", va="center", color=PINK)
    pp = (vout.max() - vout.min()) * 1e3
    axs[4].set_ylim(Vo - 0.0045, Vo + 0.0045)
    axs[4].set_yticks([Vo - 0.0025, Vo, Vo + 0.0025])
    axs[4].set_yticklabels(["3.2975", "3.3000", "3.3025"])
    axs[4].text(3.98, Vo + 0.0036, f"ripple {pp:.1f} mV p-p (C arcs + ESR triangle)", fontsize=6.4,
                ha="right", va="center")
    axs[4].set_xlim(0, 4)
    axs[4].set_xlabel("time (µs)", fontsize=8)
    fig.align_ylabels(axs)
    print(f"  30.1: Cin rms {rms:.2f} A, vout ripple {pp:.2f} mV")
    save(fig, "30", "fig-30-1-buck-waveforms")


# ----------------------------------------------------------------------------
# Figure 30.2 — boost and inverting buck-boost
# ----------------------------------------------------------------------------
def draw_boost(ax):
    d = drawing(ax, fontsize=7.0, unit=1.5)
    top, bot = 4.0, 0.0
    d.add(elm.BatteryCell().at((0, bot)).to((0, top)).label("Li-ion\n3.0–4.2 V", loc="top", ofst=0.15))
    d.add(elm.Inductor2(loops=3).at((0, top)).to((2.0, top)).label("1.0 µH", loc="top", ofst=0.05))
    xs = 2.6
    wire(d, [(2.0, top), (xs, top)])
    dot(d, (xs, top))
    q = d.add(elm.NFet().theta(0).reverse().anchor("drain").at((xs, top - 0.6)))
    wire(d, [(xs, top), q.drain])
    wire(d, [q.source, (xs, bot)])
    ax.text(xs + 0.15, q.source[1] + 0.2, "S", fontsize=6.8, ha="left")
    q2 = d.add(elm.NFet().theta(-90).reverse().anchor("source").at((xs + 0.4, top)))
    wire(d, [(xs, top), q2.source])
    ax.text(q2.gate[0], q2.gate[1] + 0.1, "sync. rect.", fontsize=6.4, ha="center", va="bottom")
    wire(d, [q2.drain, (6.6, top)])
    d.add(elm.Capacitor().at((5.0, top)).to((5.0, bot)).label("44 µF\neff.", loc="top", ofst=0.08))
    d.add(elm.Resistor().at((6.6, top)).to((6.6, bot)).label("2.08 Ω", loc="bottom", ofst=0.08))
    wire(d, [(0, bot), (6.6, bot)])
    for p in ((5.0, top), (5.0, bot), (xs, bot)):
        dot(d, p)
    ax.text(6.6, top + 0.2, "5.0 V", fontsize=7, ha="center", va="bottom")
    ax.text(xs - 0.1, top + 0.15, "SW", fontsize=6.6, ha="right", va="bottom")
    finish(ax, d, pad=0.2)


def draw_buckboost(ax):
    d = drawing(ax, fontsize=7.0, unit=1.5)
    top, bot = 4.0, 0.0
    d.add(elm.SourceV().at((0, bot)).to((0, top)).label("12 V", loc="top", ofst=0.15))
    q = d.add(elm.NFet().theta(90).anchor("drain").at((0.6, top)))
    wire(d, [(0, top), q.drain])
    ax.text(q.gate[0], q.gate[1] + 0.1, "S (high side)", fontsize=6.4, ha="center", va="bottom")
    xn = q.source[0] + 0.5
    wire(d, [q.source, (xn, top)])
    dot(d, (xn, top))
    ax.text(xn, top - 0.25, "SW", fontsize=6.6, ha="left", va="top")
    d.add(elm.Inductor2(loops=3).at((xn, top)).to((xn, bot)).label("L", loc="bottom", ofst=0.1))
    d.add(elm.Diode().at((xn + 2.0, top)).to((xn, top)).label("rect.", loc="top", ofst=0.05))
    d.add(elm.Capacitor().at((xn + 2.6, bot)).to((xn + 2.6, top)).label("$C_o$", loc="bottom", ofst=0.08))
    d.add(elm.Resistor().at((xn + 4.0, bot)).to((xn + 4.0, top)).label("5 Ω", loc="bottom", ofst=0.08))
    wire(d, [(xn + 2.0, top), (xn + 4.0, top)])
    wire(d, [(0, bot), (xn + 4.0, bot)])
    for p in ((xn, bot), (xn + 2.6, top), (xn + 2.6, bot)):
        dot(d, p)
    ax.text(xn + 4.0, top + 0.2, "−5 V", fontsize=7, ha="center", va="bottom")
    finish(ax, d, pad=0.2)


def fig_30_2():
    fig = plt.figure(figsize=(6.8, 5.0))
    # ---- boost ----
    Vin, Vo, Io, f, L, C, esr = 3.0, 5.0, 2.4, 1e6, 1e-6, 44e-6, 2e-3
    D, Ts = 1 - Vin / Vo, 1 / f
    IL = Io / (1 - D)
    dI = Vin * D / (f * L)
    t = np.linspace(0, 2 * Ts, 8000, endpoint=False)
    iL, on = tri_wave(t, Ts, D, IL - dI / 2, IL + dI / 2)
    vsw = np.where(on, 0.0, Vo)
    irect = np.where(on, 0.0, iL)
    vout = Vo + cap_ripple(t, irect - Io, C, esr)
    axc = fig.add_axes([0.0, 0.56, 0.36, 0.36])
    draw_boost(axc)
    axc.text(0.0, 1.12, "(a) boost 3.0 V → 5.0 V, 2.4 A, 1 MHz, D = 0.4", transform=axc.transAxes,
             fontsize=8, weight="bold")
    tu = t * 1e6
    sig = [("$v_{SW}$ (V)", vsw, BLUE, (-0.6, 6), [0, 5]), ("$i_L$ (A)", iL, ORANGE, (3.0, 5.0), [3.4, 4.6]),
           ("$i_{rect}$ (A)", irect, GREEN, (-0.5, 5.2), [0, 3.4, 4.6]),
           ("$v_{out}$ (mV)", (vout - Vo) * 1e3, BLUE, (-22, 22), [-15, 0, 15])]
    axs = []
    h = 0.098
    for k, (lab, y, c, yl, yt) in enumerate(sig):
        ax = fig.add_axes([0.47, 0.545 + (3 - k) * (h + 0.012), 0.51, h], sharex=axs[0] if axs else None)
        ax.plot(tu, y, color=c, lw=1.3)
        ax.set_ylim(*yl)
        ax.set_yticks(yt)
        ax.set_ylabel(lab, fontsize=7.5)
        ax.tick_params(labelsize=6.8)
        ax.grid(True, color=GRID, lw=0.5)
        if k < 3:
            ax.tick_params(labelbottom=False)
        axs.append(ax)
    pp = vout.max() - vout.min()
    axs[3].text(1.98, 17, f"{pp*1e3:.0f} mV p-p: capacitive {Io*D/(f*C)*1e3:.1f} mV + ESR steps "
                f"{(IL+dI/2)*esr*1e3:.1f} mV", fontsize=6.2, ha="right", va="center")
    axs[0].text(0.2, 3.0, "on 0.4 µs", fontsize=6.4, ha="center", va="center", color=GREY)
    axs[3].set_xlim(0, 2)
    axs[3].set_xlabel("time (µs)", fontsize=7.5)
    fig.align_ylabels(axs)
    print(f"  30.2a: boost ripple {pp*1e3:.1f} mV p-p")
    # ---- buck-boost ----
    Vin, Vo, Io = 12.0, -5.0, 1.0
    D = abs(Vo) / (Vin + abs(Vo))
    IL = Io / (1 - D)
    f, L = 500e3, 10e-6           # assumed for the sketch (not specified in the text)
    Ts = 1 / f
    dI = Vin * D / (f * L)
    t = np.linspace(0, 2 * Ts, 8000, endpoint=False)
    iL, on = tri_wave(t, Ts, D, IL - dI / 2, IL + dI / 2)
    vsw = np.where(on, Vin, Vo)
    axc2 = fig.add_axes([0.0, 0.05, 0.36, 0.33])
    draw_buckboost(axc2)
    axc2.text(0.0, 1.12, "(b) inverting buck–boost 12 V → −5 V, 1 A, D = 0.294", transform=axc2.transAxes,
              fontsize=8, weight="bold")
    tu = t * 1e6
    a1 = fig.add_axes([0.47, 0.235, 0.51, 0.13])
    a2 = fig.add_axes([0.47, 0.085, 0.51, 0.13], sharex=a1)
    a1.plot(tu, vsw, color=BLUE, lw=1.3)
    a1.set_ylim(-8, 15)
    a1.set_yticks([-5, 0, 12])
    a1.set_ylabel("$v_{SW}$ (V)", fontsize=7.5)
    a1.tick_params(labelbottom=False, labelsize=6.8)
    a1.axhline(0, color=GREY, lw=0.6)
    a2.plot(tu, iL, color=ORANGE, lw=1.3)
    a2.axhline(IL, color=ORANGE, lw=0.8, ls="--")
    a2.text(3.95, IL + 0.05, f"average {IL:.2f} A", fontsize=6.6, ha="right", va="bottom", color=ORANGE)
    a2.set_ylim(0.8, 2.0)
    a2.set_yticks([1.0, 1.42, 1.8])
    a2.set_ylabel("$i_L$ (A)", fontsize=7.5)
    a2.tick_params(labelsize=6.8)
    a2.set_xlim(0, 4)
    a2.set_xlabel("time (µs)  [sketch at 500 kHz, L = 10 µH]", fontsize=7.5)
    for a in (a1, a2):
        a.grid(True, color=GRID, lw=0.5)
    fig.align_ylabels([a1, a2])
    save(fig, "30", "fig-30-2-boost-buckboost")


# ----------------------------------------------------------------------------
# Figure 30.3 — buck conversion ratio in CCM and DCM
# ----------------------------------------------------------------------------
def fig_30_3():
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    Dg = np.linspace(1e-3, 1, 1000)
    ax.plot(Dg, Dg, color=INK, lw=1.8, label="CCM: M = D (K ≥ 1)")
    for K, c in ((0.3, BLUE), (0.05, ORANGE)):
        Db = 1 - K
        Dd = Dg[Dg <= Db]
        M = 2 / (1 + np.sqrt(1 + 4 * K / Dd ** 2))
        ax.plot(Dd, M, color=c, lw=1.8, label=f"DCM, K = {K}")
        ax.plot([Db], [Db], "o", color=c, ms=5, mfc="white", mew=1.4)
        ax.annotate(f"joins CCM at\nD = 1 − K = {Db:.2f}", xy=(Db, Db),
                    xytext=(Db - 0.27 if K == 0.3 else Db - 0.17, Db + 0.12 if K == 0.3 else Db + 0.02),
                    fontsize=7.4, color=c, ha="center",
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.7))
    # CCM region below the line is unreachable; shade DCM region description
    ax.plot(0.177, 0.275, "s", color=BLUE, ms=6, zorder=5)
    ax.plot(0.275, 0.275, "s", color=INK, ms=6, mfc="white", zorder=5)
    ax.annotate("", xy=(0.185, 0.275), xytext=(0.267, 0.275),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9, mutation_scale=8))
    ax.annotate("DCM: D = 0.177\n(3.3 V buck at 0.3 A)", xy=(0.177, 0.27), xytext=(0.16, 0.05),
                fontsize=7.4, color=BLUE, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.text(0.29, 0.245, "CCM: D = 0.275", fontsize=7.4, ha="left", va="top")
    ax.axhline(0.275, color=GREY, lw=0.6, ls=":")
    ax.text(0.98, 0.285, "M = 3.3/12 = 0.275", fontsize=7, color=GREY, ha="right", va="bottom")
    ax.text(0.55, 0.12, "CCM/DCM boundary: K = K$_{crit}$ = 1 − D\n(DCM for D < 1 − K; above it the\n"
            "curve joins the CCM line)", fontsize=7.2, color=GREY, ha="left")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("duty cycle D")
    ax.set_ylabel("conversion ratio M = $V_o/V_{in}$")
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=7.6)
    ax.text(0.98, 0.02, "K = 2L/(R $T_s$)", fontsize=7.4, ha="right", va="bottom")
    save(fig, "30", "fig-30-3-ccm-dcm-ratio")


# ----------------------------------------------------------------------------
# Figure 30.4 — efficiency and loss breakdown versus load
# ----------------------------------------------------------------------------
VIN, VO, F = 12.0, 3.3, 500e3
D_B = VO / VIN
DI_B = (VIN - VO) * D_B / (F * 3.3e-6)


def buck_losses(I):
    """Loss budget of the chapter's listing (W), forced PWM."""
    dI = DI_B
    D = D_B
    i2 = I ** 2 + dI ** 2 / 12
    i_v, i_p = I - dI / 2, I + dI / 2
    return {
        "HS conduction": D * i2 * 10.5e-3,
        "LS conduction": (1 - D) * i2 * 5.2e-3,
        "HS overlap": 0.5 * VIN * (max(i_v, 0) * 3.75e-9 + i_p * 2.31e-9) * F,
        "Coss": 0.5 * 1.0e-9 * VIN ** 2 * F,
        "dead time": 0.8 * (abs(i_v) + i_p) * 20e-9 * F,
        "LS Qrr": 15e-9 * VIN * F,
        "gate drive": 26e-9 * 5.0 * F,
        "L copper": i2 * 8e-3,
        "L core": 0.10,
        "caps + PCB": (I * math.sqrt(D * (1 - D))) ** 2 * 3e-3 + i2 * 3e-3,
        "controller": VIN * 2e-3,
    }


GROUPS = {
    "fixed (gate, $C_{oss}$, $Q_{rr}$, core, controller)": ["gate drive", "Coss", "LS Qrr", "L core", "controller"],
    "∝ I (overlap, dead time)": ["HS overlap", "dead time"],
    "∝ I² (conduction, copper, caps, PCB)": ["HS conduction", "LS conduction", "L copper", "caps + PCB"],
}
FSW_TERMS = ["HS overlap", "Coss", "dead time", "LS Qrr", "gate drive", "L core"]


def pfm_loss(I, Ib=DI_B / 2):
    """Light-load PFM model: frequency-proportional losses scaled by f_eff/f, where f_eff/f
    falls from 1 at the DCM boundary to 0.1 at 0.2 A (the tenfold cut of the worked example);
    conduction without the circulating forced-CCM ripple. Above the boundary: forced PWM."""
    if I >= Ib:
        return sum(buck_losses(I).values())
    k = math.log(0.1) / math.log(0.2 / Ib)
    r = (I / Ib) ** k
    L = buck_losses(I)
    p_sw = sum(L[n] for n in FSW_TERMS) * r
    rc = 10.5e-3 * D_B + 5.2e-3 * (1 - D_B) + 8e-3 + 3e-3
    p_cond = 1.3 * I ** 2 * rc
    return p_sw + p_cond + L["controller"]


def fig_30_4():
    I = np.logspace(-1, math.log10(5), 300)
    eta = np.array([VO * i / (VO * i + sum(buck_losses(i).values())) for i in I]) * 100
    eta_pfm = np.array([VO * i / (VO * i + pfm_loss(i)) for i in I]) * 100
    fig = plt.figure(figsize=(6.4, 5.0))
    ax = fig.add_axes([0.11, 0.47, 0.85, 0.48])
    ax.semilogx(I, eta, color=BLUE, lw=1.8, label="forced PWM (CCM) at 500 kHz")
    ax.semilogx(I, eta_pfm, color=ORANGE, lw=1.8, ls="--", label="with light-load PFM mode")
    pts = [0.2, 0.5, 1, 2, 5]
    for p in pts:
        e = VO * p / (VO * p + sum(buck_losses(p).values())) * 100
        ax.plot(p, e, "o", color=BLUE, ms=4)
        ax.text(p * (0.95 if p == 5 else 1.05), e - 1.2, f"{e:.1f} %", fontsize=7.2, color=BLUE, va="top",
                ha="right" if p == 5 else "left")
    k = np.argmax(eta)
    ax.plot(I[k], eta[k], "^", color=BLUE, ms=5)
    ax.text(I[k] * 0.9, eta[k] + 1.6, f"peak {eta[k]:.1f} % at {I[k]:.1f} A", fontsize=7.2, ha="center",
            va="bottom", color=BLUE)
    e_p = VO * 0.2 / (VO * 0.2 + pfm_loss(0.2)) * 100
    ax.plot(0.2, e_p, "o", color=ORANGE, ms=4)
    ax.text(0.21, e_p + 1.0, f"{e_p:.0f} % (PFM)", fontsize=7.2, color=ORANGE, va="bottom")
    ax.axvline(DI_B / 2, color=GREY, lw=0.8, ls=":")
    ax.text(DI_B / 2 * 1.04, 55, "DCM boundary\n0.725 A", fontsize=7.2, color=GREY, va="bottom")
    ax.set_xlim(0.1, 5)
    ax.set_ylim(50, 100)
    ax.set_ylabel("efficiency (%)")
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5])
    ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.grid(True, which="both", color=GRID, lw=0.5)
    ax.legend(loc="lower right", fontsize=7.6)
    ax.set_xlabel("load current (A)", fontsize=9)
    # stacked bars
    axb = fig.add_axes([0.11, 0.07, 0.85, 0.29])
    loads = [0.2, 1, 2, 5]
    xpos = np.arange(len(loads))
    bottom = np.zeros(len(loads))
    cols = [SKY, YELLOW, PINK]
    for (gname, members), c in zip(GROUPS.items(), cols):
        vals = np.array([sum(buck_losses(i)[m] for m in members) for i in loads])
        axb.bar(xpos, vals, 0.55, bottom=bottom, color=c, label=gname, edgecolor="white", lw=0.5)
        for x, v, b in zip(xpos, vals, bottom):
            if v > 0.04:
                axb.text(x, b + v / 2, f"{v:.2f}", ha="center", va="center", fontsize=6.8)
        bottom += vals
    for x, b in zip(xpos, bottom):
        axb.text(x, b + 0.02, f"{b:.3f} W", ha="center", va="bottom", fontsize=7.2)
    axb.set_xticks(xpos)
    axb.set_xticklabels([f"{i:g} A" for i in loads])
    axb.set_ylabel("loss (W)")
    axb.set_ylim(0, 1.15)
    axb.set_xlim(-0.5, 5.6)
    axb.legend(loc="center right", fontsize=7.0, bbox_to_anchor=(1.0, 0.55))
    axb.set_title("loss breakdown in forced PWM", fontsize=8.5, loc="left")
    save(fig, "30", "fig-30-4-efficiency-vs-load")


# ----------------------------------------------------------------------------
# Figure 30.5 — voltage-mode control loop
# ----------------------------------------------------------------------------
def fig_30_5():
    fig, ax = schematic(6.8, 4.4, xlim=(0, 18), ylim=(0, 11.6))
    fs = 7.4
    yc = 7.6
    # reference and summing junction
    ax.text(0.1, yc, "$V_{ref}$\n0.6 V", fontsize=fs, ha="left", va="center")
    line(ax, [(1.1, yc), (1.75, yc)], arrow_end=True)
    ax.add_patch(Circle((2.1, yc), 0.35, fc="white", ec=INK, lw=1.1))
    ax.text(1.85, yc + 0.5, "+", fontsize=8, ha="center")
    ax.text(2.45, yc - 0.8, "−", fontsize=9, ha="center")
    line(ax, [(2.45, yc), (2.9, yc)], arrow_end=True)
    box(ax, 2.9, yc - 1.15, 3.9, 2.3, "error amplifier, Type III\n$G_c(s)$: integrator,\n2 zeros at 7.4 kHz,\n"
        "2 poles at 250 kHz", fc="#E3F1E8", fontsize=6.4)
    line(ax, [(6.8, yc), (7.5, yc)], arrow_end=True)
    ax.text(7.15, yc + 0.15, "$v_c$", fontsize=fs, ha="center", va="bottom")
    box(ax, 7.5, yc - 0.85, 2.1, 1.7, "PWM\n$1/V_{ramp}$\n$V_{ramp}$ = 1 V", fc="#FBEFC9", fontsize=6.4)
    line(ax, [(9.6, yc), (10.2, yc)], arrow_end=True)
    ax.text(9.9, yc + 0.15, "$\\hat d$", fontsize=fs, ha="center", va="bottom")
    box(ax, 10.2, yc - 1.3, 4.9, 2.6, "power stage $G_{vd}(s)$\ngain $V_{in}$ = 12 V; LC filter\n"
        "L = 3.3 µH, C = 90 µF,\nESR 1 mΩ, load 0.66 Ω", fc="#DCEFFA", fontsize=6.4)
    line(ax, [(15.1, yc), (17.3, yc)], arrow_end=True)
    ax.text(17.4, yc, "$v_o$", fontsize=8.5, va="center")
    ax.plot(15.9, yc, "o", color=INK, ms=3.5)
    # disturbances
    line(ax, [(12.65, 10.6), (12.65, yc + 1.3)], arrow_end=True)
    ax.text(12.8, 10.4, "$\\hat v_{in}$ (line)", fontsize=fs, ha="left", va="center")
    line(ax, [(16.7, 10.6), (16.7, yc + 0.08)], arrow_end=True)
    ax.text(16.6, 10.9, "$\\hat i_o$ (load step)", fontsize=fs, ha="center", va="bottom")
    # feedback path with injection resistor
    yf = 4.4
    line(ax, [(15.9, yc), (15.9, yf), (14.6, yf)])
    ax.add_patch(Rectangle((13.4, yf - 0.25), 1.2, 0.5, fc="white", ec=INK, lw=1.0))
    ax.text(14.0, yf - 0.4, "20 Ω", fontsize=6.6, ha="center", va="top")
    line(ax, [(13.4, yf), (11.2, yf)])
    box(ax, 9.0, yf - 0.75, 2.2, 1.5, "divider\nH = 0.6/3.3\n= 0.182", fc="#EEEEEE", fontsize=6.4)
    line(ax, [(9.0, yf), (2.1, yf), (2.1, yc - 0.35)], arrow_end=True)
    # injection source and analyser channels
    ax.add_patch(Circle((14.0, yf + 1.15), 0.32, fc="white", ec=PINK, lw=1.1))
    ax.text(14.0, yf + 1.15, "~", fontsize=9, ha="center", va="center", color=PINK)
    line(ax, [(13.68, yf + 1.15), (13.4, yf + 1.15), (13.4, yf)], color=PINK)
    line(ax, [(14.32, yf + 1.15), (14.6, yf + 1.15), (14.6, yf)], color=PINK)
    ax.plot([13.25, 14.75], [yf, yf], "o", color=PINK, ms=3)
    ax.text(13.0, yf - 0.7, "A", fontsize=7.5, color=PINK, weight="bold", ha="center")
    ax.text(15.0, yf - 0.7, "B", fontsize=7.5, color=PINK, weight="bold", ha="center")
    ax.text(14.0, yf - 1.05, "injection for loop-gain\nmeasurement: T = B/A", fontsize=6.4, color=PINK,
            ha="center", va="top")
    ax.text(5.5, yf + 0.15, "feedback", fontsize=6.6, color=GREY, ha="center", va="bottom")
    # digital alternative
    yd = 1.2
    ax.add_patch(FancyBboxPatch((0.6, yd - 0.95), 16.8, 1.9, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="white", ec=GREY, lw=1.0, ls=(0, (4, 2))))
    ax.text(0.8, yd + 0.65, "digital alternative", fontsize=7, color=GREY, style="italic", va="bottom")
    for x, w, t_ in ((1.4, 3.0, "ADC, sampled\nonce per period"), (5.2, 3.4, "3p3z compensator\nin the MCU"),
                     (9.4, 2.8, "digital PWM\n(next period)")):
        box(ax, x, yd - 0.55, w, 1.1, t_, fc="#F4F4F4", fontsize=6.4)
    line(ax, [(4.4, yd), (5.2, yd)], arrow_end=True)
    line(ax, [(8.6, yd), (9.4, yd)], arrow_end=True)
    ax.text(12.6, yd, "total delay ≈ 1.5 $T_s$:\n54° of lag at $f_c = f_s/10$", fontsize=6.6, color=RED,
            ha="left", va="center")
    save(fig, "30", "fig-30-5-control-block-diagram")


# ----------------------------------------------------------------------------
# Figure 30.6 — Bode plots of plant, compensator and loop gain
# ----------------------------------------------------------------------------
def fig_30_6():
    Vin, Vramp, L, C, esr, R = 12.0, 1.0, 3.3e-6, 90e-6, 1e-3, 0.66
    H = 0.6 / 3.3
    fsw, fc = 500e3, 50e3
    f0 = 1 / (2 * np.pi * np.sqrt(L * C))

    def s(f):
        return 2j * np.pi * f

    def Gvd(f):
        x = s(f)
        return Vin * (1 + x * C * esr) / (1 + x * (L / R + C * esr) + x ** 2 * L * C)

    fz1 = fz2 = 0.8 * f0
    fp1 = fp2 = fsw / 2

    def Gc(f, k=1.0):
        x = s(f)
        return k * (1 + x / (2 * np.pi * fz1)) * (1 + x / (2 * np.pi * fz2)) / (
            x * (1 + x / (2 * np.pi * fp1)) * (1 + x / (2 * np.pi * fp2)))

    k = 1 / abs(Gc(fc) * Gvd(fc) * H / Vramp)
    f = np.logspace(2, 6, 4001)
    G, K = Gvd(f), Gc(f, k)
    T = K * G * H / Vramp
    ic = np.argmin(abs(abs(T) - 1))
    ph_T = np.unwrap(np.angle(T))
    pm = 180 + np.degrees(ph_T[ic])
    i180 = np.argmin(abs(ph_T + np.pi))
    gm = -20 * np.log10(abs(T[i180]))
    fig, (am, ap) = plt.subplots(2, 1, figsize=(6.4, 5.0), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1.15, 1], hspace=0.08))
    db = lambda z: 20 * np.log10(abs(z))  # noqa: E731
    am.semilogx(f, db(G), color=BLUE, lw=1.6, label="$G_{vd}$ (control-to-output)")
    am.semilogx(f, db(K), color=GREEN, lw=1.6, label="$G_c$ (Type III)")
    am.semilogx(f, db(T), color=INK, lw=2.0, label="loop gain $T$")
    am.axhline(0, color=GREY, lw=0.8)
    am.set_ylim(-60, 80)
    am.set_ylabel("magnitude (dB)")
    am.legend(loc="upper right", fontsize=7.6)
    am.grid(True, which="both", color=GRID, lw=0.4)
    kpk = np.argmax(db(G))
    am.annotate(f"+{db(G)[kpk]-db(G)[0]:.1f} dB resonance\n($Q$ = {R*np.sqrt(C/L):.2f})",
                xy=(f[kpk], db(G)[kpk]), xytext=(f[kpk] * 0.13, db(G)[kpk] + 20), fontsize=7.2, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    am.text(150, db(G)[0] + 2, f"{db(G)[0]:.1f} dB", fontsize=7.2, color=BLUE, va="bottom")
    am.text(9e4, -42, "−40 dB/dec", fontsize=7, color=BLUE)
    am.plot(fc, 0, "o", color=RED, ms=5, zorder=5)
    am.text(fc * 1.1, 3, "$f_c$ = 50 kHz", fontsize=7.4, color=RED, va="bottom")
    am.annotate("", xy=(f[i180], 0), xytext=(f[i180], db(T)[i180]),
                arrowprops=dict(arrowstyle="<|-|>", color=PINK, lw=0.9, mutation_scale=8))
    am.text(f[i180] * 1.08, db(T)[i180] / 2, f"GM\n{gm:.1f} dB", fontsize=7.2, color=PINK, va="center")
    for ax_ in (am, ap):
        for fx in (f0, fc, fsw / 2):
            ax_.axvline(fx, color=GREY, lw=0.6, ls=":")
    am.text(f0, -58, "$f_0$ 9.24 kHz", fontsize=7, ha="center", va="bottom",
            bbox=dict(fc="white", ec="none", pad=0.5))
    am.text(fsw / 2, -58, "$f_s/2$", fontsize=7, ha="center", va="bottom",
            bbox=dict(fc="white", ec="none", pad=0.5))
    ap.semilogx(f, np.degrees(np.unwrap(np.angle(G))), color=BLUE, lw=1.6)
    ap.semilogx(f, np.degrees(np.unwrap(np.angle(K))), color=GREEN, lw=1.6)
    ap.semilogx(f, np.degrees(ph_T), color=INK, lw=2.0)
    ap.axhline(-180, color=GREY, lw=0.8)
    ap.annotate("", xy=(fc, -180), xytext=(fc, np.degrees(ph_T[ic])),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.9, mutation_scale=8))
    ap.text(fc * 1.1, -150, f"PM {pm:.1f}° (∠T = {np.degrees(ph_T[ic]):.1f}°)", fontsize=7.2, color=RED,
            ha="left", va="center")
    ap.plot(f[i180], -180, "o", color=PINK, ms=4.5)
    ap.text(f[i180] * 0.95, -200, f"−180° at {f[i180]/1e3:.0f} kHz", fontsize=7.2, color=PINK, va="top", ha="right")
    ap.set_ylim(-270, 90)
    ap.set_yticks([-270, -180, -90, 0, 90])
    ap.set_ylabel("phase (°)")
    ap.set_xlabel("frequency (Hz)")
    ap.set_xlim(100, 1e6)
    ap.grid(True, which="both", color=GRID, lw=0.4)
    print(f"  30.6: PM {pm:.1f} deg, GM {gm:.1f} dB at {f[i180]/1e3:.0f} kHz")
    save(fig, "30", "fig-30-6-loop-bode")


if __name__ == "__main__":
    fig_30_1()
    fig_30_2()
    fig_30_3()
    fig_30_4()
    fig_30_5()
    fig_30_6()
