"""Figures for Chapter 27 — Real-Time Computing.

Run from the repository root:  python figures/scripts/ch27.py
"""
import sys
from math import ceil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Patch  # noqa: E402

from figstyle import COLORS, INK, GRID, save  # noqa: E402

BLUE, ORANGE, GREEN, PINK, YELLOW, SKY = COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4], COLORS[5]
RED = "#C62828"
GREY = "#777777"


def bar(ax, y, t0, t1, fc, h=0.6, text="", tc=INK, fs=7.5, hatch=None, ec=INK, lw=0.7):
    ax.add_patch(Rectangle((t0, y - h / 2), t1 - t0, h, fc=fc, ec=ec, lw=lw, hatch=hatch))
    if text:
        ax.text((t0 + t1) / 2, y, text, ha="center", va="center", fontsize=fs, color=tc)


def up_arrow(ax, x, y, h=0.55, color=INK):
    ax.annotate("", xy=(x, y + h), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.1, mutation_scale=8, shrinkA=0, shrinkB=0))


def down_arrow(ax, x, y, h=0.55, color=RED):
    ax.annotate("", xy=(x, y), xytext=(x, y + h),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.1, mutation_scale=8, shrinkA=0, shrinkB=0))


def bracket(ax, x0, x1, y, text="", color=INK, fs=7.5, va="top", dy=-0.06, style="|-|"):
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle=style, color=color, lw=0.9, mutation_scale=3, shrinkA=0, shrinkB=0))
    if text:
        ax.text((x0 + x1) / 2, y + dy, text, ha="center", va=va, fontsize=fs, color=color)


def gantt_axes(ax, xmax, ylabels, ypos, xstep=1, xlabel="time (ms)"):
    ax.set_xlim(0, xmax)
    ax.set_yticks(ypos)
    ax.set_yticklabels(ylabels)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xticks(np.arange(0, xmax + 1e-9, xstep))
    ax.set_xlabel(xlabel)
    for x in np.arange(0, xmax + 1e-9, xstep):
        ax.axvline(x, color=GRID, lw=0.5, zorder=0)


# ----------------------------------------------------------------------------
# Figure 27.1 — timing parameters of a periodic task
# ----------------------------------------------------------------------------
def fig_task_parameters():
    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    y = 1.5
    bar(ax, y, 0.2, 0.6, "white", hatch="////", ec=GREY)
    bar(ax, y, 1.4, 2.0, "white", hatch="////", ec=GREY)
    bar(ax, y, 0.6, 1.4, BLUE, text="job 1", tc="white")
    bar(ax, y, 2.0, 2.6, BLUE)
    bar(ax, y, 5.0, 6.4, BLUE, text="job 2", tc="white")
    for r in (0, 5, 10):
        up_arrow(ax, r, y + 0.3, 0.75, color=INK)
    for d in (4, 9):
        down_arrow(ax, d, y + 0.3, 0.75, color=RED)
    ax.text(0.05, y + 1.12, "release", fontsize=7, ha="left", va="bottom")
    ax.text(4.05, y + 1.12, "deadline (D = 4 ms)", fontsize=7, ha="left", va="bottom", color=RED)
    ax.text(9.05, y + 1.12, "deadline", fontsize=7, ha="left", va="bottom", color=RED)
    ax.text(10.05, y + 1.12, "release", fontsize=7, ha="left", va="bottom")
    ax.text(1.0, y + 0.55, "higher-priority task\n(hatched)", fontsize=6.8, ha="center", va="bottom",
            color=GREY)
    # brackets
    bracket(ax, 0, 0.2, y - 0.5, "J = 0.2", fs=7)
    bracket(ax, 0, 2.6, y - 1.0, "R = 2.6 ms (response time)", color=BLUE)
    bracket(ax, 2.6, 4.0, y - 0.5, "slack = D − R\n= 1.4 ms", color=GREEN, fs=7)
    ax.text(1.6, y - 1.55, "C = 0.8 + 0.6 = 1.4 ms (own execution only)", ha="center", va="top", fontsize=7.5,
            color=BLUE)
    bracket(ax, 5.0, 6.4, y - 0.5, "R = C = 1.4 ms", color=BLUE, fs=7)
    bracket(ax, 0, 5, y + 1.75, "T = 5 ms", fs=7.5, va="bottom", dy=0.06)
    ax.text(8.6, y - 1.0, "output jitter: completion 2.6 ms after\nrelease in job 1, 1.4 ms in job 2"
            "\n→ varies by 1.2 ms", ha="left", va="center", fontsize=7.2, color=ORANGE)
    ax.set_ylim(-0.4, 3.75)
    gantt_axes(ax, 12, ["task τ$_i$"], [y])
    ax.legend(handles=[Patch(fc=BLUE, ec=INK, label="τ$_i$ executes"),
                       Patch(fc="white", ec=GREY, hatch="////", label="preempted by higher priority")],
              loc="upper right", fontsize=7, ncol=2, bbox_to_anchor=(1.0, 1.08))
    fig.tight_layout()
    save(fig, "27", "fig-27-1-task-timing-parameters")


