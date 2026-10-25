"""Figures for Chapter 11 — Digital Number Systems.

Run from the repository root:  python figures/scripts/ch11.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Arc, FancyArrowPatch  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.logic as logic  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, new_fig, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
RED = "#C62828"
MONO = "DejaVu Sans Mono"


# ----------------------------------------------------------------------------
def fig_11_1():
    """The 4-bit number wheel read as unsigned and two's complement."""
    fig = plt.figure(figsize=(5.4, 5.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-2.3, 2.3)
    ax.set_ylim(-2.1, 2.1)

    def ang(k):
        return np.radians(90 - 22.5 * k)

    def pt(k, r):
        a = ang(k)
        return r * np.cos(a), r * np.sin(a)

    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(1.15 * np.cos(th), 1.15 * np.sin(th), color=GRID, lw=6, zorder=0, solid_capstyle="butt")
    for k in range(16):
        x, y = pt(k, 1.15)
        ax.text(x, y, format(k, "04b"), ha="center", va="center", fontsize=9, family=MONO,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=INK, lw=0.8), zorder=3)
        xo, yo = pt(k, 1.55)
        ax.text(xo, yo, str(k), ha="center", va="center", fontsize=9.5, color=BLUE)
        s = k - 16 if k >= 8 else k
        xi, yi = pt(k, 0.80)
        ax.text(xi, yi, (f"{s:+d}".replace("-", "−")) if s else "0", ha="center", va="center", fontsize=9.5,
                color=ORANGE)
    # cuts
    for kc, col, lab, ha in ((7.5, RED, "signed overflow\n+7 + 1 = −8", "center"),
                             (-0.5, BLUE, "unsigned carry\n15 + 1 = 0", "center")):
        x0, y0 = pt(kc, 0.62)
        x1, y1 = pt(kc, 1.75)
        ax.plot([x0, x1], [y0, y1], color=col, lw=2.4, zorder=2)
        xl, yl = pt(kc, 1.95)
        ax.text(xl, yl, lab, ha=ha, va="center", fontsize=8.5, color=col)
    # add / subtract arrows
    ax.add_patch(FancyArrowPatch(pt(1.3, 1.85), pt(3.3, 1.85), connectionstyle="arc3,rad=-0.2",
                                 arrowstyle="-|>", mutation_scale=11, color=INK, lw=1.1))
    xt, yt = pt(2.3, 2.05)
    ax.text(xt, yt, "add 1", ha="left", va="center", fontsize=9)
    ax.add_patch(FancyArrowPatch(pt(14.7, 1.85), pt(12.7, 1.85), connectionstyle="arc3,rad=0.2",
                                 arrowstyle="-|>", mutation_scale=11, color=INK, lw=1.1))
    xt, yt = pt(13.7, 2.05)
    ax.text(xt, yt, "subtract 1", ha="right", va="center", fontsize=9)
    # example 5 + 4: dashed arc from 0101 to 1001
    r = 0.52
    t0, t1 = 90 - 22.5 * 9, 90 - 22.5 * 5
    ax.add_patch(Arc((0, 0), 2 * r, 2 * r, theta1=t0, theta2=t1, color=PINK, lw=1.6, ls="--"))
    xe, ye = pt(9, r)
    xd, yd = pt(8.8, r)
    ax.annotate("", xy=(xe, ye), xytext=(xd, yd),
                arrowprops=dict(arrowstyle="-|>", color=PINK, lw=1.4, mutation_scale=10))
    ax.text(0, 0.05, "5 + 4\noverflows:\n+5 → −7", ha="center", va="center", fontsize=8,
            color=PINK)
    # legend for rings
    ax.text(-2.25, -1.8, "outside: unsigned", color=BLUE, fontsize=8.5, ha="left")
    ax.text(-2.25, -2.0, "inside: two's complement", color=ORANGE, fontsize=8.5, ha="left")
    save(fig, "11", "fig-11-1-twos-complement-wheel")


# ----------------------------------------------------------------------------
def _carries(a, b, n=8):
    c = [0]
    for i in range(n):
        ai, bi = (a >> i) & 1, (b >> i) & 1
        c.append((ai & bi) | (c[-1] & (ai ^ bi)))
    return c   # c[0] .. c[n]


