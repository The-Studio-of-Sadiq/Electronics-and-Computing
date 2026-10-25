# Electronics and Computing — Master Syllabus

**Book 4 — Electronics & Computing Core**

**Objective:** Cover electronic devices, analog and digital hardware, computer architecture, programming, embedded computation, and hardware-software interaction.

Structure: 8 Parts · 35 Chapters. Each part is a folder `part-N-<slug>/`: its `README.md` is the part opener and `NN-<slug>.md` is Chapter NN.

The backbone is **devices → analog circuits → digital logic → computer hardware → software → embedded and real-time systems → power electronics → integrated circuits and co-design**. One idea runs through all of it: a nonlinear device, biased and switched, is turned into a reliable abstraction (an amplifier, a logic gate, an instruction, a task, a converter), and every abstraction holds only inside the limits of voltage, current, time, power and temperature that the device beneath it sets.

---

## Part I — Electronic Devices · `part-1-electronic-devices/`

### Chapter 1. Electronic Device Fundamentals · `01-electronic-device-fundamentals.md`
- Voltage-current characteristics
- Nonlinear devices
- Device models
- Operating regions
- Biasing
- Small-signal concepts
- Temperature effects
- Device parameters
- Practical limitations

### Chapter 2. Semiconductor Junction Devices · `02-semiconductor-junction-devices.md`
- PN-junction operation
- Diode characteristics
- Rectifier diodes
- Zener diodes
- Schottky diodes
- Photodiodes
- LEDs
- Solar cells
- Varactor diodes
- Protection diodes

### Chapter 3. Bipolar Junction Transistors · `03-bipolar-junction-transistors.md`
- BJT structure
- Operating regions
- Common-base configuration
- Common-emitter configuration
- Common-collector configuration
- DC biasing
- Load lines
- Small-signal models
- Amplification
- Switching behavior
- Frequency response

### Chapter 4. Field-Effect Transistors · `04-field-effect-transistors.md`
- JFET operation
- MOSFET structure
- Enhancement and depletion modes
- Threshold voltage
- Operating regions
- DC biasing
- Small-signal models
- MOSFET amplification
- MOSFET switching
- Power MOSFET fundamentals

### Chapter 5. Advanced Semiconductor Devices · `05-advanced-semiconductor-devices.md`
- Thyristors
- SCRs
- TRIACs
- DIACs
- IGBTs
- Wide-bandgap power devices
- Optoelectronic devices
- Compound-semiconductor devices
- Device selection and ratings

## Part II — Analog Electronics · `part-2-analog-electronics/`

### Chapter 6. Diode Circuits · `06-diode-circuits.md`
- Half-wave rectifiers
- Full-wave rectifiers
- Bridge rectifiers
- Rectifier performance
- Ripple
- Capacitor filtering
- Clipping circuits
- Clamping circuits
- Voltage multipliers
- Practical rectifier design

### Chapter 7. Transistor Amplifiers · `07-transistor-amplifiers.md`
- Single-stage amplifiers
- Common-emitter amplifiers
- Common-source amplifiers
- Emitter and source followers
- Multistage amplifiers
- Voltage and current gain
- Input and output impedance
- Small-signal analysis
- Frequency response
- Distortion

### Chapter 8. Operational Amplifiers · `08-operational-amplifiers.md`
- Ideal and practical op-amps
- Inverting and non-inverting amplifiers
- Summing and difference amplifiers
- Integrators and differentiators
- Comparators
- Instrumentation amplifiers
- Precision rectifiers
- Active filters
- Oscillators
- Limitations and stability

### Chapter 9. Feedback and Oscillators · `09-feedback-and-oscillators.md`
- Positive and negative feedback
- Feedback topologies
- Gain and bandwidth
- Stability
- Barkhausen criterion
- RC oscillators
- LC oscillators
- Crystal oscillators
- Waveform generators

### Chapter 10. Analog Integrated Circuits · `10-analog-integrated-circuits.md`
- Differential amplifiers
- Current mirrors
- Active loads
- Multistage integrated amplifiers
- Frequency compensation
- Analog IC architecture
- Voltage references
- Regulators
- Comparators
- Mixed-signal interfaces

## Part III — Digital Electronics · `part-3-digital-electronics/`

### Chapter 11. Digital Number Systems · `11-digital-number-systems.md`
- Binary, octal, decimal, and hexadecimal
- Signed number representation
- Two's complement
- Fixed-point arithmetic
- Floating-point representation
- Binary arithmetic
- Overflow
- Boolean variables

