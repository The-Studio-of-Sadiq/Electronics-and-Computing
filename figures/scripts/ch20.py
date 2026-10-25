"""Figures for Chapter 20 — Programming Fundamentals.

Run from the repository root:  python figures/scripts/ch20.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, Wedge, FancyBboxPatch  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic, new_fig  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4]
RED = "#C0392B"
FC_A = "#DCEBF7"
FC_B = "#E3F2E6"
FC_C = "#FFF4D6"
FC_D = "#FBE2DF"


def wire(ax, pts, color=INK, lw=1.2, ls="-", **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", **kw)


def wire_arrow(ax, pts, color=INK, lw=1.2, ls="-", ms=10):
    if len(pts) > 2:
        wire(ax, pts[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def diamond(ax, x, y, w, h, text, fc=FC_C, fs=8.5):
    ax.add_patch(Polygon([(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)],
                         closed=True, fc=fc, ec=INK, lw=1.0))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)


def cbox(ax, x, y, w, h, text, fc=FC_A, fs=8.5, round_=False):
    """Box centred on (x, y)."""
    if round_:
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle=f"round,pad=0,rounding_size={h / 2}",
                                    fc=fc, ec=INK, lw=1.0))
        ax.text(x, y, text, ha="center", va="center", fontsize=fs)
    else:
        box(ax, x - w / 2, y - h / 2, w, h, text, fc=fc, fontsize=fs)


# ----------------------------------------------------------------------------
# thermistor table of Listing 20.1
# ----------------------------------------------------------------------------
TEMPS = list(range(-40, 126, 5))


def adc_of(t_c, r25=10e3, beta=3950.0, r_pu=10e3):
    r = r25 * math.exp(beta * (1 / (t_c + 273.15) - 1 / 298.15))
    return round(4095 * r / (r + r_pu))


COUNTS = [adc_of(t) for t in TEMPS]


def adc_to_temp(x):
    lo, hi = 0, len(COUNTS) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if COUNTS[mid] >= x:
            lo = mid
        else:
            hi = mid
    frac = (COUNTS[lo] - x) / (COUNTS[lo] - COUNTS[hi])
    return lo, hi, TEMPS[lo] + frac * (TEMPS[hi] - TEMPS[lo])


# ----------------------------------------------------------------------------
# Figure 20.1 — binary search flowchart
# ----------------------------------------------------------------------------
def fig_20_1():
    fig, ax = schematic(6.8, 5.6, xlim=(0, 14), ylim=(0, 11.55))
    cx = 3.6
    cbox(ax, cx, 10.95, 3.6, 0.7, "Start: ADC count x", fc=FC_B, round_=True)
    diamond(ax, cx, 9.6, 6.8, 1.3, "COUNTS[33] ≤ x ≤ COUNTS[0] ?")
    cbox(ax, 9.3, 9.6, 2.6, 0.7, "range error", fc=FC_D)
    cbox(ax, cx, 8.2, 3.2, 0.7, "lo = 0,  hi = 33")
    diamond(ax, cx, 6.95, 3.8, 1.15, "hi − lo > 1 ?")
    cbox(ax, cx, 5.65, 3.8, 0.7, "mid = (lo + hi) // 2")
    diamond(ax, cx, 4.35, 4.6, 1.15, "COUNTS[mid] ≥ x ?")
    cbox(ax, cx, 3.0, 2.4, 0.7, "lo = mid")
    cbox(ax, 7.7, 4.35, 2.2, 0.7, "hi = mid")
    # main flow arrows
    wire_arrow(ax, [(cx, 10.6), (cx, 10.25)])
    wire_arrow(ax, [(cx, 8.95), (cx, 8.55)])
    ax.text(cx + 0.12, 8.75, "yes", fontsize=8, color=GREEN, va="center")
    wire_arrow(ax, [(cx + 3.4, 9.6), (9.3 - 1.3, 9.6)])
    ax.text(cx + 3.5, 9.72, "no", fontsize=8, color=RED, va="bottom")
    wire_arrow(ax, [(cx, 7.85), (cx, 7.525)])
    wire_arrow(ax, [(cx, 6.375), (cx, 6.0)])
    ax.text(cx + 0.12, 6.2, "yes", fontsize=8, color=GREEN, va="center")
    wire_arrow(ax, [(cx, 5.3), (cx, 4.925)])
    wire_arrow(ax, [(cx, 3.775), (cx, 3.35)])
    ax.text(cx + 0.12, 3.57, "yes", fontsize=8, color=GREEN, va="center")
    wire_arrow(ax, [(cx + 2.3, 4.35), (7.7 - 1.1, 4.35)])
    ax.text(cx + 2.4, 4.25, "no", fontsize=8, color=RED, va="top")
    # loop back edge
    wire(ax, [(cx, 2.65), (cx, 2.1)])
    wire(ax, [(7.7, 4.0), (7.7, 2.1), (0.5, 2.1)])
    ax.plot([cx], [2.1], "o", ms=3.5, color=INK)
    wire_arrow(ax, [(0.5, 2.1), (0.5, 6.95), (cx - 1.9, 6.95)])
    ax.text(3.9, 1.8, "Invariant: COUNTS[lo] ≥ x ≥ COUNTS[hi]", fontsize=8.5,
            color=BLUE, ha="center", va="top", fontweight="bold")
    ax.text(3.9, 1.25, "hi − lo decreases every pass: terminates", fontsize=8,
            color=BLUE, ha="center", va="top")
    # exit path
    rx = 10.4
    wire_arrow(ax, [(cx + 1.9, 6.95), (rx - 2.8, 6.95)])
    ax.text(cx + 2.05, 6.85, "no", fontsize=8, color=RED, va="top")
    cbox(ax, rx, 6.95, 5.6, 0.95,
         "frac = (COUNTS[lo] − x) /\n(COUNTS[lo] − COUNTS[hi])")
    cbox(ax, rx, 5.65, 4.0, 0.7, "T = TEMPS[lo] + 5·frac")
    cbox(ax, rx, 4.55, 2.6, 0.65, "End: return T", fc=FC_B, round_=True)
    wire_arrow(ax, [(rx, 6.475), (rx, 6.0)])
    wire_arrow(ax, [(rx, 5.3), (rx, 4.875)])

    # inset: table points
    ins = fig.add_axes([0.70, 0.075, 0.28, 0.25])
    ins.plot(TEMPS, COUNTS, "o", ms=2.8, color=BLUE, zorder=3)
    ins.plot(TEMPS, COUNTS, "-", lw=0.8, color=BLUE, alpha=0.6)
    lo, hi, T = adc_to_temp(1000)
    ins.axhline(1000, color=ORANGE, lw=0.9, ls="--")
    ins.plot([TEMPS[lo], TEMPS[hi]], [COUNTS[lo], COUNTS[hi]], "s", ms=5, mfc="none",
             mec=RED, mew=1.2, zorder=4)
    ins.plot([T, T], [0, 1000], color=RED, lw=0.9)
    ins.plot(T, 1000, "o", ms=4, color=RED, zorder=5)
    ins.annotate(f"x = 1000 → {T:.2f} °C\n(between 50 and 55 °C)", xy=(T, 1000),
                 xytext=(30, 2900), fontsize=7, color=RED,
                 arrowprops=dict(arrowstyle="-", color=RED, lw=0.7))
    ins.set_xlim(-45, 130)
    ins.set_ylim(0, 4200)
    ins.set_xticks([-40, 0, 40, 80, 125])
    ins.set_yticks([0, 1000, 2000, 3000, 4000])
    ins.tick_params(labelsize=7)
    ins.set_xlabel("temperature (°C)", fontsize=7.5, labelpad=1)
    ins.set_ylabel("ADC count", fontsize=7.5, labelpad=1)
    ins.set_title("34 table points", fontsize=7.5, pad=2)
    save(fig, "20", "fig-20-1-binary-search-flowchart")


# ----------------------------------------------------------------------------
# Figure 20.2 — float32 coulomb counter
# ----------------------------------------------------------------------------
def fig_20_2():
    dt, current = 1e-3, 2.0
    n = 8 * 3600 * 1000
    q32 = np.cumsum(np.full(n, current * dt, dtype=np.float32), dtype=np.float32)
    q64 = np.cumsum(np.full(n, current * dt), dtype=np.float64)
    k = np.arange(999, n, 1000)                 # one point per second
    t_h = (k + 1) * dt / 3600
    true = current * (k + 1) * dt
    fig, ax = new_fig(6.4, 4.0)
    ax.plot(t_h, true, color=INK, lw=2.6, label="true charge")
    ax.plot(t_h, q64[k], color=GREEN, lw=1.2, ls="--", label="binary64 accumulator")
    ax.plot(t_h, q32[k], color=ORANGE, lw=1.8, label="binary32 accumulator")
    for y, lab in [(32768, "32 768 A·s: ulp 0.0039 A·s, δ = 0.512 ulp rounds up"),
                   (65536, "65 536 A·s: ulp 0.0078 A·s, δ = 0.256 ulp rounds to zero")]:
        ax.axhline(y, color="#777777", ls=":", lw=1)
        ax.text(0.08, y + 900, lab, fontsize=7.8, color="#444444", va="bottom")
    i1 = np.argmax(q32 >= 32768)
    i2 = np.argmax(q32 >= 65536)
    t1, t2 = (i1 + 1) * dt / 3600, (i2 + 1) * dt / 3600
    ax.plot([t1, t2], [32768, 65536], "o", color=ORANGE, ms=4.5, zorder=5)
    ax.annotate(f"{t1:.2f} h", xy=(t1, 32768), xytext=(t1 + 0.25, 27000), fontsize=8,
                color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.annotate(f"{t2:.2f} h: frozen", xy=(t2, 65536), xytext=(t2 - 0.35, 56000),
                fontsize=8, color=ORANGE, ha="right",
                arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.7))
    ax.text(2.4, 6500, "about 2 % low below 32 768 A·s\n(7060 at 1 h, 28 154 at 4 h)",
            fontsize=8, color=ORANGE, ha="left")
    ax.text(2.9, 57000, "slope 1.95 × true\n(37 603 at 5 h, 51 665 at 6 h)", fontsize=8,
            color=ORANGE, ha="left", va="top")
    ax.annotate("57 600 A·s at 8 h", xy=(8, 57600), xytext=(7.0, 42000), fontsize=8,
                ha="center", arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 70000)
    ax.set_xlabel("time (h)")
    ax.set_ylabel("accumulated charge (A·s)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:,.0f}".replace(",", " ")))
    ax.legend(loc="lower right", fontsize=8.5)
    save(fig, "20", "fig-20-2-float32-coulomb-counter")


# ----------------------------------------------------------------------------
# Figure 20.3 — ring buffer
# ----------------------------------------------------------------------------
def fig_20_3():
    fig, ax = schematic(6.8, 4.2, xlim=(-6.6, 6.6), ylim=(-3.9, 4.25))
    N = 16
    r_out, r_in = 2.5, 1.55
    tail, head = 21, 28
    filled = {(tail + i) & 15 for i in range(head - tail)}
    for s in range(N):
        # slot 0 at the top, clockwise
        a1 = 90 - s * 360 / N
        a0 = a1 - 360 / N
        fc = "#9CC7E8" if s in filled else "white"
        ax.add_patch(Wedge((0, 0), r_out, a0, a1, width=r_out - r_in, fc=fc, ec=INK,
                           lw=1.0))
        am = math.radians((a0 + a1) / 2)
        rm = (r_out + r_in) / 2
        ax.text(rm * math.cos(am), rm * math.sin(am), str(s), ha="center", va="center",
                fontsize=8)
    ax.text(0, 0.25, "fill = head − tail", ha="center", va="center", fontsize=9)
    ax.text(0, -0.25, "= 28 − 21 = 7", ha="center", va="center", fontsize=9,
            fontweight="bold")

    def pointer(slot, text, color, side):
        a = math.radians(90 - (slot + 0.5) * 360 / N)
        p_tip = (r_out * math.cos(a), r_out * math.sin(a))
        p_tail = ((r_out + 1.0) * math.cos(a), (r_out + 1.0) * math.sin(a))
        ax.annotate("", xy=p_tip, xytext=p_tail,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6,
                                    mutation_scale=12, shrinkA=0, shrinkB=0))
        ax.text(p_tail[0] + 0.1 * side, p_tail[1] - 0.05, text, color=color, fontsize=8.5,
                ha="left" if side > 0 else "right", va="center", fontweight="bold")

    pointer(tail & 15, "tail = 21\n(21 & 15 = 5)", GREEN, +1)
    pointer(head & 15, "head = 28\n(28 & 15 = 12)", ORANGE, -1)
    # producer / consumer blocks
    cbox(ax, -4.7, 2.85, 3.5, 1.55, "ADC ISR (producer)\ndata[head & mask] = v;\nhead++;",
         fc=FC_C, fs=8)
    cbox(ax, 4.85, 1.6, 3.5, 1.55, "main loop (consumer)\nv = data[tail & mask];\ntail++;",
         fc=FC_B, fs=8)
    wire_arrow(ax, [(-4.7, 2.07), (-4.5, 1.15)], color=ORANGE)
    wire_arrow(ax, [(4.85, 0.82), (4.3, -1.45)], color=GREEN)
    ax.text(-4.45, 1.62, "writes at head", fontsize=7.5, color=ORANGE, ha="left",
            va="center")
    ax.text(4.65, -0.35, "reads at tail", fontsize=7.5, color=GREEN, ha="left",
            va="center")
    ax.text(0, -3.35, "mask = 15.  Full when head − tail = 16; empty when head = tail. "
            "Indices are free-running\nuint32_t, so head − tail is correct across "
            "wrap-around.", ha="center", va="center", fontsize=8)
    save(fig, "20", "fig-20-3-ring-buffer")


# ----------------------------------------------------------------------------
# Figure 20.4 — memory layout
# ----------------------------------------------------------------------------
def fig_20_4():
    fig, ax = schematic(6.8, 4.9, xlim=(0, 14.6), ylim=(0, 10.4))
    # flash column
    fx, fw = 0.9, 2.6
    ax.text(fx + fw / 2, 10.05, "Flash 1 MB", ha="center", fontsize=9.5, fontweight="bold")
    fl = [(0.6, "vector table", "#F2D7B6"), (2.2, ".text\n(code)", FC_A),
          (1.3, ".rodata\n(constants)", "#C9DFF0"), (0.8, ".data initial\nvalues", FC_C),
          (4.4, "(unused)", "white")]
    y = 0.6
    ys_f = {}
    for h, t, c in fl:
        ax.add_patch(Rectangle((fx, y), fw, h, fc=c, ec=INK, lw=1.0,
                               hatch="" if t != "(unused)" else ""))
        ax.text(fx + fw / 2, y + h / 2, t, ha="center", va="center", fontsize=8,
                color="#777777" if t == "(unused)" else INK)
        ys_f[t] = (y, h)
        y += h
    ax.text(fx - 0.08, 0.6, "0x0800 0000", ha="right", va="center", fontsize=7.2,
            family="monospace")
    ax.text(fx - 0.08, y, "0x0810 0000", ha="right", va="center", fontsize=7.2,
            family="monospace")

    # SRAM column
    sx, sw = 5.4, 2.6
    ax.text(sx + sw / 2, 10.05, "SRAM 128 KB", ha="center", fontsize=9.5, fontweight="bold")
    sr = [(0.8, ".data", FC_C), (1.4, ".bss", "#E8E8E8"), (1.3, "heap ↑", FC_B),
          (3.4, "(free)", "white"), (2.4, "stack ↓", FC_D)]
    y = 0.6
    ys_s = {}
    for h, t, c in sr:
        ax.add_patch(Rectangle((sx, y), sw, h, fc=c, ec=INK, lw=1.0))
        ax.text(sx + sw / 2, y + h / 2, t, ha="center", va="center", fontsize=8.5,
                color="#777777" if t == "(free)" else INK)
        ys_s[t] = (y, h)
        y += h
    top = y
    ax.text(sx - 0.08, 0.6, "0x2000 0000", ha="right", va="center", fontsize=7.2,
            family="monospace")
    ax.text(sx - 0.08, top, "0x2002 0000", ha="right", va="center", fontsize=7.2,
            family="monospace")
    # heap / stack growth arrows
    hy, hh = ys_s["heap ↑"]
    wire_arrow(ax, [(sx + sw - 0.3, hy + hh - 0.1), (sx + sw - 0.3, hy + hh + 0.5)],
               color=GREEN)
    sy, sh = ys_s["stack ↓"]
    wire_arrow(ax, [(sx + sw - 0.3, sy + 0.1), (sx + sw - 0.3, sy - 0.5)], color=RED)
    # SP marker
    sp_y = sy + sh * (1 - 1096 / 1536 * 0.9)
    ax.annotate("SP", xy=(sx, sp_y), xytext=(sx - 0.7, sp_y), fontsize=8.5,
                va="center", ha="right", color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.1, mutation_scale=9))
    # copied at start-up
    dy0, dh0 = ys_f[".data initial\nvalues"]
    dy1, dh1 = ys_s[".data"]
    ax.annotate("", xy=(sx, dy1 + dh1 / 2), xytext=(fx + fw, dy0 + dh0 / 2),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.3, mutation_scale=10,
                                connectionstyle="arc3,rad=0.25", shrinkA=0, shrinkB=0))
    ax.text(4.45, 4.3, "copied at\nstart-up", fontsize=7.8, color=ORANGE, ha="center",
            va="center")
    by, bh = ys_s[".bss"]
    ax.text(sx + sw / 2, by + 0.2, "(zeroed)", fontsize=7, color="#555555",
            ha="center", va="center")

    # stack zoom
    zx, zw = 9.8, 3.4
    ax.text(zx + zw / 2, 10.05, "Stack (worst case)", ha="center", fontsize=9.5,
            fontweight="bold")
    frames = [("main", 32), ("scheduler", 48), ("control_task", 96), ("pid_update", 40),
              ("log_value", 64), ("snprintf", 512), ("IRQ 1 FPU frame", 104),
              ("IRQ 1 handler", 48), ("IRQ 2 FPU frame", 104), ("IRQ 2 handler", 48)]
    z_top, z_bot = 9.6, 1.4
    hmin = 60                       # small frames drawn enlarged for legibility
    scale = (z_top - z_bot) / (sum(max(b, hmin) for _, b in frames) + 440)
    y = z_top
    for i, (name, b) in enumerate(frames):
        h = max(b, hmin) * scale
        y0 = y - h
        c = FC_D if "IRQ" in name else (FC_A if name != "snprintf" else "#F7C9C0")
        ax.add_patch(Rectangle((zx, y0), zw, h, fc=c, ec=INK, lw=0.8))
        lab = f"{name}  {b} B"
        fs = 7.0
        ax.text(zx + zw / 2, y0 + h / 2, lab, ha="center", va="center", fontsize=fs)
        y = y0
    used_bot = y
    ax.add_patch(Rectangle((zx, z_bot), zw, used_bot - z_bot, fc="white", ec=INK, lw=0.8,
                           hatch="///", alpha=0.6))
    ax.text(zx + zw / 2, (used_bot + z_bot) / 2, "margin 440 B", ha="center", va="center",
            fontsize=7.5, bbox=dict(fc="white", ec="none", pad=1))
    # dimension bars
    ax.annotate("", xy=(zx + zw + 0.25, z_top), xytext=(zx + zw + 0.25, used_bot),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.9, mutation_scale=7, color=INK,
                                shrinkA=0, shrinkB=0))
    ax.text(zx + zw + 0.35, (z_top + used_bot) / 2, "1096 B\nused", fontsize=7.5,
            va="center", ha="left")
    ax.annotate("", xy=(zx - 0.25, z_top), xytext=(zx - 0.25, z_bot),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.9, mutation_scale=7, color=INK,
                                shrinkA=0, shrinkB=0))
    ax.text(zx - 0.42, (z_top + z_bot) / 2, "1536 B allocated", fontsize=7.5,
            va="center", ha="center", rotation=90)
    # zoom lines
    wire(ax, [(sx + sw, sy + sh), (zx - 0.25, z_top)], color="#999999", lw=0.8, ls="--")
    wire(ax, [(sx + sw, sy), (zx - 0.25, z_bot)], color="#999999", lw=0.8, ls="--")
    ax.text(zx + zw / 2, 0.7, "792 B call chain + 2 × (104 + 48) B\nnested interrupts"
            " = 1096 B\n(frames under 60 B drawn enlarged)", ha="center", va="center",
            fontsize=7.2)
    save(fig, "20", "fig-20-4-memory-layout")


# ----------------------------------------------------------------------------
# Figure 20.5 — V-model
# ----------------------------------------------------------------------------
def fig_20_5():
    fig, ax = schematic(6.8, 4.3, xlim=(0, 13.6), ylim=(0.6, 9.2))
    wl, hl = 3.0, 0.8
    wr, hr = 3.6, 1.2
    left = [("Requirements", 1.8, 7.4), ("Architecture", 2.6, 5.6),
            ("Module design", 3.4, 3.8)]
    code = ("Code", 5.9, 1.7)
    right = [("System tests\ntens, hours,\nhardware-in-the-loop rig", 10.0, 7.4),
             ("Integration tests\nhundreds, minutes,\ndevelopment board", 9.2, 5.6),
             ("Unit tests\nthousands, seconds,\nhost PC, test doubles", 8.4, 3.8)]
    for t, x, y in left:
        cbox(ax, x, y, wl, hl, t, fc=FC_A, fs=9)
    cbox(ax, code[1], code[2], 2.2, 0.75, code[0], fc=FC_A, fs=9)
    for t, x, y in right:
        cbox(ax, x, y, wr, hr, t, fc=FC_B, fs=8)
    # left arm (descending)
    for (_, x0, y0), (_, x1, y1) in zip(left[:-1], left[1:]):
        wire_arrow(ax, [(x0, y0 - hl / 2), (x1, y1 + hl / 2)])
    wire_arrow(ax, [(3.4, 3.8 - hl / 2), (5.3, 1.7 + 0.375)])
    # right arm (ascending)
    wire_arrow(ax, [(6.5, 1.7 + 0.375), (8.4, 3.8 - hr / 2)])
    wire_arrow(ax, [(8.4, 3.8 + hr / 2), (9.2, 5.6 - hr / 2)])
    wire_arrow(ax, [(9.2, 5.6 + hr / 2), (10.0, 7.4 - hr / 2)])
    # verifies arrows
    for (_, xl, yl), (_, xr, yr) in zip(left, right):
        x0, x1 = xl + wl / 2 + 0.05, xr - wr / 2 - 0.05
        ax.annotate("", xy=(x0, yl), xytext=(x1, yr),
                    arrowprops=dict(arrowstyle="-|>", color=PINK, lw=1.1, ls="--",
                                    mutation_scale=9, shrinkA=0, shrinkB=0))
        ax.text((x0 + x1) / 2, yl + 0.08, "verifies", fontsize=7.8, color=PINK,
                ha="center", va="bottom")
    ax.text(2.6, 8.65, "design (decomposition)", fontsize=9, color=BLUE, ha="center",
            fontweight="bold")
    ax.text(9.2, 8.65, "testing (integration)", fontsize=9, color=GREEN, ha="center",
            fontweight="bold")
    # regression side bar
    ax.add_patch(FancyBboxPatch((12.2, 1.2), 1.1, 7.2,
                                boxstyle="round,pad=0,rounding_size=0.2",
                                fc=FC_C, ec=INK, lw=1.0))
    ax.text(12.75, 4.8, "Regression: all levels on every change (CI)", rotation=90,
            ha="center", va="center", fontsize=9)
    save(fig, "20", "fig-20-5-test-levels-v-model")


if __name__ == "__main__":
    fig_20_1()
    fig_20_2()
    fig_20_3()
    fig_20_4()
    fig_20_5()
