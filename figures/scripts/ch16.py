"""Figures for Chapter 16 — Computer Architecture.

Run from the repository root:  python figures/scripts/ch16.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch, Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from figstyle import COLORS, INK, GRID, box, arrow, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK = COLORS[0], COLORS[1], COLORS[2], COLORS[3]
MEM_FC = "#DCEBF7"     # memory hierarchy tint
IO_FC = "#FBE7D3"      # I/O system tint
CORE_FC = "#E3F2E6"    # core internals
CTRL = "#7B3294"       # control-signal colour


# ----------------------------------------------------------------------------
# small drawing helpers
# ----------------------------------------------------------------------------
def wire(ax, pts, color=INK, lw=1.2, ls="-", **kw):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt",
            solid_joinstyle="miter", **kw)


def wire_arrow(ax, pts, color=INK, lw=1.2, ls="-", ms=9):
    """Polyline whose last segment ends in an arrow head."""
    if len(pts) > 2:
        wire(ax, pts[:-1], color=color, lw=lw, ls=ls)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls,
                                shrinkA=0, shrinkB=0, mutation_scale=ms))


def dot(ax, x, y, color=INK, ms=3.5):
    ax.plot([x], [y], "o", ms=ms, color=color, zorder=5)


def rect(ax, x, y, w, h, fc="white", ec=INK, lw=1.0, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))


def mux(ax, x, y0, y1, w=0.4, fc="white", label_in=None, fs=6.5):
    """Vertical 2-D multiplexer trapezoid from y0 to y1, inputs on left at x."""
    s = 0.15 * (y1 - y0)
    ax.add_patch(Polygon([(x, y0), (x, y1), (x + w, y1 - s), (x + w, y0 + s)],
                         closed=True, fc=fc, ec=INK, lw=1.0))
    if label_in:
        for yy, t in label_in:
            ax.text(x + 0.05, yy, t, fontsize=fs, va="center", ha="left")


def adder(ax, x, y0, h=1.2, w=0.6, text="+"):
    """ALU-style adder outline with inputs on the left (two) and output on right."""
    y1 = y0 + h
    pts = [(x, y0), (x + w, y0 + 0.3 * h), (x + w, y1 - 0.3 * h), (x, y1),
           (x, y0 + 0.6 * h), (x + 0.15 * w, y0 + 0.5 * h), (x, y0 + 0.4 * h)]
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec=INK, lw=1.0))
    ax.text(x + 0.55 * w, y0 + 0.5 * h, text, fontsize=9, ha="center", va="center")
    return (x, y0 + 0.75 * h), (x, y0 + 0.25 * h), (x + w, y0 + 0.5 * h)


# ----------------------------------------------------------------------------
def fig_16_1():
    """Organisation of a stored-program computer as a modern SoC."""
    fig, ax = schematic(6.8, 5.2, xlim=(0, 14.2), ylim=(-0.45, 10.6))

    # core with ISA boundary
    ax.add_patch(FancyBboxPatch((0.25, 5.95), 4.3, 3.95, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="white", ec=GREEN, lw=1.6, ls=(0, (5, 3))))
    ax.text(2.4, 9.62, "CPU core", ha="center", va="center", fontsize=9.5, weight="bold")
    box(ax, 0.5, 8.15, 1.85, 1.0, "Control\nunit", fc=CORE_FC, fontsize=8.5)
    box(ax, 2.5, 8.15, 1.85, 1.0, "Program\ncounter", fc=CORE_FC, fontsize=8.5)
    box(ax, 0.5, 6.85, 1.85, 1.0, "Register file\n32 × 32 bit", fc=CORE_FC, fontsize=7.4)
    box(ax, 2.5, 6.85, 1.85, 1.0, "ALU", fc=CORE_FC, fontsize=8.5)
    ax.text(2.4, 6.27, "instruction-set boundary", ha="center", va="center", fontsize=8,
            color=GREEN, style="italic")

    # caches
    box(ax, 5.3, 8.35, 2.2, 1.0, "L1 I-cache\n32 KiB", fc=MEM_FC, fontsize=8.5)
    box(ax, 5.3, 6.55, 2.2, 1.0, "L1 D-cache\n32 KiB", fc=MEM_FC, fontsize=8.5)
    box(ax, 8.3, 7.0, 2.2, 1.9, "Unified\nL2 cache\n512 KiB", fc=MEM_FC, fontsize=8.5)
    arrow(ax, 4.55, 8.85, 5.3, 8.85, both=True)
    arrow(ax, 4.55, 7.05, 5.3, 7.05, both=True)
    arrow(ax, 7.5, 8.85, 8.3, 8.45, both=True)
    arrow(ax, 7.5, 7.05, 8.3, 7.45, both=True)

    # interconnect
    box(ax, 0.25, 4.55, 13.45, 0.85, "On-chip interconnect   (AXI, 128 bit, 1 GHz)",
        fc=IO_FC, fontsize=9)
    arrow(ax, 9.4, 7.0, 9.4, 5.4, both=True)

    # bottom row
    yb, hb = 2.85, 0.95
    box(ax, 0.25, yb, 2.2, hb, "DRAM\ncontroller", fc=MEM_FC, fontsize=8.5)
    box(ax, 0.25, 0.75, 2.2, 1.15, "DDR4 DRAM\n8 GB", fc=MEM_FC, fontsize=8.5)
    arrow(ax, 1.35, yb, 1.35, 1.9, both=True)
    box(ax, 2.8, yb, 2.0, hb, "DMA\ncontroller", fc=IO_FC, fontsize=8.5)
    box(ax, 5.15, yb, 2.1, hb, "PCIe\nroot port", fc=IO_FC, fontsize=8.5)
    box(ax, 5.15, 0.75, 2.1, 1.15, "NVMe SSD", fc=IO_FC, fontsize=8.5)
    arrow(ax, 6.2, yb, 6.2, 1.9, both=True)
    box(ax, 7.6, yb, 2.0, hb, "AXI–APB\nbridge", fc=IO_FC, fontsize=8.5)
    box(ax, 10.85, yb, 2.55, hb, "Interrupt\ncontroller", fc=IO_FC, fontsize=8.5)
    for xc in (1.35, 3.8, 6.2, 8.6, 12.125):
        arrow(ax, xc, yb + hb, xc, 4.55, both=True)
    # APB bus and peripherals
    rect(ax, 7.6, 1.95, 5.8, 0.32, fc=IO_FC)
    ax.text(10.5, 2.11, "APB peripheral bus", fontsize=7.5, ha="center", va="center")
    wire(ax, [(8.6, yb), (8.6, 2.27)])
    names = ["Timer", "UART", "GPIO", "ADC"]
    pw, gap = 1.3, 0.2
    for i, n in enumerate(names):
        x = 7.6 + i * (pw + gap)
        box(ax, x, 0.75, pw, 0.8, n, fc=IO_FC, fontsize=8.5)
        wire(ax, [(x + pw / 2, 1.55), (x + pw / 2, 1.95)])
        # interrupt request lines (dashed)
        wire(ax, [(x + pw / 2, 0.75), (x + pw / 2, 0.3)], color=ORANGE, ls=(0, (3, 2)))
    wire(ax, [(7.6 + pw / 2, 0.3), (13.95, 0.3), (13.95, 3.3)], color=ORANGE, ls=(0, (3, 2)))
    wire_arrow(ax, [(13.95, 3.3), (13.4, 3.3)], color=ORANGE, ls=(0, (3, 2)))
    ax.text(11.1, 0.2, "interrupt requests", fontsize=7.5, color=ORANGE, ha="center", va="top")
    # controller to CPU (dashed)
    wire(ax, [(11.4, yb + hb), (11.4, 4.55)], color=ORANGE, ls=(0, (3, 2)))
    wire(ax, [(11.4, 5.4), (11.4, 10.2), (1.4, 10.2)], color=ORANGE, ls=(0, (3, 2)))
    wire_arrow(ax, [(1.4, 10.2), (1.4, 9.15)], color=ORANGE, ls=(0, (3, 2)))
    ax.text(6.5, 10.33, "IRQ to core", fontsize=7.5, color=ORANGE, ha="center", va="bottom")

    handles = [Line2D([], [], color=GREEN, lw=1.6, ls=(0, (5, 3)), label="instruction set (ISA boundary)"),
               Patch(fc=MEM_FC, ec=INK, lw=0.8, label="memory hierarchy"),
               Patch(fc=IO_FC, ec=INK, lw=0.8, label="I/O system")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3,
              fontsize=8.5, handlelength=2.2)
    save(fig, "16", "fig-16-1-computer-organisation")


# ----------------------------------------------------------------------------
def fig_16_2():
    """The six RV32I instruction formats."""
    bw = 0.34                              # width of one bit
    x0 = 1.2
    def xb(bit):                           # left edge of a bit cell (bit 31 leftmost)
        return x0 + (31 - bit) * bw

    fmts = [
        ("R", [(31, 25, "funct7", "f"), (24, 20, "rs2", "r"), (19, 15, "rs1", "r"),
               (14, 12, "funct3", "f"), (11, 7, "rd", "r"), (6, 0, "opcode", "o")]),
        ("I", [(31, 20, "imm[11:0]", "i"), (19, 15, "rs1", "r"), (14, 12, "funct3", "f"),
               (11, 7, "rd", "r"), (6, 0, "opcode", "o")]),
        ("S", [(31, 25, "imm[11:5]", "i"), (24, 20, "rs2", "r"), (19, 15, "rs1", "r"),
               (14, 12, "funct3", "f"), (11, 7, "imm[4:0]", "i"), (6, 0, "opcode", "o")]),
        ("B", [(31, 25, "imm[12|10:5]", "i"), (24, 20, "rs2", "r"), (19, 15, "rs1", "r"),
               (14, 12, "funct3", "f"), (11, 7, "imm[4:1|11]", "i"), (6, 0, "opcode", "o")]),
        ("U", [(31, 12, "imm[31:12]", "i"), (11, 7, "rd", "r"), (6, 0, "opcode", "o")]),
        ("J", [(31, 12, "imm[20|10:1|11|19:12]", "i"), (11, 7, "rd", "r"), (6, 0, "opcode", "o")]),
    ]
    fc = {"r": "#BFDCF2", "i": "#FBD9B8", "f": "#E6E6E6", "o": "#F2F2F2"}
    n = len(fmts)
    rh, gap = 0.62, 0.14
    ytop = 7.6
    fig, ax = schematic(6.8, 3.6, xlim=(0, 12.4), ylim=(1.5, 8.2))
    # bit numbers along the top
    for b in (31, 25, 24, 20, 19, 15, 14, 12, 11, 7, 6, 0):
        ax.text(xb(b) + bw / 2, ytop + 0.12, str(b), ha="center", va="bottom", fontsize=6.3)
    for r, (name, fields) in enumerate(fmts):
        y = ytop - (r + 1) * rh - r * gap
        ax.text(x0 - 0.25, y + rh / 2, name, ha="right", va="center", fontsize=10, weight="bold")
        for hi, lo, lab, k in fields:
            rect(ax, xb(hi), y, (hi - lo + 1) * bw, rh, fc=fc[k], lw=0.9)
            ax.text(xb(hi) + (hi - lo + 1) * bw / 2, y + rh / 2, lab, ha="center", va="center",
                    fontsize=8 if (hi - lo) >= 6 or len(lab) <= 6 else 7)
    side = ["register–register", "immediate, loads", "stores", "branches", "lui, auipc", "jal"]
    for r, s in enumerate(side):
        y = ytop - (r + 1) * rh - r * gap
        ax.text(x0 + 32 * bw + 0.15, y + rh / 2, s, fontsize=7.5, va="center", color="#555555")

    # example: add x5, x6, x7
    word = 0x007302B3
    yb = ytop - n * (rh + gap) - 0.75
    ax.text(x0 - 0.25, yb + rh / 2, "add\nx5,x6,x7", ha="right", va="center", fontsize=7.5)
    groups = fmts[0][1]
    for hi, lo, lab, k in groups:
        rect(ax, xb(hi), yb, (hi - lo + 1) * bw, rh, fc=fc[k], lw=0.9)
    for b in range(32):
        bit = (word >> b) & 1
        ax.text(xb(b) + bw / 2, yb + rh / 2, str(bit), ha="center", va="center", fontsize=8,
                family="DejaVu Sans Mono")
    labels = ["funct7 = 0", "rs2 = 7", "rs1 = 6", "funct3 = 0", "rd = 5", "opcode = 0110011"]
    for (hi, lo, _, _), t in zip(groups, labels):
        ax.text(xb(hi) + (hi - lo + 1) * bw / 2, yb - 0.12, t, ha="center", va="top", fontsize=7)
    ax.text(x0 + 32 * bw + 0.15, yb + rh / 2, "= 0x007302B3", fontsize=8.5, va="center",
            weight="bold")
    handles = [Patch(fc=fc["r"], ec=INK, lw=0.8, label="register fields (fixed position)"),
               Patch(fc=fc["i"], ec=INK, lw=0.8, label="immediate bits"),
               Patch(fc=fc["f"], ec=INK, lw=0.8, label="function / opcode")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, fontsize=8)
    save(fig, "16", "fig-16-2-rv32i-formats")


# ----------------------------------------------------------------------------
def fig_16_3():
    """Single-cycle RV32I datapath with control signals."""
    fig, ax = schematic(6.8, 5.7, xlim=(-0.3, 15.9), ylim=(-2.6, 10.0))
    cd = (0, (3, 2))
    fs = 7

    # PCSrc mux and PC
    mux(ax, 0.2, 4.4, 5.8, w=0.4, label_in=[(5.4, "0"), (4.8, "1")], fs=6.5)
    rect(ax, 1.0, 4.6, 0.8, 1.0, fc="#F4F4F4")
    ax.text(1.4, 5.15, "PC", ha="center", va="center", fontsize=8.5)
    ax.add_patch(Polygon([(1.25, 4.6), (1.4, 4.78), (1.55, 4.6)], closed=True, fc="none", ec=INK, lw=0.8))
    wire_arrow(ax, [(0.6, 5.1), (1.0, 5.1)])
    # instruction memory
    rect(ax, 2.5, 3.6, 1.8, 3.0)
    ax.text(3.4, 5.75, "Instruction\nmemory", ha="center", va="center", fontsize=7.5)
    ax.text(2.58, 5.1, "A", fontsize=fs, va="center")
    ax.text(4.22, 5.1, "RD", fontsize=fs, va="center", ha="right")
    wire_arrow(ax, [(1.8, 5.1), (2.5, 5.1)])
    dot(ax, 2.15, 5.1)

    # instruction bus
    xb = 4.8
    wire(ax, [(4.3, 5.1), (xb, 5.1)])
    wire(ax, [(xb, 2.05), (xb, 8.9)])
    ax.text(4.72, 6.9, "Instr", fontsize=6.3, rotation=90, ha="right", va="center")

    # register file
    rx, ry, rw, rh = 6.0, 3.7, 2.0, 3.0
    rect(ax, rx, ry, rw, rh)
    ax.text(rx + rw / 2 + 0.4, ry + 0.38, "Register\nfile", ha="center", va="center", fontsize=7.5)
    for yy, t in [(6.25, "WD3"), (5.6, "A1"), (5.0, "A2"), (4.4, "A3")]:
        ax.text(rx + 0.07, yy, t, fontsize=fs, va="center")
    ax.text(rx + rw - 0.07, 5.8, "RD1", fontsize=fs, va="center", ha="right")
    ax.text(rx + rw - 0.07, 4.6, "RD2", fontsize=fs, va="center", ha="right")
    ax.text(7.0, ry + rh - 0.08, "WE3", fontsize=6.3, va="top", ha="center")
    for yy, t, b in [(5.6, "rs1", "[19:15]"), (5.0, "rs2", "[24:20]"), (4.4, "rd", "[11:7]")]:
        wire_arrow(ax, [(xb, yy), (rx, yy)], ms=7)
        dot(ax, xb, yy)
        ax.text(xb + 0.08, yy + 0.04, t, fontsize=6.3, va="bottom")
        ax.text(xb + 0.08, yy - 0.04, b, fontsize=5.6, va="top", color="#444444")
    # immediate generator
    rect(ax, rx, 1.55, rw, 0.95, fc="#F4F4F4")
    ax.text(rx + rw / 2, 2.02, "Immediate\ngenerator", ha="center", va="center", fontsize=7)
    wire_arrow(ax, [(xb, 2.05), (rx, 2.05)], ms=7)
    ax.text(xb + 0.08, 2.1, "[31:7]", fontsize=5.6, va="bottom")

    # ALUSrc mux
    mux(ax, 8.9, 3.6, 5.0, w=0.4, label_in=[(4.6, "0"), (4.0, "1")], fs=6.5)
    wire_arrow(ax, [(rx + rw, 4.6), (8.9, 4.6)], ms=7)
    dot(ax, 8.5, 4.6)
    # ImmExt
    wire(ax, [(rx + rw, 1.85), (8.7, 1.85), (8.7, 4.0)])
    wire_arrow(ax, [(8.7, 4.0), (8.9, 4.0)], ms=6)
    dot(ax, 8.7, 1.85)
    ax.text(8.78, 2.6, "ImmExt", fontsize=6.3, va="center")
    # ALU
    ax0, ay0 = 9.8, 3.7
    alu = [(ax0, ay0), (ax0 + 1.0, ay0 + 0.8), (ax0 + 1.0, ay0 + 1.9), (ax0, ay0 + 2.7),
           (ax0, ay0 + 1.55), (ax0 + 0.2, ay0 + 1.35), (ax0, ay0 + 1.15)]
    ax.add_patch(Polygon(alu, closed=True, fc="#FFF6E0", ec=INK, lw=1.0))
    ax.text(ax0 + 0.58, ay0 + 1.35, "ALU", fontsize=8, ha="center", va="center")
    wire_arrow(ax, [(rx + rw, 5.8), (ax0, 5.8)], ms=7)
    ax.text(ax0 - 0.05, 5.88, "SrcA", fontsize=6, ha="right", va="bottom")
    wire_arrow(ax, [(9.3, 4.3), (ax0, 4.3)], ms=7)
    ax.text(ax0 - 0.05, 4.22, "SrcB", fontsize=6, ha="right", va="top")
    # ALU outputs
    dx, dy, dw, dh = 11.5, 3.0, 1.8, 3.0
    wire_arrow(ax, [(ax0 + 1.0, 4.7), (dx, 4.7)], ms=7)
    dot(ax, 11.0, 4.7)
    wire(ax, [(ax0 + 1.0, 5.4), (11.3, 5.4), (11.3, 7.25)], color=CTRL)
    # data memory
    rect(ax, dx, dy, dw, dh)
    ax.text(dx + dw / 2, 5.12, "Data\nmemory", ha="center", va="center", fontsize=7.5)
    ax.text(dx + 0.07, 4.7, "A", fontsize=fs, va="center")
    ax.text(dx + 0.07, 3.4, "WD", fontsize=fs, va="center")
    ax.text(dx + dw - 0.07, 4.3, "RD", fontsize=fs, va="center", ha="right")
    ax.text(12.4, dy + dh - 0.08, "WE", fontsize=6.3, va="top", ha="center")
    # RD2 -> WD
    wire(ax, [(8.5, 4.6), (8.5, 3.4)])
    wire_arrow(ax, [(8.5, 3.4), (dx, 3.4)], ms=7)
    ax.text(9.45, 3.33, "WriteData", fontsize=6, va="top")

    # result mux
    xm = 14.3
    mux(ax, xm, 2.9, 5.3, w=0.45, label_in=[(4.3, "01"), (3.7, "00"), (3.2, "10")], fs=6)
    wire_arrow(ax, [(dx + dw, 4.3), (xm, 4.3)], ms=7)
    ax.text(13.38, 4.38, "ReadData", fontsize=6, va="bottom")
    wire(ax, [(11.0, 4.7), (11.0, 2.6), (13.9, 2.6), (13.9, 3.7)])
    wire_arrow(ax, [(13.9, 3.7), (xm, 3.7)], ms=6)
    ax.text(11.15, 2.66, "ALUResult", fontsize=6, va="bottom")
    # writeback
    wire(ax, [(xm + 0.45, 4.1), (15.2, 4.1), (15.2, 7.25), (5.4, 7.25), (5.4, 6.25)])
    wire_arrow(ax, [(5.4, 6.25), (rx, 6.25)], ms=6)
    ax.text(13.3, 7.32, "Result", fontsize=6.5, va="bottom")

    # PC + 4 adder
    a_in1, a_in2, a_out = adder(ax, 2.6, 1.6, h=1.2, w=0.6)
    wire(ax, [(2.15, 5.1), (2.15, a_in1[1])])
    wire_arrow(ax, [(2.15, a_in1[1]), a_in1], ms=6)
    ax.text(2.4, a_in2[1], "4", fontsize=7, ha="right", va="center")
    wire_arrow(ax, [(2.42, a_in2[1]), a_in2], ms=6)
    wire(ax, [a_out, (3.75, a_out[1]), (3.75, -0.05)])
    dot(ax, 3.75, -0.05)
    ax.text(3.82, 2.25, "PCPlus4", fontsize=6, va="bottom")
    wire(ax, [(3.75, -0.05), (-0.15, -0.05), (-0.15, 5.4)])
    wire_arrow(ax, [(-0.15, 5.4), (0.2, 5.4)], ms=6)
    wire(ax, [(3.75, -0.05), (14.05, -0.05), (14.05, 3.2)])
    wire_arrow(ax, [(14.05, 3.2), (xm, 3.2)], ms=6)
    # branch adder PC + imm
    b_in1, b_in2, b_out = adder(ax, 9.5, 0.55, h=1.3, w=0.6)
    wire(ax, [(8.7, 1.85), (8.7, b_in1[1])])
    wire_arrow(ax, [(8.7, b_in1[1]), b_in1], ms=6)
    wire(ax, [(2.15, a_in1[1]), (2.15, b_in2[1])])
    wire_arrow(ax, [(2.15, b_in2[1]), b_in2], ms=6)
    dot(ax, 2.15, a_in1[1])
    wire(ax, [b_out, (10.5, b_out[1]), (10.5, 0.25), (0.05, 0.25), (0.05, 4.8)])
    wire_arrow(ax, [(0.05, 4.8), (0.2, 4.8)], ms=6)
    ax.text(10.6, 0.9, "PCTarget", fontsize=6, va="center")

    # control unit
    cx, cy, cw, ch = 5.9, 8.1, 5.7, 1.5
    rect(ax, cx, cy, cw, ch, fc="#F3E8F7", ec=CTRL)
    ax.text(cx + cw / 2, cy + ch - 0.3, "Control unit", ha="center", va="center", fontsize=8.5,
            weight="bold", color=CTRL)
    ax.text(cx + cw / 2, cy + 0.72, "main decoder + ALU decoder", ha="center", va="center",
            fontsize=6.5, color=CTRL)
    ax.text(cx + cw / 2, cy + 0.32, "PCSrc = Branch·Zero + Jump", ha="center", va="center",
            fontsize=6.5, color=CTRL)
    wire_arrow(ax, [(xb, 8.9), (cx, 8.9)], ms=6)
    dot(ax, xb, 5.1)
    ax.text(4.7, 8.35, "op, funct3,\nfunct7[5]", fontsize=6.3, ha="right", va="center")
    ax.text(11.37, 6.9, "Zero", fontsize=6.3, color=CTRL, va="center")
    wire(ax, [(11.3, 7.25), (11.3, 7.6)], color=CTRL)
    wire_arrow(ax, [(11.3, 7.6), (11.3, cy)], color=CTRL, ms=6)

    def cl(pts, name, tx, ty, ha="left"):
        wire_arrow(ax, pts, color=CTRL, ls=cd, ms=6)
        ax.text(tx, ty, name, fontsize=6.3, color=CTRL, ha=ha, va="center")
    cl([(7.0, cy), (7.0, ry + rh)], "RegWrite", 7.05, 7.7)
    cl([(8.25, cy), (8.25, 2.35), (rx + rw, 2.35)], "ImmSrc", 8.3, 7.7)
    cl([(9.1, cy), (9.1, 4.97)], "ALUSrc", 9.15, 6.6)
    cl([(10.3, cy), (10.3, 6.0)], "ALU\nControl", 10.36, 6.75)
    cl([(cx + cw, 8.5), (12.4, 8.5), (12.4, dy + dh)], "MemWrite", 12.47, 6.6)
    cl([(cx + cw, 9.1), (14.52, 9.1), (14.52, 5.12)], "ResultSrc", 14.58, 6.6)
    cl([(cx, 9.45), (0.4, 9.45), (0.4, 5.62)], "PCSrc", 0.47, 7.75)

    # stage-delay strip along the lw path
    segs = [("fetch", 200, BLUE), ("decode +\nreg read", 100, GREEN), ("ALU", 200, ORANGE),
            ("memory", 250, PINK), ("write-\nback", 100, COLORS[4])]
    x, xs, xe = 1.0, 1.0, 15.2
    scale = (xe - xs) / 850
    ys = -1.75
    for name, t, c in segs:
        w = t * scale
        rect(ax, x, ys, w, 0.45, fc=c + "40", ec=c, lw=1.0)
        ax.text(x + w / 2, ys + 0.225, f"{t} ps", ha="center", va="center", fontsize=6.5)
        ax.text(x + w / 2, ys + 0.5, name, ha="center", va="bottom", fontsize=6.3)
        x += w
    ax.text(xs - 0.1, ys + 0.225, "lw path", ha="right", va="center", fontsize=7)
    ax.annotate("", xy=(xe, ys - 0.22), xytext=(xs, ys - 0.22),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=7,
                                shrinkA=0, shrinkB=0))
    ax.text((xs + xe) / 2, ys - 0.3, r"$T_c$ = 850 ps  (CPI = 1)", ha="center", va="top", fontsize=7.5)
    save(fig, "16", "fig-16-3-single-cycle-datapath")


# ----------------------------------------------------------------------------
def fig_16_4():
    """Five-stage pipeline diagram of the sum loop."""
    rows = [
        ("lw   t1, 0(a0)",   {1: "IF", 2: "ID", 3: "EX", 4: "MEM", 5: "WB"}),
        ("add  t0, t0, t1",  {2: "IF", 3: "ID", 4: "stall", 5: "EX", 6: "MEM", 7: "WB"}),
        ("addi a0, a0, 4",   {3: "IF", 4: "stall", 5: "ID", 6: "EX", 7: "MEM", 8: "WB"}),
        ("addi a1, a1, -1",  {5: "IF", 6: "ID", 7: "EX", 8: "MEM", 9: "WB"}),
        ("bnez a1, loop",    {6: "IF", 7: "ID", 8: "EX", 9: "MEM", 10: "WB"}),
        ("mv   a0, t0",      {7: "IF*", 8: "ID*"}),
        ("ret",              {8: "IF*"}),
        ("lw   t1, 0(a0)",   {9: "IF", 10: "ID", 11: "EX", 12: "MEM"}),
    ]
    sc = {"IF": "#CFE3F3", "ID": "#D5EDDA", "EX": "#FBE0C8", "MEM": "#EBD6E6", "WB": "#FFF1BF"}
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    n = len(rows)
    for r, (name, st) in enumerate(rows):
        y = n - 1 - r
        for c, s in st.items():
            if s == "stall":
                ax.add_patch(Rectangle((c - 0.45, y - 0.36), 0.9, 0.72, fc="white", ec="#888888",
                                       lw=1.0, ls=(0, (2, 2))))
                ax.text(c, y, "stall", ha="center", va="center", fontsize=7, color="#777777",
                        style="italic")
            elif s.endswith("*"):
                ax.add_patch(Rectangle((c - 0.45, y - 0.36), 0.9, 0.72, fc="white", ec="#999999",
                                       lw=0.9, hatch="////"))
                ax.text(c, y, s[:-1], ha="center", va="center", fontsize=7.5, color="#666666",
                        bbox=dict(fc="white", ec="none", pad=0.5))
            else:
                ax.add_patch(Rectangle((c - 0.45, y - 0.36), 0.9, 0.72, fc=sc[s], ec=INK, lw=0.9))
                ax.text(c, y, s, ha="center", va="center", fontsize=7.5)
        col = "#777777" if r in (5, 6) else INK
        ax.text(0.3, y, name, ha="right", va="center", fontsize=8, family="DejaVu Sans Mono",
                color=col)
    # flushed annotation
    ax.text(9.0, n - 1 - 5.5, "flushed", fontsize=7.5, color=ORANGE, va="center", ha="left",
            style="italic")
    # forwarding arrow lw MEM/WB -> add EX
    ax.annotate("", xy=(4.55, n - 2 + 0.05), xytext=(4.05, n - 1 - 0.36),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6, mutation_scale=11,
                                shrinkA=0, shrinkB=0, connectionstyle="arc3,rad=0.35"), zorder=6)
    ax.text(5.6, n - 1, "forwarding: lw MEM/WB → add EX", fontsize=7.5, color=BLUE, ha="left",
            va="center")
    # branch resolution
    yb = n - 1 - 4
    ax.add_patch(Rectangle((8 - 0.47, yb - 0.38), 0.94, 0.76, fc="none", ec=ORANGE, lw=1.8))
    ax.text(10.6, yb, "taken: resolved\nin EX, cycle 8", fontsize=7.5, color=ORANGE, ha="left",
            va="center")
    # iteration bracket
    yt = -1.05
    ax.annotate("", xy=(9 - 0.45, yt), xytext=(1 - 0.45, yt),
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.0, mutation_scale=8,
                                shrinkA=0, shrinkB=0))
    ax.text(4.55, yt - 0.12, "8 cycles per iteration, 5 useful instructions", ha="center",
            va="top", fontsize=8)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_xlim(-2.6, 12.6)
    ax.set_ylim(-1.9, n - 0.2)
    ax.set_xticks(range(1, 13))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("clock cycle")
    ax.set_yticks([])
    for s in ("left", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["top"].set_visible(True)
    ax.spines["top"].set_bounds(0.5, 12.5)
    for c in range(1, 13):
        ax.axvline(c - 0.5, color=GRID, lw=0.6, zorder=0, ymin=0.14, ymax=1)
    save(fig, "16", "fig-16-4-pipeline-hazards")


# ----------------------------------------------------------------------------
def and_gate(ax, x, y, w=0.5, h=0.5):
    """AND gate with inputs on top, output at bottom (pointing down). (x,y) = top-centre."""
    th = np.linspace(0, np.pi, 30)
    r = w / 2
    pts = [(x - r, y), (x + r, y), (x + r, y - h + r)]
    pts += [(x + r * np.cos(t), y - h + r - r * np.sin(t)) for t in th]
    pts += [(x - r, y - h + r)]
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec=INK, lw=1.0))
    return (x, y - h - r + r)


def or_gate_right(ax, x, y, w=0.7, h=0.9):
    """OR gate pointing right; (x, y) = centre of the back edge."""
    t = np.linspace(-1, 1, 30)
    back = [(x + 0.15 * w * (1 - tt ** 2), y + tt * h / 2) for tt in t]
    top = [(x + w * (1 - (1 - s) ** 2) * 1.0 if False else x + s * w, y + h / 2 * (1 - s ** 2))
           for s in np.linspace(0, 1, 30)]
    bot = [(x + s * w, y - h / 2 * (1 - s ** 2)) for s in np.linspace(1, 0, 30)]
    pts = top + bot + back[::-1]
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec=INK, lw=1.0))
    return (x + w, y)


def fig_16_5():
    """Lookup in a 32 KiB 4-way set-associative cache."""
    fig, ax = schematic(6.8, 5.4, xlim=(-0.2, 14.0), ylim=(-0.7, 10.5))
    # address
    ay = 9.6
    flds = [("tag  [31:13]\n19 bits", 0.9, 6.6, "#FBD9B8"), ("index  [12:6]\n7 bits", 6.6, 9.4, "#BFDCF2"),
            ("offset  [5:0]\n6 bits", 9.4, 11.6, "#D5EDDA")]
    for t, x0, x1, c in flds:
        rect(ax, x0, ay, x1 - x0, 0.75, fc=c)
        ax.text((x0 + x1) / 2, ay + 0.375, t, ha="center", va="center", fontsize=7.5)
    ax.text(0.8, ay + 0.375, "address", ha="right", va="center", fontsize=8)
    ax.text(11.7, ay + 0.375, "e.g. 0x2000_1A44: tag 0x10000,\nindex 105, offset 0x04", fontsize=6.5,
            va="center")

    # ways
    wx0, ww, wg = 1.6, 2.65, 0.25
    ytop, ybot = 8.6, 5.75
    nrows = 7
    rhh = (ytop - ybot) / nrows
    sel = 3                                           # highlighted row (set 105)
    cols = [("V", 0.3), ("D", 0.3), ("tag", 1.0), ("data", 1.05)]
    hl = "#FFF1BF"
    # LRU column
    lx = 0.35
    for i in range(nrows):
        yy = ytop - (i + 1) * rhh
        rect(ax, lx, yy, 0.8, rhh, fc=hl if i == sel else "white", lw=0.6)
        if i in (1, 5):
            ax.text(lx + 0.4, yy + rhh / 2, "⋮", ha="center", va="center", fontsize=7)
    ax.text(lx + 0.4, ytop + 0.12, "LRU", ha="center", va="bottom", fontsize=7)
    ax.text(lx + 0.4, ybot - 0.1, "bits per\nset", ha="center", va="top", fontsize=6)
    iy = ytop - (sel + 0.5) * rhh
    ax.text(lx + 0.4, iy, "set 105", ha="center", va="center", fontsize=5.3)
    # index arrow to selected row
    wire(ax, [(8.0, ay), (8.0, 9.12), (0.1, 9.12), (0.1, iy)], color=BLUE)
    wire_arrow(ax, [(0.1, iy), (lx, iy)], color=BLUE, ms=7)
    ax.text(4.6, 9.17, "index selects one of 128 sets", fontsize=7, color=BLUE, va="bottom")

    tag_y, cy, gy = 5.0, 4.45, 3.75
    outs = []
    for w in range(4):
        x0 = wx0 + w * (ww + wg)
        ax.text(x0 + ww / 2, ytop + 0.12, f"way {w}", ha="center", va="bottom", fontsize=7.5)
        x = x0
        centres = []
        for name, cwid in cols:
            wpx = cwid * ww / 2.65
            for i in range(nrows):
                yy = ytop - (i + 1) * rhh
                rect(ax, x, yy, wpx, rhh, fc=hl if i == sel else "white", lw=0.6)
                if i in (1, 5):
                    ax.text(x + wpx / 2, yy + rhh / 2, "⋮", ha="center", va="center", fontsize=6)
            ax.text(x + wpx / 2, ybot - 0.08, name, ha="center", va="top", fontsize=6)
            centres.append(x + wpx / 2)
            x += wpx
        xv, _, xt, xd = centres
        # comparator
        ax.add_patch(plt.Circle((xt, cy), 0.25, fc="white", ec=INK, lw=1.0, zorder=4))
        ax.text(xt, cy, "=", ha="center", va="center", fontsize=9, zorder=5)
        wire_arrow(ax, [(xt, ybot - 0.3), (xt, cy + 0.25)], ms=6)
        wire(ax, [(xt, ybot), (xt, ybot - 0.3)])
        wire(ax, [(xt + 0.25, cy), (xt + 0.5, cy), (xt + 0.5, tag_y)], color=ORANGE)
        dot(ax, xt + 0.5, tag_y, color=ORANGE, ms=2.5)
        # AND with valid
        gx = xt - 0.12
        wire(ax, [(xt, cy - 0.25), (xt, gy)])
        wire(ax, [(xv, ybot - 0.3), (xv, 3.95), (gx - 0.13, 3.95), (gx - 0.13, gy)])
        wire(ax, [(xv, ybot), (xv, ybot - 0.3)])
        and_gate(ax, gx, gy, w=0.42, h=0.48)
        outs.append((gx, gy - 0.48, xd))
        ax.text(gx + 0.25, gy - 0.5, f"hit{w}", fontsize=6, va="top")
        wire(ax, [(xd, ybot), (xd, 1.55)])
    ax.text(-0.1, 0.25, "each entry: valid bit V, dirty bit D,\n19-bit tag, 64-byte data line", fontsize=6.5,
            va="center", color="#555555")
    # address tag bus
    wire(ax, [(1.4, ay), (1.4, tag_y), (outs[-1][0] + 0.62, tag_y)], color=ORANGE)
    ax.text(1.45, ay - 0.08, "tag", fontsize=6.5, color=ORANGE, va="top")
    # hit lines to the OR gate
    xo = 12.5
    ylev = [2.9 - 0.18 * i for i in range(4)]
    for (gx, yh, _), yl in zip(outs, ylev):
        wire(ax, [(gx, yh), (gx, yl), (xo + 0.06, yl)])
    or_gate_right(ax, xo, 2.63, w=0.6, h=0.85)
    wire_arrow(ax, [(xo + 0.6, 2.63), (13.65, 2.63)], ms=7)
    ax.text(13.15, 2.7, "Hit", fontsize=8, va="bottom", weight="bold")
    # 4:1 data mux
    mx0, mx1, my = outs[0][2] - 0.35, outs[-1][2] + 0.45, 1.55
    ax.add_patch(Polygon([(mx0, my), (mx1, my), (mx1 - 0.4, my - 0.55), (mx0 + 0.4, my - 0.55)],
                         closed=True, fc="white", ec=INK, lw=1.0))
    ax.text((mx0 + mx1) / 2, my - 0.27, "4:1 line multiplexer", ha="center", va="center", fontsize=7)
    ax.annotate("select = hit0…hit3", xy=(mx1 - 0.2, my - 0.27), xytext=(mx1 + 0.35, my - 0.27),
                fontsize=6.5, va="center", arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9,
                                                            mutation_scale=7))
    # word select mux
    wy = 0.55
    xm = (mx0 + mx1) / 2
    wire(ax, [(xm, my - 0.55), (xm, wy)])
    ax.text(xm + 0.1, (my - 0.55 + wy) / 2, "64-byte line", fontsize=6.5, va="center")
    ax.add_patch(Polygon([(xm - 1.5, wy), (xm + 1.5, wy), (xm + 1.15, wy - 0.5), (xm - 1.15, wy - 0.5)],
                         closed=True, fc="white", ec=INK, lw=1.0))
    ax.text(xm, wy - 0.25, "word select (16:1)", ha="center", va="center", fontsize=6.8)
    wire(ax, [(10.5, ay), (10.5, 9.0), (13.75, 9.0), (13.75, wy - 0.25)], color=GREEN)
    wire_arrow(ax, [(13.75, wy - 0.25), (xm + 1.33, wy - 0.25)], color=GREEN, ms=7)
    ax.text(13.7, 6.6, "offset[5:2]", fontsize=6.5, color=GREEN, rotation=90, ha="right", va="center")
    wire_arrow(ax, [(xm, wy - 0.5), (xm, -0.55)], ms=7)
    ax.text(xm + 0.1, -0.45, "32-bit data", fontsize=7.5, va="center")
    save(fig, "16", "fig-16-5-set-associative-cache")


# ----------------------------------------------------------------------------
def fig_16_6():
    """CPU activity for polling, interrupt-driven and DMA transfer of an 8-byte message."""
    tbyte = 10 / 115200 * 1e6           # 86.8 us per byte
    tev = tbyte * np.arange(1, 9)
    isr = 2.0                            # 200 cycles at 100 MHz
    T = 800
    fig, axs = plt.subplots(3, 1, figsize=(6.8, 4.6), sharex=True,
                            gridspec_kw=dict(height_ratios=[2, 2, 3], hspace=0.35))
    titles = ["Polling (programmed I/O)", "Interrupt per byte", "DMA, one interrupt per message"]
    loads = ["CPU load 100 %", f"CPU load {isr / tbyte * 100:.1f} %",
             f"CPU load ≈ {isr / (8 * tbyte) * 100:.2f} %"]
    for k, ax in enumerate(axs):
        rows = ["byte ready", "CPU"] + (["DMA engine"] if k == 2 else [])
        nr = len(rows)
        ys = {r: nr - 1 - i for i, r in enumerate(rows)}
        # events
        y = ys["byte ready"]
        for t in tev:
            ax.plot([t, t], [y - 0.3, y + 0.3], color=INK, lw=1.3)
        ax.plot(tev, [y + 0.3] * 8, "v", color=INK, ms=3.5)
        yc = ys["CPU"]
        ax.add_patch(Rectangle((0, yc - 0.3), T, 0.6, fc="white", ec="#AAAAAA", lw=0.6))
        if k == 0:
            ax.add_patch(Rectangle((0, yc - 0.3), tev[-1] + isr, 0.6, fc=BLUE + "AA", ec=BLUE, lw=0.8))
            for t in tev:
                ax.add_patch(Rectangle((t, yc - 0.3), isr, 0.6, fc=ORANGE, ec=ORANGE, lw=0.8))
            ax.text(tev[0] / 2, yc, "busy-\nwait", ha="center", va="center",
                    fontsize=6.5, color="white")
            ax.text(748, yc, "done", ha="center", va="center", fontsize=6.5, color="#777777")
        elif k == 1:
            for t in tev:
                ax.add_patch(Rectangle((t, yc - 0.3), isr, 0.6, fc=ORANGE, ec=ORANGE, lw=1.0))
            ax.annotate("ISR ≈ 2 µs", xy=(tev[2] + 1, yc + 0.3), xytext=(tev[2] + 25, yc + 0.75),
                        fontsize=7, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7), va="center")
            ax.text(tev[0] / 2, yc, "free", ha="center", va="center", fontsize=6.5,
                    color="#777777")
        else:
            ax.add_patch(Rectangle((tev[-1] + 0.5, yc - 0.3), isr, 0.6, fc=ORANGE, ec=ORANGE, lw=1.0))
            ax.text(tev[-1] - 6, yc, "transfer-complete ISR →", ha="right", va="center",
                    fontsize=6.5)
            ax.text(tev[0] / 2, yc, "free", ha="center", va="center", fontsize=6.5,
                    color="#777777")
            yd = ys["DMA engine"]
            ax.add_patch(Rectangle((0, yd - 0.3), T, 0.6, fc="white", ec="#AAAAAA", lw=0.6))
            for t in tev:
                ax.add_patch(Rectangle((t, yd - 0.3), 0.3, 0.6, fc=GREEN, ec=GREEN, lw=1.2))
            ax.text(tev[0] / 2, yd, "1 bus write\nper byte", ha="center", va="center", fontsize=6,
                    color="#555555")
        ax.set_yticks([ys[r] for r in rows])
        ax.set_yticklabels(rows, fontsize=8)
        ax.set_ylim(-0.6, nr - 0.25)
        ax.set_xlim(0, T)
        ax.set_title(titles[k], fontsize=9, loc="left", pad=3)
        ax.text(T, nr - 0.25, loads[k], ha="right", va="bottom", fontsize=8.5, weight="bold",
                color=ORANGE if k else BLUE)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    axs[0].annotate("", xy=(tev[1], 0.52), xytext=(tev[0], 0.52),
                    arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=INK, mutation_scale=6,
                                    shrinkA=0, shrinkB=0))
    axs[0].text((tev[0] + tev[1]) / 2, 0.52, "86.8 µs", fontsize=6.5, ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=0.4))
    axs[-1].set_xlabel("time (µs)  —  UART at 115 200 baud, 10 bits per byte")
    save(fig, "16", "fig-16-6-io-mechanisms")


if __name__ == "__main__":
    fig_16_1()
    fig_16_2()
    fig_16_3()
    fig_16_4()
    fig_16_5()
    fig_16_6()
