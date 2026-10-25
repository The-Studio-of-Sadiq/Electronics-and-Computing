"""Figures for Chapter 24 — Scientific Computing.

Run from the repository root:  python figures/scripts/ch24.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Circle  # noqa: E402
from matplotlib.ticker import FixedLocator, NullFormatter  # noqa: E402
import scipy.sparse as sp  # noqa: E402
from scipy.sparse.linalg import spsolve  # noqa: E402

from figstyle import COLORS, INK, save, schematic, new_fig  # noqa: E402

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


def rbox(ax, x, y, w, h, text="", fc=LIGHT, ec=INK, fs=7.5, lw=0.9, bold=False, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fc, ec=ec, lw=lw, ls=ls))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                weight="bold" if bold else "normal")


# ----------------------------------------------------------------------------
# Figure 24.1 — roofline of the four-core laptop (numbers from Listing 24.1)
# ----------------------------------------------------------------------------
def fig_roofline():
    P_peak, B = 4 * 2.8 * 16, 47.0          # GFLOP/s (179.2), GB/s
    ridge = P_peak / B
    fig, ax = new_fig(6.4, 4.0)
    I = np.logspace(np.log10(0.05), 3, 400)
    ax.loglog(I, np.minimum(P_peak, I * B), color=INK, lw=2.0)
    # shaded bands of typical kernels
    bands = [(0.1, 0.2, "SpMV\n0.1–0.2", PINK), (0.42, 0.6, "7-point\nstencil\n≈ 0.5", YELLOW),
             (0.8, 1.25, "FFT\n≈ 1", GREEN)]
    for lo, hi, lab, c in bands:
        ax.axvspan(lo, hi, color=c, alpha=0.22, lw=0)
        ax.text(np.sqrt(lo * hi), 1.15, lab, ha="center", va="bottom", fontsize=7, color=INK)
    ax.axvline(ridge, color=GREY, lw=0.8, ls=":")
    ax.plot(ridge, P_peak, "o", color=INK, ms=4)
    ax.annotate(f"ridge point\n{ridge:.1f} flop/byte", xy=(ridge, P_peak), xytext=(ridge * 2.2, 60),
                fontsize=7.5, ha="left", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.text(300, P_peak * 1.12, f"compute roof {P_peak:.0f} GFLOP/s", ha="center", fontsize=7.5)
    ax.text(1.5, 105, f"memory roof\nB = {B:.0f} GB/s", rotation=0, fontsize=7.5,
            ha="right", va="bottom")
    pts = [("DGEMV", 0.25, 11.7, BLUE, (0.058, 28)), ("DGESV n = 3000", 125, 36.9, ORANGE, (14, 14)),
           ("DGEMM", 250, 87.4, GREEN, (35, 105))]
    for name, x, y, c, xt in pts:
        ax.plot(x, y, "o", color=c, ms=7, mec=INK, mew=0.6, zorder=5)
        ax.annotate(f"{name}\n({x:g}, {y} GFLOP/s)", xy=(x, y), xytext=xt, fontsize=7.5, color=c,
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.7))
    ax.text(0.07, 150, "memory-bound", fontsize=9, color=GREY, style="italic")
    ax.text(30, 4, "compute-bound", fontsize=9, color=GREY, style="italic")
    ax.set(xlim=(0.05, 1000), ylim=(1, 300), xlabel="Arithmetic intensity (flop/byte)",
           ylabel="Performance (GFLOP/s)")
    ax.grid(True, which="major", alpha=0.5)
    save(fig, "24", "fig-24-1-roofline-laptop")


# ----------------------------------------------------------------------------
# Figure 24.2 — static IR-drop map (solves Listing 24.2)
# ----------------------------------------------------------------------------
def ir_drop():
    k, R_seg = 300, 0.1
    n = k * k
    idx = np.arange(n).reshape(k, k)
    pads = np.zeros((k, k), bool)
    pads[15::30, 15::30] = True
    I = np.full((k, k), 4.0 / n)
    I[100:130, 180:210] += 1.0 / 900
    g = 1 / R_seg
    right = (idx[:, :-1].ravel(), idx[:, 1:].ravel())
    down = (idx[:-1, :].ravel(), idx[1:, :].ravel())
    rows = np.concatenate([right[0], down[0]])
    cols = np.concatenate([right[1], down[1]])
    G = sp.coo_matrix((np.full(rows.size, -g), (rows, cols)), shape=(n, n))
    G = (G + G.T).tocsr()
    G = G - sp.diags(np.asarray(G.sum(axis=1)).ravel())
    free = ~pads.ravel()
    Gff = G[free][:, free].tocsc()
    d = np.zeros(n)
    d[free] = spsolve(Gff, I.ravel()[free])
    return d.reshape(k, k), pads


def fig_ir_drop():
    d, pads = ir_drop()
    dmv = d * 1e3
    r, c = np.unravel_index(dmv.argmax(), dmv.shape)
    fig, ax = plt.subplots(figsize=(5.4, 4.4))
    pitch = 0.01                                  # mm per node; node i at i * 10 um
    ext = [-pitch / 2, 3 - pitch / 2, -pitch / 2, 3 - pitch / 2]
    im = ax.imshow(dmv, origin="lower", extent=ext, cmap="viridis", vmin=0, vmax=20,
                   interpolation="nearest")
    pr, pc = np.nonzero(pads)
    ax.plot(pc * pitch, pr * pitch, "o", ms=2.6, mfc="white", mec="white", ls="none",
            label="VDD bumps (300 µm pitch)")
    ax.add_patch(Rectangle((1.80, 1.00), 0.30, 0.30, fc="none", ec="white", lw=1.2, ls="--"))
    ax.plot(c * pitch, r * pitch, "x", color=RED, ms=7, mew=1.8)
    ax.annotate(f"max {dmv.max():.1f} mV\n({c * pitch:.2f}, {r * pitch:.2f}) mm",
                xy=(c * pitch, r * pitch), xytext=(2.0, 0.55), color="white", fontsize=7.5, bbox=dict(fc="#222222", ec="none", alpha=0.75, pad=2),
                arrowprops=dict(arrowstyle="-", color="white", lw=0.8))
    ax.text(1.76, 1.2, "hot spot +1 A", color="white", fontsize=7.5, ha="right", va="center", bbox=dict(fc="#222222", ec="none", alpha=0.75, pad=1.5))
    ax.set(xlabel="x (mm)", ylabel="y (mm)", xlim=(0, 3), ylim=(0, 3))
    ax.set_xticks(np.arange(0, 3.01, 0.5))
    ax.set_yticks(np.arange(0, 3.01, 0.5))
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("IR drop (mV)")
    ax.set_title("white dots: VDD bumps, 10 x 10 on 300 µm pitch (held at 0.80 V)", fontsize=8)
    save(fig, "24", "fig-24-2-ir-drop-map")
    return dmv.max(), (r, c)


# ----------------------------------------------------------------------------
# Figure 24.3 — simulation campaign workflow
# ----------------------------------------------------------------------------
def fig_workflow():
    fig, ax = schematic(6.8, 4.6, xlim=(0, 17), ylim=(0, 11.5))
    fs = 7
    # 1: Git repository with config + models
    ax.add_patch(FancyBboxPatch((0.2, 5.6), 4.4, 5.6, boxstyle="round,pad=0.02,rounding_size=0.2",
                                fc="none", ec=GREY, lw=1.0, ls="--"))
    ax.text(2.4, 10.85, "Git repository", ha="center", fontsize=7.5, color=GREY, weight="bold")
    rbox(ax, 0.45, 8.3, 3.9, 2.2, "", fc=tint(YELLOW, "35"))
    ax.text(2.4, 10.1, "1  Configuration", ha="center", fontsize=7.8, weight="bold")
    ax.text(2.4, 9.15, "YAML: parameter\nranges, corners,\nMC seed, model version", ha="center",
            va="center", fontsize=6.7)
    rbox(ax, 0.45, 5.9, 3.9, 2.1, "", fc=tint(YELLOW, "35"))
    ax.text(2.4, 7.65, "Models", ha="center", fontsize=7.8, weight="bold")
    ax.text(2.4, 6.75, "netlists, device\nmodels, PDK release", ha="center", va="center", fontsize=6.7)
    # 2: case generator
    rbox(ax, 5.3, 7.2, 4.0, 2.8, "", fc=LIGHT)
    ax.text(7.3, 9.55, "2  Case generator", ha="center", fontsize=7.8, weight="bold")
    ax.text(7.3, 8.3, "expands grid or\ndraws Monte Carlo\nsamples; hash key\nper case",
            ha="center", va="center", fontsize=6.7)
    arr(ax, (4.6, 8.6), (5.3, 8.6))
    # 3: cache diamond
    dx, dy, dw, dh = 11.35, 8.6, 3.1, 2.7
    ax.add_patch(Polygon([(dx, dy + dh / 2), (dx + dw / 2, dy), (dx, dy - dh / 2), (dx - dw / 2, dy)],
                         closed=True, fc=tint(PINK, "30"), ec=INK, lw=0.9))
    ax.text(dx, dy, "3  Cache:\nresult for\nthis hash?", ha="center", va="center", fontsize=6.7)
    arr(ax, (9.3, 8.6), (dx - dw / 2, 8.6))
    ax.text(9.55, 8.35, "cases", ha="center", va="top", fontsize=6.3, color=GREY)
    # 4: execution
    rbox(ax, 13.4, 6.0, 3.4, 5.0, "", fc=tint(BLUE, "25"))
    ax.text(15.1, 10.6, "4  Execution", ha="center", fontsize=7.8, weight="bold")
    ax.text(15.1, 9.85, "pool of workers", ha="center", fontsize=fs)
    for j, t in enumerate(["laptop cores", "cluster (Slurm)", "cloud"]):
        rbox(ax, 13.65, 8.75 - j * 0.85, 2.9, 0.65, t, fc="white", fs=6.6)
    ax.text(15.1, 6.65, "each runs\nngspice -b or solve_ivp", ha="center", va="center", fontsize=6.2)
    arr(ax, (dx + dw / 2, 8.6), (13.4, 8.6))
    ax.text(13.15, 8.75, "no", ha="center", fontsize=6.8, color=RED)
    # 5: results store (bottom right)
    rbox(ax, 12.7, 1.4, 4.1, 3.0, "", fc=tint(GREEN, "30"))
    ax.text(14.75, 4.0, "5  Results store", ha="center", fontsize=7.8, weight="bold")
    ax.text(14.75, 2.65, "HDF5 or Parquet;\none record per case:\nparameters, outputs,\nstatus, runtime",
            ha="center", va="center", fontsize=6.7)
    arr(ax, (15.1, 6.0), (15.1, 4.4))
    ax.text(15.25, 5.2, "outputs,\nstatus", ha="left", va="center", fontsize=6.3, color=GREY)
    # cache hit -> skip to store
    ax.plot([dx, dx], [dy - dh / 2, 3.6], color=GREEN, lw=1.1)
    arr(ax, (dx, 3.6), (12.7, 3.6), color=GREEN)
    ax.text(dx + 0.15, 6.3, "yes:\nskip,\nreuse", ha="left", va="center", fontsize=6.8, color=GREEN)
    # 6: post-processing
    rbox(ax, 6.4, 1.4, 4.0, 3.0, "", fc=LIGHT)
    ax.text(8.4, 4.0, "6  Post-processing", ha="center", fontsize=7.8, weight="bold")
    ax.text(8.4, 2.7, "yield, worst case,\nsensitivities, plots", ha="center", va="center", fontsize=fs)
    arr(ax, (12.7, 2.4), (10.4, 2.4))
    ax.text(11.55, 2.05, "records", ha="center", va="top", fontsize=6.3, color=GREY)
    # 7: report
    rbox(ax, 0.6, 1.4, 4.4, 3.0, "", fc=tint(ORANGE, "30"))
    ax.text(2.8, 4.0, "7  Report", ha="center", fontsize=7.8, weight="bold")
    ax.text(2.8, 2.7, "figures and tables\nregenerated by\none command", ha="center", va="center",
            fontsize=fs)
    arr(ax, (6.4, 2.4), (5.0, 2.4))
    ax.text(5.7, 2.05, "metrics", ha="center", va="top", fontsize=6.3, color=GREY)
    # feedback: post-processing -> configuration (in the repository)
    ax.plot([8.4, 8.4, 3.4], [4.4, 5.0, 5.0], color=PINK, lw=1.3, ls="--")
    ax.annotate("", xy=(3.4, 5.6), xytext=(3.4, 4.98),
                arrowprops=dict(arrowstyle="-|>", color=PINK, lw=1.3, mutation_scale=10,
                                shrinkA=0, shrinkB=0))
    ax.text(3.7, 5.25, "refine sweep (edit configuration)", ha="left", fontsize=7, color=PINK,
            weight="bold")
    ax.text(8.5, 0.55, "Results are keyed by hash(parameters, model version): "
            "an interrupted campaign resumes; nothing is recomputed.", ha="center", fontsize=6.8,
            color=GREY)
    save(fig, "24", "fig-24-3-simulation-workflow")


# ----------------------------------------------------------------------------
# Figure 24.4 — Amdahl and Gustafson
# ----------------------------------------------------------------------------
def fig_amdahl():
    N = np.logspace(0, 10, 300, base=2)
    fig, ax = new_fig(6.4, 4.0)
    ax.plot(N, N, "--", color=INK, lw=1.0, label="ideal  S = N")
    cols = {0.01: BLUE, 0.05: ORANGE, 0.10: GREEN}
    for s, c in cols.items():
        ax.plot(N, 1 / (s + (1 - s) / N), color=c, lw=1.8)
        ax.plot(N, N - s * (N - 1), color=c, lw=1.4, ls=(0, (5, 1.5, 1, 1.5)))
        ax.text(1100, 1 / (s + (1 - s) / 1024), f"Amdahl s = {s:.2f} (→ {1/s:.0f})", fontsize=7.5,
                color=c, va="center")
    ax.text(1100, 1024 * 1.0, "Gustafson\ns = 0.01, 0.05, 0.10\n(near the ideal)", fontsize=7.5,
            va="center", color=INK)
    # marked points
    sA = 1 / (0.05 + 0.95 / 32)
    sG = round(32 - 0.05 * 31 + 1e-9, 1)  # 30.45 -> 30.5 as in the text
    ax.plot([32, 32], [sA, sG], "o", color=ORANGE, ms=6, mec=INK, mew=0.6, zorder=5)
    ax.annotate(f"N = 32, s = 0.05:\nAmdahl {sA:.1f}", xy=(32, sA), xytext=(80, 3.2), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.annotate(f"Gustafson {sG:.1f}", xy=(32, sG), xytext=(5, 60), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
    ax.plot(4, 2.6, "s", color=RED, ms=6.5, mec=INK, mew=0.6, zorder=6)
    ax.annotate("measured Monte Carlo,\n4 workers: S = 2.6\n(Listing 24.4)", xy=(4, 2.6),
                xytext=(6, 1.25), fontsize=7.5, color=RED,
                arrowprops=dict(arrowstyle="-", color=RED, lw=0.6))
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ticks = [2 ** k for k in range(11)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t) for t in ticks])
    ax.set_yticks(ticks)
    ax.set_yticklabels([str(t) for t in ticks])
    ax.set(xlim=(1, 1024), ylim=(1, 1024), xlabel="Number of processors N", ylabel="Speed-up S")
    ax.grid(True, alpha=0.5)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=INK, ls="--", lw=1.0), Line2D([], [], color=GREY, lw=1.8),
         Line2D([], [], color=GREY, lw=1.4, ls=(0, (5, 1.5, 1, 1.5)))]
    ax.legend(h, ["ideal S = N", "Amdahl (fixed problem)", "Gustafson (scaled problem)"],
              loc="upper left", fontsize=7.5)
    save(fig, "24", "fig-24-4-amdahl-gustafson")


# ----------------------------------------------------------------------------
# Figure 24.5 — trunk-based Git workflow
# ----------------------------------------------------------------------------
def fig_git():
    fig, ax = schematic(6.8, 4.5, xlim=(0, 17), ylim=(0, 11.2))
    ym, yf, yb = 5.6, 7.7, 3.4
    r = 0.3
    main_x = [0.9, 2.2, 3.5, 6.1, 7.6, 9.0, 13.2, 14.6]
    merge1, merge2 = 6.1, 13.2
    tag_x = 7.6
    fix = [3.9, 5.1]           # branch from 2.2
    feat = [10.0, 11.0, 12.0]  # branch from 9.0
    ax.plot([0.5, 16.0], [ym, ym], color=INK, lw=2.2, zorder=1)
    ax.annotate("", xy=(16.4, ym), xytext=(15.9, ym),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2, mutation_scale=12))
    ax.text(16.5, ym - 0.45, "main", fontsize=9, weight="bold", ha="right", va="top")
    # fix branch
    ax.plot([2.2, fix[0], fix[-1], merge1], [ym, yf, yf, ym], color=ORANGE, lw=1.8, zorder=1)
    for x in fix:
        ax.add_patch(Circle((x, yf), r, fc=ORANGE, ec=INK, lw=0.8, zorder=3))
    ax.text(4.5, yf + 0.45, "fix/loss-model-units", ha="center", fontsize=7.5, color=ORANGE,
            weight="bold")
    # feature branch
    ax.plot([9.0, feat[0], feat[-1], merge2], [ym, yb, yb, ym], color=GREEN, lw=1.8, zorder=1)
    for x in feat:
        ax.add_patch(Circle((x, yb), r, fc=GREEN, ec=INK, lw=0.8, zorder=3))
    ax.text(11.0, yb - 0.75, "feature/ir-drop-solver", ha="center", fontsize=7.5, color=GREEN,
            weight="bold")
    for x in main_x:
        merge = x in (merge1, merge2)
        ax.add_patch(Circle((x, ym), r * (1.2 if merge else 1.0), fc="white" if not merge else "#BBBBBB",
                            ec=INK, lw=1.2 if merge else 0.9, zorder=3))
    ax.text(merge1, ym - 0.75, "merge\ncommit", ha="center", va="top", fontsize=6.5, color=GREY)
    ax.text(merge2 + 0.3, ym + 0.5, "merge commit", ha="left", va="bottom", fontsize=6.5, color=GREY)

    # PR boxes
    def pr_box(x, y, w, title, color):
        rbox(ax, x, y, w, 2.2, "", fc="white", ec=color, lw=1.2)
        ax.text(x + 0.2, y + 1.85, title, fontsize=7.5, weight="bold", color=color, va="center")
        for j, t in enumerate(["CI tests passed", "coverage 87 %", "review approved by colleague"]):
            yy = y + 1.3 - j * 0.48
            ax.text(x + 0.25, yy, "✔", fontsize=8, color=GREEN, va="center")
            ax.text(x + 0.7, yy, t, fontsize=7, va="center")
    pr_box(0.4, 8.6, 4.4, "Pull request", ORANGE)
    pr_box(11.85, 0.2, 5.0, "Pull request", GREEN)
    # tag flag on a main commit after the first merge
    ax.plot([tag_x, tag_x], [ym + r, ym + 2.1], color=INK, lw=1.0)
    ax.add_patch(Polygon([(tag_x, ym + 2.1), (tag_x + 1.6, ym + 1.8), (tag_x, ym + 1.5)], closed=True,
                         fc=YELLOW, ec=INK, lw=0.8))
    ax.text(tag_x + 0.1, ym + 2.35, "tag v1.4.0", fontsize=8, weight="bold", va="bottom")
    ax.text(tag_x + 1.8, ym + 1.8, "used in design\nreview DR-3", fontsize=7, va="center", color=GREY)
    # hash box around the tagged commit
    ax.add_patch(Rectangle((tag_x - 0.75, ym - 1.55), 1.5, 1.25, fc="none", ec=BLUE, lw=1.0, ls="--"))
    ax.text(tag_x, ym - 1.0, "a1fea18", ha="center", va="center", fontsize=7.2, family="monospace",
            color=BLUE)
    # results manifest file icon
    fx, fy, fw, fh = 4.4, 0.6, 2.4, 2.6
    ax.add_patch(Polygon([(fx, fy), (fx + fw, fy), (fx + fw, fy + fh - 0.5), (fx + fw - 0.5, fy + fh),
                          (fx, fy + fh)], closed=True, fc=LIGHT, ec=INK, lw=0.9))
    ax.plot([fx + fw - 0.5, fx + fw - 0.5, fx + fw], [fy + fh, fy + fh - 0.5, fy + fh - 0.5],
            color=INK, lw=0.8)
    ax.text(fx + fw / 2, fy + fh - 0.75, "manifest.json", ha="center", fontsize=6.5, weight="bold")
    ax.text(fx + 0.25, fy + 1.05, 'commit:\n "a1fea18"\nseed, env …', fontsize=6, family="monospace",
            va="center")
    arr(ax, (tag_x - 0.3, ym - 1.55), (fx + fw + 0.05, fy + 1.6), color=BLUE, rad=-0.2)
    ax.text(7.2, 1.6, "commit recorded\nin results", fontsize=7, color=BLUE, ha="left", va="center")
    save(fig, "24", "fig-24-5-git-branch-pr-workflow")


if __name__ == "__main__":
    fig_roofline()
    print("IR drop max (mV), node:", fig_ir_drop())
    fig_workflow()
    fig_amdahl()
    fig_git()
