"""Figures for Chapter 3 — Bipolar Junction Transistors.

Run from the repository root:  python figures/scripts/ch03.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyArrowPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, new_fig, save  # noqa: E402

schemdraw.use("matplotlib")

VT = 0.02585
C_NP = "#F6D9C3"     # n+ regions
C_NM = "#FBEEE3"     # n- epi
C_P = "#D6E6F4"      # p base
C_OX = "#BFBFBF"     # oxide
C_MET = "#8C8C8C"    # metal


# ---------------------------------------------------------------------------
def fig_3_1():
    """Cross-section and doping profile of a vertical planar NPN."""
    fig, (ax, axd) = plt.subplots(1, 2, figsize=(6.8, 3.9), gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax.set_xlim(-0.2, 10.4)
    ax.set_ylim(-0.9, 7.4)
    ax.set_aspect("equal")
    ax.axis("off")
    top = 6.0
    # layers (depth drawn downward from y = top), not to scale
    ax.add_patch(Rectangle((0, 0), 10, 1.4, fc=C_NP, ec=INK, lw=0.8))                 # substrate
    ax.add_patch(Rectangle((0, 1.4), 10, top - 1.4, fc=C_NM, ec=INK, lw=0.8))         # epi
    ax.add_patch(Rectangle((0.8, top - 2.0), 6.0, 2.0, fc=C_P, ec=INK, lw=0.8))       # base
    ax.add_patch(Rectangle((1.6, top - 0.9), 2.6, 0.9, fc=C_NP, ec=INK, lw=0.8))      # emitter
    # sinker (IC version), dashed
    ax.add_patch(Rectangle((8.3, 1.4), 1.0, top - 1.4, fc="none", ec=INK, lw=0.8, ls="--"))
    ax.text(8.8, 3.0, "n$^+$\nsinker\n(IC)", fontsize=7, ha="center", va="center")
    # oxide with openings
    ox = [(0, 1.8), (2.5, 4.9), (6.0, 8.4), (9.2, 10.0)]
    for x0, x1 in ox:
        ax.add_patch(Rectangle((x0, top), x1 - x0, 0.3, fc=C_OX, ec=INK, lw=0.6))
    # metal contacts
    for (x0, x1, lab, dashed) in ((1.85, 2.45, "E", False), (4.95, 5.95, "B", False), (8.45, 9.15, "C", True)):
        ax.add_patch(Rectangle((x0, top), x1 - x0, 0.75, fc=C_MET, ec=INK, lw=0.6, ls="--" if dashed else "-"))
        ax.text((x0 + x1) / 2, top + 1.0, lab, ha="center", fontsize=10, weight="bold")
    ax.add_patch(Rectangle((0, -0.35), 10, 0.35, fc=C_MET, ec=INK, lw=0.6))
    ax.text(5.0, -0.75, "C (back contact)", ha="center", fontsize=8.5, weight="bold")
    # region labels
    ax.text(3.0, top - 0.5, "n$^+$ emitter", ha="center", va="center", fontsize=7.5)
    ax.text(5.6, top - 1.45, "p base", ha="center", va="center", fontsize=8)
    ax.text(4.6, 2.2, "n$^-$ epitaxial collector (≈5 µm)", ha="center", va="center", fontsize=8)
    ax.text(5.0, 0.7, "n$^+$ substrate", ha="center", va="center", fontsize=8)
    # electron flow
    for xx in (2.2, 2.9, 3.6):
        ax.add_patch(FancyArrowPatch((xx, top - 0.95), (xx, 3.0), arrowstyle="-|>", mutation_scale=9,
                                     color=COLORS[0], lw=1.2))
    ax.text(1.0, 3.25, "electrons\n(e$^-$)", fontsize=7.5, color=COLORS[0], ha="center", va="center")
    # holes base -> emitter
    ax.add_patch(FancyArrowPatch((4.85, top - 0.55), (4.25, top - 0.55), arrowstyle="-|>", mutation_scale=7,
                                 color=COLORS[1], lw=1.0))
    ax.text(4.75, top - 0.3, "h$^+$", fontsize=7.5, color=COLORS[1], ha="left", va="center")
    ax.text(5.0, 7.25, "not to scale", fontsize=7.5, ha="center", style="italic", color="#555")

    # doping profile
    x = np.linspace(0, 6.0, 3000)
    NA = 3e17 * np.exp(-(x / 0.542) ** 2)
    NE = 1e20 * np.exp(-(x / 0.158) ** 2)
    from scipy.special import erfc
    Nsub = 1e19 * 0.5 * erfc(-(x - 5.0) / 0.25)
    Nepi = 1e16
    ND = NE + Nepi + Nsub
    net = np.abs(ND - NA)
    axd.semilogy(x, net, color=INK, lw=1.6)
    # junctions
    s = np.sign(ND - NA)
    jx = x[np.where(np.diff(s) != 0)[0]]
    for xj in jx[:2]:
        axd.axvline(xj, color="#888", ls=":", lw=0.9)
    axd.annotate(f"E–B junction ({jx[0]:.1f} µm)", xy=(jx[0], 3e20), xytext=(1.3, 3e20), fontsize=7.5,
                 va="center", arrowprops=dict(arrowstyle="-", lw=0.6))
    axd.annotate(f"C–B junction ({jx[1]:.1f} µm)", xy=(jx[1], 4e19), xytext=(1.3, 4e19), fontsize=7.5,
                 va="center", arrowprops=dict(arrowstyle="-", lw=0.6))
    axd.annotate("", xy=(jx[0], 3e14), xytext=(jx[1], 3e14), arrowprops=dict(arrowstyle="<|-|>", lw=0.8))
    axd.text(jx[1] + 0.1, 3e14, f"$W_B$ = {jx[1]-jx[0]:.1f} µm", fontsize=8, ha="left", va="center")
    axd.fill_between(x, 1e14, net, where=(x < jx[0]), color=C_NP, lw=0)
    axd.fill_between(x, 1e14, net, where=(x >= jx[0]) & (x <= jx[1]), color=C_P, lw=0)
    axd.fill_between(x, 1e14, net, where=(x > jx[1]) & (x < 4.9), color=C_NM, lw=0)
    axd.fill_between(x, 1e14, net, where=(x >= 4.9), color=C_NP, lw=0)
    axd.annotate("n$^+$ emitter ≈10$^{20}$", xy=(0.15, 3e19), xytext=(1.3, 5e18), fontsize=7.5, va="center",
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    axd.text(1.25, 1.6e17, "p base, peak ≈10$^{17}$", fontsize=7.5)
    axd.text(2.4, 2e16, "n$^-$ epi 10$^{16}$", fontsize=7.5)
    axd.text(5.85, 1.6e19, "n$^+$ substrate\n10$^{19}$", fontsize=7.5, ha="right", va="bottom")
    axd.set_xlim(0, 6)
    axd.set_ylim(1e14, 1e21)
    axd.set_xlabel("depth below surface (µm)")
    axd.set_ylabel("net doping |$N_D-N_A$| (cm$^{-3}$)")
    fig.tight_layout(w_pad=0.5)
    save(fig, "03", "fig-3-1-npn-structure")


# ---------------------------------------------------------------------------
def fig_3_2():
    """Output characteristics with Early construction."""
    VA, BV, YMAX = 74.0, 40.0, 20.0
    fig = plt.figure(figsize=(6.8, 4.0))
    axl = fig.add_axes([0.09, 0.13, 0.17, 0.80])
    ax = fig.add_axes([0.29, 0.13, 0.69, 0.80], sharey=axl)
    v = np.linspace(0, 45, 3000)
    for k, ib in enumerate((10, 20, 30, 40, 50)):
        i0 = 0.2 * ib                                  # mA at VCE = 0 extrapolation (beta = 200)
        sat = 1 - np.exp(-v / 0.07)
        with np.errstate(divide="ignore", invalid="ignore"):
            M = 1 / (1 - (v / (BV + 1.5)) ** 10)
        M = np.where(v < BV + 1.5, M, np.inf)
        ic = i0 * (1 + v / VA) * sat * M
        m = ic < YMAX + 0.5
        ax.plot(v[m], ic[m], color=COLORS[0], lw=1.5)
        ax.text(6.0, i0 * (1 + 6.0 / VA) + 0.35, f"$I_B$ = {ib} µA", fontsize=7.5, color=COLORS[0],
                va="bottom")
        vl = np.linspace(-VA, 0, 50)
        axl.plot(vl, i0 * (1 + vl / VA), "--", color=COLORS[0], lw=0.9)
        ax.plot(np.linspace(0, 3, 10), i0 * (1 + np.linspace(0, 3, 10) / VA), "--", color=COLORS[0], lw=0.9)
    # power hyperbola (lies above 12 mA everywhere below 52 V, hence the taller current axis)
    vh = np.linspace(4, 45, 400)
    ih = 625 / vh
    mh = ih <= YMAX
    ax.plot(vh[mh], ih[mh], ":", color=COLORS[1], lw=1.8)
    ax.text(31.5, 625 / 31.5 + 0.3, "$P_D$ limit: $I_CV_{CE}$ = 625 mW (25 °C)", fontsize=7.8, color=COLORS[1],
            ha="right", va="bottom")
    ax.axvspan(0, 0.3, color="#DDDDDD", lw=0)
    ax.annotate("saturation\n($V_{CE}$ < 0.3 V)", xy=(0.3, 17.0), xytext=(1.5, 17.0), fontsize=7.8, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.text(14, 0.25, "cutoff ($I_C$ ≈ 0, $I_B$ = 0)", fontsize=7.8, va="bottom")
    ax.plot([0, 45], [0, 0], color=COLORS[2], lw=2.0)
    ax.text(20, 6.3, "forward-active region", fontsize=9, ha="center", va="center",
            bbox=dict(fc="white", ec="none", pad=0.5))
    ax.axvline(BV, color="#888", ls=":", lw=0.9)
    ax.text(BV + 0.4, 0.8, "$BV_{CEO}$\n= 40 V", fontsize=7.8)
    ax.set_xlim(0, 45)
    ax.set_ylim(0, YMAX)
    ax.set_xlabel("$V_{CE}$ (V)")
    plt.setp(ax.get_yticklabels(), visible=False)
    axl.set_xlim(-80, 0)
    axl.set_xticks([-74, 0])
    axl.set_xticklabels(["−74", "0"])
    axl.axvline(-VA, color=INK, lw=0.6)
    axl.plot(-VA, 0, "o", color=INK, ms=4, clip_on=False, zorder=5)
    axl.text(-76, 19.0, "Early\nextrapolation\n(compressed\nscale)", fontsize=7.2, va="top")
    axl.annotate("$-V_A$ = −74 V", xy=(-VA, 0), xytext=(-76, 8.0), fontsize=7.5,
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    axl.set_ylabel("$I_C$ (mA)")
    axl.set_xlabel("$V_{CE}$ (V)")
    axl.spines["right"].set_visible(True)
    axl.spines["right"].set_linestyle((0, (2, 2)))
    save(fig, "03", "fig-3-2-bjt-output-characteristics")


# ---------------------------------------------------------------------------
def _ce_stage(ax):
    """Voltage-divider-biased CE stage drawn with schemdraw on ax."""
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=2.0, lw=1.0)
    Q = d.add(elm.BjtNpn(circle=True).at((0, 0)).anchor("base"))
    rail = 3.6
    d.add(elm.Resistor().up().at(Q.collector).toy(rail).label("$R_C$\n4.7 kΩ", loc="bottom"))
    d.add(elm.Line().left().at(Q.base).length(0.8))
    nb = d.add(elm.Dot())
    d.add(elm.Resistor().up().toy(rail).label("$R_1$\n82 kΩ", loc="top"))
    d.add(elm.Line().right().tox(Q.collector[0]))
    d.add(elm.Line().right().length(0.8))
    d.add(elm.Vdd().label("$V_{CC}$ = 12 V"))
    gnd_y = -3.4
    d.add(elm.Resistor().down().at(nb.end).toy(gnd_y).label("$R_2$\n15 kΩ", loc="top"))
    d.add(elm.Ground())
    d.add(elm.Resistor().down().at(Q.emitter).toy(gnd_y).label("$R_E$\n1.2 kΩ", loc="bottom"))
    d.add(elm.Ground())
    ne = Q.emitter
    d.add(elm.Line().right().at(ne).length(1.7))
    d.add(elm.Capacitor(polar=True).down().toy(gnd_y).label("$C_E$\n100 µF", loc="bottom", ofst=0.3))
    d.add(elm.Ground())
    d.add(elm.Dot().at(ne))
    # input
    d.add(elm.Capacitor().left().at(nb.end).length(1.6).label("10 µF", loc="top"))
    d.add(elm.Dot(open=True).label("$v_{in}$", loc="left"))
    # output
    nc = Q.collector
    d.add(elm.Dot().at(nc))
    d.add(elm.Line().right().at(nc).length(1.9))
    d.add(elm.Capacitor().right().length(1.6).label("10 µF", loc="top"))
    no = d.add(elm.Dot().label("$v_{out}$", loc="top"))
    d.add(elm.Resistor().down().toy(gnd_y).label("$R_L$\n10 kΩ", loc="bottom"))
    d.add(elm.Ground())
    d.draw(show=False)
    ax.text(Q.base[0] + 0.25, Q.base[1] - 1.25, "2N3904", fontsize=8, ha="center", va="center")
    ax.set_aspect("equal")
    ax.axis("off")


def fig_3_3():
    """CE stage with DC and AC load lines."""
    fig = plt.figure(figsize=(6.8, 3.9))
    axc = fig.add_axes([0.0, 0.03, 0.40, 0.94])
    ax = fig.add_axes([0.50, 0.13, 0.48, 0.82])
    _ce_stage(axc)
    VCC, RC, RE, RL = 12.0, 4.7, 1.2, 10.0          # V, kOhm
    Rac = RC * RL / (RC + RL)
    v = np.linspace(0, 13, 800)
    for ib in (2, 4, 6, 8, 10):
        ic = 0.2 * ib * (1 - np.exp(-v / 0.08))
        ax.plot(v, ic, color="#9DB7D0", lw=1.0)
        ax.text(12.9, 0.2 * ib + 0.04, f"{ib} µA", fontsize=7, color="#5A7EA0", ha="right", va="bottom")
    ax.plot(v, (VCC - v) / (RC + RE), color=COLORS[0], label="DC load line, −1/5.9 kΩ")
    VQ, IQ = 6.39, 0.950
    vac = np.linspace(0, VQ + IQ * Rac, 200)
    ax.plot(vac, IQ - (vac - VQ) / Rac, color=COLORS[1], label="AC load line, −1/3.20 kΩ")
    ax.plot(VQ, IQ, "o", color=INK, ms=5, zorder=5)
    ax.annotate("Q (6.39 V, 0.950 mA)", xy=(VQ, IQ), xytext=(7.0, 1.55), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.text(9.6, 0.08, "9.43 V", fontsize=7.5, ha="left", color=COLORS[1])
    ax.text(0.15, 2.97, "2.95 mA", fontsize=7.5, color=COLORS[1], va="bottom")
    ax.text(0.15, 2.05, "2.03 mA", fontsize=7.5, color=COLORS[0], va="bottom")
    # swing arrows
    ya = 3.25
    for xx in (0.2, VQ, 9.43):
        ax.plot([xx, xx], [0, ya], ":", color=COLORS[1], lw=0.8)
    ax.annotate("", xy=(VQ, ya), xytext=(9.43, ya), arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=COLORS[1]))
    ax.text((VQ + 9.43) / 2, ya + 0.05, "3.04 V", fontsize=7.5, ha="center", color=COLORS[1], va="bottom")
    ax.annotate("", xy=(0.2, ya), xytext=(VQ, ya), arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=COLORS[1]))
    ax.text((0.2 + VQ) / 2, ya + 0.05, "6.19 V to saturation", fontsize=7.5, ha="center", color=COLORS[1],
            va="bottom")
    ax.text(9.6, ya + 0.05, "to cutoff", fontsize=7.5, ha="left", color=COLORS[1], va="bottom")
    # optimum Q
    Vo, Io = 4.35, 1.30
    vo = np.linspace(0, Vo + Io * Rac, 100)
    ax.plot(vo, Io - (vo - Vo) / Rac, "--", color=COLORS[2], lw=1.2, label="optimum Q: ±4.15 V swing")
    ax.plot(Vo, Io, "s", color=COLORS[2], ms=4.5, zorder=5)
    ax.annotate("optimum Q (4.35 V, 1.30 mA)", xy=(Vo, Io), xytext=(0.6, 0.12), fontsize=7.8, color=COLORS[2],
                arrowprops=dict(arrowstyle="-", lw=0.6, color=COLORS[2]))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4.5)
    ax.set_xlabel("$V_{CE}$ (V)")
    ax.set_ylabel("$I_C$ (mA)")
    ax.legend(loc="upper right", fontsize=7.3, bbox_to_anchor=(1.0, 1.04))
    save(fig, "03", "fig-3-3-bias-and-load-lines")


# ---------------------------------------------------------------------------
def fig_3_4():
    """Hybrid-pi model with T-model inset."""
    fig = plt.figure(figsize=(6.8, 3.5))
    ax = fig.add_axes([0.0, 0.0, 0.70, 1.0])
    axt = fig.add_axes([0.72, 0.08, 0.27, 0.84])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8.5, unit=2.4, lw=1.0)
    B = d.add(elm.Dot(open=True).at((0, 0)).label("B", loc="left"))
    d.add(elm.Resistor().right().label("$r_x$ = 10 Ω", loc="top"))
    nbp = d.add(elm.Dot().label("B′", loc="top", ofst=0.15))
    bot = -3.0
    d.add(elm.Line().right().length(1.2))
    nrp = d.add(elm.Dot())
    d.add(elm.Resistor().down().toy(bot).label(("+", "$v_\\pi$", "−"), loc="bottom")
          .label("$r_\\pi$\n5.17 kΩ", loc="top"))
    d.add(elm.Line().right().at(nrp.end).length(1.8))
    ncp = d.add(elm.Dot())
    d.add(elm.Capacitor().down().toy(bot).label("$C_\\pi$\n20.6 pF", loc="bottom"))
    d.add(elm.Capacitor().right().at(ncp.end).length(3.2).label("$C_\\mu$ = 1.94 pF\n($V_{CB}$ = 5 V)", loc="top"))
    nc = d.add(elm.Dot())
    d.add(elm.SourceControlledI().down().toy(bot).label("$g_m v_\\pi$\n$g_m$ = 38.7 mS", loc="bottom"))
    d.add(elm.Line().right().at(nc.end).length(3.9))
    nro = d.add(elm.Dot())
    d.add(elm.Resistor().down().toy(bot).label("$r_o$\n74 kΩ", loc="bottom"))
    d.add(elm.Line().right().at(nro.end).length(1.4))
    d.add(elm.Dot(open=True).label("C", loc="right"))
    d.add(elm.Line().right().at((nrp.end[0], bot)).tox(nro.end[0]))
    d.add(elm.Line().left().at((nrp.end[0], bot)).tox(B.end[0]))
    d.add(elm.Dot(open=True).label("E", loc="left"))
    for xx in (nrp.end[0], ncp.end[0], nc.end[0]):
        d.add(elm.Dot().at((xx, bot)))
    d.draw(show=False)
    ax.set_aspect("equal")
    ax.axis("off")
    # T-model inset
    t = schemdraw.Drawing(canvas=axt, show=False)
    t.config(fontsize=8, unit=2.0, lw=1.0)
    C = t.add(elm.Dot(open=True).at((0, 0)).label("C", loc="top"))
    t.add(elm.SourceControlledI().down().label("$\\alpha i_e$", loc="bottom"))
    nx = t.add(elm.Dot())
    t.add(elm.Resistor().down().label("$r_e$\n25.7 Ω", loc="bottom").label("$i_e$ ↓", loc="top", ofst=0.1))
    t.add(elm.Dot(open=True).label("E", loc="bottom"))
    t.add(elm.Line().left().at(nx.end).length(1.4))
    t.add(elm.Dot(open=True).label("B′", loc="left"))
    t.draw(show=False)
    axt.set_aspect("equal")
    axt.axis("off")
    xl, xr = axt.get_xlim()
    yl, yh = axt.get_ylim()
    axt.set_xlim(xl - 0.5, xr + 0.5)
    axt.set_ylim(yl - 0.4, yh + 0.9)
    axt.add_patch(Rectangle((xl - 0.45, yl - 0.35), xr - xl + 0.9, yh - yl + 1.2, fill=False, ec="#888",
                            lw=0.8, ls="--"))
    axt.text((xl + xr) / 2, yh + 0.55, "low-frequency T model", fontsize=8, ha="center", va="center")
    save(fig, "03", "fig-3-4-hybrid-pi-model")


# ---------------------------------------------------------------------------
def _edge(t, t0, tr, kind="lin"):
    """0 -> 1 transition starting at t0 with 10-90 % time tr (smooth)."""
    tau = tr / np.log(9.0)
    x = (t - t0) / tau
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))


def fig_3_5():
    """Saturated relay driver switching waveforms."""
    t = np.linspace(0, 2.5, 25001)                    # us
    ton, toff = 0.2, 1.2
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(6.6, 5.0), sharex=True,
                                     gridspec_kw=dict(height_ratios=[1, 1.15, 1.6]))
    g = 3.3 * ((t >= ton) & (t < toff))
    a1.plot(t, g, color=INK)
    a1.set_ylabel("GPIO (V)")
    a1.set_ylim(-0.4, 4.2)
    a1.set_yticks([0, 3.3])
    td, tr, tf = 0.035, 0.035, 0.050
    # collector current: 10 % at ton+td, 90 % at ton+td+tr (logistic edges)
    def ic_trace(ts):
        c10 = ton + td
        on = _edge(t, c10 + tr / 2, tr)
        f90 = toff + ts
        off = 1 - _edge(t, f90 + tf / 2, tf)
        return 30.0 * np.minimum(on, off)
    ic1, ic2 = ic_trace(0.39), ic_trace(0.78)
    # base current
    ib = np.where((t >= ton) & (t < toff), 3.04, 0.0)
    ib1 = ib.copy()
    m1 = t >= toff
    ib1[m1] = -0.99 * (1 - _edge(t[m1], toff + 0.39 + 0.06, 0.08))
    ib2 = ib.copy()
    ib2[m1] = -0.075 * (1 - _edge(t[m1], toff + 0.78 + 0.06, 0.08))
    a2.plot(t, ib1, color=COLORS[0], label="active pull-down (pin driven low, 820 Ω)")
    a2.plot(t[m1], ib2[m1], "--", color=COLORS[1], label="10 kΩ pull-down only")
    a2.axhline(0, color=INK, lw=0.5)
    a2.set_ylabel("$I_B$ (mA)")
    a2.set_ylim(-1.6, 4.3)
    a2.text(0.6, 3.25, "$I_{B1}$ ≈ +3.04 mA", fontsize=8, va="bottom")
    a2.annotate("$I_{B2}$ ≈ −0.99 mA", xy=(1.3, -0.99), xytext=(1.85, -1.25), fontsize=8, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6))
    a2.legend(loc="upper right", fontsize=7.3)
    a3.plot(t, ic1, color=COLORS[0], label="active pull-down: $t_s$ = 0.39 µs")
    a3.plot(t, ic2, "--", color=COLORS[1], label="10 kΩ only: $t_s$ = 0.78 µs")
    for lv in (3, 27):
        a3.axhline(lv, color="#999", ls=":", lw=0.8)
    a3.text(2.48, 27.6, "90 %", fontsize=7.5, ha="right", va="bottom", color="#666")
    a3.text(2.48, 3.6, "10 %", fontsize=7.5, ha="right", va="bottom", color="#666")
    a3.set_ylabel("$I_C$ (mA)")
    a3.set_ylim(-2, 40)
    a3.set_yticks([0, 10, 20, 30])
    a3.set_xlabel("time (µs)")
    a3.set_xlim(0, 2.5)
    # interval brackets
    def bracket(ax, x0, x1, y, txt, col=INK, dy=0.8, ha="center"):
        ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="|-|", lw=0.8, color=col,
                                                                   mutation_scale=3))
        ax.text((x0 + x1) / 2 if ha == "center" else x1 + 0.02, y + dy, txt, fontsize=7.8, ha=ha,
                va="bottom", color=col)
    bracket(a3, toff, toff + 0.39, 33.5, "$t_s$ = 0.39 µs", col=COLORS[0])
    bracket(a3, toff + 0.39, toff + 0.39 + tf, 22, "$t_f$", col=COLORS[0], ha="left")
    bracket(a3, toff, toff + 0.78, 37.0, "$t_s$ = 0.78 µs", col=COLORS[1], dy=0.4)
    bracket(a3, toff + 0.78, toff + 0.78 + tf, 22, "$t_f$ ≈ 50 ns", col=COLORS[1], ha="left")
    a3.annotate("$t_d$ ≈ 35 ns (to 10 %)\n$t_r$ ≈ 35 ns (10–90 %)", xy=(ton + td + tr / 2, 15),
                xytext=(0.42, 20), fontsize=7.8, va="center", arrowprops=dict(arrowstyle="-", lw=0.6))
    for tt, lv in ((ton + td, 3), (ton + td + tr, 27)):
        a3.plot(tt, lv, "o", color=INK, ms=3, zorder=5)
    a3.legend(loc="lower center", fontsize=7.3, bbox_to_anchor=(0.40, 0.08))
    for ax in (a1, a2, a3):
        for xx in (ton, toff):
            ax.axvline(xx, color="#BBB", lw=0.6, ls=":")
    fig.align_ylabels()
    fig.tight_layout(h_pad=0.3)
    save(fig, "03", "fig-3-5-switching-waveforms")


# ---------------------------------------------------------------------------
def fig_3_6():
    """fT versus collector current."""
    tauF, Cje, Cmu = 301e-12, 9.0e-12, 1.94e-12
    def ft(ic):
        gm = ic / VT
        return gm / (2 * np.pi * (gm * tauF + Cje + Cmu))
    fig, ax = new_fig(6.4, 3.9)
    ic = np.logspace(-4, np.log10(30e-3), 300)
    ax.loglog(ic * 1e3, ft(ic) / 1e6, color=COLORS[0], label="charge-control model")
    ich = np.logspace(np.log10(30e-3), -1, 100)
    roll = 1 / (1 + ((ich - 30e-3) / 66.9e-3) ** 2)
    ax.loglog(ich * 1e3, ft(ich) * roll / 1e6, ":", color=COLORS[0], lw=2.2,
              label="high injection / Kirk effect (qualitative)")
    flim = 1 / (2 * np.pi * tauF) / 1e6
    ax.axhline(flim, color=COLORS[1], ls="--", lw=1.1)
    ax.text(0.12, flim * 1.07, f"transit-time limit 1/(2π$τ_F$) = {flim:.0f} MHz", fontsize=8, color=COLORS[1])
    pts = [0.1e-3, 0.3e-3, 1e-3, 3e-3, 10e-3]
    for p in pts:
        f = ft(p) / 1e6
        ax.plot(p * 1e3, f, "o", color=COLORS[0], ms=4)
        ax.text(p * 1e3 * 1.15, f * 0.88, f"{f:.0f} MHz", fontsize=7.5, va="top")
    ax.plot(10, 300, "s", color=COLORS[3], ms=6, zorder=5, label="datasheet minimum, 300 MHz at 10 mA")
    # slope triangle
    x0, x1 = 0.25, 0.5
    y0 = 18.0
    ax.plot([x0, x1, x1, x0], [y0, y0, y0 * x1 / x0, y0], color=INK, lw=0.8)
    ax.text(x1 * 1.06, y0 * 1.35, "slope 1:\n$f_T$ ∝ $I_C$", fontsize=7.8, va="center")
    ax.text(70, 200, "≈250 MHz\nat 100 mA", fontsize=7.5, ha="center", va="top")
    ax.set_xlim(0.1, 100)
    ax.set_ylim(10, 1000)
    ax.set_xticks([0.1, 1, 10, 100])
    ax.set_xticklabels(["0.1", "1", "10", "100"])
    ax.set_yticks([10, 100, 1000])
    ax.set_yticklabels(["10 MHz", "100 MHz", "1 GHz"])
    ax.set_xlabel("collector current $I_C$ (mA)")
    ax.set_ylabel("transition frequency $f_T$")
    ax.legend(loc="lower right", fontsize=7.8)
    save(fig, "03", "fig-3-6-ft-versus-ic")


if __name__ == "__main__":
    fig_3_1()
    fig_3_2()
    fig_3_3()
    fig_3_4()
    fig_3_5()
    fig_3_6()
