# Part IV — Computer Architecture and Digital Hardware

Part III built digital circuits from gates and flip-flops: adders, multiplexers, counters, state machines, all clocked and timed. This part assembles them into the machines that run almost every modern product — processors, memories and programmable logic — and into the languages used to design them. An instruction set lets software be written once and run on circuits that change every few years, but the abstraction leaks. A motor-control loop misses deadlines because of cache misses, a data logger dies because its flash wears out, an interrupt arrives late because of a priority set one line wrong, and an FPGA design fails timing because its routing is congested. This part explains the hardware beneath the instruction set and the netlist well enough to predict those failures with numbers.

## By the end of this part you should understand

- How an instruction set (RISC-V as the example) defines the contract between software and hardware, and how a datapath, a control unit, registers and an ALU implement it.
- How pipelining raises throughput, what data, control and structural hazards cost, and how to estimate execution time with the performance equation.
- Why memory is a hierarchy, how caches are organised and why they miss, and how to compute average memory access time and its effect on CPI.
- How buses, interrupts, polling and DMA move data between processors, memory and devices, and when each is appropriate.
- How a Cortex-M microcontroller executes code, maps memory and peripherals, handles nested interrupts, and drives timers, GPIO and serial peripherals at register level — and when a microprocessor is needed instead.
- How SRAM, DRAM and flash cells store bits, and what that implies for speed, density, refresh, endurance and retention, and how memories are interfaced.
- How FPGAs implement logic with LUTs, configurable logic blocks and programmable interconnect, how CPLDs differ, and when spatial hardware accelerates a computation.
- How hardware is described in Verilog, SystemVerilog and VHDL, simulated, synthesised, constrained and verified.

## Chapters

| Chapter | Central question | What it delivers |
|---|---|---|
| [Chapter 16 — Computer Architecture](16-computer-architecture.md) | How does an instruction set become a working, fast processor, and how is its performance estimated? | Performance equation, RISC-V formats and encodings, registers, ALUs, single-cycle and pipelined datapaths with hazards, control units, memory hierarchy and AMAT, caches, buses, interrupts, polling, interrupt and DMA I/O |
| [Chapter 17 — Microprocessors and Microcontrollers](17-microprocessors-and-microcontrollers.md) | How does a microcontroller core execute code, reach its peripherals and respond to events, and when is a microprocessor needed instead? | Cortex-M programmer's model, wait states, memory map and vector table, Thumb-2 addressing modes, NVIC stacking and tail-chaining, timers and PWM with dead time, GPIO and atomic access, serial peripheral blocks, clocks, DMA and triggers, MCU versus MPU |
| [Chapter 18 — Memory and Programmable Logic](18-memory-and-programmable-logic.md) | How are bits stored and logic made programmable, and what limits speed, endurance and reliability? | SRAM and DRAM cells, DRAM timing and refresh, ROM and NOR/NAND flash with wear calculations, parallel, DDR and serial interfaces, FPGA architecture, LUTs, CLBs, routing, CPLDs, acceleration and Amdahl's law, applications |
| [Chapter 19 — Hardware Description Languages](19-hardware-description-languages.md) | How is digital hardware described, simulated, synthesised and verified in a language? | HDL fundamentals, Verilog/SystemVerilog and VHDL, combinational and sequential descriptions, simulation semantics, synthesis, timing constraints, test benches, the FPGA implementation flow and hardware verification |

## How this part connects to the rest of the book

Part IV stands on Part III: number representation (Chapter 11), Boolean algebra and logic minimisation (Chapter 12), adders, multiplexers and ALUs (Chapter 13), flip-flops, timing constraints and synchronisers (Chapter 14) and digital system design (Chapter 15) are used here as known building blocks. Looking forward, Part V programs these machines, Chapter 21 relying on the memory map, `volatile` access and cache behaviour of Chapters 16 and 17. Part VI builds embedded and real-time systems on them: Chapter 25 chooses and boots microcontrollers, Chapter 26 develops the interface protocols whose peripheral blocks appear in Chapter 17, and Chapter 27 turns the interrupt latencies of this part into schedulability analysis. The timers of Chapter 17 drive the converters of Part VII, and Part VIII designs the chips themselves, ending with processor–FPGA partitioning in Chapter 35.

Two sibling books carry theory this part uses without re-deriving it. The tunnelling physics behind flash memory and the magnetic tunnel junction behind MRAM come from *[Engineering Physics: Top Down](https://github.com/The-Studio-of-Sadiq/Engineering-Physics)*, Ch. 4 and Ch. 14. Transmission-line behaviour of fast buses and DDR interfaces, and the digital-filter and FFT algorithms that processors and FPGAs accelerate, come from *[Circuits, Signals and Communications](https://github.com/The-Studio-of-Sadiq/Circuits-Signals-and-Communications)*, Ch. 14 and Chs. 22–23. The drive-control laws that run on the microcontrollers of Chapter 17 belong to *[Electrical Energy and Machines](https://github.com/The-Studio-of-Sadiq/Electrical-Energy-and-Machines)*, Ch. 10–12.
