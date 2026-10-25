"""Figures for Chapter 17 — Microprocessors and Microcontrollers.

Run from the repository root:  python figures/scripts/ch17.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch, Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, YELLOW = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4]
CORE_FC = "#E3F2E6"
BUS_FC = "#FBE7D3"
MEM_FC = "#DCEBF7"
PER_FC = "#F1EAF6"
CLK_FC = "#FFF4D6"


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def wire(ax, pts, color=INK, lw=1.2, ls="-", **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt",
            solid_joinstyle="miter", **kw)


def wire_arrow(ax, pts, color=INK, lw=1.2, ls="-", ms=9, both=False):
    if len(pts) > 2:
        wire(ax, pts[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def dot(ax, x, y, color=INK, ms=3.5):
    ax.plot([x], [y], "o", ms=ms, color=color, zorder=5)


def rect(ax, x, y, w, h, fc="white", ec=INK, lw=1.0, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))


def tbox(ax, x, y, w, h, title, body="", fc="#EEF3F8", fs=8, fsb=6.6, ec=INK):
    """Rounded box with a bold title line and a smaller body text below it."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=fc, ec=ec, lw=1.0))
    if body:
        ax.text(x + w / 2, y + h - 0.12, title, ha="center", va="top", fontsize=fs, weight="bold")
        ax.text(x + w / 2, y + (h - 0.12 - fs / 30) / 2, body, ha="center", va="center", fontsize=fsb,
                linespacing=1.15)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs)


# ----------------------------------------------------------------------------
def fig_17_1():
    """Internal organisation of an STM32F4-class Cortex-M4 MCU."""
    fig, ax = schematic(6.8, 5.6, xlim=(0, 14.0), ylim=(-0.1, 11.4))
    # core
    ax.add_patch(FancyBboxPatch((0.2, 8.1), 4.6, 3.1, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=CORE_FC, ec=INK, lw=1.1))
    ax.text(2.5, 10.9, "Cortex-M4 core", ha="center", va="center", fontsize=9, weight="bold")
    for (x, y, t) in [(0.4, 9.6, "FPU\nsingle precision"), (2.6, 9.6, "NVIC\n82 IRQs"),
                      (0.4, 8.35, "SysTick\n24-bit timer"), (2.6, 8.35, "Debug\nSWD")]:
        box(ax, x, y, 2.0, 1.0, t, fc="white", fontsize=6.5)
    # bus matrix
    ym, hm = 5.9, 0.9
    box(ax, 0.2, ym, 13.6, hm, "", fc=BUS_FC)
    ax.text(7.0, ym + hm / 2, "Multi-layer AHB bus matrix  (168 MHz, 32 bit)", ha="center",
            va="center", fontsize=9)
    # core ports
    ports = [(0.75, "S-bus\n(System)"), (1.95, "I-code"), (3.15, "D-code")]
    for x, t in ports:
        wire_arrow(ax, [(x, 8.1), (x, ym + hm)], ms=8)
        ax.text(x + 0.07, 7.82, t, fontsize=6.3, va="center", ha="left")
    # CCM on D-bus only
    wire(ax, [(3.15, 7.25), (3.8, 7.25)])
    dot(ax, 3.15, 7.25)
    box(ax, 3.8, 6.95, 1.55, 0.65, "CCM RAM\n64 KiB", fc=MEM_FC, fontsize=6.6)
    ax.text(5.42, 7.27, "D-bus\nonly", fontsize=6, ha="left", va="center", style="italic")
    # other initiators
    inits = [(5.6, "DMA1", "8 streams"), (7.7, "DMA2", "8 streams"), (9.8, "Ethernet MAC", "DMA"),
             (11.9, "USB OTG HS", "DMA")]
    for x, t, b in inits:
        box(ax, x, 8.6, 1.9, 1.0, f"{t}\n{b}", fc=BUS_FC, fontsize=7)
        wire_arrow(ax, [(x + 0.95, 8.6), (x + 0.95, ym + hm)], ms=8)
    ax.text(9.75, 9.85, "bus-matrix initiators (masters)", ha="center", va="bottom", fontsize=7,
            style="italic", color="#555555")
    # targets
    yt, ht = 3.75, 1.55
    tg = [(0.2, 2.6, "Flash 1 MiB", "ART accelerator:\nprefetch +\n64 × 128-bit cache", MEM_FC),
          (2.95, 1.45, "SRAM1", "112 KiB", MEM_FC),
          (4.55, 1.45, "SRAM2", "16 KiB", MEM_FC),
          (6.15, 1.5, "FSMC", "external\nmemory", MEM_FC),
          (7.8, 2.2, "AHB1", "GPIOA–GPIOI,\nRCC, CRC, DMA", PER_FC),
          (10.15, 1.6, "AHB2", "USB FS,\nRNG", PER_FC),
          (11.9, 1.9, "AHB/APB", "bridges", PER_FC)]
    for x, w, t, b, c in tg:
        tbox(ax, x, yt, w, ht, t, b, fc=c, fs=7.5, fsb=6.4)
        wire_arrow(ax, [(x + w / 2, ym), (x + w / 2, yt + ht)], ms=8, both=True)
    # APB buses
    ya, ha = 1.95, 1.45
    tbox(ax, 3.0, ya, 5.3, ha, "APB2  (84 MHz)", "TIM1, TIM8, USART1, USART6,\nSPI1, ADC1–3", fc=PER_FC,
         fs=7.5, fsb=6.6)
    tbox(ax, 8.5, ya, 5.3, ha, "APB1  (42 MHz)",
         "TIM2–TIM7, USART2–3, UART4–5,\nSPI2–3, I²C1–3, CAN1–2, DAC", fc=PER_FC, fs=7.5, fsb=6.6)
    wire_arrow(ax, [(13.3, yt), (13.3, ya + ha)], ms=8)
    wire(ax, [(12.4, yt), (12.4, 3.6), (5.65, 3.6)])
    wire_arrow(ax, [(5.65, 3.6), (5.65, ya + ha)], ms=8)
    # clock tree
    yc = 0.2
    ax.add_patch(FancyBboxPatch((0.2, yc - 0.1), 13.6, 1.55, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc=CLK_FC, ec=INK, lw=1.0))
    ax.text(0.35, yc + 1.25, "Clock tree (RCC)", fontsize=7.5, weight="bold", va="center")
    cb = [(0.4, 1.9, "HSE crystal\n8 MHz"), (2.8, 1.5, "PLL"), (4.8, 2.1, "SYSCLK\n168 MHz"),
          (7.4, 1.9, "AHB  /1\n168 MHz"), (9.7, 1.9, "APB2  /2\n84 MHz"), (12.0, 1.7, "APB1  /4\n42 MHz")]
    for x, w, t in cb:
        box(ax, x, yc, w, 0.85, t, fc="white", fontsize=6.8)
    for (x1, w1, _), (x2, _, _) in zip(cb[:3], cb[1:4]):
        wire_arrow(ax, [(x1 + w1, yc + 0.42), (x2, yc + 0.42)], ms=7)
    wire(ax, [(6.9, yc + 0.42), (7.1, yc + 0.42), (7.1, 1.27), (10.65, 1.27)])
    wire_arrow(ax, [(10.65, 1.27), (10.65, yc + 0.85)], ms=6)
    wire(ax, [(10.65, 1.27), (12.85, 1.27)])
    wire_arrow(ax, [(12.85, 1.27), (12.85, yc + 0.85)], ms=6)
    dot(ax, 7.1, yc + 0.42)
    dot(ax, 10.65, 1.27, ms=2.8)
    ax.text(3.0, 1.3, "", fontsize=6)
    save(fig, "17", "fig-17-1-cortex-m4-mcu-block")