def fig_11_2():
    """8-bit ripple-carry adder with C, V, N, Z flag logic and two worked additions."""
    fig = plt.figure(figsize=(6.8, 5.0))
    ax = fig.add_axes([0.0, 0.40, 1.0, 0.60])
    ax.set_xlim(-0.6, 17.2)
    ax.set_ylim(-2.6, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    w, h, gap = 1.1, 1.1, 0.45
    xs = [0.2 + i * (w + gap) for i in range(8)]
    yb = 0.0
    for i, x in enumerate(xs):
        box(ax, x, yb, w, h, f"FA{i}", fontsize=8.5)
        # operands
        for dx, lab in ((0.3, f"$a_{i}$"), (0.8, f"$b_{i}$")):
            ax.annotate("", xy=(x + dx, yb + h), xytext=(x + dx, yb + h + 0.7),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7))
            ax.text(x + dx, yb + h + 0.75, lab, ha="center", va="bottom", fontsize=8)
        ax.annotate("", xy=(x + w / 2, yb - 0.7), xytext=(x + w / 2, yb),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7))
        ax.text(x + w / 2, yb - 0.75, f"$s_{i}$", ha="center", va="top", fontsize=8)
        if i < 7:
            ax.annotate("", xy=(x + w + gap, yb + h / 2), xytext=(x + w, yb + h / 2),
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7))
            ax.text(x + w + gap / 2, yb + h / 2 + 0.08, f"$c_{i + 1}$", ha="center", va="bottom",
                    fontsize=7.5)
    ax.annotate("", xy=(xs[0], yb + h / 2), xytext=(xs[0] - 0.55, yb + h / 2),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, mutation_scale=7))
    ax.text(xs[0] - 0.6, yb + h / 2 + 0.1, "$c_0$=0", ha="left", va="bottom", fontsize=7.5)
    # flag logic
    x7 = xs[7] + w
    yc8 = yb + h / 2
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, lw=1.0)
    xg = 14.6
    xor = d.add(logic.Xor().at((xg, 2.6)).anchor("in1").scale(0.85))
    nor = d.add(logic.Nor(inputs=8).at((xg, -0.85)).anchor("in1").scale(0.85))
    d.draw(show=False)
    xi1, xi2 = xor.absanchors["in1"], xor.absanchors["in2"]
    # C = c8 (also to the XOR's lower input)
    ax.plot([x7, 16.3], [yc8, yc8], color=INK, lw=1.0)
    ax.plot([13.4, 13.4, xi2.x], [yc8, xi2.y, xi2.y], color=INK, lw=1.0)
    ax.plot([13.4], [yc8], "o", ms=3, color=INK)
    ax.text(16.4, yc8, "C", fontsize=10, va="center", color=BLUE, weight="bold")
    ax.text(x7 + 0.1, yc8 + 0.08, "$c_8$", fontsize=8, va="bottom")
    # c7 tap to the XOR's upper input
    xc7 = xs[6] + w + gap / 2
    ax.plot([xc7, xc7, xi1.x], [yc8, xi1.y, xi1.y], color=INK, lw=1.0)
    ax.plot([xc7], [yc8], "o", ms=3, color=INK)
    xo = xor.absanchors["out"]
    ax.plot([xo.x, 16.3], [xo.y, xo.y], color=INK, lw=1.0)
    ax.text(16.4, xo.y, "V", fontsize=10, va="center", color=BLUE, weight="bold")
    ax.text(xg + 0.6, xo.y + 0.5, r"$c_8\oplus c_7$", fontsize=7.5, ha="center")
    # N = s7
    xs7 = xs[7] + w / 2
    yn = -0.38
    ax.plot([xs7, 16.3], [yn, yn], color=INK, lw=1.0)
    ax.plot([xs7], [yn], "o", ms=3, color=INK)
    ax.text(16.4, yn, "N", fontsize=10, va="center", color=BLUE, weight="bold")
    ax.text(13.4, yn + 0.05, "$s_7$", fontsize=7.5, va="bottom", ha="center")
    # sum bus to the 8-input NOR
    ybus = -1.85
    ax.plot([xs[0] + w / 2, xg - 0.3, xg - 0.3], [ybus, ybus, nor.absanchors["in8"].y],
            color=INK, lw=2.2)
    for x in xs:
        ax.plot([x + w / 2, x + w / 2], [yb - 1.15, ybus], color=INK, lw=0.8, ls=(0, (2, 1.5)))
    ax.plot([xg - 0.3, xg - 0.3], [nor.absanchors["in8"].y, nor.absanchors["in1"].y], color=INK,
            lw=2.2)
    for k in range(1, 9):
        yy = nor.absanchors[f"in{k}"].y
        ax.plot([xg - 0.3, nor.absanchors[f"in{k}"].x], [yy, yy], color=INK, lw=0.7)
    ax.text(xs[3] + w, ybus - 0.12, "$s_7 … s_0$ (8-bit bus)", fontsize=7.5, ha="center", va="top")
    no = nor.absanchors["out"]
    ax.plot([no.x, 16.3], [no.y, no.y], color=INK, lw=1.0)
    ax.text(16.4, no.y, "Z", fontsize=10, va="center", color=BLUE, weight="bold")

    # ---- two worked additions ----
    examples = ((0x64, 0x32, "(100)", "(50)"), (0xF0, 0x20, "(−16 or 240)", "(32)"))
    for j, (a, b, la, lb) in enumerate(examples):
        axt = fig.add_axes([0.02 + 0.5 * j, 0.0, 0.47, 0.38])
        axt.axis("off")
        axt.set_xlim(0, 10)
        axt.set_ylim(0, 6)
        s = (a + b) & 0xFF
        c = _carries(a, b)
        dx, x0 = 0.5, 1.6

        def xb(i):
            return x0 + (8 - i) * dx + (0.3 if i < 4 else 0.0)

        ytop = 5.3
        axt.text(0.1, ytop, "carry", fontsize=8, va="center", color="#555555")
        for i in range(1, 9):
            col = RED if i in (7, 8) else "#777777"
            axt.text(xb(i), ytop, str(c[i]), fontsize=8.5, family=MONO, ha="center", va="center",
                     color=col)
        axt.text(xb(8), ytop + 0.45, "$c_8$", fontsize=7, ha="center", color=RED)
        axt.text(xb(7), ytop + 0.45, "$c_7$", fontsize=7, ha="center", color=RED)
        for k, (nm, v, lab) in enumerate((("a", a, la), ("b", b, lb), ("s", s, ""))):
            y = ytop - 1.0 - k * 0.9
            axt.text(0.1, y, nm, fontsize=9, va="center")
            if k == 1:
                axt.text(xb(8), y, "+", fontsize=10, ha="center", va="center")
            for i in range(8):
                axt.text(xb(i), y, str((v >> i) & 1), fontsize=9.5, family=MONO, ha="center",
                         va="center")
            axt.text(xb(0) + 0.45, y, lab if k < 2 else f"(0x{s:02X})", fontsize=8.5, va="center")
        axt.plot([xb(8) - 0.25, xb(0) + 0.25], [ytop - 2.35, ytop - 2.35], color=INK, lw=0.8)
        C, V = c[8], c[8] ^ c[7]
        sv = s - 256 if s & 0x80 else s
        txt = (f"$c_7$ = {c[7]}, $c_8$ = {c[8]}  →  C = {C}, V = {V}, N = {s >> 7}, "
               f"Z = {int(s == 0)}")
        axt.text(0.1, 1.35, txt, fontsize=8, va="center")
        if j == 0:
            res = f"unsigned 150 (correct); signed {sv}: overflow".replace("-", "−")
        else:
            res = f"unsigned 16 (carry lost); signed {sv} (correct)"
        axt.text(0.1, 0.55, res, fontsize=8, va="center", color=RED if V else GREEN)
    save(fig, "11", "fig-11-2-adder-flags")


