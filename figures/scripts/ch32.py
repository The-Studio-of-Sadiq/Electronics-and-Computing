"""Figures for Chapter 32 — Motor Drives and Power Conversion.

Run from the repository root:  python figures/scripts/ch32.py
"""
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch, Ellipse  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save  # noqa: E402

schemdraw.use("matplotlib")
warnings.filterwarnings("ignore", message=".*non-interactive.*")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
GREY = "#888888"
RED = "#C62828"
FC_POW = "#EEF3F8"
FC_DC = "#FFF4E0"
FC_CTL = "#E9F5EC"


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


def _canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _motor(ax, x, y, r=0.55, txt="M", fs=8, fc="white"):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=INK, lw=1.0, zorder=3))
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, zorder=4)


def _harrow(ax, x0, x1, y, both=False, color=INK, lw=1.1):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=7))


def _varrow(ax, x, y0, y1, both=False, color=INK, lw=1.1):
    ax.annotate("", xy=(x, y1), xytext=(x, y0),
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=7))


# ----------------------------------------------------------------------------
# Figure 32.1 — drive architectures
# ----------------------------------------------------------------------------
def fig_32_1():
    fig, ax = _canvas(6.8, 7.0, (-0.2, 20.2), (-0.3, 20.6))
    fs = 7.2
    h = 1.3

    def row_title(y, txt):
        ax.text(-0.1, y, txt, fontsize=8.5, ha="left", va="bottom", fontweight="bold", color=INK)

    def chain(y, blocks, both=False, gap=0.62):
        """blocks: list of (width, text, fc). Returns list of (x0, x1)."""
        xs = []
        x = 0.0
        for k, (w, txt, fc) in enumerate(blocks):
            if txt == "M":
                _motor(ax, x + w / 2, y + h / 2, r=h / 2 + 0.05, txt=fc, fs=6.8)
            else:
                box(ax, x, y, w, h, txt, fc=fc, fontsize=fs)
            xs.append((x, x + w))
            if k < len(blocks) - 1:
                _harrow(ax, x + w + 0.03, x + w + gap - 0.03, y + h / 2, both=both,
                        color=BLUE if not both else GREEN)
            x += w + gap
        return xs

    # Row 1: standard VFD
    y1 = 17.2
    row_title(y1 + h + 1.0, "1  Standard VFD (2 quadrants + braking)")
    xs = chain(y1, [(1.75, "400 V\ngrid", "#F4F4F4"), (2.0, "3 % line\nreactor", FC_POW),
                    (2.2, "6-diode\nbridge", FC_POW), (1.75, "DC\nchoke", FC_POW),
                    (2.3, "DC link\n540 V", FC_DC), (2.6, "2-level IGBT\ninverter", FC_POW),
                    (2.1, "M", "IM\n37 kW")])
    xb = 0.5 * (xs[4][0] + xs[4][1])
    _varrow(ax, xb, y1 - 0.02, y1 - 0.55, color=ORANGE)
    box(ax, xb - 1.6, y1 - 1.75, 3.2, 1.15, "brake chopper\n+ resistor", fc="#FBE3D6", fontsize=fs)
    ax.text(xb + 1.75, y1 - 1.2, "braking energy\nburnt as heat", fontsize=6.5, color=ORANGE, va="center")

    # Row 2: regenerative VFD
    y2 = 12.9
    row_title(y2 + h + 0.35, "2  Regenerative VFD with active front end (4 quadrants)")
    xs = chain(y2, [(1.75, "400 V\ngrid", "#F4F4F4"), (2.0, "LCL\nfilter", FC_POW),
                    (2.6, "IGBT active\nfront end", FC_POW), (2.3, "DC link\n650 V", FC_DC),
                    (2.6, "2-level\ninverter", FC_POW), (2.4, "M", "crane\nhoist")], both=True)
    ax.text(xs[-1][1] + 0.25, y2 + h / 2, "lowering:\npower flows\nback to grid", fontsize=6.5,
            color=GREEN, va="center")

    # Row 3: common DC bus
    y3 = 9.9
    row_title(y3 + h + 0.35, "3  Common DC bus (energy exchanged between drives)")
    xs = chain(y3, [(1.75, "400 V\ngrid", "#F4F4F4"), (2.4, "AFE\n(+ LCL)", FC_POW)], both=True)
    xbus0, xbus1 = xs[-1][1] + 0.62, 19.6
    ybus = y3 + h / 2
    ax.plot([xbus0, xbus1], [ybus, ybus], color=ORANGE, lw=4, solid_capstyle="butt", zorder=2)
    _harrow(ax, xs[-1][1] + 0.03, xbus0, ybus, both=True, color=GREEN)
    ax.text(0.5 * (xbus0 + xbus1), ybus + 0.3, "650 V DC bus", fontsize=7.5, ha="center", va="bottom",
            color=ORANGE)
    names = [("unwinder", "regenerating", GREEN, True), ("winder 1", "motoring", BLUE, False),
             ("winder 2", "motoring", BLUE, False)]
    for k, (nm, mode, col, regen) in enumerate(names):
        xc = xbus0 + 1.7 + k * 4.0
        if regen:
            _varrow(ax, xc, ybus - 2.1, ybus - 0.12, color=col)
        else:
            _varrow(ax, xc, ybus - 0.12, ybus - 2.1, color=col)
        box(ax, xc - 1.1, ybus - 3.25, 2.2, 1.1, "inverter", fc=FC_POW, fontsize=fs)
        if regen:
            _varrow(ax, xc, ybus - 4.2, ybus - 3.3, color=col)
        else:
            _varrow(ax, xc, ybus - 3.3, ybus - 4.2, color=col)
        _motor(ax, xc, ybus - 4.8, r=0.6, txt="M", fs=8)
        ax.text(xc + 0.75, ybus - 4.8, f"{nm}\n{mode}", fontsize=6.5, va="center", color=col)
    ax.text(17.0, ybus - 2.6, "unwinder braking power\nfeeds the winders\ndirectly; only the net\n"
            "power passes\nthrough the AFE", fontsize=6.3, ha="left", va="center", color=INK)

    # Row 4: EV traction
    y4 = 0.4
    row_title(y4 + h + 2.05, "4  EV traction drive (800 V battery)")
    xs = chain(y4, [(3.4, "800 V battery\n+ contactors\n+ precharge", "#E8E2F2"),
                    (2.9, "film DC-link\ncapacitor\n500 µF", FC_DC), (2.6, "SiC\ninverter", FC_POW),
                    (2.4, "M", "PMSM\n200 kW")], both=True)
    xb = 0.5 * (xs[1][0] + xs[1][1])
    yl = y4 + h + 1.55
    ax.plot([xb, xb], [y4 + h, yl], color=INK, lw=1.0)
    ax.plot([xb, 18.1], [yl, yl], color=INK, lw=1.0)
    ax.plot(xb, yl, "o", color=INK, ms=3)
    ax.text(xb + 0.2, yl + 0.1, "800 V bus", fontsize=6.3, va="bottom")
    for xc_, txt in ((14.45, "on-board\ncharger"), (18.1, "DC–DC\nto 12 V")):
        _varrow(ax, xc_, yl, yl - 0.45, both=True, color=GREEN)
        box(ax, xc_ - 1.45, yl - 1.45, 2.9, 1.0, txt, fc=FC_POW, fontsize=fs)
    ax.text(13.3, y4 + 0.05, "regenerative braking limited\nby battery charge acceptance", fontsize=6.5,
            color=GREEN, va="bottom")
    ax.text(17.2, 19.9, "→ motoring power flow\n↔ bidirectional", fontsize=6.5, color=GREY, ha="left", va="top")
    save(fig, "32", "fig-32-1-drive-architectures")