# ----------------------------------------------------------------------------
def fig_17_2():
    """Cortex-M memory map with STM32F4 placements."""
    fig, ax = schematic(6.8, 6.0, xlim=(0, 14.2), ylim=(-0.3, 12.3))
    x0, x1 = 1.55, 3.85
    regs = [  # name, base, height, colour
        ("Code", "0x0000_0000", 2.9, MEM_FC),
        ("SRAM", "0x2000_0000", 1.5, MEM_FC),
        ("Peripheral", "0x4000_0000", 2.1, PER_FC),
        ("External RAM", "0x6000_0000", 1.5, "#EFEFEF"),
        ("External device", "0xA000_0000", 1.5, "#EFEFEF"),
        ("Private periph.\nbus (PPB)", "0xE000_0000", 0.9, CORE_FC),
        ("Vendor", "0xE010_0000", 0.7, "#EFEFEF"),
    ]
    y = 0.2
    spans = {}
    for name, base, h, c in regs:
        rect(ax, x0, y, x1 - x0, h, fc=c)
        ax.text((x0 + x1) / 2, y + h / 2, name, ha="center", va="center", fontsize=7)
        ax.text(x0 - 0.08, y, base, ha="right", va="center", fontsize=6.3, family="DejaVu Sans Mono")
        spans[name.split("\n")[0]] = (y, y + h)
        y += h
    ax.text(x0 - 0.08, y, "0xFFFF_FFFF", ha="right", va="center", fontsize=6.3, family="DejaVu Sans Mono")
    ax.text((x0 + x1) / 2, y + 0.15, "4 GiB address space\n(not to scale)", ha="center", va="bottom",
            fontsize=6.5)

    mono = dict(family="DejaVu Sans Mono", fontsize=6.0)

    def callout(region, bx, by, bw, bh, title, rows, fc):
        y0, y1 = spans[region]
        ax.add_patch(Polygon([(x1, y0), (x1, y1), (bx, by + bh), (bx, by)], closed=True,
                             fc=fc, ec="none", alpha=0.7, zorder=0))
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc="white", ec=INK, lw=0.9))
        ax.text(bx + 0.12, by + bh - 0.1, title, fontsize=7.3, weight="bold", va="top")
        n = len(rows)
        top = by + bh - 0.62
        step = (top - by - 0.2) / max(n - 1, 1) if n > 1 else 0
        for i, (addr, txt) in enumerate(rows):
            yy = top - i * step
            ax.text(bx + 0.15, yy, addr, va="center", **mono)
            ax.text(bx + 1.75, yy, txt, va="center", fontsize=6.4)

    # code callout with vector table
    callout("Code", 4.6, 0.0, 5.55, 3.3, "Code region (STM32F4)",
            [("0x1FFF_0000", "system memory (bootloader)"),
             ("0x1000_0000", "CCM RAM 64 KiB (data only)"),
             ("0x080F_FFFF", "end of 1 MiB flash"),
             ("0x0800_0000", "flash: vector table first"),
             ("0x0000_0000", "boot alias (flash/ROM/SRAM)")], MEM_FC)
    vx, vy = 10.3, 0.0
    ax.add_patch(FancyBboxPatch((vx, vy), 3.75, 3.3, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="#F7FBFE", ec=INK, lw=0.9))
    ax.text(vx + 0.12, vy + 3.2, "Vector table at 0x0800_0000", fontsize=6.2, weight="bold", va="top")
    vt = [("0x000", "initial MSP"), ("0x004", "Reset"), ("0x008", "NMI"), ("0x00C", "HardFault"),
          ("…", "MemManage … SysTick"[10:]), ("0x040", "IRQ0 (WWDG)"), ("…", "… IRQ81")]
    for i, (a, t) in enumerate(vt):
        yy = vy + 2.68 - i * 0.38
        rect(ax, vx + 0.12, yy - 0.17, 3.5, 0.34, fc="white", lw=0.6)
        ax.text(vx + 0.2, yy, a, va="center", **mono)
        ax.text(vx + 0.95, yy, t, va="center", fontsize=6.3)
    yfl = 2.68 - 3 * (2.68 - 0.2) / 4
    wire(ax, [(9.95, yfl), (vx, yfl)], color="#777777", ls=(0, (2, 2)), lw=0.9)

    callout("SRAM", 4.6, 3.65, 5.55, 1.75, "SRAM region",
            [("0x2000_0000", "SRAM1 112 KiB"), ("0x2001_C000", "SRAM2 16 KiB"),
             ("0x2200_0000", "bit-band alias (32 MiB)")], MEM_FC)
    callout("Peripheral", 4.6, 5.75, 9.45, 2.6, "Peripheral region",
            [("0x4000_0000", "APB1 (TIM2–7, USART2–3, I²C, SPI2–3, CAN, DAC)"),
             ("0x4001_0000", "APB2 (TIM1 0x4001_0000, USART1 0x4001_1000, ADC)"),
             ("0x4002_0000", "AHB1: GPIOA 0x4002_0000 (ODR +0x14, BSRR +0x18)"),
             ("0x4002_3800", "RCC (reset and clock control)"),
             ("0x4200_0000", "bit-band alias (PA5 of ODR → 0x4240_0294)")], PER_FC)
    callout("Private periph.", 4.6, 8.75, 9.45, 1.95, "Private peripheral bus (core)",
            [("0xE000_E010", "SysTick"), ("0xE000_E100", "NVIC (ISER, … IPR at 0xE000_E400)"),
             ("0xE000_ED00", "System Control Block (VTOR, AIRCR, …)")], CORE_FC)
    save(fig, "17", "fig-17-2-cortex-m-memory-map")


