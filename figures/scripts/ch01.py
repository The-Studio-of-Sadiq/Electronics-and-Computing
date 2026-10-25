"""Figures for Chapter 1 — Electronic Device Fundamentals.

Run from the repository root:  python figures/scripts/ch01.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

from figstyle import COLORS, INK, GRID, new_fig, save  # noqa: E402

K_B, Q_E = 1.380649e-23, 1.602176634e-19
IS0, N_D, RS_D = 2.52e-9, 1.752, 0.568      # 1N4148 SPICE parameters
SHADE = "#E6E6E6"


def vt(T):
    return K_B * T / Q_E


def is_T(T, T0=298.15, xti=3.0, eg=1.11, n=N_D):
    """Saturation current scaled from T0 with the SPICE temperature law."""
    return IS0 * (T / T0) ** (xti / n) * np.exp(eg / (n * vt(T)) * (T / T0 - 1.0))


def diode_v(i, T=300.0, Is=IS0, n=N_D, Rs=RS_D):
    """Terminal voltage of the exponential-plus-Rs diode for forward current i (A)."""
    i = np.asarray(i, dtype=float)
    return n * vt(T) * np.log(i / Is + 1.0) + i * Rs


def diode_i(v, T=300.0, Is=IS0, n=N_D, Rs=RS_D):
    """Current of the diode at terminal voltage v (solves the implicit Rs equation)."""
    v = np.atleast_1d(np.asarray(v, dtype=float))
    out = np.empty_like(v)
    for k, vk in enumerate(v):
        if vk <= 0:
            out[k] = Is * np.expm1(vk / (n * vt(T)))
        else:
            out[k] = brentq(lambda i: diode_v(i, T, Is, n, Rs) - vk, 0.0, vk / Rs + 1e-12)
    return out


def bias_point(Vs, R, T=300.0):
    """Intersection of load line (Vs, R) with the diode characteristic."""
    i = brentq(lambda i: Vs - i * R - diode_v(i, T), 0.0, Vs / R)
    return diode_v(i, T), i


# ---------------------------------------------------------------------------
def fig_1_1():
    """Five static characteristics with power quadrants."""
    fig, axs = plt.subplots(1, 5, figsize=(6.8, 2.6), sharey=True)
    titles = ["(a) 1 kΩ resistor", "(b) 5 V source", "(c) 2 mA source",
              "(d) 1N4148 diode", "(e) 5.1 V Zener"]
    v = np.linspace(-6, 6, 1201)
    for k, ax in enumerate(axs):
        ax.fill_between([0, 6], 0, 10, color=SHADE, lw=0, zorder=0)
        ax.fill_between([-6, 0], -10, 0, color=SHADE, lw=0, zorder=0)
        ax.axhline(0, color=INK, lw=0.6)
        ax.axvline(0, color=INK, lw=0.6)
        ax.set_xlim(-6, 6)
        ax.set_ylim(-10, 10)
        ax.set_xticks([-5, 0, 5])
        ax.set_title(titles[k], fontsize=8.5)
        ax.tick_params(labelsize=8)
        ax.set_xlabel("v (V)", fontsize=8.5)
    c = COLORS[0]
    axs[0].plot(v, v / 1.0, color=c)                       # 1 mA/V
    axs[1].plot([5, 5], [-10, 10], color=c)
    axs[2].plot([-6, 6], [-2, -2], color=c)
    # diode
    vd = np.linspace(-6, 0.75, 800)
    axs[3].plot(vd, diode_i(vd) * 1e3, color=c)
    # Zener: forward exponential, flat reverse, breakdown at -5.1 V (rz ~ 30 ohm)
    vz = np.linspace(-6, 0.8, 1400)
    iz = diode_i(vz, Is=1e-12, n=1.0, Rs=1.0) * 1e3
    brk = vz < -5.1
    iz[brk] = (vz[brk] + 5.1) / 30.0 * 1e3
    axs[4].plot(vz, iz, color=c)
    axs[0].set_ylabel("i (mA)")
    axs[0].text(3.0, 7.6, "I", ha="center", fontsize=8, color="#555")
    axs[0].text(-3.0, 7.6, "II", ha="center", fontsize=8, color="#555")
    axs[0].text(-3.0, -9.0, "III", ha="center", fontsize=8, color="#555")
    axs[0].text(3.0, -9.0, "IV", ha="center", fontsize=8, color="#555")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(fc=SHADE, ec="none", label="quadrants I, III: absorbs power (vi > 0)"),
                        Patch(fc="white", ec="#999", label="quadrants II, IV: delivers power (vi < 0)")],
               loc="lower center", ncol=2, fontsize=8.5, bbox_to_anchor=(0.5, -0.06))
    fig.tight_layout(rect=(0, 0.08, 1, 1), w_pad=0.6)
    save(fig, "01", "fig-1-1-iv-characteristics")


def fig_1_2():
    """Load-line solution, two cases."""
    fig, ax = new_fig(6.4, 3.8)
    v = np.linspace(0, 1.4, 600)
    i = diode_i(v) * 1e3
    ax.plot(v, i, color=COLORS[0], label="1N4148 (exponential + $R_S$)")
    ax.plot(v, (5 - v) / 1.0, color=COLORS[1], label="load line A: 5 V, 1 kΩ")
    va, ia = bias_point(5.0, 1e3)
    ax.plot(va, ia * 1e3, "o", color=INK, ms=5, zorder=5)
    ax.annotate(f"$Q_A$ = ({va:.3f} V, {ia*1e3:.2f} mA)", xy=(va, ia * 1e3), xytext=(0.72, 5.2),
                fontsize=9, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.set_xlim(0, 1.4)
    ax.set_ylim(0, 6)
    ax.set_xlabel("diode voltage v (V)")
    ax.set_ylabel("diode current i (mA)")
    ax.legend(loc="upper left", fontsize=8.5)
    # inset
    axi = ax.inset_axes([0.54, 0.12, 0.43, 0.45])
    vv = np.linspace(0.3, 0.8, 400)
    axi.plot(vv, diode_i(vv) * 1e3, color=COLORS[0])
    axi.plot(vv, (1.2 - vv) / 10.0, color=COLORS[2])
    vb, ib = bias_point(1.2, 10e3)
    axi.plot(vb, ib * 1e3, "o", color=INK, ms=4, zorder=5)
    axi.axvline(0.7, color=INK, ls="--", lw=0.9)
    axi.plot(0.7, 0.050, "s", color=COLORS[3], ms=4, zorder=5)
    axi.annotate(f"$Q_B$ = ({vb:.3f} V,\n{ib*1e3:.3f} mA)", xy=(vb, ib * 1e3), xytext=(0.31, 0.21),
                 fontsize=7.5, arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    axi.annotate("0.7 V model:\n0.050 mA", xy=(0.7, 0.050), xytext=(0.715, 0.13), fontsize=7.5)
    axi.text(0.795, 0.335, "line B: 1.2 V, 10 kΩ", fontsize=7, color=COLORS[2], ha="right", va="top",
             bbox=dict(fc="white", ec="none", pad=0.5))
    axi.set_xlim(0.3, 0.8)
    axi.set_ylim(0, 0.35)
    axi.tick_params(labelsize=7)
    axi.set_xlabel("v (V)", fontsize=7.5, labelpad=1)
    axi.set_ylabel("i (mA)", fontsize=7.5, labelpad=1)
    axi.spines["top"].set_visible(True)
    axi.spines["right"].set_visible(True)
    save(fig, "01", "fig-1-2-diode-load-line")


def fig_1_3():
    """Diode model hierarchy, linear and log axes."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.6))
    v = np.linspace(0, 1.0, 1000)
    iexp = diode_i(v) * 1e3
    v0, rD = 0.572, 12.2
    ipwl = np.where(v > v0, (v - v0) / rD * 1e3, 0.0)
    for ax, log in ((a1, False), (a2, True)):
        lo = 1e-3 if log else 0
        hi = 100 if log else 20
        ax.plot([0, 0], [lo, hi], color=COLORS[3], lw=2.2, label="(1) ideal switch")
        ax.plot([0.7, 0.7], [lo, hi], color=COLORS[1], label="(2) constant drop 0.7 V")
        if log:
            m = v > v0 + 1e-4
            ax.plot(v[m], ipwl[m], color=COLORS[2], label="(3) piecewise linear")
        else:
            ax.plot(v, ipwl, color=COLORS[2], label="(3) piecewise linear")
        ax.plot(v, iexp, color=COLORS[0], label="(4) exponential + $R_S$")
        ax.plot([0.584, 0.694], [1, 10], "o", color=INK, ms=4.5, zorder=6)
        ax.set_xlim(-0.02, 1.0)
        ax.set_xlabel("v (V)")
    a1.set_ylim(0, 20)
    a1.set_ylabel("i (mA)")
    a1.annotate("1 mA, 0.584 V", xy=(0.584, 1), xytext=(0.25, 3.2), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.annotate("10 mA, 0.694 V", xy=(0.694, 10), xytext=(0.28, 12), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a1.legend(loc="upper left", fontsize=7.5, bbox_to_anchor=(0.0, 1.0))
    a1.set_title("linear current axis", fontsize=9.5)
    a2.set_yscale("log")
    a2.set_ylim(1e-3, 100)
    a2.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 100])
    a2.set_yticklabels(["1 µA", "10 µA", "100 µA", "1 mA", "10 mA", "100 mA"])
    a2.axhspan(1e-3, 0.5, color=SHADE, lw=0, zorder=0)
    a2.text(0.03, 0.012, "below 0.5 mA:\nPWL and 0.7 V models\nwrong by decades", fontsize=8, va="center")
    a2.set_title("logarithmic current axis", fontsize=9.5)
    fig.tight_layout()
    save(fig, "01", "fig-1-3-diode-model-hierarchy")