# ----------------------------------------------------------------------------
# Figure 27.2 — Cortex-M interrupt latency
# ----------------------------------------------------------------------------
def fig_interrupt_latency():
    f = 168e6
    st = 12 / f * 1e6       # 0.071 µs
    tc = 6 / f * 1e6        # 0.036 µs
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    Y = [3.7, 2.15, 0.6]
    vis = 0.07   # stacking drawn to scale (0.071 µs)
    # row 1: best case
    y = Y[0]
    bar(ax, y, 0, st, ORANGE)
    bar(ax, y, st, 1.4, BLUE, text="ISR", tc="white")
    up_arrow(ax, 0, y + 0.3, 0.5, color=RED)
    ax.annotate("stacking 12 cycles = 71 ns", xy=(st / 2, y + 0.3), xytext=(1.7, y + 0.55), fontsize=7,
                va="center", arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.text(1.5, y, "latency 0.071 µs", fontsize=7.5, va="center", color=RED)
    # row 2: tail-chaining
    y = Y[1]
    bar(ax, y, 0, st, ORANGE)
    bar(ax, y, st, 1.2, SKY, text="ISR A")
    bar(ax, y, 1.2, 1.2 + tc, GREY)
    bar(ax, y, 1.2 + tc, 2.4, BLUE, text="ISR B", tc="white")
    up_arrow(ax, 0, y + 0.3, 0.5, color=INK)
    up_arrow(ax, 0.5, y + 0.3, 0.5, color=RED)
    ax.text(0.55, y + 0.85, "IRQ B pending", fontsize=7, color=RED, va="center")
    ax.annotate("tail-chain 6 cycles = 36 ns,\nno unstacking/restacking", xy=(1.2 + tc / 2, y + 0.3),
                xytext=(2.65, y + 0.5), fontsize=7, va="center", arrowprops=dict(arrowstyle="-", lw=0.6))
    # row 3: worst case
    y = Y[2]
    bar(ax, y, 0, 2.0, "#DDDDDD", text="background code in critical\nsection (interrupts off, 2 µs)", fs=7)
    bar(ax, y, 2.0, 5.0, PINK, text="higher-priority ISR 3 µs", fs=7.5)
    bar(ax, y, 5.0, 5.0 + st, ORANGE)
    bar(ax, y, 5.0 + st, 6.0, BLUE, text="target\nISR", tc="white", fs=7)
    up_arrow(ax, 0, y + 0.3, 0.5, color=RED)
    up_arrow(ax, 0.06, y + 0.3, 0.5, color=PINK)
    bracket(ax, 0, 5.071, y - 0.48, "worst-case latency 5.07 µs", color=RED)
    ax.text(0.1, y + 0.9, "target IRQ and higher-priority IRQ asserted at t = 0", fontsize=7, color=RED,
            va="center")
    ax.text(6.0, Y[0] + 0.9, "best 0.07 µs, worst 5.07 µs → jitter ≈ 5 µs", ha="right", fontsize=8,
            va="center", weight="bold")
    ax.set_ylim(-0.25, 4.75)
    gantt_axes(ax, 6, ["best case", "tail-chaining", "worst case"], Y, xlabel="time (µs)")
    ax.legend(handles=[Patch(fc=ORANGE, ec=INK, label="exception entry (stacking)"),
                       Patch(fc=BLUE, ec=INK, label="target ISR"),
                       Patch(fc=PINK, ec=INK, label="higher-priority ISR")],
              loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=7)
    fig.tight_layout()
    save(fig, "27", "fig-27-2-cortex-m-interrupt-latency")


# ----------------------------------------------------------------------------
# Figure 27.3 — utilisation bounds
# ----------------------------------------------------------------------------
def fig_utilisation_bounds():
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    n = np.arange(1, 21)
    u = n * (2 ** (1 / n) - 1)
    ax.fill_between(n, u, 1.0, color=YELLOW, alpha=0.25, lw=0, step=None)
    ax.plot(n, u, "o-", color=BLUE, ms=4, label="RMS (Liu–Layland) bound n(2$^{1/n}$ − 1)")
    ax.axhline(1.0, color=GREEN, lw=1.6, label="EDF: U ≤ 1 (necessary and sufficient)")
    ax.axhline(np.log(2), color=BLUE, lw=1.0, ls="--")
    ax.text(20, np.log(2) - 0.008, "ln 2 = 0.693", ha="right", va="top", fontsize=7.5, color=BLUE)
    for k in (1, 2, 3, 4, 5, 10):
        ax.annotate(f"{u[k - 1]:.3f}", xy=(k, u[k - 1]), xytext=(5, -10) if k == 1 else ((0, 6) if k == 10 else (-3, -11)),
                    textcoords="offset points", ha="left" if k == 1 else ("center" if k == 10 else "right"), fontsize=7, color=BLUE)
    ax.plot(3, 0.90, "D", color=RED, ms=7, zorder=5)
    ax.annotate("flight controller, n = 3, U = 0.90:\nabove the RMS bound, below 1;\nschedulable by "
                "response-time analysis", xy=(3, 0.90), xytext=(4.6, 0.925), fontsize=7.5, color=RED,
                va="center", arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.8, mutation_scale=8))
    ax.text(13.5, 0.85, "RMS test inconclusive:\nuse response-time analysis", ha="center", va="center",
            fontsize=8, color="#8A6D00")
    ax.set_xlim(0.5, 20.5)
    ax.set_ylim(0.6, 1.05)
    ax.set_xticks(n)
    ax.set_xlabel("number of tasks n")
    ax.set_ylabel("schedulable utilisation U")
    ax.legend(loc="lower left", fontsize=7.5)
    fig.tight_layout()
    save(fig, "27", "fig-27-3-utilisation-bounds")