# ----------------------------------------------------------------------------
def fig_11_3():
    """Fixed-point data path from a Hall current sensor to Q15 current and Q30 power."""
    fig = plt.figure(figsize=(6.8, 4.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 13.6)
    ax.set_ylim(-1.1, 7.6)
    ax.set_aspect("equal")
    ax.axis("off")
    fs = 8
    bw, bh = 3.4, 2.3
    # row 1
    y1 = 4.9
    xs1 = [0.2, 5.1, 10.0]
    box(ax, xs1[0], y1, bw, bh, "Hall sensor + amplifier\n−50 A … +50 A\n→ 0 … 3.3 V\n(1.65 V at 0 A)",
        fontsize=fs, fc="#FCEFE6")
    box(ax, xs1[1], y1, bw, bh, "12-bit SAR ADC\noffset binary\n0x000 … 0xFFF\n+25 A → 0xC00 (3072)",
        fontsize=fs)
    box(ax, xs1[2], y1, bw, bh, "XOR 0x800\n(invert MSB)\n→ 0x400 = +1024\n12-bit two's complement",
        fontsize=fs)
    # row 2
    y2 = 0.9
    xs2 = [10.0, 5.1, 0.2]
    box(ax, xs2[0], y2, bw, bh, "sign-extend to 16 b,\nshift left 4\n→ 16 384 = 0.5\n(of 50 A: 25.0 A)",
        fontsize=fs)
    box(ax, xs2[1], y2, bw, bh, "multiply\nQ15 × Q15 → Q30\n16 384 × 16 384", fontsize=fs)
    box(ax, xs2[2], y2, bw, bh, "268 435 456\n(32-bit register)\n= 0.25 of 40 kW\n= 10.0 kW",
        fontsize=fs, fc="#E6F4EE")
    # arrows with word width labels
    ym1 = y1 + bh / 2
    for xa, lab in ((xs1[0] + bw, "analog\n0–3.3 V"), (xs1[1] + bw, "12 b\noffset binary")):
        arrow(ax, xa, ym1, xa + 1.5, ym1)
        ax.text(xa + 0.75, ym1 - 0.15, lab, ha="center", va="top", fontsize=7.5, color=BLUE)
    # down from XOR to sign-extend
    xm = xs1[2] + bw / 2
    arrow(ax, xm, y1, xm, y2 + bh)
    ax.text(xm + 0.15, (y1 + y2 + bh) / 2, "12 b two's\ncomplement", ha="left", va="center",
            fontsize=7.5, color=BLUE)
    ym2 = y2 + bh / 2
    arrow(ax, xs2[0], ym2, xs2[1] + bw, ym2)
    ax.text((xs2[0] + xs2[1] + bw) / 2, ym2 - 0.15, "16 b Q15\n(current)", ha="center", va="top",
            fontsize=7.5, color=BLUE)
    arrow(ax, xs2[1], ym2, xs2[2] + bw, ym2)
    ax.text((xs2[1] + xs2[2] + bw) / 2, ym2 - 0.15, "32 b Q30", ha="center", va="top", fontsize=7.5,
            color=BLUE)
    # voltage input to multiplier
    xv = xs2[1] + bw / 2
    arrow(ax, xv, -0.9, xv, y2)
    ax.text(xv + 0.15, -0.45, "DC-link voltage, 16 b Q15:\n16 384 = 400 V of 800 V", ha="left",
            va="center", fontsize=7.5, color=BLUE)
    ax.text(xs2[2] + bw / 2, y2 - 0.25, r"full scale 800 V × 50 A = 40 kW", ha="center", va="top",
            fontsize=7.5)
    save(fig, "11", "fig-11-3-fixed-point-current-path")


# ----------------------------------------------------------------------------
def _ulp_float(x, p, emin, emax_val):
    """Spacing of a binary FP format with p significand bits (incl. hidden) at magnitude x."""
    x = np.asarray(x, dtype=float)
    e = np.floor(np.log2(x))
    e = np.maximum(e, emin)                  # subnormal range: constant spacing
    u = 2.0 ** (e - (p - 1))
    u[x > emax_val] = np.nan
    return u


def fig_11_4():
    """Spacing of representable values versus magnitude."""
    fig, ax = new_fig(6.4, 4.2)
    x = np.logspace(-6, 6, 20001)
    u32 = _ulp_float(x, 24, -126, 3.4e38)
    u16 = _ulp_float(x, 11, -14, 65504)
    ubf = _ulp_float(x, 8, -126, 3.39e38)
    # verify against numpy where possible
    for xv in (1e-5, 3.3, 1000.0, 30000.0):
        assert np.isclose(np.spacing(np.float32(xv)), _ulp_float([xv], 24, -126, 3.4e38)[0], rtol=0)
        assert np.isclose(float(np.spacing(np.float16(xv))), _ulp_float([float(np.float16(xv))], 11, -14,
                                                                         65504)[0])
    ufx = np.where(x <= 32768, 2.0 ** -16, np.nan)
    ax.loglog(x, ubf, color=ORANGE, label="bfloat16 (8-bit significand)", drawstyle="steps-post")
    ax.loglog(x, u16, color=PINK, label="binary16 (11-bit significand)", drawstyle="steps-post")
    ax.loglog(x, u32, color=BLUE, label="binary32 (24-bit significand)", drawstyle="steps-post")
    ax.loglog(x, ufx, color=GREEN, lw=2.2, label="fixed point, 16 fractional bits")
    ax.plot([65504], [2.0 ** 5], "o", color=PINK, ms=5)
    ax.annotate("65 504\n(binary16 max)", xy=(65504, 32), xytext=(2e2, 60), fontsize=7.5,
                color=PINK, ha="center",
                arrowprops=dict(arrowstyle="-", color=PINK, lw=0.7))
    ax.plot([32768], [2.0 ** -16], "X", color=GREEN, ms=7)
    ax.text(3.6e4, 2.0 ** -16 / 2.2, "overflow at 32 768", fontsize=7.5, color=GREEN, va="top")
    ax.axvline(32768, color=INK, ls="--", lw=0.9)
    ax.plot([32768], [2.0 ** -8], "o", color=BLUE, ms=5)
    ax.annotate("binary32 spacing\n3.9 ms at 32 768 s", xy=(32768, 2.0 ** -8), xytext=(3e2, 1.5e-3),
                fontsize=7.5, color=BLUE, ha="center",
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.8, mutation_scale=8))
    ax.annotate("subnormals:\nconstant spacing\n$2^{-24}$", xy=(2e-5, 2.0 ** -24), xytext=(1.2e-6, 2e-11),
                fontsize=7.5, color=PINK, ha="left",
                arrowprops=dict(arrowstyle="-|>", color=PINK, lw=0.8, mutation_scale=8))
    ax.text(3e-2, 1.1e-11, "floating point: relative spacing constant\n(staircase doubles at every power of 2)",
            fontsize=7.5, ha="left", va="bottom")
    ax.text(1.3e-6, 3e-5, "fixed point: absolute spacing\nconstant, $2^{-16}=1.53\\times10^{-5}$",
            fontsize=7.5, color=GREEN, ha="left", va="bottom")
    ax.set_xlim(1e-6, 1e6)
    ax.set_ylim(1e-12, 1e3)
    ax.set_xlabel("magnitude $|x|$")
    ax.set_ylabel("spacing to next representable value")
    ax.grid(True, which="major", color=GRID, lw=0.5)
    ax.legend(fontsize=7.5, loc="upper left")
    save(fig, "11", "fig-11-4-float-spacing")


