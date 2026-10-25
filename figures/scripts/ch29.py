"""Figures for Chapter 29 — Power-Electronic Fundamentals.

Run from the repository root:  python figures/scripts/ch29.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def drawing(ax, fontsize=8, lw=1.1, unit=2.0):
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


# ----------------------------------------------------------------------------
# switching-transient models (shared by Figures 29.1 and 29.5)
# ----------------------------------------------------------------------------
VDC, I0 = 400.0, 20.0
L_SIG, C_OSS = 31.7e-9, 80e-12        # from the snubber worked example
TAU_RING = 40e-9                       # decay of the undamped ringing
R_LOOP = 2 * L_SIG / TAU_RING          # series loop resistance giving that decay
T_RV, T_FI = 7.8e-9, 4.5e-9            # voltage rise and current fall (Section 29.3)
V_ON = 1.6                             # on-state drop 20 A x 81 mOhm


def turn_off(t, t1=20e-9, snubber=None, t_fi=None):
    """Clamped inductive turn-off: switch = channel current source || C_oss (|| R_s-C_s).

    During the Miller plateau the gate fixes dv/dt (a 7.8 ns rise to 400 V); the channel
    carries whatever load current the capacitances do not take. Once the switch node
    reaches V_dc the freewheeling diode clamps it, the channel current falls linearly
    over t_fi and the loop L_sigma - C_oss (- snubber) rings, damped to a 40 ns decay.
    Returns v_ds and the drain-terminal (loop) current.
    """
    if t_fi is None:
        t_fi = T_FI_MODEL
    dt = t[1] - t[0]
    dvdt = (VDC - V_ON) / T_RV
    v, iL, vcs = V_ON, I0, V_ON
    clamped, t_cl, i_cl = False, 0.0, 0.0
    vs, il = np.empty_like(t), np.empty_like(t)
    for k, tt in enumerate(t):
        i_sn = (v - vcs) / snubber[0] if snubber is not None else 0.0
        if tt < t1:
            ic = I0
        elif not clamped:
            ic = max(I0 - C_OSS * dvdt - i_sn, 0.0)
        else:
            ic = max(0.0, i_cl * (1 - (tt - t_cl) / t_fi))
        if not clamped:
            v += (I0 - ic - i_sn) / C_OSS * dt
            iL = I0
            if v >= VDC:
                clamped, t_cl, i_cl = True, tt, ic
        else:
            iL += (VDC - v - R_LOOP * iL) / L_SIG * dt
            v += (iL - ic - i_sn) / C_OSS * dt
            iL = min(iL, I0)
        if snubber is not None:
            vcs += i_sn / snubber[1] * dt
        vs[k], il[k] = v, iL
    return vs, il


T_FI_MODEL = T_FI                      # the chapter's own t_fi (Section 29.3)


def gate_exp(t, t0, v0, vinf, tau=9e-9):
    return vinf + (v0 - vinf) * np.exp(-(t - t0) / tau)


# ----------------------------------------------------------------------------
# Figure 29.1 — commutation cell and clamped inductive switching
# ----------------------------------------------------------------------------
def draw_cell(ax):
    d = drawing(ax, fontsize=8)
    top, bot, xs = 6.0, 0.0, 5.0
    # DC link capacitor
    d.add(elm.Capacitor(polar=True).at((0, bot)).to((0, top)).label("$C_{dc}$\n400 V", loc="top", ofst=0.5))
    # loop inductance on top rail
    d.add(elm.Inductor2(loops=2).at((0, top)).to((2.4, top)).label(r"$L_\sigma$ 30 nH", loc="top", ofst=0.1))
    wire(d, [(2.4, top), (xs, top)])
    wire(d, [(0, bot), (xs, bot)])
    q1 = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xs, 4.4)))
    q2 = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xs, 1.6)))
    wire(d, [q1.drain, (xs, top)])
    wire(d, [q1.source, (xs, 3.0)])
    wire(d, [(xs, 3.0), q2.drain])
    wire(d, [q2.source, (xs, bot)])
    for q, y0, y1 in ((q1, q1.source[1], q1.drain[1]), (q2, q2.source[1], q2.drain[1])):
        wire(d, [(xs, y0 - 0.0), (xs + 1.1, y0)])
        d.add(elm.Diode().at((xs + 1.1, y0)).to((xs + 1.1, y1)))
        wire(d, [(xs + 1.1, y1), (xs, y1)])
    ax.text(xs - 0.45, 4.95, "S1", fontsize=8.5, ha="right")
    ax.text(xs - 0.45, 2.15, "S2", fontsize=8.5, ha="right")
    # switch node and inductor
    dot(d, (xs, 3.0))
    wire(d, [(xs, 3.0), (7.2, 3.0)])
    d.add(elm.Inductor2(loops=3).at((7.2, 3.0)).to((9.6, 3.0)).label("$L$", loc="top", ofst=0.1))
    d.add(elm.Line().at((9.6, 3.0)).to((10.8, 3.0)).linestyle("-"))
    ax.annotate("", xy=(10.9, 3.0), xytext=(9.9, 3.0),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.4, mutation_scale=11))
    ax.text(10.4, 3.25, "$I_L$ = 20 A", color=ORANGE, fontsize=8, ha="center", va="bottom")
    ax.text(10.9, 2.75, "to load", fontsize=7.5, ha="right", va="top")
    ax.text(xs + 0.1, 3.2, "SW", fontsize=7.5, ha="left", va="bottom")
    # gate drivers
    for q in (q1, q2):
        g = q.gate
        wire(d, [g, (g[0] - 0.5, g[1])])
        bx = g[0] - 0.5 - 1.3
        ax.add_patch(FancyBboxPatch((bx, g[1] - 0.4), 1.3, 0.8, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc="#EEF3F8", ec=INK, lw=0.9, zorder=3))
        ax.text(bx + 0.65, g[1], "GD", fontsize=7.5, ha="center", va="center", zorder=4)
    finish(ax, d, pad=0.2)


def turn_on(t, t0=20e-9):
    """Piecewise clamped inductive turn-on (hard switching, SiC values of Section 29.3)."""
    tau = 9e-9
    vg = np.where(t < t0, -4.0, 0.0)
    t_th = t0 + tau * np.log(19 / 12)       # gate reaches 3 V
    t_pl0 = t_th + 4.2e-9                    # current reaches 20 A, plateau starts
    t_pl1 = t_pl0 + 12.0e-9                  # voltage fall complete
    # gate
    a = (t >= t0) & (t < t_pl0)
    vg = np.where(a, gate_exp(t, t0, -4.0, 15.0), vg)
    vg = np.where((t >= t_pl0) & (t < t_pl1), 7.5, vg)
    t_eq = t0 + tau * np.log(19 / 7.5)       # equivalent time on the exponential at 7.5 V
    vg = np.where(t >= t_pl1, gate_exp(t - (t_pl1 - t_eq), t0, -4.0, 15.0), vg)
    # current: linear rise, plus diode recovery bump to 26 A
    i = np.clip((t - t_th) / 4.2e-9, 0, 1) * I0
    trr = 9e-9
    bump = np.where(t >= t_pl0, 6.0 * np.clip(1 - (t - t_pl0 - 2e-9) / (trr - 2e-9), 0, 1), 0)
    bump = np.where((t >= t_pl0) & (t < t_pl0 + 2e-9), 6.0 * (t - t_pl0) / 2e-9, bump)
    i = i + bump
    # voltage: clamped at VDC until 20 A, then linear fall to 1.6 V
    v = np.where(t < t_pl0, VDC, VDC - (VDC - V_ON) * np.clip((t - t_pl0) / 12e-9, 0, 1))
    return vg, i, v, (t_th, t_pl0, t_pl1)


def fig_29_1():
    fig = plt.figure(figsize=(6.8, 5.0))
    axc = fig.add_axes([0.0, 0.62, 0.62, 0.37])
    draw_cell(axc)
    axc.text(0.0, 1.0, "(a)", transform=axc.transAxes, fontsize=9, weight="bold", va="top")
    fig.text(0.64, 0.93, "(b) clamped inductive switching of S1", fontsize=8.5, weight="bold")
    fig.text(0.64, 0.68, "$V_{dc}$ = 400 V, $I_L$ = 20 A\n$R_G$ = 9 Ω, −4 V / +15 V drive\n"
             "SiC 650 V, 60 mΩ, 125 °C\nshaded: v·i overlap", fontsize=7.6, va="bottom", linespacing=1.4)

    t = np.arange(0, 120e-9, 5e-12)
    tn = t * 1e9
    # turn-on
    vg_on, i_on, v_on, (t_th, t_pl0, t_pl1) = turn_on(t)
    # turn-off
    v_off, i_off = turn_off(t, t1=20e-9)
    tau = 9e-9
    t1 = 20e-9
    t_pl = t1 + tau * np.log(19 / 11.5)
    vg_off = np.where(t < t1, 15.0, gate_exp(t, t1, 15.0, -4.0))
    vg_off = np.where((t >= t_pl) & (t < t_pl + T_RV), 7.5, vg_off)
    vg_off = np.where(t >= t_pl + T_RV, gate_exp(t - T_RV, t1, 15.0, -4.0), vg_off)
    # time shift the turn-off model so the plateau starts after the gate reaches 7.5 V
    shift = int(round((t_pl - t1) / (t[1] - t[0])))
    v_off = np.concatenate([np.full(shift, V_ON), v_off[:-shift]])
    i_off = np.concatenate([np.full(shift, I0), i_off[:-shift]])

    E_on = np.trapezoid(v_on * i_on, t) if hasattr(np, "trapezoid") else np.trapz(v_on * i_on, t)
    mask = t > 0
    p_off = v_off * i_off
    E_off = np.trapezoid(p_off[mask], t[mask]) if hasattr(np, "trapezoid") else np.trapz(p_off[mask], t[mask])
    E_off -= V_ON * I0 * 20e-9 * 0  # conduction before t1 is negligible

    panels = [("turn-on", vg_on, i_on, v_on, E_on), ("turn-off", vg_off, i_off, v_off, E_off)]
    lefts = [0.085, 0.585]
    for (title, vg, ii, vv, E), lx in zip(panels, lefts):
        axg = fig.add_axes([lx, 0.47, 0.32, 0.12])
        axm = fig.add_axes([lx, 0.07, 0.32, 0.38], sharex=axg)
        axg.plot(tn, vg, color=GREEN, lw=1.4)
        axg.set_ylim(-7, 18)
        axg.set_yticks([-4, 7.5, 15])
        axg.set_yticklabels(["−4", "7.5", "15"], fontsize=7)
        axg.axhline(7.5, color=GREY, lw=0.5, ls=":")
        axg.set_ylabel("$v_{GS}$ (V)", fontsize=8)
        axg.tick_params(labelbottom=False)
        axg.set_title(title, fontsize=9)
        axi = axm.twinx()
        axi.spines["right"].set_visible(True)
        axm.plot(tn, vv, color=BLUE, lw=1.6, label="$v_{DS}$")
        axi.plot(tn, ii, color=ORANGE, lw=1.6, label="$i_D$")
        # overlap shading (power) drawn on voltage axis scaled
        p = vv * ii
        axm.fill_between(tn, 0, p / p.max() * 250, color=PINK, alpha=0.35, lw=0)
        axm.set_ylim(-20, 700)
        axi.set_ylim(-1, 31)
        axm.set_xlim(0, 120)
        axm.set_xlabel("time (ns)")
        axm.set_ylabel("$v_{DS}$ (V)", color=BLUE)
        axi.set_ylabel("$i_D$ (A)", color=ORANGE)
        axm.tick_params(axis="y", colors=BLUE, labelsize=8)
        axi.tick_params(axis="y", colors=ORANGE, labelsize=8)
        axm.tick_params(axis="x", labelsize=8)
        k = np.argmax(p)
        lab = "$E_{on}$" if title == "turn-on" else "$E_{off}$"
        axm.text(tn[k] + 4, 150, f"{lab}\n(v·i overlap)", color="#8E3B73", fontsize=7.4,
                 ha="left", va="center")
        if title == "turn-on":
            axi.annotate("26 A\n(diode\nrecovery)", xy=(t_pl0 * 1e9 + 2, 26), xytext=(t_pl0 * 1e9 + 22, 26),
                         fontsize=7, ha="left", va="center", color=ORANGE,
                         arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
            axm.text(3, 560, "$t_{ri}$ = 4.2 ns", fontsize=7, ha="left")
            axm.text(44, 330, "$t_{fv}$ = 12 ns", fontsize=7, ha="left")
        else:
            kpk = np.argmax(vv)
            axm.annotate(f"{vv[kpk]:.0f} V\n(100 MHz ring)", xy=(tn[kpk], vv[kpk]),
                         xytext=(tn[kpk] + 18, 650), fontsize=7, color=BLUE, ha="left", va="center",
                         arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
            axm.text(3, 500, "$t_{rv}$ = 7.8 ns\n$t_{fi}$ = 4.5 ns", fontsize=7, ha="left")
        if title == "turn-on":
            axm.legend(handles=[axm.lines[0], axi.lines[0]], loc="upper right", fontsize=7.5,
                       bbox_to_anchor=(1.0, 0.98))
    print(f"  29.1: E_on ~ {E_on*1e6:.1f} uJ, E_off ~ {E_off*1e6:.1f} uJ, v_pk {v_off.max():.0f} V")
    save(fig, "29", "fig-29-1-commutation-cell")


# ----------------------------------------------------------------------------
# Figure 29.2 — loss versus frequency
# ----------------------------------------------------------------------------
def fig_29_2():
    V, I, D = 400.0, 20.0, 0.5
    devs = [("Si SJ MOSFET", dict(R=0.095, E=325e-6), BLUE),
            ("Si IGBT", dict(V0=0.95, r=0.030, E=600e-6), ORANGE),
            ("SiC MOSFET", dict(R=0.081, E=115e-6), GREEN),
            ("GaN HEMT", dict(R=0.090, E=43e-6), PINK)]
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    f = np.linspace(0, 200e3, 401)
    P_max = 25.0
    for name, d, c in devs:
        pc = D * I ** 2 * d["R"] if "R" in d else D * (d["V0"] * I + d["r"] * I ** 2)
        ax.plot(f / 1e3, pc + d["E"] * f, color=c, lw=1.8)
        fmax = (P_max - pc) / d["E"]
        ax.plot(fmax / 1e3, P_max, "o", color=c, ms=5, zorder=5)
        d["pc"], d["fmax"] = pc, fmax
    # direct labels at line ends / inside
    lab = {"Si IGBT": (55, 70, "Si IGBT\n15.5 W + 600 µJ·f"),
           "Si SJ MOSFET": (168, 55, "Si SJ MOSFET\n19.0 W + 325 µJ·f"),
           "SiC MOSFET": (168, 44, "SiC MOSFET\n16.2 W + 115 µJ·f"),
           "GaN HEMT": (120, 15.5, "GaN HEMT\n18.0 W + 43 µJ·f")}
    for name, d, c in devs:
        x, y, txt = lab[name]
        ax.text(x, y, txt, color=c, fontsize=7.8, ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=0.6))
    ax.axhline(P_max, color=INK, ls="--", lw=1.0)
    ax.text(97, 25.4, "thermal budget 25 W per device", ha="left", va="bottom", fontsize=7.6)
    # f_max markers
    offs = {"Si IGBT": (-8, 8), "Si SJ MOSFET": (12, -12), "SiC MOSFET": (0, 5), "GaN HEMT": (8, -7)}
    for name, d, c in devs:
        dx, dy = offs[name]
        ax.annotate(f"{d['fmax']/1e3:.1f} kHz", xy=(d["fmax"] / 1e3, P_max),
                    xytext=(d["fmax"] / 1e3 + dx, P_max + dy), fontsize=7.6, color=c, ha="center",
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.7))
    ax.text(2, 8.0, "f = 0 intercepts: conduction loss 15.5–19.0 W", fontsize=7.6, color=GREY, ha="left")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 80)
    ax.set_xlabel("switching frequency (kHz)")
    ax.set_ylabel("loss per device (W)")
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.text(198, 2, "400 V, 20 A, D = 0.5, $T_j$ = 125 °C", ha="right", fontsize=7.6, color=GREY)
    save(fig, "29", "fig-29-2-loss-vs-frequency")


# ----------------------------------------------------------------------------
# Figure 29.3 — thermal network and transient thermal impedance
# ----------------------------------------------------------------------------
def fig_29_3():
    fig = plt.figure(figsize=(6.8, 3.4))
    axn = fig.add_axes([0.0, 0.05, 0.48, 0.85])
    axz = fig.add_axes([0.60, 0.15, 0.38, 0.75])
    d = drawing(axn, fontsize=7.2, unit=1.6)
    yt, yg, xh = 5.0, 0.0, 6.0
    # junction J1 -> heatsink
    d.add(elm.Resistor().at((0.0, yt)).to((3.0, yt)).label("$R_{th,jc}$\n0.8 K/W", loc="top", ofst=0.1))
    d.add(elm.Resistor().at((3.0, yt)).to((xh, yt)).label("$R_{th,ch}$\n0.5 K/W", loc="top", ofst=0.1))
    # heatsink -> J2
    d.add(elm.Resistor().at((xh, yt)).to((9.0, yt)).label("$R_{th,ch}$\n0.5 K/W", loc="top", ofst=0.1))
    d.add(elm.Resistor().at((9.0, yt)).to((12.0, yt)).label("$R_{th,jc}$\n0.8 K/W", loc="top", ofst=0.1))
    # heat sources (power injected at the junctions, referenced to ambient)
    d.add(elm.SourceI().at((0.0, yg)).to((0.0, yt)).label("21.6 W", loc="bottom", ofst=0.15))
    d.add(elm.SourceI().at((12.0, yg)).to((12.0, yt)).label("21.6 W", loc="top", ofst=0.15))
    # heatsink to ambient
    d.add(elm.Resistor().at((xh, yt)).to((xh, yg)).label("$R_{th,ha}$\n0.9 K/W", loc="bottom", ofst=0.1))
    wire(d, [(0.0, yg), (12.0, yg)])
    for p in ((0.0, yt), (xh, yt), (12.0, yt), (xh, yg)):
        dot(d, p)
    d.add(elm.Ground().at((xh, yg)))
    axn.text(0.0, yt + 1.75, "J1\n$T_j$ = 116.9 °C", fontsize=7.4, ha="center", va="bottom", color=RED)
    axn.text(12.0, yt + 1.75, "J2\n$T_j$ = 116.9 °C", fontsize=7.4, ha="center", va="bottom", color=RED)
    axn.text(xh, yt + 1.75, "heatsink\n88.9 °C", fontsize=7.4, ha="center", va="bottom", color=RED)
    axn.text(xh + 0.3, yg - 0.9, "ambient 50 °C", fontsize=7.4, ha="left", va="top")
    axn.text(xh, -2.6, "each device: 15.9 W conduction + 5.7 W switching", fontsize=7, ha="center",
             va="top", color=GREY)
    finish(axn, d, xlim=(-2.2, 14.2), ylim=(-3.4, 8.6))
    axn.text(0.0, 1.02, "(a)", transform=axn.transAxes, fontsize=9, weight="bold", va="top")

    r = np.array([0.05, 0.20, 0.35, 0.20])
    tau = np.array([10e-6, 0.2e-3, 3e-3, 30e-3])
    t = np.logspace(-6, 0, 600)
    z = (r[None, :] * (1 - np.exp(-t[:, None] / tau[None, :]))).sum(axis=1)
    axz.semilogx(t, z, color=BLUE, lw=1.8)
    axz.axhline(0.8, color=INK, ls="--", lw=1.0)
    axz.text(1.2e-6, 0.815, "steady state 0.8 K/W", fontsize=7.6, va="bottom")
    pos = {1e-3: (2.5e-2, 0.30), 10e-3: (1.2e-1, 0.56)}
    for tt in (1e-3, 10e-3):
        zz = (r * (1 - np.exp(-tt / tau))).sum()
        axz.plot(tt, zz, "o", color=ORANGE, ms=5, zorder=5)
        axz.annotate(f"{tt*1e3:.0f} ms:\n{zz:.3f} K/W", xy=(tt, zz), xytext=pos[tt], ha="center",
                     fontsize=7.6, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    axz.set_xlim(1e-6, 1)
    axz.set_ylim(0, 0.9)
    axz.set_xlabel("time after power step (s)")
    axz.set_ylabel("$Z_{th,jc}$ (K/W)")
    axz.grid(True, which="major", color=GRID, lw=0.6)
    axz.text(1.3e-6, 0.74, "Foster fit:\nr = 0.05, 0.20, 0.35, 0.20 K/W\nτ = 10 µs, 0.2 ms, 3 ms, 30 ms",
             fontsize=7, va="top")
    axz.text(-0.22, 1.08, "(b)", transform=axz.transAxes, fontsize=9, weight="bold", va="top")
    save(fig, "29", "fig-29-3-thermal-network-zth")


# ----------------------------------------------------------------------------
# Figure 29.4 — gate drive with bootstrap and isolated alternative
# ----------------------------------------------------------------------------
def gate_network(d, x0, y, x1, ron="4.7 Ω", roff="2.2 Ω"):
    """Parallel R_on and (diode + R_off) between x0 and x1 at height y."""
    dy = 0.55
    wire(d, [(x0, y), (x0 + 0.3, y)])
    wire(d, [(x0 + 0.3, y + dy), (x0 + 0.3, y - dy)])
    dot(d, (x0 + 0.3, y))
    d.add(elm.Resistor().at((x0 + 0.3, y + dy)).to((x1 - 0.3, y + dy)).label(ron, loc="top", ofst=0.05))
    xm = (x0 + x1) / 2
    d.add(elm.Diode().at((xm + 0.1, y - dy)).to((x0 + 0.3, y - dy)).scale(0.7))
    d.add(elm.Resistor().at((xm + 0.1, y - dy)).to((x1 - 0.3, y - dy)).scale(0.7)
          .label(roff, loc="bottom", ofst=0.05))
    wire(d, [(x1 - 0.3, y + dy), (x1 - 0.3, y - dy)])
    dot(d, (x1 - 0.3, y))
    wire(d, [(x1 - 0.3, y), (x1, y)])


def fig_29_4():
    fig = plt.figure(figsize=(6.8, 4.6))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    d = drawing(ax, fontsize=7.2, unit=1.5)
    ICx0, ICx1, ICy0, ICy1 = 0.0, 2.2, -0.1, 9.9
    ax.add_patch(Rectangle((ICx0, ICy0), ICx1 - ICx0, ICy1 - ICy0, fc="#EEF3F8", ec=INK, lw=1.1, zorder=1))
    ax.text(1.1, 2.6, "driver IC", ha="center", va="center", fontsize=7.0, weight="bold")
    xq = 8.6
    rail, sw, gnd = 10.9, 4.2, -0.6
    yh, yl = 7.0, 1.6           # gate heights
    pins_r = {"VB": 9.4, "HO": yh, "VS": sw, "LO": yl, "COM": 0.4}
    for n, y in pins_r.items():
        ax.text(ICx1 - 0.08, y, n, fontsize=6.4, ha="right", va="center", zorder=3)
    pins_l = {"VDD": 7.8, "HIN": 5.0, "LIN": 3.6}
    for n, y in pins_l.items():
        ax.text(ICx0 + 0.08, y, n, fontsize=6.4, ha="left", va="center", zorder=3)
    # MOSFETs
    q1 = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xq, yh)))
    q2 = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xq, yl)))
    wire(d, [q1.drain, (xq, rail)])
    wire(d, [q1.source, (xq, sw)])
    wire(d, [(xq, sw), q2.drain])
    wire(d, [q2.source, (xq, gnd)])
    ax.text(xq + 0.25, yh + 0.1, "Q1\n80 V Si\n$Q_g$ 120 nC\nat 10 V", fontsize=6.4, ha="left", va="center")
    ax.text(xq + 0.25, yl + 0.1, "Q2\n80 V Si", fontsize=6.4, ha="left", va="center")
    # gate networks (4.7 ohm on; diode-steered 2.2 ohm off)
    for y, q in ((yh, q1), (yl, q2)):
        wire(d, [(ICx1, y), (3.5, y)])
        gate_network(d, 3.5, y, q.gate[0])
    # gate-source resistors
    xr = 7.05
    for yg_, ybot in ((yh, sw), (yl, gnd)):
        d.add(elm.Resistor().at((xr, yg_)).to((xr, ybot)).label("10 kΩ", loc="bottom", ofst=0.05))
        dot(d, (xr, ybot))
    # switch node and ground
    wire(d, [(ICx1, sw), (xq, sw)])
    dot(d, (xq, sw))
    wire(d, [(ICx1, 0.4), (ICx1 + 0.4, 0.4), (ICx1 + 0.4, gnd)])
    wire(d, [(ICx1 + 0.4, gnd), (12.4, gnd)])
    dot(d, (xq, gnd))
    d.add(elm.Ground().at((ICx1 + 0.4, gnd)))
    # bootstrap capacitor between VB and VS
    xb = 3.0
    wire(d, [(ICx1, 9.4), (xb, 9.4)])
    dot(d, (xb, 9.4))
    d.add(elm.Capacitor().at((xb, 9.4)).to((xb, 8.0)).label("$C_{BS}$ 1 µF X7R", loc="bottom", ofst=0.1))
    wire(d, [(xb, 8.0), (xb, sw)])
    dot(d, (xb, sw))
    # bootstrap resistor and diode from 12 V
    ax.text(-1.5, 10.6, "+12 V", fontsize=7, ha="right", va="center")
    d.add(elm.Line().at((-1.4, 10.6)).to((-0.6, 10.6)))
    d.add(elm.Resistor().at((-0.6, 10.6)).to((0.9, 10.6)).scale(0.8).label("2.2 Ω", loc="top", ofst=0.05))
    d.add(elm.Diode().at((0.9, 10.6)).to((2.4, 10.6)).scale(0.8).label("100 V fast", loc="bottom", ofst=0.05))
    wire(d, [(2.4, 10.6), (xb, 10.6), (xb, 9.4)])
    # VDD from 12 V
    wire(d, [(-1.0, 10.6), (-1.0, 7.8), (ICx0, 7.8)])
    dot(d, (-1.0, 10.6))
    ax.text(-1.1, 9.1, "$V_{DD}$\n12 V", fontsize=6.6, ha="right", va="center")
    # PWM inputs
    for y in (5.0, 3.6):
        d.add(elm.Line().at((-1.4, y)).to((ICx0, y)))
    ax.text(-1.5, 4.3, "PWM\nfrom MCU", fontsize=6.8, ha="right", va="center")
    # input rail and capacitor
    wire(d, [(xq, rail), (12.4, rail)])
    ax.text(10.5, rail + 0.15, "48 V bus", fontsize=7, ha="center", va="bottom")
    d.add(elm.Capacitor(polar=True).at((12.4, gnd)).to((12.4, rail)).label("$C_{in}$", loc="bottom", ofst=0.1))
    dot(d, (12.4, gnd))
    # output inductor
    wire(d, [(xq, sw), (9.7, sw)])
    d.add(elm.Inductor2(loops=3).at((9.7, sw)).to((11.0, sw)).scale(0.8))
    ax.text(11.1, sw, "to\nmotor", fontsize=6.6, ha="left", va="center")
    ax.text(5.3, sw - 0.3, "SW (switch node)", fontsize=6.6, ha="center", va="top")
    # charge budget
    ax.text(-1.6, -1.6, "bootstrap charge per high-side on-time (47.5 µs at 20 kHz, D = 0.95):\n"
            "$Q_g$ 120 nC + level shifter 5 nC + leakage (0.1 mA + 1 mA) × 47.5 µs = 52 nC  →  177 nC\n"
            "droop ≈ 177 nC / 0.75 µF ≈ 0.2–0.25 V on a 1 µF X7R at its 12 V bias",
            fontsize=6.8, ha="left", va="top", linespacing=1.4)

    # ---- right inset: isolated driver for a 400 V SiC leg --------------------
    X0 = 13.8
    ax.add_patch(FancyBboxPatch((X0, -0.4), 8.4, 11.4, boxstyle="round,pad=0.02,rounding_size=0.25",
                                fc="#FAFAFA", ec=GREY, lw=1.0, ls=(0, (4, 2)), zorder=0))
    ax.text(X0 + 4.2, 10.45, "isolated alternative:\n400 V SiC leg", ha="center", va="center", fontsize=7.4,
            weight="bold")
    ax.plot([X0 + 1.35, X0 + 1.35], [1.9, 9.3], color=RED, lw=1.2, ls=(0, (2, 2)), zorder=0.5)
    box(ax, X0 + 0.25, 6.4, 2.2, 2.6, "digital\nisolator\nCMTI\n150 V/ns", fc="#DCEFFA", fontsize=6.6)
    box(ax, X0 + 0.25, 2.3, 2.2, 3.4, "isolated\nDC–DC\n< 3 pF\nbarrier\n+15 V /\n−4 V", fc="#FBEFC9",
        fontsize=6.6)
    ax.text(X0 + 1.35, 1.75, "isolation barrier", color=RED, fontsize=6.4, ha="center", va="top")
    ax.text(X0 + 0.25, 9.3, "PWM in", fontsize=6.4, va="bottom")
    box(ax, X0 + 3.0, 5.4, 1.7, 2.4, "driver\noutput\nstage", fc="#EEF3F8", fontsize=6.6)
    ax.annotate("", xy=(X0 + 3.0, 7.1), xytext=(X0 + 2.45, 7.7),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=8))
    ax.annotate("", xy=(X0 + 3.0, 5.9), xytext=(X0 + 2.45, 4.9),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=8))
    # SiC MOSFET with Kelvin source
    xf, yf = X0 + 7.3, 6.6
    qf = d.add(elm.NFet().theta(0).reverse().anchor("center").at((xf, yf)))
    gx = qf.gate[0]
    wire(d, [qf.drain, (xf, 9.0)])
    ax.text(xf + 0.15, 9.0, "D", fontsize=6.6, va="center")
    ks_y = 5.1
    wire(d, [qf.source, (xf, 2.4)])
    ax.text(xf + 0.15, 2.4, "power\nsource", fontsize=6.2, va="center")
    dot(d, (xf, ks_y))
    wire(d, [(X0 + 4.7, yf), (X0 + 4.95, yf)])
    d.add(elm.Resistor().at((X0 + 4.95, yf)).to((gx - 0.25, yf)).scale(0.5))
    ax.text((X0 + 4.95 + gx - 0.25) / 2, yf + 0.3, "$R_G$", fontsize=6.4, ha="center", va="bottom")
    wire(d, [(gx - 0.25, yf), qf.gate])
    dot(d, (gx - 0.25, yf))
    # Miller clamp from gate node to Kelvin source
    cx = gx - 0.25
    wire(d, [(cx, yf), (cx, 5.6)])
    box(ax, cx - 0.65, 4.4, 1.3, 1.2, "Miller\nclamp", fc="#D6F0E6", fontsize=6.2)
    wire(d, [(cx, 4.4), (cx, 3.6)])
    dot(d, (cx, 3.6))
    # Kelvin return
    kx = xf - 0.45
    wire(d, [(xf, ks_y), (kx, ks_y), (kx, 3.6), (X0 + 3.85, 3.6), (X0 + 3.85, 5.4)])
    wire(d, [(X0 + 2.45, 3.6), (X0 + 3.85, 3.6)])
    dot(d, (X0 + 3.85, 3.6))
    ax.text(kx - 0.1, 3.4, "Kelvin source", fontsize=6.2, ha="right", va="top", color=BLUE)
    ax.text(X0 + 2.55, 1.0, "clamp: ≈ 0.5 Ω gate–source once\n$v_{GS}$ < 2 V; driver returns to the\n"
            "Kelvin source, not the power source", fontsize=6.0, ha="left", va="top", color=GREY)
    finish(ax, d, xlim=(-3.4, 22.4), ylim=(-3.4, 11.5))
    save(fig, "29", "fig-29-4-gate-driver-bootstrap")


# ----------------------------------------------------------------------------
# Figure 29.5 — turn-off ringing with and without RC snubber
# ----------------------------------------------------------------------------
def fig_29_5():
    t = np.arange(0, 100e-9, 2e-12)
    v0, _ = turn_off(t, t1=8e-9)
    v1, _ = turn_off(t, t1=8e-9, snubber=(20.0, 240e-12))
    fig = plt.figure(figsize=(6.8, 3.8))
    ax = fig.add_axes([0.09, 0.13, 0.60, 0.80])
    tn = t * 1e9
    ax.plot(tn, v0, color=BLUE, lw=1.5, label="no snubber")
    ax.plot(tn, v1, color=ORANGE, lw=1.8, label="RC snubber 20 Ω + 240 pF")
    ax.axhline(400, color=GREY, ls="--", lw=0.9)
    ax.axhline(650, color=RED, ls="--", lw=0.9)
    ax.text(99, 405, "400 V bus", fontsize=7.6, ha="right", va="bottom", color=GREY)
    ax.text(99, 640, "650 V rating", fontsize=7.6, ha="right", va="top", color=RED)
    k0, k1 = np.argmax(v0), np.argmax(v1)
    ax.annotate(f"{v0[k0]:.0f} V", xy=(tn[k0], v0[k0]), xytext=(tn[k0] + 8, 665), fontsize=7.6, color=BLUE,
                arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    ax.annotate(f"{v1[k1]:.0f} V", xy=(tn[k1], v1[k1]), xytext=(tn[k1] + 14, 560), fontsize=7.6, color=ORANGE,
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.text(60, 300, "ringing at 100 MHz,\ndecay time constant ≈ 40 ns", fontsize=7.6, color=BLUE)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 700)
    ax.set_xlabel("time (ns)")
    ax.set_ylabel("drain–source voltage (V)")
    ax.legend(loc="lower right", fontsize=7.6, bbox_to_anchor=(1.0, 0.1))
    ax.grid(True, color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    # inset circuit
    axc = fig.add_axes([0.71, 0.18, 0.29, 0.75])
    d = drawing(axc, fontsize=7, unit=1.6)
    d.add(elm.Inductor2(loops=2).at((0, 4.0)).to((2.0, 4.0)).label("$L_\\sigma$ 31.7 nH", loc="top", ofst=0.08))
    wire(d, [(2.0, 4.0), (2.4, 4.0)])
    wire(d, [(2.4, 4.0), (2.4, 3.6)])
    sw = d.add(elm.Switch().at((2.4, 3.6)).to((2.4, 1.6)))
    wire(d, [(2.4, 1.6), (2.4, 0.0)])
    wire(d, [(2.4, 3.6), (1.5, 3.6)])
    d.add(elm.Capacitor().at((1.5, 3.6)).to((1.5, 1.2)).label("$C_{oss}$\n80 pF", loc="top", ofst=0.05))
    wire(d, [(1.5, 1.2), (1.5, 0.5), (2.4, 0.5)])
    wire(d, [(2.4, 3.6), (3.4, 3.6)])
    d.add(elm.Resistor().at((3.4, 3.6)).to((3.4, 2.0)).scale(0.8).label("$R_s$\n20 Ω", loc="bottom", ofst=0.05))
    d.add(elm.Capacitor().at((3.4, 2.0)).to((3.4, 0.5)).scale(0.8).label("$C_s$\n240 pF", loc="bottom", ofst=0.05))
    wire(d, [(3.4, 0.5), (2.4, 0.5)])
    dot(d, (2.4, 3.6))
    dot(d, (2.4, 0.5))
    finish(axc, d, pad=0.3)
    axc.text(0.5, 0.06, "measured ring: 100 MHz alone,\n50 MHz with 240 pF added\n→ $C_p$ = 80 pF, $L_p$ = 31.7 nH",
             transform=axc.transAxes, fontsize=6.8, ha="center", va="top")
    print(f"  29.5: peaks {v0.max():.0f} V / {v1.max():.0f} V")
    save(fig, "29", "fig-29-5-snubber-ringing")


# ----------------------------------------------------------------------------
# Figure 29.6 — desaturation detection and soft turn-off
# ----------------------------------------------------------------------------
def fig_29_6():
    t = np.linspace(0, 12, 2401)
    pwm = np.ones_like(t)
    # gate: rise to 15 V by 0.5 us, soft turn-off from 5 us to 0 V at 7 us, then -8 V
    vg = np.where(t < 0, -8.0, 15 - 23 * np.exp(-t / 0.1))
    soft = (t >= 5.0) & (t < 7.0)
    vg = np.where(soft, 15 * (1 - np.clip((t - 5.0) / 2.0, 0, 1) ** 1.3), vg)
    vg = np.where(t >= 7.0, -8.0 + 8.0 * np.exp(-(t - 7.0) / 0.05), vg)
    # collector current
    ic = 600 * np.clip(t / 1.0, 0, 1) ** 1.0
    fall = (t >= 5.5) & (t < 7.0)
    ic = np.where(fall, 600 * (1 - (t - 5.5) / 1.5), ic)
    ic = np.where(t >= 7.0, 0.0, ic)
    # collector-emitter voltage
    vce = np.full_like(t, 600.0)
    vce = np.where(fall, 600 + 100 * np.clip(np.sin(np.pi * (t - 5.5) / 1.5), 0, 1) ** 0.6, vce)
    # DESAT pin
    vd = np.where(t < 3.0, 0.0, np.minimum(4.5 * (t - 3.0), 12.0))
    vd = np.where(t >= 5.05, 12.0 * np.exp(-(t - 5.05) / 0.15), vd)
    vd = np.where(t >= 5.05, np.minimum(vd, 9.0), vd)
    fault = np.where(t >= 5.0, 1.0, 0.0)

    fig, axs = plt.subplots(6, 1, figsize=(6.6, 5.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[0.55, 1, 1, 1, 1, 0.55], hspace=0.18))
    sigs = [("PWM", pwm, (-0.2, 1.3), None, BLUE), ("$v_{GE}$ (V)", vg, (-11, 19), [-8, 0, 15], GREEN),
            ("$i_C$ (A)", ic, (-60, 700), [0, 600], ORANGE), ("$v_{CE}$ (V)", vce, (0, 780), [0, 600], BLUE),
            ("DESAT (V)", vd, (-1, 14), [0, 9], PINK), ("FAULT", fault, (-0.2, 1.3), None, RED)]
    for ax, (lab, y, yl, yt, c) in zip(axs, sigs):
        ax.plot(t, y, color=c, lw=1.5)
        ax.set_ylim(*yl)
        ax.set_ylabel(lab, rotation=0, ha="right", va="center", fontsize=8)
        if yt is None:
            ax.set_yticks([])
            ax.spines["left"].set_visible(False)
        else:
            ax.set_yticks(yt)
            ax.tick_params(axis="y", labelsize=7)
        for x in (3.0, 5.0, 7.0, 10.0):
            ax.axvline(x, color=GRID, lw=0.8, zorder=0)
    axs[0].text(0.15, 0.45, "command on at t = 0 into a short circuit; the driver overrides it after the fault", fontsize=7, va="center")
    axs[1].text(7.2, 8, "soft turn-off through\nlarge resistor", fontsize=7, va="center")
    axs[2].text(1.2, 450, "6 × rated (600 A for a 100 A IGBT)", fontsize=7, va="center")
    axs[2].text(7.15, 470, "falls over 1.5 µs (5.5–7 µs)", fontsize=7, va="center")
    axs[3].text(1.2, 330, "device desaturated: full 600 V bus across it", fontsize=7, va="center")
    axs[3].text(7.2, 690, "overshoot limited to 700 V", fontsize=7, va="center")
    axs[4].axhline(9.0, color=PINK, ls="--", lw=0.8)
    axs[4].text(11.9, 9.6, "9 V threshold", fontsize=7, ha="right", va="bottom", color=PINK)
    axs[4].annotate("", xy=(3.0, 3.0), xytext=(0.0, 3.0),
                    arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=8))
    axs[4].text(1.5, 3.8, "blanking 3 µs", fontsize=7, ha="center", va="bottom")
    axs[4].text(3.1, 11.5, "$C_{BLK}$ charging\n(filter) 2 µs", fontsize=7, ha="left", va="center")
    axs[5].text(5.15, 0.5, "FAULT asserted at 5 µs, latched", fontsize=7, va="center", color=RED)
    # withstand time
    ax = axs[2]
    ax.annotate("", xy=(10.0, 660), xytext=(0.0, 660),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.9, mutation_scale=8))
    ax.text(3.6, 668, "short-circuit withstand time 10 µs", fontsize=7, color=RED, ha="center", va="bottom")
    ax.annotate("", xy=(10.0, 150), xytext=(7.0, 150),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=0.9, mutation_scale=8))
    ax.text(8.5, 170, "margin 3 µs", fontsize=7, color=GREEN, ha="center", va="bottom")
    axs[-1].set_xlim(0, 12)
    axs[-1].set_xlabel("time (µs)")
    axs[-1].set_xticks(range(0, 13, 1))
    fig.align_ylabels(axs)
    save(fig, "29", "fig-29-6-desat-protection")


if __name__ == "__main__":
    fig_29_1()
    fig_29_2()
    fig_29_3()
    fig_29_4()
    fig_29_5()
    fig_29_6()