### Chapter 12. Boolean Algebra and Logic Gates · `12-boolean-algebra-and-logic-gates.md`
- Boolean algebra
- Logic gates
- Truth tables
- Boolean simplification
- Karnaugh maps
- De Morgan's laws
- Combinational logic
- Logic minimization

### Chapter 13. Combinational Digital Systems · `13-combinational-digital-systems.md`
- Adders and subtractors
- Multiplexers
- Demultiplexers
- Encoders
- Decoders
- Comparators
- Arithmetic logic units
- Code converters
- Timing and propagation delay

### Chapter 14. Sequential Digital Systems · `14-sequential-digital-systems.md`
- Latches
- Flip-flops
- Registers
- Counters
- Shift registers
- Finite-state machines
- State encoding
- Timing constraints
- Clock-domain considerations
- Reset strategies

### Chapter 15. Digital System Design · `15-digital-system-design.md`
- Design methodology
- State diagrams
- State tables
- Hardware timing
- Glitches
- Synchronization
- Memory elements
- Logic implementation
- Verification and test benches

## Part IV — Computer Architecture and Digital Hardware · `part-4-computer-architecture-and-digital-hardware/`

### Chapter 16. Computer Architecture · `16-computer-architecture.md`
- Computer organization
- Instruction sets
- CPU datapaths
- Control units
- Registers
- ALUs
- Memory hierarchy
- Caches
- Buses
- Interrupts
- Input/output architecture

### Chapter 17. Microprocessors and Microcontrollers · `17-microprocessors-and-microcontrollers.md`
- Processor architecture
- Instruction execution
- Memory maps
- Addressing modes
- Interrupt handling
- Timers and counters
- GPIO
- Serial interfaces
- Peripheral integration
- Microprocessor versus microcontroller

### Chapter 18. Memory and Programmable Logic · `18-memory-and-programmable-logic.md`
- SRAM and DRAM
- ROM and Flash
- Memory interfaces
- FPGA architecture
- LUTs
- Configurable logic blocks
- Programmable interconnects
- CPLDs
- Hardware acceleration
- FPGA applications

### Chapter 19. Hardware Description Languages · `19-hardware-description-languages.md`
- HDL fundamentals
- Verilog or SystemVerilog
- VHDL overview
- Combinational logic descriptions
- Sequential logic descriptions
- Simulation
- Synthesis
- Timing constraints
- Test benches
- FPGA implementation
- Hardware verification

## Part V — Programming and Computational Systems · `part-5-programming-and-computational-systems/`

### Chapter 20. Programming Fundamentals · `20-programming-fundamentals.md`
- Algorithms
- Variables and data types
- Control flow
- Functions
- Arrays and data structures
- Memory
- Debugging
- Modular programming
- Error handling
- Testing

### Chapter 21. C/C++ for Engineering · `21-c-cpp-for-engineering.md`
- C fundamentals
- Pointers
- Structures
- Memory management
- Bitwise operations
- Peripheral-oriented programming
- C++ classes
- Object-oriented design
- Compilation and linking
- Embedded-oriented C/C++

### Chapter 22. Python for Engineering · `22-python-for-engineering.md`
- Python fundamentals
- Numerical arrays
- Data processing
- Plotting and visualization
- Scientific libraries
- Signal analysis
- Data acquisition
- Automation scripts
- File formats
- Reproducible computational experiments

### Chapter 23. Algorithms and Data Structures · `23-algorithms-and-data-structures.md`
- Complexity analysis
- Arrays and linked lists
- Stacks and queues
- Trees and graphs
- Hash tables
- Searching and sorting
- Numerical algorithms
- Graph algorithms
- Algorithm selection
- Engineering applications

### Chapter 24. Scientific Computing · `24-scientific-computing.md`
- Numerical computing environments
- Matrix computation
- Scientific data formats
- Simulation workflows
- Parallel computing fundamentals
- Performance profiling
- Numerical precision
- Reproducibility
- Software testing
- Version control and collaborative workflows

## Part VI — Embedded and Real-Time Systems · `part-6-embedded-and-real-time-systems/`

### Chapter 25. Embedded-System Architecture · `25-embedded-system-architecture.md`
- Embedded-system models
- Hardware-software partitioning
- Microcontroller selection
- Memory constraints
- Power constraints
- Firmware architecture
- Peripheral drivers
- Boot processes
- Firmware updates

