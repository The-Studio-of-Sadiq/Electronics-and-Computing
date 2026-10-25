"""Figures for Chapter 25 — Embedded-System Architecture.

Run from the repository root:  python figures/scripts/ch25.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, FancyArrowPatch  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4], COLORS[5]
RED = "#C62828"
GREY = "#777777"
LIGHT = "#EEF3F8"


def tint(c, a="33"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False):
    """Poly-line through pts, optional arrow head on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=10))


# ----------------------------------------------------------------------------
# Figure 25.1 — block diagram of the water meter
# ----------------------------------------------------------------------------
def fig_block_diagram():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7.5

    # --- microcontroller --------------------------------------------------
    mx0, mx1, my0, my1 = 4.9, 11.5, 2.6, 9.0
    ax.add_patch(FancyBboxPatch((mx0, my0), mx1 - mx0, my1 - my0,
                                boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#F6F9FC", ec=INK, lw=1.4))
    ax.text((mx0 + mx1) / 2, my1 - 0.38, "Microcontroller", ha="center", va="center",
            fontsize=9.5, weight="bold")
    bw, bh = 1.95, 0.85
    cols = [mx0 + 0.18, mx0 + 2.33, mx0 + 4.48]
    inner = [["Cortex-M4F\ncore", "512 KB\nFlash", "128 KB\nSRAM"],
             ["NVIC", "DMA", "Timers"],
             ["ADC", "CRC unit", "AES unit"]]
    fcs = [tint(BLUE, "30"), tint(BLUE, "18"), tint(BLUE, "18")]
    for r, row in enumerate(inner):
        y = my1 - 1.75 - r * 1.05
        for c, txt in enumerate(row):
            box(ax, cols[c], y, bw, bh, txt, fc=fcs[r], fontsize=7.2 if r == 0 else fs)
    # always-on domain (dashed)
    ax0, ay0, aw, ah = mx0 + 0.12, my0 + 0.2, 4.75, 1.4
    ax.add_patch(Rectangle((ax0, ay0), aw, ah, fill=False, ls=(0, (4, 2.5)), ec=GREEN, lw=1.3))
    ax.text(ax0 + 0.08, ay0 + ah - 0.05, "always-on domain", ha="left", va="top",
            fontsize=7.5, color=GREEN, style="italic")
    ab_w, ab_s = 1.45, 1.55
    centers = []
    for i, t in enumerate(["RTC", "Wake-up\nlogic", "Backup\nregisters"]):
        bx = ax0 + 0.1 + i * ab_s
        box(ax, bx, ay0 + 0.1, ab_w, 0.85, t, fc=tint(GREEN, "22"), fontsize=7)
        centers.append(bx + ab_w / 2)
    hf_x0 = ax0 + aw + 0.12
    hf_w = mx1 - 0.12 - hf_x0
    box(ax, hf_x0, ay0 + 0.1, hf_w, 0.85, "HF clock\n+ PLL", fc=tint(BLUE, "18"), fontsize=7)
    hf_c = hf_x0 + hf_w / 2
    rtc_c, wk_c = centers[0], centers[1]

    # --- left: measurement chain ------------------------------------------
    lx, lw_ = 0.1, 3.4
    box(ax, lx, 7.8, lw_, 1.0, "Ultrasonic\ntransducer pair", fc=tint(YELLOW, "33"), fontsize=fs)
    box(ax, lx, 5.6, lw_, 1.2, "Analog front end:\npulser + receiver\namplifier", fc=tint(YELLOW, "33"),
        fontsize=fs)
    box(ax, lx, 3.4, lw_, 1.2, "Time-to-digital\nconverter\n(or MCU ADC)", fc=tint(YELLOW, "33"),
        fontsize=fs)
    cx = lx + lw_ / 2
    arrow(ax, cx - 0.5, 7.8, cx - 0.5, 6.8, both=True)
    ax.text(cx - 0.35, 7.3, "TX burst / echo", fontsize=7, va="center", ha="left")
    arrow(ax, cx, 5.6, cx, 4.6)
    ax.text(cx + 0.15, 5.1, "stop pulses", fontsize=7, va="center")
    arrow(ax, lx + lw_, 4.0, mx0, 4.0)
    ax.text((lx + lw_ + mx0) / 2, 4.08, "SPI\n+ IRQ", fontsize=7, ha="center", va="bottom")
    arrow(ax, mx0, 6.2, lx + lw_, 6.2)
    ax.text((lx + lw_ + mx0) / 2, 6.28, "timer\nstart", fontsize=7, ha="center", va="bottom")

    # --- top: power --------------------------------------------------------
    box(ax, 0.1, 10.4, 3.6, 1.2, "3.6 V Li-SOCl$_2$ cell\n2.6 Ah", fc=tint(ORANGE, "22"), fontsize=fs)
    box(ax, 6.7, 10.4, 3.0, 1.2, "Buck regulator\n1.8 V", fc=tint(ORANGE, "22"), fontsize=fs)
    box(ax, 12.75, 10.4, 4.2, 1.2, "100 µF hybrid capacitor\n(radio pulses)", fc=tint(ORANGE, "22"),
        fontsize=fs)
    arrow(ax, 3.7, 11.0, 6.7, 11.0)
    ax.text(5.2, 11.08, "3.6 V", fontsize=7.5, ha="center", va="bottom")
    arrow(ax, 8.2, 10.4, 8.2, my1)
    ax.text(8.35, 9.7, "1.8 V", fontsize=7.5, va="center")
    line(ax, [(1.9, 11.6), (1.9, 12.1), (14.85, 12.1), (14.85, 11.6)], arrow_end=True)
    ax.text(8.2, 12.17, "3.6 V rail to modem", fontsize=7.5, ha="center", va="bottom")

    # --- right: modem and external Flash -----------------------------------
    rx, rw = 13.4, 3.5
    box(ax, rx, 6.9, rw, 1.6, "LTE-M modem\npeak 400 mA", fc=tint(PINK, "33"), fontsize=8)
    box(ax, rx, 3.6, rw, 1.6, "SPI NOR Flash 8 MB\nlogs, update images", fc=tint(PINK, "33"), fontsize=fs)
    arrow(ax, 14.85, 10.4, 14.85, 8.5)
    ax.text(15.0, 9.45, "supply\n+ buffer", fontsize=7, va="center")
    arrow(ax, mx1, 7.7, rx, 7.7, both=True)
    ax.text((mx1 + rx) / 2, 7.8, "UART\n115 200\nbaud", fontsize=7, ha="center", va="bottom")
    arrow(ax, mx1, 4.4, rx, 4.4, both=True)
    ax.text((mx1 + rx) / 2, 4.5, "SPI", fontsize=7, ha="center", va="bottom")

    # --- bottom: clocks and service ---------------------------------------
    by, bh2 = 0.2, 1.1
    box(ax, 1.9, by, 2.6, bh2, "32.768 kHz\ncrystal", fc=tint(SKY, "33"), fontsize=fs)
    box(ax, wk_c - 1.15, by, 2.3, bh2, "Tamper\nswitch", fc=tint(SKY, "33"), fontsize=fs)
    box(ax, hf_c - 1.25, by, 2.5, bh2, "32 MHz\ncrystal", fc=tint(SKY, "33"), fontsize=fs)
    box(ax, 13.2, by, 3.2, bh2, "Optical\nservice port", fc=tint(SKY, "33"), fontsize=fs)
    line(ax, [(3.2, by + bh2), (3.2, 1.95), (rtc_c, 1.95), (rtc_c, ay0 + 0.1)], arrow_end=True)
    ax.text(3.35, 1.6, "LSE", fontsize=7, ha="left", va="center")
    arrow(ax, wk_c, by + bh2, wk_c, ay0 + 0.1)
    ax.text(wk_c + 0.12, 1.6, "GPIO", fontsize=7, ha="left", va="center")
    arrow(ax, hf_c, by + bh2, hf_c, ay0 + 0.1)
    ax.text(hf_c + 0.12, 1.6, "HSE", fontsize=7, ha="left", va="center")
    line(ax, [(14.8, by + bh2), (14.8, 2.2), (12.4, 2.2), (12.4, 3.1), (mx1, 3.1)], arrow_end=True)
    ax.text(14.95, 1.7, "UART2", fontsize=7, ha="left", va="center")

    save(fig, "25", "fig-25-1-embedded-system-block-diagram")


# ----------------------------------------------------------------------------
# Figure 25.2 — Flash and SRAM memory layout
# ----------------------------------------------------------------------------
def fig_memory_layout():
    fig, ax = schematic(6.6, 5.0, xlim=(0, 16.5), ylim=(0, 12.5))
    fs = 8

    def region(x, y0, y1, w, text, fc, ec=INK, fontsize=fs, tx=None):
        ax.add_patch(Rectangle((x, y0), w, y1 - y0, fc=fc, ec=ec, lw=1.0))
        if text:
            ax.text(tx if tx is not None else x + w / 2, (y0 + y1) / 2, text, ha="center", va="center",
                    fontsize=fontsize)

    # Flash bar (display heights, not to scale)
    fx, fw = 2.9, 3.4
    fl = [
        (0.8, 1.35, "vector table (0x1C8 B)", tint(GREY, "40")),
        (1.35, 4.6, ".text  180 KB", tint(BLUE, "40")),
        (4.6, 5.9, ".rodata  40 KB", tint(BLUE, "25")),
        (5.9, 6.6, ".data image  4 KB", tint(ORANGE, "45")),
        (6.6, 9.6, "free", "white"),
        (9.6, 11.0, "settings and\nlog sectors  64 KB", tint(GREEN, "35")),
    ]
    for y0, y1, t, c in fl:
        region(fx, y0, y1, fw, t, c, fontsize=7 if y1 - y0 < 0.6 else fs)
    ax.text(fx + fw / 2, 11.4, "Flash  512 KB", ha="center", va="bottom", fontsize=9.5, weight="bold")
    faddr = [(0.8, "0x0800 0000"), (1.35, "0x0800 01C8"), (4.6, "0x0802 D1C8"),
             (5.9, "0x0803 71C8"), (6.6, "0x0803 81C8"), (9.6, "0x0807 0000"), (11.0, "0x0808 0000")]
    for y, a in faddr:
        ax.plot([fx - 0.15, fx], [y, y], color=INK, lw=0.8)
        ax.text(fx - 0.22, y, a, ha="right", va="center", fontsize=7, family="DejaVu Sans Mono")

    # SRAM bar
    sx, sw = 10.0, 3.4
    region(sx, 0.8, 1.6, sw, ".data  4 KB", tint(ORANGE, "45"))
    region(sx, 1.6, 3.6, sw, "", tint(PINK, "35"))
    ax.text(sx + sw / 2, 2.9, ".bss  38 KB", ha="center", va="center", fontsize=fs)
    region(sx, 3.6, 4.9, sw, "heap\n16 KB", tint(YELLOW, "40"), tx=sx + sw / 2 + 0.6)
    region(sx, 4.9, 5.05, sw, "", "white")
    y = 5.05
    stack_h, guard_h = 0.5, 0.13
    guard_ys = []
    for k in range(5):
        region(sx, y, y + guard_h, sw, "", RED, ec=RED)
        guard_ys.append(y + guard_h / 2)
        region(sx, y + guard_h, y + guard_h + stack_h, sw, f"task {k + 1} stack  2 KB", tint(SKY, "40"),
               fontsize=7.5)
        y += guard_h + stack_h
    region(sx, y, 9.9, sw, "free", "white", tx=sx + sw / 2 + 0.6)
    region(sx, 9.9, 11.0, sw, "main stack  4 KB", tint(SKY, "70"))
    ax.text(sx + sw / 2, 11.4, "SRAM  128 KB", ha="center", va="bottom", fontsize=9.5, weight="bold")
    saddr = [(0.8, "0x2000 0000"), (1.6, "0x2000 1000"), (3.6, "0x2000 A800"), (4.9, "0x2000 E800"),
             (9.9, "0x2001 F000"), (11.0, "0x2002 0000")]
    for yy, a in saddr:
        ax.plot([sx + sw, sx + sw + 0.15], [yy, yy], color=INK, lw=0.8)
        ax.text(sx + sw + 0.22, yy, a, ha="left", va="center", fontsize=7, family="DejaVu Sans Mono")
    ax.text(sx + sw + 0.22, 11.38, "initial SP", ha="left", va="center", fontsize=7.5, color=BLUE)

    # growth arrows
    arrow(ax, sx + 0.45, 3.75, sx + 0.45, 4.75)
    ax.text(sx + 0.62, 4.25, "grows\nup", fontsize=7, va="center", ha="left")
    arrow(ax, sx + 0.45, 9.8, sx + 0.45, 8.85)
    ax.text(sx + 0.62, 9.3, "grows\ndown", fontsize=7, va="center", ha="left")

    # guard label on the right side
    gy = guard_ys[2]
    line(ax, [(sx + sw, gy), (sx + sw + 0.5, 7.2)], color=RED, lw=0.9)
    ax.text(sx + sw + 0.55, 7.2, "MPU guard\nregion 32 B\nbelow each\ntask stack", ha="left", va="center",
            fontsize=7.5, color=RED)

    # copy arrow .data
    ax.add_patch(FancyArrowPatch((fx + fw, 6.25), (sx, 1.2), connectionstyle="arc3,rad=0.2",
                                 arrowstyle="-|>", mutation_scale=12, color=ORANGE, lw=1.6))
    ax.text(8.3, 5.6, "copied by\nReset_Handler", ha="center", va="center", fontsize=8, color=ORANGE,
            weight="bold")
    # zeroed at boot
    ax.text(sx + sw / 2, 2.3, "zeroed at boot", ha="center", va="center", fontsize=7.5, color="#8E3B73",
            weight="bold")

    ax.text(8.25, 0.25, "Section heights not to scale; addresses increase upwards.", ha="center",
            va="center", fontsize=7.5, style="italic", color=GREY)
    save(fig, "25", "fig-25-2-memory-layout")


# ----------------------------------------------------------------------------
# Figure 25.3 — duty-cycled supply current
# ----------------------------------------------------------------------------
def fig_current_profile():
    I_SLEEP = 2e-6
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.8), gridspec_kw=dict(width_ratios=[1, 1.15]))

    # left: metering events every 1 s
    t = np.linspace(0, 1.2, 240001)
    i = np.full_like(t, I_SLEEP)
    for t0 in (0.1, 1.1):
        m = (t >= t0) & (t < t0 + 2e-3)
        i[m] = 3e-3
    a1.fill_between(t, 1e-7, i, where=i > 1e-4, color=BLUE, alpha=0.35, step=None, lw=0)
    a1.plot(t, i, color=BLUE, lw=1.3)
    a1.set_yscale("log")
    a1.set_ylim(1e-6, 1)
    a1.set_xlim(0, 1.2)
    a1.set_xlabel("time (s)")
    a1.set_ylabel("supply current (A)")
    a1.set_title("Metering period", fontsize=10)
    # inset: one metering event on a linear millisecond scale
    ins = a1.inset_axes([0.34, 0.56, 0.5, 0.36])
    tz = np.linspace(-1, 4, 5001)
    iz = np.where((tz >= 0) & (tz < 2), 3.0, 0.002)
    ins.fill_between(tz, 0, iz, color=BLUE, alpha=0.35, lw=0)
    ins.plot(tz, iz, color=BLUE, lw=1.2)
    ins.set_xlim(-1, 4)
    ins.set_ylim(0, 5.2)
    ins.set_xticks([0, 2, 4])
    ins.set_yticks([0, 3])
    ins.tick_params(labelsize=6.5, length=2)
    ins.set_xlabel("ms", fontsize=6.5, labelpad=0)
    ins.set_ylabel("mA", fontsize=6.5, labelpad=0)
    ins.text(1.0, 1.5, "6 µC", ha="center", va="center", fontsize=7, weight="bold")
    ins.text(-0.85, 4.55, "2 ms at 3 mA: wake,\ntime of flight, totaliser", ha="left", va="center",
             fontsize=6.3)
    a1.annotate("", xy=(0.104, 3e-3), xytext=(0.43, 0.04),
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7, ls=":"))
    a1.text(0.6, 3.0e-6, "stop mode + RTC, 2 µA", ha="center", va="bottom", fontsize=7.5)
    a1.annotate("", xy=(0.1, 6e-5), xytext=(1.1, 6e-5),
                arrowprops=dict(arrowstyle="<|-|>", color=GREY, lw=0.8, mutation_scale=8))
    a1.text(0.6, 7e-5, "T = 1 s", ha="center", va="bottom", fontsize=7.5, color=GREY)

    # right: radio report
    t2 = np.linspace(0, 2.0, 400001)
    i2 = np.full_like(t2, I_SLEEP)
    t_mcu, t_mod0, t_mod1 = 0.20, 0.201, 1.701
    i2[(t2 >= t_mcu) & (t2 < t_mod0)] = 3e-3
    burst = (t2 >= t_mod0) & (t2 < t_mod1)
    slots = []
    slot_w = 4e-3
    for k in range(10):
        s0 = 0.55 + k * 0.105
        slots.append((s0, s0 + slot_w))
    tx_time = 10 * slot_w
    # base current chosen so that the burst averages exactly 40 mA (60 mC over 1.5 s)
    i_base = (40e-3 * 1.5 - 400e-3 * tx_time) / (1.5 - tx_time)
    i2[burst] = i_base
    # attach phase with modest ripple (deterministic) — keep the average fixed
    for s0, s1 in slots:
        i2[(t2 >= s0) & (t2 < s1)] = 400e-3
    q = np.trapezoid(i2[burst], t2[burst])
    a2.fill_between(t2, 1e-7, i2, where=burst, color=PINK, alpha=0.35, lw=0)
    a2.plot(t2, i2, color=PINK, lw=1.0)
    a2.set_yscale("log")
    a2.set_ylim(1e-6, 1)
    a2.set_xlim(0, 2.0)
    a2.set_xlabel("time (s)")
    a2.set_title("Radio report (every 6 h)", fontsize=10)
    a2.annotate("MCU wake\n1 ms", xy=(0.2005, 3e-3), xytext=(0.03, 2e-4), fontsize=7.5,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=8))
    a2.text(0.95, 6e-4, f"LTE-M attach + transmit\n1.5 s, average 40 mA\n≈ {q * 1e3:.0f} mC",
            ha="center", va="center", fontsize=7.5)
    a2.text(1.06, 0.55, "TX slots, 400 mA peaks", ha="center", va="bottom", fontsize=7.5)
    a2.text(1.85, 3.0e-6, "2 µA", ha="center", va="bottom", fontsize=7.5)
    for a in (a1, a2):
        a.grid(True, which="major", axis="y", color=GRID, lw=0.6)
    fig.text(0.5, -0.02, "Average current: 2 µA sleep + 6.00 µA metering + 2.78 µA radio = 10.8 µA "
             "(reports every 6 h)", ha="center", fontsize=8.5)
    fig.tight_layout()
    save(fig, "25", "fig-25-3-duty-cycle-current-profile")