# ----------------------------------------------------------------------------
def fig_17_3():
    """Cortex-M4 exception timing: entry, nesting and tail-chaining."""
    f = 168e6
    tA, tB, tC = 40, 110, 236
    st, ust, tc = 12, 10, 6
    a1 = (tA + st, tB)                # handler A first part
    sB = (tB, tB + st)
    hB = (tB + st, 200)
    uB = (200, 200 + ust)
    a2 = (210, 272)
    tch = (272, 272 + tc)
    hC = (278, 352)
    uC = (352, 352 + ust)
    T = 410

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    rows = {"IRQ A (prio 2)": 5.0, "IRQ B (prio 1)": 4.0, "IRQ C (prio 2)": 3.0,
            "core": 1.85, "stack depth": 0.0}
    h = 0.55
    # request lines: high from assertion until the handler starts (pending)
    for name, t0, t1, c in [("IRQ A (prio 2)", tA, tA + st, BLUE), ("IRQ B (prio 1)", tB, tB + st, ORANGE),
                            ("IRQ C (prio 2)", tC, tch[1], GREEN)]:
        y = rows[name]
        ax.plot([0, t0, t0, t1, t1, T], [y, y, y + h, y + h, y, y], color=c, lw=1.5)
        ax.text(t0 - 2, y + h + 0.05, "request", fontsize=6.3, ha="right", va="bottom", color=c)
    ax.text((tC + tch[1]) / 2, rows["IRQ C (prio 2)"] + h / 2, "pending", fontsize=6.3, color=GREEN,
            ha="center", va="center")
    ax.text(tch[1] + 5, rows["IRQ C (prio 2)"] + h / 2, "same priority as A: waits, then tail-chains",
            fontsize=6.3, color=GREEN, va="center")
    ax.text(tB + st + 5, rows["IRQ B (prio 1)"] + h / 2, "higher priority: preempts handler A",
            fontsize=6.3, color=ORANGE, va="center")
    # core activity
    yc = rows["core"] - 0.4
    segs = [((0, tA), "thread", "#E6E6E6"), ((tA, tA + st), "", "#555555"), (a1, "handler A", BLUE + "55"),
            (sB, "", "#555555"), (hB, "handler B (nested)", ORANGE + "66"), (uB, "", "#999999"),
            (a2, "handler A", BLUE + "55"), (tch, "", GREEN), (hC, "handler C", GREEN + "55"),
            (uC, "", "#999999"), ((uC[1], T), "thread", "#E6E6E6")]
    for (t0, t1), lab, c in segs:
        ax.add_patch(Rectangle((t0, yc), t1 - t0, 0.8, fc=c, ec=INK, lw=0.7))
        if lab:
            ax.text((t0 + t1) / 2, yc + 0.4, lab, ha="center", va="center", fontsize=6.8)
    # labels for the short blocks
    def tag(t0, t1, txt, y, col=INK):
        ax.annotate(txt, xy=((t0 + t1) / 2, yc + 0.8), xytext=((t0 + t1) / 2, y), fontsize=6.3,
                    ha="center", va="bottom", color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.7))
    tag(tA, tA + st, "stack 12", yc + 1.2)
    tag(*sB, "stack 12", yc + 1.2)
    tag(*uB, "unstack 10", yc + 1.2)
    tag(*tch, f"tail-chain 6 cycles = {6 / f * 1e9:.0f} ns", yc + 1.2, GREEN)
    tag(*uC, "unstack 10", yc + 1.2)
    # stack depth
    ys = rows["stack depth"]
    tt = [0, tA, tA + st, tB, tB + st, uB[0], uB[1], uC[0], uC[1], T]
    dd = [0, 0, 8, 8, 16, 16, 8, 8, 0, 0]
    ax.plot(tt, [ys + d / 16 * 1.1 for d in dd], color=PINK, lw=1.6)
    for d in (8, 16):
        ax.text(T + 3, ys + d / 16 * 1.1, f"{d} words", fontsize=6.3, va="center", color=PINK)
    ax.axhline(ys, color=GRID, lw=0.6, zorder=0)
    # latency dims
    ax.annotate("", xy=(tA + st, 5.95), xytext=(tA, 5.95),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, mutation_scale=6, shrinkA=0, shrinkB=0))
    ax.text(tA + st + 4, 5.95, f"entry latency 12 cycles = {12 / f * 1e9:.0f} ns", fontsize=7,
            va="center")
    for t in (tA, tB, tC, tch[0]):
        ax.axvline(t, color=GRID, lw=0.6, ls=(0, (3, 3)), zorder=0)
    ax.set_yticks(list(rows.values()))
    ax.set_yticklabels(list(rows.keys()), fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, T)
    ax.set_ylim(-0.35, 6.3)
    ax.set_xlabel("core clock cycles at 168 MHz (1 cycle = 5.95 ns)")
    sec = ax.secondary_xaxis("top", functions=(lambda c: c / f * 1e6, lambda u: u * f / 1e6))
    sec.set_xlabel("time (µs)", fontsize=8)
    sec.tick_params(labelsize=8)
    save(fig, "17", "fig-17-3-nvic-entry-tailchain")


