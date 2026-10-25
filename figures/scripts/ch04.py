"""Figures for Chapter 4 — Field-Effect Transistors.

Run from the repository root:  python figures/scripts/ch04.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch  # noqa: E402

from figstyle import COLORS, INK, GRID, save  # noqa: E402

BLUE, ORANGE, GREEN, PINK, AMBER, SKY = COLORS[:6]
GREY = "#888888"

# region colours for cross-sections
C_N = "#DCEBF7"      # n-type
C_NP = "#9EC5E8"     # n+
C_NM = "#EEF5FB"     # n-
C_P = "#F7E1D3"      # p-type
C_PP = "#EDB896"     # p+
C_OX = "#FFF7C2"     # oxide
C_POLY = "#B8B8B8"   # polysilicon / gate
C_MET = "#8C8C8C"    # metal
C_DEP = "#FFFFFF"    # depletion (hatched)


def rect(ax, x, y, w, h, fc, ec=INK, lw=0.8, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, **kw))


def rrect(ax, x, y, w, h, fc, r=0.12, ec=INK, lw=0.8, **kw):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, **kw))


def arr(ax, x0, y0, x1, y1, color=INK, lw=1.1, ms=9, style="-|>", **kw):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0,
                                mutation_scale=ms, **kw))


def diode_sym(ax, x, y0, y1, color=INK, size=0.16, lw=1.1):
    """Vertical diode from anode at y0 to cathode at y1 (current direction y0 -> y1)."""
    ym = (y0 + y1) / 2
    d = 1 if y1 > y0 else -1
    ax.plot([x, x], [y0, ym - d * size * 0.6], color=color, lw=lw)
    ax.plot([x, x], [ym + d * size * 0.6, y1], color=color, lw=lw)
    ax.add_patch(Polygon([(x - size, ym - d * size * 0.6), (x + size, ym - d * size * 0.6),
                          (x, ym + d * size * 0.6)], closed=True, fc=color, ec=color, lw=lw))
    ax.plot([x - size, x + size], [ym + d * size * 0.6] * 2, color=color, lw=lw * 1.3)


# ----------------------------------------------------------------------------
# Figure 4.1 — JFET structure and transfer characteristic
# ----------------------------------------------------------------------------
def fig_4_1():
    fig = plt.figure(figsize=(6.8, 3.4))
    axs = fig.add_axes([0.0, 0.03, 0.47, 0.94])
    ax = fig.add_axes([0.58, 0.15, 0.40, 0.78])

    # ---- cross-section ----
    axs.set_xlim(-0.9, 6.3)
    axs.set_ylim(-0.5, 4.6)
    axs.set_aspect("equal")
    axs.axis("off")
    x0, x1 = 0.6, 5.4          # channel between contacts
    yb, yt = 1.0, 3.0          # channel bottom / top (inside the gate regions)
    a = (yt - yb) / 2
    yc = (yb + yt) / 2
    # channel bar
    rect(axs, x0, yb, x1 - x0, yt - yb, C_N)
    # p+ gate regions
    gx0, gx1 = 1.2, 4.8
    rect(axs, gx0, yt, gx1 - gx0, 0.45, C_PP)
    rect(axs, gx0, yb - 0.45, gx1 - gx0, 0.45, C_PP)
    # depletion region widths: w(x) = a*sqrt((Vbi - VGS + V(x)) / (Vbi - VP)),
    # VGS = -1 V, VP = -2 V, Vbi = 0.7 V; V(x) from gradual channel up to pinch-off at V = 1 V
    Vbi, VGS, VP = 0.7, -1.0, -2.0
    xs = np.linspace(gx0, gx1, 200)
    xp = gx0 + 0.86 * (gx1 - gx0)            # pinch-off point
    u = np.clip((xs - gx0) / (xp - gx0), 0, 1)
    Vx = 1.0 * (1 - np.sqrt(1 - u))           # potential rises faster near pinch-off
    w = a * np.sqrt((Vbi - VGS + Vx) / (Vbi - VP))
    w = a - (a - w) * 2.2                     # exaggerate the taper for legibility
    w = np.minimum(w, a * 0.985)
    top = np.concatenate([[gx0], xs, [gx1]])
    for sgn, ybase in ((-1, yt), (1, yb)):
        pts = [(gx0, ybase)] + [(x, ybase + sgn * ww) for x, ww in zip(xs, w)] + [(gx1, ybase)]
        axs.add_patch(Polygon(pts, closed=True, fc="#F5F5F5", ec=GREY, lw=0.8, hatch="////"))
    # ohmic contacts
    rect(axs, x0 - 0.35, yb, 0.35, yt - yb, C_MET)
    rect(axs, x1, yb, 0.35, yt - yb, C_MET)
    axs.text(x0 - 0.55, yc, "S", ha="right", va="center", fontsize=11, weight="bold")
    axs.text(x1 + 0.55, yc, "D", ha="left", va="center", fontsize=11, weight="bold")
    # gate contacts tied together
    gm = (gx0 + gx1) / 2
    rect(axs, gm - 0.4, yt + 0.45, 0.8, 0.15, C_MET)
    rect(axs, gm - 0.4, yb - 0.6, 0.8, 0.15, C_MET)
    axs.plot([gm, gm, 5.95, 5.95, gm, gm], [yt + 0.6, 4.1, 4.1, -0.3, -0.3, yb - 0.6],
             color=INK, lw=1.0)
    axs.plot([5.95], [4.1], "o", ms=3, color=INK)
    axs.text(6.05, 4.1, "G", ha="left", va="center", fontsize=11, weight="bold")
    # labels
    axs.text(2.0, yc, "n channel", ha="center", va="center", fontsize=8.5)
    axs.text(1.55, yt + 0.22, "p+", ha="center", va="center", fontsize=8.5)
    axs.text(1.55, yb - 0.22, "p+", ha="center", va="center", fontsize=8.5)
    axs.text(gm - 0.5, yt + 0.52, "gate", ha="right", va="center", fontsize=8)
    axs.annotate("depletion regions", xy=(3.6, yt - 0.3), xytext=(3.75, 3.85),
                 fontsize=8, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    axs.plot([xp], [yc], "o", ms=5, color=ORANGE)
    axs.annotate("pinch-off\npoint", xy=(xp, yc), xytext=(4.0, -0.15), fontsize=8,
                 ha="center", va="center", color=ORANGE,
                 arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=0.9, mutation_scale=8))
    arr(axs, 0.25, 0.45, 1.3, 0.45, color=BLUE, lw=1.0)
    axs.text(0.25, 0.25, "electrons S→D", ha="left", va="center", fontsize=7.5, color=BLUE)
    axs.text(2.0, 4.45, r"$V_{GS}=-1$ V, $V_{DS}=3$ V", ha="center", va="center", fontsize=9)

    # ---- transfer characteristic ----
    vgs = np.linspace(-3.5, 0, 500)
    labels = []
    for (idss, vp), col in zip(((2, -1.2), (4, -2.0), (8, -3.0)), (GREEN, BLUE, ORANGE)):
        i = np.where(vgs >= vp, idss * (1 - vgs / vp) ** 2, 0.0)
        line, = ax.plot(vgs, i, color=col)
        # self-bias intersection: ID = -VGS / 1 kOhm
        R = 1.0
        A = idss * (R / vp) ** 2
        B = 2 * idss * R / vp - 1
        roots = np.roots([A, B, idss])
        idq = [r.real for r in roots if -r.real * R > vp][0]
        ax.plot(-idq * R, idq, "o", ms=5.5, color=col, mec="white", zorder=5)
        line.set_label(fr"$I_{{DSS}}={idss}$ mA, $V_P={vp}$ V: $I_D$ = {idq:.2f} mA")
    vl = np.linspace(-3.5, 0, 10)
    ax.plot(vl, -vl / 1.0, color=INK, ls="--", lw=1.2)
    ax.text(-2.82, 2.94, r"self-bias line $I_D=-V_{GS}/1\ \mathrm{k\Omega}$",
            fontsize=7.5, ha="center", va="bottom", rotation=-24.5, rotation_mode="anchor")
    ax.set_xlim(-3.5, 0)
    ax.set_ylim(0, 9)
    ax.set_xlabel(r"$V_{GS}$ (V)")
    ax.set_ylabel(r"$I_D$ (mA)")
    ax.legend(fontsize=7.3, loc="upper left", handlelength=1.2, title="dots: self-bias points",
              title_fontsize=7.3)
    ax.grid(True, lw=0.5)
    save(fig, "04", "fig-4-1-jfet-structure-transfer")


# ----------------------------------------------------------------------------
# MOSFET symbol helper (hand-drawn, so enhancement/depletion are explicit)
# ----------------------------------------------------------------------------
def mos_symbol(ax, x, y, ptype=False, depletion=False, four=False, power=False, title=""):
    lw = 1.4
    gx, cx, lx = x - 0.42, x - 0.28, x + 0.25     # gate plate, channel, leg x
    top_lbl, bot_lbl = ("S", "D") if ptype else ("D", "S")
    # gate
    ax.plot([gx, gx], [y - 0.38, y + 0.38], color=INK, lw=lw)
    gy = y - 0.3 if power else y
    ax.plot([x - 0.85, gx], [gy, gy], color=INK, lw=lw)
    ax.text(x - 0.9, gy, "G", ha="right", va="center", fontsize=8.5)
    # channel
    if depletion:
        ax.plot([cx, cx], [y - 0.45, y + 0.45], color=INK, lw=lw * 1.6)
    else:
        for a, b in ((0.22, 0.45), (-0.11, 0.11), (-0.45, -0.22)):
            ax.plot([cx, cx], [y + a, y + b], color=INK, lw=lw * 1.6)
    # drain / source legs
    ax.plot([cx, lx, lx], [y + 0.33, y + 0.33, y + 0.8], color=INK, lw=lw)
    ax.plot([cx, lx, lx], [y - 0.33, y - 0.33, y - 0.8], color=INK, lw=lw)
    tx, tha = (lx - 0.07, "right") if power else (lx + 0.07, "left")
    ax.text(tx, y + 0.8, top_lbl, ha=tha, va="top", fontsize=8.5)
    ax.text(tx, y - 0.8, bot_lbl, ha=tha, va="bottom", fontsize=8.5)
    # body line with arrow (inward for n-channel, outward for p-channel)
    if four:
        ax.plot([cx, x + 0.6], [y, y], color=INK, lw=lw)
        ax.text(x + 0.65, y, "B", ha="left", va="center", fontsize=8.5)
    else:
        src_y = y + 0.33 if ptype else y - 0.33
        ax.plot([cx, lx, lx], [y, y, src_y], color=INK, lw=lw)
    if ptype:
        arr(ax, cx + 0.04, y, cx + 0.3, y, lw=lw, ms=8)
    else:
        arr(ax, cx + 0.32, y, cx + 0.05, y, lw=lw, ms=8)
    if power:
        dx = x + 0.62
        ax.plot([lx, dx], [y + 0.62, y + 0.62], color=INK, lw=1.1)
        ax.plot([lx, dx], [y - 0.62, y - 0.62], color=INK, lw=1.1)
        for yy in (y + 0.62, y - 0.62):
            ax.plot([lx], [yy], "o", ms=2.5, color=INK)
        # body diode: anode at source, cathode at drain
        if ptype:
            diode_sym(ax, dx, y - 0.62, y + 0.62, size=0.13)   # S on top: anode at bottom (D)
        else:
            diode_sym(ax, dx, y - 0.62, y + 0.62, size=0.13)
    ax.text(x, y - 1.12, title, ha="center", va="top", fontsize=8)


def fig_4_2():
    fig = plt.figure(figsize=(6.8, 3.9))
    ax = fig.add_axes([0.0, 0.0, 0.5, 1.0])
    ax.set_xlim(-0.3, 6.6)
    ax.set_ylim(-0.3, 5.6)
    ax.set_aspect("equal")
    ax.axis("off")

    ys = 3.4                               # silicon surface
    rect(ax, 0, 0.4, 6.3, ys - 0.4, C_P)
    ax.text(3.9, 0.85, "p-type body (well)", ha="center", fontsize=8.5)
    # body contact p+
    rrect(ax, 0.25, ys - 0.45, 0.8, 0.45, C_PP, r=0.1)
    # source / drain n+
    rrect(ax, 1.5, ys - 0.7, 1.3, 0.7, C_NP, r=0.15)
    rrect(ax, 4.5, ys - 0.7, 1.3, 0.7, C_NP, r=0.15)
    # depletion around drain junction (hatched band) and under the channel
    dep = [(4.3, ys), (4.3, ys - 0.85), (4.45, ys - 0.95), (5.95, ys - 0.95), (6.05, ys - 0.85),
           (6.05, ys), (5.8, ys), (5.8, ys - 0.7), (4.5, ys - 0.7), (4.5, ys)]
    ax.add_patch(Polygon(dep, closed=True, fc="none", ec=GREY, lw=0.6, hatch="////"))
    ax.add_patch(Polygon([(2.8, ys - 0.03), (2.8, ys - 0.3), (4.5, ys - 0.38), (4.5, ys - 0.03)],
                         closed=True, fc="none", ec=GREY, lw=0.5, hatch="....", ls="--"))
    # inversion layer
    rect(ax, 2.75, ys - 0.07, 1.8, 0.07, "#1F3A5F", ec="none")
    # gate oxide (exaggerated) and gate
    rect(ax, 2.6, ys, 2.1, 0.16, C_OX)
    rect(ax, 2.6, ys + 0.16, 2.1, 0.55, C_POLY)
    # metal contacts
    for xm in (0.4, 1.85, 4.85):
        rect(ax, xm, ys, 0.5 if xm < 1 else 0.6, 0.3, C_MET)
    rect(ax, 3.35, ys + 0.71, 0.6, 0.25, C_MET)
    for lbl, xx, yy in (("B", 0.65, ys + 0.55), ("S", 2.15, ys + 0.55), ("D", 5.15, ys + 0.55),
                        ("G", 3.65, ys + 1.2)):
        ax.text(xx, yy, lbl, ha="center", va="center", fontsize=11, weight="bold")
    ax.text(0.65, ys - 0.24, "p+", ha="center", va="center", fontsize=8)
    ax.text(2.15, ys - 0.42, "n+", ha="center", va="center", fontsize=8.5)
    ax.text(5.15, ys - 0.42, "n+", ha="center", va="center", fontsize=8.5)
    ax.text(3.65, ys + 0.44, "gate", ha="center", va="center", fontsize=8)
    # oxide label
    ax.annotate(r"gate oxide, $t_{ox}=2$ nm" "\n(not to scale)", xy=(4.62, ys + 0.08),
                xytext=(5.25, 4.85), fontsize=7.5, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    # channel length
    yl = ys - 1.25
    arr(ax, 2.8, yl, 4.5, yl, style="<|-|>", lw=0.9, ms=8)
    ax.text(3.65, yl - 0.08, r"$L$", ha="center", va="top", fontsize=10)
    for xx in (2.8, 4.5):
        ax.plot([xx, xx], [yl - 0.08, ys - 0.72], color=GREY, lw=0.6, ls=":")
    ax.annotate(r"inversion layer ($V_{GS}>V_{th}$)", xy=(3.2, ys - 0.05), xytext=(2.3, 1.55),
                fontsize=7.5, ha="center", color="#1F3A5F",
                arrowprops=dict(arrowstyle="-", color="#1F3A5F", lw=0.7))
    ax.annotate("drain depletion\nregion", xy=(5.95, ys - 0.85), xytext=(6.4, 1.6),
                fontsize=7.5, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.7))
    ax.text(3.15, 5.4, "Planar n-channel MOSFET", ha="center", fontsize=9.5, weight="bold")

    # ---- symbol grid ----
    sx = fig.add_axes([0.5, 0.0, 0.5, 1.0])
    sx.set_xlim(0, 6.2)
    sx.set_ylim(-0.3, 5.6)
    sx.set_aspect("equal")
    sx.axis("off")
    sx.text(3.1, 5.4, "Circuit symbols", ha="center", fontsize=9.5, weight="bold")
    xs = (1.0, 3.1, 5.2)
    y1, y2 = 4.0, 1.25
    mos_symbol(sx, xs[0], y1, title="NMOS enhancement")
    mos_symbol(sx, xs[1], y1, depletion=True, title="NMOS depletion")
    mos_symbol(sx, xs[2], y1, ptype=True, title="PMOS enhancement")
    mos_symbol(sx, xs[0], y2, four=True, title="NMOS, 4-terminal")
    mos_symbol(sx, xs[1], y2, power=True, title="n-ch power MOSFET\n(body diode)")
    mos_symbol(sx, xs[2], y2, ptype=True, power=True, title="p-ch power MOSFET\n(body diode)")
    save(fig, "04", "fig-4-2-mosfet-structure-symbols")


# ----------------------------------------------------------------------------
# Figure 4.3 — output characteristics and regions
# ----------------------------------------------------------------------------
def id_square(vds, vgs, k=1.0, vth=0.7, lam=0.05):
    vov = vgs - vth
    tri = k * (vov * vds - vds ** 2 / 2) * (1 + lam * vds)
    sat = 0.5 * k * vov ** 2 * (1 + lam * vds)
    return np.where(vds < vov, tri, sat)


def id_vsat(vds, vgs, k=1.0, vth=0.7, lam=0.05, vc=1.0):
    """Velocity-saturated model: mobility reduced by (1 + VDS/Vc), Vc = Esat*L."""
    vov = vgs - vth
    vdsat = vov * vc / (vov + vc)
    v = np.minimum(vds, vdsat)
    return k * (vov * v - v ** 2 / 2) / (1 + v / vc) * (1 + lam * vds)


def fig_4_3():
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    vds = np.linspace(0, 3, 600)
    # triode shading: left of / above the boundary parabola VDS = Vov
    bound = 0.5 * vds ** 2 * (1 + 0.05 * vds)
    ax.fill_between(vds, bound, 2.5, color="#E8F1FA", lw=0)
    ax.plot(vds, bound, ls=":", color=INK, lw=1.4)
    cols = (GREEN, BLUE, ORANGE)
    for vgs, col in zip((1.5, 2.0, 2.5), cols):
        ax.plot(vds, id_square(vds, vgs), color=col)
        ax.plot(vds, id_vsat(vds, vgs), color=col, ls="--", lw=1.5)
        ax.text(3.03, id_square(3.0, vgs), fr"$V_{{GS}}={vgs}$ V", color=col, fontsize=8.5,
                va="center", ha="left")
    # small-VDS slope for VGS = 2.5 V
    s = 1.0 * 1.8
    xx = np.linspace(0, 0.75, 10)
    ax.plot(xx, s * xx, color=INK, lw=0.9, ls="-.")
    ax.annotate(r"slope $=1/R_{DS(on)}$" "\n" r"($\approx556\ \Omega$ at $V_{GS}=2.5$ V)",
                xy=(0.62, s * 0.62), xytext=(0.95, 2.2), fontsize=8, va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.text(0.2, 1.75, "triode", fontsize=9.5, color="#2A5D8F", ha="left", style="italic")
    ax.text(2.45, 1.3, "saturation", fontsize=9.5, color=INK, ha="center", style="italic")
    ax.annotate(r"boundary $V_{DS}=V_{GS}-V_{th}$", xy=(1.65, 0.5 * 1.65 ** 2 * 1.0825),
                xytext=(1.85, 1.95), fontsize=8, ha="left",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
    ax.fill_between(vds, 0, 0.035, color="#DDDDDD", lw=0)
    ax.text(1.55, 0.06, r"$V_{GS}<V_{th}=0.7$ V: cut-off / subthreshold ($I_D\approx0$)",
            fontsize=7.8, ha="left", va="bottom", color="#555555")
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=INK, label=r"square law, $k'W/L=1\ \mathrm{mA/V^2}$, $\lambda=0.05\ \mathrm{V^{-1}}$"),
         Line2D([], [], color=INK, ls="--", lw=1.5, label="velocity-saturated ($E_{sat}L=1$ V)")]
    ax.legend(handles=h, loc="upper left", fontsize=7.8, bbox_to_anchor=(0.0, 1.07))
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 2.5)
    ax.set_xlabel(r"$V_{DS}$ (V)")
    ax.set_ylabel(r"$I_D$ (mA)")
    save(fig, "04", "fig-4-3-mosfet-output-regions")


# ----------------------------------------------------------------------------
# Figure 4.4 — bias spread
# ----------------------------------------------------------------------------
def fig_4_4():
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    K = 0.1
    v = np.linspace(0, 6, 1200)
    cols = (GREEN, BLUE, ORANGE)
    names = ("min", "typ", "max")
    for vth, col, nm in zip((0.8, 2.1, 3.0), cols, names):
        i = np.where(v > vth, K * (v - vth) ** 2, 0) * 1e3
        m = i <= 8.0
        ax.plot(v[m], i[m], color=col, label=fr"$V_{{th}}={vth}$ V ({nm})")
        # degenerated bias point: 6 - Vth = Vov + K*R*Vov^2
        vov = (-1 + np.sqrt(1 + 4 * K * 1e3 * (6 - vth))) / (2 * K * 1e3)
        idq = K * vov ** 2 * 1e3
        ax.plot(vth + vov, idq, "o", ms=6, color=col, mec="white", zorder=5)
        off = {0.8: (0.35, 0.55), 2.1: (-0.95, -0.85), 3.0: (0.35, -1.3)}[vth]
        ax.annotate(f"{idq:.2f} mA", xy=(vth + vov, idq),
                    xytext=(vth + vov + off[0], idq + off[1]), fontsize=8.5, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.7))
    ax.plot([0, 6], [6, 0], color=INK, lw=1.4)
    ax.text(4.62, 1.72, r"bias line $I_D=(6\ \mathrm{V}-V_{GS})/1\ \mathrm{k\Omega}$",
            rotation=-45, transform_rotates_text=True, fontsize=8.5, ha="center", va="bottom", rotation_mode="anchor")
    # fixed bias at 2.5 V
    ax.axvline(2.5, color=PINK, ls="--", lw=1.3)
    arr(ax, 2.5, 7.0, 2.5, 7.95, color=GREEN, lw=1.3)
    arr(ax, 2.5, 6.2, 2.5, 7.0, color=BLUE, lw=1.3)
    ax.text(2.5, 8.12, "off scale at 2.5 V:", color=INK, fontsize=7.8, ha="right", va="bottom")
    ax.text(2.55, 8.12, "289 mA", color=GREEN, fontsize=7.8, ha="left", va="bottom")
    ax.text(3.2, 8.12, "and", color=INK, fontsize=7.8, ha="left", va="bottom")
    ax.text(3.52, 8.12, "16 mA", color=BLUE, fontsize=7.8, ha="left", va="bottom")
    ax.plot(2.5, 0, "s", ms=6, color=ORANGE, clip_on=False, zorder=6)
    ax.text(2.58, 0.22, "0 mA", color=ORANGE, fontsize=7.8, ha="left")
    ax.text(3.75, 3.9, "fixed bias " r"$V_{GS}=2.5$ V:" "\n" r"$I_D$ = 0 to 289 mA",
            color=PINK, fontsize=8.5, ha="left", va="center")
    ax.text(3.75, 4.9, "degenerated ($R_S$ = 1 kΩ):\n" r"$I_D$ = 2.83 to 4.98 mA",
            fontsize=8.5, color=INK, ha="left", va="center")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 8)
    ax.set_xlabel(r"$V_{GS}$ (V)")
    ax.set_ylabel(r"$I_D$ (mA)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, lw=0.5)
    save(fig, "04", "fig-4-4-bias-spread")


# ----------------------------------------------------------------------------
# Figure 4.5 — gate charge and switching waveforms
# ----------------------------------------------------------------------------
def fig_4_5():
    Qgs, Qgd, Qg = 1.5, 2.0, 12.0
    Vth, Vpl, Vdr = 1.5, 2.2, 3.3
    fig = plt.figure(figsize=(6.8, 4.0))
    ax = fig.add_axes([0.08, 0.13, 0.36, 0.8])
    q = [0, Qgs, Qgs + Qgd, Qg]
    vg = [0, Vpl, Vpl, 10]
    ax.plot(q, vg, color=BLUE)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10.5)
    ax.set_xlabel(r"gate charge $Q_g$ (nC)")
    ax.set_ylabel(r"$V_{GS}$ (V)")
    ax.grid(True, lw=0.5)
    qth = Qgs * Vth / Vpl
    ax.plot(qth, Vth, "o", ms=4, color=INK)
    ax.annotate(r"$V_{th}=1.5$ V", xy=(qth, Vth), xytext=(1.3, 0.55), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    ax.annotate(r"plateau 2.2 V", xy=(2.5, Vpl), xytext=(0.3, 4.6), fontsize=8,
                arrowprops=dict(arrowstyle="-", lw=0.6))
    slope = (10 - Vpl) / (Qg - Qgs - Qgd)
    q33 = Qgs + Qgd + (Vdr - Vpl) / slope
    ax.axhline(Vdr, color=ORANGE, ls="--", lw=1.0)
    ax.plot(q33, Vdr, "o", ms=5, color=ORANGE)
    ax.text(q33 + 0.3, Vdr - 0.15, f"3.3 V drive reached\nat {q33:.1f} nC", color=ORANGE,
            fontsize=7.8, va="top")
    # brackets
    yb = 7.6
    for a, b, t in ((0, Qgs, r"$Q_{gs}$"), (Qgs, Qgs + Qgd, r"$Q_{gd}$")):
        arr(ax, a, yb, b, yb, style="<|-|>", lw=0.8, ms=6)
        ax.text((a + b) / 2, yb + 0.2, t, ha="center", va="bottom", fontsize=8.5)
    for xx in (Qgs, Qgs + Qgd):
        ax.plot([xx, xx], [Vpl, yb + 0.2], color=GREY, lw=0.6, ls=":")
    ax.text(11.8, 10.15, r"$Q_g=12$ nC at 10 V", ha="right", va="top", fontsize=8)
    ax.set_title("Gate-charge curve", fontsize=10)

    # ---- time domain ----
    R = 72.0
    C1 = Qgs / Vpl * 1e-9
    C3 = 1 / slope * 1e-9
    tau1, tau3 = R * C1, R * C3
    t1 = tau1 * np.log(Vdr / (Vdr - Vpl))
    ig = (Vdr - Vpl) / R
    tpl = Qgd * 1e-9 / ig
    t2 = t1 + tpl
    t = np.linspace(0, 300e-9, 3000)
    vgs = np.where(t < t1, Vdr * (1 - np.exp(-t / tau1)),
                   np.where(t < t2, Vpl, Vdr - (Vdr - Vpl) * np.exp(-(t - t2) / tau3)))
    Kk = 5.0 / (Vpl - Vth) ** 2
    idr = np.where(t < t1, np.where(vgs > Vth, Kk * (vgs - Vth) ** 2, 0), 5.0)
    vds = np.where(t < t1, 12.0, np.where(t < t2, 12.0 - (12.0 - 0.1) * (t - t1) / tpl, 0.1))
    tn = t * 1e9
    tth = tau1 * np.log(Vdr / (Vdr - Vth)) * 1e9

    a1 = fig.add_axes([0.56, 0.58, 0.36, 0.35])
    a2 = fig.add_axes([0.56, 0.13, 0.36, 0.38], sharex=a1)
    for a in (a1, a2):
        a.axvspan(tth, t2 * 1e9, color="#FCE4D6", lw=0)
        a.grid(True, lw=0.5)
    a1.plot(tn, vgs, color=BLUE)
    a1.set_ylabel(r"$v_{GS}$ (V)")
    a1.set_ylim(0, 3.8)
    a1.axhline(Vdr, color=ORANGE, ls="--", lw=0.9)
    a1.text(296, 3.42, "3.3 V", color=ORANGE, fontsize=7.5, ha="right", va="bottom")
    arr(a1, t1 * 1e9, 1.6, t2 * 1e9, 1.6, style="<|-|>", lw=0.8, ms=6)
    a1.text((t1 + t2) / 2 * 1e9, 1.25, f"plateau {tpl * 1e9:.0f} ns", ha="center", fontsize=8)
    plt.setp(a1.get_xticklabels(), visible=False)
    a1.set_title("Turn-on from a 3.3 V pin (72 Ω)", fontsize=10)
    a2.plot(tn, vds, color=ORANGE, label=r"$v_{DS}$")
    a2.set_ylabel(r"$v_{DS}$ (V)", color=ORANGE)
    a2.set_ylim(0, 14)
    a2.set_xlabel("time (ns)")
    a2.set_xlim(0, 300)
    a3 = a2.twinx()
    a3.spines["right"].set_visible(True)
    a3.plot(tn, idr, color=GREEN, label=r"$i_D$")
    a3.set_ylabel(r"$i_D$ (A)", color=GREEN)
    a3.set_ylim(0, 7)
    a2.text(tn[50] + 2, 12.4, r"$v_{DS}$", color=ORANGE, fontsize=9)
    a3.text(150, 5.25, r"$i_D=5$ A", color=GREEN, fontsize=9, ha="center")
    a2.text((tth + t2 * 1e9) / 2 + 30, 3.0, "switching-loss\ninterval", fontsize=7.8,
            ha="center", color="#A0522D")
    save(fig, "04", "fig-4-5-gate-charge-switching")


# ----------------------------------------------------------------------------
# Figure 4.6 — power MOSFET structures
# ----------------------------------------------------------------------------
def _layers(ax, x0, w, y_drift_top, label_drift=True):
    rect(ax, x0, 0.0, w, 0.18, C_MET)                    # drain metal
    rect(ax, x0, 0.18, w, 0.55, C_NP)                    # n+ substrate
    rect(ax, x0, 0.73, w, y_drift_top - 0.73, C_NM)      # n- drift
    ax.text(x0 + w / 2, 0.45, "n+ substrate", ha="center", va="center", fontsize=7.2)
    ax.text(x0 + w / 2, 0.09, "drain", ha="center", va="center", fontsize=7, color="white")


def zigzag(ax, x, y0, y1, n=5, amp=0.1, lw=1.1):
    ys = np.linspace(y0, y1, 2 * n + 1)
    lead = (y1 - y0) * 0.15
    ys = np.linspace(y0 + lead, y1 - lead, 2 * n + 1)
    xs = [x] + [x + (amp if k % 2 else -amp) for k in range(1, 2 * n)] + [x]
    ax.plot([x, x], [y0, y0 + lead], color=INK, lw=lw)
    ax.plot(xs, ys, color=INK, lw=lw)
    ax.plot([x, x], [y1 - lead, y1], color=INK, lw=lw)


def planar_top(ax, x0, w, ys):
    """Planar DMOS surface: p-bodies at both cell edges, n+ sources, gate over the neck."""
    cell = Rectangle((x0, 0), w, ys, transform=ax.transData)
    pb = 0.85     # p-body lateral extent from each edge
    for patch in (
            FancyBboxPatch((x0 - 0.4, ys - 0.8), pb + 0.4, 1.1,
                           boxstyle="round,pad=0,rounding_size=0.22", fc=C_P, ec=INK, lw=0.8),
            FancyBboxPatch((x0 + w - pb, ys - 0.8), pb + 0.4, 1.1,
                           boxstyle="round,pad=0,rounding_size=0.22", fc=C_P, ec=INK, lw=0.8),
            FancyBboxPatch((x0 + 0.2, ys - 0.3), 0.42, 0.6,
                           boxstyle="round,pad=0,rounding_size=0.08", fc=C_NP, ec=INK, lw=0.8),
            FancyBboxPatch((x0 + w - 0.62, ys - 0.3), 0.42, 0.6,
                           boxstyle="round,pad=0,rounding_size=0.08", fc=C_NP, ec=INK, lw=0.8)):
        ax.add_patch(patch)
        patch.set_clip_path(cell)
    # gate oxide + poly + cap oxide
    gx0, gx1 = x0 + 0.45, x0 + w - 0.45
    rect(ax, gx0, ys, gx1 - gx0, 0.06, C_OX)
    rect(ax, gx0, ys + 0.06, gx1 - gx0, 0.3, C_POLY)
    rect(ax, gx0 - 0.08, ys + 0.36, gx1 - gx0 + 0.16, 0.14, C_OX)
    ax.plot([gx0 - 0.08, gx0 - 0.08], [ys, ys + 0.36], color=INK, lw=0.6)
    ax.plot([gx1 + 0.08, gx1 + 0.08], [ys, ys + 0.36], color=INK, lw=0.6)
    # source metal
    pts = [(x0, ys), (gx0 - 0.08, ys), (gx0 - 0.08, ys + 0.5), (gx1 + 0.08, ys + 0.5),
           (gx1 + 0.08, ys), (x0 + w, ys), (x0 + w, ys + 0.72), (x0, ys + 0.72)]
    ax.add_patch(Polygon(pts, closed=True, fc=C_MET, ec=INK, lw=0.8))
    ax.text(x0 + w / 2, ys + 0.62, "source metal", ha="center", va="center", fontsize=6.8,
            color="white")
    ax.text(x0 + w / 2, ys + 0.21, "poly gate", ha="center", va="center", fontsize=6.6)
    # surface channels (between n+ edge and p-body edge)
    for cx0 in (x0 + 0.62, x0 + w - pb):
        rect(ax, cx0, ys - 0.05, pb - 0.62, 0.05, "#1F3A5F", ec="none")
    return gx0, gx1


def planar_current(ax, x0, w, ys, yend, dx=0.32):
    for sgn in (1, -1):
        xs0 = x0 + (0.62 if sgn > 0 else w - 0.62)
        xm = x0 + w / 2 - sgn * dx
        ax.plot([xs0, xm], [ys - 0.1, ys - 0.1], color=ORANGE, lw=1.3)
        arr(ax, xm, ys - 0.1, xm, yend, color=ORANGE, lw=1.3, ms=9)


def fig_4_6():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.set_xlim(-1.75, 11.0)
    ax.set_ylim(-0.75, 5.5)
    ax.set_aspect("equal")
    ax.axis("off")
    W = 2.9

    # ---------------- (a) planar DMOS ----------------
    xa = 0.4
    ysa = 3.6
    _layers(ax, xa, W, ysa)
    gx0, gx1 = planar_top(ax, xa, W, ysa)
    planar_current(ax, xa, W, ysa, 1.85)
    ax.text(xa + W / 2, 1.3, "thick n− drift\n(600 V class)", ha="center", va="center", fontsize=7.2)
    ax.text(xa + 0.06, ysa - 0.62, "p-body", ha="left", va="center", fontsize=6.3)
    ax.text(xa + W / 2, ysa - 0.55, "JFET\nregion", ha="center", va="center", fontsize=6.2)
    ax.annotate("channel", xy=(xa + 0.74, ysa - 0.03), xytext=(xa - 0.1, ysa + 0.95),
                fontsize=6.6, ha="center", va="bottom", color="#1F3A5F",
                arrowprops=dict(arrowstyle="-", color="#1F3A5F", lw=0.7))
    # parasitic body diode (left p-body to drift) and NPN (right)
    diode_sym(ax, xa + 0.3, ysa - 0.72, ysa - 1.35, color=PINK, size=0.1, lw=1.0)
    ax.text(xa + 0.06, ysa - 1.45, "body\ndiode", ha="left", va="top", fontsize=6.3, color=PINK)
    bx = xa + W - 0.3
    ax.plot([bx - 0.1, bx - 0.1], [ysa - 0.72, ysa - 0.42], color=PINK, lw=1.3)   # base bar
    ax.plot([bx - 0.1, bx + 0.05], [ysa - 0.62, ysa - 0.95], color=PINK, lw=1.0)  # collector
    ax.plot([bx + 0.05, bx + 0.05], [ysa - 0.95, ysa - 1.3], color=PINK, lw=1.0)
    arr(ax, bx - 0.1, ysa - 0.52, bx + 0.02, ysa - 0.25, color=PINK, lw=1.0, ms=6)  # emitter
    ax.text(xa + W - 0.06, ysa - 1.4, "parasitic\nNPN", ha="right", va="top", fontsize=6.3,
            color=PINK)
    ax.text(xa + W / 2, -0.3, "(a) planar DMOS", ha="center", va="top", fontsize=8.5, weight="bold")

    # resistor stack beside (a)
    rx = -0.9
    nodes = np.linspace(ysa + 0.6, 0.1, 6)
    names = (r"$R_{source}$", r"$R_{ch}$", r"$R_{JFET}$", r"$R_{drift}$", r"$R_{sub}$")
    for k, nm in enumerate(names):
        zigzag(ax, rx, nodes[k], nodes[k + 1], n=3, amp=0.09)
        ax.text(rx - 0.16, (nodes[k] + nodes[k + 1]) / 2, nm, ha="right", va="center", fontsize=7.3)
    ax.text(rx, nodes[0] + 0.1, "S", ha="center", va="bottom", fontsize=9, weight="bold")
    ax.text(rx, nodes[-1] - 0.1, "D", ha="center", va="top", fontsize=9, weight="bold")
    ax.text(-1.7, 5.45, r"$R_{drift}$ dominates at 600 V;" "\n" r"$R_{ch}$ dominates at 30 V",
            ha="left", va="top", fontsize=7.2,
            bbox=dict(fc="white", ec=GREY, lw=0.6, boxstyle="round,pad=0.25"))

    # ---------------- (b) trench ----------------
    xb = xa + W + 0.7
    ysb = 3.6
    ytb = 2.6           # thinner drift top
    _layers(ax, xb, W, ytb)
    rect(ax, xb, ytb, W, ysb - ytb, C_P)        # p-body across the cell
    tx0, tx1 = xb + W / 2 - 0.32, xb + W / 2 + 0.32
    ttop, tbot = ysb, 2.15
    rect(ax, tx0, tbot, tx1 - tx0, ttop - tbot, C_OX)
    rect(ax, tx0 + 0.07, tbot + 0.07, tx1 - tx0 - 0.14, ttop - tbot - 0.07, C_POLY)
    rrect(ax, tx0 - 0.42, ysb - 0.3, 0.42, 0.3, C_NP, r=0.06)
    rrect(ax, tx1, ysb - 0.3, 0.42, 0.3, C_NP, r=0.06)
    rect(ax, tx0 - 0.06, ysb, tx1 - tx0 + 0.12, 0.22, C_OX)
    pts = [(xb, ysb), (tx0 - 0.06, ysb), (tx0 - 0.06, ysb + 0.22), (tx1 + 0.06, ysb + 0.22),
           (tx1 + 0.06, ysb), (xb + W, ysb), (xb + W, ysb + 0.72), (xb, ysb + 0.72)]
    ax.add_patch(Polygon(pts, closed=True, fc=C_MET, ec=INK, lw=0.8))
    ax.text(xb + W / 2, ysb + 0.5, "source metal", ha="center", va="center", fontsize=6.8,
            color="white")
    for cxx in (tx0 - 0.05, tx1):
        rect(ax, cxx, ytb, 0.05, ysb - 0.3 - ytb, "#1F3A5F", ec="none")
    ax.text(xb + 0.4, ysb - 0.62, "p-body", ha="center", va="center", fontsize=6.6)
    ax.text(xb + W / 2, 2.9, "gate", ha="center", va="center", fontsize=6.4, rotation=90)
    ax.text(xb + W / 2, 1.45, "thinner n− drift\n(low-voltage class)", ha="center", va="center",
            fontsize=7.2)
    for xx in (tx0 - 0.17, tx1 + 0.17):
        arr(ax, xx, ysb - 0.15, xx, 1.9, color=ORANGE, lw=1.3, ms=9)
    ax.annotate("vertical channel\nalong trench wall", xy=(tx1 + 0.03, 2.9), xytext=(xb + W + 0.05, 4.75),
                fontsize=6.8, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color="#1F3A5F", lw=0.7))
    ax.text(xb + W / 2, 0.97, "no JFET region", ha="center", fontsize=7, style="italic")
    ax.text(xb + W / 2, -0.35, "(b) trench MOSFET", ha="center", va="top", fontsize=8.5,
            weight="bold")

    # ---------------- (c) superjunction ----------------
    xc = xb + W + 0.7
    ysc = 3.6
    _layers(ax, xc, W, ysc)
    # p pillars under the p-bodies (cell edges), n pillar in the centre
    pw = 0.62
    rect(ax, xc, 0.95, pw, ysc - 0.95, "#F3CDB4", lw=0.6)
    rect(ax, xc + W - pw, 0.95, pw, ysc - 0.95, "#F3CDB4", lw=0.6)
    rect(ax, xc + pw, 0.73, W - 2 * pw, ysc - 0.73, "#C9DFF2", lw=0.6)
    planar_top(ax, xc, W, ysc)
    ax.text(xc + pw / 2, 1.7, "p\npillar", ha="center", va="center", fontsize=6.8)
    ax.text(xc + W - pw / 2, 1.7, "p\npillar", ha="center", va="center", fontsize=6.8)
    ax.text(xc + W / 2, 1.85, "n pillar\n(10× doping)", ha="center", va="center", fontsize=6.8)
    arr(ax, xc + pw + 0.05, 1.15, xc + W - pw - 0.05, 1.15, style="<|-|>", color=GREEN, lw=0.9, ms=6)
    ax.text(xc + W / 2, 0.8, "charge balance", ha="center", va="bottom", fontsize=6.6, color=GREEN)
    planar_current(ax, xc, W, ysc, 2.35, dx=0.3)
    ax.text(xc + W / 2, -0.35, "(c) superjunction", ha="center", va="top", fontsize=8.5,
            weight="bold")

    # legend of regions
    items = ((C_NP, "n+"), (C_NM, "n−"), (C_P, "p"), (C_OX, "oxide"), (C_POLY, "poly"),
             (C_MET, "metal"))
    for k, (c, t) in enumerate(items):
        xx = 2.6 + k * 1.3
        rect(ax, xx, 5.2, 0.28, 0.2, c, lw=0.6)
        ax.text(xx + 0.36, 5.3, t, va="center", fontsize=7.2)
    arr(ax, 2.0 + 6 * 1.3 + 0.75, 5.3, 2.0 + 6 * 1.3 + 1.2, 5.3, color=ORANGE, lw=1.3, ms=8)
    ax.text(2.0 + 6 * 1.3 + 1.28, 5.3, "electron\ncurrent", va="center", fontsize=6.8)
    save(fig, "04", "fig-4-6-power-mosfet-structures")


if __name__ == "__main__":
    fig_4_1()
    fig_4_2()
    fig_4_3()
    fig_4_4()
    fig_4_5()
    fig_4_6()