### Chapter 26. Embedded Interfaces · `26-embedded-interfaces.md`
- GPIO
- UART
- SPI
- I²C
- CAN
- USB fundamentals
- Ethernet fundamentals
- ADC and DAC interfaces
- Sensor interfaces
- Communication troubleshooting

### Chapter 27. Real-Time Computing · `27-real-time-computing.md`
- Real-time constraints
- Interrupts
- Scheduling
- Timers
- Concurrency
- Race conditions
- Synchronization
- Real-time operating systems
- Task priorities
- Latency and jitter
- Watchdogs and fault handling

### Chapter 28. Embedded System Design · `28-embedded-system-design.md`
- Hardware abstraction
- Firmware modularity
- Device drivers
- State machines
- Low-power design
- Data logging
- Communications
- Debugging
- Hardware-in-the-loop testing
- Firmware validation

## Part VII — Power Electronics · `part-7-power-electronics/`

### Chapter 29. Power-Electronic Fundamentals · `29-power-electronic-fundamentals.md`
- Power switching
- Semiconductor switch characteristics
- Switching losses
- Conduction losses
- Thermal constraints
- Gate driving
- Snubbers
- Protection
- Switching-frequency trade-offs

### Chapter 30. DC–DC Converters · `30-dc-dc-converters.md`
- Buck converter
- Boost converter
- Buck–boost converter
- Continuous and discontinuous conduction
- Converter waveforms
- Inductor and capacitor sizing
- Ripple
- Efficiency
- Feedback control interface

### Chapter 31. AC–DC and DC–AC Conversion · `31-ac-dc-and-dc-ac-conversion.md`
- Controlled and uncontrolled rectifiers
- Inverters
- PWM
- Single-phase and three-phase inverters
- Harmonics
- Filtering
- Switching strategies
- Semiconductor selection
- Protection and thermal design

### Chapter 32. Motor Drives and Power Conversion · `32-motor-drives-and-power-conversion.md`
- Power-electronic drive architectures
- DC motor drives
- Induction motor drive interfaces
- Variable-frequency drives
- Converter-fed machines
- Regenerative operation
- Battery charging
- Renewable-energy converters
- Grid-connected converter fundamentals

## Part VIII — Integrated Circuits and VLSI · `part-8-integrated-circuits-and-vlsi/`

### Chapter 33. CMOS Fundamentals · `33-cmos-fundamentals.md`
- CMOS logic
- MOSFET switching
- Static and dynamic power
- Propagation delay
- Noise margins
- CMOS gates
- Latches and flip-flops
- Layout fundamentals

### Chapter 34. VLSI Design · `34-vlsi-design.md`
- Design hierarchy
- RTL design
- Logic synthesis
- Physical design
- Placement and routing
- Timing analysis
- Power estimation
- Design-rule checking
- Verification
- Fabrication constraints

### Chapter 35. Hardware–Software Co-Design · `35-hardware-software-co-design.md`
- Partitioning computation
- Processor versus FPGA
- Hardware acceleration
- Memory and data movement
- Performance modeling
- Embedded AI deployment
- Real-time constraints
- System-level verification

---

## Boundary

This book owns electronic devices as circuit elements, analog and digital circuits, computer architecture and digital hardware, programming and scientific computing as engineering tools, embedded and real-time systems, power-electronic converter circuits, and integrated-circuit design. Semiconductor band physics and carrier transport are taken from *Engineering Physics*; semiconductor materials from *Materials Science and Engineering*; circuit laws, frequency response, signals, DSP and control theory from Book 3; machines, drive control and grid integration from Book 5.

## Relation to the other books

| Topic | Where it lives |
|---|---|
| Linear algebra, ODEs, transforms, numerical methods and optimisation (the mathematics itself) | The Mathematics Universe |
| Band theory, carrier statistics, doping, drift–diffusion, Maxwell's equations, heat transfer (the physics itself) | Engineering Physics |
| Semiconductor material properties and families (Si, SiC, GaN, III–V), thin films, electronic-materials manufacturing | Materials Science and Engineering |
| Circuit laws, network theorems, transient and AC analysis, Laplace domain, two-ports, Bode plots, sampling, DSP, communication links, feedback and control theory | Circuits, Signals and Communications (Book 3) |
| Electrical machines, drive control (V/f, FOC, DTC), power-system analysis, grid codes and renewable grid integration | Electrical Energy and Machines (Book 5) |
| Practical robot and industrial-automation controllers | Robotics and automation books |
| Devices, analog and digital circuits, computer architecture, HDLs, programming, embedded and real-time systems, power-electronic converters, CMOS and VLSI, hardware–software co-design | **This book** |
