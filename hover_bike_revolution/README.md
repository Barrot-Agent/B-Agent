# 🏍️ Barrot Revolution Hover Bike

An open-source, 3D-printable personal levitation vehicle powered by
Halbach array magnetic levitation, active PID stabilisation, linear
motor propulsion, and a hybrid Li-ion/solar energy system.

**Part of the Barrot APEX Lattice Research System**

---

## ⚡ Quick Start

```bash
# Generate complete design package
cd hover_bike_revolution
python src/hover_bike_generator.py

# Run magnetic system analysis
python src/magnetic_system_designer.py

# Run propulsion simulation
python src/propulsion_simulator.py

# Run power management analysis
python src/power_management_system.py

# Simulate control firmware
python src/control_firmware.py

# 3D print preparation
python src/3d_print_preparation.py

# Generate assembly guide
python src/assembly_guide_generator.py
```

---

## 📊 Performance Specifications

| Parameter | Target |
|-----------|--------|
| Hover height | 10–30 mm (adjustable) |
| Max payload | 90–120 kg |
| Cruise speed | 30–50 km/h |
| Max speed | 55 km/h |
| Range | 15–30 km per charge |
| Total power | 400–550 W cruise |
| Battery | 48V 10Ah (480 Wh LiPo) |
| Solar | +50–75 W peak supplement |
| Total weight | 20–35 kg |
| DIY cost | $2,000–$4,000 |

---

## 🗂️ Project Structure

```
hover_bike_revolution/
├── src/
│   ├── hover_bike_generator.py       # Parametric design + BOM
│   ├── magnetic_system_designer.py   # Halbach array physics
│   ├── propulsion_simulator.py       # Motor + propulsion models
│   ├── power_management_system.py    # Energy system optimisation
│   ├── control_firmware.py           # Flight controller simulation
│   ├── 3d_print_preparation.py       # STL specs + print estimates
│   └── assembly_guide_generator.py   # Step-by-step build guide
│
├── models/                           # Generated design outputs (JSON)
│   ├── hover_bike_design.json
│   ├── magnetic_analysis.json
│   ├── propulsion_analysis.json
│   ├── power_analysis.json
│   ├── control_simulation.json
│   └── print_preparation.json
│
├── firmware/                         # Arduino firmware files
│   ├── stabilization_controller.ino
│   ├── power_manager.ino
│   ├── sensor_fusion.ino
│   └── safety_protocols.ino
│
└── docs/
    ├── hover_bike_design_specification.md  # Full technical spec
    ├── cost_breakdown.md                   # Detailed BOM + costs
    └── assembly_guide.md                   # Auto-generated build guide
```

---

## 🔧 System Overview

### 1. Magnetic Levitation (Halbach Arrays)

Four Halbach arrays (N52 neodymium magnets) concentrate magnetic flux
downward for levitation. Active PID control (4 correction coils, ~80W)
maintains stable hover height against Earnshaw instability.

```
B(y) = B₀ · exp(-k·y)    [field decays exponentially with gap]
Lift pressure: P = B²/(2μ₀)
```

### 2. Propulsion (Hybrid)

- **Hub motors:** 2× 48V 500W brushless (direct drive, 87% η)
- **Linear motor:** 3D-printed stator + permanent magnet rotor
- **Regenerative braking:** 70% kinetic recovery

### 3. Power System

- **Battery:** LiPo 48V 10Ah with 13S BMS
- **Solar:** Thin-film 100W flexible panel
- **Supercap:** 16V 100F bank for peak demand buffering
- **Range:** ~25 km at 40 km/h (battery only)

### 4. Control System

- **Main controller:** Raspberry Pi 4 (1 kHz PID loop)
- **Co-processor:** Arduino Nano (real-time sensor reading)
- **Sensors:** MPU-6050 IMU (×2), HC-SR04 ultrasonic (×4), Hall effect (×8)
- **Algorithms:** Complementary filter for attitude, PID for height + attitude

---

## ✅ Physics Feasibility

| System | Status | Based On |
|--------|--------|----------|
| Halbach levitation | ✅ Proven | Maglev/Inductrack research |
| Active PID control | ✅ Proven | Drone technology |
| Hub motor propulsion | ✅ Proven | E-bikes |
| Li-ion energy system | ✅ Proven | EV industry |
| CF-PLA frame | ✅ Proven | Markforged aerospace parts |
| Solar supplement | ✅ Proven | Commercial solar e-bikes |

**Key constraint:** Active electromagnet stabilisation adds ~80W overhead.
Hover height is limited to 10–30 mm (not aerial flight).

---

## 🛡️ Safety

- Hover height: 10–30 mm (surface transport, not aerial)
- Emergency stop: pull main fuse (battery enclosure left side)
- Fail-safe: power loss → magnets de-energise → settles to ground
- Required PPE: helmet + full protective gear at all times
- Max initial speed: 20 km/h until 5+ hours logged

---

## 🚀 APEX Lattice Connection

The hover bike magnetic system shares mathematical foundations with:

- **Fusion reactors:** Halbach array optimisation ↔ stellarator coil design
- **Millennium Problems:** Yang-Mills field equations govern permanent magnet physics
- **Control theory:** PID hover control ↔ plasma shape control in tokamaks

See `../.apex_lattice/Hover_Bike_Physics.log` for complete physics analysis.

---

## 📄 License

Open source — community contributions welcome.
All code and designs released for educational and non-commercial use.
