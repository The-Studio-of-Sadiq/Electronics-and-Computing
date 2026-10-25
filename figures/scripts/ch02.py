"""Figures for Chapter 2 — Semiconductor Junction Devices.

Run from the repository root:  python figures/scripts/ch02.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from scipy.optimize import brentq, minimize_scalar  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, new_fig, save  # noqa: E402

schemdraw.use("matplotlib")

Q = 1.602176634e-19
EPS0 = 8.8541878128e-14          # F/cm
K_EV = 8.617333e-5
SHADE = "#E9E9E9"


# ---------------------------------------------------------------------------
def fig_2_1():
    """Depletion-region electrostatics of a p+n junction at 5 V reverse bias."""
    NA, ND, ni, VR = 1e19, 1e16, 1.0e10, 5.0
    eps = 11.7 * EPS0
    vt = 0.02585
    vbi = vt * np.log(NA * ND / ni ** 2)
    W = np.sqrt(2 * eps * (vbi + VR) / (Q * ND))           # cm (n side)
    xp = W * ND / NA                                        # cm (p side)
    Emax = Q * ND * W / eps                                 # V/cm
    Wum, xpum = W * 1e4, xp * 1e4
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(6.4, 5.2), sharex=True)
    x = np.linspace(-0.1, 1.2, 2001)                         # um
    # (a) charge density, normalised to q*ND
    a1.add_patch(Rectangle((0, 0), Wum, 1.0, fc=COLORS[0] + "55", ec=COLORS[0], lw=1.4))
    drawn_w = 0.012                                         # exaggerated width
    a1.add_patch(Rectangle((-drawn_w, -2.6), drawn_w, 2.6, fc=COLORS[1] + "55", ec=COLORS[1], lw=1.4))
    a1.plot([-drawn_w - 0.004, -drawn_w + 0.016], [-2.45, -2.35], color=INK, lw=0.8)
    a1.plot([-drawn_w - 0.004, -drawn_w + 0.016], [-2.6, -2.5], color=INK, lw=0.8)
    a1.text(0.03, -1.6, f"−q$N_A$ = −1000 q$N_D$, width {xpum*1e3:.2f} nm (not to scale)",
            fontsize=8, color=COLORS[1], va="center")
    a1.text(Wum / 2, 1.18, "+q$N_D$ (ionised donors)", fontsize=8.5, ha="center", color=COLORS[0])
    a1.axhline(0, color=INK, lw=0.6)
    a1.set_ylim(-2.8, 1.7)
    a1.set_yticks([-2, -1, 0, 1])
    a1.set_ylabel("ρ / q$N_D$")
    a1.text(-0.09, 1.25, "p$^+$", fontsize=10)
    a1.text(1.12, 1.25, "n", fontsize=10)
    # (b) field
    E = np.where((x >= 0) & (x <= Wum), Emax * (1 - x / Wum), 0.0)
    E = np.where((x < 0) & (x >= -xpum), Emax * (1 + x / xpum), E)
    a2.plot(x, E / 1e3, color=COLORS[0])
    a2.axhline(400, color=COLORS[1], ls="--", lw=1.1)
    a2.text(0.60, 388, "critical field ≈ 400 kV/cm (breakdown)", fontsize=8, color=COLORS[1], va="top")
    a2.annotate(f"$\\mathcal{{E}}_{{max}}$ = {Emax/1e3:.0f} kV/cm", xy=(0.0, Emax / 1e3), xytext=(0.10, 230),
                fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.6))
    a2.set_ylim(0, 480)
    a2.set_ylabel("|$\\mathcal{E}$| (kV/cm)")
    # (c) potential
    phi = np.where(x <= 0, 0.0, 0.0)
    m = (x > 0) & (x <= Wum)
    phi = np.where(m, (vbi + VR) * (1 - (1 - x / Wum) ** 2), phi)
    phi = np.where(x > Wum, vbi + VR, phi)
    a3.plot(x, phi, color=COLORS[0])
    a3.annotate("", xy=(1.1, vbi + VR), xytext=(1.1, 0),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9))
    a3.text(1.08, (vbi + VR) / 2, f"$V_{{bi}}+V_R$\n= {vbi+VR:.2f} V", fontsize=8.5, ha="right", va="center")
    a3.set_ylim(-0.4, 7.0)
    a3.set_ylabel("potential (V)")
    a3.set_xlabel("position x (µm), junction at x = 0")
    a3.set_xlim(-0.1, 1.2)
    for ax in (a1, a2, a3):
        ax.axvline(0, color="#999", lw=0.6, ls=":")
        ax.axvline(Wum, color="#999", lw=0.6, ls=":")
    a2.annotate("", xy=(Wum, 445), xytext=(0, 445), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9))
    a2.text(Wum / 2, 448, f"W = {Wum:.3f} µm", fontsize=8.5, ha="center", va="bottom",
            bbox=dict(fc="white", ec="none", pad=0.3))
    fig.align_ylabels()
    fig.tight_layout(h_pad=0.4)
    save(fig, "02", "fig-2-1-depletion-electrostatics")


# ---------------------------------------------------------------------------
def fig_2_2():
    """Real diode: four forward regimes; reverse leakage and breakdown."""
    vt = 0.02585
    Is, Ir0, IKF, Rs = 1.75e-14, 1.3e-10, 0.03, 0.5
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.9))

    def ij(vj):
        e = Is * np.expm1(vj / vt)
        return Ir0 * np.expm1(vj / (2 * vt)) + e / np.sqrt(1 + e / IKF)

    vj = np.linspace(1e-4, 1.2, 4000)
    i = ij(vj)
    v = vj + i * Rs
    m = v <= 1.2
    a1.semilogy(v[m], i[m], color=COLORS[0], lw=2.0, label="real diode")
    # reference slopes
    vv = np.linspace(0, 1.2, 10)
    a1.semilogy(vv, Is * np.exp(vv / vt), "--", color=COLORS[2], lw=1.0, label="60 mV/decade (n = 1)")
    a1.semilogy(vv, Ir0 * np.exp(vv / (2 * vt)), "--", color=COLORS[1], lw=1.0, label="120 mV/decade (n = 2)")
    a1.set_ylim(1e-12, 1)
    a1.set_xlim(0, 1.2)
    a1.set_yticks([1e-12, 1e-9, 1e-6, 1e-3, 1])
    a1.set_yticklabels(["1 pA", "1 nA", "1 µA", "1 mA", "1 A"])
    a1.set_xlabel("forward voltage V (V)")
    a1.set_ylabel("forward current I")
    a1.set_title("forward bias", fontsize=9.5)
    lab = dict(fontsize=7.8, ha="left", va="center")
    a1.text(0.02, 1e-7, "① recombination\n     (n ≈ 2)", **lab)
    a1.text(0.66, 1e-5, "② diffusion (n ≈ 1)", **lab)
    a1.annotate("③ high injection", xy=(0.77, 5e-2), xytext=(0.12, 1.5e-2), fontsize=7.8, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.annotate("④ ohmic ($R_S$ = 0.5 Ω)", xy=(1.02, 0.42), xytext=(0.12, 0.3), fontsize=7.8, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.legend(loc="lower right", fontsize=7.2)
    # reverse
    VR = np.linspace(0, 120, 2000)
    vbi = 0.9
    igen = 3e-9 * np.sqrt((VR + vbi) / (1 + vbi))
    bv, mexp = 100.0, 10.0
    with np.errstate(divide="ignore"):
        M = np.where(VR < bv, 1 / (1 - (VR / bv) ** mexp), np.inf)
    for scale, col, lab2 in ((1, COLORS[0], "25 °C"), (1000, COLORS[1], "125 °C (×1000)")):
        ir = igen * scale * M
        ok = ir < 2e-2
        vplot = np.append(VR[ok], VR[ok][-1])
        iplot = np.append(ir[ok], 2e-2)
        a2.semilogy(vplot, iplot, color=col, label=lab2)
    a2.plot([1, 75], [3e-9, 3e-9 * np.sqrt(75.9 / 1.9)], "o", color=COLORS[0], ms=4)
    a2.text(4, 1.8e-9, "3 nA at 1 V", fontsize=7.8)
    a2.text(60, 9e-9, "≈20 nA at 75 V", fontsize=7.8)
    a2.text(45, 4e-8, "generation leakage ∝ $\\sqrt{V_{bi}+V_R}$", fontsize=7.8, ha="center")
    a2.annotate("breakdown\n$V_{BR}$ = 100 V", xy=(100, 1e-4), xytext=(102, 1e-6), fontsize=7.8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a2.set_xlim(0, 120)
    a2.set_ylim(1e-10, 1e-2)
    a2.set_yticks([1e-10, 1e-8, 1e-6, 1e-4, 1e-2])
    a2.set_yticklabels(["100 pA", "10 nA", "1 µA", "100 µA", "10 mA"])
    a2.set_xlabel("reverse voltage $V_R$ (V)")
    a2.set_ylabel("reverse current |I|")
    a2.set_title("reverse bias", fontsize=9.5)
    a2.legend(loc="upper left", fontsize=7.8)
    fig.tight_layout(w_pad=1.2)
    save(fig, "02", "fig-2-2-real-diode-characteristic")


# ---------------------------------------------------------------------------
def fig_2_3():
    """Reverse recovery, soft versus snappy."""
    t = np.linspace(-100, 300, 4001)                 # ns
    IF, didt, ta = 10.0, -0.1, 50.0                  # A, A/ns, ns
    irrm = didt * ta                                 # -5 A

    def current(tb, ring):
        i = np.where(t < ta, didt * t, 0.0)            # 10 A at -100 ns, zero at t = 0
        i = np.where((t >= ta) & (t < ta + tb), irrm * (1 - (t - ta) / tb), i)
        if ring:
            tt = t - (ta + tb)
            i = np.where(t >= ta + tb, 0.9 * np.exp(-tt / 30) * np.sin(2 * np.pi * tt / 25.0), i)
        return i

    def voltage(tb, overshoot):
        v = np.where(t < 0, 1.0, 1.0 - t / ta * 0.8)    # ~+1 V while conducting, falling to ~0 at t_a
        s = np.clip((t - ta) / tb, 0, 1)
        if overshoot:
            tt = t - (ta + tb)
            ring = np.where(tt > 0, -80 * np.exp(-tt / 30) * np.cos(2 * np.pi * tt / 25.0), -80 * s)
            v = np.where(t >= ta, -400 * s + ring, v)
        else:
            v = np.where(t >= ta, -400 * (3 * s ** 2 - 2 * s ** 3), v)
        return v

    i_soft, i_snap = current(50.0, False), current(10.0, True)
    v_soft, v_snap = voltage(50.0, False), voltage(10.0, True)
    fig, ax = new_fig(6.6, 4.0)
    axv = ax.twinx()
    axv.spines["right"].set_visible(True)
    m = (t >= 0) & (t <= ta + 50)
    ax.fill_between(t[m], i_soft[m], 0, color=COLORS[0], alpha=0.18, lw=0)
    ax.plot(t, i_soft, color=COLORS[0], label="current, soft (S = 1)")
    ax.plot(t, i_snap, "--", color=COLORS[0], lw=1.4, label="current, snappy (S = 0.2)")
    axv.plot(t, v_soft, color=COLORS[1], label="voltage, soft")
    axv.plot(t, v_snap, "--", color=COLORS[1], lw=1.4, label="voltage, snappy")
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xlim(-100, 300)
    ax.set_ylim(-8, 12)
    # align zeros: left zero at fraction 8/20 = 0.4 -> right limits (-a, 1.5a)
    axv.set_ylim(-500, 750)
    axv.set_yticks([-500, -400, -300, -200, -100, 0, 50])
    ax.set_xlabel("time t (ns)")
    ax.set_ylabel("diode current (A)", color=COLORS[0])
    axv.set_ylabel("diode voltage (V)", color=COLORS[1])
    # annotations
    ax.annotate("$I_F$ = 10 A, d$i$/d$t$ = −100 A/µs", xy=(-60, 10), xytext=(-95, 10.8), fontsize=8)
    ax.plot([ta], [irrm], "o", color=INK, ms=4)
    ax.annotate("$I_{RRM}$ = −5 A at $t_a$", xy=(ta, irrm), xytext=(-95, -5.6), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    yb = 4.5
    ax.annotate("", xy=(0, yb), xytext=(ta, yb), arrowprops=dict(arrowstyle="<|-|>", lw=0.8))
    ax.text(ta / 2, yb + 0.25, "$t_a$ = 50 ns", ha="center", fontsize=8)
    ax.annotate("", xy=(ta, yb), xytext=(ta + 50, yb), arrowprops=dict(arrowstyle="<|-|>", lw=0.8))
    ax.text(ta + 25, yb + 0.25, "$t_b$ = 50 ns", ha="center", fontsize=8)
    ax.annotate("", xy=(0, 6.6), xytext=(100, 6.6), arrowprops=dict(arrowstyle="<|-|>", lw=0.8))
    ax.text(50, 6.85, "$t_{rr}$ = 100 ns (soft)", ha="center", fontsize=8)
    for xx in (0, ta, ta + 50):
        ax.axvline(xx, color="#AAA", lw=0.6, ls=":")
    ax.annotate("$Q_{rr}$ = 250 nC (shaded)", xy=(28, -1.6), xytext=(-95, -2.6), fontsize=8.5, color=COLORS[0],
                arrowprops=dict(arrowstyle="-", lw=0.6, color=COLORS[0]))
    ax.text(-95, 0.45, "v ≈ +1 V while conducting", fontsize=8, color=COLORS[1])
    axv.annotate("−480 V overshoot (snappy, $t_b$ = 10 ns)", xy=(ta + 10 + 1.5, -478), xytext=(125, -470),
                 fontsize=8, color=COLORS[1], arrowprops=dict(arrowstyle="-", lw=0.6, color=COLORS[1]))
    axv.axhline(-400, color=COLORS[1], lw=0.6, ls=":")
    axv.text(295, -390, "400 V bus", fontsize=8, color=COLORS[1], ha="right", va="bottom")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = axv.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=7.5, ncol=1)
    save(fig, "02", "fig-2-3-reverse-recovery")


# ---------------------------------------------------------------------------
def fig_2_4():
    """Illuminated junction: three operating regions."""
    vt, Is = 0.025852, 10e-12
    V = np.linspace(-5, 1, 3000)
    fig, ax = new_fig(6.4, 4.2)
    ax.fill_between([-5, 0], -12, 0, color="#DCE8F3", lw=0, zorder=0)
    ax.fill_between([0, 1], -12, 0, color="#F8E3D3", lw=0, zorder=0)
    for iph, col, lab in ((0.0, INK, "dark"), (2.75e-6, COLORS[2], "5 µW (2.75 µA)"),
                          (5.5e-6, COLORS[0], "10 µW at 850 nm (5.5 µA)")):
        I = Is * np.expm1(V / vt) - iph
        m = I < 13e-6
        ax.plot(V[m], I[m] * 1e6, color=col, label=lab)
    # load line: 3 V bias through 100 kOhm
    ax.plot(V, -(V + 3) / 100e3 * 1e6, "--", color=COLORS[3], lw=1.3, label="load line, 3 V through 100 kΩ")
    vq = -3 + 5.5e-6 * 100e3
    ax.plot(vq, -5.5, "o", color=COLORS[3], ms=4.5, zorder=5)
    voc = vt * np.log(1 + 5.5e-6 / Is)
    ax.plot([voc], [0], "o", color=COLORS[0], ms=4.5, zorder=5)
    ax.plot([0], [-5.5], "o", color=COLORS[0], ms=4.5, zorder=5)
    ax.annotate(f"$V_{{oc}}$ ≈ {voc:.2f} V", xy=(voc, 0), xytext=(0.42, 2.2), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("$I_{sc}$ = −5.5 µA", xy=(0, -5.5), xytext=(0.12, -8.2), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.axhline(0, color=INK, lw=0.7)
    ax.axvline(0, color=INK, lw=0.7)
    ax.text(-4.9, -10.9, "photoconductive mode\nreverse bias: I ≈ −$I_{ph}$, linear, fast",
            fontsize=8.5, va="center")
    ax.text(0.5, -10.5, "photovoltaic /\nsolar cell\n(power delivered)", fontsize=8, ha="center", va="center")
    ax.text(0.5, 9.0, "forward\ninjection:\nLED if\ndirect gap", fontsize=8, ha="center", va="center")
    ax.set_xlim(-5, 1)
    ax.set_ylim(-12, 12)
    ax.set_xlabel("junction voltage V (V)")
    ax.set_ylabel("current I (µA)")
    ax.legend(loc="upper left", fontsize=8)
    save(fig, "02", "fig-2-4-illuminated-junction-quadrants")


# ---------------------------------------------------------------------------
def cell_current(V, T=298.15, Iph=9.80, I0=1.0e-10, n=1.05, Rs=0.003, Rsh=20.0):
    """Single-diode model as in the chapter listing."""
    vt = K_EV * T
    i0 = I0 * (T / 298.15) ** (3 / n) * np.exp(1.12 / (n * K_EV) * (1 / 298.15 - 1 / T))
    iph = Iph * (1 + 0.0005 * (T - 298.15))
    f = lambda I: iph - i0 * np.expm1((V + I * Rs) / (n * vt)) - (V + I * Rs) / Rsh - I  # noqa: E731
    return brentq(f, -10 * Iph, 2 * Iph)


def cell_summary(**p):
    isc = cell_current(0.0, **p)
    voc = brentq(lambda V: cell_current(V, **p), 0.0, 0.8)
    r = minimize_scalar(lambda V: -V * cell_current(V, **p), bounds=(0, voc), method="bounded")
    vm = r.x
    im = cell_current(vm, **p)
    return isc, voc, vm, im


def fig_2_5():
    """Solar cell I-V and P-V."""
    fig, ax = new_fig(6.5, 4.1)
    axp = ax.twinx()
    axp.spines["right"].set_visible(True)
    cases = [("STC, 25 °C", {}, "-"), ("$R_s$ = 10 mΩ", {"Rs": 0.010}, "--"),
             ("cell at 60 °C", {"T": 333.15}, ":")]
    for k, (lab, p, ls) in enumerate(cases):
        isc, voc, vm, im = cell_summary(**p)
        V = np.linspace(0, voc, 400)
        I = np.array([cell_current(v, **p) for v in V])
        ax.plot(V, I, ls, color=COLORS[0], lw=1.8 if ls != ":" else 2.2, label=f"I–V, {lab}")
        axp.plot(V, V * I, ls, color=COLORS[1], lw=1.8 if ls != ":" else 2.2)
        axp.plot(vm, vm * im, "o", color=COLORS[1], ms=4.5)
        if k == 0:
            ax.add_patch(Rectangle((0, 0), vm, im, fc=COLORS[0], alpha=0.10, lw=0))
            ax.add_patch(Rectangle((0, 0), voc, isc, fc="none", ec="#777", lw=0.8, ls=(0, (4, 3))))
            ax.plot(vm, im, "o", color=COLORS[0], ms=4.5)
            ax.text(0.40, 2.3, "shaded $V_{mp}I_{mp}$ inside dashed\n$V_{oc}I_{sc}$: FF = 0.797", fontsize=8.5,
                    ha="center", va="center")
            axp.annotate(f"MPP {vm:.3f} V, {im:.2f} A, {vm*im:.2f} W", xy=(vm, vm * im),
                         xytext=(0.24, 5.0), fontsize=8, arrowprops=dict(arrowstyle="-", lw=0.6))
            ax.annotate(f"$V_{{oc}}$ = {voc:.3f} V", xy=(voc, 0), xytext=(0.655, 1.2), fontsize=8,
                        ha="right", arrowprops=dict(arrowstyle="-", lw=0.6))
            ax.text(0.01, isc - 0.15, f"$I_{{sc}}$ = {isc:.2f} A", fontsize=8, va="top")
        elif k == 1:
            axp.annotate(f"{vm:.3f} V, {vm*im:.2f} W", xy=(vm, vm * im), xytext=(0.25, 4.45), fontsize=8,
                         arrowprops=dict(arrowstyle="-", lw=0.6))
        else:
            axp.annotate(f"{vm:.3f} V, {vm*im:.2f} W", xy=(vm, vm * im), xytext=(0.36, 3.0), fontsize=8,
                         arrowprops=dict(arrowstyle="-", lw=0.6))
            ax.annotate(f"$V_{{oc}}$ = {voc:.3f} V\n(60 °C)", xy=(voc, 0), xytext=(0.53, 0.35), fontsize=8,
                        ha="right", arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.set_xlim(0, 0.72)
    ax.set_ylim(0, 10.5)
    axp.set_ylim(0, 6)
    ax.set_xlabel("cell voltage V (V)")
    ax.set_ylabel("current I (A)", color=COLORS[0])
    axp.set_ylabel("power P (W)", color=COLORS[1])
    axp.plot([], [], color=COLORS[1], label="P–V (same line styles)")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = axp.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7.8, bbox_to_anchor=(0.0, 0.86))
    save(fig, "02", "fig-2-5-solar-cell-iv")


# ---------------------------------------------------------------------------
def fig_2_6():
    """ISO 7637-2 pulse 2a clamped by an SMBJ24A."""
    t = np.linspace(0, 150, 3001)                   # us
    UA, Us, Ri = 13.5, 112.0, 2.0
    VBR, rd = 28.0, 0.708
    tau = 50.0 / np.log(10)                         # falls to 10 % at 50 us
    shape = np.where(t < 1.0, t / 1.0, np.exp(-(t - 1.0) / tau))
    voc = UA + (Us - UA) * shape
    itvs = np.clip((voc - VBR) / (Ri + rd), 0, None)
    vline = np.where(itvs > 0, VBR + rd * itvs, voc)
    fig = plt.figure(figsize=(6.6, 4.3))
    ax = fig.add_axes([0.10, 0.12, 0.76, 0.84])
    axi = ax.twinx()
    axi.spines["right"].set_visible(True)
    ax.plot(t, voc, "--", color=INK, lw=1.3, label="open-circuit pulse (no TVS)")
    ax.plot(t, vline, color=COLORS[0], lw=2.0, label="line voltage with TVS")
    axi.plot(t, itvs, color=COLORS[1], lw=1.4, label="TVS current")
    for lvl, txt in ((24, "$V_{RWM}$ = 24 V"), (28, "$V_{BR}$ = 28 V"), (50, "$V_C$ = 50 V")):
        ax.axhline(lvl, color="#777", ls=":", lw=0.9)
        ax.text(148, lvl + (1.0 if lvl != 24 else -1.0), txt, fontsize=7.8, ha="right",
                va="bottom" if lvl != 24 else "top", color="#444")
    ip = itvs.max()
    axi.annotate(f"peak {ip:.0f} A", xy=(t[itvs.argmax()], ip), xytext=(9, 31), fontsize=8,
                 color=COLORS[1], arrowprops=dict(arrowstyle="-", lw=0.6, color=COLORS[1]))
    ax.annotate("112 V, 1 µs rise", xy=(1.0, 112), xytext=(8, 113), fontsize=8, va="center")
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 120)
    axi.set_ylim(0, 40)
    ax.set_xlabel("time (µs)")
    ax.set_ylabel("voltage (V)")
    axi.set_ylabel("TVS current (A)", color=COLORS[1])
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = axi.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="center right", fontsize=8, bbox_to_anchor=(1.0, 0.60))
    # inset circuit
    axc = fig.add_axes([0.40, 0.70, 0.45, 0.25])
    axc.axis("off")
    d = schemdraw.Drawing(canvas=axc, show=False)
    d.config(fontsize=7.5, unit=1.6, lw=1.0)
    src = d.add(elm.SourceV().up())
    d.add(elm.Resistor().right().label("$R_i$ = 2 Ω", ofst=0.08))
    n1 = d.add(elm.Dot())
    d.add(elm.Line().right(1.4))
    d.add(elm.Dot(open=True).label("to regulator\ninput (13.5 V line)", loc="right", ofst=0.1))
    d.here = n1.end
    d.add(elm.DiodeTVS().down().reverse().label("SMBJ24A", loc="bottom", ofst=0.1))
    d.add(elm.Line().left().to(src.start))
    d.add(elm.Ground().at(src.start))
    d.draw(show=False)
    axc.set_aspect("equal")
    x0, y0 = src.center
    axc.text(x0 - 0.75, y0, "$U_s$ = 112 V\npulse 2a", fontsize=7.5, ha="right", va="center")
    axc.set_xlim(x0 - 3.6, axc.get_xlim()[1])
    save(fig, "02", "fig-2-6-tvs-clamping")


if __name__ == "__main__":
    fig_2_1()
    fig_2_2()
    fig_2_3()
    fig_2_4()
    fig_2_5()
    fig_2_6()