# ----------------------------------------------------------------------------
# Figure 27.4 — RMS Gantt chart of the flight controller
# ----------------------------------------------------------------------------
def rms_schedule(tasks, horizon, dt=1.0):
    """Simulate preemptive fixed-priority scheduling (tasks sorted by priority) on an integer grid."""
    rem = [0.0] * len(tasks)
    rel = [0.0] * len(tasks)
    slots, completions = [], []
    t = 0.0
    while t < horizon - 1e-9:
        for i, (name, c, T) in enumerate(tasks):
            if abs((t / T) - round(t / T)) < 1e-9:
                rem[i] = c
                rel[i] = t
        run = next((i for i in range(len(tasks)) if rem[i] > 1e-9), None)
        if run is not None:
            slots.append((run, t, t + dt))
            rem[run] -= dt
            if rem[run] <= 1e-9:
                completions.append((run, rel[run], t + dt))
        t += dt
    return slots, completions


def fig_rms_gantt():
    tasks = [("attitude", 1, 4), ("estimator", 2, 5), ("logging", 3, 12)]
    slots, comps = rms_schedule(tasks, 24)
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    Y = {0: 3.0, 1: 1.85, 2: 0.7}
    colors = [ORANGE, BLUE, GREEN]
    merged = []
    for i, t0, t1 in slots:
        if merged and merged[-1][0] == i and abs(merged[-1][2] - t0) < 1e-9:
            merged[-1] = (i, merged[-1][1], t1)
        else:
            merged.append((i, t0, t1))
    for i, t0, t1 in merged:
        bar(ax, Y[i], t0, t1, colors[i], h=0.55)
    for i, (name, c, T) in enumerate(tasks):
        for r in np.arange(0, 24 + 1e-9, T):
            up_arrow(ax, r, Y[i] + 0.28, 0.42, color=INK)
            if r > 0:
                ax.plot([r, r], [Y[i] - 0.42, Y[i] - 0.28], color=RED, lw=1.6)
    # worst-case responses
    worst = {}
    for i, rel, done in comps:
        worst[i] = max(worst.get(i, 0), done - rel)
    bracket(ax, 0, 10, Y[2] - 0.55, "", color=GREEN)
    ax.text(5, Y[2] - 0.62, "first logging job: R = 10 ms", ha="center", va="top", fontsize=7.5, color=GREEN)
    ax.text(15.5, Y[2] - 0.62, "second job done at 19 ms", ha="center", va="top", fontsize=7.5, color=GREEN)
    for x0, x1 in [(19, 20), (23, 24)]:
        ax.text((x0 + x1) / 2, Y[2] + 0.55, "idle", ha="center", va="bottom", fontsize=7, color=GREY)
    labels = [f"attitude\nC = 1, T = 4\nR = {worst[0]:g} ms", f"estimator\nC = 2, T = 5\nR = {worst[1]:g} ms",
              f"logging\nC = 3, T = 12\nR = {worst[2]:g} ms"]
    ax.set_ylim(-0.2, 3.7)
    gantt_axes(ax, 24, labels, [Y[0], Y[1], Y[2]])
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_xticklabels([str(k) if k % 2 == 0 else "" for k in range(25)])
    ax.legend(handles=[plt.Line2D([], [], color=INK, marker="^", ls="", ms=5, label="release"),
                       plt.Line2D([], [], color=RED, marker="|", ls="", ms=8, mew=1.6, label="deadline")],
              loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=7.5)
    fig.tight_layout()
    save(fig, "27", "fig-27-4-rms-gantt-flight-controller")