def fig_1_4():
    """Small-signal linearisation and large-signal distortion."""
    fig = plt.figure(figsize=(6.8, 4.2))
    gs = GridSpec(2, 2, height_ratios=[2.3, 1], width_ratios=[1, 1.05], hspace=0.08, wspace=0.32)
    ax = fig.add_subplot(gs[0, 0])
    axs = fig.add_subplot(gs[1, 0], sharex=ax)
    axr = fig.add_subplot(gs[:, 1])
    T = 300.0
    VQ, IQ = diode_v(1e-3, T), 1e-3
    rd = N_D * vt(T) / IQ
    v = np.linspace(0.52, 0.64, 400)
    ax.plot(v, diode_i(v, T) * 1e3, color=COLORS[0], label="1N4148 model")
    ax.plot(v, (IQ + (v - VQ) / rd) * 1e3, "--", color=COLORS[1], lw=1.3,
            label=f"tangent, slope 1/{rd:.1f} Ω")
    ax.plot(VQ, 1.0, "o", color=INK, ms=5, zorder=5)
    ax.annotate(f"Q ({VQ:.3f} V, 1.00 mA)", xy=(VQ, 1.0), xytext=(0.522, 1.55), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.set_ylim(0, 2.5)
    ax.set_xlim(0.52, 0.64)
    ax.set_ylabel("$I_D$ (mA)")
    ax.legend(loc="upper left", fontsize=8)
    plt.setp(ax.get_xticklabels(), visible=False)
    # input sinusoids, time running downward
    tt = np.linspace(0, 2, 400)
    axs.plot(VQ + 0.005 * np.sin(2 * np.pi * tt), tt, color=COLORS[2], label="5 mV peak")
    axs.plot(VQ + 0.030 * np.sin(2 * np.pi * tt), tt, color=COLORS[3], label="30 mV peak")
    axs.axvline(VQ, color=INK, lw=0.5, ls=":")
    axs.set_ylim(2, 0)
    axs.set_yticks([0, 1, 2])
    axs.set_ylabel("t / period", fontsize=8.5)
    axs.set_xlabel("$V_D$ (V)")
    axs.text(0.6165, 0.25, "30 mV pk", fontsize=7.5, va="center", color=COLORS[3])
    axs.text(0.5905, 0.75, "5 mV pk", fontsize=7.5, va="center", color=COLORS[2])
    # currents vs time
    t = np.linspace(0, 2, 800)
    for vp, col in ((0.005, COLORS[2]), (0.030, COLORS[3])):
        vin = VQ + vp * np.sin(2 * np.pi * t)
        i = diode_i(vin, T) * 1e3
        axr.plot(t, i, color=col, label=f"{vp*1e3:.0f} mV peak")
        axr.plot(t, 1 + vp / rd * 1e3 * np.sin(2 * np.pi * t), ":", color=col, lw=1.0)
    i30 = diode_i(VQ + 0.030 * np.sin(2 * np.pi * t), T) * 1e3
    axr.axhline(1.0, color=INK, lw=0.5)
    axr.annotate(f"+{i30.max()-1:.2f} mA", xy=(0.25, i30.max()), xytext=(0.36, 2.05), fontsize=8,
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    axr.annotate(f"−{1-i30.min():.2f} mA", xy=(0.75, i30.min()), xytext=(0.88, 0.25), fontsize=8,
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    axr.text(1.2, 0.08, "5 mV: ±0.110 mA, HD$_2$ = 2.8 %", fontsize=8, color=COLORS[2])
    axr.set_xlim(0, 2)
    axr.set_ylim(0, 2.5)
    axr.set_xlabel("t / period")
    axr.set_ylabel("$I_D$ (mA)")
    axr.plot([], [], ":", color="#777", lw=1.0, label="linear (small-signal) model")
    axr.legend(loc="upper right", fontsize=7.5)
    save(fig, "01", "fig-1-4-small-signal-linearisation")


def fig_1_5():
    """Forward characteristic at four temperatures."""
    fig, ax = new_fig(6.4, 3.9)
    I = np.logspace(-6, -1, 400)
    temps = [(-40, COLORS[0]), (25, COLORS[2]), (85, COLORS[4]), (125, COLORS[1])]
    for tc, col in temps:
        T = tc + 273.15
        V = diode_v(I, T, Is=is_T(T))
        ax.semilogy(V, I * 1e3, color=col, label=f"{tc} °C".replace("-", "−"))
        v1 = diode_v(1e-3, T, Is=is_T(T))
        ax.plot(v1, 1, "o", color=col, ms=4, zorder=5)
        if tc == 125:
            ax.text(v1 - 0.008, 1.25, f"{v1:.3f} V", fontsize=7.5, color=col, va="bottom", ha="right")
        else:
            ax.text(v1 + 0.006, 0.8, f"{v1:.3f} V", fontsize=7.5, color=col, va="top")
    ax.axhline(1, color=INK, ls=":", lw=0.9)
    ax.text(0.205, 1.15, "1 mA", fontsize=8)
    ax.annotate("", xy=(0.457, 3.5), xytext=(0.581, 3.5),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    ax.text(0.45, 5.0, "≈ −2 mV/K at constant current", fontsize=8.5, ha="left")
    ax.annotate("curves bend above ≈30 mA\n(drop $I R_S$ across 0.568 Ω)", xy=(0.874, 45), xytext=(0.66, 0.02),
                fontsize=8.5, arrowprops=dict(arrowstyle="-|>", lw=0.8))
    ax.set_xlim(0.2, 0.9)
    ax.set_ylim(1e-3, 100)
    ax.set_yticks([1e-3, 1e-2, 1e-1, 1, 10, 100])
    ax.set_yticklabels(["1 µA", "10 µA", "100 µA", "1 mA", "10 mA", "100 mA"])
    ax.set_xlabel("$V_D$ (V)")
    ax.set_ylabel("$I_D$")
    ax.legend(loc="upper left", fontsize=8.5, title="junction temperature", title_fontsize=8.5)
    save(fig, "01", "fig-1-5-diode-temperature")


def fig_1_6():
    """TO-92 power derating."""
    fig, ax = new_fig(6.4, 3.6)
    Ta = np.linspace(0, 175, 701)
    p = np.clip(np.minimum(625, (150 - Ta) / 200 * 1e3), 0, None)
    pd = np.clip(np.minimum(625, (110 - Ta) / 200 * 1e3), 0, None)
    ax.plot(Ta, p, color=COLORS[0], label="absolute maximum ($R_{θJA}$ = 200 K/W, −5.0 mW/K)")
    ax.plot(Ta, pd, "--", color=COLORS[1], label="design derating ($T_J$ ≤ 110 °C)")
    ax.plot([85], [325], "o", color=COLORS[0], ms=5)
    ax.plot([85], [125], "o", color=COLORS[1], ms=5)
    ax.annotate("85 °C, 325 mW", xy=(85, 325), xytext=(95, 400), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("85 °C, 125 mW", xy=(85, 125), xytext=(40, 60), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("425 mW at 25 °C", xy=(25, 425), xytext=(30, 470), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("$T_{J(max)}$ = 150 °C", xy=(150, 0), xytext=(140, 140), fontsize=8.5,
                arrowprops=dict(arrowstyle="-|>", lw=0.7))
    ax.set_xlim(0, 175)
    ax.set_ylim(0, 700)
    ax.set_xlabel("ambient temperature $T_A$ (°C)")
    ax.set_ylabel("allowed dissipation (mW)")
    ax.legend(loc="upper right", fontsize=8.5)
    save(fig, "01", "fig-1-6-power-derating")


if __name__ == "__main__":
    fig_1_1()
    fig_1_2()
    fig_1_3()
    fig_1_4()
    fig_1_5()
    fig_1_6()
