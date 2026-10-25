"""Figures for Chapter 33 — CMOS Fundamentals.

Run from the repository root:  python figures/scripts/ch33.py
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Circle, Polygon  # noqa: E402
from scipy.optimize import brentq  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

schemdraw.use("matplotlib")
warnings.filterwarnings("ignore", message=".*non-interactive.*")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
GREY = "#888888"
RED = "#C62828"


def _sd(ax, fontsize=8, unit=1.5, lw=1.1):
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=fontsize, unit=unit, lw=lw, color=INK)
    return d


def _finish(d, ax, xlim=None, ylim=None):
    d.draw(show=False)
    ax.set_aspect("equal")
    ax.axis("off")
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)


def _fet(d, kind, x, ytop, gate_left=True):
    """Vertical FET whose upper terminal is at (x, ytop); returns (gate_xy, ybottom)."""
    e = (elm.NFet() if kind == "n" else elm.PFet()).theta(0)
    if gate_left:
        e = e.reverse()
    e = e.anchor("drain" if kind == "n" else "source").at((x, ytop))
    d += e
    return e.gate, ytop - 1.5


def _vdd(d, ax, x0, x1, y):
    d += elm.Line().at((x0, y)).to((x1, y))
    ax.text(0.5 * (x0 + x1), y + 0.12, r"$V_{DD}$", fontsize=7.5, ha="center", va="bottom")


def _gnd(d, x0, x1, y):
    d += elm.Line().at((x0, y)).to((x1, y))
    d += elm.Ground().at((0.5 * (x0 + x1), y))


# ----------------------------------------------------------------------------
# Figure 33.1 — inverter VTC
# ----------------------------------------------------------------------------
VDD, VTN, VTP, LAM = 1.8, 0.45, 0.45, 0.1
KN, KP = 270e-6 * 1.0, 110e-6 * 2.0


def _ids(k, vgs, vds, vt):
    if vgs <= vt:
        return 0.0
    vov = vgs - vt
    core = k * (vov * vds - vds ** 2 / 2) if vds < vov else k / 2 * vov ** 2
    return core * (1 + LAM * vds)


def _vout(vin):
    f = lambda vo: _ids(KN, vin, vo, VTN) - _ids(KP, VDD - vin, VDD - vo, VTP)
    return brentq(f, 0.0, VDD)


def fig_33_1():
    vin = np.linspace(0.0, VDD, 3601)
    vo = np.array([VDD if v <= VTN else 0.0 if v >= VDD - VTP else _vout(v) for v in vin])
    idd = np.array([_ids(KN, v, o, VTN) for v, o in zip(vin, vo)])
    gain = np.gradient(vo, vin)
    VM = vin[np.argmin(np.abs(vo - vin))]
    idx = np.where(gain <= -1)[0]
    VIL, VIH = vin[idx[0]], vin[idx[-1]]
    VOH, VOL = np.interp(VIL, vin, vo), np.interp(VIH, vin, vo)
    # region boundaries from the saturation conditions
    nsat = vo >= vin - VTN
    psat = vo <= vin + VTP
    on = (vin > VTN) & (vin < VDD - VTP)
    both = on & nsat & psat
    c0, c1 = vin[both][0], vin[both][-1]

    fig = plt.figure(figsize=(6.8, 4.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.55, 1.6], wspace=0.22)
    axs = fig.add_subplot(gs[0])
    d = _sd(axs, fontsize=8)
    _vdd(d, axs, -0.3, 0.3, 5.0)
    axs.text(0.45, 5.12, "= 1.8 V", fontsize=7.5, ha="left", va="bottom")
    d += elm.Line().at((0, 5.0)).to((0, 4.5))
    gp, yb = _fet(d, "p", 0, 4.5)
    d += elm.Line().at((0, yb)).to((0, 2.5))
    d += elm.Line().at((0, 2.5)).to((0, 2.0))
    gn, yb2 = _fet(d, "n", 0, 2.0)
    d += elm.Line().at((0, yb2)).to((0, 0.0))
    _gnd(d, -0.3, 0.3, 0.0)
    d += elm.Line().at(gp).to((gp[0], gn[1]))
    d += elm.Line().at((gp[0], 2.5)).to((gp[0] - 0.6, 2.5))
    d += elm.Dot().at((gp[0], 2.5))
    axs.text(gp[0] - 0.7, 2.5, r"$V_{in}$", fontsize=8, ha="right", va="center")
    d += elm.Dot().at((0, 2.5))
    d += elm.Line().at((0, 2.5)).to((1.4, 2.5))
    d += elm.Capacitor().at((1.4, 2.5)).to((1.4, 0.8)).label(r"$C_L$", loc="bottom", ofst=0.1)
    d += elm.Ground().at((1.4, 0.8))
    axs.text(1.5, 2.65, r"$V_{out}$", fontsize=8, ha="left", va="bottom")
    axs.text(0.25, 3.75, r"$W_p=2W_n$", fontsize=7, ha="left", va="center")
    axs.text(0.25, 1.25, r"$W_n$", fontsize=7, ha="left", va="center")
    _finish(d, axs, xlim=(-2.6, 2.6), ylim=(-0.8, 6.0))

    ax = fig.add_subplot(gs[1])
    regions = [(0, VTN, "A", "n off\np lin"), (VTN, c0, "B", "n sat\np lin"), (c0, c1, "C", ""),
               (c1, VDD - VTP, "D", "n lin\np sat"), (VDD - VTP, VDD, "E", "n lin\np off")]
    shades = ["#F3F3F3", "#E8F0F8", "#FBE3D6", "#E8F3EC", "#F3F3F3"]
    for (a, b, nm, st), sh in zip(regions, shades):
        ax.axvspan(a, b, color=sh, lw=0, zorder=0)
        ax.text(0.5 * (a + b), 1.93, nm, ha="center", va="bottom", fontsize=8, fontweight="bold")
        if st:
            ax.text(0.5 * (a + b), 1.3, st, ha="center", va="center",
                    fontsize=6.5, color=GREY)
    ax.annotate("C: both\nsaturated", xy=(0.5 * (c0 + c1), 1.85), xytext=(0.98, 1.74), fontsize=6.5,
                color=GREY, ha="left", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.plot(vin, vo, color=BLUE, lw=2.0, label=r"$V_{out}$")
    ax.plot([0, 1.08], [0, 1.08], color=GREY, lw=0.9, ls="--")
    ax.text(1.1, 1.08, r"$V_{out}=V_{in}$", fontsize=7, color=GREY, ha="left", va="center")
    ax.plot(VM, VM, "o", color=INK, ms=4)
    ax.annotate(rf"$V_M$ = {VM:.3f} V", xy=(VM, VM), xytext=(VM + 0.12, VM + 0.08), fontsize=7.5)
    for vx, vy, nm in ((VIL, VOH, "IL"), (VIH, VOL, "IH")):
        ax.plot([vx - 0.1, vx + 0.1], [vy + 0.1, vy - 0.1], color=ORANGE, lw=1.6)
        ax.plot(vx, vy, "o", color=ORANGE, ms=3.5)
    ax.annotate(rf"$V_{{IL}}$ = {VIL:.3f} V" + "\n" + rf"($V_{{OH}}$ = {VOH:.3f} V, slope −1)", xy=(VIL, VOH),
                xytext=(0.03, 1.45), fontsize=6.8, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    ax.annotate(rf"$V_{{IH}}$ = {VIH:.3f} V" + "\n" + rf"($V_{{OL}}$ = {VOL:.3f} V, slope −1)", xy=(VIH, VOL),
                xytext=(1.79, 0.32), fontsize=6.8, color=ORANGE, ha="right",
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    # noise-margin bars
    ax.annotate("", xy=(VIL, -0.13), xytext=(0, -0.13), annotation_clip=False,
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=1.2, mutation_scale=8))
    ax.text(VIL / 2, -0.11, rf"$NM_L$ = {VIL:.3f} V", fontsize=7, color=GREEN, ha="center", va="bottom")
    ax.annotate("", xy=(VDD, -0.13), xytext=(VIH, -0.13), annotation_clip=False,
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=1.2, mutation_scale=8))
    ax.text((VIH + VDD) / 2, -0.11, rf"$NM_H$ = {VDD - VIH:.3f} V", fontsize=7, color=GREEN, ha="center",
            va="bottom")
    ax.set_xlim(0, VDD)
    ax.set_ylim(-0.2, 2.1)
    ax.set_yticks(np.arange(0, 1.81, 0.3))
    ax.set_xticks(np.arange(0, 1.81, 0.3))
    ax.set_xlabel(r"$V_{in}$ (V)")
    ax.set_ylabel(r"$V_{out}$ (V)", color=BLUE)
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(vin, idd * 1e6, color=PINK, lw=1.5)
    ax2.set_ylim(-0.2 / 2.3 * 32, 2.1 / 2.3 * 32 * 1.0)
    ax2.set_ylim(-32 * 0.2 / 2.1, 32)
    ax2.set_ylabel(r"supply current $I_{DD}$ (µA)", color=PINK)
    ax2.tick_params(axis="y", colors=PINK)
    ax2.set_yticks(range(0, 31, 5))
    kpk = np.argmax(idd)
    ax2.annotate(rf"$I_{{DD}}$ peak {idd[kpk]*1e6:.0f} µA at {vin[kpk]:.2f} V", xy=(vin[kpk], idd[kpk] * 1e6),
                 xytext=(1.13, 23.2), fontsize=6.8, color=PINK,
                 arrowprops=dict(arrowstyle="-", color=PINK, lw=0.6))
    print(f"  33.1: VM={VM:.3f} VIL={VIL:.3f} VOH={VOH:.3f} VIH={VIH:.3f} VOL={VOL:.3f} "
          f"peak gain={gain.min():.1f} Ipk={idd.max()*1e6:.1f} uA at {vin[kpk]:.3f}; C region {c0:.3f}-{c1:.3f}")
    save(fig, "33", "fig-33-1-inverter-vtc")


# ----------------------------------------------------------------------------
# Figure 33.2 — inverter delay and RC model
# ----------------------------------------------------------------------------
def fig_33_2():
    fig = plt.figure(figsize=(6.8, 4.6))
    gs = fig.add_gridspec(2, 2, width_ratios=[0.8, 1.6], height_ratios=[2.3, 1.0], wspace=0.28, hspace=0.12)
    axs = fig.add_subplot(gs[:, 0])
    d = _sd(axs, fontsize=7.5)
    _vdd(d, axs, -0.4, 0.4, 6.0)
    d += elm.Switch().at((0, 6.0)).to((0, 5.0))
    axs.text(-0.45, 5.5, "p", fontsize=7.5, ha="right", va="center", color=ORANGE)
    d += elm.Resistor().at((0, 5.0)).to((0, 3.4)).label(r"$R_p$" + "\n5.2 kΩ", loc="top", ofst=0.1)
    d += elm.Line().at((0, 3.4)).to((0, 2.6))
    d += elm.Dot().at((0, 3.0))
    d += elm.Resistor().at((0, 2.6)).to((0, 1.0)).label(r"$R_n$" + "\n4.5 kΩ", loc="top", ofst=0.1)
    d += elm.Switch().at((0, 1.0)).to((0, 0.0))
    axs.text(-0.45, 0.5, "n", fontsize=7.5, ha="right", va="center", color=BLUE)
    _gnd(d, -0.4, 0.4, 0.0)
    d += elm.Line().at((0, 3.0)).to((3.6, 3.0))
    for x, lab in ((1.2, "self"), (2.4, "fan-out"), (3.6, "wire")):
        if x < 3.6:
            d += elm.Dot().at((x, 3.0))
        d += elm.Capacitor().at((x, 3.0)).to((x, 1.7))
        d += elm.Ground().at((x, 1.7))
        axs.text(x, 0.95, lab, fontsize=6.3, ha="center", va="top")
    axs.text(2.4, 3.6, r"$C_L$ = 20 fF in total", fontsize=7, ha="center", va="bottom")
    axs.text(0.2, 3.3, "out", fontsize=7, ha="left", va="bottom")
    axs.text(1.5, 6.6, "switch model:\ninput high closes n, opens p", fontsize=6.5, ha="center", va="bottom",
             color=GREY)
    _finish(d, axs, xlim=(-1.6, 4.4), ylim=(-0.7, 7.6))

    ax = fig.add_subplot(gs[0, 1])
    axc = fig.add_subplot(gs[1, 1], sharex=ax)
    V = 1.8
    t = np.linspace(0, 800, 8001)
    tr_in = 40.0
    t_up, t_dn = 50.0, 450.0
    vin = V * (np.clip((t - t_up) / tr_in, 0, 1) - np.clip((t - t_dn) / tr_in, 0, 1))
    tauf, taur = 4.5e3 * 20e-15 * 1e12, 5.2e3 * 20e-15 * 1e12  # 90 ps, 104 ps
    t50a, t50b = t_up + tr_in / 2, t_dn + tr_in / 2
    vfall = np.where(t < t50a, V, V * np.exp(-(t - t50a) / tauf))
    v0 = V * np.exp(-(t50b - t50a) / tauf)
    vout = np.where(t >= t50b, V - (V - v0) * np.exp(-(t - t50b) / taur), vfall)
    ax.plot(t, vin, color=GREY, lw=1.4, label=r"$V_{in}$ (40 ps edges)")
    ax.plot(t, vout, color=BLUE, lw=1.9, label=r"$V_{out}$")
    for f in (0.1, 0.5, 0.9):
        ax.axhline(f * V, color=GRID, lw=0.7, ls=":", zorder=0)
    tphl = tauf * np.log(2)
    tplh = taur * np.log(2)
    y_a = 2.0
    for t0, tp, nm in ((t50a, tphl, "pHL"), (t50b, tplh, "pLH")):
        ax.annotate("", xy=(t0 + tp, y_a), xytext=(t0, y_a), annotation_clip=False,
                    arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=7))
        ax.text(t0 + tp + 8, y_a, rf"$t_{{{nm}}}$ = {tp:.0f} ps", fontsize=7, ha="left", va="center")
        ax.plot([t0, t0], [0.9, y_a], color=GREY, lw=0.5, ls=":")
        ax.plot([t0 + tp, t0 + tp], [0.9, y_a], color=GREY, lw=0.5, ls=":")
    tf1, tf2 = t50a + tauf * np.log(1 / 0.9), t50a + tauf * np.log(1 / 0.1)
    tr1, tr2 = t50b + taur * np.log((V - v0) / (V - 0.1 * V)), t50b + taur * np.log((V - v0) / (V - 0.9 * V))
    for (a, b, txt) in ((tf1, tf2, rf"$t_f$ (10–90 %) = {tf2 - tf1:.0f} ps"), (tr1, tr2, rf"$t_r$ = {tr2 - tr1:.0f} ps")):
        ax.annotate("", xy=(b, -0.15), xytext=(a, -0.15), annotation_clip=False,
                    arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=0.9, mutation_scale=7))
        ax.text(0.5 * (a + b), -0.12, txt, fontsize=7, color=ORANGE, ha="center", va="bottom")
    for tx, f in ((tf1, 0.9), (tf2, 0.1), (tr1, 0.1), (tr2, 0.9)):
        ax.plot([tx, tx], [-0.15, f * V], color=ORANGE, lw=0.5, ls=":")
    ax.text(t50a + 80, 1.05, r"$\tau_f=R_nC_L$ = 90 ps", fontsize=7, color=BLUE)
    ax.text(600, 0.55, r"$\tau_r=R_pC_L$ = 104 ps", fontsize=7, color=BLUE)
    ax.set_ylim(-0.3, 2.2)
    ax.set_ylabel("voltage")
    ax.set_yticks([0, 0.18, 0.9, 1.62, 1.8])
    ax.set_yticklabels(["0", "10 %", "50 %", "90 %", "1.8 V"])
    ax.legend(loc="center", fontsize=7, bbox_to_anchor=(0.5, 0.36))
    plt.setp(ax.get_xticklabels(), visible=False)
    # supply current during the rising output transition
    idd = np.where(t >= t50b, 20e-15 * (V - v0) / (taur * 1e-12) * np.exp(-(t - t50b) / taur), 0.0)
    axc.fill_between(t, idd * 1e3, color=PINK, alpha=0.35, lw=0)
    axc.plot(t, idd * 1e3, color=PINK, lw=1.3)
    axc.set_ylim(0, 0.42)
    axc.set_ylabel(r"$I_{DD}$ (mA)", fontsize=8)
    axc.set_xlim(0, 800)
    axc.set_xlabel("time (ps)")
    axc.text(560, 0.22, r"area = $C_LV_{DD}$ ≈ 36 fC" + "\n(charge drawn from the supply\nwhile the output rises)",
             fontsize=6.6, ha="left", va="center")
    axc.text(60, 0.22, "no supply current while\nthe output falls (n discharges $C_L$)", fontsize=6.3,
             ha="left", va="center", color=GREY)
    q = np.trapezoid(idd, t * 1e-12) * 1e15
    print(f"  33.2: tpHL={tphl:.1f} tpLH={tplh:.1f} tf={tf2-tf1:.1f} tr={tr2-tr1:.1f} Q={q:.1f} fC v0={v0:.3f}")
    save(fig, "33", "fig-33-2-inverter-delay")


# ----------------------------------------------------------------------------
# Figure 33.3 — static CMOS gates
# ----------------------------------------------------------------------------
def _wlab(ax, x, y, w, col):
    ax.text(x + 0.22, y, str(w), fontsize=7.5, color=col, ha="left", va="center", fontweight="bold")


def _glab(ax, g, txt):
    ax.text(g[0] - 0.08, g[1], txt, fontsize=7.5, ha="right", va="center")


def fig_33_3():
    fig, axs = plt.subplots(1, 5, figsize=(6.8, 2.85), gridspec_kw=dict(wspace=0.02))
    P, N = ORANGE, BLUE
    XL, YL = (-2.3, 4.6), (-2.6, 8.6)

    # inverter -------------------------------------------------------------
    ax = axs[0]
    d = _sd(ax, fontsize=7.5)
    top = 6.5
    _vdd(d, ax, -0.4, 0.4, top)
    d += elm.Line().at((0, top)).to((0, top - 0.5))
    g, y = _fet(d, "p", 0, top - 0.5); _glab(ax, g, "A"); _wlab(ax, 0, top - 1.25, 2, P)
    d += elm.Line().at((0, y)).to((0, 3.0))
    d += elm.Dot().at((0, 3.25))
    d += elm.Line().at((0, 3.25)).to((1.2, 3.25))
    ax.text(1.3, 3.25, "Y", fontsize=8, va="center")
    g, y = _fet(d, "n", 0, 3.0); _glab(ax, g, "A"); _wlab(ax, 0, 2.25, 1, N)
    d += elm.Line().at((0, y)).to((0, 0.5))
    _gnd(d, -0.4, 0.4, 0.5)
    ax.set_title("inverter", fontsize=8.5)
    _finish(d, ax, XL, YL)

    # NAND2 ----------------------------------------------------------------
    ax = axs[1]
    d = _sd(ax, fontsize=7.5)
    top = 7.5
    _vdd(d, ax, 0, 3.0, top)
    for x, nm in ((0.0, "A"), (3.0, "B")):
        d += elm.Line().at((x, top)).to((x, top - 0.3))
        g, y = _fet(d, "p", x, top - 0.3); _glab(ax, g, nm); _wlab(ax, x, top - 1.05, 2, P)
        d += elm.Line().at((x, y)).to((x, 5.3))
    d += elm.Line().at((0, 5.3)).to((3.0, 5.3))
    d += elm.Line().at((3.0, 5.3)).to((3.6, 5.3))
    ax.text(3.7, 5.3, "Y", fontsize=8, va="center")
    d += elm.Dot().at((3.0, 5.3))
    d += elm.Line().at((0, 5.3)).to((0, 4.6))
    g, y = _fet(d, "n", 0, 4.6); _glab(ax, g, "A"); _wlab(ax, 0, 3.85, 2, N)
    g, y = _fet(d, "n", 0, y); _glab(ax, g, "B"); _wlab(ax, 0, y + 0.75, 2, N)
    d += elm.Line().at((0, y)).to((0, 0.5))
    _gnd(d, -0.4, 0.4, 0.5)
    ax.set_title("NAND2", fontsize=8.5)
    _finish(d, ax, XL, YL)

    # NOR2 -----------------------------------------------------------------
    ax = axs[2]
    d = _sd(ax, fontsize=7.5)
    top = 7.5
    _vdd(d, ax, -0.4, 0.4, top)
    d += elm.Line().at((0, top)).to((0, top - 0.3))
    g, y = _fet(d, "p", 0, top - 0.3); _glab(ax, g, "A"); _wlab(ax, 0, top - 1.05, 4, P)
    g, y = _fet(d, "p", 0, y); _glab(ax, g, "B"); _wlab(ax, 0, y + 0.75, 4, P)
    d += elm.Line().at((0, y)).to((0, 3.6))
    d += elm.Line().at((0, 3.6)).to((3.0, 3.6))
    d += elm.Line().at((3.0, 3.6)).to((3.6, 3.6))
    ax.text(3.7, 3.6, "Y", fontsize=8, va="center")
    d += elm.Dot().at((0, 3.6))
    d += elm.Dot().at((3.0, 3.6))
    for x, nm in ((0.0, "A"), (3.0, "B")):
        d += elm.Line().at((x, 3.6)).to((x, 3.0))
        g, y = _fet(d, "n", x, 3.0); _glab(ax, g, nm); _wlab(ax, x, 2.25, 1, N)
        d += elm.Line().at((x, y)).to((x, 0.5))
    _gnd(d, 0, 3.0, 0.5)
    ax.set_title("NOR2", fontsize=8.5)
    _finish(d, ax, XL, YL)

    # AOI21 ----------------------------------------------------------------
    ax = axs[3]
    d = _sd(ax, fontsize=7.5)
    top = 8.0
    _vdd(d, ax, 0, 3.0, top)
    for x, nm in ((0.0, "A"), (3.0, "B")):
        d += elm.Line().at((x, top)).to((x, top - 0.2))
        g, y = _fet(d, "p", x, top - 0.2); _glab(ax, g, nm); _wlab(ax, x, top - 0.95, 4, P)
        d += elm.Line().at((x, y)).to((x, 6.0))
    d += elm.Line().at((0, 6.0)).to((3.0, 6.0))
    d += elm.Dot().at((0, 6.0))
    d += elm.Line().at((0, 6.0)).to((0, 5.8))
    g, y = _fet(d, "p", 0, 5.8); _glab(ax, g, "C"); _wlab(ax, 0, 5.05, 4, P)
    d += elm.Line().at((0, y)).to((0, 3.9))
    d += elm.Line().at((0, 3.9)).to((3.6, 3.9))
    ax.text(3.7, 3.9, "Y", fontsize=8, va="center")
    d += elm.Dot().at((0, 3.9))
    d += elm.Dot().at((3.0, 3.9))
    d += elm.Line().at((0, 3.9)).to((0, 3.6))
    g, y = _fet(d, "n", 0, 3.6); _glab(ax, g, "A"); _wlab(ax, 0, 2.85, 2, N)
    g, y = _fet(d, "n", 0, y); _glab(ax, g, "B"); _wlab(ax, 0, y + 0.75, 2, N)
    d += elm.Line().at((0, y)).to((0, 0.3))
    d += elm.Line().at((3.0, 3.9)).to((3.0, 2.85))
    g, y2 = _fet(d, "n", 3.0, 2.85); _glab(ax, g, "C"); _wlab(ax, 3.0, 2.1, 1, N)
    d += elm.Line().at((3.0, y2)).to((3.0, 0.3))
    _gnd(d, 0, 3.0, 0.3)
    ax.set_title(r"AOI21  $Y=\overline{AB+C}$", fontsize=8.5)
    _finish(d, ax, XL, YL)

    # TG multiplexer -------------------------------------------------------
    ax = axs[4]
    d = _sd(ax, fontsize=7)

    def tg(xl, y, ctl_n, ctl_p):
        # pMOS on top (gate up), nMOS below (gate down), in parallel between xl and xl+1.5
        p = elm.PFet().theta(90).anchor("source").at((xl, y + 0.6))
        d.add(p)
        n = elm.NFet().theta(-90).anchor("source").at((xl, y - 0.6))
        d.add(n)
        # NFet theta(-90): source at left? fix ends with lines
        pa, pb = sorted([p.source, p.drain], key=lambda q: q[0])
        na, nb = sorted([n.source, n.drain], key=lambda q: q[0])
        d.add(elm.Line().at(pa).to(na))
        d.add(elm.Line().at(pb).to(nb))
        ax.text(p.gate[0], p.gate[1] + 0.08, ctl_p, fontsize=6.8, ha="center", va="bottom")
        ax.text(n.gate[0], n.gate[1] - 0.08, ctl_n, fontsize=6.8, ha="center", va="top")
        ax.text(pb[0] + 0.05, y + 0.95, "1", fontsize=6.5, color=P, ha="left", fontweight="bold")
        ax.text(nb[0] + 0.05, y - 0.95, "1", fontsize=6.5, color=N, ha="left", va="top", fontweight="bold")
        return pa[0], pb[0]

    y0, y1 = 6.6, 0.8
    a0, b0 = tg(-1.2, y0, r"$\overline{S}$", "S")
    a1, b1 = tg(-1.2, y1, "S", r"$\overline{S}$")
    for yy, nm in ((y0, "D0"), (y1, "D1")):
        d += elm.Line().at((a0 - 0.5, yy)).to((a0, yy))
        ax.text(a0 - 0.55, yy, nm, fontsize=7.5, ha="right", va="center")
    xo = b0 + 0.5
    d += elm.Line().at((b0, y0)).to((xo, y0))
    d += elm.Line().at((b1, y1)).to((xo, y1))
    d += elm.Line().at((xo, y0)).to((xo, y1))
    d += elm.Dot().at((xo, 0.5 * (y0 + y1)))
    d += elm.Line().at((xo, 0.5 * (y0 + y1))).to((xo + 0.4, 0.5 * (y0 + y1)))
    # output inverter as a triangle with bubble
    yc = 0.5 * (y0 + y1)
    x0 = xo + 0.4
    ax.add_patch(Polygon([(x0, yc - 0.45), (x0, yc + 0.45), (x0 + 0.75, yc)], closed=True, fill=False,
                         ec=INK, lw=1.1))
    ax.add_patch(Circle((x0 + 0.85, yc), 0.1, fill=False, ec=INK, lw=1.1))
    ax.plot([x0 + 0.95, x0 + 1.3], [yc, yc], color=INK, lw=1.1)
    ax.text(x0 + 1.35, yc, "Y", fontsize=8, va="center")
    ax.text(x0 + 0.35, yc - 0.6, "inv", fontsize=6.3, ha="center", va="top")
    ax.set_title("TG 2:1 mux", fontsize=8.5)
    _finish(d, ax, (-3.1, 3.8), (YL[0], YL[1] + 0.9))

    # logical effort / parasitic delay under the first four
    rows = [("g = 1", "p = 1"), ("g = 4/3", "p = 2"), ("g = 5/3", "p = 2"),
            ("g = 2 (A, B)\n   5/3 (C)", "p = 7/3")]
    for ax, (g_, p_) in zip(axs[:4], rows):
        ax.text(0.5, -0.65, g_ + "\n" + p_, fontsize=7.2, ha="center", va="top",
                transform=ax.transData, color=INK)
    fig.text(0.5, 0.005, "widths in units of the minimum nMOS width (orange: pMOS, blue: nMOS); "
             "g: logical effort per input, p: parasitic delay", fontsize=6.8, ha="center", va="bottom",
             color=GREY)
    save(fig, "33", "fig-33-3-static-cmos-gates")


# ----------------------------------------------------------------------------
# Figure 33.4 — TG master-slave flip-flop and its timing
# ----------------------------------------------------------------------------
def _inv(ax, x, y, w=0.7, h=0.6, label=None, flip=False, lw=1.1):
    """Inverter symbol with input at (x, y), pointing right (or left if flip)."""
    s = -1 if flip else 1
    ax.add_patch(Polygon([(x, y - h / 2), (x, y + h / 2), (x + s * w, y)], closed=True, fc="white",
                         ec=INK, lw=lw, zorder=3))
    ax.add_patch(Circle((x + s * (w + 0.08), y), 0.08, fc="white", ec=INK, lw=lw, zorder=3))
    if label:
        ax.text(x + s * w * 0.4, y - h / 2 - 0.08, label, fontsize=6.5, ha="center", va="top")
    return x + s * (w + 0.16)


def _tg(ax, x, y, label, on_txt, w=0.8, h=0.5, lw=1.1):
    """Transmission-gate symbol (bow-tie with control bubble) from x to x+w."""
    ax.add_patch(Polygon([(x, y - h / 2), (x, y + h / 2), (x + w, y - h / 2), (x + w, y + h / 2)],
                         closed=True, fc="white", ec=INK, lw=lw, zorder=3))
    ax.plot([x + w / 2, x + w / 2], [y + h / 2 - 0.12, y + h / 2 + 0.25], color=INK, lw=lw)
    ax.add_patch(Circle((x + w / 2, y + 0.05), 0.0, fc=INK))
    ax.plot([x + w / 2, x + w / 2], [y - h / 2 + 0.12, y - h / 2 - 0.25], color=INK, lw=lw)
    ax.text(x + w / 2, y + h / 2 + 0.3, label, fontsize=6.8, ha="center", va="bottom", fontweight="bold")
    ax.text(x + w / 2, y - h / 2 - 0.3, on_txt, fontsize=6.0, ha="center", va="top", color=GREY)
    return x + w


def fig_33_4():
    fig = plt.figure(figsize=(6.8, 6.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.85, 1.15], hspace=0.12)
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(-0.7, 14.6)
    ax.set_ylim(-0.9, 5.6)
    ax.set_aspect("equal")
    ax.axis("off")
    yl, yf = 3.0, 1.25
    lw = 1.1

    def wire(xs, ys):
        ax.plot(xs, ys, color=INK, lw=lw, zorder=2)

    def dot(x, y):
        ax.plot(x, y, "o", color=INK, ms=3.2, zorder=5)

    def latch(x0, tga, tgb, ia, ib, on_a, on_b, node_lab=None):
        """Input TG, forward inverter, feedback inverter + TG.  Returns output x."""
        wire([x0, x0 + 0.3], [yl, yl])
        xe = _tg(ax, x0 + 0.3, yl, tga, on_a)
        xn = xe + 0.8
        wire([xe, xn + 0.6], [yl, yl])
        dot(xn, yl)
        if node_lab:
            ax.text(xn, yl + 0.15, node_lab, fontsize=7.5, ha="center", va="bottom", color=RED)
        xi = _inv(ax, xn + 0.6, yl, label=ia)
        xo = xi + 0.8
        wire([xi, xo + 0.4], [yl, yl])
        dot(xo, yl)
        wire([xo, xo], [yl, yf])
        wire([xo, xo - 0.2], [yf, yf])
        xi2 = _inv(ax, xo - 0.2, yf, flip=True, label=ib)
        wire([xi2, xi2 - 0.25], [yf, yf])
        _tg(ax, xi2 - 0.25 - 0.8, yf, tgb, on_b)
        wire([xi2 - 1.05, xn], [yf, yf])
        wire([xn, xn], [yf, yl])
        return xo, xn

    ax.text(-0.6, yl, "D", fontsize=8.5, ha="left", va="center")
    xo1, xX = latch(-0.3, "TG1", "TG2", "I1", "I2", "on: CLK low", "on: CLK high", node_lab="X")
    xo2, _ = latch(xo1 + 0.7, "TG3", "TG4", "I3", "I4", "on: CLK high", "on: CLK low")
    xb = _inv(ax, xo2 + 0.6, yl, label="buffer")
    wire([xb, xb + 0.5], [yl, yl])
    ax.text(xb + 0.6, yl, "Q", fontsize=8.5, ha="left", va="center")
    ax.add_patch(Rectangle((-0.15, 0.2), xo1 + 0.25 + 0.15, 4.6, fill=False, ec=BLUE, lw=0.9, ls="--"))
    ax.text(-0.05, 4.72, "master latch\ntransparent: CLK low", fontsize=6.5, color=BLUE, va="top")
    ax.add_patch(Rectangle((xo1 + 0.45, 0.2), xo2 + 0.25 - xo1 - 0.45, 4.6, fill=False, ec=GREEN, lw=0.9,
                           ls="--"))
    ax.text(xo1 + 0.55, 4.72, "slave latch\ntransparent: CLK high", fontsize=6.5, color=GREEN, va="top")
    # clock buffers
    xc = 12.0
    ax.text(xc - 0.4, 5.25, "local clock inverters", fontsize=6.8, ha="left", va="bottom")
    ax.text(xc - 0.2, 4.55, "CLK", fontsize=7, ha="right", va="center")
    wire([xc - 0.15, xc], [4.55, 4.55])
    x1 = _inv(ax, xc, 4.55, w=0.55, h=0.45)
    wire([x1, x1 + 0.4], [4.55, 4.55])
    x2 = _inv(ax, x1 + 0.4, 4.55, w=0.55, h=0.45)
    ax.text(x1 + 0.2, 4.35, r"$\overline{\phi}$", fontsize=8, ha="center", va="top")
    wire([x2, x2 + 0.3], [4.55, 4.55])
    ax.text(x2 + 0.35, 4.55, r"$\phi$", fontsize=8, ha="left", va="center")
    ax.text(xc - 0.4, 3.55, "each TG takes φ on one device\nand φ̄ on the other", fontsize=6.0,
            color=GREY, ha="left", va="top")
    ax.text(14.55, -0.85, "4 TGs (8) + 4 inverters (8) + 2 clock inverters (4) = 20 transistors;\n"
            "the output buffer adds 2", fontsize=6.5, ha="right", va="bottom")

    # --- timing ---------------------------------------------------------
    axt = fig.add_subplot(gs[1])
    T, tr = 2.0, 0.05
    t = np.linspace(0, 4, 8001)

    def wave(edges, start, rise=tr):
        v = np.full_like(t, float(start))
        lev = float(start)
        for te in edges:
            new = 1 - lev
            ramp = np.clip((t - te) / rise + 0.5, 0, 1)
            v = np.where(t >= te - rise / 2, lev + (new - lev) * ramp, v)
            lev = new
        return v

    clk = wave([1.0, 2.0, 3.0], 0)
    dsig = wave([0.7, 2.85], 0)
    tx = 0.03
    xsig = wave([0.7 + tx, 2.85 + tx], 0)
    tcq = 0.19
    q = wave([1.0 + tcq, 3.0 + tcq], 0)
    rows = [("CLK", clk, INK, 4.5), ("D", dsig, BLUE, 3.2), ("X (master)", xsig, RED, 1.9), ("Q", q, GREEN, 0.6)]
    for nm, v, col, y0 in rows:
        axt.plot(t, y0 + 0.8 * v, color=col, lw=1.5)
        axt.text(-0.05, y0 + 0.4, nm, fontsize=7.5, ha="right", va="center", color=col)
    for te in (1.0, 3.0):
        axt.axvline(te, color=GREY, lw=0.6, ls=":", zorder=0)
        axt.axvspan(te - 0.110, te, color=ORANGE, alpha=0.25, lw=0)
        axt.axvspan(te, te + 0.010, color=PINK, alpha=0.6, lw=0)
        axt.annotate("", xy=(te + tcq, 1.75), xytext=(te, 1.75),
                     arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
        axt.text(te + tcq + 0.03, 1.62, r"$t_{cq}$ = 190 ps", fontsize=6.5, ha="left", va="center")
    axt.annotate(r"setup window 110 ps", xy=(0.945, 5.45), xytext=(0.35, 5.75), fontsize=6.5, color=ORANGE,
                 arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    axt.annotate(r"hold window 0–10 ps", xy=(1.005, 5.45), xytext=(1.25, 5.75), fontsize=6.5, color=PINK,
                 arrowprops=dict(arrowstyle="-", color=PINK, lw=0.6))
    axt.text(1.5, 2.95, "X holds while CLK high", fontsize=6.3, color=RED, ha="center", va="top")
    axt.text(2.42, 2.95, "X follows D\nwhile CLK low", fontsize=6.3, color=RED, ha="center", va="top")
    axt.text(2.8, 3.42, "D changes 150 ps\nbefore the edge", fontsize=6.3, color=BLUE, ha="right", va="bottom")
    axt.text(3.98, 0.2, r"$t_{cq}$ = 2.5 FO4 at FO4 = 75 ps; $t_{setup}$ ≈ 1.5 FO4", fontsize=6.5,
             ha="right", va="bottom", color=GREY)
    axt.set_xlim(0, 4)
    axt.set_ylim(0, 6.1)
    axt.set_yticks([])
    axt.spines["left"].set_visible(False)
    axt.set_xlabel("time (ns): 2 ns clock period, 50 ps edges")
    save(fig, "33", "fig-33-4-tg-master-slave-ff")


# ----------------------------------------------------------------------------
# Figure 33.5 — stick diagram and lambda-rule layout of an inverter
# ----------------------------------------------------------------------------
C_PDIFF, C_NDIFF, C_POLY, C_M1, C_WELL = "#E6C229", "#4CAF50", "#D62728", "#1F77B4", "#B39DDB"


def _contact(ax, x, y, s=2.0):
    ax.add_patch(Rectangle((x, y), s, s, fc="#222222", ec="#222222", lw=0.6, zorder=6))
    ax.plot([x, x + s], [y, y + s], color="white", lw=0.7, zorder=7)
    ax.plot([x, x + s], [y + s, y], color="white", lw=0.7, zorder=7)


def _dim(ax, p0, p1, txt, off=(0, 0), ha="center", va="center", col=INK, fs=6.5):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<|-|>", color=col, lw=0.8,
                                                     mutation_scale=6, shrinkA=0, shrinkB=0), zorder=9)
    ax.text(0.5 * (p0[0] + p1[0]) + off[0], 0.5 * (p0[1] + p1[1]) + off[1], txt, fontsize=fs, ha=ha, va=va,
            color=col, zorder=9)


def fig_33_5():
    fig = plt.figure(figsize=(6.8, 5.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[0.8, 1.35], wspace=0.05)
    # --- stick diagram --------------------------------------------------
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(-2.5, 12)
    ax.set_ylim(-2, 22)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((-0.5, 10.5), 11, 9.0, fill=False, ec=C_WELL, lw=1.3, ls="--"))
    ax.text(10.3, 10.8, "n-well", fontsize=7, color="#6A4FB3", ha="right", va="bottom")
    ax.plot([-0.5, 10.5], [19, 19], color=C_M1, lw=3.0)
    ax.plot([-0.5, 10.5], [1, 1], color=C_M1, lw=3.0)
    ax.text(-0.7, 19, r"$V_{DD}$", fontsize=7.5, ha="right", va="center")
    ax.text(-0.7, 1, "GND", fontsize=7.5, ha="right", va="center")
    ax.plot([2, 8], [15, 15], color=C_PDIFF, lw=4.0)
    ax.plot([2, 8], [5, 5], color=C_NDIFF, lw=4.0)
    ax.plot([5, 5], [3.2, 16.8], color=C_POLY, lw=2.2)
    ax.plot([1.0, 5], [10, 10], color=C_POLY, lw=2.2)
    ax.text(0.8, 10, "A", fontsize=8.5, ha="right", va="center", color=C_POLY)
    for (x, y) in ((2.6, 15), (7.4, 15), (2.6, 5), (7.4, 5)):
        ax.plot(x, y, marker="x", color=INK, ms=7, mew=1.5)
    ax.plot([2.6, 2.6], [15, 19], color=C_M1, lw=2.0)
    ax.plot([2.6, 2.6], [5, 1], color=C_M1, lw=2.0)
    ax.plot([7.4, 7.4], [5, 15], color=C_M1, lw=2.0)
    ax.plot([7.4, 9.8], [10, 10], color=C_M1, lw=2.0)
    ax.text(10.0, 10, "Y", fontsize=8.5, ha="left", va="center", color=C_M1)
    ax.text(8.3, 15.6, "p-diff", fontsize=6.5, color="#9A7D0A", va="bottom")
    ax.text(8.3, 5.6, "n-diff", fontsize=6.5, color="#2E7D32", va="bottom")
    ax.text(5.3, 17.0, "poly", fontsize=6.5, color=C_POLY, va="bottom")
    ax.set_title("stick diagram", fontsize=9)
    ax.text(5, -1.2, "× contact   — metal 1", fontsize=6.5, ha="center", color=GREY)

    # --- layout ---------------------------------------------------------
    al = fig.add_subplot(gs[1])
    al.set_xlim(-6, 31)
    al.set_ylim(-8.5, 44)
    al.set_aspect("equal")
    al.axis("off")
    for gx in range(0, 25):
        al.plot([gx, gx], [0, 40], color="#EEEEEE", lw=0.4, zorder=0)
    for gy in range(0, 41):
        al.plot([0, 24], [gy, gy], color="#EEEEEE", lw=0.4, zorder=0)
    al.add_patch(Rectangle((0, 0), 24, 40, fill=False, ec=GREY, lw=0.8, ls=":", zorder=1))
    # n-well
    al.add_patch(Rectangle((-1, 20), 26, 22, fc=C_WELL, alpha=0.25, ec="#6A4FB3", lw=1.0, ls="--", zorder=1))
    al.text(0.2, 41.7, "n-well", fontsize=6.8, color="#6A4FB3", ha="left", va="top")
    # active
    al.add_patch(Rectangle((6, 25), 12, 8, fc=C_PDIFF, alpha=0.75, ec="#9A7D0A", lw=0.8, zorder=2))
    al.add_patch(Rectangle((6, 8), 12, 4, fc=C_NDIFF, alpha=0.75, ec="#2E7D32", lw=0.8, zorder=2))
    # taps
    al.add_patch(Rectangle((19, 36), 4, 4, fc=C_NDIFF, alpha=0.75, ec="#2E7D32", lw=0.8, zorder=2))
    al.add_patch(Rectangle((19, 1), 4, 4, fc=C_PDIFF, alpha=0.75, ec="#9A7D0A", lw=0.8, zorder=2))
    # poly
    al.add_patch(Rectangle((11, 6), 2, 29, fc=C_POLY, alpha=0.8, ec=C_POLY, lw=0.6, zorder=3))
    al.add_patch(Rectangle((3, 18), 8, 2, fc=C_POLY, alpha=0.8, ec=C_POLY, lw=0.6, zorder=3))
    al.add_patch(Rectangle((1, 17), 4, 4, fc=C_POLY, alpha=0.8, ec=C_POLY, lw=0.6, zorder=3))
    # metal 1
    m1 = dict(fc=C_M1, alpha=0.35, ec=C_M1, lw=0.8, zorder=4)
    al.add_patch(Rectangle((0, 36), 24, 4, **m1))
    al.add_patch(Rectangle((0, 0), 24, 4, **m1))
    al.add_patch(Rectangle((6.5, 25), 3, 11, **m1))
    al.add_patch(Rectangle((6.5, 4), 3, 8, **m1))
    al.add_patch(Rectangle((14.5, 8), 3, 25, **m1))
    al.add_patch(Rectangle((0.5, 16.5), 5, 5, **m1))
    # contacts
    for (x, y) in ((7, 26), (7, 30), (15, 26), (15, 30), (7, 9), (15, 9), (2, 18), (20, 37), (20, 2)):
        _contact(al, x, y)
    al.text(-0.6, 38, r"$V_{DD}$", fontsize=7.5, ha="right", va="center")
    al.text(-0.6, 2, "GND", fontsize=7.5, ha="right", va="center")
    al.text(-0.6, 19, "A", fontsize=8, ha="right", va="center", color=C_POLY)
    al.text(18.0, 21, "Y", fontsize=8.5, ha="left", va="center", color=C_M1, fontweight="bold")
    al.text(23.4, 38.0, "well\ntap", fontsize=5.8, ha="left", va="center")
    al.text(23.4, 3.0, "substrate\ntap", fontsize=5.8, ha="left", va="center")
    # dimensions
    _dim(al, (11, 23.4), (13, 23.4), r"2λ", off=(0, -1.0), fs=6.2)
    al.text(12, 21.3, "poly width\n(L)", fontsize=5.6, ha="center", va="top")
    _dim(al, (12.0, 33), (12.0, 35), "", fs=6)
    al.text(13.3, 34.0, "2λ", fontsize=6.0, ha="left", va="center")
    _dim(al, (12.0, 6), (12.0, 8), "", fs=6)
    al.text(13.3, 6.6, "2λ poly end-cap", fontsize=5.8, ha="left", va="center")
    _dim(al, (20.5, 12), (20.5, 25), "", fs=6.2)
    al.text(21.0, 15.5, "13λ active\nspacing", fontsize=5.6, ha="left", va="center")
    _dim(al, (18.0, 25.0), (18.0, 33.0), "", fs=6)
    al.text(18.6, 29.0, r"$W_p$ = 8λ", fontsize=6.0, ha="left", va="center")
    _dim(al, (18.0, 8.0), (18.0, 12.0), "", fs=6)
    al.text(18.6, 10.5, r"$W_n$ = 4λ", fontsize=6.0, ha="left", va="center")
    _dim(al, (6.0, 25.6), (7.0, 25.6), "", fs=6)
    al.text(3.5, 27.0, "1λ contact\nenclosure", fontsize=5.6, ha="center", va="center")
    al.plot([5.2, 6.4], [26.4, 25.8], color=INK, lw=0.5)
    _dim(al, (17.0, 33.0), (17.0, 36.0), "", fs=6)
    al.text(16.0, 37.2, "", fontsize=5.6)
    al.text(17.4, 34.3, "3λ m1 spacing", fontsize=5.6, ha="left", va="center")
    _dim(al, (24.0, 20.0), (24.0, 25.0), "", fs=6)
    al.text(25.6, 22.5, "5λ well\nenclosure", fontsize=5.6, ha="left", va="center")
    al.plot([24.2, 25.5], [22.5, 22.5], color=INK, lw=0.5)
    _dim(al, (0, -2.2), (24, -2.2), "24λ", off=(0, -1.0), fs=6.5)
    _dim(al, (27.5, 0), (27.5, 40), "40λ", off=(1.0, 0), ha="left", fs=6.5)
    _dim(al, (1.2, 36), (1.2, 40), "", fs=6)
    al.text(-0.6, 35.0, "4λ rail", fontsize=5.6, ha="right", va="top")
    al.set_title("layout on a λ grid (λ = 0.09 µm: cell area 7.8 µm²)", fontsize=9)
    # legend swatches
    lx, ly = -5.5, -7.8
    for k, (c, nm, a) in enumerate(((C_PDIFF, "p+ active", 0.75), (C_NDIFF, "n+ active", 0.75),
                                    (C_POLY, "poly", 0.8), (C_M1, "metal 1", 0.35))):
        al.add_patch(Rectangle((lx + k * 8.4, ly), 1.6, 1.2, fc=c, alpha=a, ec=c, lw=0.6))
        al.text(lx + k * 8.4 + 2.0, ly + 0.6, nm, fontsize=6.2, va="center")
    save(fig, "33", "fig-33-5-inverter-layout-stick")


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4", "5"]
    for w in which:
        globals()[f"fig_33_{w}"]()