# ----------------------------------------------------------------------------
# Figure 25.4 — superloop vs interrupt vs RTOS
# ----------------------------------------------------------------------------
def fig_architectures_timing():
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    rows = {"Superloop": 5.2, "Interrupt-\ndriven": 2.9, "RTOS-based": 0.7}
    h = 0.8
    C_TASK, C_BG, C_ISR, C_K = BLUE, "#A9D3F0", ORANGE, "#333333"
    VIS = 0.14  # drawn width of 2-50 us blocks (exaggerated for visibility)

    def blk(y, t0, t1, c, text="", tc=INK, fs=7.5):
        ax.add_patch(Rectangle((t0, y), t1 - t0, h, fc=c, ec=INK, lw=0.6))
        if text:
            ax.text((t0 + t1) / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc)

    def event(y):
        ax.annotate("", xy=(1.0, y + h), xytext=(1.0, y + h + 0.7),
                    arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.4, mutation_scale=10))

    def bracket(y, t0, t1):
        ax.annotate("", xy=(t0, y), xytext=(t1, y),
                    arrowprops=dict(arrowstyle="|-|", color=RED, lw=1.0, mutation_scale=3,
                                    shrinkA=0, shrinkB=0))

    # superloop
    y = rows["Superloop"]
    blk(y, 0, 12, C_BG, "display 12 ms")
    blk(y, 12, 12.3, "#7FB8E0")
    blk(y, 12.3, 13.1, "#4F9AD0")
    blk(y, 13.1, 15.1, C_TASK, "protocol\n2 ms", tc="white")
    blk(y, 15.1, 20, C_BG, "display …")
    ax.annotate("sensor 0.3 ms", xy=(12.15, y + h), xytext=(10.6, y + h + 0.45), fontsize=7,
                ha="center", arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    ax.annotate("filter 0.8 ms", xy=(12.7, y + h), xytext=(13.6, y + h + 0.45), fontsize=7,
                ha="left", arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
    event(y)
    bracket(y - 0.3, 1.0, 13.1)
    ax.text(7.05, y - 0.42, "response 12.1 ms (frame handled at 13.1 ms)", ha="center", va="top",
            fontsize=7.5, color=RED)
    ax.text(1.12, y + h + 0.72, "UART frame complete (t = 1 ms)", fontsize=7.5, color=RED, ha="left",
            va="center")

    # interrupt-driven
    y = rows["Interrupt-\ndriven"]
    blk(y, 0, 1.0, C_BG)
    blk(y, 1.0 + VIS, 20, C_BG, "background loop (display) resumes")
    blk(y, 1.0, 1.0 + VIS, C_ISR)
    event(y)
    ax.annotate("ISR (50 µs) handles the reply", xy=(1.0 + VIS, y + h * 0.75), xytext=(2.2, y + h + 0.45),
                fontsize=7.5, color=ORANGE, va="center",
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.8, mutation_scale=8))
    ax.text(1.0, y - 0.12, "response 0.05 ms", ha="left", va="top", fontsize=7.5, color=RED)

    # RTOS
    y = rows["RTOS-based"]
    blk(y, 0, 1.0, C_BG)
    blk(y, 1.0, 1.0 + VIS, C_K)
    blk(y, 1.0 + VIS, 3.0, C_TASK, "protocol\ntask 2 ms", tc="white")
    blk(y, 3.0, 3.0 + VIS, C_K)
    blk(y, 3.0 + VIS, 20, C_BG, "low-priority display task resumes")
    event(y)
    ax.annotate("kernel switch (2 µs)", xy=(1.0 + VIS / 2, y + h), xytext=(3.4, y + h + 0.45), fontsize=7.5,
                va="center", arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=8))
    bracket(y - 0.3, 1.0, 3.0)
    ax.text(3.25, y - 0.3, "response ≈ 2 ms", ha="left", va="center", fontsize=7.5, color=RED)

    ax.set_xlim(0, 20)
    ax.set_ylim(0.0, 7.0)
    ax.set_yticks([v + h / 2 for v in rows.values()])
    ax.set_yticklabels(list(rows.keys()))
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xticks(range(0, 21, 2))
    ax.set_xlabel("time (ms)   [ISR and kernel blocks drawn wider than scale]")
    from matplotlib.patches import Patch
    handles = [Patch(fc=C_TASK, ec=INK, label="task / activity"),
               Patch(fc=C_BG, ec=INK, label="low-priority / background"),
               Patch(fc=C_ISR, ec=INK, label="ISR"),
               Patch(fc=C_K, ec=INK, label="kernel")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, fontsize=7.5,
              handlelength=1.4, columnspacing=1.2)
    fig.tight_layout()
    save(fig, "25", "fig-25-4-firmware-architectures-timing")