# ----------------------------------------------------------------------------
# Figure 32.2 — reflected wave and bearing voltage
# ----------------------------------------------------------------------------
def _motor_terminal(t, length, tr, Vdc=560.0, Gm=0.85, v=150.0, shape="lin",
                    eta=5e-4, kap=1.5e-3):
    """Bounce-diagram motor-terminal voltage (t, tr in microseconds, length in m).

    The inverter end reflects with -1 and the motor end with Gm.  Each round trip
    after the first arrival loses amplitude exp(-eta*d) and its edge is slowed by
    dispersion kap*d (microseconds per metre), a crude model of cable loss.
    """
    tp = length / v
    out = np.zeros_like(t)

    def edge(x, r):
        z = np.clip(x / r, 0, 1)
        return z if shape == "lin" else 0.5 - 0.5 * np.cos(np.pi * z)

    k = 0
    while (2 * k + 1) * tp < t[-1] and k < 2000:
        dd = 2 * k * length
        trk = np.sqrt(tr ** 2 + (kap * dd) ** 2)
        a = np.exp(-eta * dd)
        out += (1 + Gm) * ((-Gm) ** k) * a * Vdc * edge(t - (2 * k + 1) * tp, trk)
        k += 1
    return out


def fig_32_2():
    fig = plt.figure(figsize=(6.8, 4.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.08)
    ax = fig.add_subplot(gs[0])
    t = np.linspace(0, 10, 20001)
    t0 = 0.3  # edge start
    vin = 560 * np.clip((t - t0) / 0.1, 0, 1)
    ax.plot(t, vin, color=INK, lw=1.0, ls="--", label="inverter output (100 ns)")
    res = {}
    for L, col in ((5, GREEN), (50, BLUE), (300, ORANGE)):
        vm = _motor_terminal(t - t0, L, 0.1)
        res[L] = vm.max()
        ax.plot(t, vm, color=col, lw=1.3, label=f"motor, {L} m cable (peak {vm.max():.0f} V)")
    vf = _motor_terminal(t - t0, 50, 1.12)
    res["dvdt"] = vf.max()
    ax.plot(t, vf, color=PINK, lw=1.6, ls=":", label=f"50 m with dv/dt filter, 1.12 µs (peak {vf.max():.0f} V)")
    ax.axhline(1600, color=RED, ls="--", lw=1.0)
    ax.text(9.9, 1620, "1600 V: NEMA MG 1 Part 31 limit", fontsize=7, color=RED, ha="right", va="bottom")
    ax.axhline(560, color=GREY, lw=0.6, ls=":")
    ax.text(9.9, 540, r"$V_{dc}$ = 560 V", fontsize=7, color=GREY, ha="right", va="top")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1750)
    ax.set_xlabel("time (µs)")
    ax.set_ylabel("voltage (V)")
    ax.legend(loc="upper left", fontsize=6.6, bbox_to_anchor=(0.0, 0.93))
    ax.text(2.2, 950, "50 m rings at ≈ 750 kHz", fontsize=6.8, color=BLUE)

    # --- motor cross-section and divider ---------------------------------
    axm = fig.add_subplot(gs[1])
    yo = 1.4
    axm.add_patch(Rectangle((0.6, 5.6 + yo), 5.6, 3.6, fc="#F2F2F2", ec=INK, lw=1.2))
    axm.add_patch(Rectangle((1.1, 8.15 + yo), 4.6, 0.55, fc="#F6C28B", ec=INK, lw=0.8))
    axm.add_patch(Rectangle((1.1, 6.1 + yo), 4.6, 0.55, fc="#F6C28B", ec=INK, lw=0.8))
    axm.text(3.4, 8.42 + yo, "stator winding", fontsize=6.5, ha="center", va="center")
    axm.add_patch(Rectangle((1.6, 6.85 + yo), 3.6, 1.1, fc="#C9D7E8", ec=INK, lw=0.8))
    axm.text(3.4, 7.62 + yo, "rotor", fontsize=6.5, ha="center", va="center")
    axm.plot([0.0, 6.9], [7.4 + yo, 7.4 + yo], color=INK, lw=2.4)  # shaft
    for xb in (0.85, 5.95):
        axm.add_patch(Rectangle((xb - 0.2, 7.0 + yo), 0.4, 0.8, fc="white", ec=INK, lw=0.9, zorder=3))
        axm.add_patch(Circle((xb, 7.62 + yo), 0.09, fc=INK, zorder=4))
        axm.add_patch(Circle((xb, 7.18 + yo), 0.09, fc=INK, zorder=4))
    axm.text(3.4, 9.35 + yo, "motor cross-section", fontsize=6.5, ha="center",
             va="bottom")
    axm.text(6.3, 5.65 + yo, "frame (earthed)", fontsize=6.5, ha="left", va="bottom")
    # fluted race inset
    axm.add_patch(Rectangle((7.4, 8.2 + yo), 2.6, 1.2, fc="white", ec=INK, lw=0.8))
    for k in range(14):
        xk = 7.55 + k * 0.17
        axm.plot([xk, xk + 0.05], [8.32 + yo, 9.28 + yo], color=GREY, lw=1.0)
    axm.text(8.7, 8.05 + yo, "fluted race\n(EDM damage)", fontsize=6.3, ha="center", va="top")
    # common-mode staircase
    tt = np.array([0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7])
    lev = np.array([-3, -3, -1, -1, 1, 1, 3, 3, 1, 1, -1, -1, -3, -3]) * 93.3
    axm.plot(0.3 + tt * 0.25, 5.75 + lev / 280 * 0.45, color=BLUE, lw=0.9)
    axm.text(2.3, 5.75, r"$v_{cm}$: steps of 187 V, peak ±280 V", fontsize=6.3, color=BLUE,
             ha="left", va="center")
    # divider schematic
    d = _sd(axm, fontsize=7, lw=0.9, unit=1.2)
    xs, yt, yb = 1.2, 4.3, 0.6
    d += elm.SourceV().at((xs, yb)).to((xs, yt - 0.3)).label(r"$v_{cm}$", loc="top", ofst=0.15)
    d += elm.Line().at((xs, yt - 0.3)).to((xs, yt))
    d += elm.Capacitor().at((xs, yt)).to((4.0, yt)).label(r"$C_{wr}$ 100 pF", ofst=0.1)
    d += elm.Dot().at((4.0, yt))
    d += elm.Capacitor().at((4.0, yt)).to((4.0, yb)).label(r"$C_{rf}$" + "\n1.5 nF", loc="top", ofst=0.15)
    d += elm.Line().at((4.0, yt)).to((6.6, yt))
    d += elm.Capacitor().at((6.6, yt)).to((6.6, yb)).label(r"$2C_b$" + "\n2×150 pF", loc="bottom", ofst=0.15)
    d += elm.Line().at((xs, yb)).to((6.6, yb))
    d += elm.Ground().at((4.0, yb))
    axm.text(4.1, yt + 0.2, "shaft", fontsize=6.5, ha="left", va="bottom")
    axm.annotate("", xy=(9.5, yt - 0.05), xytext=(9.5, yb + 0.05),
                 arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0))
    axm.text(9.65, 2.45, r"$v_b\approx$ 15 V" + "\nBVR 5.3 %", fontsize=7, color=RED, va="center")
    _finish(d, axm, xlim=(0, 11.6), ylim=(-0.2, 11.4))
    print("  32.2:", {k: round(float(v)) for k, v in res.items()})
    save(fig, "32", "fig-32-2-reflected-wave-bearing")


