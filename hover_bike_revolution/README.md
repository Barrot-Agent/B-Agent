# 🚲 Barrot HoverBike Revolution

**A fully open-source, 3D-printable magnetic levitation bicycle.**

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

---

## What is it?

The Barrot HoverBike MK-I is a community-designed, open-source personal
transport vehicle that uses **passive Halbach array magnetic levitation**
combined with **BLDC hub-motor propulsion** and a **hybrid LiFePO4 + solar
+ regenerative** energy system.

Every structural component is designed to be printed on a desktop FDM printer.

---

## Quick Specs

| Parameter | Value |
|-----------|-------|
| Hover height | 10–30 cm |
| Range | 25–30 km per charge |
| Top speed | 50 km/h |
| Build cost (DIY) | ~$2,000–$2,400 USD |
| Total mass | ~27 kg |
| Rider capacity | up to 120 kg |

---

## Repository Structure

```
hover_bike_revolution/
├── src/                       # Python design & simulation scripts
│   ├── hover_bike_generator.py
│   ├── magnetic_system_designer.py
│   ├── propulsion_simulator.py
│   ├── power_management_system.py
│   ├── control_firmware.py
│   ├── 3d_print_preparation.py
│   └── assembly_guide_generator.py
├── models/                    # STL placeholder files
├── firmware/                  # Arduino / ATtiny firmware
│   ├── stabilization_controller.ino
│   ├── power_manager.ino
│   ├── sensor_fusion.ino
│   └── safety_protocols.ino
├── simulations/               # Physics simulation modules
│   ├── magnetic_field_sim.py
│   ├── flight_dynamics_sim.py
│   ├── power_consumption_sim.py
│   └── stability_analysis.py
├── tools/                     # BOM, cost, print estimation
│   ├── bom_generator.py
│   ├── cost_calculator.py
│   ├── print_estimator.py
│   └── component_sourcer.py
├── docs/                      # Technical documentation
│   ├── hover_bike_design_specification.md
│   ├── 3d_printing_guide.md
│   ├── magnetic_system_theory.md
│   ├── propulsion_analysis.md
│   ├── control_system_guide.md
│   ├── power_system_analysis.md
│   └── cost_breakdown.md
└── README.md
```

---

## Getting Started

### Generate Design Artefacts

```bash
cd hover_bike_revolution
python src/hover_bike_generator.py
```

Outputs: `hover_bike_spec.json`, `component_geometry.json`, `assembly_guide.md`, `bill_of_materials.md`

### Run Magnetic System Analysis

```bash
python src/magnetic_system_designer.py
```

### Simulate the Control Loop

```bash
python src/control_firmware.py
```

### Estimate Print Time & Cost

```bash
python tools/print_estimator.py
python tools/cost_calculator.py
```

### Run All Simulations

```bash
python simulations/magnetic_field_sim.py
python simulations/flight_dynamics_sim.py
python simulations/power_consumption_sim.py
python simulations/stability_analysis.py
```

---

## Physics Basis

The levitation system is based on the well-validated **Inductrack concept**
(Post & Ryutov, 2000) and has been demonstrated in laboratory settings
worldwide. The propulsion system uses commercial BLDC motors identical to
those in electric bicycles and skateboards.

**This design does not claim perpetual motion or over-unity energy.** All
subsystems operate within established thermodynamic laws.

---

## License

All designs and code in this directory are released under **CC BY-SA 4.0**.
You are free to build, modify, and redistribute with attribution.

---

*Part of the Barrot-Agent B-Agent open research project.*
