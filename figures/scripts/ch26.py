"""Figures for Chapter 26 — Embedded Interfaces.

Run from the repository root:  python figures/scripts/ch26.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Polygon  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402
import schemdraw.logic as logic  # noqa: E402

from figstyle import COLORS, INK, GRID, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4], COLORS[5]
RED = "#C62828"
GREY = "#777777"


def hline_arrow(ax, x0, x1, y, text="", color=INK, fs=7.5, va="bottom", dy=0.0, style="<|-|>"):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle=style, color=color, lw=0.9, mutation_scale=8,
                                shrinkA=0, shrinkB=0))
    if text:
        ax.text((x0 + x1) / 2, y + dy, text, ha="center", va=va, fontsize=fs, color=color)


def digital(ax, t, levels, y0, h, color=INK, lw=1.4, slope=0.0):
    """Draw a digital waveform from edge times t (len n+1) and levels (len n) at baseline y0."""
    xs, ys = [], []
    for k, lev in enumerate(levels):
        a, b = t[k], t[k + 1]
        if k > 0 and levels[k - 1] != lev:
            xs.append(a + slope / 2)
        else:
            xs.append(a)
        ys.append(y0 + lev * h)
        xs.append(b - (slope / 2 if k + 1 < len(levels) and levels[k + 1] != lev else 0))
        ys.append(y0 + lev * h)
    ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="miter")


# ----------------------------------------------------------------------------
# Figure 26.1 — GPIO pin structure
# ----------------------------------------------------------------------------
def fig_gpio_pin():
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.axis("off")
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=2.0, lw=1.1)
    VDD_Y, VSS_Y = 4.0, -4.0
    PAD_X = 11.8

    # --- rails ------------------------------------------------------------
    xo = 0.0
    d += elm.Line().at((xo, VDD_Y)).to((PAD_X - 0.6, VDD_Y))
    d += elm.Line().at((xo, VSS_Y)).to((PAD_X - 0.6, VSS_Y))
    d += elm.Label().at((PAD_X - 0.5, VDD_Y)).label("V$_{DD}$ = 3.3 V", loc="right", halign="left")
    d += elm.Label().at((PAD_X - 0.5, VSS_Y)).label("V$_{SS}$", loc="right", halign="left")

    # --- output stage ---------------------------------------------------
    pf = elm.PFet().theta(0).reverse().anchor("source").at((xo, VDD_Y))
    d += pf
    d += elm.Line().at(pf.drain).to((xo, 0))
    nf = elm.NFet().theta(0).reverse().anchor("source").at((xo, VSS_Y))
    d += elm.Line().at((xo, 0)).to((xo, VSS_Y + 1.5))
    nf = elm.NFet().theta(0).reverse().anchor("drain").at((xo, VSS_Y + 1.5))
    d += nf
    d += elm.Line().at(pf.gate).left(0.6)
    d += elm.Label().at((pf.gate[0] - 0.65, pf.gate[1])).label(
        "output data\n(PMOS gate forced off\nin open-drain mode)", loc="left", halign="right", fontsize=7.5)
    d += elm.Line().at(nf.gate).left(0.6)
    d += elm.Label().at((nf.gate[0] - 0.65, nf.gate[1])).label("output data", loc="left", halign="right",
                                                              fontsize=7.5)
    d += elm.Label().at((xo + 0.25, pf.center[1] + 0.1)).label("PMOS", loc="right", halign="left", fontsize=7)
    d += elm.Label().at((xo + 0.25, nf.center[1] + 0.1)).label("NMOS", loc="right", halign="left", fontsize=7)
    d += elm.Dot().at((xo, 0))
    # --- internal node to the pad ---------------------------------------
    d += elm.Line().at((xo, 0)).to((PAD_X, 0))

    # pull-up and pull-down (switch + 40 k)
    xp = 2.2
    d += elm.Dot().at((xp, 0))
    d += elm.Switch().at((xp, 0)).up(1.6).label("PU en", loc="top", fontsize=7)
    d += elm.Resistor().up(2.4).label("40 kΩ", loc="bottom", fontsize=7.5)
    d += elm.Switch().at((xp, 0)).down(1.6).label("PD en", loc="top", fontsize=7)
    d += elm.Resistor().down(2.4).label("40 kΩ", loc="bottom", fontsize=7.5)

    # input path: Schmitt trigger to the input data register
    xi = 4.0
    d += elm.Dot().at((xi, 0))
    d += elm.Line().at((xi, 0)).up(1.3)
    d += elm.Line().right(0.35)
    d += elm.Line().at((xi + 1.45, 1.3)).right(0.35)
    d += elm.Label().at((xi + 1.85, 1.3)).label("to input data\nregister", loc="right", halign="left",
                                               fontsize=7.5)
    d += elm.Label().at((xi + 1.3, 2.25)).label("Schmitt trigger", fontsize=7, halign="center")

    # clamp diodes
    xc = 10.7
    d += elm.Dot().at((xc, 0))
    d += elm.Diode().at((xc, 0)).up(VDD_Y).label("clamp", loc="bottom", fontsize=7)
    d += elm.Diode().at((xc, VSS_Y)).up(-VSS_Y).label("clamp", loc="bottom", fontsize=7)

    # --- right top: LED -------------------------------------------------
    X0 = 17.6
    yl = 4.2
    d += elm.Label().at((X0 - 0.15, yl)).label("GPIO", loc="left", halign="right", fontsize=8)
    d += elm.Dot(open=True).at((X0, yl))
    d += elm.Resistor().at((X0, yl)).right(2.4).label("200 Ω", fontsize=7.5)
    d += elm.LED(fill="#E53935").down(1.8).label("red LED\nV$_F$ = 2.0 V", loc="bottom", fontsize=7.5)
    d += elm.Ground()
    d += elm.Label().at((X0 + 1.2, yl - 1.25)).label("5 mA", fontsize=7.5, color=RED)

    # --- right bottom: MOSFET and relay ----------------------------------
    yg = -2.9
    d += elm.Label().at((X0 - 0.15, yg)).label("GPIO", loc="left", halign="right", fontsize=8)
    d += elm.Dot(open=True).at((X0, yg))
    r_g = elm.Resistor().at((X0, yg)).right(2.0).label("100 Ω", fontsize=7.5)
    d += r_g
    q = elm.NFet().theta(0).reverse().anchor("gate").at(r_g.end)
    d += q
    xd = r_g.end[0] - 0.5
    d += elm.Dot().at((xd, yg))
    d += elm.Resistor().at((xd, yg)).down(1.4).label("100 kΩ", loc="bottom", fontsize=7.5)
    d += elm.Ground()
    d += elm.Line().at(q.source).to((q.source[0], yg - 1.4))
    d += elm.Ground().at((q.source[0], yg - 1.4))
    d += elm.Label().at((q.center[0] + 0.35, q.center[1] - 0.1)).label("logic-level\nN-MOSFET", loc="right",
                                                                      halign="left", fontsize=7)
    xq = q.drain[0]
    d += elm.Line().at(q.drain).up(0.3)
    top = (xq, q.drain[1] + 0.3)
    coil = elm.Inductor2(loops=3).at(top).up(1.6).label("relay\ncoil", loc="top", fontsize=7)
    d += coil
    d += elm.Line().up(0.3)
    d += elm.Vdd().label("+12 V", fontsize=7.5)
    d += elm.Line().at(top).right(1.1)
    d += elm.Diode().up(1.6).reverse().label("flyback\ndiode", loc="bottom", fontsize=7)
    d += elm.Line().left(1.1)
    d += elm.Dot().at(top)
    d += elm.Dot().at((xq, top[1] + 1.6))

    d.draw(show=False)
    # Schmitt-trigger buffer drawn directly (drawing units = axis data units)
    ax.add_patch(Polygon([(xi + 0.35, 0.72), (xi + 0.35, 1.88), (xi + 1.45, 1.3)], closed=True, fc="white",
                         ec=INK, lw=1.1, zorder=3))
    gx, gy = xi + 0.55, 1.3
    ax.plot([gx, gx + 0.32, gx + 0.32, gx + 0.5], [gy - 0.18, gy - 0.18, gy + 0.18, gy + 0.18], color=INK,
            lw=0.9, zorder=4)
    ax.plot([gx + 0.18, gx + 0.18, gx + 0.5], [gy - 0.18, gy + 0.18, gy + 0.18], color=INK, lw=0.9, zorder=4)
    # pad and annotations
    ax.add_patch(Rectangle((PAD_X, -0.4), 0.8, 0.8, fc="#DDDDDD", ec=INK, lw=1.1, zorder=3))
    ax.text(PAD_X + 0.4, -0.65, "pad", ha="center", va="top", fontsize=7.5)
    ax.plot([PAD_X + 0.8, PAD_X + 2.2], [0, 0], color=INK, lw=1.1, ls=(0, (3, 2)))
    ax.text(PAD_X + 1.5, 0.15, "to external\ncircuit", ha="center", va="bottom", fontsize=7, color=GREY)
    ax.text(5.6, -5.15, "Schmitt input: V$_{T+}$ ≤ 2.0 V, V$_{T-}$ ≥ 1.2 V, hysteresis ≥ 0.2 V;  "
            "input leakage ≤ 1 µA;  pin capacitance 5 pF\n"
            "Output: V$_{OH}$ ≥ 2.9 V and V$_{OL}$ ≤ 0.4 V at 8 mA", ha="center", va="top", fontsize=7.5,
            linespacing=1.5)
    ax.text(X0 + 1.2, yl + 1.25, "(3.3 − 0.3 − 2.0) V / 200 Ω = 5 mA", ha="center", fontsize=7)
    ax.add_patch(Rectangle((-5.4, VSS_Y - 0.8), PAD_X + 5.4 + 0.25, VDD_Y - VSS_Y + 1.4, fill=False,
                           ec=GREY, ls=":", lw=0.9))
    ax.text(0.6, VSS_Y - 0.12, "inside the microcontroller", fontsize=7, color=GREY, va="top")
    ax.set_aspect("equal")
    ax.autoscale()
    save(fig, "26", "fig-26-1-gpio-pin-structure")

# ----------------------------------------------------------------------------
# Figure 26.2 — UART frame and sampling
# ----------------------------------------------------------------------------
def fig_uart_frame():
    Tb = 1e6 / 115200            # µs
    bits = [0] + [(0x55 >> k) & 1 for k in range(8)] + [1]   # start, LSB first, stop
    names = ["start"] + [f"D{k}" for k in range(8)] + ["stop"]
    t_edges = [-0.9 * Tb] + [k * Tb for k in range(11)] + [11.2 * Tb]
    levels = [1] + bits + [1]

    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    H = 1.0
    Y_TX, Y_CLK, Y_RX = 6.0, 3.6, 0.6

    # --- top: TX line with nominal sampling ----------------------------
    digital(ax, t_edges, levels, Y_TX, H, slope=0.35)
    for k in range(10):
        ax.text((k + 0.5) * Tb, Y_TX + H + 0.15, names[k], ha="center", va="bottom", fontsize=7)
        ax.text((k + 0.5) * Tb, Y_TX + 0.5 * H, str(bits[k]), ha="center", va="center", fontsize=7.5,
                color=GREY)
    centres = [(k + 0.5) * Tb for k in range(10)]
    ax.plot(centres, [Y_TX + bits[k] * H for k in range(10)], "o", color=BLUE, ms=4.5, zorder=5)
    ax.text(-0.85 * Tb, Y_TX + H + 0.15, "idle", fontsize=7, va="bottom")
    hline_arrow(ax, 1 * Tb, 2 * Tb, Y_TX - 0.35, "8.68 µs", va="top", dy=-0.08)
    hline_arrow(ax, 0, 10 * Tb, Y_TX + H + 0.85, "frame 10 bits = 86.8 µs", va="bottom", dy=0.05)
    for k in range(11):
        ax.plot([k * Tb] * 2, [Y_CLK - 0.2, Y_TX + H + 0.1], color=GRID, lw=0.6, zorder=0)

    # --- middle: 16x sample clock ---------------------------------------
    tick = Tb / 16
    detect = tick  # start edge recognised on the first tick after it
    n_ticks = 10 * 16
    for j in range(n_ticks):
        tt = j * tick
        bitpos = j % 16
        hi = bitpos in (7, 8, 9)
        ax.plot([tt, tt], [Y_CLK, Y_CLK + (0.75 if hi else 0.35)], color=ORANGE if hi else INK,
                lw=1.0 if hi else 0.5)
    ax.plot([0, 10 * Tb], [Y_CLK, Y_CLK], color=INK, lw=0.6)
    ax.annotate("start edge detected", xy=(0.02, Y_CLK + 0.4), xytext=(-0.9 * Tb, Y_CLK + 1.25), fontsize=7,
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=INK, mutation_scale=7))
    ax.text(3 * Tb, Y_CLK + 1.0, "16 ticks per bit (0.54 µs each); majority vote of ticks 7, 8, 9 (orange)",
            fontsize=7, ha="left", va="center", color=ORANGE)

    # --- bottom: receiver 4.6 % slow ------------------------------------
    digital(ax, t_edges, levels, Y_RX, H, slope=0.35)
    Tr = Tb * 1.046
    samp = [detect + (k + 0.5) * Tr for k in range(10)]
    for k, ts in enumerate(samp):
        lev = bits[min(int(ts // Tb), 9)] if ts < 10 * Tb else 1
        ax.plot([ts, ts], [Y_RX - 0.15, Y_RX + H + 0.15], color=RED, lw=0.7, ls=":")
        ax.plot(ts, Y_RX + lev * H, "o", color=RED, ms=4.5, zorder=5)
    for k in range(10):
        ax.plot([(k + 0.5) * Tb] * 2, [Y_RX + H + 0.05, Y_RX + H + 0.3], color=BLUE, lw=1.0)
    ax.annotate("stop-bit sample lands at the\nend of the stop bit:\nlimit of tolerance",
                xy=(samp[9], Y_RX + H), xytext=(10.25 * Tb, Y_RX + H + 1.2), fontsize=7, color=RED,
                ha="left", arrowprops=dict(arrowstyle="-|>", lw=0.7, color=RED, mutation_scale=7))
    ax.text(0.0, Y_RX + H + 0.55, "receiver clock 4.6 % slow: samples (red) drift right of the bit centres (blue ticks)",
            fontsize=7, ha="left", va="bottom", color=RED)

    ax.set_yticks([Y_TX + 0.5, Y_CLK + 0.3, Y_RX + 0.5])
    ax.set_yticklabels(["TX line\n(0x55, 8N1)", "receiver\n16× clock", "received with\n4.6 % slow clock"],
                       fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.9 * Tb, 13.2 * Tb)
    ax.set_ylim(-0.1, 8.6)
    ax.set_xticks(np.arange(0, 11) * Tb)
    ax.set_xticklabels([f"{k * Tb:.1f}" if k % 2 == 0 else "" for k in range(11)])
    ax.set_xlabel("time from start edge (µs)")
    fig.tight_layout()
    save(fig, "26", "fig-26-2-uart-frame-sampling")


# ----------------------------------------------------------------------------
# Figure 26.3 — SPI mode 0 and the isolator round trip
# ----------------------------------------------------------------------------
def fig_spi_timing():
    fig = plt.figure(figsize=(6.8, 4.9))
    ax = fig.add_axes([0.13, 0.45, 0.85, 0.53])
    ax2 = fig.add_axes([0.13, 0.07, 0.85, 0.22])
    H = 0.8
    Y = {"CS": 6.0, "SCK": 4.5, "MOSI": 3.0, "MISO": 1.5}
    tcss, T = 10.0, 100.0
    rise = [tcss + k * T for k in range(8)]
    fall = [r + T / 2 for r in rise]
    s = 4.0
    # CS
    digital(ax, [-60, 0, fall[-1] + 20, fall[-1] + 80], [1, 0, 1], Y["CS"], H, slope=s)
    # SCK
    te = [-60] + sorted(rise + fall) + [fall[-1] + 80]
    lv = [0] + [1 if k % 2 == 0 else 0 for k in range(16)]
    digital(ax, te, lv, Y["SCK"], H, slope=s)
    # MOSI 0x9F MSB first, valid from CS fall, changes on falling edges
    mosi = [(0x9F >> (7 - k)) & 1 for k in range(8)]
    edges = [0] + fall[:7] + [fall[7]]

    def bus(y, vals, color, labels=True):
        for k in range(8):
            a, b = edges[k], edges[k + 1]
            pts = [(a, y + H / 2), (a + s, y + H), (b - s, y + H), (b, y + H / 2), (b - s, y), (a + s, y)]
            ax.add_patch(Polygon(pts, closed=True, fc=color + "22", ec=color, lw=1.1))
            if labels:
                ax.text((a + b) / 2, y + H / 2, str(vals[k]), ha="center", va="center", fontsize=7.5)
        ax.plot([-60, edges[0]], [y + H / 2] * 2, color=GREY, lw=1.0)
        ax.plot([edges[-1], fall[-1] + 80], [y + H / 2] * 2, color=GREY, lw=1.0)

    bus(Y["MOSI"], mosi, BLUE)
    bus(Y["MISO"], ["x"] * 8, ORANGE)
    ax.text(fall[-1] + 30, Y["MOSI"] + H + 0.15, "= 0x9F (read ID), MSB first", fontsize=7, ha="right",
            va="bottom", color=BLUE)
    ax.text(fall[-1] + 30, Y["MISO"] + H + 0.15, "don't care during the command byte", fontsize=7, ha="right",
            va="bottom", color=ORANGE)
    for r in rise:
        ax.annotate("", xy=(r, Y["MISO"] - 0.05), xytext=(r, Y["MISO"] - 0.55),
                    arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9, mutation_scale=7))
        ax.plot([r, r], [Y["MISO"] - 0.05, Y["SCK"] + H], color=GREEN, lw=0.6, ls=":", zorder=0)
    ax.text(rise[0] - 8, Y["MISO"] - 0.75, "sample on rising edges", fontsize=7, color=GREEN, ha="left",
            va="top")
    hline_arrow(ax, 0, tcss, Y["CS"] - 0.35, "", style="<|-|>")
    ax.text(tcss + 4, Y["CS"] - 0.35, "t$_{CSS}$ = 10 ns", fontsize=7, va="center")
    hline_arrow(ax, rise[3], rise[4], Y["SCK"] + H + 0.25, "T = 100 ns (10 MHz)", dy=0.05)
    ax.set_yticks([v + H / 2 for v in Y.values()])
    ax.set_yticklabels(["CS", "SCK (mode 0)", "MOSI", "MISO"])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-60, fall[-1] + 80)
    ax.set_ylim(0.3, 7.3)
    ax.set_xlabel("time (ns)")

    # inset: half-period budget
    parts = [("isolator\n16", 16, SKY), ("0.7", 0.7, GREY), ("target t$_{CO}$\n8", 8, ORANGE),
             ("isolator\n16", 16, SKY), ("0.7", 0.7, GREY), ("setup\n5", 5, GREEN)]
    x = 0
    for lab, w, c in parts:
        ax2.add_patch(Rectangle((x, 0.3), w, 0.8, fc=c + "55", ec=INK, lw=0.8))
        if w > 2:
            ax2.text(x + w / 2, 0.7, lab, ha="center", va="center", fontsize=7)
        x += w
    ax2.annotate("board 0.7 ns", xy=(16.35, 1.1), xytext=(13.5, 1.75), fontsize=7, ha="center",
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    ax2.annotate("board 0.7 ns", xy=(40.75, 1.1), xytext=(43.0, 1.75), fontsize=7, ha="center",
                 arrowprops=dict(arrowstyle="-", lw=0.6))
    ax2.add_patch(Rectangle((46.4, 0.3), 3.6, 0.8, fc="white", ec=GREEN, lw=1.0, hatch="////"))
    ax2.axvline(50, color=RED, lw=1.2)
    ax2.text(50.4, 1.45, "next rising edge:\nT/2 = 50 ns at 10 MHz", fontsize=7, color=RED, va="center",
             ha="left")
    ax2.text(50.6, 0.15, "margin 3.6 ns", fontsize=7, color=GREEN, ha="left", va="center")
    hline_arrow(ax2, 0, 46.4, 0.05, "")
    ax2.text(23.2, -0.1, "total 46.4 ns", fontsize=7.5, ha="center", va="top")
    ax2.axvline(0, color=INK, lw=1.0)
    ax2.text(-0.6, 1.45, "controller drives\nfalling SCK edge", fontsize=7, ha="right", va="center")
    ax2.set_xlim(-12, 64)
    ax2.set_ylim(-0.9, 2.2)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    ax2.set_xticks(range(0, 51, 10))
    ax2.set_xlabel("time after falling SCK edge (ns)", fontsize=8)
    ax2.set_title("Half-period budget through a digital isolator", fontsize=8.5, loc="left")
    save(fig, "26", "fig-26-3-spi-mode-timing")


# ----------------------------------------------------------------------------
# Figure 26.4 — I2C read transaction and RC rise time
# ----------------------------------------------------------------------------
def fig_i2c():
    fig = plt.figure(figsize=(6.8, 5.0))
    ax = fig.add_axes([0.09, 0.58, 0.89, 0.40])
    ax2 = fig.add_axes([0.10, 0.09, 0.86, 0.36])
    # sequence of symbols: ('S'|'Sr'|'P') or (bit, driver)
    C, Tg = "C", "T"
    seq = [("S",)]
    def byte(v, drv):
        return [((v >> (7 - k)) & 1, drv) for k in range(8)]
    groups = []
    def add(items, label):
        start = len(seq)
        seq.extend(items)
        groups.append((start, len(seq), label))
    add(byte(0xD0, C), "0x68 + W")
    add([(0, Tg)], "A")
    add(byte(0x3B, Tg if False else C), "reg 0x3B")
    add([(0, Tg)], "A")
    add([("Sr",)], "Sr")
    add(byte(0xD1, C), "0x68 + R")
    add([(0, Tg)], "A")
    add(byte(0xE2, Tg), "data (target)")
    add([(1, C)], "N")
    add([("P",)], "P")
    groups.insert(0, (0, 1, "S"))

    yscl, ysda, H = 2.2, 0.4, 0.9
    x = 0.0
    scl_x, scl_y = [x], [yscl + H]
    sda_segs = []   # (x0, x1, level, driver)
    sda_level = 1
    W = 1.0
    sl = 0.12
    centers = []
    for item in seq:
        if item[0] in ("S", "Sr", "P"):
            kind = item[0]
            if kind == "S":
                # SCL high, SDA falls
                sda_segs.append((x, x + 0.5 * W, 1, "C"))
                sda_segs.append((x + 0.5 * W, x + W, 0, "C"))
                scl_x += [x + W - sl, x + W]
                scl_y += [yscl + H, yscl]
            elif kind == "Sr":
                # SDA released high while SCL low, SCL rises, then SDA falls while SCL high
                sda_segs.append((x, x + 0.35 * W, 1, "C"))
                scl_x += [x + 0.3 * W, x + 0.3 * W + sl]
                scl_y += [yscl, yscl + H]
                sda_segs.append((x + 0.35 * W, x + 0.65 * W, 1, "C"))
                sda_segs.append((x + 0.65 * W, x + W, 0, "C"))
                scl_x += [x + W - sl, x + W]
                scl_y += [yscl + H, yscl]
            else:  # P
                sda_segs.append((x, x + 0.35 * W, 0, "C"))
                scl_x += [x + 0.3 * W, x + 0.3 * W + sl]
                scl_y += [yscl, yscl + H]
                sda_segs.append((x + 0.35 * W, x + 0.65 * W, 0, "C"))
                sda_segs.append((x + 0.65 * W, x + 1.3 * W, 1, "C"))
                scl_x += [x + 1.3 * W]
                scl_y += [yscl + H]
            centers.append(x + 0.5 * W)
            x += W
        else:
            bit, drv = item
            sda_segs.append((x, x + W, bit, drv))
            scl_x += [x + 0.3 * W, x + 0.3 * W + sl, x + 0.75 * W - sl, x + 0.75 * W]
            scl_y += [yscl, yscl + H, yscl + H, yscl]
            scl_x += [x + W]
            scl_y += [yscl]
            centers.append(x + 0.5 * W)
            x += W
    ax.plot(scl_x, scl_y, color=INK, lw=1.2)
    # SDA drawn segment by segment, coloured by driver
    prev = None
    for (a, b, lev, drv) in sda_segs:
        col = BLUE if drv == "C" else ORANGE
        if prev is not None and prev[0] != lev:
            ax.plot([a, a + 0.08], [ysda + prev[0] * H, ysda + lev * H], color=col, lw=1.4)
            a = a + 0.08
        ax.plot([a, b], [ysda + lev * H] * 2, color=col, lw=1.4)
        prev = (lev, drv)
    # group labels
    for k, (i0, i1, lab) in enumerate(groups):
        x0, x1 = i0 * W, i1 * W
        ax.plot([x0 + 0.05, x1 - 0.05], [yscl + H + 0.35] * 2, color=GREY, lw=0.8)
        col = ORANGE if lab in ("A", "data (target)") else (RED if lab == "N" else INK)
        ax.text((x0 + x1) / 2, yscl + H + 0.45, lab, ha="center", va="bottom", fontsize=7, color=col)
    ax.set_xlim(-0.3, x + 0.8)
    ax.set_ylim(0.0, 4.2)
    ax.set_yticks([yscl + H / 2, ysda + H / 2])
    ax.set_yticklabels(["SCL", "SDA"])
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([])
    for sp in ("left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.plot([], [], color=BLUE, lw=1.6, label="SDA driven by controller")
    ax.plot([], [], color=ORANGE, lw=1.6, label="SDA driven by target")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, -0.22), ncol=2, fontsize=7)
    ax.text(0, -0.05, "A = ACK (target pulls SDA low), N = NACK, S/Sr/P = START / repeated START / STOP",
            fontsize=7, transform=ax.transData, va="top")

    # --- bottom: RC rise, aligned at the 30 % crossing ------------------
    VDD, Cb = 3.3, 200e-12
    t = np.linspace(-0.4e-6, 2.2e-6, 2000)
    for Rp, c in [(1.5e3, GREEN), (4.7e3, BLUE), (10e3, ORANGE)]:
        tau = Rp * Cb
        t30 = tau * np.log(1 / 0.7)
        tt = t + t30
        v = np.where(tt > 0, VDD * (1 - np.exp(-tt / tau)), 0)
        tr = tau * np.log(0.7 / 0.3)
        ax2.plot(t * 1e6, v, color=c, lw=1.6, label=f"R$_p$ = {Rp / 1e3:g} kΩ:  t$_r$ = "
                 + (f"{tr * 1e9:.0f} ns" if tr < 1e-6 else f"{tr * 1e6:.2f} µs"))
        ax2.plot(tr * 1e6, 0.7 * VDD, "o", color=c, ms=4)
    ax2.axvspan(0, 0.3, color=GREEN, alpha=0.12, lw=0)
    ax2.text(0.15, 4.5, "Fast-mode\nlimit\n300 ns", ha="center", va="top", fontsize=7, color=GREEN)
    for lev, lab in [(0.3, "0.3 V$_{DD}$ = 0.99 V"), (0.7, "0.7 V$_{DD}$ = 2.31 V")]:
        ax2.axhline(lev * VDD, color=GREY, lw=0.8, ls="--")
        ax2.text(-0.38, lev * VDD + 0.05, lab, ha="left", va="bottom", fontsize=7, color=GREY)
    ax2.set_xlim(-0.4, 2.2)
    ax2.set_ylim(0, 4.6)
    ax2.set_yticks([0, 1, 2, 3])
    ax2.set_xlabel("time from the 30 % crossing (µs)")
    ax2.set_ylabel("SDA voltage (V)")
    ax2.legend(loc="upper right", fontsize=7, ncol=1, bbox_to_anchor=(1.0, 1.02))
    ax2.set_title("Rising edge on C$_b$ = 200 pF at 3.3 V", fontsize=8.5, loc="left")
    save(fig, "26", "fig-26-4-i2c-transaction-rise-time")


# ----------------------------------------------------------------------------
# Figure 26.5 — CAN levels and bit timing
# ----------------------------------------------------------------------------
def fig_can():
    fig = plt.figure(figsize=(6.8, 5.0))
    ax = fig.add_axes([0.11, 0.62, 0.86, 0.35])
    axd = fig.add_axes([0.11, 0.40, 0.86, 0.17], sharex=ax)
    ax2 = fig.add_axes([0.04, 0.03, 0.93, 0.25])
    Tb = 2.0
    bits = [1, 0, 0, 1]   # 1 = recessive
    t = np.linspace(-0.5, 8.5, 3000)
    tr_ = 0.12

    def level(tt, rec, dom):
        out = np.full_like(tt, rec)
        state = np.zeros_like(tt)   # 0 recessive, 1 dominant (smoothed)
        for k, b in enumerate(bits):
            a = k * Tb
            m = (tt >= a) & (tt < a + Tb)
            state[m] = 0 if b else 1
        # smooth edges with a short exponential filter
        sm = np.copy(state)
        dt = tt[1] - tt[0]
        alpha = dt / tr_
        for i in range(1, len(sm)):
            sm[i] = sm[i - 1] + alpha * (state[i] - sm[i - 1])
        return rec + (dom - rec) * sm

    h = level(t, 2.5, 3.5)
    l = level(t, 2.5, 1.5)
    ax.plot(t, h, color=BLUE, label="CAN_H")
    ax.plot(t, l, color=ORANGE, label="CAN_L")
    for k, b in enumerate(bits):
        ax.text(k * Tb + Tb / 2, 3.95, "recessive" if b else "dominant", ha="center", fontsize=7.5,
                color=GREY)
        ax.axvline(k * Tb, color=GRID, lw=0.7, zorder=0)
    ax.axvline(4 * Tb, color=GRID, lw=0.7, zorder=0)
    ax.text(2.0 + 0.1, 3.5 + 0.08, "3.5 V", fontsize=7, color=BLUE, va="bottom")
    ax.text(2.0 + 0.1, 1.5 - 0.08, "1.5 V", fontsize=7, color=ORANGE, va="top")
    ax.text(0.1, 2.58, "2.5 V (both)", fontsize=7, va="bottom")
    ax.set_ylim(1.0, 4.3)
    ax.set_ylabel("voltage (V)")
    ax.legend(loc="lower right", fontsize=7.5)
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.set_title("High-speed CAN bus levels (500 kbit/s, 2 µs per bit)", fontsize=8.5, loc="left")

    axd.plot(t, h - l, color=GREEN)
    for v, lab in [(0.5, "0.5 V: recessive below"), (0.9, "0.9 V: dominant above")]:
        axd.axhline(v, color=GREY, ls="--", lw=0.8)
    axd.text(8.45, 0.5 - 0.08, "0.5 V: recessive below", ha="right", va="top", fontsize=7, color=GREY)
    axd.text(8.45, 0.9 + 0.08, "0.9 V: dominant above", ha="right", va="bottom", fontsize=7, color=GREY)
    axd.set_ylim(-0.3, 2.5)
    axd.set_ylabel("V$_{diff}$ (V)")
    axd.set_xlabel("time (µs)")
    axd.set_xlim(-0.5, 8.5)

    # --- one bit, 16 tq -------------------------------------------------
    tq = 0.125
    segs = [("Sync", 1, GREY), ("Prop_Seg  8 tq", 8, BLUE), ("Phase_Seg1  5 tq", 5, GREEN),
            ("Phase_\nSeg2", 2, ORANGE)]
    x = 0
    for lab, n, c in segs:
        ax2.add_patch(Rectangle((x, 0.6), n * tq, 0.8, fc=c + "44", ec=INK, lw=1.0))
        ax2.text(x + n * tq / 2, 1.0, lab, ha="center", va="center", fontsize=7.5)
        x += n * tq
    for k in range(17):
        ax2.plot([k * tq] * 2, [0.6, 0.45], color=INK, lw=0.6)
    for k in range(0, 17, 2):
        ax2.text(k * tq, 0.35, f"{k}", ha="center", va="top", fontsize=6.5)
    ax2.text(-0.03, 0.35, "tq", ha="right", va="top", fontsize=6.5)
    sp = 14 * tq
    ax2.annotate("", xy=(sp, 1.4), xytext=(sp, 2.15),
                 arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4, mutation_scale=10))
    ax2.text(sp, 2.2, "sample point 14/16 = 87.5 %", ha="center", va="bottom", fontsize=7.5, color=RED)
    ax2.text(tq + 4 * tq, 1.55, "covers 2 × (40 m × 5 ns/m + 255 ns) = 910 ns", ha="center", va="bottom",
             fontsize=7, color=BLUE)
    hline_arrow(ax2, 0, 2.0, -0.35, "", style="<|-|>")
    ax2.text(1.0, -0.42, "1 bit = 2 µs = 16 tq of 125 ns", ha="center", va="top", fontsize=7.5)
    hline_arrow(ax2, sp, sp + 2 * tq, 2.75, "", color=ORANGE)
    ax2.text(sp + 2 * tq + 0.03, 2.75, "SJW = 2 tq", fontsize=7.5, color=ORANGE, va="center")
    ax2.set_xlim(-0.25, 2.45)
    ax2.set_ylim(-0.9, 3.1)
    ax2.axis("off")
    save(fig, "26", "fig-26-5-can-levels-and-bit-timing")


# ----------------------------------------------------------------------------
# Figure 26.6 — SAR ADC input model and settling
# ----------------------------------------------------------------------------
def fig_sar_input():
    fig = plt.figure(figsize=(6.8, 5.0))
    axc = fig.add_axes([0.0, 0.52, 1.0, 0.47])
    axc.axis("off")
    d = schemdraw.Drawing(canvas=axc, show=False)
    d.config(fontsize=8, unit=2.0, lw=1.1)
    src = elm.SourceV().up()
    d += src
    d += elm.Resistor().right(2.4).label("R$_S$ = 10 kΩ\n(divider)")
    n1 = d.here
    d += elm.Resistor().right(2.2).label("100 Ω")
    n2 = d.here
    d += elm.Dot()
    d += elm.Capacitor().at(n2).down().label("100 nF", loc="top")
    d += elm.Ground()
    d += elm.Line().at(n2).right(1.6)
    pin = d.here
    d += elm.Dot()
    d += elm.Capacitor().at(pin).down().label("C$_{pad}$\n5 pF", loc="bottom")
    d += elm.Ground()
    d += elm.Line().at(pin).right(0.8)
    d += elm.Switch().right(1.6).label("S/H switch", loc="top")
    d += elm.Resistor().right(2.0).label("R$_{SW}$ = 1 kΩ")
    nc = d.here
    d += elm.Dot()
    d += elm.Capacitor().at(nc).down().label("C$_S$\n5 pF", loc="bottom")
    d += elm.Ground()
    d += elm.Line().at(nc).right(1.0)
    d += elm.Line().right(0.2)
    d += elm.Ic(pins=[elm.IcPin(side="left", anchorname="inp")], size=(1.8, 1.4), label="SAR\nlogic").anchor("inp")
    d += elm.Ground().at(src.start)
    d.draw(show=False)
    axc.text(src.center[0] - 0.7, src.center[1], "V$_S$", ha="right", va="center", fontsize=8.5)
    axc.add_patch(Rectangle((n1[0] - 0.25, n2[1] - 3.2), pin[0] - n1[0] - 0.1, 3.75, fill=False,
                            ls="--", ec=GREEN, lw=1.0))
    axc.text((n1[0] + pin[0]) / 2 - 0.4, n2[1] + 0.75, "optional charge bucket", ha="center", fontsize=7.5,
             color=GREEN)
    axc.add_patch(Rectangle((pin[0] + 0.4, n2[1] - 3.2), nc[0] - pin[0] + 3.7, 3.95, fill=False,
                            ls=":", ec=GREY, lw=1.0))
    axc.text(pin[0] + 0.5, n2[1] - 3.1, "inside the MCU", ha="left", va="bottom", fontsize=7, color=GREY)
    axc.text(pin[0], n2[1] + 0.35, "pin", ha="center", fontsize=7.5)
    axc.autoscale()
    axc.set_aspect("equal")

    # --- plots ---------------------------------------------------------
    a1 = fig.add_axes([0.08, 0.08, 0.38, 0.38])
    a2 = fig.add_axes([0.58, 0.08, 0.39, 0.38])
    Cs = 5e-12
    half_lsb = 2.0 ** -13
    t = np.linspace(0, 2.6e-6, 4000)
    for Rs, c in [(10e3, BLUE), (50e3, ORANGE)]:
        tau = (Rs + 1e3) * Cs
        tacq = tau * np.log(2 ** 13)
        lab = f"R$_S$ = {Rs / 1e3:g} kΩ (τ = {tau * 1e9:.0f} ns)"
        a1.plot(t * 1e9, 1 - np.exp(-t / tau), color=c, label=lab)
        a2.semilogy(t * 1e6, np.exp(-t / tau), color=c)
        a2.plot(tacq * 1e6, half_lsb, "o", color=c, ms=5)
        a2.annotate(f"{tacq * 1e9:.0f} ns" if tacq < 1e-6 else f"{tacq * 1e6:.1f} µs",
                    xy=(tacq * 1e6, half_lsb), xytext=(tacq * 1e6 + 0.12, half_lsb * 12), fontsize=7.5,
                    color=c, arrowprops=dict(arrowstyle="-", lw=0.6, color=c))
    a1.set_xlim(0, 600)
    a1.set_ylim(0, 1.05)
    a1.set_xlabel("acquisition time (ns)")
    a1.set_ylabel("V$_{CS}$ / V$_S$")
    a1.legend(fontsize=7, loc="center right", bbox_to_anchor=(1.0, 0.42))
    a1.axvline(496, color=GREY, lw=0.7, ls=":")
    a1.text(490, 0.03, "496 ns", rotation=90, fontsize=7, ha="right", va="bottom", color=GREY)
    a1.set_title("Sampling-capacitor voltage", fontsize=8.5, loc="left")
    a2.axhline(half_lsb, color=RED, lw=0.9, ls="--")
    a2.text(1.45, half_lsb * 0.6, "½ LSB at 12 bits (2$^{-13}$)", ha="center", va="top", fontsize=7, color=RED)
    a2.set_xlim(0, 2.6)
    a2.set_ylim(1e-5, 1.2)
    a2.set_xlabel("acquisition time (µs)")
    a2.set_ylabel("settling error (V$_S$ − V$_{CS}$) / V$_S$")
    a2.set_title("Settling error, log scale", fontsize=8.5, loc="left")
    a2.grid(True, which="major", color=GRID, lw=0.5)
    save(fig, "26", "fig-26-6-sar-adc-input-model")


if __name__ == "__main__":
    fig_gpio_pin()
    fig_uart_frame()
    fig_spi_timing()
    fig_i2c()
    fig_can()
    fig_sar_input()