# ----------------------------------------------------------------------------
def _bitbar(ax, y, fields, value=None, h=0.9, x0=0.0, cw=0.5, fs=7.5):
    """Draw a 32-cell register bar. fields: list of (hi, lo, name, color)."""
    for b in range(32):
        x = x0 + (31 - b) * cw
        ax.text(x + cw / 2, y + h + 0.08, str(b), ha="center", va="bottom", fontsize=5.8,
                color="#555555")
    for hi, lo, name, col in fields:
        xl = x0 + (31 - hi) * cw
        wd = (hi - lo + 1) * cw
        ax.add_patch(Rectangle((xl, y), wd, h, fc=col, ec=INK, lw=0.8))
        if name:
            rot = 90 if (wd < 0.9 and len(name) > 2) else 0
            ax.text(xl + wd / 2, y + h / 2, name, ha="center", va="center", fontsize=fs,
                    rotation=rot)
    if value is not None:
        for b in range(32):
            x = x0 + (31 - b) * cw
            bit = (value >> b) & 1
            ax.text(x + cw / 2, y - 0.08, str(bit), ha="center", va="top", fontsize=7,
                    family=MONO, color=RED if bit else "#888888", weight="bold" if bit else None)


def fig_11_5():
    """Timer control register bit fields and the BSRR set/reset layout."""
    fig = plt.figure(figsize=(6.8, 4.4))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(-0.3, 16.6)
    ax.set_ylim(0.3, 10.6)
    ax.axis("off")
    grey = "#D9D9D9"
    flag = "#DCEAF5"
    field = "#FBE3CF"
    # control register
    ax.text(0.0, 10.25, "Illustrative timer control register (CR1)", fontsize=9, weight="bold")
    fields = [(31, 10, "reserved", grey), (9, 8, "CKD", field), (7, 7, "ARPE", flag),
              (6, 5, "CMS", field), (4, 4, "DIR", flag), (3, 3, "OPM", flag), (2, 2, "URS", flag),
              (1, 1, "UDIS", flag), (0, 0, "CEN", flag)]
    _bitbar(ax, 8.2, fields, value=0x81)
    ax.text(0.0, 7.45, "value 0x0000_0081:", fontsize=8, va="top")
    ax.text(0.0, 6.95, "CEN = 1 (counter enabled), ARPE = 1 (auto-reload preload), all other fields 0",
            fontsize=8, va="top", color=RED)
    ax.text(0.0, 6.35, "1-bit Boolean flags", fontsize=7.5, va="top",
            bbox=dict(fc=flag, ec=INK, lw=0.6, pad=2))
    ax.text(3.3, 6.35, "multi-bit fields: CMS[1:0] centre-aligned mode, CKD[1:0] clock division",
            fontsize=7.5, va="top", bbox=dict(fc=field, ec=INK, lw=0.6, pad=2))
    # BSRR
    ax.text(0.0, 5.05, "GPIO bit set/reset register (BSRR)", fontsize=9, weight="bold")
    bs = [(31 - i, 31 - i, f"BR{15 - i}", "#F6D5D5") for i in range(16)]
    bs += [(15 - i, 15 - i, f"BS{15 - i}", "#D5EEDF") for i in range(16)]
    _bitbar(ax, 3.0, bs, fs=6.0)
    ax.annotate("", xy=(0.0, 2.75), xytext=(8.0, 2.75),
                arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=0.9, mutation_scale=8))
    ax.text(4.0, 2.65, "bits 31:16  BR0–BR15: write 1 to reset pin", ha="center", va="top",
            fontsize=7.5, color=RED)
    ax.annotate("", xy=(8.0, 2.75), xytext=(16.0, 2.75),
                arrowprops=dict(arrowstyle="<|-|>", color=GREEN, lw=0.9, mutation_scale=8))
    ax.text(12.0, 2.65, "bits 15:0  BS0–BS15: write 1 to set pin", ha="center", va="top",
            fontsize=7.5, color=GREEN)
    # example writes
    ax.text(0.0, 1.6, "GPIOA_BSRR = 0x0000_0020", family=MONO, fontsize=8, va="center")
    ax.text(5.0, 1.6, "→ bit 5 = BS5: set PA5 (LED on); zeros leave other pins unchanged",
            fontsize=7.5, va="center")
    ax.text(0.0, 0.8, "GPIOA_BSRR = 0x0020_0000", family=MONO, fontsize=8, va="center")
    ax.text(5.0, 0.8, "→ bit 21 = BR5: reset PA5 (LED off)", fontsize=7.5, va="center")
    for b, col in ((5, GREEN), (21, RED)):
        x = (31 - b) * 0.5
        ax.add_patch(Rectangle((x, 3.0), 0.5, 0.9, fill=False, ec=col, lw=2.0))
    save(fig, "11", "fig-11-5-register-bit-fields")


if __name__ == "__main__":
    fig_11_1()
    fig_11_2()
    fig_11_3()
    fig_11_4()
    fig_11_5()