# ----------------------------------------------------------------------------
# Figure 25.5 — secure boot flow
# ----------------------------------------------------------------------------
def fig_boot_flow():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7
    C_HW, C_BL, C_APP = tint(GREY, "30"), tint(ORANGE, "28"), tint(BLUE, "25")

    def diamond(cx, cy, w, h, text, fc):
        ax.add_patch(Polygon([(cx - w / 2, cy), (cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2)],
                             closed=True, fc=fc, ec=INK, lw=1.0))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)

    # column A (hardware + bootloader start)
    A, aw = 3.0, 5.6
    steps_a = [
        (11.3, 0.8, "Power applied", C_HW),
        (9.85, 1.2, "POR/BOR hold until V$_{DD}$ > 1.7 V\n(≈ 1–3 ms incl. supply ramp)", C_HW),
        (8.2, 1.3, "Core fetches initial SP from\n0x0000 0000 and the reset\nvector (PC) from 0x0000 0004", C_HW),
        (6.55, 1.3, "Immutable bootloader\n(write-protected Flash):\nminimal clock init, 16 MHz RC", C_BL),
    ]
    for cy, hh, t, c in steps_a:
        box(ax, A - aw / 2, cy - hh / 2, aw, hh, t, fc=c, fontsize=fs)
    for (c1, h1, _, _), (c2, h2, _, _) in zip(steps_a[:-1], steps_a[1:]):
        arrow(ax, A, c1 - h1 / 2, A, c2 + h2 / 2)
    diamond(A, 4.55, 4.0, 1.6, "Update flag\nset?", C_BL)
    arrow(ax, A, 6.55 - 0.65, A, 4.55 + 0.8)
    box(ax, A - 1.9, 1.6, 3.8, 1.1, "Install update\n(Section 25.9)", fc=C_BL, fontsize=fs)
    arrow(ax, A, 4.55 - 0.8, A, 2.7)
    ax.text(A + 0.15, 3.35, "yes", fontsize=fs, ha="left", va="center")

    # column B (verify, jump, application)
    B, bw = 10.1, 6.4
    gx = 6.35  # gutter
    # "no" from diamond and the install path join in the gutter and climb to the verify box
    line(ax, [(A + 2.0, 4.55), (gx, 4.55)])
    ax.text(A + 2.1, 4.65, "no", fontsize=fs, ha="left", va="bottom")
    line(ax, [(A + 1.9, 2.15), (gx, 2.15), (gx, 11.25)])
    line(ax, [(gx, 11.25), (B - bw / 2, 11.25)], arrow_end=True)

    vy = 11.25
    box(ax, B - bw / 2, vy - 0.95, bw, 1.9,
        "Verify application image:\nSHA-256 over 256 KB (≈ 0.2 s software,\na few ms with hash accelerator)\n"
        "+ ECDSA P-256 signature check", fc=C_BL, fontsize=fs)
    diamond(B, 8.75, 3.6, 1.5, "Signature\nvalid?", C_BL)
    arrow(ax, B, vy - 0.95, B, 8.75 + 0.75)
    box(ax, 13.7, 8.25, 3.2, 1.0, "Recovery mode /\nprevious image", fc=tint(RED, "25"), fontsize=fs)
    arrow(ax, B + 1.8, 8.75, 13.7, 8.75)
    ax.text(B + 1.9, 8.85, "no", fontsize=fs, ha="left", va="bottom")
    box(ax, B - bw / 2, 6.45, bw, 1.0, "Set VTOR, load application SP\nand reset vector, jump", fc=C_BL,
        fontsize=fs)
    arrow(ax, B, 8.75 - 0.75, B, 7.45)
    ax.text(B + 0.15, 7.72, "yes", fontsize=fs, ha="left", va="center")
    box(ax, B - bw / 2, 3.45, bw, 2.35,
        "Application Reset_Handler:\nSystemInit (HSE crystal start 1–2 ms,\nPLL lock ≈ 0.1–0.3 ms, "
        "Flash wait states),\ncopy .data, zero .bss,\nC++ constructors", fc=C_APP, fontsize=fs)
    arrow(ax, B, 6.45, B, 5.8)
    box(ax, B - bw / 2, 1.85, bw, 1.0, "main: driver init, RTOS start", fc=C_APP, fontsize=fs)
    arrow(ax, B, 3.45, B, 2.85)
    box(ax, B - 1.5, 0.3, 3.0, 0.8, "Running", fc=tint(GREEN, "40"), fontsize=8)
    arrow(ax, B, 1.85, B, 1.1)

    # side annotation
    ax.text(15.3, 4.9, "Total cold boot\n≈ 50–300 ms,\ndominated by\nsignature check\nand peripheral\ninit",
            ha="center", va="center", fontsize=7.5, style="italic",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=GREY, lw=0.8))
    # legend
    for k, (c, t) in enumerate([(C_HW, "hardware"), (C_BL, "bootloader"), (C_APP, "application")]):
        ax.add_patch(Rectangle((13.65, 2.3 - k * 0.55), 0.45, 0.35, fc=c, ec=INK, lw=0.6))
        ax.text(14.25, 2.47 - k * 0.55, t, fontsize=7.5, va="center")
    save(fig, "25", "fig-25-5-boot-flow")


