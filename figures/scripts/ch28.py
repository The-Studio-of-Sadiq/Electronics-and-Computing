"""Figures for Chapter 28 — Embedded System Design.

Run from the repository root:  python figures/scripts/ch28.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import (Rectangle, FancyBboxPatch, FancyArrowPatch,  # noqa: E402
                                Ellipse)

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"


def tint(c, a="30"):
    return c + a


def line(ax, pts, color=INK, lw=1.1, ls="-", arrow_end=False, both=False):
    """Poly-line through pts with optional arrow head(s) on the last segment."""
    xs, ys = zip(*pts)
    if not arrow_end and not both:
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt")
        return
    if len(pts) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                ls=ls, shrinkA=0, shrinkB=0, mutation_scale=10))


# ----------------------------------------------------------------------------
# Figure 28.1 — layered firmware architecture
# ----------------------------------------------------------------------------
def fig_28_1():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(-0.2, 12.3))
    layers = [
        ("Register\ndefinitions","CMSIS device header (STM32L4 class)\nvendor-generated, never edited", "#E8E8E8"),
        ("HAL", "GPIO · LPTIM · ADC · I2C · SPI · LPUART · DMA · RTC\nMCU's own peripherals", tint(BLUE, "22")),
        ("BSP", "pin map · clock tree 16 MHz HSI · radio on SPI1\nsensor on I2C1 · battery divider on ADC ch5", tint(BLUE, "38")),
        ("Device\ndrivers","SHT4x humidity sensor · SX1276 LoRa radio\nW25Q32 SPI NOR flash", tint(GREEN, "30")),
        ("Services", "LoRaWAN MAC · logger · power manager · CLI", tint(YELLOW, "40")),
        ("Application", "node state machine (app_fsm)", tint(ORANGE, "30")),
    ]
    down = [None,
            "register access",
            "HAL init / config calls",
            "i2c_bus_t, spi_bus_t (instances bound by BSP)",
            "flash_dev_t, radio_if",
            "lorawan_send(), log_append(), pwr_request()"]
    x0, w, h, g = 0.2, 13.2, 1.42, 0.6
    ys = [0.0 + i * (h + g) for i in range(6)]
    for (name, content, fc), y in zip(layers, ys):
        ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=fc, ec=INK, lw=1.0))
        ax.text(x0 + 0.25, y + h / 2, name, ha="left", va="center", fontsize=9, weight="bold")
        ax.text(x0 + 3.55, y + h / 2, content, ha="left", va="center", fontsize=8, linespacing=1.35)
    # inter-layer arrows
    for i in range(1, 6):
        ytop = ys[i]
        ybot = ys[i - 1] + h
        line(ax, [(3.0, ytop), (3.0, ybot)], arrow_end=True, lw=1.2)
        ax.text(3.2, (ytop + ybot) / 2, down[i], ha="left", va="center", fontsize=7.6,
                family="monospace" if i in (3, 4, 5) else None, color=INK)
        line(ax, [(13.0, ybot), (13.0, ytop)], arrow_end=True, ls=(0, (3, 2)), color=GREY, lw=1.1)
    ax.text(12.85, (ys[4] + ys[3] + h) / 2, "callbacks / events", ha="right", va="center",
            fontsize=7.6, color=GREY, style="italic")
    ax.text(12.85, (ys[2] + ys[1] + h) / 2, "completion callbacks", ha="right", va="center",
            fontsize=7.6, color=GREY, style="italic")
    # side bar spanning HAL and BSP
    sb_y0, sb_y1 = ys[1], ys[2] + h
    ax.add_patch(FancyBboxPatch((13.8, sb_y0), 3.0, sb_y1 - sb_y0,
                                boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="white", ec=PINK, lw=1.4, ls=(0, (4, 2))))
    ax.text(15.3, (sb_y0 + sb_y1) / 2, "host build:\nreplace with\nfakes for\nunit tests\n(fake_spi.c,\nfake_i2c.c)",
            ha="center", va="center", fontsize=8, color=PINK, linespacing=1.3)
    # legend
    ax.text(13.8, ys[5] + h / 2 + 0.25, "solid: calls down through\npublished interfaces", fontsize=7.4,
            ha="left", va="center")
    ax.text(13.8, ys[4] + h / 2, "dashed: information back\nup, never direct calls", fontsize=7.4,
            ha="left", va="center", color=GREY)
    save(fig, "28", "fig-28-1-firmware-layers")


# ----------------------------------------------------------------------------
# Figure 28.2 — node state machine
# ----------------------------------------------------------------------------
def fig_28_2():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    states = {
        "SLEEP": ((2.6, 6.6), "2 µA", tint(SKY, "40")),
        "MEASURE": ((8.5, 10.6), "2.5 mA", tint(GREEN, "35")),
        "SEND": ((14.4, 6.6), "45 mA", tint(ORANGE, "35")),
        "RX_WAIT": ((8.5, 1.9), "11.5 mA", tint(YELLOW, "45")),
        "FAULT": ((8.5, 6.6), "2 µA", "#F4C7C7"),
    }
    patches = {}
    rx, ry = 1.45, 1.05
    for name, ((x, y), cur, fc) in states.items():
        e = Ellipse((x, y), 2 * rx, 2 * ry, fc=fc, ec=INK, lw=1.3)
        ax.add_patch(e)
        patches[name] = e
        ax.text(x, y + 0.22, name, ha="center", va="center", fontsize=9, weight="bold")
        ax.text(x, y - 0.38, cur, ha="center", va="center", fontsize=8, color="#444444")

    def edge(a, b, rad=0.0, color=INK):
        p = FancyArrowPatch(posA=states[a][0], posB=states[b][0], patchA=patches[a], patchB=patches[b],
                            connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>", mutation_scale=12,
                            lw=1.2, color=color, shrinkA=1, shrinkB=1)
        ax.add_patch(p)

    fs = 7.3
    # initial
    ax.annotate("", xy=(2.6 - rx, 6.6), xytext=(0.15, 6.6),
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color=INK, mutation_scale=12))
    ax.plot([0.15], [6.6], "o", color=INK, ms=6)
    # SLEEP -> MEASURE
    edge("SLEEP", "MEASURE", rad=-0.42)
    ax.text(1.0, 10.9, "EV_RTC_ALARM /\nstart sensor,\narm 50 ms", fontsize=fs, ha="left", va="center")
    # MEASURE -> SLEEP (retry)
    edge("MEASURE", "SLEEP", rad=0.12, color=GREY)
    ax.text(8.35, 8.55, "EV_MEAS_FAIL |\nEV_TIMEOUT\n[retries ≤ 3] /\nlog error",
            fontsize=fs, ha="right", va="center", color="#444444")
    # MEASURE -> SEND
    edge("MEASURE", "SEND", rad=-0.25)
    ax.text(12.4, 10.9, "EV_MEAS_DONE /\nradio_send,\narm 3 s", fontsize=fs, ha="left", va="center")
    # MEASURE -> FAULT
    edge("MEASURE", "FAULT", rad=0.0, color=RED)
    ax.text(8.7, 8.45, "EV_MEAS_FAIL |\nEV_TIMEOUT\n[retries > 3]", fontsize=fs, ha="left",
            va="center", color=RED)
    # SEND -> FAULT
    edge("SEND", "FAULT", rad=0.0, color=RED)
    ax.text(11.45, 6.85, "EV_TIMEOUT", fontsize=fs, ha="center", va="bottom", color=RED)
    # SEND -> RX_WAIT
    edge("SEND", "RX_WAIT", rad=-0.25)
    ax.text(13.0, 2.6, "EV_TX_DONE /\nopen RX1 after 1 s", fontsize=fs, ha="left", va="center")
    # RX_WAIT -> SLEEP
    edge("RX_WAIT", "SLEEP", rad=-0.25)
    ax.text(0.4, 2.6, "EV_RX_DONE | EV_TIMEOUT /\nschedule next alarm 600 s", fontsize=fs,
            ha="left", va="center")
    # FAULT -> SLEEP
    edge("FAULT", "SLEEP", rad=0.0, color=RED)
    ax.text(5.6, 5.85, "EV_RTC_ALARM\nafter 6 h back-off /\nreset driver, bus", fontsize=fs,
            ha="center", va="top", color=RED)
    ax.text(16.9, 0.25, "every waiting state has a timeout;\ncurrent draw shown in each state",
            fontsize=7.3, ha="right", va="bottom", color=GREY, style="italic")
    save(fig, "28", "fig-28-2-node-state-machine")


# ----------------------------------------------------------------------------
# Figure 28.3 — energy profile of one reporting cycle
# ----------------------------------------------------------------------------
def lora_toa(payload, sf, bw=125e3, cr=1, n_pre=8):
    de = 1 if (sf >= 11 and bw == 125e3) else 0
    t_sym = 2 ** sf / bw
    n = 8 + max(math.ceil((8 * payload - 4 * sf + 44) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (n_pre + 4.25 + n) * t_sym, t_sym


def fig_28_3():
    t_tx, t_sym = lora_toa(24, 7)
    t_rx = 8 * t_sym
    i_sl, i_me, i_tx, i_rx = 2e-6, 2.5e-3, 45e-3, 11.5e-3
    t0 = 0.05
    segs = [(0, t0, i_sl), (t0, 0.030, i_me), (None, t_tx, i_tx), (None, 1.0, i_sl),
            (None, t_rx, i_rx), (None, 1.0 - t_rx, i_sl), (None, t_rx, i_rx), (None, 0.0, i_sl)]
    # build piecewise-constant profile (RX2 opens 2 s after TX end)
    t_me0 = t0
    t_tx0 = t_me0 + 0.030
    t_tx1 = t_tx0 + t_tx
    t_rx1 = t_tx1 + 1.0
    t_rx2 = t_tx1 + 2.0
    edges = [0, t_me0, t_tx0, t_tx1, t_rx1, t_rx1 + t_rx, t_rx2, t_rx2 + t_rx, 2.35]
    cur = [i_sl, i_me, i_tx, i_sl, i_rx, i_sl, i_rx, i_sl]
    del segs

    fig = plt.figure(figsize=(6.8, 3.9))
    ax = fig.add_axes([0.10, 0.14, 0.66, 0.78])
    ax2 = fig.add_axes([0.785, 0.14, 0.09, 0.78], sharey=ax)
    for a in (ax, ax2):
        xs = np.repeat(edges, 2)[1:-1]
        ys = np.repeat(cur, 2)
        a.fill_between(xs, 1e-7, ys, color=tint(BLUE, "30"), lw=0)
        a.plot(xs, ys, color=BLUE, lw=1.4)
        a.set_yscale("log")
        a.set_ylim(1e-6, 2e-1)
    ax.set_xlim(0, 2.35)
    # second axis: end of cycle and next wake at 600 s
    e2 = [599.9, 600.0, 600.03, 600.03 + t_tx, 600.15]
    xs = np.repeat(e2, 2)[1:-1]
    ys = np.repeat([i_sl, i_me, i_tx, i_sl], 2)
    ax2.cla()
    ax2.fill_between(xs, 1e-7, ys, color=tint(BLUE, "30"), lw=0)
    ax2.plot(xs, ys, color=BLUE, lw=1.4)
    ax2.set_yscale("log")
    ax2.set_ylim(1e-6, 2e-1)
    ax2.set_xlim(599.9, 600.15)
    ax2.set_xticks([600])
    ax2.set_xticklabels(["600"])
    ax2.tick_params(which="both", labelleft=False, left=False)
    ax2.spines["left"].set_visible(False)
    # break marks
    for a, xpos in ((ax, 1.0), (ax2, 0.0)):
        kw = dict(transform=a.transAxes, color=INK, clip_on=False, lw=1)
        a.plot([xpos - 0.012 * (1 if a is ax else 6), xpos + 0.012 * (1 if a is ax else 6)],
               [-0.03, 0.03], **kw)
    ax.spines["right"].set_visible(False)
    ax.set_yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1])
    ax.set_yticklabels(["1 µA", "10 µA", "100 µA", "1 mA", "10 mA", "100 mA"])
    ax.set_xlabel("time from wake-up (s)")
    ax.set_ylabel("supply current (log scale)")
    ax2.set_xlabel("(s)")
    fs = 7.8
    ax.annotate("measure\n2.5 mA, 30 ms", xy=(t_me0 + 0.015, i_me), xytext=(0.13, 2.5e-4),
                fontsize=fs, ha="left", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.annotate(f"transmit SF7\n45 mA, {t_tx*1e3:.1f} ms", xy=(t_tx1, 0.03), xytext=(0.28, 0.06),
                fontsize=fs, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.annotate(f"RX1 window\n11.5 mA, {t_rx*1e3:.1f} ms", xy=(t_rx1, 3e-3), xytext=(1.08, 3.0e-4),
                fontsize=fs, ha="right", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.annotate(f"RX2 window\n11.5 mA, {t_rx*1e3:.1f} ms", xy=(t_rx2, 1.5e-4), xytext=(2.08, 4.0e-5),
                fontsize=fs, ha="right", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.annotate("", xy=(t_rx1, 4e-6), xytext=(t_tx1, 4e-6),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=8))
    ax.text((t_tx1 + t_rx1) / 2, 4.6e-6, "RX1 delay 1 s", ha="center", va="bottom", fontsize=fs)
    ax.annotate("", xy=(t_rx2, 4e-6), xytext=(t_rx1, 4e-6),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.8, mutation_scale=8))
    ax.text((t_rx1 + t_rx2) / 2, 4.6e-6, "1 s", ha="center", va="bottom", fontsize=fs)
    ax.text(2.3, 1.12e-6, "sleep 2 µA until 600 s", ha="right", va="bottom", fontsize=fs)
    ax.axhline(7.07e-6, color=ORANGE, ls="--", lw=1.1)
    ax.text(0.9, 9.3e-6, "average over 600 s: 7.07 µA", color=ORANGE, fontsize=fs, ha="left",
            va="bottom")
    ax2.axhline(7.07e-6, color=ORANGE, ls="--", lw=1.1)
    ax2.text(600.0, 0.11, "next\nwake", fontsize=7, ha="center", va="bottom")
    # inset bar chart of charge
    axi = fig.add_axes([0.525, 0.52, 0.15, 0.24])
    names = ["transmit", "sleep", "rx windows", "measure"]
    q = [2776, 1200, 188, 75]
    cols = [ORANGE, SKY, YELLOW, GREEN]
    axi.barh(names[::-1], q[::-1], color=cols[::-1], height=0.65)
    for i, v in enumerate(q[::-1]):
        axi.text(v + 60, i, f"{v} µC", va="center", fontsize=7)
    axi.set_xlim(0, 4600)
    axi.tick_params(labelsize=7)
    axi.set_xticks([0, 2000, 4000]); axi.set_xticklabels(["0", "2000", "4000 µC"])
    axi.set_title("charge per cycle: 4.24 mC", fontsize=7.5)
    axi.patch.set_alpha(0.9)
    save(fig, "28", "fig-28-3-energy-profile")


# ----------------------------------------------------------------------------
# Figure 28.4 — circular append-only flash log
# ----------------------------------------------------------------------------
def fig_28_4():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7.6
    # strip of 8 sectors
    sw, sh, sx0, sy0 = 1.85, 1.3, 0.75, 9.6
    info = [("seq 0–126", tint(GREEN, "40")), ("127–253", tint(GREEN, "40")),
            ("254–380", tint(GREEN, "40")), ("381–507", tint(GREEN, "40")),
            ("508–634", tint(GREEN, "40")), ("635–652\n+ torn", tint(YELLOW, "50")),
            ("pre-erased\n0xFF", "#FFFFFF"), ("erased\n(1st pass)", "#F2F2F2")]
    for i, (txt, fc) in enumerate(info):
        x = sx0 + i * sw
        ax.add_patch(Rectangle((x, sy0), sw, sh, fc=fc, ec=INK, lw=1.0,
                               ls=(0, (3, 2)) if i == 6 else "-"))
        ax.add_patch(Rectangle((x, sy0 + sh - 0.22), sw, 0.22, fc="#BBBBBB", ec=INK, lw=0.6))
        ax.text(x + sw / 2, sy0 + sh + 0.15, f"sector {i}", ha="center", va="bottom", fontsize=fs)
        ax.text(x + sw / 2, sy0 + (sh - 0.22) / 2, txt, ha="center", va="center", fontsize=7.2)
    ax.text(sx0 + 8 * sw + 0.12, sy0 + sh / 2, "… 1024\nsectors\n× 4 KB", ha="left", va="center",
            fontsize=7.2)
    # wrap-around arrow under strip
    yb = sy0 - 0.35
    line(ax, [(sx0 + 8 * sw - 0.3, sy0), (sx0 + 8 * sw - 0.3, yb), (sx0 + 0.3, yb), (sx0 + 0.3, sy0)],
         arrow_end=True, color=GREY)
    ax.text(sx0 + 4 * sw, yb - 0.05, "ring wraps: after the last sector, sector 0 is erased and reused",
            ha="center", va="top", fontsize=7.2, color=GREY)
    ax.text(sx0 + 6.5 * sw, sy0 + sh + 0.62, "kept erased ahead of head", ha="center", va="bottom",
            fontsize=7.2, color=BLUE)
    # zoom lines to sector 5 detail
    dx0, dy0, cw, ch = 2.2, 3.05, 0.72, 0.62
    ncol, nrow = 16, 8
    s5 = sx0 + 5 * sw
    ax.plot([s5, dx0], [yb - 0.55, dy0 + nrow * ch], color=GREY, lw=0.7, ls=":")
    ax.plot([s5 + sw, dx0 + ncol * cw], [yb - 0.55, dy0 + nrow * ch], color=GREY, lw=0.7, ls=":")
    ax.text(dx0, dy0 + nrow * ch + 0.12, "sector 5 in detail: 32 B header + 127 records × 32 B = 4096 B",
            ha="left", va="bottom", fontsize=fs, weight="bold",
            bbox=dict(fc="white", ec="none", pad=0.5))
    for k in range(ncol * nrow):
        r, c = divmod(k, ncol)
        x = dx0 + c * cw
        y = dy0 + (nrow - 1 - r) * ch
        if k == 0:
            fc, t = "#BBBBBB", "hdr"
        else:
            seq = 635 + k - 1
            if seq <= 652:
                fc, t = tint(GREEN, "70"), str(seq)
            elif seq == 653:
                fc, t = "#E57373", "653"
            else:
                fc, t = "white", ""
        ax.add_patch(Rectangle((x, y), cw, ch, fc=fc, ec="#666666", lw=0.5,
                               hatch="////" if t == "653" else None))
        if t:
            ax.text(x + cw / 2, y + ch / 2, t, ha="center", va="center", fontsize=5.6)
    # labels for the detail
    ax.text(dx0 - 0.1, dy0 + nrow * ch - ch / 2, "magic 0x4C4F4731\n+ erase count", ha="right",
            va="center", fontsize=6.8)
    ax.text(dx0 + ncol * cw / 2 + 1.0, dy0 + 3.0 * ch, "erased slots: all bytes 0xFF\n(rejected by seq test)",
            ha="center", va="center", fontsize=7.4, color=GREY,
            bbox=dict(fc="white", ec="none", pad=1.0))
    # torn record callout: k=19 -> row 1, col 3
    tr_x = dx0 + 3 * cw + cw / 2
    tr_y = dy0 + (nrow - 2) * ch
    ax.annotate("seq 653 torn by power loss:\npartially programmed, CRC fails → ignored",
                xy=(tr_x, tr_y), xytext=(dx0 + 8.0 * cw, dy0 + 5.0 * ch),
                fontsize=7.2, color=RED, ha="left", va="center",
                bbox=dict(fc="white", ec="none", pad=1.0),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.9, mutation_scale=9))
    # write head after 652 (k=18 -> row1 col2 right edge)
    wh_x = dx0 + 3 * cw
    ax.annotate("write head\n(after seq 652)", xy=(wh_x, dy0 + (nrow - 2) * ch),
                xytext=(wh_x - 0.4, dy0 - 0.15 + 3.6 * ch), fontsize=7.2, color=BLUE, ha="center", va="top",
                bbox=dict(fc="white", ec="none", pad=1.0),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.0, mutation_scale=9))
    # recovery scan arrow
    ys = dy0 - 0.3
    line(ax, [(dx0, ys), (dx0 + ncol * cw, ys)], arrow_end=True, color=PINK, lw=1.2)
    ax.text(dx0 + ncol * cw / 2, ys - 0.1, "boot-time recovery scan: head = after the valid record "
            "with the highest sequence number", ha="center", va="top", fontsize=7.2, color=PINK)
    # record layout
    ry = 0.75
    fields = [("seq", 4), ("time", 4), ("ten 16-bit channels", 20), ("status", 2), ("CRC-16", 2)]
    scale = 0.44
    x = 2.2
    ax.text(x - 0.1, ry + 0.35, "record\n(32 B)", ha="right", va="center", fontsize=fs, weight="bold")
    for name, nb in fields:
        wdt = nb * scale
        fc = tint(PINK, "40") if name == "CRC-16" else tint(BLUE, "22")
        ax.add_patch(Rectangle((x, ry), wdt, 0.7, fc=fc, ec=INK, lw=0.8))
        ax.text(x + wdt / 2, ry + 0.35, f"{name}\n{nb} B", ha="center", va="center",
                fontsize=6.6 if nb > 2 else 6.0)
        x += wdt
    ax.text(x, ry - 0.12, "CRC-16/CCITT-FALSE over the first 30 bytes; the whole record is "
            "written in one page-program operation", ha="right", va="top", fontsize=7)
    save(fig, "28", "fig-28-4-flash-log-layout")


# ----------------------------------------------------------------------------
# Figure 28.5 — debug and trace architecture
# ----------------------------------------------------------------------------
def fig_28_5():
    fig, ax = schematic(6.8, 4.5, xlim=(0, 18), ylim=(0, 11.9))
    # MCU box
    ax.add_patch(FancyBboxPatch((0.2, 0.9), 7.4, 10.6, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="#F6F9FC", ec=INK, lw=1.3))
    ax.text(3.9, 11.0, "Cortex-M4 microcontroller", ha="center", va="center", fontsize=9, weight="bold")
    box(ax, 0.45, 8.9, 3.3, 1.5, "Cortex-M4\ncore", fc=tint(BLUE, "38"), fontsize=8.5)
    comps = [("FPB\n6 breakpoints", 7.3), ("DWT\n4 watchpoints\n+ CYCCNT", 5.4),
             ("ITM\n32 stimulus ports", 3.8), ("ETM\ninstruction trace", 2.2)]
    hts = [1.2, 1.5, 1.2, 1.2]
    for (t, y), hh in zip(comps, hts):
        box(ax, 0.45, y, 3.3, hh, t, fc=tint(GREEN, "30"), fontsize=7.4)
    for ytop, ybot in ((8.9, 8.5), (7.3, 6.9), (5.4, 5.0), (3.8, 3.4)):
        line(ax, [(2.1, ytop), (2.1, ybot)])
    box(ax, 4.3, 7.4, 2.0, 1.8, "DAP\nSW-DP or\nJTAG-DP", fc=tint(YELLOW, "45"), fontsize=7.6)
    box(ax, 4.3, 2.3, 2.0, 1.8, "TPIU\ntrace port\ninterface", fc=tint(PINK, "35"), fontsize=7.4)
    # internal links
    line(ax, [(3.75, 9.6), (4.0, 9.6), (4.0, 8.6), (4.3, 8.6)], arrow_end=True)
    ax.text(4.05, 9.75, "AHB-AP", fontsize=6.6, ha="left", va="bottom")
    line(ax, [(3.75, 4.4), (4.0, 4.4), (4.0, 3.6), (4.3, 3.6)], arrow_end=True)
    line(ax, [(3.75, 2.8), (4.3, 2.8)], arrow_end=True)
    line(ax, [(3.75, 6.1), (3.95, 6.1), (3.95, 4.4)], color=GREY, lw=0.9)
    ax.text(3.9, 5.0, "DWT\nevents", fontsize=6.0, color=GREY, ha="right", va="center")
    # pins from DAP
    for n, y in (("SWDIO", 8.7), ("SWCLK", 8.3), ("nRESET", 7.9)):
        line(ax, [(6.3, y), (10.3, y)])
        ax.text(7.75, y + 0.03, n, fontsize=6.6, va="bottom")
    # pins from TPIU
    line(ax, [(6.3, 3.8), (10.0, 3.8), (10.0, 6.6), (10.3, 6.6)], arrow_end=True)
    ax.text(7.75, 3.83, "SWO", fontsize=6.6, va="bottom")
    for n, y in (("TRACECLK", 3.0), ("TRACEDATA[3:0]", 2.55)):
        line(ax, [(6.3, y), (10.3, y)], ls=(0, (3, 2)))
        ax.text(7.75, y + 0.03, n, fontsize=6.4, va="bottom")
    # debug probe
    box(ax, 10.3, 5.8, 3.6, 3.9, "", fc=tint(SKY, "35"))
    ax.text(12.1, 9.25, "debug probe", ha="center", fontsize=8.5, weight="bold")
    ax.text(12.1, 8.75, "J-Link / CMSIS-DAP", ha="center", fontsize=7.2)
    ax.text(12.1, 7.3, "SWD 4–10 MHz:\nmemory ≈ 1 MB/s\n\nSWO capture:\nup to 4 Mbit/s NRZ",
            ha="center", va="center", fontsize=7.0, linespacing=1.25)
    # trace probe
    box(ax, 10.3, 1.4, 3.6, 3.0, "", fc="white", ls=(0, (4, 2)))
    ax.text(12.1, 3.75, "trace probe\n(optional)", ha="center", va="center", fontsize=8, weight="bold")
    ax.text(12.1, 2.35, "4-bit ETM, 100 MHz\n≈ 400 Mbit/s", ha="center", va="center", fontsize=7.0)
    # host
    box(ax, 15.0, 1.9, 2.9, 7.8, "", fc=tint(ORANGE, "22"))
    ax.text(16.45, 9.2, "host PC", ha="center", fontsize=8.5, weight="bold")
    for i, t in enumerate(["GDB server", "IDE /\ndebugger", "trace viewer\n(SWO, ETM)"]):
        box(ax, 15.15, 7.2 - i * 2.0, 2.6, 1.5, t, fc="white", fontsize=7.4)
    line(ax, [(13.9, 8.0), (15.0, 8.0)], arrow_end=True, both=True)
    ax.text(14.45, 8.1, "USB", fontsize=6.6, ha="center", va="bottom")
    line(ax, [(13.9, 2.9), (15.0, 2.9)], arrow_end=True, both=True)
    ax.text(14.45, 3.0, "USB 3", fontsize=6.6, ha="center", va="bottom")
    ax.text(9.0, 0.35, "SWO: ITM packets of 1 header + 1–4 data bytes, 10 bits per byte in NRZ mode; "
            "ETB = on-chip trace buffer alternative", fontsize=6.8, color=GREY, ha="center")
    save(fig, "28", "fig-28-5-debug-architecture")


# ----------------------------------------------------------------------------
# Figure 28.6 — HIL bench for a BMS controller
# ----------------------------------------------------------------------------
def fig_28_6():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(0, 12.5))
    fs = 7.4
    # test automation PC
    box(ax, 4.2, 10.3, 8.6, 1.9, "", fc=tint(ORANGE, "25"))
    ax.text(8.5, 11.75, "test-automation PC", ha="center", fontsize=8.5, weight="bold")
    ax.text(8.5, 10.9, "pytest scripts · requirements-traceability database · report generator",
            ha="center", fontsize=7.4)
    # DUT
    box(ax, 0.2, 0.6, 4.3, 8.6, "", fc=tint(BLUE, "22"))
    ax.text(2.35, 8.75, "DUT: BMS\ncontroller board", ha="center", va="center", fontsize=8.5, weight="bold")
    conns = ["cell-sense harness (16)", "NTC inputs (8)", "contactor drivers", "CAN",
             "isolation-monitor input", "12 V supply", "debug port (SWD)"]
    ys = [7.3, 6.3, 5.3, 4.3, 3.3, 2.3, 1.3]
    for t, y in zip(conns, ys):
        box(ax, 0.4, y - 0.37, 3.85, 0.74, t, fc="white", fontsize=6.9)
    # simulator
    box(ax, 8.5, 0.6, 8.3, 8.6, "", fc=tint(GREEN, "20"))
    ax.text(12.65, 8.75, "real-time simulator", ha="center", va="center", fontsize=8.5, weight="bold")
    box(ax, 13.4, 3.6, 3.2, 4.4, "battery-pack\nmodel\n16 cells,\nequivalent-\ncircuit model,\n1 ms step",
        fc=tint(GREEN, "45"), fontsize=7.2)
    sims = [("cell-voltage emulators\n0–5 V, 1 mV accuracy", 7.3), ("resistor emulators (NTC)", 6.3),
            ("contactor load emulators\n(read driver outputs)", 5.3), ("CAN interface:\nrestbus simulation", 4.3),
            ("insulation-fault emulator", 3.3), ("programmable 12 V supply\n(dips per ISO 16750-2)", 2.3)]
    for t, y in sims:
        box(ax, 8.75, y - 0.4, 4.3, 0.8, t, fc="white", fontsize=6.6)
        if y >= 3.6:
            line(ax, [(13.4, y), (13.05, y)], arrow_end=True if y != 5.3 else False, both=(y == 5.3))
    # fault injection matrix
    box(ax, 5.1, 1.6, 2.6, 6.3, "", fc="#FBE9E7", ec=RED)
    ax.text(6.4, 8.05, "fault-injection\nmatrix", ha="center", va="bottom", fontsize=7.6, color=RED,
            weight="bold")
    ax.text(6.35, 2.55, "open wire\nshort to GND\nshort to battery", ha="center", va="center",
            fontsize=6.6, color=RED)
    for y in [7.3, 6.3, 5.3, 4.3, 3.3, 2.3]:
        line(ax, [(4.25, y), (5.1, y)])
        line(ax, [(7.7, y), (8.75, y)])
    for y in [6.3, 5.3, 4.3, 3.3]:
        for xx in (5.6, 6.35, 7.1):
            ax.plot(xx, y, marker="x", color=RED, ms=4, mew=1)
        line(ax, [(5.1, y), (7.7, y)], color=GREY, lw=0.6)
    # signal-direction labels
    # debug link to PC
    line(ax, [(4.25, 1.3), (4.75, 1.3), (4.75, 9.9), (6.0, 9.9), (6.0, 10.3)], arrow_end=True, both=True)
    ax.text(4.85, 9.55, "debug / flashing", fontsize=6.6, ha="left")
    line(ax, [(11.5, 10.3), (11.5, 9.2)], arrow_end=True, both=True)
    ax.text(11.65, 9.75, "test control, logging", fontsize=6.6, ha="left")
    # latency budget
    ax.text(12.65, 0.85, "loop latency budget:\nI/O sampling 20 µs · model step 1 ms", ha="center",
            fontsize=7.0, style="italic")
    save(fig, "28", "fig-28-6-hil-bench")


if __name__ == "__main__":
    fig_28_1()
    fig_28_2()
    fig_28_3()
    fig_28_4()
    fig_28_5()
    fig_28_6()
