"""Render the GitHub social preview (1280x640) to docs/social-preview.png.

    python scripts/make-social-preview.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "social-preview.png"

BG = "#0b2230"
INK = "#f2f5f9"
MUTED = "#9fb8c8"
ACCENT = ["#56B4E9", "#E69F00", "#009E73", "#CC79A7", "#F0E442"]

plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "cm"})
fig = plt.figure(figsize=(12.8, 6.4), dpi=100, facecolor=BG)

# Upper right: MOSFET output characteristics for four gate overdrives (Chapter 4).
ax = fig.add_axes([0.62, 0.55, 0.35, 0.36], facecolor=BG)
vds = np.linspace(0, 5, 400)
for vov, c in zip((0.5, 1.0, 1.5, 2.0), ACCENT):
    lin = vov * vds - vds**2 / 2
    sat = vov**2 / 2 * (1 + 0.04 * (vds - vov))
    ax.plot(vds, np.where(vds < vov, lin, sat), color=c, lw=2.4)
vb = np.linspace(0, 2.0, 100)
ax.plot(vb, vb**2 / 2, color=MUTED, lw=1.2, ls="--", alpha=0.8)
ax.text(5.1, 2.1, r"$V_{GS}$", color=MUTED, fontsize=13, va="center")
ax.set_xlim(0, 5.8)
ax.set_ylim(0, 2.6)
ax.axis("off")

# Lower right: CMOS inverter transfer characteristic under a clock waveform (Chapters 14, 33).
ax2 = fig.add_axes([0.64, 0.08, 0.31, 0.38], facecolor=BG)
vin = np.linspace(0, 1.8, 400)
ax2.plot(vin, 1.8 / (1 + np.exp((vin - 0.9) / 0.06)), color=ACCENT[0], lw=2.4)
ax2.plot(vin, vin, color=MUTED, lw=0.8, ls=":", alpha=0.8)
t = np.linspace(0, 1.8, 800)
clk = 0.15 * (np.sign(np.sin(2 * np.pi * t / 0.3)) + 1) / 2 + 2.05
ax2.plot(t, clk, color=ACCENT[1], lw=2.0)
ax2.text(1.0, 1.35, r"$P=\alpha C V_{DD}^2 f$", color=INK, fontsize=15)
ax2.set_xlim(0, 2.0)
ax2.set_ylim(-0.05, 2.35)
ax2.axis("off")

# Left panel: title block.
fig.text(0.06, 0.83, "BOOK 4  ·  EEE CORE", color=ACCENT[0], fontsize=20, weight="bold")
fig.text(0.06, 0.63, "Electronics\nand Computing", color=INK, fontsize=38, weight="bold",
         va="center", linespacing=1.12)
fig.text(0.06, 0.45, "Devices, analog and digital circuits, computer\narchitecture, programming, embedded and "
         "real-time\nsystems, power electronics and VLSI.",
         color=MUTED, fontsize=16, style="italic", va="top", linespacing=1.35)
fig.text(0.06, 0.24, r"$I_D=I_S\left(e^{V_D/nV_T}-1\right)$", color=INK, fontsize=19)
fig.text(0.06, 0.14, "8 parts · 35 chapters · 197 figures · 654-page PDF · MCP server", color=INK, fontsize=14)
fig.text(0.06, 0.07, "github.com/The-Studio-of-Sadiq/Electronics-and-Computing", color=MUTED, fontsize=12)

OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, facecolor=BG)
print(f"wrote {OUT.relative_to(ROOT)}")
