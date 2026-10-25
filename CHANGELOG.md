# Changelog

All notable changes to *Electronics and Computing*. Dates are ISO 8601. Versions follow the tags in this repository; each release attaches the compiled PDF.

## [1.0.0] — 2026-10-25

First complete edition.

### Added
- **Part I — Electronic Devices** (Chapters 1–5): device fundamentals, junction devices, BJTs, FETs, thyristors, IGBTs and wide-bandgap devices. Each chapter opens where *Engineering Physics* leaves off and links the exact sections it builds on.
- **Part II — Analog Electronics** (6–10): diode circuits, transistor amplifiers, operational amplifiers, feedback and oscillators, analog integrated circuits.
- **Part III — Digital Electronics** (11–15): number systems, Boolean algebra and logic gates, combinational and sequential systems, digital system design.
- **Part IV — Computer Architecture and Digital Hardware** (16–19): computer architecture, microprocessors and microcontrollers, memory and programmable logic, hardware description languages.
- **Part V — Programming and Computational Systems** (20–24): programming fundamentals, C/C++ and Python for engineering, algorithms and data structures, scientific computing.
- **Part VI — Embedded and Real-Time Systems** (25–28): embedded-system architecture, embedded interfaces, real-time computing, embedded system design.
- **Part VII — Power Electronics** (29–32): power-electronic fundamentals, DC–DC converters, AC–DC and DC–AC conversion, motor drives and power conversion.
- **Part VIII — Integrated Circuits and VLSI** (33–35): CMOS fundamentals, VLSI design, hardware–software co-design.
- Eight part openers, one per part folder.
- Code listings in C, C++, Python, Verilog/SystemVerilog and VHDL; every Python listing runs and prints the output quoted in the text.
- 197 figures, each drawn by a reproducible script in `figures/scripts/chNN.py` from the chapter's own numbers; figure plan in `FIGURES.md`.
- `pdf/Electronics-and-Computing.pdf` with clickable contents, PDF bookmarks and KaTeX math, built by `scripts/build-pdf.mjs`.
- MCP server (`mcp/server.mjs`) to list, read, search and typeset the book and fetch its figures.
- Book checks (`scripts/check-book.mjs`), CI and release workflows, issue and pull-request templates, community files, citation file, social preview image and wiki generator.

### Fixed (before release, from figure-agent cross-checks)
- Ch. 1–6: BJT avalanche run-away condition; relay-driver base drive and storage times; solar-cell open-circuit voltage; IRF540N threshold wording; GaN output-charge energy; clamper droop.
- Ch. 7–12: CE corner frequencies (exact versus time-constant estimates); crystal load-capacitance margin and frequency; op-amp compensation phase margins; bandgap gain; binary-fraction rule; deterministic Quine–McCluskey output.
- Ch. 13–19: RISC-V register-file size; FPGA path delays; ADC capture window; DMA CPU load; SRAM cell area versus node name; quadrature-decoder direction; coverage test count.
- Ch. 21–28: C++ vtable layout under the Itanium ABI; converter efficiency figures; IR-drop hot-spot location; Flash-wear log budget; leakage versus temperature; PWM update delay; priority-inversion timing.
- Ch. 29–33: overload example and turn-off overshoot (Figures 29.1 and 29.5 redrawn); capacitor DC-bias derating and ripple; commutation overlap; LCL damping roll-off; grid-converter current loop retuned for the full LCL model (Figure 32.6 redrawn); inverter switching threshold and Elmore delay.
- Ch. 34–35: pipelining throughput; AEC-Q100 temperature grades; int8 quantisation scale.