# ----------------------------------------------------------------------------
def fig_17_4():
    """Timer structure and centre-aligned complementary PWM with dead time."""
    fig = plt.figure(figsize=(6.8, 5.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.85, 2.3], hspace=0.08)
    axb = fig.add_subplot(gs[0])
    axb.set_xlim(-0.15, 14.1)
    axb.set_ylim(0, 3.2)
    axb.axis("off")
    # block diagram (row 1: clock path, row 2: reload, update event, pins)
    yr, hr = 1.95, 1.1
    box(axb, 0.0, yr, 1.7, hr, "timer clock\n168 MHz", fc=CLK_FC, fontsize=7.5)
    box(axb, 2.1, yr, 1.7, hr, "prescaler\nPSC = 0", fontsize=7.5)
    box(axb, 4.2, yr, 2.2, hr, "16-bit up/down\ncounter CNT", fontsize=7.5)
    box(axb, 6.8, yr, 2.3, hr, "comparator\nCNT < CCR1\n(CCR1 = 2100)", fontsize=7.2)
    box(axb, 9.5, yr, 1.5, hr, "output\nlogic", fontsize=7.5)
    box(axb, 11.4, yr, 2.6, hr, "dead-time gen.\nDTG = 0x94\n(168 ticks, 1.0 µs)", fontsize=7)
    for (xa, xb_) in [(1.7, 2.1), (3.8, 4.2), (6.4, 6.8), (9.1, 9.5), (11.0, 11.4)]:
        arrow(axb, xa, yr + hr / 2, xb_, yr + hr / 2)
    box(axb, 4.2, 0.1, 2.2, 1.0, "auto-reload\nARR = 4200", fontsize=7.5)
    arrow(axb, 5.3, 1.1, 5.3, yr)
    wire(axb, [(6.0, yr), (6.0, 1.55), (7.4, 1.55)], color=ORANGE)
    wire_arrow(axb, [(7.4, 1.55), (7.4, 1.1)], color=ORANGE, ms=7)
    axb.text(7.0, 0.95, "update event at each counter\npeak (RCR = 1): interrupt\nand ADC trigger",
             fontsize=6.8, ha="left", va="top", color=ORANGE)
    for xo, lab in [(12.1, "CH1"), (13.3, "CH1N")]:
        wire_arrow(axb, [(xo, yr), (xo, 1.05)], ms=7)
        axb.text(xo, 0.95, lab, fontsize=7.5, ha="center", va="top")
    axb.text(12.7, 0.45, "pins to gate driver", fontsize=6.5, ha="center", va="top")

    # waveforms
    ax = fig.add_subplot(gs[1])
    t = np.linspace(0, 100, 20001)                    # µs
    Tp, arr, ccr, dt = 50.0, 4200, 2100, 1.0
    ph = np.mod(t, Tp)
    cnt = np.where(ph < Tp / 2, ph / (Tp / 2) * arr, (Tp - ph) / (Tp / 2) * arr)
    ref = (cnt < ccr).astype(float)
    # dead time: delay rising edges by dt
    n_dt = int(round(dt / (t[1] - t[0])))
    def delay_rise(sig):
        out = sig.copy()
        rises = np.where(np.diff(sig) > 0)[0] + 1
        for r in rises:
            out[r:r + n_dt] = 0
        return out
    ch1 = delay_rise(ref)
    ch1n = delay_rise(1 - ref)
    ch1n[:n_dt] = 1 - ref[:n_dt]                      # trace starts mid-state (no edge at t = 0)
    yc0, sc = 3.2, 2.4 / arr
    ax.plot(t, yc0 + cnt * sc, color=BLUE, lw=1.6)
    ax.axhline(yc0 + ccr * sc, color=BLUE, ls=(0, (4, 3)), lw=0.9)
    ax.text(100.5, yc0 + ccr * sc, "CCR1 = 2100", fontsize=7, va="center", color=BLUE)
    ax.text(100.5, yc0 + arr * sc, "ARR = 4200", fontsize=7, va="center", color=BLUE)
    ax.text(100.5, yc0, "0", fontsize=7, va="center", color=BLUE)
    y1, y2, hh = 1.7, 0.4, 0.8
    ax.plot(t, y1 + ch1 * hh, color=INK, lw=1.4)
    ax.plot(t, y2 + ch1n * hh, color=ORANGE, lw=1.4)
    # shade dead-time gaps
    both_low = (ch1 == 0) & (ch1n == 0)
    edges = np.flatnonzero(np.diff(both_low.astype(int)))
    starts = edges[::2] + 1 if not both_low[0] else np.r_[0, edges[1::2] + 1]
    for i in range(0, len(edges) - 1, 2):
        ta, tb = t[edges[i] + 1], t[edges[i + 1]]
        ax.axvspan(ta, tb, ymin=0.03, ymax=0.47, color=PINK, alpha=0.35, lw=0)
    ax.annotate("dead time 1.0 µs\n(both off)", xy=(12.5 + 0.5, 1.45), xytext=(16, 2.9 - 0.15),
                fontsize=6.5, color=PINK, arrowprops=dict(arrowstyle="-", color=PINK, lw=0.7),
                va="center")
    # update events and ADC sampling at counter peaks
    for tp in (25, 75):
        ax.plot([tp], [yc0 + arr * sc + 0.25], "v", color=ORANGE, ms=6)
        ax.plot([tp, tp], [0.2, yc0 + arr * sc], color=GREEN, lw=0.9, ls=(0, (2, 2)))
        ax.plot([tp], [y2 + hh + 0.12], "o", color=GREEN, ms=4)
    ax.text(25, yc0 + arr * sc + 0.45, "update event", fontsize=6.5, ha="center", va="bottom",
            color=ORANGE)
    ax.text(75, yc0 + arr * sc + 0.45, "update event", fontsize=6.5, ha="center", va="bottom",
            color=ORANGE)
    ax.annotate("ADC samples low-side\nshunt current (CH1N on)", xy=(75, y2 + hh + 0.12),
                xytext=(84, y1 + 0.4), fontsize=6.5, color=GREEN, va="center",
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=0.7))
    ax.annotate("", xy=(50, -0.15), xytext=(0, -0.15),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, mutation_scale=7, shrinkA=0, shrinkB=0))
    ax.text(25, -0.2, "PWM period 50 µs (20 kHz) = 2 × ARR ticks", fontsize=7, ha="center", va="top")
    ax.set_yticks([yc0 + 1.2, y1 + hh / 2, y2 + hh / 2])
    ax.set_yticklabels(["CNT", "CH1", "CH1N"], fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.75, yc0 + arr * sc + 1.0)
    ax.set_xlabel("time (µs)")
    ax.set_xticks(np.arange(0, 101, 12.5))
    ax.set_xticklabels([f"{v:g}" for v in np.arange(0, 101, 12.5)])
    save(fig, "17", "fig-17-4-timer-pwm")


