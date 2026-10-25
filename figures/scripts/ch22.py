"""Figures for Chapter 22 — Python for Engineering.

Run from the repository root:  python figures/scripts/ch22.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon  # noqa: E402
from scipy import signal  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
LIGHT = "#EEF3F8"


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=True):
    xs, ys = zip(*pts)
    if not arrow_end:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls)
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=10))


def grid_cells(ax, x0, y_top, ncol, nrow, cw, ch, labels=None, fc="white", hl_col=None,
               hl_fc=None, fs=7, ghost_rows=()):
    """Draw an nrow x ncol grid with top-left at (x0, y_top)."""
    for r in range(nrow):
        for c in range(ncol):
            f = hl_fc if (hl_col is not None and c == hl_col) else fc
            ls = "--" if r in ghost_rows else "-"
            ec = GREY if r in ghost_rows else INK
            ax.add_patch(Rectangle((x0 + c * cw, y_top - (r + 1) * ch), cw, ch, fc=f, ec=ec,
                                   lw=0.8, ls=ls))
            if labels is not None and labels[r][c]:
                ax.text(x0 + (c + 0.5) * cw, y_top - (r + 0.5) * ch, labels[r][c],
                        ha="center", va="center", fontsize=fs,
                        color=GREY if r in ghost_rows else INK)


# ----------------------------------------------------------------------------
# Figure 22.1 — ndarray memory, strides, view and broadcasting
# ----------------------------------------------------------------------------
def fig_ndarray_strides():
    fig, ax = schematic(6.8, 4.75, xlim=(0, 17), ylim=(0.6, 12.4))
    fs = 7.5
    # --- memory strip -----------------------------------------------------
    cw, ch, y0 = 1.12, 0.75, 9.9
    x0 = 0.6
    ax.text(x0, 12.0, "Memory: one contiguous block of int16 (2 bytes per cell), 80 000 bytes",
            fontsize=8.5, weight="bold", va="center")
    for i in range(12):
        s, c = divmod(i, 4)
        f = tint(ORANGE) if c == 2 else (LIGHT if s % 2 == 0 else "white")
        ax.add_patch(Rectangle((x0 + i * cw, y0), cw, ch, fc=f, ec=INK, lw=0.8))
        ax.text(x0 + (i + 0.5) * cw, y0 + ch / 2, f"s{s}c{c}", ha="center", va="center", fontsize=7)
        ax.text(x0 + i * cw, y0 - 0.28, str(2 * i), ha="center", va="center", fontsize=6.5, color=GREY)
    ax.text(x0 + 12 * cw + 0.45, y0 + ch / 2, "...", fontsize=10, va="center")
    ax.text(x0 + 12 * cw + 1.2, y0 + ch / 2, "s9999c3", fontsize=7, va="center")
    ax.text(x0 + 12 * cw + 1.2, y0 - 0.28, "byte address", fontsize=6.5, color=GREY, va="center")
    # stride arcs above strip
    for k in range(2):
        xa = x0 + (2 + 4 * k + 0.5) * cw
        xb = x0 + (2 + 4 * (k + 1) + 0.5) * cw
        ax.annotate("", xy=(xb, y0 + ch), xytext=(xa, y0 + ch),
                    arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.1, mutation_scale=9,
                                    connectionstyle="arc3,rad=-0.25"))
        ax.text((xa + xb) / 2, y0 + ch + 0.62, "+8 B", ha="center", fontsize=7, color=ORANGE)
    ax.annotate("", xy=(x0 + 1.5 * cw, y0 - 0.55), xytext=(x0 + 0.5 * cw, y0 - 0.55),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.1, mutation_scale=9))
    ax.text(x0 + 1.6 * cw, y0 - 0.58, "+2 B", fontsize=7, color=BLUE, va="center")

    # --- logical array ----------------------------------------------------
    gx, gtop, gcw, gch = 1.5, 7.3, 1.1, 0.66
    ax.text(0.6, 8.45, "Logical array codes", fontsize=8.5, weight="bold", va="center")
    ax.text(0.6, 7.95, "shape (10000, 4), strides (8, 2) bytes", fontsize=7.5, va="center")
    labels = [[f"s{s}c{c}" for c in range(4)] for s in range(4)] + [["⋮"] * 4] + \
             [[f"s9999c{c}" for c in range(4)]]
    for r in range(6):
        for c in range(4):
            f = tint(ORANGE) if c == 2 else "white"
            ax.add_patch(Rectangle((gx + c * gcw, gtop - (r + 1) * gch), gcw, gch, fc=f, ec=INK, lw=0.8))
            ax.text(gx + (c + 0.5) * gcw, gtop - (r + 0.5) * gch, labels[r][c], ha="center",
                    va="center", fontsize=5.8 if r == 5 else 7)
    for c in range(4):
        ax.text(gx + (c + 0.5) * gcw, gtop + 0.22, f"ch {c}", ha="center", fontsize=7, color=GREY)
    for r, lab in enumerate(["s0", "s1", "s2", "s3", "", "s9999"]):
        ax.text(gx - 0.12, gtop - (r + 0.5) * gch, lab, ha="right", va="center", fontsize=7, color=GREY)
    ybot = gtop - 6 * gch
    # stride arrows
    ax.annotate("", xy=(gx - 0.75, gtop - 2.5 * gch), xytext=(gx - 0.75, gtop - 0.5 * gch),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=9))
    ax.text(gx - 0.95, gtop - 1.5 * gch, "axis 0\nstride 8 B", ha="right", va="center", fontsize=7)
    ax.annotate("", xy=(gx + 2.5 * gcw, ybot - 0.35), xytext=(gx + 0.5 * gcw, ybot - 0.35),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=9))
    ax.text(gx + 1.5 * gcw, ybot - 0.6, "axis 1: stride 2 B", ha="center", va="top", fontsize=7)
    ax.text(gx + 4 * gcw + 0.2, gtop - 2.4 * gch,
            "codes[:, 2]\n= view:\nsame memory,\nshape (10000,),\nstride 8 B,\nno copy",
            fontsize=7, color=ORANGE, va="center", ha="left")

    # --- broadcasting -----------------------------------------------------
    bx, btop, bcw, bch = 8.75, 7.3, 0.56, 0.55
    ax.add_patch(Rectangle((8.4, 1.0), 8.4, 7.75, fc="none", ec=GREY, lw=0.7, ls=":"))
    ax.text(8.6, 8.45, "Broadcasting", fontsize=8.5, weight="bold", va="center")
    ax.text(8.6, 7.95, "volts = codes * lsb / gain - offset", fontsize=7.5, va="center", family="monospace")
    lab_a = [["", "", "", ""] for _ in range(6)]
    grid_cells(ax, bx, btop, 4, 6, bcw, bch, lab_a, fc=LIGHT)
    ax.text(bx + 2 * bcw, btop - 6 * bch - 0.32, "codes\n(10000, 4)", ha="center", va="top", fontsize=7)
    ax.text(bx + 4 * bcw + 0.25, btop - 3 * bch, "÷", fontsize=13, ha="center", va="center")
    gx2 = bx + 4 * bcw + 0.5
    gains = ["1.0", "1.0", "2.5", "0.5"]
    lab_g = [gains] + [gains] * 5
    grid_cells(ax, gx2, btop, 4, 6, bcw, bch, lab_g, fc=tint(GREEN), ghost_rows=(1, 2, 3, 4, 5), fs=6)
    ax.text(gx2 + 2 * bcw, btop - 6 * bch - 0.32, "gain, shape (4,)\nstretched virtually\nalong axis 0",
            ha="center", va="top", fontsize=7)
    ax.text(gx2 + 4 * bcw + 0.25, btop - 3 * bch, "=", fontsize=13, ha="center", va="center")
    rx = gx2 + 4 * bcw + 0.5
    grid_cells(ax, rx, btop, 4, 6, bcw, bch, None, fc=tint(BLUE, "40"))
    ax.text(rx + 2 * bcw, btop - 6 * bch - 0.32, "volts\n(10000, 4)\nfloat64", ha="center", va="top",
            fontsize=7)
    ax.text(12.6, 1.55, "Shapes compared from the right:\n(10000, 4) with (4,) → (10000, 4).\n"
            "Dashed rows are never stored: no copy of gain.",
            ha="center", va="center", fontsize=6.8, color=INK)
    save(fig, "22", "fig-22-1-ndarray-strides-broadcasting")


def tint(c, a="33"):
    return c + a


# ----------------------------------------------------------------------------
# Figure 22.2 — converter efficiency curves
# ----------------------------------------------------------------------------
def fig_efficiency():
    fig, ax = new_fig(6.4, 3.8)
    i = np.linspace(0.2, 20, 600)
    for (vin, ls, col) in [(36, "-", BLUE), (48, "--", ORANGE), (60, ":", GREEN)]:
        eff = 12 * i / (12 * i + 0.8 + 0.02 * vin + 0.03 * i + 0.008 * i ** 2)
        ax.plot(i, 100 * eff, ls, color=col, label=f"$V_{{in}}$ = {vin} V", lw=2.0 if ls == ":" else 1.8)
        p0 = 0.8 + 0.02 * vin
        istar = np.sqrt(p0 / 0.008)
        estar = 12 * istar / (12 * istar + p0 + 0.03 * istar + 0.008 * istar ** 2)
        ax.plot(istar, 100 * estar, "o", color=col, ms=4.5, zorder=5)
        yk = {36: 93.6, 48: 92.9, 60: 92.2}[vin]
        ax.plot(8.6, yk, "o", color=col, ms=4.5)
        ax.text(9.0, yk, f"peak {100 * estar:.2f} % at {istar:.1f} A  ({vin} V)", fontsize=8,
                color=col, va="center")
    ax.text(8.4, 94.4, r"Peaks (dots), at $I^* = \sqrt{P_0/b}$:", fontsize=8, va="center")
    ax.set(xlabel="Output current (A)", ylabel="Efficiency (%)", xlim=(0, 20), ylim=(85, 100))
    ax.grid(True, alpha=0.5)
    ax.legend(loc="lower right")
    ax.text(0.5, 99.2, r"$\eta = 12I\,/\,(12I + 0.8 + 0.02V_{in} + 0.03I + 0.008I^2)$", fontsize=8.5)
    save(fig, "22", "fig-22-2-converter-efficiency-curves")


# ----------------------------------------------------------------------------
# Figure 22.3 — THD spectrum (Listing 22.6)
# ----------------------------------------------------------------------------
def fig_thd_spectrum():
    fs, N, f0 = 48_000, 4_800, 1_000.0
    n = np.arange(N)
    rng = np.random.default_rng(7)
    x = (1.0 * np.sin(2 * np.pi * f0 * n / fs) + 1e-3 * np.sin(2 * np.pi * 2 * f0 * n / fs)
         + 3e-3 * np.sin(2 * np.pi * 3 * f0 * n / fs) + rng.normal(0, 1e-4, N))
    w = signal.windows.hann(N, sym=False)
    P = np.abs(np.fft.rfft(x * w)) ** 2
    k0 = 100
    tp = lambda k: P[k - 1:k + 2].sum()  # noqa: E731
    thd = np.sqrt(sum(tp(h * k0) for h in range(2, 11)) / tp(k0))
    db = 10 * np.log10(P / P[k0])
    f = np.arange(P.size) * fs / N
    floor = 10 * np.log10(np.mean(10 ** (db[(f > 4000) & (f < 12000)] / 10)))  # mean noise power per bin

    fig, ax = new_fig(6.4, 3.8)
    ax.plot(f / 1e3, db, color=BLUE, lw=0.7)
    ax.set(xlabel="Frequency (kHz)", ylabel="Level (dB re fundamental)", xlim=(0, 12), ylim=(-140, 5))
    ax.grid(True, alpha=0.5)
    for k, lab in [(100, "fundamental\n0 dBc"), (200, f"H2  {10*np.log10(tp(200)/tp(k0)):.1f} dBc"),
                   (300, f"H3  {10*np.log10(tp(300)/tp(k0)):.1f} dBc")]:
        if k == 100:
            continue
        ax.annotate(lab, xy=(f[k] / 1e3, db[k]), xytext=(f[k] / 1e3 - 0.8 if k == 200 else f[k] / 1e3 + 0.15, -46 if k == 200 else -42),
                    fontsize=7.5, color=INK, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.axhline(floor, color=ORANGE, lw=0.9, ls="--")
    ax.text(11.9, floor + 4, f"noise floor ≈ {floor:.0f} dBc per bin", fontsize=7.5, color=ORANGE,
            ha="right", bbox=dict(fc="white", ec="none", pad=1))
    ax.text(11.9, -3, f"THD = {100*thd:.3f} %  ({20*np.log10(thd):.1f} dB)\n"
            f"bin spacing {fs/N:.0f} Hz, N = 4800, $f_s$ = 48 kHz\nperiodic Hann window",
            fontsize=7.5, ha="right", va="top")
    # inset: bins 97..103
    ins = ax.inset_axes([0.50, 0.40, 0.22, 0.34])
    kk = np.arange(97, 104)
    ins.stem(kk, np.maximum(db[kk], -140), bottom=-140, basefmt=" ",
             linefmt=BLUE, markerfmt="o")
    ins.set_ylim(-140, 5)
    ins.set_xticks(kk[::2])
    ins.tick_params(labelsize=6)
    ins.set_xlabel("bin k", fontsize=6.5, labelpad=1)
    ins.set_ylabel("dBc", fontsize=6.5, labelpad=1)
    ins.set_title("fundamental, bins 97–103:\n3-bin Hann main lobe", fontsize=6.5, pad=2)
    ins.patch.set_facecolor("white")
    save(fig, "22", "fig-22-3-thd-spectrum")
    return thd, floor


# ----------------------------------------------------------------------------
# Figure 22.4 — DAQ software stacks
# ----------------------------------------------------------------------------
def fig_daq_stack():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0.4, 12.6))
    fs = 7.5

    def layer(x, y, w, h, text, fc=LIGHT, f=fs, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=fc, ec=INK, lw=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=f,
                weight="bold" if bold else "normal")

    # left stack
    L, W = 0.2, 7.9
    cx = L + W / 2
    ax.text(cx, 12.2, "Bench instruments (SCPI text)", ha="center", fontsize=9, weight="bold")
    layer(L, 10.75, W, 0.95, "Python script", fc=tint(BLUE, "30"), bold=True)
    layer(L, 9.3, W, 0.95, "PyVISA (ResourceManager, write / query)")
    layer(L, 7.45, W, 1.35, "VISA library\nvendor VISA (NI, Keysight, R&S) or pyvisa-py")
    widths = [1.8, 2.6, 1.65, 1.45]
    trans = ["USB-TMC", "LAN: VXI-11,\nHiSLIP port 4880,\nsocket port 5025", "GPIB\n(IEEE 488)", "RS-232"]
    inst = ["DC supply", "electronic\nload", "DMM", "oscillo-\nscope"]
    x = L
    for wk, t, it in zip(widths, trans, inst):
        layer(x, 4.95, wk, 1.6, t, fc=tint(YELLOW, "30"), f=6.5)
        ax.add_patch(Rectangle((x, 3.05), wk, 1.15, fc=tint(GREEN, "30"), ec=INK, lw=0.9))
        ax.text(x + wk / 2, 3.625, it, ha="center", va="center", fontsize=7)
        line(ax, [(x + wk / 2, 4.95), (x + wk / 2, 4.2)], lw=0.8)
        x += wk + 0.133
    ax.text(L, 6.85, "transports", fontsize=7, color=GREY, va="center")
    ax.text(L, 2.75, "instruments", fontsize=7, color=GREY, va="center")
    for ya, yb in [(10.75, 10.25), (9.3, 8.8), (7.45, 6.55)]:
        line(ax, [(cx, ya), (cx, yb)], lw=0.9)
    ax.text(cx, 1.6, "SCPI query round trip: 0.2 to 5 ms\n(e.g. *IDN?, :MEAS:VOLT?)",
            ha="center", va="center", fontsize=7.5, color=ORANGE)

    # right stack
    R, W2 = 8.9, 7.9
    cr = R + W2 / 2
    ax.text(cr, 12.2, "Embedded target (binary frames)", ha="center", fontsize=9, weight="bold")
    layer(R, 10.75, W2, 0.95, "Python script (acquisition thread)", fc=tint(BLUE, "30"), bold=True)
    layer(R, 9.3, W2, 0.95, "pyserial (serial_for_url, read)")
    layer(R, 7.45, W2, 1.35, "OS driver: COM port or /dev/ttyACM0\nUSB CDC-ACM, or USB-UART bridge")
    layer(R, 5.65, W2, 0.95, "UART 921 600 baud, 8N1", fc=tint(YELLOW, "30"))
    ax.add_patch(Rectangle((R, 3.05), W2, 1.95, fc=tint(GREEN, "30"), ec=INK, lw=0.9))
    ax.text(cr, 4.62, "MCU firmware: 14-byte frame per sample", ha="center", va="center", fontsize=fs)
    fields = [("AA 55", tint(ORANGE, "55")), ("seq", "white"), ("s0", "white"), ("s1", "white"),
              ("s2", "white"), ("s3", "white"), ("CRC", tint(PINK, "55"))]
    fx, fw = R + 0.3, (W2 - 0.6) / 7
    for name, fc in fields:
        ax.add_patch(Rectangle((fx, 3.35), fw, 0.75, fc=fc, ec=INK, lw=0.7))
        ax.text(fx + fw / 2, 3.725, name, ha="center", va="center", fontsize=6.8)
        fx += fw
    ax.text(cr, 2.75, "2 bytes per field: sync, uint16 seq, 4 x int16, CRC-16", ha="center",
            va="center", fontsize=6.8, color=GREY)
    for ya, yb in [(10.75, 10.25), (9.3, 8.8), (7.45, 6.6), (5.65, 5.0)]:
        line(ax, [(cr, ya), (cr, yb)], lw=0.9)
    ax.text(cr, 1.6, "USB CDC: one transfer per 1 ms frame\n921 600 baud: 140 bits = 152 µs per frame",
            ha="center", va="center", fontsize=7.5, color=ORANGE)
    save(fig, "22", "fig-22-4-daq-software-stack")


# ----------------------------------------------------------------------------
# Figure 22.5 — automated sweep flowchart
# ----------------------------------------------------------------------------
def fig_sweep_flowchart():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7.3
    w, h = 4.6, 0.95

    def b(x, y, text, fc=LIGHT, ww=w, hh=h, ec=INK, lw=0.9, bold=False):
        ax.add_patch(FancyBboxPatch((x - ww / 2, y - hh / 2), ww, hh,
                                    boxstyle="round,pad=0.02,rounding_size=0.14", fc=fc, ec=ec, lw=lw))
        ax.text(x, y, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal")

    # column 1: setup
    c1 = 2.6
    y1 = [11.6, 10.15, 8.7, 7.25]
    b(c1, y1[0], "Load config,\ncreate run folder")
    b(c1, y1[1], "Connect instruments,\nrecord *IDN?")
    b(c1, y1[2], "Safe initial state:\nload 0 A, supply off")
    b(c1, y1[3], "Supply on")
    for a, bb in zip(y1[:-1], y1[1:]):
        line(ax, [(c1, a - h / 2), (c1, bb + h / 2)])
    # loop header
    yl = 5.5
    b(c1, yl, "Next point?\nfor Vin in 36, 48, 60 V\n  for Iout in 1 … 20 A", fc=tint(YELLOW, "40"),
      hh=1.5)
    line(ax, [(c1, y1[3] - h / 2), (c1, yl + 0.75)])

    # column 2: inside loop
    c2 = 8.5
    y2 = [11.6, 10.15, 8.7, 7.25]
    b(c2, y2[0], "Set point:\nsupply Vin, load Iout")
    b(c2, y2[1], "Settle until temperature\nslope < 0.1 °C/min")
    b(c2, y2[2], "Measure Vin, Iin, Vout,\nIout, Tcase")
    b(c2, y2[3], "Check limits: Tcase < 105 °C,\nVout = 12 V ± 5 %", ww=5.1)
    for a, bb in zip(y2[:-1], y2[1:]):
        line(ax, [(c2, a - h / 2), (c2, bb + h / 2)])
    # loop -> set point
    line(ax, [(c1 + w / 2, yl + 0.35), (5.4, yl + 0.35), (5.4, y2[0]), (c2 - w / 2, y2[0])])
    ax.text(5.5, 9.0, "yes", fontsize=7, color=GREEN)
    # diamond
    yd = 5.3
    dw, dh = 4.4, 1.7
    ax.add_patch(Polygon([(c2, yd + dh / 2), (c2 + dw / 2, yd), (c2, yd - dh / 2), (c2 - dw / 2, yd)],
                         closed=True, fc=tint(PINK, "30"), ec=INK, lw=0.9))
    ax.text(c2, yd, "Limit violated\nor exception?", ha="center", va="center", fontsize=fs)
    line(ax, [(c2, y2[3] - h / 2), (c2, yd + dh / 2)])
    # No -> store -> back to loop
    ys_ = 3.25
    b(c2, ys_, "Store point to HDF5\n(flush)")
    line(ax, [(c2, yd - dh / 2), (c2, ys_ + h / 2)])
    ax.text(c2 + 0.15, yd - dh / 2 - 0.35, "no", fontsize=7, color=GREEN)
    line(ax, [(c2 - w / 2, ys_), (5.4, ys_), (5.4, yl - 0.35), (c1 + w / 2, yl - 0.35)])
    ax.text(5.5, 4.0, "next\npoint", fontsize=7, color=GREY)

    # column 3: exit path
    c3 = 14.3
    b(c3, 7.25, "Log error\n(point, traceback)", fc=tint(ORANGE, "30"), ww=4.2)
    line(ax, [(c2 + dw / 2, yd), (c3, yd), (c3, 7.25 - h / 2)])
    ax.text(c2 + dw / 2 + 0.2, yd + 0.15, "yes", fontsize=7, color=RED)
    # finally box
    yf = 3.25
    ax.add_patch(FancyBboxPatch((c3 - 2.35, yf - 0.85), 4.7, 1.7,
                                boxstyle="round,pad=0.02,rounding_size=0.14", fc=tint(RED, "22"),
                                ec=RED, lw=2.0))
    ax.text(c3, yf + 0.2, "finally:", ha="center", va="center", fontsize=8, weight="bold", color=RED)
    ax.text(c3, yf - 0.35, "load 0 A, supply off,\nclose files", ha="center", va="center", fontsize=fs)
    line(ax, [(c3 + 1.6, 7.25 - h / 2), (c3 + 1.6, yf + 0.85)], color=RED)
    ax.text(c3 + 1.75, 5.9, "exception", fontsize=6.8, color=RED, rotation=90, va="center")
    # normal end: from loop header bottom down to finally
    line(ax, [(c1, yl - 0.75), (c1, 1.9), (11.4, 1.9), (11.4, yf - 0.45), (c3 - 2.35, yf - 0.45)], color=INK)
    ax.text(c1 + 0.15, 2.55, "loops done\n(normal end)", fontsize=6.8, color=GREY, va="center")
    # Ctrl-C
    ax.text(c3 + 1.0, 10.0, "Ctrl-C\n(KeyboardInterrupt)\nfrom any step", ha="center", va="center",
            fontsize=6.8, color=RED)
    line(ax, [(c3 + 1.0, 9.35), (c3 + 1.0, 8.5), (c3 + 2.45, 8.5), (c3 + 2.45, yf), (c3 + 2.35, yf)],
         color=RED, ls="--")
    # report
    line(ax, [(c3, yf - 0.85), (c3, 1.55)])
    b(c3, 1.05, "Generate report", fc=tint(GREEN, "30"), ww=3.6, hh=0.8)
    save(fig, "22", "fig-22-5-automated-sweep-flowchart")


if __name__ == "__main__":
    fig_ndarray_strides()
    fig_efficiency()
    thd, floor = fig_thd_spectrum()
    print(f"THD {100*thd:.4f} %, floor {floor:.1f} dBc")
    fig_daq_stack()
    fig_sweep_flowchart()