# ----------------------------------------------------------------------------
# Figure 27.5 — priority inversion and inheritance
# ----------------------------------------------------------------------------
def fig_priority_inversion():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.0), sharex=True)
    Y = {"H": 2.6, "M": 1.6, "L": 0.6}
    C = {"H": RED, "M": YELLOW, "L": BLUE}

    def cs(ax, y, t0, t1, c, text=""):
        bar(ax, y, t0, t1, c, h=0.5, text=text, fs=7)
        ax.add_patch(Rectangle((t0, y - 0.25), t1 - t0, 0.5, fill=False, hatch="xx", ec="white", lw=0))

    # --- without inheritance ---
    ax = a1
    bar(ax, Y["L"], 0, 1, C["L"], h=0.5)
    cs(ax, Y["L"], 1, 2, C["L"])
    bar(ax, Y["H"], 2, 2.5, C["H"], h=0.5)
    cs(ax, Y["L"], 2.5, 3, C["L"])
    bar(ax, Y["M"], 3, 9, C["M"], h=0.5, text="M runs 6 ms (needs no mutex)", fs=7.5)
    cs(ax, Y["L"], 9, 9.5, C["L"])
    cs(ax, Y["H"], 9.5, 10.5, C["H"])
    bar(ax, Y["L"], 10.5, 11, C["L"], h=0.5)
    ax.plot([2.5, 9.5], [Y["H"], Y["H"]], color=RED, lw=1.0, ls=":")
    ax.text(4.6, Y["H"] - 0.1, "H blocked on mutex", ha="center", va="top", fontsize=7, color=RED)
    for t, k, lab in [(1, "L", "lock"), (9.5, "L", "unlock")]:
        ax.annotate(lab, xy=(t, Y[k] + 0.25), xytext=(t, Y[k] + 0.6), ha="center", fontsize=6.8,
                    arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate("request", xy=(2.5, Y["H"] + 0.25), xytext=(2.5, Y["H"] + 0.6), ha="center", fontsize=6.8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    up_arrow(ax, 2, Y["H"] - 0.25, -0.0)
    for t, k in [(2, "H"), (3, "M")]:
        ax.annotate("", xy=(t, Y[k] + 0.25), xytext=(t, Y[k] - 0.45),
                    arrowprops=dict(arrowstyle="-|>", lw=1.0, mutation_scale=7, color=INK))
    ax.plot([7, 7], [Y["H"] - 0.45, Y["H"] + 0.62], color=RED, lw=2)
    ax.text(7.08, Y["H"] + 0.52, "deadline 7 ms — missed", fontsize=7, color=RED, va="center", weight="bold")
    bracket(ax, 2.5, 9.5, 0.0, "unbounded inversion 2.5–9.5 ms (grows with every medium-priority task)",
            color=RED, fs=7.2, va="top", dy=-0.08)
    ax.set_title("Without priority inheritance", fontsize=9, loc="left")
    ax.set_ylim(-0.75, 3.4)

    # --- with inheritance ---
    ax = a2
    bar(ax, Y["L"], 0, 1, C["L"], h=0.5)
    cs(ax, Y["L"], 1, 2, C["L"])
    bar(ax, Y["H"], 2, 2.5, C["H"], h=0.5)
    cs(ax, Y["L"], 2.5, 3.5, C["L"])
    ax.add_patch(Rectangle((2.5, Y["L"] - 0.25), 1.0, 0.5, fill=False, ec=RED, lw=1.8))
    ax.text(3.0, Y["L"] + 0.3, "L at H's priority", ha="center", va="bottom", fontsize=6.8, color=RED)
    cs(ax, Y["H"], 3.5, 4.5, C["H"])
    bar(ax, Y["M"], 4.5, 10.5, C["M"], h=0.5, text="M runs 6 ms (ready at 3 ms, could not preempt L)", fs=7)
    bar(ax, Y["L"], 10.5, 11, C["L"], h=0.5)
    ax.plot([2.5, 3.5], [Y["H"], Y["H"]], color=RED, lw=1.0, ls=":")
    ax.plot([3, 4.5], [Y["M"], Y["M"]], color=GREY, lw=1.0, ls=":")
    for t, k in [(2, "H"), (3, "M")]:
        ax.annotate("", xy=(t, Y[k] + 0.25), xytext=(t, Y[k] - 0.45),
                    arrowprops=dict(arrowstyle="-|>", lw=1.0, mutation_scale=7, color=INK))
    ax.annotate("unlock", xy=(3.5, Y["L"] + 0.15), xytext=(4.0, Y["L"] + 0.15), ha="left", va="center", fontsize=6.8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.plot([7, 7], [Y["H"] - 0.45, Y["H"] + 0.62], color=GREEN, lw=2)
    ax.text(7.08, Y["H"] + 0.52, "deadline 7 ms — met (H done at 4.5 ms)", fontsize=7, color=GREEN,
            va="center", weight="bold")
    bracket(ax, 2.5, 3.5, 0.0, "", color=GREEN)
    ax.text(3.8, -0.0, "blocking bounded by one critical section: 1 ms", ha="left", va="center", fontsize=7.2,
            color=GREEN)
    ax.set_title("With priority inheritance", fontsize=9, loc="left")
    ax.set_ylim(-0.75, 3.4)

    for ax in (a1, a2):
        gantt_axes(ax, 12, ["H (high)", "M (medium)", "L (low)"], [Y["H"], Y["M"], Y["L"]])
    a1.set_xlabel("")
    a1.tick_params(labelbottom=True)
    a2.legend(handles=[Patch(fc=BLUE, ec=INK, hatch="xx", label="inside critical section (mutex held)"),
                       plt.Line2D([], [], color=INK, marker="^", ls="", ms=5, label="release")],
              loc="upper right", fontsize=7, ncol=2, bbox_to_anchor=(1.0, -0.3))
    fig.tight_layout()
    save(fig, "27", "fig-27-5-priority-inversion-inheritance")


# ----------------------------------------------------------------------------
# Figure 27.6 — control-loop jitter
# ----------------------------------------------------------------------------
def fig_control_jitter():
    T = 50.0
    t = np.linspace(0, 150, 15001)
    carrier = np.abs(((t + T / 2) % T) - T / 2) / (T / 2)   # 0 at valleys (0, 50, 100), 1 at peaks
    triggers = [25.0, 75.0, 125.0]
    comp = [10.0, 15.0, 12.0]
    duties = [0.4, 0.6, 0.5, 0.45]   # before first update, then after each update

    def pwm(update_times):
        cmp = np.full_like(t, duties[0])
        for k, tu in enumerate(update_times):
            cmp[t >= tu] = duties[k + 1]
        return (carrier < cmp).astype(float), cmp

    imm_t = [tr + c for tr, c in zip(triggers, comp)]
    sh_t = [tr + T for tr in triggers]
    p_imm, _ = pwm(imm_t)
    p_sh, _ = pwm(sh_t)

    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    Yc, Yi, Ypi, Ys, Yps = 6.9, 5.3, 3.75, 2.2, 0.65
    ax.plot(t, Yc + carrier * 1.1, color=INK, lw=1.2)
    for tr in triggers:
        ax.annotate("", xy=(tr, Yc + 1.15), xytext=(tr, Yc + 1.75),
                    arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.2, mutation_scale=8))
    ax.text(25, Yc + 1.85, "ADC trigger at carrier peak", ha="center", fontsize=7, color=GREEN, va="bottom")
    # duty compare levels on the carrier
    for k in range(3):
        pass

    def comp_row(y, label_delay, updates, color):
        for tr, c in zip(triggers, comp):
            bar(ax, y, tr, tr + c, SKY, h=0.55, text=f"{c:g} µs", fs=7)
        for tu in updates:
            ax.annotate("", xy=(tu, y - 0.35), xytext=(tu, y + 0.55),
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3, mutation_scale=8))

    comp_row(Yi, "", imm_t, ORANGE)
    ax.plot(t, Ypi + p_imm * 0.7, color=ORANGE, lw=1.4)
    comp_row(Ys, "", sh_t, BLUE)
    ax.plot(t, Yps + p_sh * 0.7, color=BLUE, lw=1.4)
    # asymmetric pulse marker (immediate update lands mid-pulse around t = 100)
    ax.annotate("asymmetric pulse:\nupdate mid-pulse", xy=(90.5, Ypi + 0.7), xytext=(113.8, Ypi + 0.33),
                fontsize=7, color=ORANGE, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=ORANGE, mutation_scale=7))
    for v in (50, 100, 150):
        ax.plot([v, v], [Ypi - 0.15, Ypi + 0.85], color=GREY, lw=0.6, ls=":")
        ax.plot([v, v], [Yps - 0.15, Yps + 0.85], color=GREY, lw=0.6, ls=":")
    # brackets
    bracket(ax, 25, 35, Yi - 0.5, "", color=ORANGE)
    bracket(ax, 75, 90, Yi - 0.5, "", color=ORANGE)
    ax.text(55, Yi, "delay 10–15 µs,\njitter 5 µs", ha="center", va="center", fontsize=7, color=ORANGE)
    bracket(ax, 25, 75, Ys + 0.75, "constant delay 50 µs", color=BLUE, va="bottom", dy=0.06)
    bracket(ax, 75, 125, Ys + 0.75, "50 µs", color=BLUE, va="bottom", dy=0.06)
    ax.text(72.5, Yps + 0.35, "symmetric\npulses", ha="center", fontsize=7, color=BLUE, va="center")

    ax.set_yticks([Yc + 0.55, Yi, Ypi + 0.35, Ys, Yps + 0.35])
    ax.set_yticklabels(["PWM carrier", "immediate:\ncompute", "PWM output", "shadow register:\ncompute",
                        "PWM output"], fontsize=8)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 150)
    ax.set_ylim(0.2, 9.1)
    ax.set_xticks(np.arange(0, 151, 25))
    ax.set_xlabel("time (µs)   —   20 kHz PWM, period 50 µs")
    fig.text(0.5, 0.005, "Phase lag at the 1 kHz crossover: immediate update 4.5° ± 0.9° (varies every cycle); "
             "shadow register 18° (constant)", ha="center", fontsize=7.8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, "27", "fig-27-6-control-loop-jitter")


if __name__ == "__main__":
    fig_task_parameters()
    fig_interrupt_latency()
    fig_utilisation_bounds()
    fig_rms_gantt()
    fig_priority_inversion()
    fig_control_jitter()