# ----------------------------------------------------------------------------
def fig_17_5():
    """Structure of a microcontroller GPIO pin."""
    fig, ax = schematic(6.8, 5.2, xlim=(-0.1, 14.4), ylim=(-0.2, 11.1))
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7, lw=1.1, unit=2)
    yv, yg, yo = 10.2, 4.6, 7.4             # VDD rail, VSS rail, output node
    xp, xr, xe, xpad = 9.0, 10.4, 11.6, 12.6
    # rails
    wire(ax, [(8.3, yv), (12.0, yv)], lw=1.4)
    wire(ax, [(8.3, yg), (12.0, yg)], lw=1.4)
    ax.text(8.25, yv, "VDD 3.3 V", ha="right", va="center", fontsize=7.5)
    ax.text(8.25, yg, "VSS", ha="right", va="center", fontsize=7.5)
    # output transistors
    pf = d.add(elm.PFet().reverse().at((xp, 9.45)).anchor("source"))
    nf = d.add(elm.NFet().reverse().at((xp, 6.9)).anchor("drain"))
    d.draw(show=False)
    wire(ax, [(xp, yv), (xp, 9.45)])
    wire(ax, [(xp, pf.absanchors["drain"].y), (xp, nf.absanchors["drain"].y)])
    wire(ax, [(xp, nf.absanchors["source"].y), (xp, yg)])
    ax.text(xp + 0.2, 8.7, "P-MOS", fontsize=7, va="center")
    ax.text(xp + 0.2, 6.15, "N-MOS", fontsize=7, va="center")
    dot(ax, xp, yo)
    dot(ax, xp, yv)
    dot(ax, xp, yg)
    # pull-up / pull-down
    d2 = schemdraw.Drawing(canvas=ax, show=False)
    d2.config(fontsize=7, lw=1.1, unit=1.4)
    d2.add(elm.Switch().down().at((xr, yv)).to((xr, 9.0)))
    d2.add(elm.Resistor().down().at((xr, 9.0)).to((xr, yo)))
    d2.add(elm.Resistor().down().at((xr, yo)).to((xr, 5.9)))
    d2.add(elm.Switch().down().at((xr, 5.9)).to((xr, yg)))
    d2.add(elm.Diode().up().at((xe, yo)).to((xe, yv)))
    d2.add(elm.Diode().up().at((xe, yg)).to((xe, yo)))
    d2.draw(show=False)
    for x in (xr, xe):
        dot(ax, x, yv)
        dot(ax, x, yg)
        dot(ax, x, yo)
    ax.text(xr + 0.2, 8.2, "≈40 kΩ", fontsize=5.9, ha="left", va="center")
    ax.text(xr + 0.2, 6.65, "≈40 kΩ", fontsize=5.9, ha="left", va="center")
    ax.text(xr - 0.25, 9.6, "PUPDR", fontsize=6.3, ha="right", va="center", color=BLUE)
    ax.text(xr - 0.25, 5.25, "PUPDR", fontsize=6.3, ha="right", va="center", color=BLUE)
    ax.text(xe + 0.25, 8.8, "ESD", fontsize=6.3, va="center")
    ax.text(xe + 0.25, 6.0, "ESD", fontsize=6.3, va="center")
    # pad and node
    wire(ax, [(xp, yo), (13.0, yo)])
    rect(ax, 13.0, yo - 0.5, 1.0, 1.0, fc="#D9D9D9", lw=1.2)
    ax.text(13.5, yo, "pad", ha="center", va="center", fontsize=7.5)
    dot(ax, xpad, yo)
    wire(ax, [(xpad, yo), (xpad, 0.7)])
    # input path
    yi = 2.6
    dot(ax, xpad, yi)
    wire(ax, [(xpad, yi), (10.75, yi)])
    ax.add_patch(Polygon([(10.75, yi - 0.55), (10.75, yi + 0.55), (9.75, yi)], closed=True,
                         fc="white", ec=INK, lw=1.1))
    hx, hy = 10.42, yi                        # hysteresis glyph
    wire(ax, [(hx - 0.2, hy - 0.15), (hx + 0.05, hy - 0.15), (hx + 0.05, hy + 0.15), (hx + 0.2, hy + 0.15)], lw=0.8)
    wire(ax, [(hx - 0.2, hy - 0.15), (hx - 0.05, hy - 0.15), (hx - 0.05, hy + 0.15), (hx + 0.2, hy + 0.15)], lw=0.8)
    ax.text(10.3, yi + 0.7, "Schmitt trigger (TTL)\n$V_{IL}$ = 0.3 $V_{DD}$, $V_{IH}$ = 0.7 $V_{DD}$",
            ha="center", va="bottom", fontsize=6.3)
    ax.text(10.3, yi - 0.65, "off in analog mode", ha="center", va="top", fontsize=6, style="italic")
    # synchroniser
    for i, xf in enumerate((7.7, 5.7)):
        rect(ax, xf, yi - 0.6, 1.1, 1.2)
        ax.text(xf + 0.9, yi + 0.25, "D", fontsize=6.5, ha="center", va="center")
        ax.text(xf + 0.2, yi + 0.25, "Q", fontsize=6.5, ha="center", va="center")
        ax.add_patch(Polygon([(xf + 0.42, yi - 0.6), (xf + 0.55, yi - 0.42), (xf + 0.68, yi - 0.6)],
                             closed=True, fc="none", ec=INK, lw=0.8))
        wire(ax, [(xf + 0.55, yi - 0.6), (xf + 0.55, 1.5)])
        dot(ax, xf + 0.55, 1.5, ms=2.8) if i == 0 else None
    wire_arrow(ax, [(9.75, yi), (8.8, yi)], ms=7)
    wire_arrow(ax, [(7.7, yi), (6.8, yi)], ms=7)
    wire(ax, [(6.25, 1.5), (9.0, 1.5)], color=GREEN)
    ax.text(9.05, 1.5, "AHB clock", fontsize=6.5, va="center", color=GREEN)
    ax.text(6.75, yi + 0.75, "2-flip-flop synchroniser", ha="center", va="bottom", fontsize=6.5)
    # IDR and AF input
    wire(ax, [(5.7, yi), (4.9, yi)])
    dot(ax, 4.9, yi)
    wire_arrow(ax, [(4.9, yi), (4.5, yi)], ms=7)
    box(ax, 2.2, yi - 0.4, 2.3, 0.8, "IDR (read)", fc=PER_FC, fontsize=7)
    wire(ax, [(4.9, yi), (4.9, 3.75)])
    wire_arrow(ax, [(4.9, 3.75), (4.5, 3.75)], ms=7)
    box(ax, 2.2, 3.35, 2.3, 0.8, "AF input\n(to peripheral)", fc=PER_FC, fontsize=6.6)
    # analog path
    ya = 0.7
    d3 = schemdraw.Drawing(canvas=ax, show=False)
    d3.config(fontsize=7, lw=1.1, unit=1.3)
    d3.add(elm.Switch().left().at((xpad, ya)).to((10.9, ya)))
    d3.draw(show=False)
    wire_arrow(ax, [(10.9, ya), (9.9, ya)], ms=7)
    ax.text(9.8, ya, "to ADC (analog mode)", ha="right", va="center", fontsize=6.6)
    ax.text(11.75, ya + 0.35, "analog switch", ha="center", va="bottom", fontsize=6.2)

    # output side: BSRR, ODR, AF output, mux, output control
    box(ax, 0.0, 9.6, 2.5, 1.1, "BSRR\nbits 0–15 set,\n16–31 reset", fc=PER_FC, fontsize=6.5)
    box(ax, 0.0, 8.0, 2.5, 0.9, "ODR bit", fc=PER_FC, fontsize=7)
    box(ax, 0.0, 6.4, 2.5, 0.9, "AF output\n(peripheral)", fc=PER_FC, fontsize=6.6)
    wire_arrow(ax, [(1.25, 9.6), (1.25, 8.9)], ms=7)
    ax.text(1.35, 9.25, "atomic write path", fontsize=6, va="center", color=ORANGE)
    ax.add_patch(Polygon([(3.1, 6.55), (3.1, 8.75), (3.6, 8.45), (3.6, 6.85)], closed=True,
                         fc="white", ec=INK, lw=1.0))
    wire_arrow(ax, [(2.5, 8.45), (3.1, 8.45)], ms=6)
    wire_arrow(ax, [(2.5, 6.85), (3.1, 6.85)], ms=6)
    ax.text(3.35, 6.35, "MODER,\nAFR", fontsize=6.2, ha="center", va="top", color=BLUE)
    wire_arrow(ax, [(3.6, 7.65), (4.3, 7.65)], ms=7)
    ctl = (4.3, 5.75, 2.9, 3.75)
    rect(ax, *ctl, fc="#F4F4F4")
    ax.text(5.75, 9.2, "output control", ha="center", va="center", fontsize=7.5, weight="bold")
    ax.text(5.75, 8.0, "OTYPER:\npush-pull or\nopen-drain\n(P-MOS off)", ha="center", va="center",
            fontsize=6.3, color=BLUE)
    ax.text(5.75, 6.4, "OSPEEDR:\nslew rate", ha="center", va="center", fontsize=6.3, color=BLUE)
    gp, gn = pf.absanchors["gate"], nf.absanchors["gate"]
    wire(ax, [(7.2, gp.y), (gp.x, gp.y)])
    wire(ax, [(7.2, gn.y), (gn.x, gn.y)])
    save(fig, "17", "fig-17-5-gpio-pin-structure")


