"""Figures for Chapter 6 — Diode Circuits.

Run from the repository root:  python figures/scripts/ch06.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import schemdraw  # noqa: E402
import schemdraw.elements as elm  # noqa: E402

from figstyle import COLORS, INK, box, save  # noqa: E402

schemdraw.use("matplotlib")

BLUE, ORANGE, GREEN, PINK, AMBER, SKY = COLORS[:6]
GREY = "#888888"


def line(d, a, b, **kw):
    return d.add(elm.Line(**kw).at(a).to(b))


def dot(d, p, **kw):
    d.add(elm.Dot(**kw).at(p))


def canvas(fig, rect, xlim=None, ylim=None):
    ax = fig.add_axes(rect)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax


# ----------------------------------------------------------------------------
# Figure 6.1 — the three rectifiers
# ----------------------------------------------------------------------------
VRMS, F, RL, VD = 12.0, 50.0, 10.0, 0.7
VM = VRMS * math.sqrt(2)


def _xfmr(d, ct=False):
    t = elm.Transformer(t1=4, t2=8 if ct else 4).right().at((0, 0))
    if ct:
        t = t.tap(name="ct", pos=4, side="secondary")
    return d.add(t)


def fig_6_1():
    fig = plt.figure(figsize=(6.8, 4.9))
    cols = [0.0, 0.335, 0.67]
    w = 0.33
    # (a) half-wave ------------------------------------------------------
    ax = canvas(fig, [cols[0], 0.5, w, 0.46])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=1.6, lw=1.1)
    t = _xfmr(d)
    d.add(elm.Label().at((t.p1[0] - 0.15, (t.p1[1] + t.p2[1]) / 2)).label("230 V", halign="right"))
    ytop, ybot = t.s1[1] + 0.6, t.s2[1] - 0.6
    line(d, t.s1, (t.s1[0], ytop))
    d1 = d.add(elm.Diode().right().at((t.s1[0], ytop)).length(2.2).label("D1", loc="top"))
    line(d, d1.end, (d1.end[0] + 0.5, ytop))
    xo = d1.end[0] + 0.5
    dot(d, (xo, ytop))
    r = d.add(elm.Resistor().down().at((xo, ytop)).toy(ybot).label("10 Ω", loc="bottom"))
    line(d, (xo, ybot), (t.s2[0], ybot))
    line(d, (t.s2[0], ybot), t.s2)
    d.add(elm.Label().at((t.s2[0] + 0.25, (t.s1[1] + t.s2[1]) / 2)).label("12 V\nrms", halign="left", fontsize=7.5))
    d.add(elm.Label().at((xo + 0.3, ytop + 0.35)).label("$v_o$", fontsize=9))
    d.draw(show=False)
    ax.text((t.s1[0] + d1.end[0]) / 2 + 0.1, ytop - 0.55, "PIV = 17.0 V", fontsize=7.5,
            ha="center", va="top", color=PINK)
    ax.set_title("(a) half-wave", fontsize=9, weight="bold")

    # (b) centre-tapped ---------------------------------------------------
    ax = canvas(fig, [cols[1], 0.5, w, 0.46])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=1.6, lw=1.1)
    t = _xfmr(d, ct=True)
    ytop, ybot = t.s1[1] + 0.3, t.s2[1] - 0.3
    xr, xd2 = t.s1[0] + 3.0, t.s1[0] + 4.0
    line(d, t.s1, (t.s1[0], ytop))
    d1 = d.add(elm.Diode().right().at((t.s1[0], ytop)).length(2.0).label("D1", loc="top"))
    line(d, d1.end, (xd2, ytop))
    line(d, t.s2, (t.s2[0], ybot))
    d2 = d.add(elm.Diode().right().at((t.s2[0], ybot)).length(2.0).label("D2", loc="bottom"))
    line(d, d2.end, (xd2, ybot))
    line(d, (xd2, ybot), (xd2, ytop))
    dot(d, (xr, ytop))
    dot(d, (xd2, ytop))
    r = d.add(elm.Resistor().down().at((xr, ytop)).toy(t.ct[1]).label("10 Ω", loc="bottom"))
    line(d, t.ct, (xr, t.ct[1]))
    dot(d, (xr, t.ct[1]))
    line(d, (xr, t.ct[1]), (xr, t.ct[1] - 0.3))
    d.add(elm.Ground().at((xr, t.ct[1] - 0.3)))
    d.add(elm.Label().at((t.s1[0] + 0.2, (t.s1[1] + t.ct[1]) / 2)).label("12 V", halign="left", fontsize=7.2))
    d.add(elm.Label().at((t.s1[0] + 0.2, (t.s2[1] + t.ct[1]) / 2)).label("12 V", halign="left", fontsize=7.2))
    d.add(elm.Label().at((xr + 0.25, ytop + 0.35)).label("$v_o$", fontsize=9))
    d.draw(show=False)
    ax.text(t.s1[0] + 1.0, ybot - 0.7, "PIV = 2$V_m$ = 33.9 V", fontsize=7.5, ha="center",
            va="top", color=PINK)
    ax.set_title("(b) centre-tapped full-wave", fontsize=9, weight="bold")

    # (c) bridge -------------------------------------------------------------
    ax = canvas(fig, [cols[2], 0.5, w, 0.46])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=1.6, lw=1.1)
    t = _xfmr(d)
    s = 1.35                                    # diamond half-diagonal
    cx, cy = t.s1[0] + 2.3, (t.s1[1] + t.s2[1]) / 2
    T, B, L, R = (cx, cy + s), (cx, cy - s), (cx - s, cy), (cx + s, cy)
    ln = math.hypot(s, s)
    # diodes point toward the + node R and away from the - node L
    d.add(elm.Diode().at(T).theta(-45).length(ln).color(ORANGE).label("D1", loc="top", ofst=0.05))
    d.add(elm.Diode().at(B).theta(45).length(ln).color(BLUE).label("D2", loc="bottom", ofst=0.05))
    d.add(elm.Diode().at(L).theta(-45).length(ln).color(ORANGE).label("D3", loc="bottom", ofst=0.05))
    d.add(elm.Diode().at(L).theta(45).length(ln).color(BLUE).label("D4", loc="top", ofst=0.05))
    line(d, t.s1, (t.s1[0], T[1]))
    line(d, (t.s1[0], T[1]), T)
    line(d, t.s2, (t.s2[0], B[1]))
    line(d, (t.s2[0], B[1]), B)
    for p in (T, B, L, R):
        dot(d, p)
    # load from + (R) to - (L), drawn below the bridge
    yl = B[1] - 0.7
    xl = R[0] + 0.8
    line(d, R, (xl, R[1]))
    rl = d.add(elm.Resistor().down().at((xl, R[1])).toy(yl).label("10 Ω", loc="bottom"))
    d.add(elm.Ground().at((xl, yl)))
    line(d, L, (L[0] - 0.45, L[1]))
    line(d, (L[0] - 0.45, L[1]), (L[0] - 0.45, L[1] - 0.4))
    d.add(elm.Ground().at((L[0] - 0.45, L[1] - 0.4)))
    d.add(elm.Label().at((R[0] + 0.15, R[1] + 0.3)).label("+", fontsize=9))
    d.add(elm.Label().at((L[0] - 0.15, L[1] + 0.3)).label("−", fontsize=9))
    d.add(elm.Label().at((xl + 0.25, R[1] + 0.35)).label("$v_o$", fontsize=9))
    d.draw(show=False)
    ax.text(cx, yl - 0.75, "+ half: D1, D3   − half: D2, D4", fontsize=7, ha="center", va="top")
    ax.text(cx, yl - 1.25, "PIV = $V_m$ = 17.0 V", fontsize=7.5, ha="center", va="top",
            color=PINK)
    ax.set_title("(c) bridge", fontsize=9, weight="bold")

    # waveforms --------------------------------------------------------------
    tt = np.linspace(0, 40e-3, 4000)
    vs = VM * np.sin(2 * math.pi * F * tt)
    outs = [np.maximum(vs - VD, 0), np.maximum(np.abs(vs) - VD, 0),
            np.maximum(np.abs(vs) - 2 * VD, 0)]
    pk = [VM - VD, VM - VD, VM - 2 * VD]
    rip = ["ripple at 50 Hz", "ripple at 100 Hz", "ripple at 100 Hz"]
    for k, (vo, p) in enumerate(zip(outs, pk)):
        a = fig.add_axes([cols[k] + 0.06, 0.1, w - 0.085, 0.3])
        a.plot(tt * 1e3, vs, color=GREY, ls="--", lw=1.0, label="$v_s$")
        a.plot(tt * 1e3, vo, color=BLUE if k < 2 else GREEN, lw=1.7, label="$v_o$")
        a.axhline(0, color=GREY, lw=0.5)
        a.set_ylim(-19, 22)
        a.set_xlim(0, 40)
        a.set_xticks([0, 10, 20, 30, 40])
        a.set_xlabel("time (ms)", fontsize=8.5)
        a.tick_params(labelsize=8)
        if k == 0:
            a.set_ylabel("voltage (V)", fontsize=8.5)
            a.legend(loc="lower left", fontsize=7, ncol=2, handlelength=1.4)
        a.text(39.5, 21.5, f"peak {p:.1f} V", fontsize=7.5, ha="right", va="top")
        a.text(0.5, 21.5, rip[k], fontsize=7, ha="left", va="top", color="#555555")
    save(fig, "06", "fig-6-1-rectifier-circuits")


# ----------------------------------------------------------------------------
# Figure 6.2 — capacitor-input bridge waveforms
# ----------------------------------------------------------------------------
def bridge_sim(Vrms=18.0, f=50.0, Rs=1.0, Vd=0.8, rd=0.05, C=3300e-6, Iload=1.0,
               cycles=40, n=4000):
    """Same time-stepping model as Listing 6.1."""
    dt = 1 / (f * n)
    t = np.arange(cycles * n) * dt
    vs = np.sqrt(2) * Vrms * np.sin(2 * np.pi * f * t)
    vc = np.zeros_like(t)
    i = np.zeros_like(t)
    v = 0.0
    for k in range(len(t)):
        drive = abs(vs[k]) - 2 * Vd - v
        i[k] = drive / (Rs + 2 * rd) if drive > 0 else 0.0
        v = max(v + (i[k] - Iload) * dt / C, 0.0)
        vc[k] = v
    s = slice((cycles - 2) * n, cycles * n)
    return t[s] - t[s][0], vs[s], vc[s], i[s]


def fig_6_2():
    t, vs, vc, i = bridge_sim()
    tm = t * 1e3
    rect_src = np.abs(vs) - 1.6
    fig = plt.figure(figsize=(6.8, 5.2))
    # circuit inset
    ac = canvas(fig, [0.06, 0.72, 0.88, 0.27])
    d = schemdraw.Drawing(canvas=ac, show=False)
    d.config(fontsize=8, unit=1.7, lw=1.1)
    src = d.add(elm.SourceSin().up().at((0, 0)).length(2.4))
    d.add(elm.Label().at((-0.55, 1.5)).label("18 V rms", halign="right"))
    rs = d.add(elm.Resistor().right().at(src.end).length(2.0).label("1.0 Ω", loc="top"))
    s = 1.2
    cx, cy = rs.end[0] + 1.6, 1.2
    T, B, L, R = (cx, cy + s), (cx, cy - s), (cx - s, cy), (cx + s, cy)
    ln = math.hypot(s, s)
    d.add(elm.Diode().at(T).theta(-45).length(ln).color(ORANGE))
    d.add(elm.Diode().at(B).theta(45).length(ln).color(BLUE))
    d.add(elm.Diode().at(L).theta(-45).length(ln).color(ORANGE))
    d.add(elm.Diode().at(L).theta(45).length(ln).color(BLUE))
    line(d, rs.end, (cx, rs.end[1]))
    line(d, (cx, rs.end[1]), T)
    line(d, src.start, (cx, src.start[1]))
    line(d, (cx, src.start[1]), B)
    ytop, ybot = cy + s + 0.4, cy - s - 0.2
    xc = R[0] + 1.0
    line(d, R, (xc, R[1]))
    line(d, (xc, R[1]), (xc, ytop))
    line(d, (xc, ytop), (xc + 4.2, ytop))
    d.add(elm.Capacitor(polar=True).down().at((xc + 1.2, ytop)).toy(ybot)
          .label("3300 µF", loc="bottom", ofst=0.15))
    d.add(elm.SourceI().down().at((xc + 4.2, ytop)).toy(ybot).label("1 A\nload", loc="bottom"))
    line(d, (xc + 1.2, ybot), (xc + 4.2, ybot))
    d.add(elm.Ground().at((xc + 2.7, ybot)))
    line(d, L, (L[0] - 0.7, L[1]))
    line(d, (L[0] - 0.7, L[1]), (L[0] - 0.7, L[1] - 0.4))
    d.add(elm.Ground().at((L[0] - 0.7, L[1] - 0.4)))
    for p in (T, B, L, R, (xc + 1.2, ytop), (xc + 1.2, ybot)):
        dot(d, p)
    d.draw(show=False)
    ac.text(-0.55, 0.45, "each diode\n0.8 V + 0.05 Ω", fontsize=7.5, ha="right", va="top")
    for lbl, dx, dy, col in (("D1", 0.62, 0.62, ORANGE), ("D2", 0.62, -0.62, BLUE),
                             ("D3", -0.62, -0.62, ORANGE), ("D4", -0.62, 0.62, BLUE)):
        ac.text(cx + dx * 0.45, cy + dy * 0.45, lbl, fontsize=7.3, color=col, ha="center",
                va="center")

    # top panel: voltages
    a1 = fig.add_axes([0.1, 0.4, 0.86, 0.28])
    cond = i > 0
    a1.fill_between(tm, 17.0, 26.6, where=cond, color=AMBER, alpha=0.25, lw=0)
    a1.plot(tm, rect_src, color=GREY, ls="--", lw=1.1, label="$|v_s|-2V_{F0}$ (peak 23.9 V)")
    a1.plot(tm, vc, color=BLUE, lw=1.8, label="capacitor voltage $v_C$")
    # constant-discharge estimate from each peak
    pk_idx = [k for k in range(1, len(vc) - 1) if vc[k] >= vc[k - 1] and vc[k] > vc[k + 1]]
    for k in pk_idx:
        t0 = tm[k]
        tl = np.linspace(t0, t0 + 10, 50)
        a1.plot(tl, vc[k] - 1.0 / 3300e-6 * (tl - t0) * 1e-3, color=INK, ls=":", lw=1.2)
    a1.set_ylim(17.0, 26.6)
    a1.set_xlim(0, 40)
    a1.set_ylabel("V")
    vmin, vmax = vc.min(), vc.max()
    for v in (vmin, vmax):
        a1.plot([26.0, 33.5], [v, v], color=INK, lw=0.6, ls=(0, (2, 2)))
    a1.annotate("", xy=(31.0, vmin), xytext=(31.0, vmax),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, mutation_scale=7))
    a1.text(31.0, vmax + 0.35, f"ripple {vmax - vmin:.2f} V p-p", fontsize=7.8, ha="center",
            va="bottom")
    k0 = pk_idx[0]
    a1.annotate("constant-discharge\nestimate: 3.03 V", xy=(tm[k0] + 7.5, vc[k0] - 2.27),
                xytext=(tm[k0] + 1.6, 22.4), fontsize=7.5, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6))
    seg = np.where(np.diff(cond.astype(int)) == 1)[0]
    a1.text(tm[seg[0]] + 0.1, 24.5, "recharge\n69°", fontsize=7.3, color="#9A6B00", va="top")
    a1.legend(loc="upper right", fontsize=7.3, ncol=2, frameon=True, facecolor="white",
              edgecolor="none", framealpha=1.0, borderpad=0.2)
    plt.setp(a1.get_xticklabels(), visible=False)
    a1.grid(True, lw=0.4)

    # bottom panel: currents
    a2 = fig.add_axes([0.1, 0.08, 0.86, 0.28], sharex=a1)
    half = (np.floor(t / 10e-3).astype(int)) % 2
    for hlf, col, lbl in ((0, ORANGE, "D1–D3 pulses"), (1, BLUE, "D2–D4 pulses")):
        m = cond & (half == hlf)
        a2.fill_between(tm, 0, np.where(m, i, 0), color=col, alpha=0.35, lw=0, label=lbl)
    a2.plot(tm, i, color=INK, lw=1.2)
    a2.plot(tm, i - 1.0, color=GREEN, lw=1.5, label="capacitor current $i - 1$ A")
    a2.axhline(0, color=GREY, lw=0.6)
    a2.set_ylim(-1.5, 6.4)
    a2.set_ylabel("A")
    a2.set_xlabel("time (ms)")
    isec = np.sqrt(np.mean(i ** 2))
    icap = np.sqrt(np.mean((i - 1) ** 2))
    a2.text(0.4, 5.0, f"peak {i.max():.2f} A;  RMS: secondary {isec:.2f} A, capacitor {icap:.2f} A",
            fontsize=7.8, va="top")
    a2.legend(loc="upper left", fontsize=7.3, ncol=3, bbox_to_anchor=(0.0, 1.02))
    a2.grid(True, lw=0.4)
    save(fig, "06", "fig-6-2-capacitor-filter-waveforms")


# ----------------------------------------------------------------------------
# Figure 6.3 — clipper transfer characteristics
# ----------------------------------------------------------------------------
def fig_6_3():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 3.4), gridspec_kw=dict(width_ratios=[1, 1.1]))
    Rs, VB, Is, n, VT = 1e3, 3.0, 1e-9, 1.8, 0.02585
    vo = np.linspace(-10, VB + n * VT * math.log(10e-3 / Is + 1), 3000)
    iD = Is * (np.exp(np.clip((vo - VB) / (n * VT), -50, 60)) - 1)
    vi = vo + Rs * iD
    m = vi <= 10
    a.plot(vi[m], vo[m], color=BLUE, label="A: shunt clipper, $V_B$ = 3.0 V, 1 kΩ")
    vin = np.linspace(-10, 10, 500)
    a.plot(vin, np.clip(vin, -5.8, 5.8), color=ORANGE, ls="--", label="B: back-to-back 5.1 V Zeners")
    a.axhline(0, color=GREY, lw=0.5)
    a.axvline(0, color=GREY, lw=0.5)
    a.set_xlim(-10, 10)
    a.set_ylim(-10, 10)
    a.set_aspect("equal")
    a.set_xlabel("$v_{in}$ (V)")
    a.set_ylabel("$v_{out}$ (V)")
    a.grid(True, lw=0.4)
    a.legend(loc="upper left", fontsize=6.8, handlelength=1.6)
    # slope in the clipped region
    v9 = np.interp(9.0, vi, vo)
    v7 = np.interp(7.0, vi, vo)
    a.annotate(f"slope ≈ {(v9 - v7) / 2:.3f}", xy=(8.0, (v9 + v7) / 2), xytext=(4.6, -2.2),
               fontsize=7.5, color=BLUE, arrowprops=dict(arrowstyle="-", color=BLUE, lw=0.6))
    a.text(9.7, -5.4, "±5.8 V", fontsize=7.5, color=ORANGE, ha="right", va="top")
    a.text(9.7, 3.35, f"≈{v9:.2f} V", fontsize=7.5, color=BLUE, ha="right", va="top")

    t = np.linspace(0, 2e-3, 1000)
    vs = 8 * np.sin(2 * math.pi * 1e3 * t)
    b.plot(t * 1e3, vs, color=GREY, ls="--", lw=1.2, label="input, 8 V peak, 1 kHz")
    b.plot(t * 1e3, np.clip(vs, -5.8, 5.8), color=ORANGE, lw=1.8, label="output of clipper B")
    for s in (1, -1):
        b.axhline(s * 5.8, color=ORANGE, lw=0.6, ls=":")
    b.text(0.03, 6.1, "+5.8 V", fontsize=7.5, color=ORANGE, ha="left")
    b.text(0.03, -6.1, "−5.8 V", fontsize=7.5, color=ORANGE, ha="left", va="top")
    b.set_xlim(0, 2)
    b.set_ylim(-10, 10)
    b.set_xlabel("time (ms)")
    b.set_ylabel("voltage (V)")
    b.legend(loc="lower left", fontsize=7.3, ncol=2, bbox_to_anchor=(0, -0.02))
    b.grid(True, lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "06", "fig-6-3-clipper-transfer")


# ----------------------------------------------------------------------------
# Figure 6.4 — clamper
# ----------------------------------------------------------------------------
def clamp_sim(RC, t_end=3e-3, n=60000, Vp=5.0, f=1e3, R=100e3, Rsrc=50.0, Is=1e-14, nd=1.0):
    """Square-wave source (series Rsrc) -> series C -> shunt diode || R (output node)."""
    C = RC / R
    dt = t_end / n
    t = np.arange(n) * dt
    vin = np.where((t * f) % 1.0 < 0.5, Vp, -Vp)
    vc = 0.0                     # capacitor voltage (input side minus output side)
    vo = np.zeros(n)
    VT = 0.02585
    for k in range(n):
        # solve vout from KCL: (vin - vc - vout)/Rsrc = vout/R - Id(-vout)
        # diode: anode at ground, cathode at output -> conducts when vout < 0
        v = vin[k] - vc
        lo, hi = -2.0, 20.0
        for _ in range(60):
            mid = (lo + hi) / 2
            idd = Is * (math.exp(min(-mid / (nd * VT), 80)) - 1)
            fval = (v - mid) / Rsrc - mid / R + idd
            if fval > 0:
                lo = mid
            else:
                hi = mid
        vout = (lo + hi) / 2
        ic = (v - vout) / Rsrc
        vc += ic * dt / C
        vo[k] = vout
    return t, vin, vo


def fig_6_4():
    fig = plt.figure(figsize=(6.8, 3.3))
    ax = canvas(fig, [0.0, 0.05, 0.34, 0.85])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=1.8, lw=1.1)
    src = d.add(elm.SourceSquare().up().at((0, 0)).length(2.6))
    d.add(elm.Label().at((-0.5, 1.3)).label("1 kHz\n±5 V", halign="right"))
    line(d, src.end, (0, 3.0))
    c = d.add(elm.Capacitor().right().at((0, 3.0)).length(2.0).label("C = 1 µF", loc="top"))
    no = (c.end[0] + 0.3, 3.0)
    line(d, c.end, no)
    dot(d, no)
    d.add(elm.Diode().up().at((no[0], 0)).toy(no[1]).label("Si", loc="bottom"))
    line(d, no, (no[0] + 1.4, 3.0))
    d.add(elm.Resistor().down().at((no[0] + 1.4, 3.0)).toy(0).label("R\n100 kΩ", loc="bottom"))
    line(d, src.start, (no[0] + 1.4, 0))
    dot(d, (no[0], 0))
    d.add(elm.Ground().at((no[0] / 2, 0)))
    d.add(elm.Dot(open=True).at((no[0] + 1.4, 3.0)).label("$v_{out}$", loc="right"))
    d.draw(show=False)
    ax.text(no[0] + 0.7, -0.95, "RC = 0.1 s,  T = 1 ms", ha="center", fontsize=8)
    ax.set_title("Negative-peak clamper", fontsize=9, weight="bold")

    a = fig.add_axes([0.53, 0.16, 0.45, 0.74])
    X = 20
    t, vin, vo = clamp_sim(RC=0.1 / X)
    a.plot(t * 1e3, vin, color=GREY, ls="--", lw=1.2, label="input")
    a.plot(t * 1e3, vo, color=BLUE, lw=1.6, label="output")
    a.axhline(-0.6, color=PINK, lw=0.7, ls=":")
    a.axhline(9.4, color=PINK, lw=0.7, ls=":")
    a.text(3.0, -0.75, "−0.6 V", fontsize=7.5, color=PINK, ha="right", va="top")
    a.text(1.02, 9.55, "+9.4 V", fontsize=7.5, color=PINK, ha="left", va="bottom")
    a.annotate(f"droop drawn ×{X}\n(actual ≈47 mV = 9.4 mV per 0.1 ms)", xy=(1.95, 8.6),
               xytext=(2.05, 5.6), fontsize=7.3, ha="center",
               arrowprops=dict(arrowstyle="-", lw=0.6))
    a.annotate("first cycle:\nC charging", xy=(0.55, -2.5), xytext=(0.62, -6.6), fontsize=7.3,
               arrowprops=dict(arrowstyle="-", lw=0.6))
    a.set_xlim(0, 3)
    a.set_ylim(-7.5, 11.5)
    a.set_xlabel("time (ms)")
    a.set_ylabel("voltage (V)")
    a.legend(loc="upper left", fontsize=7.5, ncol=2)
    a.grid(True, lw=0.4)
    save(fig, "06", "fig-6-4-clamper")


# ----------------------------------------------------------------------------
# Figure 6.5 — voltage multipliers
# ----------------------------------------------------------------------------
def fig_6_5():
    fig = plt.figure(figsize=(6.8, 4.8))
    # (a) Greinacher / Villard doubler
    ax = canvas(fig, [0.0, 0.08, 0.42, 0.84])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=8, unit=1.8, lw=1.1)
    src = d.add(elm.SourceSin().up().at((0, 0)).length(2.4))
    d.add(elm.Label().at((-0.5, 1.2)).label("peak $V_m$", halign="right"))
    line(d, src.end, (0, 3.0))
    c1 = d.add(elm.Capacitor().right().at((0, 3.0)).length(1.8).label("C1", loc="top"))
    nx = (c1.end[0] + 0.2, 3.0)
    line(d, c1.end, nx)
    dot(d, nx)
    d.add(elm.Diode().up().at((nx[0], 0)).toy(3.0).label("D1", loc="bottom"))
    d2 = d.add(elm.Diode().right().at(nx).length(1.9).label("D2", loc="top"))
    no = d2.end
    dot(d, no)
    d.add(elm.Capacitor().down().at(no).toy(0).label("C2", loc="bottom"))
    line(d, (no[0], 3.0), (no[0] + 0.7, 3.0))
    d.add(elm.Dot(open=True).at((no[0] + 0.7, 3.0)))
    line(d, src.start, (no[0], 0))
    dot(d, (nx[0], 0))
    d.add(elm.Ground().at((no[0], 0)))
    d.draw(show=False)
    ax.text(nx[0] + 0.15, 2.55, "clamper node:\n0 to $2V_m$", ha="left", va="top", fontsize=7.6,
            color=BLUE)
    ax.text(no[0] + 0.85, 3.0, "output\n$2V_m$", ha="left", va="center", fontsize=7.8,
            color=GREEN)
    ax.text(nx[0] - 0.95, 1.5, "clamper\n(C1, D1)", ha="center", fontsize=7.3, color="#555555")
    ax.text(no[0] + 1.5, 1.2, "peak\ndetector\n(D2, C2)", ha="center", fontsize=7.3,
            color="#555555")
    ax.set_title("(a) half-wave (Greinacher) doubler", fontsize=9, weight="bold", pad=14)

    # (b) five-stage Cockcroft-Walton
    ax = canvas(fig, [0.45, 0.0, 0.55, 1.0])
    d = schemdraw.Drawing(canvas=ax, show=False)
    d.config(fontsize=7.5, unit=1.0, lw=1.0)
    h, xs, xp = 0.95, 3.0, 0.0
    N = 5
    S = [(xs, 2 * k * h) for k in range(N + 1)]            # smoothing-column nodes
    P = [(xp, (2 * k - 1) * h) for k in range(N + 1)]      # pumping-column nodes
    for k in range(1, N + 1):
        d.add(elm.Capacitor().at(P[k - 1]).to(P[k]))
        d.add(elm.Capacitor().at(S[k - 1]).to(S[k]))
        d.add(elm.Diode().at(S[k - 1]).to(P[k]).color(ORANGE))
        d.add(elm.Diode().at(P[k]).to(S[k]).color(ORANGE))
        dot(d, P[k])
        dot(d, S[k])
    dot(d, S[0])
    # transformer secondary between P0 and ground
    yb = P[0][1] - 1.2
    t = d.add(elm.Transformer(t1=4, t2=4).right().anchor("s1").at(P[0]))
    line(d, t.s2, (t.s2[0], yb))
    line(d, (t.s2[0], yb), (xs, yb))
    line(d, (xs, yb), S[0])
    d.add(elm.Ground().at((xs, yb)))
    line(d, S[N], (xs + 0.9, S[N][1]))
    d.add(elm.Dot(open=True).at((xs + 0.9, S[N][1])))
    d.draw(show=False)
    for k in range(1, N + 1):
        ax.text(xs + 0.25, S[k][1] - 0.12, f"{2 * k} kV", fontsize=7.8, color=GREEN, va="top")
    ax.text(xs + 1.0, S[N][1] + 0.25, "output: 10 kV ideal,\n9.976 kV at 100 µA", fontsize=7.8,
            va="bottom", ha="left", color=GREEN)
    ax.text(t.p1[0] - 0.15, (t.p1[1] + t.p2[1]) / 2, "HF\ninverter", fontsize=7.3, ha="right",
            va="center")
    ax.text(t.p1[0] - 1.6, yb - 0.85, "HF secondary: 1 kV peak, 40 kHz\nall C = 10 nF, 2 kV;  10 diodes",
            fontsize=7.5, ha="left", va="top")
    ax.text(xp - 0.45, S[3][1], "pumping\ncolumn", fontsize=7.5, ha="right", va="center")
    ax.text(xs + 1.05, S[2][1] + h, "smoothing\ncolumn", fontsize=7.5, ha="left", va="center")
    ax.set_title("(b) five-stage Cockcroft–Walton", fontsize=9, weight="bold", pad=22)
    save(fig, "06", "fig-6-5-voltage-multipliers")


# ----------------------------------------------------------------------------
# Figure 6.6 — design flowchart
# ----------------------------------------------------------------------------
def fig_6_6():
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 14)
    ax.axis("off")
    ax.set_position([0, 0, 1, 1])
    fs = 7.6
    cx, w, h = 6.2, 7.0, 0.85
    seq = [
        (13.0, "Load spec: $V_{out}$, $I_{out}$, regulator dropout, ripple, $T_a$, life"),
        (11.75, "Topology: bridge / centre-tapped full-wave / half-wave"),
        (10.5, "Transformer voltage at low line (230 V − 10 %)"),
        (9.25, "Capacitor value for the ripple trough"),
        (8.0, "Simulate: $I_{pk}$, $I_{sec,rms}$, $I_{cap,rms}$, conduction angle"),
    ]
    for y, txt in seq:
        box(ax, cx - w / 2, y - h / 2, w, h, txt, fontsize=fs)
    for (y0, _), (y1, _) in zip(seq[:-1], seq[1:]):
        ax.annotate("", xy=(cx, y1 + h / 2), xytext=(cx, y0 - h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=10))
    # three parallel rating boxes
    yr, hr, wr = 5.75, 2.2, 4.0
    xr = [0.25, 5.0, 9.75]
    rt = ["Transformer:\nVA rating from\n$I_{sec,rms}$",
          "Diodes: $I_{av}$;\nloss $V_0I_{av}+r_TI_{rms}^2$;\nPIV margin ≥ 2;\n$I_{FSM}$, $I^2t$ for inrush",
          "Capacitor: voltage at\nhigh line, no load;\nripple current;\nlife by 10 K rule"]
    for x, txt in zip(xr, rt):
        box(ax, x, yr - hr / 2, wr, hr, txt, fc="#FFF6E5", ec="#B07A00", fontsize=fs)
        ax.annotate("", xy=(x + wr / 2, yr + hr / 2), xytext=(cx, seq[-1][0] - h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=10))
    seq2 = [(3.4, "Regulator dissipation at high line; heatsink"),
            (2.15, "Protection and compliance: fuse, bleeder, IEC 61000-3-2, IEC 62368-1"),
            (0.9, "Done")]
    for y, txt in seq2:
        fc = "#E3F2E1" if txt == "Done" else "#EEF3F8"
        ww = 2.4 if txt == "Done" else w + 1.6
        box(ax, cx - ww / 2, y - h / 2, ww, h, txt, fc=fc, fontsize=fs)
    for x in xr:
        ax.annotate("", xy=(cx, seq2[0][0] + h / 2), xytext=(x + wr / 2, yr - hr / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, mutation_scale=10))
    for (y0, _), (y1, _) in zip(seq2[:-1], seq2[1:]):
        ax.annotate("", xy=(cx, y1 + h / 2), xytext=(cx, y0 - h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1, mutation_scale=10))
    # iterate loop: regulator box back to transformer-voltage box
    RED = "#C62828"
    xl = 13.95
    yreg = seq2[0][0]
    x_reg_r = cx + (w + 1.6) / 2
    ax.plot([x_reg_r, xl, xl], [yreg, yreg, seq[2][0]], color=RED, lw=1.3)
    ax.annotate("", xy=(cx + w / 2, seq[2][0]), xytext=(xl, seq[2][0]),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3, mutation_scale=11))
    ax.text(xl - 0.15, seq[3][0] - 0.3, "iterate if\ntoo hot", color=RED, fontsize=fs,
            ha="right", va="center")
    save(fig, "06", "fig-6-6-rectifier-design-flow")


if __name__ == "__main__":
    fig_6_1()
    fig_6_2()
    fig_6_3()
    fig_6_4()
    fig_6_5()
    fig_6_6()
