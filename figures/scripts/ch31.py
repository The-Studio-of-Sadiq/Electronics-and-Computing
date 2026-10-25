"""Figures for Chapter 31 — AC–DC and DC–AC Conversion.

Run from the repository root:  python figures/scripts/ch31.py
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, Circle, FancyArrowPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402
from scipy.special import jv  # noqa: E402,F401
from scipy import signal  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

schemdraw.use("matplotlib")
warnings.filterwarnings("ignore", message=".*non-interactive.*")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
GREY = "#888888"
LIGHT = "#BBBBBB"


def _sd(ax, fontsize=8, unit=1.5, lw=1.1):
    """schemdraw Drawing that renders onto a matplotlib axis."""
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


# ----------------------------------------------------------------------------
# Figure 31.1 — six-pulse thyristor bridge with commutation overlap
# ----------------------------------------------------------------------------
def _bridge_waveforms(alpha_deg, VLL=400.0, f=50.0, Lc=0.3e-3, Id=400.0, n=7200):
    w = 2 * np.pi * f
    Vm = VLL * np.sqrt(2 / 3)
    a = np.radians(alpha_deg)
    cosmu = np.cos(a) - 2 * w * Lc * Id / (np.sqrt(2) * VLL)
    mu = np.arccos(cosmu) - a
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ph = np.array([Vm * np.sin(th - k * 2 * np.pi / 3) for k in range(3)])  # a, b, c

    def group(fire0, order):
        """Rail voltage and phase currents for one commutation group."""
        v = np.zeros_like(th)
        cur = np.zeros((3, th.size))
        for i, t in enumerate(th):
            # most recent firing
            rel = (t - fire0) % (2 * np.pi)
            k = int(rel // (2 * np.pi / 3))
            phi = rel - k * 2 * np.pi / 3
            inc, out = order[k], order[k - 1]
            if phi < mu:
                x = (np.cos(a) - np.cos(a + phi)) / (np.cos(a) - np.cos(a + mu))
                v[i] = 0.5 * (ph[inc, i] + ph[out, i])
                cur[inc, i] = Id * x
                cur[out, i] = Id * (1 - x)
            else:
                v[i] = ph[inc, i]
                cur[inc, i] = Id
        return v, cur

    vp, ip = group(np.radians(30) + a, [0, 1, 2])          # T1, T3, T5 on a, b, c
    vn, inn = group(np.radians(90) + a, [2, 0, 1])          # T2, T4, T6 on c, a, b
    vd = vp - vn
    # terminal phase voltage a (after Lc): equals rail during overlap involving phase a
    va_t = ph[0].copy()
    for (v, cur) in ((vp, ip), (vn, inn)):
        mask = (cur[0] > 1e-9) & (cur[0] < Id - 1e-9)
        va_t[mask] = v[mask]
    return th, ph, vd, ip, inn, va_t, np.degrees(mu)


def fig_31_1():
    alpha = np.degrees(np.arccos((250 + 36.0) / 540.2))
    th, ph, vd, ip, inn, va_t, mu = _bridge_waveforms(alpha)
    deg = np.degrees(th)
    ia = ip[0] - inn[1]  # T1 on a minus T4 on a (lower group order c,a,b -> index 1)
    # lower group currents indexed by phase: inn[phase]
    ia = ip[0] - inn[0]

    fig = plt.figure(figsize=(6.8, 7.6))
    gs = fig.add_gridspec(4, 1, height_ratios=[1.75, 1.1, 0.75, 1.0], hspace=0.38)
    axc = fig.add_subplot(gs[0])
    # --- circuit -----------------------------------------------------------
    d = _sd(axc, fontsize=8)
    top, bot = 5.0, 0.0
    legx = [6.0, 7.6, 9.2]
    mids = [3.3, 2.5, 1.7]
    names_up = ["T1", "T3", "T5"]
    names_dn = ["T4", "T6", "T2"]
    for k, (x, ym) in enumerate(zip(legx, mids)):
        d += elm.Line().at((x, ym)).to((x, 3.7))
        d += elm.SCR().at((x, 3.7)).to((x, top)).label(names_up[k], loc="bottom", ofst=0.15)
        d += elm.SCR().at((x, bot)).to((x, 1.3)).label(names_dn[k], loc="bottom", ofst=0.15)
        d += elm.Line().at((x, 1.3)).to((x, ym))
        d += elm.Dot().at((x, ym))
    d += elm.Line().at((legx[0], top)).to((12.2, top))
    d += elm.Line().at((legx[0], bot)).to((12.2, bot))
    for x in legx:
        d += elm.Dot().at((x, top))
        d += elm.Dot().at((x, bot))
    # source and commutating inductances
    for k, (ym, nm) in enumerate(zip(mids, "abc")):
        d += elm.Line().at((1.0, ym)).to((2.4, ym))
        d += elm.Inductor2(loops=2).at((2.4, ym)).to((3.9, ym))
        d += elm.Line().at((3.9, ym)).to((legx[k], ym))
        axc.text(1.2, ym + 0.08, nm, fontsize=8, ha="left", va="bottom", color=INK)
    axc.text(3.15, mids[2] - 0.45, r"$L_c=0.3$ mH" + "\n(each line)", fontsize=7.5, ha="center", va="top")
    box(axc, -0.9, 1.2, 1.9, 2.6, "", fc="#F4F4F4")
    axc.text(0.05, 2.9, "3~", fontsize=11, ha="center", va="center")
    axc.text(0.05, 2.1, "400 V\n50 Hz", fontsize=7.5, ha="center", va="center")
    # DC side: smoothing reactor and load
    d += elm.Inductor2(loops=3).at((12.2, top)).to((12.2, 3.1)).label(r"$L_d$", loc="bottom", ofst=0.2)
    d += elm.Resistor().at((12.2, 3.1)).to((12.2, bot)).label("plating\nload", loc="top", ofst=0.25)
    axc.annotate("", xy=(11.1, top + 0.05), xytext=(10.2, top + 0.05),
                 arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.2))
    axc.text(10.65, top + 0.25, r"$I_d=400$ A", fontsize=7.5, color=ORANGE, ha="center")
    axc.annotate("", xy=(13.3, top - 0.2), xytext=(13.3, bot + 0.2),
                 arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9))
    axc.text(13.45, 2.5, r"$v_d$" + "\nmean\n250 V", fontsize=8, ha="left", va="center")
    axc.text(10.5, 5.75, r"$\alpha=58^\circ$, $\mu=%.1f^\circ$" % mu, fontsize=8, ha="center")
    _finish(d, axc, xlim=(-1.0, 15.0), ylim=(-0.3, 6.1))

    # --- panel 1: DC voltage ---------------------------------------------
    ax1 = fig.add_subplot(gs[1])
    vab = ph[0] - ph[1]
    for k in range(3):
        vll = ph[k] - ph[(k + 1) % 3]
        ax1.plot(deg, vll, color=LIGHT, lw=0.8)
        ax1.plot(deg, -vll, color=LIGHT, lw=0.8)
    ax1.plot(deg, vd, color=BLUE, lw=1.8, label=r"$v_d$")
    ax1.axhline(vd.mean(), color=ORANGE, ls="--", lw=1.1)
    ax1.text(362, vd.mean(), r"$V_d=%.0f$ V" % vd.mean(), color=ORANGE, fontsize=8, va="center")
    ax1.text(362, 566, "566 V", color=GREY, fontsize=7.5, va="center")
    # mark one firing and overlap: T1 fired at 30+alpha
    f1 = 30 + alpha
    ax1.axvline(30, color=GREY, lw=0.6, ls=":")
    ax1.annotate("", xy=(f1, -480), xytext=(30, -480),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    ax1.text((30 + f1) / 2, -440, r"$\alpha$", ha="center", fontsize=8)
    ax1.axvspan(f1, f1 + mu, color=ORANGE, alpha=0.18, lw=0)
    ax1.annotate(r"overlap $\mu$: $v_d$ drops to" + "\nmean of two phases",
                 xy=(f1 + mu / 2, 150), xytext=(f1 + 40, -330), fontsize=7.5,
                 arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax1.plot([], [], color=LIGHT, lw=0.8, label="line-to-line voltages")
    ax1.legend(loc="upper right", fontsize=8, ncol=2, bbox_to_anchor=(1.0, 1.22))
    ax1.set_xlim(0, 360)
    ax1.set_ylim(-620, 640)
    ax1.set_ylabel("voltage (V)")
    ax1.set_xticks(range(0, 361, 60))
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax1.set_title("(1) DC output voltage", fontsize=9, loc="left")

    # --- panel 2: thyristor currents --------------------------------------
    ax2 = fig.add_subplot(gs[2], sharex=ax1)
    ax2.plot(deg, ip[0], color=BLUE, label=r"$i_{T1}$")
    ax2.plot(deg, ip[1], color=GREEN, label=r"$i_{T3}$")
    ax2.set_ylim(-40, 470)
    ax2.set_ylabel("current (A)")
    ax2.legend(loc="upper right", fontsize=8, ncol=2, bbox_to_anchor=(1.0, 1.25))
    f3 = 150 + alpha
    ax2.axvspan(f3, f3 + mu, color=ORANGE, alpha=0.18, lw=0)
    ax2.annotate(r"400 A transferred in $\mu=%.1f^\circ$" % mu, xy=(f3 + mu / 2, 200),
                 xytext=(f3 + 30, 230), fontsize=7.5,
                 arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    plt.setp(ax2.get_xticklabels(), visible=False)
    ax2.set_title("(2) thyristor currents", fontsize=9, loc="left")

    # --- panel 3: line current and fundamental ----------------------------
    ax3 = fig.add_subplot(gs[3], sharex=ax1)
    c1 = np.fft.rfft(ia)[1] * 2 / ia.size
    i1 = np.abs(c1) * np.cos(th + np.angle(c1))  # cos convention
    lag = -90.0 - np.degrees(np.angle(c1))  # va = sin(th) = cos(th - 90 deg)
    lag = (lag + 180) % 360 - 180
    ax3.plot(deg, ia, color=BLUE, label=r"$i_a$")
    ax3.plot(deg, i1, color=BLUE, ls="--", lw=1.2, label=r"$i_{a1}$ (peak %.0f A)" % np.abs(c1))
    ax3.set_ylim(-520, 520)
    ax3.set_ylabel("current (A)")
    ax3b = ax3.twinx()
    ax3b.spines["right"].set_visible(True)
    ax3b.plot(deg, ph[0], color=GREY, lw=0.9, ls=":")
    ax3b.plot(deg, va_t, color=ORANGE, lw=1.0, label=r"$v_a$ at terminals")
    ax3b.set_ylim(-520 * 326.6 / 441, 520 * 326.6 / 441)
    ax3b.set_ylabel("phase voltage (V)", color=ORANGE)
    ax3b.tick_params(axis="y", colors=ORANGE)
    # lag marker between peaks
    pk_v = 90.0
    pk_i = (np.degrees(-np.angle(c1))) % 360
    ax3.annotate("", xy=(pk_i, 470), xytext=(pk_v, 470),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    ax3.text((pk_v + pk_i) / 2, 480, r"lag $%.1f^\circ$" % lag, ha="center", va="bottom", fontsize=7.5)
    # notch annotation
    notch = np.where((np.abs(va_t - ph[0]) > 1) & (deg > 200) & (deg < 230))[0]
    if notch.size:
        xn = deg[notch[0]]
        ax3b.annotate("commutation\nnotches", xy=(xn, va_t[notch[0]] + 20), xytext=(150, -60),
                      fontsize=7.5, color=ORANGE, ha="center",
                      arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    h1, l1 = ax3.get_legend_handles_labels()
    h2, l2 = ax3b.get_legend_handles_labels()
    ax3.legend(h1 + h2, l1 + l2, loc="lower right", fontsize=7.5, ncol=3, bbox_to_anchor=(1.0, -0.72))
    ax3.set_xlabel(r"supply angle $\omega t$ (degrees)")
    ax3.set_title(r"(3) line current $i_a$, its fundamental and terminal voltage $v_a$", fontsize=9, loc="left")
    print(f"  31.1: alpha={alpha:.2f}, mu={mu:.2f}, Vd={vd.mean():.1f}, I1pk={np.abs(c1):.0f}, lag={lag:.1f}")
    save(fig, "31", "fig-31-1-thyristor-bridge-overlap")


# ----------------------------------------------------------------------------
# Figure 31.2 — three-phase inverter, hexagon and SVPWM period
# ----------------------------------------------------------------------------
def _igbt_leg(d, ax, x, ytop, ybot, names, s=0.9):
    """Two IGBTs with antiparallel diodes in a column at x; returns the midpoint (x, ym)."""
    ym = (ytop + ybot) / 2
    h = 0.7 * s
    for (yc, ye, nm) in ((ytop, ym, names[0]), (ym, ybot, names[1])):
        yc0 = (yc + ye) / 2
        q = elm.IgbtN().theta(0).anchor("center").at((x, yc0)).scale(s)
        d += q
        d += elm.Line().at((x, yc0 + h)).to((x, yc))
        d += elm.Line().at((x, yc0 - h)).to((x, ye))
        xd = x + 0.75
        dy = 0.85
        d += elm.Line().at((x, yc0 + dy)).to((xd, yc0 + dy))
        d += elm.Line().at((x, yc0 - dy)).to((xd, yc0 - dy))
        d += elm.Diode().at((xd, yc0 - dy)).to((xd, yc0 + dy))
        d += elm.Dot(radius=0.06).at((x, yc0 + dy))
        d += elm.Dot(radius=0.06).at((x, yc0 - dy))
        ax.text(x - 0.75, yc0 + 0.35, nm, fontsize=7.5, ha="right", va="bottom")
    return x, ym


def fig_31_2():
    Vdc = 540.0
    fig = plt.figure(figsize=(6.8, 6.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.2], width_ratios=[1.1, 1.0], hspace=0.10, wspace=0.22)
    axc = fig.add_subplot(gs[0, :])
    d = _sd(axc, fontsize=8)
    ytop, ybot = 4.8, 0.0
    # DC link
    d += elm.Capacitor().at((1.2, ytop)).to((1.2, ybot)).label("540 V\nDC link\ncapacitor\nbank", loc="top", ofst=0.25)
    axc.text(0.2, ytop, "+", fontsize=10, ha="right", va="center")
    axc.text(0.2, ybot, "−", fontsize=10, ha="right", va="center")
    xs = [3.6, 6.3, 9.0]
    taps = []
    for k, x in enumerate(xs):
        taps.append(_igbt_leg(d, axc, x, ytop, ybot, (f"S{2*k+1}", f"S{2*k+2}")))
    d += elm.Line().at((0.3, ytop)).to((xs[-1] + 0.75, ytop))
    d += elm.Line().at((0.3, ybot)).to((xs[-1] + 0.75, ybot))
    for x in xs:
        d += elm.Dot(radius=0.06).at((x, ytop))
        d += elm.Dot(radius=0.06).at((x, ybot))
    for (x, ym), nm in zip(taps, "abc"):
        d += elm.Dot(radius=0.06).at((x, ym))
        d += elm.Line().at((x, ym)).to((x + 1.3, ym))
        axc.add_patch(Circle((x + 1.38, ym), 0.08, fc="white", ec=INK, lw=0.9, zorder=5))
        axc.text(x + 1.38, ym + 0.15, nm, fontsize=8, ha="center", va="bottom")
    # star R-L load, drawn separately with matching terminals
    lx = 11.6
    ys = [3.6, 2.4, 1.2]
    for yo, nm in zip(ys, "abc"):
        axc.add_patch(Circle((lx, yo), 0.08, fc="white", ec=INK, lw=0.9, zorder=5))
        axc.text(lx - 0.15, yo, nm, fontsize=8, ha="right", va="center")
        d += elm.Resistor().at((lx + 0.08, yo)).to((lx + 1.3, yo)).scale(0.55)
        d += elm.Inductor2(loops=2).at((lx + 1.3, yo)).to((lx + 2.4, yo))
    d += elm.Line().at((lx + 2.4, ys[0])).to((lx + 2.4, ys[-1]))
    d += elm.Dot(radius=0.06).at((lx + 2.4, ys[1]))
    axc.text(lx + 2.55, ys[1], "n", fontsize=8, va="center")
    axc.text(lx + 1.2, ys[0] + 0.5, "star R–L load", fontsize=7.5, ha="center")
    # gate driver blocks
    box(axc, 1.7, 5.5, 9.4, 0.7, r"isolated gate drivers, complementary pairs, dead time $t_d$",
        fc="#FFF4E0", fontsize=7.5)
    for x in xs:
        for yg in (ytop - 1.2 - 0.05, 1.2 - 0.05):
            pass
        axc.annotate("", xy=(x - 0.85, ytop - 0.15), xytext=(x - 0.85, 5.5),
                     arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.7, ls="--"))
    _finish(d, axc, xlim=(-0.6, 14.8), ylim=(-0.4, 6.3))

    # --- hexagon --------------------------------------------------------
    axh = fig.add_subplot(gs[1, 0])
    R = 2 * Vdc / 3
    labels = ["V1 (100)", "V2 (110)", "V3 (010)", "V4 (011)", "V5 (001)", "V6 (101)"]
    pts = [(R * np.cos(np.radians(60 * k)), R * np.sin(np.radians(60 * k))) for k in range(6)]
    axh.add_patch(Polygon(pts, closed=True, fill=False, ec=INK, lw=1.0))
    axh.add_patch(Circle((0, 0), Vdc / np.sqrt(3), fill=False, ec=GREEN, ls="--", lw=1.0))
    for k, (x, y) in enumerate(pts):
        axh.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.8))
        dx = {0: 0.27, 3: -0.27}.get(k, 0.0)
        dyy = 0.13 if k in (1, 2) else (-0.13 if k in (4, 5) else 0.0)
        axh.text(x + dx * R, y + dyy * R, labels[k], fontsize=7.5, ha="center", va="center")
    axh.plot(0, 0, "o", color=INK, ms=3)
    axh.text(-55, -25, "V0 (000)\nV7 (111)", fontsize=7, ha="right", va="top")
    th = np.radians(20)
    Vr = 0.5 * Vdc
    T1, T2 = np.sqrt(3) * 0.5 * np.sin(np.radians(40)), np.sqrt(3) * 0.5 * np.sin(th)
    p1 = np.array([T1 * R, 0])
    p2 = p1 + T2 * R * np.array([np.cos(np.radians(60)), np.sin(np.radians(60))])
    axh.annotate("", xy=p1, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    axh.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
    axh.annotate("", xy=(Vr * np.cos(th), Vr * np.sin(th)), xytext=(0, 0),
                 arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.8))
    axh.text(p1[0] / 2 + 40, -22, r"$T_1/T_s=%.3f$" % T1, color=BLUE, fontsize=7.5, ha="center", va="top")
    axh.text(p1[0] + 55, p2[1] / 2 + 12, r"$T_2/T_s=%.3f$" % T2, color=BLUE, fontsize=7.5, ha="left", va="center")
    axh.text(-60, 150, r"$v^*=270$ V" + "\n" + r"$(0.5V_{dc})$ at 20°", color=ORANGE, fontsize=7.5, ha="center")
    axh.annotate("", xy=(150, 62), xytext=(-20, 150), arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.6))
    axh.text(-285, -175,
             r"$V_{dc}/\sqrt{3}$" + "\n= 312 V", color=GREEN, fontsize=7.5, ha="right", va="top")
    axh.text(R * 0.75 + 15, -R * 0.433 - 15, r"$\frac{2}{3}V_{dc}$" + "\n= 360 V", fontsize=7.5,
             ha="left", va="top")
    axh.text(R * 0.87 * np.cos(np.radians(30)) + 25, R * 0.87 * np.sin(np.radians(30)) + 15,
             "sector 1", fontsize=7, color=GREY, ha="left", va="center")
    axh.set_xlim(-520, 520)
    axh.set_ylim(-450, 450)
    axh.set_aspect("equal")
    axh.axis("off")

    # --- timing ---------------------------------------------------------
    axt = fig.add_subplot(gs[1, 1])
    Ts = 100.0
    t = np.linspace(0, Ts, 2001)
    cnt = np.abs(1 - 2 * t / Ts)  # period from counter peak to peak: 1 -> 0 -> 1
    duties = [0.926, 0.370, 0.074]
    gates = [(cnt < dd).astype(float) for dd in duties]
    # counter panel occupies y in [3.6, 5.6]
    y0c, hc = 3.7, 2.0
    axt.plot(t, y0c + hc * cnt, color=INK, lw=1.2)
    cols = [BLUE, ORANGE, GREEN]
    for dd, c, nm in zip(duties, cols, "abc"):
        axt.axhline(y0c + hc * dd, color=c, lw=0.9, ls="--")
        axt.text(Ts + 1.5, y0c + hc * dd, f"{nm}: {dd:.3f}", color=c, fontsize=7, va="center")
    axt.text(-2, y0c + hc, "peak", fontsize=7, ha="right", va="center")
    axt.text(-2, y0c, "0", fontsize=7, ha="right", va="center")
    for k, (g, c, nm) in enumerate(zip(gates, cols, "abc")):
        yb = 2.4 - k * 0.95
        axt.fill_between(t, yb, yb + 0.6 * g, step=None, color=c, alpha=0.25, lw=0)
        axt.plot(t, yb + 0.6 * g, color=c, lw=1.2)
        axt.text(-2, yb + 0.3, f"leg {nm}", fontsize=7.5, ha="right", va="center", color=c)
    # state sequence
    edges = sorted([0.0] + [Ts / 2 * (1 - dd) for dd in duties] + [Ts / 2 * (1 + dd) for dd in duties] + [Ts])
    states = ["000", "100", "110", "111", "110", "100", "000"]
    for k in range(7):
        xm = 0.5 * (edges[k] + edges[k + 1])
        axt.text(xm, 3.25, states[k], fontsize=6.5, ha="center", va="center", rotation=90)
        axt.axvline(edges[k + 1], color=GRID, lw=0.6, zorder=0) if k < 6 else None
    axt.annotate("", xy=(edges[1], -0.25), xytext=(0, -0.25),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    axt.text(edges[1] / 2 + 1, -0.35, r"$T_0/4$", fontsize=7, ha="left", va="top")
    axt.annotate("", xy=(edges[4], -0.25), xytext=(edges[3], -0.25),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=7))
    axt.text(Ts / 2, -0.35, r"$T_0/2$", fontsize=7, ha="center", va="top")
    axt.text(Ts / 2, -0.95, r"$T_0/T_s=0.147$, split equally between 000 and 111", fontsize=7, ha="center", va="top")
    axt.set_xlim(0, Ts)
    axt.set_ylim(-1.4, 5.9)
    axt.set_yticks([])
    axt.spines["left"].set_visible(False)
    axt.set_xticks([0, 25, 50, 75, 100])
    axt.set_xlabel(r"time in one period $T_s$ ($\mu$s)")
    axt.set_title("centre-aligned counter, compares, gates", fontsize=8.5)
    save(fig, "31", "fig-31-2-three-phase-inverter-svpwm")


# ----------------------------------------------------------------------------
# Figure 31.3 — spectra of sine-triangle PWM
# ----------------------------------------------------------------------------
def fig_31_3():
    Vdc, M, f1, mf = 540.0, 0.8, 50.0, 51
    N = 2 ** 18
    t = np.arange(N) / (N * f1)
    carrier = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * mf * f1 * t + np.pi / 2))

    def leg(ph):
        return np.where(M * np.sin(2 * np.pi * f1 * t - ph) > carrier, Vdc / 2, -Vdc / 2)

    va, vb = leg(0.0), leg(2 * np.pi / 3)
    Sa = 2 * np.abs(np.fft.rfft(va)) / N
    Sab = 2 * np.abs(np.fft.rfft(va - vb)) / N
    wthd = np.sqrt(sum((Sab[h] / h) ** 2 for h in range(2, 2000))) / Sab[1]
    h = np.arange(0, 161)
    fig, axs = plt.subplots(2, 1, figsize=(6.4, 4.8), sharex=True)
    for ax, S, title, col in ((axs[0], Sa, r"leg voltage $v_{a0}$", BLUE),
                              (axs[1], Sab, r"line voltage $v_{ab}$", ORANGE)):
        ax.vlines(h[1:], 0, S[1:161], color=col, lw=1.6)
        ax.set_ylim(0, 420)
        ax.set_xlim(0, 160)
        ax.set_ylabel("peak amplitude (V)")
        ax.text(0.99, 0.95, title, transform=ax.transAxes, ha="right", va="top", fontsize=9)
        ax.text(3, S[1] + 6, f"{S[1]:.0f}", fontsize=7, color=col, va="bottom")
        if S[51] > 5:
            ax.text(54, S[51] + 6, f"{S[51]:.0f} (h = 51)", fontsize=7, color=col, va="bottom")
        ax.text(42, S[49] + 6, f"{S[49]:.0f}", fontsize=7, color=col, va="bottom", ha="center")
        ax.text(60, S[53] + 6, f"{S[53]:.0f}", fontsize=7, color=col, va="bottom", ha="center")
        ax.text(102, S[101] + 6, f"{S[101]:.0f} (h = 101, 103)", fontsize=7, color=col, va="bottom", ha="center")
    axs[0].text(153, Sa[148:159].max() + 8, "cluster\nnear 153", fontsize=7, ha="center", va="bottom")
    axs[1].annotate("no line at h = 51", xy=(51, 3), xytext=(51, 190), fontsize=7, ha="center",
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7))
    axs[1].annotate("no line at h = 153", xy=(153, 3), xytext=(150, 190), fontsize=7, ha="center",
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7))
    axs[1].text(30, 300, "carrier and triplen sidebands\ncancel between legs\n"
                f"WTHD = {100 * wthd:.2f} %", fontsize=8, ha="left", va="center")
    axs[1].set_xlabel("harmonic order h")
    sec = axs[0].secondary_xaxis("top", functions=(lambda x: x * f1 / 1e3, lambda x: x * 1e3 / f1))
    sec.set_xlabel("frequency (kHz)")
    fig.tight_layout()
    print(f"  31.3: leg h1={Sa[1]:.1f} h51={Sa[51]:.1f} h49={Sa[49]:.1f} h101={Sa[101]:.1f}; "
          f"line h1={Sab[1]:.1f} h49={Sab[49]:.1f} h101={Sab[101]:.1f}; WTHD={100*wthd:.3f}%")
    save(fig, "31", "fig-31-3-spwm-spectrum")


# ----------------------------------------------------------------------------
# Figure 31.4 — LCL filter Bode plot
# ----------------------------------------------------------------------------
def fig_31_4():
    L1, L2, Cf, Rd = 1.91e-3, 0.8e-3, 15e-6, 2.0
    f = np.logspace(1, 5, 4000)
    s = 2j * np.pi * f

    def lcl(R):
        Zc = R + 1 / (s * Cf)
        return Zc / (s * L1 * s * L2 + (s * L1 + s * L2) * Zc)

    HL = 1 / (s * (L1 + L2))
    Hu, Hd = lcl(0.0), lcl(Rd)
    db = lambda H: 20 * np.log10(np.abs(H))
    fres = np.sqrt((L1 + L2) / (L1 * L2 * Cf)) / (2 * np.pi)
    fig = plt.figure(figsize=(6.4, 5.4))
    gsf = fig.add_gridspec(2, 1, height_ratios=[0.9, 2.6], hspace=0.08)
    ax = fig.add_subplot(gsf[1])
    ax.semilogx(f, db(HL), color=GREY, lw=1.4, label="L filter, 2.71 mH")
    ax.semilogx(f, np.clip(db(Hu), -200, 60), color=ORANGE, lw=1.4, label="LCL, undamped")
    ax.semilogx(f, db(Hd), color=BLUE, lw=1.8, label=r"LCL, $R_d=2\ \Omega$")
    for fx, txt in ((50, "50 Hz"), (fres, f"{fres/1e3:.2f} kHz\nresonance"), (1e4, "10 kHz\n$f_s$")):
        ax.axvline(fx, color=INK, ls="--", lw=0.7)
        ax.text(fx * 1.08, -60 if fx == 50 else -132, txt, fontsize=7.5, va="bottom")
    ax.set_xlim(10, 1e5)
    ax.set_ylim(-140, 20)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel(r"$|i_2/v_1|$ (dB re 1 S)")
    ax.grid(True, which="major", color=GRID, lw=0.5)
    ax.legend(loc="lower left", fontsize=8)
    att = 1 / abs(1 - (2 * np.pi * 1e4) ** 2 * L2 * Cf)
    k10 = np.argmin(np.abs(f - 1e4))
    ax.annotate(r"$|i_2/i_1|$ at 10 kHz = %.0f dB" % (20 * np.log10(att)),
                xy=(1e4, db(Hd)[k10]), xytext=(1.25e4, -48), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.text(250, -32, "−20 dB/dec", fontsize=7.5, color=GREY, rotation=-17)
    ax.text(1.3e4, -113, "−60 dB/dec", fontsize=7.5, color=ORANGE, rotation=-33)
    ax.text(2.4e4, -78, "−40 dB/dec above\n" + r"$1/(2\pi R_dC_f)$ = 5.3 kHz", fontsize=7, color=BLUE,
            ha="left", va="top")
    pk = db(Hd)[(f > 1e3) & (f < 3e3)].max()
    kpk = np.argmin(np.abs(f - fres))
    ax.annotate(f"damped peak {pk - db(HL)[kpk]:.0f} dB\nabove the L-filter line",
                xy=(fres, pk), xytext=(2.4e3, 2), fontsize=7.5,
                color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.7))
    # inset circuit
    axi = fig.add_subplot(gsf[0])
    d = _sd(axi, fontsize=7, lw=0.9)
    d += elm.SourceSin().at((0, 0)).to((0, 2)).label(r"$v_1$", loc="top", ofst=0.1)
    d += elm.Inductor2(loops=2).at((0, 2)).to((2.2, 2)).label(r"$L_1$ 1.91 mH", ofst=0.08)
    d += elm.Dot().at((2.2, 2))
    d += elm.Capacitor().at((2.2, 2)).to((2.2, 1.0)).label(r"$C_f$ 15 µF", loc="top", ofst=0.1)
    d += elm.Resistor().at((2.2, 1.0)).to((2.2, 0)).label(r"$R_d$ 2 Ω", loc="top", ofst=0.1)
    d += elm.Inductor2(loops=2).at((2.2, 2)).to((4.4, 2)).label(r"$L_2$ 0.8 mH", ofst=0.08)
    d += elm.SourceSin().at((4.4, 0)).to((4.4, 2)).label("grid\n230 V", loc="bottom", ofst=0.1)
    d += elm.Line().at((0, 0)).to((4.4, 0))
    axi.annotate("", xy=(3.9, 1.75), xytext=(3.1, 1.75), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK))
    axi.text(3.2, 1.65, r"$i_2$", fontsize=7, ha="center", va="top")
    axi.text(-3.4, 1.0, "LCL filter\n(per phase)", fontsize=8, ha="left", va="center")
    _finish(d, axi)
    axi.set_xlim(-3.5, 8.5)
    axi.set_ylim(-0.3, 2.9)
    print(f"  31.4: fres={fres:.0f} Hz, damped peak={pk:.1f} dB, att10k={20*np.log10(att):.1f} dB, "
          f"undamped@10k={db(Hu)[k10]:.1f}, damped@10k={db(Hd)[k10]:.1f}")
    save(fig, "31", "fig-31-4-lcl-filter-bode")


# ----------------------------------------------------------------------------
# Figure 31.5 — thermal network and junction-temperature ripple
# ----------------------------------------------------------------------------
# Typical 4-term Foster network of a 1200 V / 200 A IGBT (sums to 0.15 K/W)
FOSTER_R = np.array([0.008, 0.022, 0.070, 0.050])
FOSTER_TAU = np.array([0.0006, 0.006, 0.060, 0.30])
RCH = 0.02
TAU_CH = 0.5  # interface/baseplate lag, s


def _igbt_loss(t, fo, Ipk=141.0, M=1.0, pf=0.86, Vdc=560.0, fs=4e3):
    """Instantaneous (switching-period averaged) loss of one IGBT in an SPWM leg."""
    phi = np.arccos(pf)
    wt = 2 * np.pi * fo * t
    i = Ipk * np.sin(wt)
    duty = 0.5 * (1 + M * np.sin(wt + phi))
    ip = np.clip(i, 0, None)
    pc = (0.85 * ip + 5e-3 * ip ** 2) * duty
    ps = fs * 33e-3 * (ip / 200.0) * (Vdc / 600.0)
    return pc + ps


def _tj(fo, T=1.0, Ths=89.0):
    dt = min(1e-4, 1 / (fo * 400))
    t = np.arange(-6.0, T, dt)
    p = _igbt_loss(t, fo)
    Rs = np.append(FOSTER_R, RCH)
    taus = np.append(FOSTER_TAU, TAU_CH)
    pavg = p.mean()
    x = Rs * pavg  # start from the mean
    out = np.empty_like(t)
    a = np.exp(-dt / taus)
    for k, pk in enumerate(p):
        x = a * x + (1 - a) * Rs * pk
        out[k] = Ths + x.sum()
    m = t >= 0
    return t[m], out[m], pavg


def fig_31_5():
    fig = plt.figure(figsize=(6.8, 6.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.25], hspace=0.12)
    axc = fig.add_subplot(gs[0])
    axc.set_xlim(-1.4, 14.2)
    axc.set_ylim(-0.3, 6.1)
    axc.set_aspect("equal")
    axc.axis("off")
    lw = 0.9

    def res(x0, x1, y, txt=None, below=True):
        axc.add_patch(Rectangle((x0, y - 0.13), x1 - x0, 0.26, fc="white", ec=INK, lw=lw, zorder=3))
        if txt:
            axc.text(0.5 * (x0 + x1), y - 0.25 if below else y + 0.25, txt, fontsize=7,
                     ha="center", va="top" if below else "bottom")

    def foster(y, x0, n=4, w=1.0):
        x = x0
        for k in range(n):
            xa, xb = x + 0.12, x + w - 0.12
            axc.plot([x, xa], [y, y], color=INK, lw=lw)
            axc.plot([xb, x + w], [y, y], color=INK, lw=lw)
            axc.plot([xa, xa], [y - 0.32, y + 0.32], color=INK, lw=lw)
            axc.plot([xb, xb], [y - 0.32, y + 0.32], color=INK, lw=lw)
            axc.plot([xa, xb], [y + 0.32, y + 0.32], color=INK, lw=lw)
            axc.add_patch(Rectangle((xa + 0.16, y + 0.22), xb - xa - 0.32, 0.2, fc="white", ec=INK, lw=lw, zorder=3))
            xm = 0.5 * (xa + xb)
            axc.plot([xa, xm - 0.05], [y - 0.32, y - 0.32], color=INK, lw=lw)
            axc.plot([xm + 0.05, xb], [y - 0.32, y - 0.32], color=INK, lw=lw)
            axc.plot([xm - 0.05] * 2, [y - 0.46, y - 0.18], color=INK, lw=1.2)
            axc.plot([xm + 0.05] * 2, [y - 0.46, y - 0.18], color=INK, lw=1.2)
            x += w
        return x

    xbus = 9.2
    rows = ((4.3, BLUE, "IGBT", "81 W", "0.15", "103 °C"), (2.2, ORANGE, "diode", "21 W", "0.25", "95 °C"))
    for y, col, nm, pw, rth, tj in rows:
        axc.add_patch(Circle((0.5, y), 0.36, fc="white", ec=col, lw=1.3, zorder=3))
        axc.annotate("", xy=(0.5, y + 0.25), xytext=(0.5, y - 0.25),
                     arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0), zorder=4)
        axc.text(0.05, y, f"{nm} loss\n{pw}", fontsize=7, ha="right", va="center", color=col)
        axc.plot([0.86, 1.6], [y, y], color=INK, lw=lw)
        axc.plot(1.3, y, "o", color=col, ms=4, zorder=4)
        axc.text(1.3, y - 0.2, rf"$T_j$" + "\n" + tj, fontsize=7, ha="center", va="top", color=col)
        xe = foster(y, 1.6)
        axc.text(4.1, y + 0.55, rf"$Z_{{th,jc}}$: 4 RC pairs, $\Sigma R$ = {rth} K/W", fontsize=7,
                 ha="center", va="bottom", color=col)
        axc.plot([xe, 6.4], [y, y], color=INK, lw=lw)
        axc.plot(6.0, y, "o", color=INK, ms=3, zorder=4)
        axc.text(6.0, y + 0.18, "case", fontsize=6.5, ha="center", va="bottom")
        res(6.4, 7.4, y, r"$R_{th,ch}$ 0.02 K/W")
        axc.plot([7.4, xbus], [y, y], color=INK, lw=lw)
    axc.plot([xbus, xbus], [2.2, 4.3], color=INK, lw=lw)
    yh = 3.25
    axc.plot(xbus, yh, "o", color=GREEN, ms=5, zorder=4)
    axc.text(xbus - 0.15, yh, "heatsink\n89 °C", fontsize=7.5, ha="right", va="center", color=GREEN)
    axc.plot([xbus, 10.4], [yh, yh], color=INK, lw=lw)
    res(10.4, 11.6, yh, r"$R_{th,ha}$ 0.08 K/W", below=False)
    axc.plot([11.6, 12.5], [yh, yh], color=INK, lw=lw)
    axc.plot([12.5, 12.5], [yh, yh - 0.6], color=INK, lw=lw)
    for k, wdt in enumerate((0.5, 0.33, 0.16)):
        axc.plot([12.5 - wdt / 2, 12.5 + wdt / 2], [yh - 0.6 - 0.12 * k] * 2, color=INK, lw=1.2)
    axc.text(12.5, yh - 1.0, "ambient\n40 °C", fontsize=7.5, ha="center", va="top")
    # other switch positions
    axc.plot([xbus, xbus], [0.5, 2.2], color=GREY, lw=lw, ls="--")
    axc.annotate("", xy=(xbus, 1.6), xytext=(xbus, 0.6),
                 arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.0))
    axc.text(xbus + 0.15, 0.55, "heat from the other five switch positions\n(total inverter loss 612 W)",
             fontsize=7, ha="left", va="center", color=GREY)
    axc.text(-0.1, 6.0, "one switch position (IGBT + diode) of the 55 kW inverter, 4 kHz",
             fontsize=8, ha="left", va="top")

    ax = fig.add_subplot(gs[1])
    res_ = {}
    for fo, col in ((50, BLUE), (5, GREEN), (1, ORANGE)):
        t, tj, pavg = _tj(fo)
        res_[fo] = (tj.max() - tj.min(), tj.max(), tj.mean(), pavg)
        ax.plot(t, tj, color=col, lw=1.1 if fo == 50 else 1.5,
                label=f"{fo} Hz: ripple {tj.max()-tj.min():.0f} K, peak {tj.max():.0f} °C")
    ax.axhline(103, color=BLUE, ls=":", lw=0.8)
    ax.text(1.005, 103, "103 °C\n(mean)", fontsize=7, color=BLUE, va="center", ha="left")
    ax.axhline(89, color=GREY, ls="--", lw=1.0)
    ax.text(1.005, 89, "heatsink\n89 °C", fontsize=7, color=GREY, ha="left", va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(80, 140)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("IGBT junction temperature (°C)")
    ax.legend(loc="upper left", fontsize=7.5, title="output frequency (same 100 A RMS)", title_fontsize=7.5,
              ncol=1, bbox_to_anchor=(0.0, 1.03))
    ax.text(0.99, 0.02, "typical Foster network; ripple values illustrative",
            transform=ax.transAxes, fontsize=7, ha="right", va="bottom", color=GREY)
    print("  31.5:", {k: tuple(round(float(x), 1) for x in v) for k, v in res_.items()})
    save(fig, "31", "fig-31-5-inverter-thermal-network")



if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4", "5"]
    for w in which:
        globals()[f"fig_31_{w}"]()