# ----------------------------------------------------------------------------
def fig_17_6():
    """Hardware-triggered peripheral chain of a motor-control MCU."""
    fig, ax = schematic(6.8, 4.3, xlim=(-0.1, 14.3), ylim=(1.0, 9.8))
    HW, SW = BLUE, ORANGE
    hwc, swc = "#DCEBF7", "#FBE7D3"
    dash = (0, (4, 2))
    # main chain (top lane)
    y0, h = 6.7, 1.6
    ym = y0 + 0.8
    tbox(ax, 0.1, y0, 2.2, h, "TIM1", "centre-aligned\nPWM 20 kHz", fc=hwc, fs=8, fsb=6.6)
    tbox(ax, 3.4, y0, 2.6, h, "ADC1 + ADC2", "injected: ia, ib, Vdc\n3 + 12 cycles\nat 21 MHz ≈ 0.7 µs",
         fc=hwc, fs=8, fsb=6.3)
    tbox(ax, 6.9, y0, 1.7, h, "EOC IRQ", "priority 0", fc=swc, fs=8, fsb=6.6)
    tbox(ax, 9.4, y0, 2.1, h, "CPU ISR", "current loop\n≈ 9 µs", fc=swc, fs=8, fsb=6.6)
    tbox(ax, 12.2, y0, 1.95, h, "CCR1–3", "preloaded;\ntake effect at\nnext update", fc=swc, fs=8,
         fsb=6.2)
    wire_arrow(ax, [(2.3, ym), (3.4, ym)], color=HW, lw=1.6)
    ax.text(2.85, ym + 0.12, "TRGO at\npeak", fontsize=6.2, ha="center", va="bottom", color=HW)
    ax.text(2.85, ym - 0.12, "every\n50 µs", fontsize=6.2, ha="center", va="top", color=HW)
    wire_arrow(ax, [(6.0, ym), (6.9, ym)], color=HW, lw=1.6)
    wire_arrow(ax, [(8.6, ym), (9.4, ym)], color=SW, lw=1.6, ls=dash)
    wire_arrow(ax, [(11.5, ym), (12.2, ym)], color=SW, lw=1.6, ls=dash)
    ax.text(11.85, ym + 0.12, "write", fontsize=6.2, ha="center", va="bottom", color=SW)
    # feedback CCR -> TIM1
    wire(ax, [(13.2, y0 + h), (13.2, 9.0), (1.2, 9.0)], color=HW, lw=1.4)
    wire_arrow(ax, [(1.2, 9.0), (1.2, y0 + h)], color=HW, lw=1.4)
    ax.text(7.2, 9.08, "preloaded CCR values load into TIM1 at the update event (hardware-timed)",
            fontsize=6.6, ha="center", va="bottom", color=HW)
    # PWM pins to power stage
    tbox(ax, 0.1, 4.4, 2.2, 1.3, "gate driver", "+ inverter", fc="#EFEFEF", fs=7.5, fsb=6.6)
    wire_arrow(ax, [(0.8, y0), (0.8, 5.7)], color=HW, lw=1.6)
    ax.text(0.72, 6.2, "PWM\npins", fontsize=6.2, va="center", ha="right", color=HW)
    # protection branch
    tbox(ax, 3.4, 4.4, 2.6, 1.3, "comparator", "on shunt", fc=hwc, fs=7.5, fsb=6.6)
    wire(ax, [(2.3, 4.75), (3.4, 4.75)], color=INK, lw=1.0)
    ax.text(2.85, 4.68, "shunt\nsignal", fontsize=5.8, ha="center", va="top")
    tbox(ax, 6.9, 4.4, 4.6, 1.3, "TIM1 break input", "outputs forced off in ≈ 0.5 µs\n(no CPU involved)",
         fc=hwc, fs=7.5, fsb=6.4)
    wire_arrow(ax, [(6.0, 5.05), (6.9, 5.05)], color=HW, lw=1.6)
    wire(ax, [(11.5, 5.05), (11.9, 5.05), (11.9, 6.15), (1.7, 6.15)], color=HW, lw=1.4)
    wire_arrow(ax, [(1.7, 6.15), (1.7, y0)], color=HW, lw=1.4)
    ax.text(7.0, 6.22, "break disables the PWM outputs", fontsize=6.2, color=HW, va="bottom")
    # UART DMA branch
    yb = 2.45
    tbox(ax, 0.1, yb, 2.2, 1.3, "UART RX", "protocol stream", fc=hwc, fs=7.5, fsb=6.4)
    tbox(ax, 3.4, yb, 2.6, 1.3, "DMA2 stream", "circular mode", fc=hwc, fs=7.5, fsb=6.6)
    tbox(ax, 6.9, yb, 2.4, 1.3, "SRAM", "circular buffer", fc=hwc, fs=7.5, fsb=6.6)
    tbox(ax, 10.1, yb, 4.05, 1.3, "half / full transfer IRQs", "priority 5 → protocol task", fc=swc,
         fs=7.5, fsb=6.6)
    wire_arrow(ax, [(2.3, yb + 0.65), (3.4, yb + 0.65)], color=HW, lw=1.6)
    wire_arrow(ax, [(6.0, yb + 0.65), (6.9, yb + 0.65)], color=HW, lw=1.6)
    wire_arrow(ax, [(9.3, yb + 0.65), (10.1, yb + 0.65)], color=SW, lw=1.6, ls=dash)
    # legend
    handles = [Line2D([], [], color=HW, lw=1.6, label="hardware-timed (jitter ≈ one peripheral clock)"),
               Line2D([], [], color=SW, lw=1.6, ls=dash,
                      label="through software (inherits interrupt latency)")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=2, fontsize=7)
    save(fig, "17", "fig-17-6-peripheral-chain")


if __name__ == "__main__":
    fig_17_1()
    fig_17_2()
    fig_17_3()
    fig_17_4()
    fig_17_5()
    fig_17_6()