# ----------------------------------------------------------------------------
# Figure 32.3 — VFD hardware and control-period timing
# ----------------------------------------------------------------------------
def fig_32_3():
    fig = plt.figure(figsize=(6.8, 7.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.25], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 9.6)
    ax.set_aspect("equal")
    ax.axis("off")
    fs = 7
    y, h = 5.6, 1.7
    blocks = [(0.0, 2.1, "EMC\nfilter\n(X, Y, CM)"), (2.5, 2.6, "diode bridge\n+ precharge\nR and relay"),
              (5.5, 1.7, "DC\nchoke"), (7.6, 2.3, "DC link\n4.7 mF"), (10.3, 2.5, "brake\nchopper"),
              (13.2, 3.0, "IGBT six-pack\n+ NTC")]
    for x, w, txt in blocks:
        box(ax, x, y, w, h, txt, fc=FC_DC if "DC link" in txt else FC_POW, fontsize=fs)
    for (x, w, _), (xn, _, _) in zip(blocks[:-1], blocks[1:]):
        _harrow(ax, x + w + 0.02, xn - 0.02, y + h / 2, color=BLUE)
    _harrow(ax, 16.22, 17.7, y + h / 2, color=BLUE)
    _motor(ax, 18.5, y + h / 2, r=0.75, txt="M\n37 kW", fs=6.8)
    ax.text(0.0, y + h + 0.15, "400 V in", fontsize=6.5, ha="left", va="bottom")
    # sensors
    for xx in (16.6, 17.2):
        ax.add_patch(Rectangle((xx - 0.2, y + h / 2 - 0.35), 0.4, 0.7, fc="#FFE9A8", ec=INK, lw=0.7, zorder=4))
    ax.text(16.9, y + h / 2 + 0.5, "Hall a, b", fontsize=6.3, ha="center", va="bottom")
    # control rows
    yc = 0.9
    box(ax, 4.8, yc, 5.6, 2.1, "Cortex-M4 MCU\nPWM timer · ADC · fieldbus", fc=FC_CTL, fontsize=fs)
    box(ax, 7.3, 3.55, 2.9, 1.25, "isolated V$_{dc}$\nmeasurement", fc=FC_CTL, fontsize=fs)
    box(ax, 12.7, yc, 3.3, 2.1, "isolated gate\ndrivers (desat,\nMiller clamp)", fc=FC_CTL, fontsize=fs)
    box(ax, 17.0, yc, 2.9, 2.1, "STO channel\ncuts driver\nsupply", fc="#FBE3D6", fontsize=fs)
    _harrow(ax, 10.42, 12.68, yc + 1.05, color=GREEN)
    ax.text(11.55, yc + 1.2, "6 PWM", fontsize=6.3, ha="center", va="bottom", color=GREEN)
    _varrow(ax, 14.7, yc + 2.12, y - 0.02, color=GREEN)
    _harrow(ax, 16.98, 16.02, yc + 1.05, color=RED)
    _varrow(ax, 8.75, y - 0.02, 4.82, color=GREY)
    _varrow(ax, 8.75, 3.53, yc + 2.12, color=GREY)
    ax.plot([16.9, 16.9, 10.3, 10.3], [y + h / 2 - 0.37, 5.15, 5.15, yc + 2.4], color=GREY, lw=0.9, ls="--")
    ax.annotate("", xy=(10.3, yc + 2.12), xytext=(10.3, yc + 2.45),
                arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.9))
    ax.text(12.0, 5.05, "i$_a$, i$_b$", fontsize=6.5, color=GREY, va="top")
    ax.text(0.0, 9.35, "power stage", fontsize=7.5, color=BLUE, va="top")
    ax.text(0.0, 2.2, "control and\nprotection", fontsize=7.5, color=GREEN, va="center")

    # --- timing ---------------------------------------------------------
    axt = fig.add_subplot(gs[1])
    T = 125.0
    t = np.linspace(0, 2 * T, 50001)
    cnt = 10500 * (1 - np.abs(1 - 2 * ((t / T) % 1.0)))   # 0 at period boundaries, peak mid-period
    rows = {"cnt": 7.2, "adc": 5.75, "isr": 4.75, "load": 3.75, "gH": 2.55, "gL": 1.35}
    axt.plot(t, rows["cnt"] + 1.6 * cnt / 10500, color=INK, lw=1.2)
    duty = [0.62, 0.45]
    axt.text(-3, rows["cnt"] + 1.6, "10500", fontsize=6.5, ha="right", va="center")
    axt.text(-3, rows["cnt"], "0", fontsize=6.5, ha="right", va="center")
    for k, dk in enumerate(duty):
        axt.plot([k * T, (k + 1) * T], [rows["cnt"] + 1.6 * dk] * 2, color=BLUE, ls="--", lw=0.8)
        axt.text(k * T + 3, rows["cnt"] + 1.6 * dk + 0.08, f"compare = {dk:.2f} × 10500", fontsize=6.0,
                 color=BLUE, va="bottom")
    axt.text(2 * T + 2, rows["cnt"] + 0.8, "up–down\ncounter", fontsize=6.5, va="center")
    for tk in (T / 2, 1.5 * T):
        axt.plot([tk, tk], [rows["adc"], rows["adc"] + 0.6], color=ORANGE, lw=1.5)
        axt.add_patch(Rectangle((tk, rows["adc"] - 0.05), 2.0, 0.3, fc=ORANGE, alpha=0.5, lw=0))
        axt.add_patch(Rectangle((tk + 2.0, rows["isr"]), 40.0, 0.55, fc=GREEN, alpha=0.35, ec=GREEN, lw=0.8))
        axt.text(tk + 22, rows["isr"] + 0.27, "ISR ≈ 40 µs", fontsize=6.3, ha="center", va="center")
        axt.text(tk + 2.5, rows["adc"] + 0.45, "ADC conversion 2 µs", fontsize=6.0, ha="left", va="center",
                 color=ORANGE)
    for tk in (T, 2 * T):
        axt.plot([tk, tk], [rows["load"], rows["load"] + 0.6], color=PINK, lw=1.5)
    axt.text(2 * T + 2, rows["adc"] + 0.3, "ADC trigger\nat peak", fontsize=6.5, va="center")
    axt.text(2 * T + 2, rows["isr"] + 0.27, "control ISR", fontsize=6.5, va="center")
    axt.text(2 * T + 2, rows["load"] + 0.3, "shadow load\nat zero", fontsize=6.5, va="center")
    # gate signals: upper on while the counter is below the compare value (Listing 31.1)
    td = 1.0
    for k, dk in enumerate(duty):
        half = dk * T / 2
        a0, a1 = k * T + half, (k + 1) * T - half      # upper turns off at a0, back on at a1
        axt.plot([k * T, a0, a0, a1, a1, (k + 1) * T],
                 [rows["gH"] + 0.6] * 2 + [rows["gH"]] * 2 + [rows["gH"] + 0.6] * 2, color=BLUE, lw=1.2)
        axt.plot([k * T, a0 + td, a0 + td, a1 - td, a1 - td, (k + 1) * T],
                 [rows["gL"]] * 2 + [rows["gL"] + 0.6] * 2 + [rows["gL"]] * 2, color=ORANGE, lw=1.2)
    axt.text(2 * T + 2, rows["gH"] + 0.3, "gate a, upper", fontsize=6.5, va="center", color=BLUE)
    axt.text(2 * T + 2, rows["gL"] + 0.3, "gate a, lower", fontsize=6.5, va="center", color=ORANGE)
    tz = T + duty[1] * T / 2
    axt.annotate("1 µs dead time at every\nedge (too short to see\nat this scale)", xy=(tz + td, rows["gL"] + 0.3),
                 xytext=(tz + 45, rows["gL"] - 1.05), fontsize=6.3, ha="center",
                 arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    # delay annotation
    ya = -0.75
    _harrow(axt, T / 2, 1.5 * T, ya, both=True)
    axt.text(T, ya - 0.15, "sample → centre of updated period: 1 period = 125 µs", fontsize=6.8,
             ha="center", va="top")
    axt.plot([T / 2, T / 2], [ya, rows["adc"]], color=GREY, lw=0.5, ls=":")
    axt.plot([1.5 * T, 1.5 * T], [ya, rows["cnt"]], color=GREY, lw=0.5, ls=":")
    axt.annotate("", xy=(T + 3, rows["load"] + 0.3), xytext=(T / 2 + 42, rows["isr"] + 0.2),
                 arrowprops=dict(arrowstyle="-|>", color=GREY, lw=0.7))
    axt.text(T * 1.5, rows["gH"] + 0.85, "new duty (0.45) applies in this period", fontsize=6.3, ha="center", color=BLUE)
    axt.set_xlim(0, 2 * T)
    axt.set_ylim(-1.6, 9.1)
    axt.set_yticks([])
    axt.spines["left"].set_visible(False)
    axt.set_xticks([0, T / 2, T, 1.5 * T, 2 * T])
    axt.set_xlabel("time (µs), carrier 8 kHz (period 125 µs)")
    for tk in (T, 2 * T):
        axt.axvline(tk, color=GRID, lw=0.6, zorder=0)
    save(fig, "32", "fig-32-3-vfd-hardware-timing")


# ----------------------------------------------------------------------------
# Figure 32.4 — on-board charger and CC-CV profile
# ----------------------------------------------------------------------------
def _cccv(Q=3.0, R=0.05, I=3.0, Vmax=4.2, s0=0.10, iterm=0.15, tend=80 * 60, dt=1.0):
    t = np.arange(0, tend + dt, dt)
    s, mode = s0, "CC"
    V, Iout, S = [], [], []
    for tk in t:
        ocv = 3.3 + 0.9 * s
        if mode == "CC" and ocv + I * R >= Vmax:
            mode = "CV"
            t_cv = tk
            s_cv = s
        if mode == "CC":
            i = I
            v = ocv + i * R
        elif mode == "CV":
            i = (Vmax - ocv) / R
            v = Vmax
            if i <= iterm:
                mode = "DONE"
                t_done = tk
        if mode == "DONE":
            i = 0.0
            v = ocv
        s += i * dt / (Q * 3600)
        V.append(v)
        Iout.append(i)
        S.append(s)
    return t / 60, np.array(V), np.array(Iout), np.array(S), t_cv / 60, s_cv, t_done / 60


def fig_32_4():
    fig = plt.figure(figsize=(6.8, 6.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.05, 1.0], hspace=0.12)
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 20.3)
    ax.set_ylim(0, 10.2)
    ax.set_aspect("equal")
    ax.axis("off")
    fs = 6.5
    y, h = 5.8, 1.9
    blk = [(0.0, 1.9, "230 V\n32 A\nAC inlet", "#F4F4F4"), (2.25, 1.6, "EMI\nfilter", FC_POW),
           (4.2, 3.7, "totem-pole PFC\nGaN leg 65 kHz\n+ slow Si leg\nL = 100 µH", FC_POW),
           (8.25, 2.3, "400 V bus\n1.47 mF", FC_DC),
           (10.9, 3.7, "LLC: full bridge,\nLr Cr, Lm, HF\ntransformer,\nsync. rectifier", FC_POW),
           (14.95, 1.5, "output\nfilter", FC_POW)]
    for x, w, txt, fc in blk:
        box(ax, x, y, w, h, txt, fc=fc, fontsize=fs)
    for (x, w, *_), (xn, *_) in zip(blk[:-1], blk[1:]):
        _harrow(ax, x + w + 0.02, xn - 0.02, y + h / 2, color=BLUE)
    # contactors and pack
    xk = 16.65
    ax.plot([16.45, xk], [y + h / 2] * 2, color=INK, lw=1.0)
    ax.plot([xk, xk + 0.35], [y + h / 2, y + h / 2 + 0.3], color=INK, lw=1.2)
    ax.plot([xk + 0.45, 17.3], [y + h / 2] * 2, color=INK, lw=1.0)
    ax.text(xk + 0.25, y + h / 2 - 0.35, "con-\ntactor", fontsize=5.8, ha="center", va="top")
    box(ax, 17.3, y - 0.3, 2.7, h + 0.6, "77 kWh\nbattery\npack", fc="#E8E2F2", fontsize=7.5)
    # DC fast charge path
    ax.text(10.0, 9.95, "DC fast-charge inlet (bypasses the OBC)", fontsize=6.6, ha="left", va="top",
            color=ORANGE)
    ax.plot([9.8, 18.4, 18.4], [9.4, 9.4, y + h + 0.3], color=ORANGE, lw=1.4)
    ax.annotate("", xy=(18.4, y + h + 0.32), xytext=(18.4, y + h + 0.9),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.4))
    ax.plot([17.6, 17.95], [9.4, 9.7], color=ORANGE, lw=1.2)
    ax.text(17.75, 9.2, "own contactors", fontsize=6.0, ha="center", va="top", color=ORANGE)
    # control
    yc = 1.0
    box(ax, 0.6, yc, 3.4, 1.7, "current loop\n(PI)", fc=FC_CTL, fontsize=fs, ls="--")
    box(ax, 0.6, yc + 2.1, 3.4, 1.4, "voltage loop\n(PI)", fc=FC_CTL, fontsize=fs, ls="--")
    box(ax, 5.0, yc + 0.8, 3.0, 1.9, "minimum\nselector", fc=FC_CTL, fontsize=fs, ls="--")
    _harrow(ax, 4.02, 4.98, yc + 0.85, color=GREEN)
    _harrow(ax, 4.02, 4.98, yc + 2.55, color=GREEN)
    _harrow(ax, 8.02, 10.6, yc + 1.75, color=GREEN)
    ax.text(9.3, yc + 1.9, "duty / frequency", fontsize=6.0, ha="center", va="bottom", color=GREEN)
    ax.plot([10.6, 11.9, 11.9], [yc + 1.75, yc + 1.75, y - 0.02], color=GREEN, lw=1.0)
    ax.annotate("", xy=(11.9, y - 0.02), xytext=(11.9, y - 0.5), arrowprops=dict(arrowstyle="-|>", color=GREEN))
    box(ax, 14.0, yc + 0.2, 2.6, 2.2, "charge\ncontroller", fc=FC_CTL, fontsize=fs)
    box(ax, 17.2, yc + 0.2, 2.7, 2.2, "BMS", fc="#E8E2F2", fontsize=7.5)
    _harrow(ax, 16.62, 17.18, yc + 1.3, both=True, color=PINK)
    ax.text(16.9, yc + 2.55, "CAN:\ncurrent limits", fontsize=6.0, ha="center", va="bottom", color=PINK)
    ax.plot([14.0, 12.8, 12.8], [yc + 1.3, yc + 1.3, yc - 0.4], color=GREY, lw=0.9, ls="--")
    ax.plot([12.8, 2.3, 2.3], [yc - 0.4, yc - 0.4, yc], color=GREY, lw=0.9, ls="--")
    ax.text(7.5, yc - 0.55, r"$I_{ref}$, $V_{ref}$ set-points", fontsize=6.0, ha="center", va="top", color=GREY)
    ax.text(0.0, 10.0, "on-board charger 7.4 kW", fontsize=7.5, color=BLUE, va="top")

    # --- CC-CV plot -----------------------------------------------------
    axp = fig.add_subplot(gs[1])
    tm, V, I, S, tcv, scv, tdone = _cccv()
    axp.plot(tm, V, color=BLUE, lw=1.8, label="cell voltage")
    axp.set_xlim(0, 80)
    axp.set_ylim(3.3, 4.3)
    axp.set_xlabel("time (min)")
    axp.set_ylabel("cell voltage (V)", color=BLUE)
    axp.tick_params(axis="y", colors=BLUE)
    axi = axp.twinx()
    axi.spines["right"].set_visible(True)
    axi.plot(tm, I, color=ORANGE, lw=1.8, label="current")
    axi.set_ylim(0, 3.5)
    axi.set_ylabel("current (A)", color=ORANGE)
    axi.tick_params(axis="y", colors=ORANGE)
    axs = axp.twinx()
    axs.spines["right"].set_visible(True)
    axs.spines["right"].set_position(("axes", 1.13))
    axs.plot(tm, 100 * S, color=GREEN, lw=1.4, ls="--", label="state of charge")
    axs.set_ylim(0, 100)
    axs.set_ylabel("state of charge (%)", color=GREEN)
    axs.tick_params(axis="y", colors=GREEN)
    axp.axvline(tcv, color=GREY, lw=0.8, ls=":")
    axp.axvline(tdone, color=GREY, lw=0.8, ls=":")
    axp.text(tcv / 2, 3.36, "CC: 3 A (1C)", fontsize=7.5, ha="center")
    axp.text((tcv + tdone) / 2, 3.36, "CV: 4.2 V", fontsize=7.5, ha="center")
    axs.annotate(f"SOC {100*scv:.0f} % at\nCC→CV ({tcv:.0f} min)", xy=(tcv, 100 * scv),
                 xytext=(tcv - 23, 100 * scv + 3), fontsize=7, color=GREEN,
                 arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    axi.annotate(r"$\tau$ = 10 min decay" + f"\nto 0.15 A at {tdone:.0f} min", xy=(tdone - 1, 0.2),
                 xytext=(52, 1.9), fontsize=7, color=ORANGE,
                 arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    hs = [l for a in (axp, axi, axs) for l in a.get_lines()[:1]]
    axp.legend(hs, [h_.get_label() for h_ in hs], loc="lower right", fontsize=7, bbox_to_anchor=(1.0, 0.1))
    axp.text(0.5, 4.33, "3 Ah NMC cell, 50 mΩ, from 10 % SOC", fontsize=7, va="bottom", color=INK)
    print(f"  32.4: t_cv={tcv:.1f} min, soc_cv={scv:.3f}, t_done={tdone:.1f} min, final SOC={S[-1]:.3f}")
    save(fig, "32", "fig-32-4-obc-cccv")


# ----------------------------------------------------------------------------
# Figure 32.5 — PV and wind converter power stages
# ----------------------------------------------------------------------------
def _sw(d, ax, x, ytop, ybot, label, s=0.8, diode=True, lab_left=True):
    """Vertical IGBT (+ antiparallel diode) between ytop and ybot at x."""
    yc = (ytop + ybot) / 2
    q = elm.IgbtN().theta(0).anchor("center").at((x, yc)).scale(s)
    d += q
    hh = 0.7 * s
    d += elm.Line().at((x, yc + hh)).to((x, ytop))
    d += elm.Line().at((x, yc - hh)).to((x, ybot))
    if diode:
        xd, dy = x + 0.6, 0.75
        d += elm.Line().at((x, yc + dy)).to((xd, yc + dy))
        d += elm.Line().at((x, yc - dy)).to((xd, yc - dy))
        d += elm.Diode().at((xd, yc - dy)).to((xd, yc + dy)).scale(0.85)
    ax.text(x - 0.7 if lab_left else x + 1.0, yc + 0.25, label, fontsize=6.8,
            ha="right" if lab_left else "left", va="bottom")


def fig_32_5():
    fig = plt.figure(figsize=(6.8, 6.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 0.8], hspace=0.0)
    ax = fig.add_subplot(gs[0])
    d = _sd(ax, fontsize=7, lw=1.0)
    yt, yb = 5.0, 0.0
    # PV string
    d += elm.Solar().at((0.6, yb)).to((0.6, yt)).label("PV string\n12 modules\n330–372 V", loc="top", ofst=0.2)
    d += elm.Line().at((0.6, yt)).to((2.0, yt))
    d += elm.Line().at((0.6, yb)).to((2.0, yb))
    d += elm.Capacitor().at((2.0, yt)).to((2.0, yb)).label(r"$C_{in}$", loc="bottom", ofst=0.1)
    d += elm.Inductor2(loops=3).at((2.0, yt)).to((4.4, yt)).label("0.53 mH", loc="bottom", ofst=0.1)
    d += elm.Line().at((2.0, yb)).to((13.0, yb))
    d += elm.Dot().at((4.4, yt))
    # boost switch (SiC MOSFET with body diode, drawn with the switch symbol) and diode
    _sw(d, ax, 4.4, yt, yb, "", s=0.75, diode=False)
    ax.text(4.7, 2.3, "SiC\nboost\nswitch", fontsize=6.3, ha="left", va="center")
    d += elm.Diode().at((4.4, yt)).to((6.4, yt)).label("boost diode", loc="bottom", ofst=0.1)
    # bypass diode above
    d += elm.Line().at((2.6, yt)).to((2.6, yt + 1.2))
    d += elm.Diode().at((2.6, yt + 1.2)).to((6.4, yt + 1.2)).label("bypass diode", ofst=0.08)
    d += elm.Line().at((6.4, yt + 1.2)).to((6.4, yt))
    d += elm.Dot().at((2.6, yt))
    d += elm.Dot().at((6.4, yt))
    d += elm.Dot().at((4.4, yb))
    d += elm.Line().at((6.4, yt)).to((13.0, yt))
    d += elm.Capacitor().at((7.3, yt)).to((7.3, yb)).label("DC link\n400 V\n2 mF", loc="top", ofst=0.1)
    for xx in (7.3,):
        d += elm.Dot().at((xx, yt))
        d += elm.Dot().at((xx, yb))
    # H-bridge
    xl1, xl2 = 9.4, 12.4
    for x, (n1, n2) in ((xl1, ("S1", "S2")), (xl2, ("S3", "S4"))):
        _sw(d, ax, x, yt, 2.5, n1, s=0.75)
        _sw(d, ax, x, 2.5, yb, n2, s=0.75)
        d += elm.Dot().at((x, yt))
        d += elm.Dot().at((x, yb))
        d += elm.Dot().at((x, 2.5))
    # outputs to the right
    d += elm.Line().at((xl1, 2.5)).to((xl1 + 0.4, 2.5))
    d += elm.Line().at((xl1 + 0.4, 2.5)).to((xl1 + 0.4, -0.9))
    d += elm.Line().at((xl1 + 0.4, -0.9)).to((14.4, -0.9))
    d += elm.Line().at((xl2, 2.5)).to((14.4, 2.5))
    # HERIC: two back-to-back IGBTs across output (horizontal pair drawn vertically)
    xh = 14.4
    d += elm.Line().at((xh, 2.5)).to((xh, 2.0))
    d += elm.Line().at((xh, -0.9)).to((xh, -0.4))
    box(ax, xh - 0.55, -0.4, 1.1, 2.4, "", fc="#FBE3D6")
    ax.text(xh, 0.8, "S5\n↕\nS6", fontsize=6.8, ha="center", va="center")
    ax.text(xh, -1.05, "HERIC bidirectional\nswitch S5–S6", fontsize=6.3, ha="center", va="top")
    # LCL, relay, grid
    d += elm.Line().at((xh, 2.5)).to((15.2, 2.5))
    d += elm.Inductor2(loops=2).at((15.2, 2.5)).to((16.6, 2.5))
    d += elm.Capacitor().at((16.6, 2.5)).to((16.6, -0.9)).scale(0.8)
    d += elm.Inductor2(loops=2).at((16.6, 2.5)).to((18.0, 2.5))
    d += elm.Line().at((xh, -0.9)).to((19.6, -0.9))
    ax.text(16.6, 3.2, "LCL filter", fontsize=6.5, ha="center")
    d += elm.Switch().at((18.0, 2.5)).to((19.0, 2.5))
    ax.text(18.5, 2.0, "relay", fontsize=6.3, ha="center", va="top")
    d += elm.Line().at((19.0, 2.5)).to((19.6, 2.5))
    d += elm.SourceSin().at((19.6, -0.9)).to((19.6, 2.5)).label("grid\n230 V", loc="bottom", ofst=0.15)
    d += elm.Ground().at((19.6, -0.9))
    # array capacitance to earth and leakage path
    ax.plot([0.6, 0.6], [yb, -1.6], color=RED, lw=0.9, ls="--")
    ax.plot([0.25, 0.95], [-1.6, -1.6], color=RED, lw=1.2)
    ax.plot([0.25, 0.95], [-1.8, -1.8], color=RED, lw=1.2)
    ax.plot([0.6, 0.6], [-1.8, -2.5], color=RED, lw=0.9, ls="--")
    ax.plot([0.6, 19.6, 19.6], [-2.5, -2.5, -1.5], color=RED, lw=0.9, ls="--")
    ax.text(1.2, -1.7, "array capacitance to earth ≈ 1 µF", fontsize=6.5, color=RED, va="center")
    ax.text(10.0, -2.65, "leakage-current path through earth (blocked by HERIC freewheeling)",
            fontsize=6.5, color=RED, ha="center", va="top")
    ax.text(-0.4, 7.9, "6 kW transformerless PV string inverter", fontsize=8, color=BLUE, va="top")
    _finish(d, ax, xlim=(-1.6, 21.2), ylim=(-3.2, 8.0))

    # --- wind back-to-back ---------------------------------------------
    axw = fig.add_subplot(gs[1])
    axw.set_xlim(-1.6, 21.2)
    axw.set_ylim(-0.5, 7.0)
    axw.set_aspect("equal")
    axw.axis("off")
    yc = 3.6
    _motor(axw, 0.6, yc, r=0.9, txt="PMSG", fs=6.8)

    def conv(x, txt, l, r):
        axw.add_patch(Rectangle((x, yc - 1.0), 2.4, 2.0, fc=FC_POW, ec=INK, lw=1.0))
        axw.plot([x, x + 2.4], [yc - 1.0, yc + 1.0], color=INK, lw=0.7)
        axw.text(x + 0.55, yc + 0.5, l, fontsize=7.5, ha="center", va="center")
        axw.text(x + 1.85, yc - 0.5, r, fontsize=7.5, ha="center", va="center")
        axw.text(x + 1.2, yc - 1.15, txt, fontsize=6.3, ha="center", va="top")

    conv(2.2, "machine-side\n2-level converter", "~", "=")
    axw.plot([1.5, 2.2], [yc, yc], color=INK, lw=1.0)
    # DC link
    axw.plot([4.6, 10.4], [yc + 0.8, yc + 0.8], color=INK, lw=1.0)
    axw.plot([4.6, 10.4], [yc - 0.8, yc - 0.8], color=INK, lw=1.0)
    for xx in (5.2,):
        axw.plot([xx, xx], [yc + 0.8, yc + 0.12], color=INK, lw=1.0)
        axw.plot([xx, xx], [yc - 0.8, yc - 0.12], color=INK, lw=1.0)
        axw.plot([xx - 0.3, xx + 0.3], [yc + 0.12, yc + 0.12], color=INK, lw=1.4)
        axw.plot([xx - 0.3, xx + 0.3], [yc - 0.12, yc - 0.12], color=INK, lw=1.4)
    axw.text(5.2, yc + 1.0, "DC link 1100 V", fontsize=6.5, ha="center", va="bottom")
    # chopper: resistor in series with IGBT
    xc = 6.9
    axw.add_patch(Rectangle((xc - 0.18, yc + 0.0), 0.36, 0.7, fc="white", ec=INK, lw=0.9))
    axw.plot([xc, xc], [yc + 0.7, yc + 0.8], color=INK, lw=1.0)
    axw.plot([xc, xc], [yc, yc - 0.15], color=INK, lw=1.0)
    axw.plot([xc - 0.15, xc - 0.15], [yc - 0.25, yc - 0.65], color=INK, lw=1.4)
    axw.plot([xc - 0.32, xc - 0.32], [yc - 0.3, yc - 0.6], color=INK, lw=1.0)
    axw.plot([xc - 0.15, xc, xc], [yc - 0.3, yc - 0.15, yc - 0.15], color=INK, lw=1.0)
    axw.plot([xc - 0.15, xc, xc], [yc - 0.6, yc - 0.75, yc - 0.8], color=INK, lw=1.0)
    axw.text(xc + 0.3, yc + 0.35, "chopper resistor\n1.5 MJ per event", fontsize=6.3, ha="left", va="center",
             color=RED)
    axw.text(xc + 0.3, yc - 0.5, "chopper IGBT", fontsize=6.3, ha="left", va="center")
    conv(10.4, "grid-side\nconverter", "=", "~")
    axw.plot([12.8, 13.4], [yc, yc], color=INK, lw=1.0)
    box(axw, 13.4, yc - 0.6, 1.8, 1.2, "LCL\nfilter", fc=FC_POW, fontsize=6.5)
    axw.plot([15.2, 15.8], [yc, yc], color=INK, lw=1.0)
    axw.add_patch(Circle((16.4, yc), 0.6, fill=False, ec=INK, lw=1.0))
    axw.add_patch(Circle((17.15, yc), 0.6, fill=False, ec=INK, lw=1.0))
    axw.text(16.78, yc - 0.75, "0.69/33 kV", fontsize=6.3, ha="center", va="top")
    axw.plot([17.75, 18.8], [yc, yc], color=INK, lw=1.0)
    axw.plot([18.8, 18.8], [yc - 0.8, yc + 0.8], color=INK, lw=2.5)
    axw.text(19.0, yc, "33 kV\ngrid", fontsize=6.5, ha="left", va="center")
    # power-flow arrows
    _harrow(axw, 1.2, 18.6, yc + 2.1, color=BLUE, lw=1.4)
    axw.text(10.0, yc + 2.25, "normal power flow, 3 MW", fontsize=6.5, ha="center", va="bottom", color=BLUE)
    axw.plot([1.2, xc], [0.6, 0.6], color=RED, lw=1.4)
    _varrow(axw, xc, 0.6, yc - 0.95, color=RED, lw=1.4)
    axw.text(4.4, 0.45, "grid fault: generator power → chopper (≤ 500 ms)", fontsize=6.5, ha="left",
             va="top", color=RED)
    axw.text(-0.4, 6.9, "3 MW Type 4 wind turbine, back-to-back converter", fontsize=8, color=BLUE, va="top")
    save(fig, "32", "fig-32-5-pv-wind-converters")


# ----------------------------------------------------------------------------
# Figure 32.6 — grid current loop and its Bode plot
# ----------------------------------------------------------------------------
def _loop_gain(f, full=True, Kp=5.1, Ti=27.1e-3, Td=150e-6, L1=1.91e-3, L2=0.8e-3,
               Cf=15e-6, Rd=2.0, R=0.1):
    s = 2j * np.pi * f
    if full:
        Zc = Rd + 1 / (s * Cf)
        Z1 = s * L1 + R * L1 / (L1 + L2)
        Z2 = s * L2 + R * L2 / (L1 + L2)
        G = Zc / (Z1 * Z2 + (Z1 + Z2) * Zc)
    else:
        G = 1 / (s * (L1 + L2) + R)
    return Kp * (1 + 1 / (s * Ti)) * np.exp(-s * Td) * G


def fig_32_6():
    fig = plt.figure(figsize=(6.8, 7.6))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.35, 0.8, 0.7], hspace=0.10)
    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 10.4)
    ax.set_aspect("equal")
    ax.axis("off")
    fs = 6.6
    # power path along the top
    yp, hp = 8.0, 1.5
    box(ax, 0.0, yp, 2.6, hp, "min–max\nmodulator", fc=FC_CTL, fontsize=fs)
    box(ax, 2.95, yp, 3.3, hp, "delay\n1.5 $T_s$ = 150 µs", fc="#FBE3D6", fontsize=fs)
    box(ax, 6.6, yp, 2.1, hp, "inverter\n(700 V)", fc=FC_POW, fontsize=fs)
    box(ax, 9.05, yp, 6.45, hp, "LCL: $L_1$ 1.91 mH, $C_f$ 15 µF\n+ $R_d$ 2 Ω, $L_2$ 0.8 mH", fc=FC_POW, fontsize=fs)
    box(ax, 16.0, yp, 2.3, hp, "grid\n400 V", fc="#F4F4F4", fontsize=fs)
    for x0, x1 in ((2.6, 2.95), (6.25, 6.6), (8.7, 9.05), (15.5, 16.0)):
        _harrow(ax, x0 + 0.02, x1 - 0.02, yp + hp / 2, color=BLUE)
    # sensing
    box(ax, 16.0, 5.3, 3.6, 1.4, "isolated voltage\nsensing $v_{abc}$", fc=FC_CTL, fontsize=fs)
    box(ax, 11.6, 5.3, 3.6, 1.4, "current sensing\n$i_{abc}$ (grid side)", fc=FC_CTL, fontsize=fs)
    _varrow(ax, 17.15, yp - 0.02, 6.72, color=GREY)
    _varrow(ax, 13.4, yp - 0.02, 6.72, color=GREY)
    # PLL
    box(ax, 15.2, 1.6, 4.6, 2.8, "SRF-PLL\nClarke → Park → PI\n$k_p$ 0.547, $k_i$ 48.6\n→ ∫ → θ",
        fc=FC_CTL, fontsize=fs)
    _varrow(ax, 17.6, 5.28, 4.42, color=GREY)
    # abc->dq of current
    box(ax, 11.6, 2.6, 2.8, 1.6, "abc → dq", fc=FC_CTL, fontsize=fs)
    _varrow(ax, 13.0, 5.28, 4.22, color=GREY)
    _harrow(ax, 15.18, 14.42, 3.4, color=PINK)
    ax.text(14.8, 3.55, "θ", fontsize=7, color=PINK, ha="center", va="bottom")
    # PI controllers
    box(ax, 6.4, 3.6, 4.4, 1.5, "PI on $i_d$, $i_q$\n$K_p$ 5.1 Ω, $T_i$ 27 ms", fc=FC_CTL, fontsize=fs)
    box(ax, 6.4, 1.2, 4.4, 1.8, "decoupling $\\pm\\omega L i$\n+ grid-voltage\nfeed-forward", fc=FC_CTL,
        fontsize=fs)
    _harrow(ax, 11.58, 10.82, 3.4, color=GREY)
    ax.text(11.12, 3.25, "$i_d$, $i_q$", fontsize=6.0, ha="center", va="top", color=GREY)
    ax.text(8.6, 5.4, "$i_d^*$, $i_q^*$ (P, Q)", fontsize=6.3, ha="center", va="bottom", color=INK)
    _varrow(ax, 8.6, 5.38, 5.12, color=INK)
    box(ax, 2.6, 2.5, 2.8, 1.7, "dq → abc", fc=FC_CTL, fontsize=fs)
    _harrow(ax, 6.38, 5.42, 4.0, color=GREEN)
    _harrow(ax, 6.38, 5.42, 2.4, color=GREEN)
    ax.plot([5.4, 5.4], [2.4, 4.0], color=GREEN, lw=1.0)
    ax.annotate("", xy=(1.3, yp - 0.02), xytext=(1.3, 3.35), arrowprops=dict(arrowstyle="-|>", color=GREEN))
    ax.plot([1.3, 2.58], [3.35, 3.35], color=GREEN, lw=1.0)
    ax.plot([17.6, 17.6, 4.0, 4.0], [1.58, 0.5, 0.5, 2.48], color=PINK, lw=0.9)
    ax.text(10.5, 0.35, "θ to dq → abc", fontsize=6.3, color=PINK, ha="center", va="top")
    ax.text(0.0, 10.35, "grid-connected converter: current loop and synchronisation", fontsize=7.5,
            color=BLUE, va="top")

    # --- Bode ------------------------------------------------------------
    f = np.logspace(1, 4, 6000)
    Lf = _loop_gain(f, full=True)
    Ll = _loop_gain(f, full=False)
    db = lambda H: 20 * np.log10(np.abs(H))
    ph = lambda H: np.degrees(np.unwrap(np.angle(H)))
    axm = fig.add_subplot(gs[1])
    axp = fig.add_subplot(gs[2], sharex=axm)
    axm.semilogx(f, db(Ll), color=GREY, lw=1.4, ls="--", label="design model: $L_1+L_2$ only")
    axm.semilogx(f, db(Lf), color=BLUE, lw=1.6, label="full damped LCL")
    axp.semilogx(f, ph(Ll), color=GREY, lw=1.4, ls="--")
    axp.semilogx(f, ph(Lf), color=BLUE, lw=1.6)
    axm.axhline(0, color=INK, lw=0.7)
    axm.set_ylim(-30, 40)
    axm.set_ylabel("loop gain (dB)")
    axm.grid(True, which="major", color=GRID, lw=0.5)
    axp.grid(True, which="major", color=GRID, lw=0.5)
    axm.legend(loc="lower left", fontsize=7)
    plt.setp(axm.get_xticklabels(), visible=False)
    # design crossover and margin
    k6 = np.argmin(np.abs(db(Ll)))
    fc, phc = f[k6], ph(Ll)[k6]
    axm.axvline(fc, color=GREY, lw=0.6, ls=":")
    axp.axvline(fc, color=GREY, lw=0.6, ls=":")
    axm.text(fc * 0.92, 25, f"0 dB at {fc:.0f} Hz\n(−20 dB/dec)", fontsize=6.8, ha="right")
    axp.axhline(-180, color=RED, lw=0.8, ls="--")
    axp.annotate("", xy=(fc, phc), xytext=(fc, -180),
                 arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8))
    axp.text(fc * 0.9, -150, f"PM {180 + phc:.1f}°\n(phase {phc:.1f}°)", fontsize=6.8, ha="right", va="center")
    fres = 1731.0
    axm.axvline(fres, color=ORANGE, lw=0.6, ls=":")
    axp.axvline(fres, color=ORANGE, lw=0.6, ls=":")
    kpk = np.argmax(db(Lf) * ((f > 1200) & (f < 2500)) - 1e3 * ~((f > 1200) & (f < 2500)))
    axm.annotate(f"LCL resonance 1.73 kHz:\ndamped bump {db(Lf)[kpk]:+.1f} dB", xy=(f[kpk], db(Lf)[kpk]),
                 xytext=(2.6e3, 20), fontsize=6.8, color=ORANGE,
                 arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    kf = int(np.where(db(Lf) < 0)[0][0])
    i180 = np.where(np.diff(np.sign(ph(Lf) + 180)))[0][0]
    axp.text(12, -345, f"full LCL: crossover {f[kf]:.0f} Hz, PM {180 + ph(Lf)[kf]:.0f}°,\n"
             f"gain margin {-db(Lf)[i180]:.1f} dB at {f[i180]:.0f} Hz", fontsize=6.6, ha="left",
             va="bottom", color=BLUE)
    axp.set_ylim(-360, -60)
    axp.set_yticks([-90, -180, -270, -360])
    axp.set_ylabel("phase (°)")
    axp.set_xlabel("frequency (Hz)")
    axp.set_xlim(10, 1e4)
    print(f"  32.6: design fc={fc:.0f} Hz phase={phc:.1f}; full: fc={f[kf]:.0f} PM={180+ph(Lf)[kf]:.1f} "
          f"bump={db(Lf)[kpk]:.2f} dB GM={-db(Lf)[i180]:.2f} dB at {f[i180]:.0f} Hz")
    save(fig, "32", "fig-32-6-grid-current-loop")


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4", "5", "6"]
    for w in which:
        globals()[f"fig_32_{w}"]()
