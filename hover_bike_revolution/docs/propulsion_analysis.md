# Propulsion Analysis — Barrot HoverBike MK-I

## Comparison of Propulsion Systems

| System | Thrust (N) | Power (W) | Efficiency | Maturity |
|--------|-----------:|----------:|------------|---------|
| BLDC Hub Motors (primary) | ~200 | 750 | 88 % | High |
| EM Pulse Drive (burst) | ~15 | 100 avg | 60 % | Medium |
| Ion Thruster (experimental) | ~0.1 | 200 | 65 % | Low |

## BLDC Hub Motor Performance

- **Rated power**: 750 W per motor × 2 = 1,500 W total
- **Peak power**: 1,500 W per motor × 2 = 3,000 W (30 s burst)
- **Torque at 48 V, 30 km/h**: ~25 N·m per motor
- **Efficiency**: 88 % at rated load
- **Regenerative braking**: ~80 W recovered at 30 km/h, 1.5 m/s² deceleration

## Efficiency Metrics

At 30 km/h cruise:
- Aerodynamic drag: ~22 N (Cd=0.35, A=0.60 m²)
- Required propulsive power: ~182 W
- Electrical input (@ 88 % eff): ~207 W
- Remaining for acceleration reserve: 543 W (motors running at ~14 % rated)

## Thrust Calculations

Tractive force = Motor torque × 2 / Wheel radius = 25 × 2 / 0.20 = **250 N**  
Available acceleration = (250 N − 22 N drag) / 120 kg = **1.9 m/s²**  
Time 0→30 km/h ≈ (30/3.6) / 1.9 ≈ **4.4 s** (full throttle, level)

## Real-World Testing Protocol

1. Mount bike on dyno or tethered to load cell.
2. Apply 10 %, 25 %, 50 %, 75 %, 100 % throttle; record speed, current, voltage.
3. Calculate efficiency at each point; compare to motor datasheet.
4. Run 30-minute sustained ride at 30 km/h; monitor motor temperature.
5. Test regenerative braking: coast from 30 km/h to 0; measure recovered Wh.
6. Test acceleration 0→30 km/h; compare to simulation.