# ----------------------------------------------------------------------------
# Figure 25.6 — A/B slots and update state machine
# ----------------------------------------------------------------------------
def fig_ab_update():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7.5

    # ---- Flash bar (1 MB, to scale) ----
    x0, total_w = 0.5, 16.0
    scale = total_w / 1024
    parts = [(32, tint(GREY, "50")), (448, tint(BLUE, "30")), (448, tint(ORANGE, "30")),
             (32, tint(PINK, "40")), (64, tint(GREEN, "35"))]
    labels = [None, "slot 0 — image v1.4", "slot 1 — downloaded v1.5", None, None]
    by0, bh = 10.25, 0.85
    x = x0
    pos = []
    for (size, c), lab in zip(parts, labels):
        w = size * scale
        ax.add_patch(Rectangle((x, by0), w, bh, fc=c, ec=INK, lw=1.0))
        pos.append((x, w, size))
        if lab:
            hw = 1.4
            ax.add_patch(Rectangle((x, by0), hw, bh, fc="white", ec=INK, lw=0.8, hatch="////"))
            ax.text(x + hw / 2, by0 + bh / 2, "header", ha="center", va="center", fontsize=7,
                    bbox=dict(fc="white", ec="none", pad=0.5))
            ax.text(x + hw + (w - hw) / 2, by0 + bh / 2, lab, ha="center", va="center", fontsize=8)
            ax.text(x + w / 2, by0 + bh + 0.1, f"{size} KB", ha="center", va="bottom", fontsize=7.5)
        x += w
    ax.annotate("bootloader 32 KB", xy=(pos[0][0] + pos[0][1] / 2, by0), xytext=(0.3, 9.45), fontsize=7.5,
                va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))
    ax.annotate("scratch 32 KB", xy=(pos[3][0] + pos[3][1] / 2, by0), xytext=(13.6, 9.45), fontsize=7.5,
                ha="right", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))
    ax.annotate("settings 64 KB", xy=(pos[4][0] + pos[4][1] / 2, by0), xytext=(16.8, 9.45), fontsize=7.5,
                ha="right", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))
    ax.text(x0, 11.75, "Flash 1 MB", fontsize=9, weight="bold", va="bottom")
    ax.text(3.6, 11.75, "image header: magic | version | size | SHA-256 | signature, followed by code",
            fontsize=7.5, va="bottom", style="italic")

    # ---- state machine ----
    sw_, sh_ = 3.3, 1.45
    X1, X2, X3 = 2.2, 8.5, 14.8
    Y1, Y2, Y3 = 7.55, 4.65, 1.75
    S = {
        "RUN": (X1, Y1, "RUNNING v1.4", "normal operation"),
        "DL": (X2, Y1, "DOWNLOADING", "writing slot 1,\nresumable"),
        "VER": (X3, Y1, "VERIFIED", "hash + signature\nchecked by app"),
        "PEND": (X3, Y2, "PENDING", "update flag set,\nreboot"),
        "SWAP": (X3, Y3, "SWAPPING", "bootloader swaps\nslots via scratch"),
        "TRIAL": (X2, Y3, "TRIAL v1.5", "running,\nnot yet confirmed"),
        "CONF": (X1, Y3, "CONFIRMED v1.5", "security counter\nraised"),
        "REV": (X1, Y2, "REVERTING", "bootloader\nswaps back"),
    }
    cols = {"RUN": GREEN, "DL": BLUE, "VER": BLUE, "PEND": BLUE, "SWAP": ORANGE, "TRIAL": ORANGE,
            "CONF": GREEN, "REV": RED}
    for k, (cx, cy, name, desc) in S.items():
        ax.add_patch(FancyBboxPatch((cx - sw_ / 2, cy - sh_ / 2), sw_, sh_,
                                    boxstyle="round,pad=0.02,rounding_size=0.45",
                                    fc=tint(cols[k], "22"), ec=cols[k], lw=1.4))
        ax.text(cx, cy + sh_ / 2 - 0.3, name, ha="center", va="center", fontsize=7.5, weight="bold")
        ax.text(cx, cy - 0.2, desc, ha="center", va="center", fontsize=7)

    def tr(p0, p1, text, rad=0.0, toff=(0, 0), color=INK, ha="center"):
        ax.add_patch(FancyArrowPatch(p0, p1, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                                     mutation_scale=11, color=color, lw=1.1, shrinkA=1, shrinkB=1))
        mx, my = (p0[0] + p1[0]) / 2 + toff[0], (p0[1] + p1[1]) / 2 + toff[1]
        ax.text(mx, my, text, ha=ha, va="center", fontsize=fs, color=color)

    hw, hh = sw_ / 2, sh_ / 2
    tr((X1 + hw, Y1), (X2 - hw, Y1), "new image\noffered", toff=(0, 0.45))
    tr((X2 + hw, Y1), (X3 - hw, Y1), "download\ncomplete", toff=(0, 0.45))
    tr((X3, Y1 - hh), (X3, Y2 + hh), "set flag", toff=(0.15, 0), ha="left")
    tr((X3, Y2 - hh), (X3, Y3 + hh), "reboot", toff=(0.15, 0), ha="left")
    tr((X3 - hw, Y3), (X2 + hw, Y3), "swap done", toff=(0, 0.3))
    tr((X2 - hw, Y3), (X1 + hw, Y3), "self-test OK +\nserver contact", toff=(0, 0.5))
    tr((X1, Y2 + hh), (X1, Y1 - hh), "swap back\ndone", toff=(0.15, 0), ha="left")
    # TRIAL -> REVERTING (diagonal)
    tr((X2 - 0.9, Y3 + hh), (X1 + hw, Y2 - 0.25), "watchdog reset or\nreboot without\nconfirmation",
       toff=(1.75, -0.05), color=RED, ha="left")
    # VERIFIED -> RUNNING on verify fail, curving through the middle
    tr((X3 - hw, Y1 - 0.35), (X1 + hw, Y1 - 0.35), "verify fail", rad=-0.28, toff=(0, -1.78), color=RED)
    # power-loss self loop below SWAPPING
    ax.add_patch(FancyArrowPatch((X3 + 0.7, Y3 - hh), (X3 - 0.7, Y3 - hh), connectionstyle="arc3,rad=-0.9",
                                 arrowstyle="-|>", mutation_scale=9, color=GREY, lw=1.0))
    ax.text(X3 + 1.25, 0.35, "power loss: resume from\nprogress in trailer", ha="left", va="center",
            fontsize=6.8, color=GREY)
    save(fig, "25", "fig-25-6-ab-update-states")

if __name__ == "__main__":
    fig_block_diagram()
    fig_memory_layout()
    fig_current_profile()
    fig_architectures_timing()
    fig_boot_flow()
    fig_ab_update()
