"""Figures for Chapter 23 — Algorithms and Data Structures.

Run from the repository root:  python figures/scripts/ch23.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import heapq  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Wedge, Circle  # noqa: E402

from figstyle import COLORS, INK, save, schematic  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[:6]
RED = "#C62828"
GREY = "#777777"
LIGHT = "#EEF3F8"


def tint(c, a="33"):
    return c + a


def arr(ax, p0, p1, color=INK, lw=1.1, rad=0.0, ms=10, ls="-"):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms, ls=ls,
                                shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"))


def rbox(ax, x, y, w, h, text="", fc=LIGHT, ec=INK, fs=7.5, lw=0.9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                weight="bold" if bold else "normal")


# ----------------------------------------------------------------------------
# Figure 23.1 — array vs linked list against 64-byte cache lines
# ----------------------------------------------------------------------------
def fig_array_vs_list():
    fig, ax = schematic(6.8, 5.0, xlim=(0, 17), ylim=(-0.5, 12.2))
    # --- array ------------------------------------------------------------
    sc = 0.13                      # drawing units per byte
    x0, y0, h = 0.6, 9.3, 0.8
    ax.text(x0, 11.75, "Array: a0 … a7 (int32) in 32 consecutive bytes", fontsize=8.5,
            weight="bold", va="center")
    ax.add_patch(Rectangle((x0, y0), 64 * sc, h, fc="none", ec=INK, lw=1.4))
    ax.text(x0 + 32 * sc, y0 + h + 0.3, "cache line 0x2000 – 0x203F (64 B)", ha="center",
            fontsize=7, color=GREY)
    x2, w2 = x0 + 64 * sc, 4.2
    ax.plot([x2, x2 + w2], [y0, y0], color=INK, lw=1.4)
    ax.plot([x2, x2 + w2], [y0 + h, y0 + h], color=INK, lw=1.4)
    ax.text(x2 + w2 / 2, y0 + h / 2, "next line 0x2040 …\n(prefetched)", fontsize=6.5,
            ha="center", va="center", color=GREY)
    for i in range(16):
        f = tint(BLUE, "55") if i < 8 else "white"
        ax.add_patch(Rectangle((x0 + 4 * i * sc, y0), 4 * sc, h, fc=f, ec=GREY, lw=0.5))
        if i < 8:
            ax.text(x0 + (4 * i + 2) * sc, y0 + h / 2, f"a{i}", ha="center", va="center", fontsize=6.5)
    ax.text(x0, y0 - 0.3, "0x2000", fontsize=6.5, ha="center", va="top", color=GREY)
    ax.text(x0 + 30 * sc, y0 - 0.3, "0x201C", fontsize=6.5, ha="center", va="top", color=GREY)
    ax.text(x0 + 64 * sc, y0 - 0.3, "0x2040", fontsize=6.5, ha="center", va="top", color=GREY)
    arr(ax, (x0 + 16 * sc, y0 - 1.25), (x0 + 16 * sc, y0 - 0.05), color=BLUE)
    ax.text(x0 + 16 * sc + 0.2, y0 - 1.0, "one cache miss loads all eight values",
            fontsize=7.5, color=BLUE, va="center")

    # --- linked list -----------------------------------------------------
    ax.text(x0, 7.15, "Linked list: 16-byte nodes (value 4 B, pad 4 B, next 8 B) in six cache lines",
            fontsize=8.5, weight="bold", va="center")
    lsc = 0.075
    lw_ = 64 * lsc                 # 4.8 units per line
    line_addr = [0x1C80, 0x3100, 0x55C0, 0x7A40, 0x9E00, 0xB3C0]
    pos = {0x1C80: (0.6, 4.6), 0x3100: (6.1, 4.6), 0x55C0: (11.6, 4.6),
           0x7A40: (0.6, 1.4), 0x9E00: (6.1, 1.4), 0xB3C0: (11.6, 1.4)}
    nodes = [0x7A40, 0x1C80, 0x55C0, 0x9E10, 0x1CA0, 0x3120, 0xB3C0, 0x7A60]
    hit = {4, 7}                   # nodes whose line was already loaded
    for la in line_addr:
        px, py = pos[la]
        ax.add_patch(Rectangle((px, py), lw_, 1.0, fc="none", ec=INK, lw=1.4))
        for s in range(1, 4):
            ax.plot([px + s * 16 * lsc] * 2, [py, py + 1.0], color=GREY, lw=0.4, ls=":")
        ax.text(px + lw_, py - 0.22, f"line 0x{la:04X}", fontsize=6.5, va="top", ha="right", color=GREY)
    centres = []
    for k, a in enumerate(nodes):
        la = a & ~0x3F
        px, py = pos[la]
        off = (a - la) * lsc
        nx = px + off
        ax.add_patch(Rectangle((nx, py), 4 * lsc, 1.0, fc=tint(BLUE, "55"), ec=INK, lw=0.6))
        ax.add_patch(Rectangle((nx + 4 * lsc, py), 4 * lsc, 1.0, fc="#DDDDDD", ec=INK, lw=0.6))
        ax.add_patch(Rectangle((nx + 8 * lsc, py), 8 * lsc, 1.0, fc=tint(ORANGE, "40"), ec=INK, lw=0.6))
        ax.text(nx + 2 * lsc, py + 0.5, f"a{k}", ha="center", va="center", fontsize=6.3, rotation=90)
        ax.text(nx + 12 * lsc, py + 0.5, "next", ha="center", va="center", fontsize=6)
        tag = "hit" if k in hit else "miss"
        ax.text(nx + 8 * lsc, py + 1.18, f"0x{a:04X} {tag}", ha="center", va="bottom", fontsize=5.8,
                color=GREEN if k in hit else RED)
        centres.append((nx, py, nx + 12 * lsc))
    for k in range(7):
        nx, py, ptr_x = centres[k]
        mx, my, _ = centres[k + 1]
        start = (ptr_x, py + 0.5)
        end = (mx + 0.05, my + 0.5 + (0.3 if my != py else 0.0))
        rad = 0.25 if k % 2 else -0.25
        arr(ax, start, end, color=ORANGE, lw=0.9, rad=rad, ms=8)
        mxp, myp = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        dxp, dyp = end[0] - start[0], end[1] - start[1]
        lab = (mxp + rad * dyp / 2, myp - rad * dxp / 2)
        ax.text(*lab, str(k + 1), ha="center", va="center", fontsize=6.5, color="white", weight="bold",
                bbox=dict(boxstyle="circle,pad=0.15", fc=ORANGE, ec="none"), zorder=6)
    ax.text(16.9, -0.25, "6 lines touched here = 6 misses; in general up to 8 (one per node)",
            ha="right", fontsize=7.5, color=RED)
    # latency annotation
    rbox(ax, 13.9, 8.9, 3.0, 1.9, "", fc="white", ec=GREY)
    ax.text(15.4, 10.3, "L1 hit ≈ 1 ns", ha="center", fontsize=8, color=GREEN)
    ax.text(15.4, 9.45, "DRAM ≈ 90 ns", ha="center", fontsize=8, color=RED)
    save(fig, "23", "fig-23-1-array-vs-linked-list-memory")


# ----------------------------------------------------------------------------
# Figure 23.2 — UART ring buffer
# ----------------------------------------------------------------------------
def fig_ring_buffer():
    fig, ax = schematic(6.8, 4.6, xlim=(0, 17), ylim=(0, 11.5))
    cx, cy, r_out, r_in = 8.5, 6.3, 3.6, 2.2
    data = dict(zip(range(4, 12), ["$", "G", "P", "G", "G", "A", ",", "1"]))
    for k in range(16):
        # slot 0 at top, clockwise
        th1 = 90 - k * 22.5 + 11.25
        th0 = th1 - 22.5
        occ = k in data
        ax.add_patch(Wedge((cx, cy), r_out, th0, th1, width=r_out - r_in,
                           fc=tint(BLUE, "55") if occ else "white", ec=INK, lw=0.9))
        mid = np.deg2rad((th0 + th1) / 2)
        rm = (r_out + r_in) / 2
        ax.text(cx + rm * np.cos(mid), cy + rm * np.sin(mid), data.get(k, ""), ha="center",
                va="center", fontsize=10, family="monospace", weight="bold")
        rl = r_in - 0.38
        ax.text(cx + rl * np.cos(mid), cy + rl * np.sin(mid), str(k), ha="center", va="center",
                fontsize=7, color=GREY)

    def ptr(k, label, color, side):
        mid = np.deg2rad(90 - k * 22.5)
        p_tip = (cx + (r_out + 0.05) * np.cos(mid), cy + (r_out + 0.05) * np.sin(mid))
        p_tail = (cx + (r_out + 1.4) * np.cos(mid), cy + (r_out + 1.4) * np.sin(mid))
        arr(ax, p_tail, p_tip, color=color, lw=1.6, ms=12)
        ax.text(p_tail[0] + 0.15 * side, p_tail[1] - 0.15, label, ha="left" if side > 0 else "right",
                va="top", fontsize=7.5, color=color, weight="bold")
    ptr(4, "tail = 4\n(read index,\nowned by task)", GREEN, +1)
    ptr(12, "head = 12\n(write index,\nowned by ISR)", ORANGE, -1)
    ax.text(cx, cy + 0.25, "buf[16]", ha="center", va="center", fontsize=8.5, weight="bold")
    ax.text(cx, cy - 0.4, "count = 8", ha="center", va="center", fontsize=7.5)

    rbox(ax, 0.2, 7.6, 3.4, 1.4, "UART RX ISR\n(producer)", fc=tint(ORANGE, "30"), bold=True)
    ax.text(1.9, 7.25, "buf[head & 15] = byte;\nhead++;", ha="center", va="top", fontsize=7,
            family="monospace")
    rbox(ax, 13.4, 7.6, 3.4, 1.4, "Parser task\n(consumer)", fc=tint(GREEN, "30"), bold=True)
    ax.text(15.1, 7.25, "byte = buf[tail & 15];\ntail++;", ha="center", va="top", fontsize=7,
            family="monospace")
    notes = ("count = head − tail = 12 − 4 = 8        empty when head = tail        "
             "full when count = 16\n"
             "size 16 = 2^4, so the wrap is a mask (index & 15), not a division; "
             "free-running unsigned counters")
    ax.text(8.5, 0.75, notes, ha="center", va="center", fontsize=7.3)
    save(fig, "23", "fig-23-2-uart-ring-buffer")


# ----------------------------------------------------------------------------
# Figure 23.3 — hash collisions: chaining vs linear probing
# ----------------------------------------------------------------------------
def fig_hash_collisions():
    fig, ax = schematic(6.8, 4.6, xlim=(0, 17), ylim=(-0.7, 11))
    keys = ["VDD", "GND", "CLK", "RST_N", "DATA0", "DATA1"]
    h = {"VDD": 3, "GND": 6, "CLK": 3, "RST_N": 1, "DATA0": 6, "DATA1": 0}
    ax.text(8.5, 10.55, "Insertion order and h(key) mod 8:   " +
            "   ".join(f"{k} → {h[k]}" for k in keys), ha="center", fontsize=7.5)
    bw, bh = 1.0, 0.95
    top = 9.3

    # --- chaining ---
    ax.text(0.3, top + 0.05, "Separate chaining", fontsize=9, weight="bold", va="bottom")
    xa = 1.0
    chains = {}
    for k in keys:
        chains.setdefault(h[k], []).append(k)
    for i in range(8):
        y = top - (i + 1) * bh - 0.1
        ax.add_patch(Rectangle((xa, y), bw, bh, fc=LIGHT, ec=INK, lw=0.9))
        ax.text(xa - 0.2, y + bh / 2, str(i), ha="right", va="center", fontsize=7.5, color=GREY)
        if i in chains:
            ax.plot(xa + bw / 2, y + bh / 2, "o", color=INK, ms=3)
            px = xa + bw / 2
            for j, k in enumerate(chains[i]):
                nx = xa + 1.6 + j * 2.45
                arr(ax, (px, y + bh / 2), (nx, y + bh / 2), lw=0.9, ms=8)
                fc = tint(ORANGE, "40") if j > 0 else tint(BLUE, "40")
                rbox(ax, nx, y + 0.12, 1.75, bh - 0.24, k, fc=fc, fs=7)
                px = nx + 1.75
        else:
            ax.text(xa + bw / 2, y + bh / 2, "∅", ha="center", va="center", fontsize=8, color=GREY)
    ax.text(0.3, 0.55, "collisions extend a chain: bucket 3 → VDD → CLK,\nbucket 6 → GND → DATA0",
            fontsize=7.3, va="center")

    # --- linear probing ---
    ax.text(9.6, top + 0.05, "Linear probing (open addressing)", fontsize=9, weight="bold", va="bottom")
    xb = 10.5
    slot = {}
    probes = []
    for k in keys:
        s = h[k]
        while s in slot:
            probes.append((k, s, (s + 1) % 8))
            s = (s + 1) % 8
        slot[s] = k
    for i in range(8):
        y = top - (i + 1) * bh - 0.1
        k = slot.get(i)
        moved = k is not None and h[k] != i
        fc = tint(ORANGE, "40") if moved else (tint(BLUE, "40") if k else "white")
        ax.add_patch(Rectangle((xb, y), 2.4, bh, fc=fc, ec=INK, lw=0.9))
        ax.text(xb - 0.2, y + bh / 2, str(i), ha="right", va="center", fontsize=7.5, color=GREY)
        if k:
            ax.text(xb + 1.2, y + bh / 2, k, ha="center", va="center", fontsize=7.5)
    for k, s0, s1 in probes:
        y0 = top - (s0 + 0.5) * bh - 0.1
        y1 = top - (s1 + 0.5) * bh - 0.1
        arr(ax, (xb + 2.45, y0), (xb + 2.45, y1), color=RED, rad=-0.9, lw=1.1, ms=8)
        ax.text(xb + 3.15, (y0 + y1) / 2, f"{k}: slot {s0} taken,\nprobe {s1}", fontsize=7,
                color=RED, va="center")
    ax.text(9.6, 0.55, "colliding keys move to the next free slot (orange)", fontsize=7.3,
            va="center")
    ax.text(8.5, -0.35, "load factor α = 6/8 = 0.75 in both tables", ha="center", fontsize=7.5, weight="bold",
            va="center")
    save(fig, "23", "fig-23-3-hash-table-collisions")


# ----------------------------------------------------------------------------
# Figure 23.4 — static timing analysis, critical path
# ----------------------------------------------------------------------------
def fig_sta():
    gates = {"g1": (25, ["a", "b"]), "g2": (18, ["b", "c"]), "g3": (32, ["g1", "g2"]),
             "g4": (20, ["g2", "d"]), "g5": (27, ["g3", "g4"]), "g6": (15, ["g4"])}
    arrival = {"a": 0, "b": 40, "c": 0, "d": 10}
    for g in ["g1", "g2", "g3", "g4", "g5", "g6"]:
        d, ins = gates[g]
        arrival[g] = max(arrival[i] for i in ins) + d
    period = 120
    crit = {("b", "g1"), ("g1", "g3"), ("g3", "g5")}

    fig, ax = schematic(6.8, 4.0, xlim=(0, 17), ylim=(0.7, 10.7))
    gw, gh = 1.7, 1.5
    pos = {"g1": (4.0, 7.2), "g2": (4.0, 3.9), "g3": (8.0, 6.3), "g4": (8.0, 2.7),
           "g5": (12.0, 5.0), "g6": (12.0, 1.4)}
    inp = {"a": 8.6, "b": 6.6, "c": 4.2, "d": 1.9}
    out_pt = {}
    for n, y in inp.items():
        ax.plot(1.2, y, "o", color=INK, ms=4)
        ax.text(0.95, y, f"{n}", ha="right", va="center", fontsize=9, weight="bold")
        ax.text(0.95, y - 0.45, f"{arrival[n]} ps", ha="right", va="center", fontsize=7, color=GREY)
        out_pt[n] = (1.2, y)
    for g, (x, y) in pos.items():
        out_pt[g] = (x + gw, y + gh / 2)
    for g, (x, y) in pos.items():
        d, ins = gates[g]
        n = len(ins)
        for k, src in enumerate(ins):
            chan = {("a", "g1"): 2.1, ("b", "g1"): 2.7, ("b", "g2"): 2.7, ("c", "g2"): 3.3, ("d", "g4"): 7.2, ("g1", "g3"): 6.4, ("g2", "g3"): 6.6, ("g2", "g4"): 6.6, ("g3", "g5"): 10.4, ("g4", "g5"): 10.0, ("g4", "g6"): 10.0}
            yy = y + gh - gh * (k + 1) / (n + 1) if n > 1 else y + gh / 2
            sx, sy = out_pt[src]
            c = (src, g) in crit
            xm = chan[(src, g)]
            if src in ("b", "g2", "g4"): ax.plot(xm, sy, "o", color=RED if src == "b" else INK, ms=3.5, zorder=4)
            ax.plot([sx, xm, xm, x], [sy, sy, yy, yy],
                    color=RED if c else INK, lw=2.6 if c else 1.0, zorder=1 if not c else 3)
        oncrit = g in ("g1", "g3", "g5")
        rbox(ax, x, y, gw, gh, "", fc=tint(RED, "22") if oncrit else LIGHT, ec=RED if oncrit else INK,
             lw=1.8 if oncrit else 0.9)
        ax.text(x + gw / 2, y + gh * 0.64, g, ha="center", va="center", fontsize=9, weight="bold")
        ax.text(x + gw / 2, y + gh * 0.3, f"{d} ps", ha="center", va="center", fontsize=7.5)
        ax.text(x + gw + 0.1, y + gh / 2 + 0.3, f"{arrival[g]}", ha="left", va="bottom", fontsize=8,
                color=RED if oncrit else BLUE, weight="bold")
    # outputs
    for g, col, sl in [("g5", RED, period - arrival["g5"]), ("g6", GREEN, period - arrival["g6"])]:
        sx, sy = out_pt[g]
        ax.plot([sx, 14.6], [sy, sy], color=RED if g == "g5" else INK, lw=2.6 if g == "g5" else 1.0)
        ax.plot(14.6, sy, "o", color=INK, ms=4)
        ax.text(14.8, sy + 0.2, f"{g}: arrival {arrival[g]} ps", fontsize=7.5, va="bottom")
        ax.text(14.8, sy - 0.15, f"slack {sl:+d} ps", fontsize=8.5, va="top", color=col, weight="bold")
    ax.text(16.9, 9.0, "clock period 120 ps", ha="right", fontsize=8.5, weight="bold")
    ax.text(0.2, 10.3, "Arrival times (ps, bold) computed in topological order;"
            " critical path b → g1 → g3 → g5 in red", fontsize=7.5)
    save(fig, "23", "fig-23-4-sta-critical-path")
    return arrival


# ----------------------------------------------------------------------------
# Figure 23.5 — OSPF shortest-path tree
# ----------------------------------------------------------------------------
def fig_ospf():
    links = [("R1", "R2", 10), ("R1", "R3", 1), ("R2", "R4", 10), ("R3", "R4", 10),
             ("R3", "R5", 100), ("R4", "R6", 10), ("R5", "R6", 10), ("R2", "R5", 10)]
    graph = {}
    for u, v, c in links:
        graph.setdefault(u, []).append((v, c))
        graph.setdefault(v, []).append((u, c))
    dist, prev = {"R1": 0}, {}
    pq = [(0, "R1")]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, c in graph[u]:
            if d + c < dist.get(v, float("inf")):
                dist[v], prev[v] = d + c, u
                heapq.heappush(pq, (d + c, v))
    tree = {frozenset((v, u)) for v, u in prev.items()}

    fig, ax = schematic(6.8, 4.1, xlim=(0, 17), ylim=(0.3, 10.3))
    P = {"R1": (1.3, 5.0), "R2": (5.3, 8.85), "R3": (5.3, 1.7), "R4": (7.6, 5.0),
         "R6": (11.0, 5.0), "R5": (14.0, 5.0)}
    # R3-R5 and R2-R5 straight; outer quad R1-R2-R5-R3
    for u, v, c in links:
        (x0, y0), (x1, y1) = P[u], P[v]
        t = frozenset((u, v)) in tree
        ax.plot([x0, x1], [y0, y1], color=BLUE if t else "#AAAAAA", lw=3.2 if t else 1.1,
                zorder=1)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my, str(c), ha="center", va="center", fontsize=8,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"), zorder=2)
    for n, (x, y) in P.items():
        ax.add_patch(Circle((x, y), 0.62, fc="#CFE3F1" if n != "R1" else "#F6C9A6",
                            ec=INK, lw=1.2, zorder=3))
        ax.text(x, y, n, ha="center", va="center", fontsize=9, weight="bold", zorder=4)
    off = {"R1": (0, -1.05), "R2": (0, 0.92), "R3": (0, -1.0), "R4": (0.85, -1.0), "R5": (0, -1.0),
           "R6": (0, 0.92)}
    for n, (x, y) in P.items():
        dx, dy = off[n]
        ax.text(x + dx, y + dy, f"d = {dist[n]}", ha="center", va="center", fontsize=8,
                color=ORANGE if n == "R1" else BLUE, weight="bold")
    ax.text(1.3, 6.0, "source", ha="center", fontsize=7, color=GREY)
    # legend
    ax.plot([11.3, 12.3], [9.2, 9.2], color=BLUE, lw=3.2)
    ax.text(12.5, 9.2, "shortest-path tree", fontsize=7.5, va="center")
    ax.plot([11.3, 12.3], [8.5, 8.5], color="#AAAAAA", lw=1.1)
    ax.text(12.5, 8.5, "unused link", fontsize=7.5, va="center")
    ax.text(16.9, 1.2, "OSPF cost (ref. 10 Gb/s):\n1 = 10 Gb/s,  10 = 1 Gb/s,  100 = 100 Mb/s",
            ha="right", va="center", fontsize=7.5)
    save(fig, "23", "fig-23-5-ospf-shortest-path-tree")
    return dist, prev


if __name__ == "__main__":
    fig_array_vs_list()
    fig_ring_buffer()
    fig_hash_collisions()
    print(fig_sta())
    print(fig_ospf())
