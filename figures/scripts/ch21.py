"""Figures for Chapter 21 — C and C++ for Engineering.

Run from the repository root:  python figures/scripts/ch21.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Patch, Circle  # noqa: E402

from figstyle import COLORS, INK, box, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4]
RED = "#C0392B"
FC_A = "#DCEBF7"     # RAM / data
FC_B = "#E3F2E6"     # code
FC_C = "#FFF4D6"     # flash tables / tools
FC_D = "#FBE2DF"     # warnings
PAD_FC = "#EEEEEE"
MONO = "monospace"


def wire(ax, pts, color=INK, lw=1.2, ls="-", **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", **kw)


def wire_arrow(ax, pts, color=INK, lw=1.2, ls="-", ms=10):
    if len(pts) > 2:
        wire(ax, pts[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def rect(ax, x, y, w, h, fc="white", ec=INK, lw=1.0, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))


def cbox(ax, x, y, w, h, text, fc=FC_A, fs=8.5, **kw):
    box(ax, x - w / 2, y - h / 2, w, h, text, fc=fc, fontsize=fs, **kw)


def step_badge(ax, x, y, n, color=RED):
    ax.add_patch(Circle((x, y), 0.22, fc=color, ec="none", zorder=6))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=8, color="white",
            fontweight="bold", zorder=7)


# ----------------------------------------------------------------------------
# Figure 21.1 — pointer arithmetic
# ----------------------------------------------------------------------------
def fig_21_1():
    fig, ax = schematic(6.8, 5.25, xlim=(0, 14), ylim=(-0.5, 10.3))
    x0, cw, y0, ch = 0.9, 0.6, 6.9, 0.7
    base = 0x20000100
    ax.text(0.2, 10.0, "int16_t buf[64] at 0x2000 0100 (2 bytes per element)",
            fontsize=9, fontweight="bold", va="center")
    for i in range(21):
        fc = "#9CC7E8" if 10 <= i < 18 else "white"
        rect(ax, x0 + i * cw, y0, cw, ch, fc=fc, lw=0.9)
        ax.text(x0 + (i + 0.5) * cw, y0 + ch / 2, str(i), ha="center", va="center",
                fontsize=7.5)
        a = base + 2 * i
        ax.text(x0 + (i + 0.5) * cw, y0 - 0.08, f"{a & 0xFFFF:04X}",
                rotation=90, ha="center", va="top", fontsize=6.5, family=MONO)
    ax.text(x0 + 21 * cw + 0.05, y0 + ch / 2, "…", fontsize=10, va="center")
    ax.text(x0 - 0.1, y0 - 0.4, "addr\n0x2000…", fontsize=6.0, ha="right",
            va="center", family=MONO, color="#555555")
    # p and end arrows
    xp, xe = x0 + 10 * cw, x0 + 18 * cw
    wire_arrow(ax, [(xp, 9.25), (xp, y0 + ch)], color=BLUE)
    ax.text(xp - 0.1, 9.45, "p = &buf[10] = 0x2000 0114", color=BLUE, fontsize=8.5,
            ha="right", va="center", fontweight="bold")
    wire_arrow(ax, [(xe, 9.25), (xe, y0 + ch)], color=ORANGE)
    ax.text(xe + 0.1, 9.45, "end = p + 8 = 0x2000 0124", color=ORANGE, fontsize=8.5,
            ha="left", va="center", fontweight="bold")
    # bracket over summed elements
    yb = y0 + ch + 0.2
    wire(ax, [(xp + 0.05, yb), (xp + 0.05, yb + 0.15), (xe - 0.05, yb + 0.15),
              (xe - 0.05, yb)], color=INK, lw=1.0)
    ax.text((xp + xe) / 2, yb + 0.28, "8 elements summed\n(+2 bytes per step)",
            ha="center", va="bottom", fontsize=7.8)

    # byte view
    yv, bw = 4.3, cw / 2
    a_first = 0x110
    nbytes = 24
    xb0 = x0 + (a_first - 0x100) / 2 * cw
    ax.text(xb0 - 0.15, yv + ch / 2, "same memory as\nconst uint8_t *q:", fontsize=8,
            ha="right", va="center")
    for k in range(nbytes):
        a = a_first + k
        inside = 0x114 <= a < 0x11C
        rect(ax, xb0 + k * bw, yv, bw, ch, fc="#F6D0B0" if inside else "white", lw=0.7)
        if k % 2 == 0:
            ax.text(xb0 + k * bw + 0.02, yv - 0.08, f"{a & 0xFFF:03X}", rotation=90,
                    ha="left", va="top", fontsize=6.0, family=MONO)
    ax.text(xb0 + nbytes * bw + 0.05, yv + ch / 2, "…", fontsize=10, va="center")
    xq, xq8 = x0 + 10 * cw, x0 + 10 * cw + 8 * bw
    wire_arrow(ax, [(xq, yv + ch + 0.75), (xq, yv + ch)], color=BLUE, ms=8)
    ax.text(xq - 0.1, yv + ch + 0.65, "q = 0x2000 0114", color=BLUE, fontsize=8,
            ha="right", va="center")
    wire_arrow(ax, [(xq8, yv + ch + 0.75), (xq8, yv + ch)], color=ORANGE, ms=8)
    ax.text(xq8 + 0.1, yv + ch + 0.65, "q + 8 = 0x2000 011C (8 bytes on)", color=ORANGE,
            fontsize=8, ha="left", va="center")
    # dashed alignment guides from int16 view
    for x in (xp, xe):
        wire(ax, [(x, y0), (x, yv + ch)], color="#BBBBBB", lw=0.7, ls=":")

    # function-pointer table
    ty = 0.5
    ax.text(0.2, 3.05, "static const cmd_handler_t handlers[] (flash)", fontsize=8.5,
            fontweight="bold", va="center")
    tx, tw, th = 2.2, 3.8, 0.6
    entries = [("0x0800 4000", "[0] &cmd_reset"), ("0x0800 4004", "[1] &cmd_set_speed")]
    for j, (addr, lab) in enumerate(entries):
        yy = ty + 1.3 - j * th
        rect(ax, tx, yy, tw, th, fc=FC_C, lw=0.9)
        ax.text(tx + 0.1, yy + th / 2, lab, fontsize=7.5, va="center", family=MONO)
        ax.text(tx - 0.1, yy + th / 2, addr, fontsize=7, va="center", ha="right",
                family=MONO)
    cbox(ax, 8.6, ty + 1.95, 3.4, 0.65, "cmd_reset() code", fc=FC_B, fs=7.8)
    cbox(ax, 8.6, ty + 0.55, 3.4, 0.65, "cmd_set_speed() code", fc=FC_B, fs=7.8)
    wire_arrow(ax, [(tx + tw, ty + 1.6), (6.4, ty + 1.6), (6.4, ty + 1.95), (6.9, ty + 1.95)])
    wire_arrow(ax, [(tx + tw, ty + 1.0), (6.4, ty + 1.0), (6.4, ty + 0.55), (6.9, ty + 0.55)])
    cbox(ax, 12.4, ty + 1.95, 3.2, 1.2, "dispatch(opcode = 1)\nbounds check:\nopcode < 2",
         fc=FC_D, fs=7.0)
    wire_arrow(ax, [(12.4, ty + 1.35), (12.4, ty - 0.2), (tx + tw / 2, ty - 0.2),
                    (tx + tw / 2, ty + 1.0 - th / 2)], color=RED)
    ax.text(9.0, ty - 0.3, "handlers[1](args, len): indirect call", fontsize=7.5,
            color=RED, ha="center", va="top")
    save(fig, "21", "fig-21-1-pointer-arithmetic")


# ----------------------------------------------------------------------------
# Figure 21.2 — struct padding
# ----------------------------------------------------------------------------
def fig_21_2():
    fig, ax = schematic(6.8, 4.0, xlim=(0, 13.6), ylim=(1.5, 9.5))
    cw, ch = 1.2, 0.62
    x0 = 2.6
    colors = {"valid": "#F2D7B6", "timestamp": "#9CC7E8", "channel": "#F6C6D8",
              "voltage": "#B7E0C4", "flags": "#FBE2A8", "energy": "#C9C3E6"}
    bad = [("valid", 0, 1), ("pad", 1, 3), ("timestamp", 4, 4), ("channel", 8, 1),
           ("pad", 9, 3), ("voltage", 12, 4), ("flags", 16, 2), ("pad", 18, 6),
           ("energy", 24, 8)]
    good = [("energy", 0, 8), ("timestamp", 8, 4), ("voltage", 12, 4), ("flags", 16, 2),
            ("valid", 18, 1), ("channel", 19, 1), ("pad", 20, 4)]

    def draw(layout, ytop, title, total):
        ax.text(0.2, ytop + 0.7, title, fontsize=9, fontweight="bold", va="center")
        ax.text(x0 - 0.1, ytop + 0.12, "offset", fontsize=7, color="#555555", ha="right", va="bottom")
        for k in range(8):
            ax.text(x0 + (k + 0.5) * cw, ytop + 0.12, str(k), fontsize=7, ha="center",
                    va="bottom", color="#666666")
        nrows = total // 8
        for name, off, size in layout:
            for b in range(off, off + size):
                r, c = divmod(b, 8)
                x, y = x0 + c * cw, ytop - (r + 1) * ch
                if name == "pad":
                    rect(ax, x, y, cw, ch, fc=PAD_FC, lw=0.6, hatch="////", ec="#888888")
                else:
                    rect(ax, x, y, cw, ch, fc=colors[name], lw=0, ec="none")
            # field outline per row segment and label
            b = off
            first = True
            while b < off + size:
                r, c = divmod(b, 8)
                seg = min(off + size - b, 8 - c)
                x, y = x0 + c * cw, ytop - (r + 1) * ch
                rect(ax, x, y, seg * cw, ch, fc="none", lw=1.2, ec=INK)
                if name != "pad" and first:
                    lab = name if seg * cw > 1.0 else name[:4]
                    ax.text(x + seg * cw / 2, y + ch / 2, lab, ha="center", va="center",
                            fontsize=7.8 if seg > 1 else 7.0)
                first = False
                b += seg
        for r in range(nrows):
            ax.text(x0 - 0.1, ytop - (r + 0.5) * ch, f"{8 * r:2d}", ha="right",
                    va="center", fontsize=7.5, family=MONO, color="#555555")
        return ytop - nrows * ch

    yb = draw(bad, 8.4, "rec_bad_t  (field order as first written)", 32)
    ax.text(x0 + 8 * cw + 0.25, 8.4 - 2 * ch, "32 bytes\n20 data\n12 padding (37.5 %)",
            fontsize=8, va="center")
    yg = draw(good, yb - 1.45, "rec_good_t  (largest alignment first)", 24)
    ax.text(x0 + 8 * cw + 0.25, yb - 1.45 - 1.5 * ch, "24 bytes\n20 data\n4 tail padding",
            fontsize=8, va="center")
    # legend
    handles = [Patch(fc=c, ec=INK, label=n) for n, c in colors.items()]
    handles.append(Patch(fc=PAD_FC, ec="#888888", hatch="////", label="padding"))
    ax.legend(handles=handles, loc="lower center", ncol=7, fontsize=7.5,
              bbox_to_anchor=(0.5, -0.02), handlelength=1.2, columnspacing=0.9)
    save(fig, "21", "fig-21-2-struct-padding")


# ----------------------------------------------------------------------------
# Figure 21.3 — register block and W1C
# ----------------------------------------------------------------------------
def fig_21_3():
    fig, ax = schematic(6.8, 5.5, xlim=(0, 14), ylim=(0.9, 12.2))
    regs = [("0x4001 2000", "CR", "+0x00  CR", FC_A),
            ("0x4001 2004", "SR", "+0x04  SR", FC_A),
            ("0x4001 2008", "DR", "+0x08  DR\n(const volatile)", "#C9DFF0"),
            ("0x4001 200C", "RESERVED", "+0x0C  RESERVED0", PAD_FC),
            ("0x4001 2010", "SMPR", "+0x10  SMPR", FC_A)]
    ax.text(0.15, 11.75, "ADC1 registers and the", fontsize=9, fontweight="bold")
    ax.text(0.15, 11.25, "struct adc_regs_t overlay", fontsize=9, fontweight="bold")
    ax.text(3.35, 10.55, "member offset", fontsize=7, color="#555555")
    rx, rw, rh = 1.85, 1.35, 0.9
    for i, (addr, name, member, fc) in enumerate(regs):
        y = 9.45 - i * 1.2
        res = name == "RESERVED"
        rect(ax, rx, y, rw, rh, fc=fc, lw=1.0, hatch="////" if res else "",
             ec="#777777" if res else INK)
        ax.text(rx + rw / 2, y + rh / 2, name, ha="center", va="center",
                fontsize=6.5 if res else 8.5, fontweight="bold",
                bbox=dict(fc="white", ec="none", pad=0.4) if res else None)
        ax.text(rx - 0.08, y + rh / 2, addr, ha="right", va="center", fontsize=6.5,
                family=MONO)
        wire(ax, [(rx + rw, y + rh / 2), (3.35, y + rh / 2)], color="#999999", lw=0.8,
             ls=":")
        ax.text(3.4, y + rh / 2, member, ha="left", va="center", fontsize=7.2)
    ax.text(0.15, 3.15, "static_assert(offsetof(", fontsize=7, family=MONO, color=GREEN)
    ax.text(0.15, 2.7, "  adc_regs_t, SMPR) == 0x10u);", fontsize=7, family=MONO,
            color=GREEN)
    ax.text(0.15, 2.05, "a missing member becomes a", fontsize=7.5, color=GREEN)
    ax.text(0.15, 1.65, "compile error, not a write to", fontsize=7.5, color=GREEN)
    ax.text(0.15, 1.25, "the wrong register", fontsize=7.5, color=GREEN)

    bx0, bw, bh = 9.0, 0.75, 0.55

    def bits(y, vals, label, colors=None):
        ax.text(bx0 - 0.15, y + bh / 2, label, ha="right", va="center", fontsize=7.8,
                family=MONO)
        for k, v in enumerate(vals):          # k = 0 is bit 3 (left)
            fc = colors[k] if colors and colors[k] else "white"
            rect(ax, bx0 + k * bw, y, bw, bh, fc=fc, lw=0.9)
            ax.text(bx0 + (k + 0.5) * bw, y + bh / 2, str(v), ha="center", va="center",
                    fontsize=8.5, family=MONO)

    ax.text(6.6, 11.75, "Status register SR (write 1 to clear)", fontsize=9,
            fontweight="bold")
    for k, lab in enumerate(["b3", "b2", "OVR\nb1", "EOC\nb0"]):
        ax.text(bx0 + (k + 0.5) * bw, 10.5, lab, ha="center", va="bottom", fontsize=7)
    hot = "#F6D0B0"
    bits(9.85, [0, 0, 1, 1], "SR reads 0x3", [None, None, hot, hot])

    # case 1: SR |= EOC
    ax.add_patch(FancyBboxPatch((6.5, 5.55), 7.4, 3.85,
                                boxstyle="round,pad=0,rounding_size=0.15",
                                fc="#FDF0EE", ec=RED, lw=1.0))
    ax.text(6.7, 9.05, "ADC1->SR |= ADC_SR_EOC;", fontsize=8, family=MONO, color=RED,
            fontweight="bold", va="center")
    bits(8.0, [0, 0, 1, 1], "read 0x3")
    bits(7.25, [0, 0, 0, 1], "OR 0x1")
    bits(6.5, [0, 0, 1, 1], "write 0x3", [None, None, "#F4B6AE", "#F4B6AE"])
    ax.text(bx0 + 4 * bw + 0.12, 6.5 + bh / 2, "both flags\ncleared", fontsize=7.3,
            color=RED, va="center")
    ax.text(6.7, 5.9, "OVR cleared too: overrun lost", fontsize=7.8, color=RED,
            fontweight="bold", va="center")

    # case 2: SR = EOC
    ax.add_patch(FancyBboxPatch((6.5, 1.1), 7.4, 4.1,
                                boxstyle="round,pad=0,rounding_size=0.15",
                                fc="#EEF7F0", ec=GREEN, lw=1.0))
    ax.text(6.7, 4.85, "ADC1->SR = ADC_SR_EOC;", fontsize=8, family=MONO, color=GREEN,
            fontweight="bold", va="center")
    bits(3.75, [0, 0, 0, 1], "write 0x1", [None, None, None, "#B7E0C4"])
    bits(2.65, [0, 0, 1, 0], "SR after", [None, None, hot, None])
    ax.text(bx0 + 4 * bw + 0.12, 3.75 + bh / 2, "EOC\ncleared", fontsize=7.3,
            color=GREEN, va="center")
    ax.text(bx0 + 4 * bw + 0.12, 2.65 + bh / 2, "OVR\nstill 1", fontsize=7.3,
            color=GREEN, va="center")
    ax.text(6.7, 1.55, "zeros written to W1C bits have no effect", fontsize=7.6,
            color=GREEN, va="center")
    save(fig, "21", "fig-21-3-register-block-w1c")


# ----------------------------------------------------------------------------
# Figure 21.4 — vtable dispatch
# ----------------------------------------------------------------------------
def fig_21_4():
    fig, ax = schematic(6.8, 4.9, xlim=(0, 14), ylim=(0, 10.1))
    ax.add_patch(FancyBboxPatch((0.2, 0.9), 4.9, 8.7, boxstyle="round,pad=0,rounding_size=0.2",
                                fc="#F3F8FC", ec="#9BB8D3", lw=1.0))
    ax.add_patch(FancyBboxPatch((5.5, 0.9), 8.3, 8.7, boxstyle="round,pad=0,rounding_size=0.2",
                                fc="#FFFBEF", ec="#D9C48A", lw=1.0))
    ax.text(2.65, 9.15, "RAM", fontsize=9.5, fontweight="bold", ha="center")
    ax.text(9.65, 9.15, "Flash", fontsize=9.5, fontweight="bold", ha="center")

    ox, ow, oh = 0.6, 2.7, 0.55
    objs = [("ntc0 : Ntc", 7.9, "ch_ = 3"), ("tmp0 : Tmp117", 5.0, "addr_ = 0x48")]
    vp = {}
    for name, ytop, mem in objs:
        ax.text(ox, ytop + 0.2, name, fontsize=8.5, family=MONO, fontweight="bold")
        rect(ax, ox, ytop - oh, ow, oh, fc=FC_A)
        ax.text(ox + 0.1, ytop - oh / 2, "vptr  (4 B)", fontsize=7.8, family=MONO,
                va="center")
        rect(ax, ox, ytop - 2 * oh, ow, oh, fc="white")
        ax.text(ox + 0.1, ytop - 1.5 * oh, mem, fontsize=7.8, family=MONO, va="center")
        vp[name] = (ox + ow, ytop - oh / 2)
    # monitor holding a reference
    rect(ax, 0.5, 1.3, 4.3, 1.05, fc=FC_D)
    ax.text(2.65, 2.0, "OvertempMonitor", fontsize=8, family=MONO, ha="center",
            va="center", fontweight="bold")
    ax.text(2.65, 1.6, "TemperatureSensor& s_", fontsize=7, family=MONO, ha="center",
            va="center")
    wire_arrow(ax, [(1.6, 2.35), (1.6, 5.0 - 2 * oh)], color=PINK, ls="--")
    ax.text(1.72, 3.2, "s_ refers to one\nsensor object", fontsize=7, color=PINK,
            ha="left", va="center")

    vx, vw, vh = 6.1, 3.4, 0.55
    vts = [("vtable for Ntc", 8.2), ("vtable for Tmp117", 5.3)]
    slot_y = {}
    for title, ytop in vts:
        ax.text(vx, ytop + 0.2, title, fontsize=8.5, fontweight="bold")
        rect(ax, vx, ytop - vh, vw, vh, fc=FC_C)
        ax.text(vx + 0.1, ytop - vh / 2, "[0] ~destructor", fontsize=7.5, family=MONO,
                va="center")
        rect(ax, vx, ytop - 2 * vh, vw, vh, fc=FC_C)
        ax.text(vx + 0.1, ytop - 1.5 * vh, "[1] read_celsius", fontsize=7.5, family=MONO,
                va="center")
        slot_y[title] = ytop - 1.5 * vh
    cx = 11.85
    cbox(ax, cx, 7.65, 3.3, 0.8, "Ntc::read_celsius()\nADC + table lookup", fc=FC_B, fs=7.3)
    cbox(ax, cx, 4.75, 3.3, 0.8, "Tmp117::read_celsius()\nI2C read", fc=FC_B, fs=7.3)
    for (oname, _, _), (vtitle, ytop) in zip(objs, vts):
        x1, y1 = vp[oname]
        wire_arrow(ax, [(x1, y1), (5.8, y1), (5.8, ytop - vh / 2), (vx, ytop - vh / 2)],
                   color=BLUE)
    wire_arrow(ax, [(vx + vw, slot_y["vtable for Ntc"]), (cx - 1.65, 7.65)], color=GREEN)
    wire_arrow(ax, [(vx + vw, slot_y["vtable for Tmp117"]), (cx - 1.65, 4.75)], color=GREEN)
    # numbered steps for the call s_.read_celsius() on tmp0
    step_badge(ax, 4.45, vp["tmp0 : Tmp117"][1] + 0.3, 1)
    step_badge(ax, vx - 0.42, slot_y["vtable for Tmp117"], 2)
    step_badge(ax, 9.95, 4.15, 3)
    steps = ["load vptr from the object (LDR)",
             "load function address from vtable slot [1] (LDR)",
             "indirect branch to it (BLX)"]
    ax.text(5.8, 2.75, "Virtual call  s_.read_celsius()  on tmp0:", fontsize=7.8,
            fontweight="bold", va="center")
    for k, t in enumerate(steps):
        y = 2.2 - k * 0.48
        step_badge(ax, 6.05, y, k + 1)
        ax.text(6.4, y, t, fontsize=7.8, va="center")
    ax.text(7.0, 0.45, "about 3-5 extra cycles per call on Cortex-M4; "
            "6 calls × 5 cycles × 20 kHz = 0.6 M cycles/s = 0.36 % of 168 MHz",
            fontsize=7.3, ha="center", va="center")
    save(fig, "21", "fig-21-4-vtable-dispatch")


# ----------------------------------------------------------------------------
# Figure 21.5 — build and load
# ----------------------------------------------------------------------------
def fig_21_5():
    fig, ax = schematic(6.8, 5.2, xlim=(0, 14), ylim=(0, 10.7))
    srcs = ["main.c", "pid.c", "motor.cpp"]
    objs = ["main.o", "pid.o", "motor.o"]
    ys3 = [9.6, 8.9, 8.2]
    for s_, y in zip(srcs, ys3):
        cbox(ax, 0.75, y, 1.4, 0.5, s_, fc="white", fs=6.9)
    for k, y in enumerate(ys3):
        wire(ax, [(1.45, y), (1.6, y), (1.6, 8.9)], lw=1.0)
    stages = [("preprocessor", 2.9, 1.8), ("compiler\n(-O2)", 4.85, 1.5),
              ("assembler", 6.7, 1.6)]
    for t, x, w in stages:
        cbox(ax, x, 8.9, w, 0.9, t, fc=FC_C, fs=7.2)
    wire_arrow(ax, [(1.6, 8.9), (2.0, 8.9)], ms=8)
    wire_arrow(ax, [(3.8, 8.9), (4.1, 8.9)], ms=8)
    wire_arrow(ax, [(5.6, 8.9), (5.9, 8.9)], ms=8)
    wire(ax, [(7.5, 8.9), (7.7, 8.9)])
    for o, y in zip(objs, ys3):
        cbox(ax, 8.6, y, 1.3, 0.5, o, fc=FC_A, fs=7.2)
        wire_arrow(ax, [(7.7, 8.9), (7.7, y), (7.95, y)], ms=7)
        wire(ax, [(9.25, y), (9.5, y), (9.5, 8.9)], lw=1.0)
    ax.text(8.6, 7.8, "sections .text .rodata .data .bss\n+ symbol tables", fontsize=6.6,
            ha="center", va="top", color="#444444")
    cbox(ax, 10.5, 8.9, 1.3, 0.9, "linker", fc=FC_C, fs=7.5)
    wire_arrow(ax, [(9.5, 8.9), (9.85, 8.9)], ms=8)
    ax.text(10.5, 10.05, "stm32f407.ld, libc, libm", fontsize=6.8, ha="center",
            color="#444444")
    wire_arrow(ax, [(10.5, 9.9), (10.5, 9.35)], ms=7)
    cbox(ax, 12.65, 8.9, 1.9, 0.9, "app.elf\n+ app.map", fc=FC_A, fs=7.2)
    wire_arrow(ax, [(11.15, 8.9), (11.7, 8.9)], ms=8)
    cbox(ax, 12.65, 7.35, 1.9, 0.6, "objcopy", fc=FC_C, fs=7.2)
    wire_arrow(ax, [(12.65, 8.45), (12.65, 7.65)], ms=8)
    cbox(ax, 12.65, 6.2, 1.9, 0.6, "app.bin", fc=FC_A, fs=7.2)
    wire_arrow(ax, [(12.65, 7.05), (12.65, 6.5)], ms=8)
    cbox(ax, 10.0, 6.2, 2.7, 0.6, "flash programmer", fc=FC_B, fs=7.2)
    wire_arrow(ax, [(11.7, 6.2), (11.35, 6.2)], ms=8)

    # memory maps
    my0, mh = 0.7, 4.2
    fx, fw = 1.8, 3.6
    ax.text(fx + fw / 2, my0 + mh + 0.65, "Flash  (0x0800 0000)", fontsize=8.5,
            fontweight="bold", ha="center")
    fl = [(0.45, "vector table", "#F2D7B6"), (2.3, ".text + .rodata\n23 456 B", FC_B),
          (0.55, ".data load image 512 B", FC_C), (0.9, "free", "white")]
    y = my0
    fpos = {}
    for h, t, c in fl:
        rect(ax, fx, y, fw, h, fc=c)
        ax.text(fx + fw / 2, y + h / 2, t, ha="center", va="center", fontsize=7.5,
                color="#888888" if t == "free" else INK)
        fpos[t] = (y, h)
        y += h
    ax.text(fx - 0.08, my0, "0x0800 0000", ha="right", va="center", fontsize=6.5,
            family=MONO)
    rx, rw = 8.4, 3.6
    ax.text(rx + rw / 2, my0 + mh + 0.65, "RAM  (0x2000 0000)", fontsize=8.5,
            fontweight="bold", ha="center")
    rl = [(0.55, ".data 512 B", FC_C), (0.95, ".bss 6144 B", "#E8E8E8"),
          (0.6, "heap ↑", "#E3F2E6"), (1.2, "free", "white"), (0.9, "stack ↓ 1.5 KB", FC_D)]
    y = my0
    rpos = {}
    for h, t, c in rl:
        rect(ax, rx, y, rw, h, fc=c)
        ax.text(rx + rw / 2, y + h / 2, t, ha="center", va="center", fontsize=7.5,
                color="#888888" if t == "free" else INK)
        rpos[t] = (y, h)
        y += h
    ax.text(rx - 0.08, my0, "0x2000 0000", ha="right", va="center", fontsize=6.5,
            family=MONO)
    ax.text(rx + rw + 0.08, y, "0x2002 0000\n(_estack)", ha="left", va="center",
            fontsize=6.5, family=MONO)
    # copy and zero arrows
    dy, dh = fpos[".data load image 512 B"]
    ry, rh = rpos[".data 512 B"]
    ax.annotate("", xy=(rx, ry + rh / 2), xytext=(fx + fw, dy + dh / 2),
                arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.4, mutation_scale=11,
                                connectionstyle="arc3,rad=0.2", shrinkA=0, shrinkB=0))
    ax.text(7.3, 3.4, "copied by\nReset_Handler", fontsize=7.8, color=ORANGE,
            ha="center", va="center")
    by, bh = rpos[".bss 6144 B"]
    ax.annotate("zeroed", xy=(rx + rw, by + bh / 2), xytext=(rx + rw + 0.6, by + bh / 2),
                fontsize=7.8, color="#555555", va="center",
                arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.0,
                                mutation_scale=8))
    # programmer -> flash
    wire_arrow(ax, [(8.65, 6.2), (fx + fw / 2, 6.2), (fx + fw / 2, my0 + mh + 0.95)],
               color=GREEN)
    ax.text(5.6, 6.32, "writes image to flash", fontsize=7.5, color=GREEN, ha="center",
            va="bottom")
    ax.text(rx + rw / 2, my0 + mh + 0.25, "runs here", fontsize=7, color="#555555",
            ha="center")
    ax.text(fx + fw / 2, my0 + mh + 0.25, "loaded and executed in place", fontsize=7,
            color="#555555", ha="center")
    save(fig, "21", "fig-21-5-build-and-load")


if __name__ == "__main__":
    fig_21_1()
    fig_21_2()
    fig_21_3()
    fig_21_4()
    fig_21_5()
