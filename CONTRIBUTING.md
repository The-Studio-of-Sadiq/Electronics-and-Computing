# Contributing — Electronics and Computing

Corrections, clearer explanations, better figures and new worked examples are welcome. Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## How to contribute

- **Found an error?** Open an [Erratum](../../issues/new?template=erratum.yml) issue with the section number (e.g. §7.5), what the book says and what it should say, with a derivation, a simulation or a numerical check.
- **A figure is wrong or unclear?** Open a [Figure](../../issues/new?template=figure.yml) issue, or fix `figures/scripts/chNN.py` and send a pull request.
- **Build, figure-script or MCP-server problem?** Open a [Tooling bug](../../issues/new?template=tooling-bug.yml).
- **Bigger change** (a new section, a rewrite, a new worked example)? Open a [Proposal](../../issues/new?template=proposal.yml) first so the scope can be agreed.

## Pull requests

1. One topic per pull request: a fix, a figure, a section.
2. Follow the house style below; every number you add must be checked (e.g. with Python), and every code listing must compile or run as shown.
3. Run the checks locally before pushing (CI runs the same ones):

```bash
npm ci
```

```bash
npm run check
```

```bash
python scripts/build-figures.py ch07
```

4. Changed a figure? Commit the script and the regenerated PNG together. Added a figure marker? Draw it, run `node scripts/insert-figures.mjs` and `npm run figures:plan`.
5. Leave `pdf/` alone; the PDF is rebuilt and attached to each release by the release workflow.

By contributing you agree that your contribution is licensed under the repository's [MIT License](LICENSE).

---

# House Style

The master outline is [`TOC.md`](TOC.md). It is fixed: 8 parts, 35 chapters. Do not skip, merge or rename listed topics; every bullet in the TOC must be covered by a section or subsection of its chapter.

## Files

- Each part is a folder `part-N-<slug>/`. Its `README.md` is the part opener; `NN-<slug>.md` (NN two digits, global chapter number) is a chapter. The exact file names are listed in the TOC.
- Markdown only. Math is GitHub-style LaTeX: `$...$` inline, `$$...$$` display (display math on its own lines). Never `\(...\)` or `\[...\]`.
- In tables, never put a raw `|` inside math; use `\lvert ... \rvert` or `\Vert`. Outside math, write the logical OR of code as `||` only inside code spans or fenced blocks, never in a table cell.
- Use `\mathrm{}` for units in math, e.g. `$g_m=40\ \mathrm{mS}$`, `$t_{pd}=85\ \mathrm{ps}$`. Prefer plain text units outside math.
- Use $j=\sqrt{-1}$ (engineering convention). Small-signal quantities are lower case with lower-case subscripts ($v_{be}$, $i_c$), DC quantities upper case ($V_{BE}$, $I_C$), total quantities lower case with upper-case subscripts ($v_{BE}$), as in standard device texts. Logic: $\overline{A}$ for NOT, $A\cdot B$ or $AB$ for AND, $A+B$ for OR, $A\oplus B$ for XOR.
- **No exercises, problems, quizzes or answer sections.** Worked examples inside the text are welcome.

## Code listings

Chapters 11–35 use code freely: C and C++ (Ch. 17, 21, 25–28), Python (Ch. 22–24 and wherever a computation is shown), Verilog/SystemVerilog and VHDL (Ch. 15, 18, 19, 34, 35), assembly where it clarifies execution (Ch. 16–17).

- Fenced blocks with a language tag: ` ```c `, ` ```cpp `, ` ```python `, ` ```verilog `, ` ```systemverilog `, ` ```vhdl `, ` ```asm `, ` ```text `.
- Short and complete: a listing shows one idea in at most ~40 lines; elide with a comment, never with code that would not compile.
- Correct: Python listings must run as shown (run them). C, C++ and HDL listings must be syntactically valid for the stated standard (C11/C17, C++17, Verilog-2001/SystemVerilog-2017, VHDL-2008); where a target is named (an Arm Cortex-M4, an AVR, an FPGA family) register names and widths must be plausible for it and marked as illustrative when not a vendor's exact header.
- Code is explained in prose, not by comment walls.

## Chapter layout

```
# Chapter N — Title

*Part X · Part title*

Opening paragraph that starts from an engineering problem (an amplifier that oscillates when a cable is connected, a counter that skips states on a fast clock, a sensor driver that hangs once a week, a buck converter that runs hot at light load).

> **Question 1?**
> **Question 2?**

| Concept | Engineering destination |
|---|---|
| ... | ... |

**Roadmap.** Short arrow-chain through the sections (N.1 → N.2–N.3 → ...).

---

## N.1 Section title
...
---
## N.2 ...
...
## What remains open

| Open question | Where it is answered |
|---|---|

**Next:** one sentence pointing to the next chapter.
```

Use `### ` subsections freely inside sections. Separate `## ` sections with `---`.

## Voice and method

1. **Start from the engineering problem**, not a definition: a phone charger's bridge rectifier that fails at turn-on, a sensor front end that drifts with temperature, an audio stage that clips asymmetrically, a state machine that locks up after reset, a cache miss that doubles a control loop's execution time, an I²C bus that hangs when a sensor browns out, a motor inverter whose IGBTs fail from overshoot, a chip that misses timing at the slow corner. Draw examples from across the field: consumer devices, instrumentation, automotive and EV electronics, industrial control, data centres and servers, telecom, medical devices, aerospace, robotics, renewable and power systems.
2. **Model → analysis → consequence.** Every method is introduced as a model with stated assumptions, solved with the right mathematics or code, and taken to a measurable consequence on real hardware or software (a gain, a bandwidth, a ripple voltage, a timing slack, a cycle count, a latency, a power dissipation, a junction temperature).
3. **Every concept gets an engineering destination.** The opening table maps concepts to where an engineer uses them.
4. **Status box after every important law, theorem or rule**, using exactly one of four labels:
   - **Fundamental** — follows from physical law or from the definition of the system (charge conservation behind KCL in a circuit, the Boltzmann factor behind the diode law's exponential, Boolean algebra as the algebra of two-valued logic).
   - **Derived** — a mathematical consequence of more basic results (the small-signal hybrid-π model from the large-signal law, the closed-loop gain formula, De Morgan's laws, two's-complement arithmetic, Amdahl's law, the buck converter's $V_o=DV_{in}$ by volt-second balance, rate-monotonic utilisation bounds, CMOS dynamic power $\alpha C V^2 f$).
   - **Approximate** — valid under stated simplifying assumptions (the ideal op-amp, the constant-drop diode model, square-law MOSFET, the Miller approximation, the single-pole op-amp model, the lumped-RC wire delay, the ripple formulas with linear inductor current). State the assumptions and the domain.
   - **Empirical** — fitted to observation (Moore's law and Dennard scaling as trends, the 10 °C rule for electrolytic-capacitor life, Arrhenius-type device reliability, Rent's rule, the 90/10 rule of program hot spots, cache miss-rate curves versus size).

   Format:
   ```
   > **Status of the principle: Name**
   > *Derived.* One sentence on why and where it holds.
   ```
5. **Show why an abstraction works, then where it fails.** The ideal op-amp fails at high frequency and near the rails; the digital abstraction fails at metastability and with ringing; the instruction-set model fails when caches and pipelines matter; the RTOS priority model fails under priority inversion; the averaged converter model fails near the switching frequency. A failure is missing physics or a changed regime, never an arbitrary exception.
6. **Real numbers.** Give representative values (with units) in tables: diode drops and leakage currents, transistor $\beta$, $V_T$, $g_m$, $f_T$ and $R_{DS(on)}$, op-amp GBW, slew rate and offset, logic-family thresholds and propagation delays, cache sizes and latencies, DRAM timings, bus speeds, microcontroller currents in each power mode, interrupt latencies, switching energies of Si, SiC and GaN devices, CMOS node parameters. Values must be correct to typical datasheet or handbook accuracy; say "typical" or give ranges where they vary, name real part classes where useful (a 1N4148, a 2N3904, a TL072, a Cortex-M4 at 168 MHz, a 1200 V SiC MOSFET) and name the standard (IEEE 754, IEC 61000, USB 2.0, ISO 11898, IEC 60747, JEDEC) when a limit comes from one. Recompute every worked example.
7. **Worked examples** as `**Worked example — title.**` paragraphs with full numbers (or a short listing and its measured or computed result).
8. **Respect the boundaries** (see the table at the end of `TOC.md`). Recap a result from a sibling book in a sentence or short paragraph and use it; never re-derive it. Add a short `> **Boundary.**` note where a chapter leans on another book, with a link to the exact chapter (see below).
9. Do not overclaim. State domains of validity.

## Cross-references to the sibling books

When a chapter uses physics, mathematics, materials, circuit theory or energy-system material owned by another book, cite the exact chapter and section with a link. Link targets:

- *Engineering Physics: Top Down* — `https://github.com/The-Studio-of-Sadiq/Engineering-Physics/blob/main/CHAPTERS/CHAPTER%20N.md`, cited as *Engineering Physics*, Ch. N §N.k.
- *Circuits, Signals and Communications* (Book 3) — `https://github.com/The-Studio-of-Sadiq/Circuits-Signals-and-Communications/blob/main/<part folder>/<NN-slug>.md`, cited as *Circuits, Signals and Communications*, Ch. N.
- *Electrical Energy and Machines* (Book 5) — `https://github.com/The-Studio-of-Sadiq/Electrical-Energy-and-Machines/blob/main/<part folder>/<NN-slug>.md`, cited as *Electrical Energy and Machines*, Ch. N.
- *Materials Science and Engineering* — `https://github.com/The-Studio-of-Sadiq/Materials-Science-and-Engineering/blob/main/Chapters/CHAPTER%20N.md`, cited as *Materials Science and Engineering*, Ch. N.
- *The Mathematics Universe* — `https://github.com/The-Studio-of-Sadiq/engineering-mathematics/blob/main/<part folder>/<NN-slug>.md`, cited as *The Mathematics Universe*, Ch. N.

### Extend the sibling books, do not repeat them

This book continues *Engineering Physics: Top Down* and Book 3 into hardware and software. *Engineering Physics* carries the solid state down to bands, carriers and doping (Ch. 6 §6.5–6.6), drift–diffusion (Ch. 14 §14.5) and a one-section sketch of the diode, BJT, MOSFET, op-amp and switching converter (Ch. 18 §18.3, §18.4, §18.8). Book 3 owns circuit analysis, frequency response, sampling, DSP and control. This book starts at those points: real devices with datasheet parameters, operating regions, temperature and breakdown; circuits that bias, amplify, switch, compute and convert; and the abstractions (logic levels, instructions, tasks) built on top.

- **Do not re-derive** band theory, carrier statistics, the law of mass action, doping, drift and diffusion currents, Maxwell's equations, heat-conduction laws, KCL/KVL and network theorems, phasors, Laplace and Bode analysis, two-port parameters, the sampling theorem, the DFT, digital-filter design, or Nyquist/root-locus control theory. State the result in one line (at most one displayed equation), cite the exact chapter and section with a link, and move on.
- **Add what the sibling books do not have**: device models as engineers use them (Shockley equation with $n$, $R_S$ and temperature; Ebers–Moll and hybrid-π; square-law and short-channel MOSFET; datasheet ratings and safe operating areas), circuit design procedures, logic and timing, architecture, code, real parts and numbers, failure modes and worked examples.
- **Make the hand-off visible**: Part I chapters open their first section with a short "Where *Engineering Physics* leaves off" paragraph naming the result taken over and the link; later chapters use `> **Boundary.**` notes. Where this book goes beyond the physics book's validity limits (high injection, breakdown, short-channel effects, self-heating), say so explicitly.

| Topic in this book | Owned by (exact place) |
|---|---|
| Bands, Fermi level, metals vs semiconductors vs insulators | *Engineering Physics* Ch. 6 §6.5 |
| Carrier concentrations, doping, common semiconductors | *Engineering Physics* Ch. 6 §6.6 |
| Drift–diffusion equations | *Engineering Physics* Ch. 14 §14.5 |
| Thermionic emission (Schottky barriers) | *Engineering Physics* Ch. 14 §14.6 |
| Thermal-resistance networks (heatsinks, junction temperature) | *Engineering Physics* Ch. 14 §14.7 |
| Diode, BJT and MOSFET from physics to circuit models (one-section sketch) | *Engineering Physics* Ch. 18 §18.3 |
| Ideal op-amp and standard configurations (sketch) | *Engineering Physics* Ch. 18 §18.4 |
| Filters, Fourier, sampling, ADC/DAC (sketch) | *Engineering Physics* Ch. 18 §18.5–18.7 |
| Rectifiers and switching converters (sketch) | *Engineering Physics* Ch. 18 §18.8 |
| Where lumped EEE models fail (high frequency, quantum limits) | *Engineering Physics* Ch. 18 §18.9; Ch. 17 §17.10 |
| Photons, optics and photonics (LEDs, photodiodes, lasers) | *Engineering Physics* Ch. 12 |
| Feedback and control across domains | *Engineering Physics* Ch. 21 |
| Circuit laws, nodal and mesh analysis, network theorems | *Circuits, Signals and Communications* Ch. 2–4 (`part-1-circuit-fundamentals/`) |
| Capacitors, inductors, first- and second-order transients | Book 3 Ch. 5–7 |
| Phasors, AC power, frequency response, Bode plots, two-ports | Book 3 Ch. 8–9, 12–13 |
| Laplace-domain analysis, poles and zeros | Book 3 Ch. 11 (`part-3-advanced-network-theory/11-laplace-domain-circuit-analysis.md`) |
| Transmission lines and high-frequency interconnects (signal integrity) | Book 3 Ch. 14 |
| Sampling, quantisation, reconstruction | Book 3 Ch. 19, 21 (`part-4-signals-and-systems/19-sampling-and-reconstruction.md`) |
| DFT/FFT and digital filters (the algorithms) | Book 3 Ch. 22–23 (`part-5-digital-signal-processing/`) |
| Noise in communication systems | Book 3 Ch. 29 |
| Feedback, stability margins, Nyquist, controller design | Book 3 Ch. 34–35 (`part-7-control-system-fundamentals/`) |
| Machines, drive control (V/f, FOC, DTC), four-quadrant drive mechanics | *Electrical Energy and Machines* Ch. 6–8, 10–12 (`part-3-motor-drives/`) |
| Energy storage and battery systems at system level | Book 5 Ch. 16 (`part-4-power-generation/16-energy-storage.md`) |
| Power quality, harmonics limits, grid codes, renewable grid integration | Book 5 Ch. 25, 27 (`part-7-power-quality-and-grid-modernization/`) |
| Semiconductor material properties, families (Si, SiC, GaN, III–V), interfaces | *Materials Science and Engineering* Ch. 32–35 |
| Electronic-materials manufacturing (wafers, lithography, deposition) | *Materials Science and Engineering* Ch. 50 |
| Linear systems, eigenvalues | *The Mathematics Universe* Ch. 8–10 (`part-3-linear-algebra/`) |
| Numerical methods, computational mathematics, optimisation (the mathematics) | *The Mathematics Universe* Ch. 22–24 (`part-7-numerical-computational/`) |

Before writing, open the sections in this table that your chapter touches and read them, so you know exactly what is covered there and how; use the real section numbers you saw.

## Figure markers

Planned figures are recorded in the chapter as an HTML comment on its own line, at the exact point the figure should appear (invisible in the PDF until the figure exists):

```
<!-- FIGURE 7.3 | figures/ch07/fig-7-3-ce-frequency-response.png | plot | Caption sentence. | Content: what is drawn, axes, data ranges, labels. -->
```

Fields: number, target path, kind (`plot`, `circuit`, `schematic`, `block-diagram`, `timing-diagram`, `state-diagram`, `waveform`, `cross-section`, `layout`, `flowchart`, `table-graphic`), caption, and a brief content spec for whoever draws it. Captions and specs must not contain the `|` character.

Figures are drawn by `figures/scripts/chNN.py` (shared style in `figures/scripts/figstyle.py`; circuit drawings may use `schemdraw`, including its logic-gate and timing-diagram modules) and saved to the marker's path. `node scripts/insert-figures.mjs` then places each drawn figure directly below its marker; the marker stays as the figure's specification:

```
<!-- FIGURE 7.3 | ... -->

![Figure 7.3 — Caption](../figures/ch07/fig-7-3-ce-frequency-response.png)

*Figure 7.3 — Caption.*
```

The full plan is collected in [`FIGURES.md`](FIGURES.md) (`node scripts/figure-plan.mjs`).
