# Power System Analysis — Barrot HoverBike MK-I

## Battery Requirements

| Parameter | Value |
|-----------|-------|
| Chemistry | LiFePO4 (lithium iron phosphate) |
| Configuration | 15S4P (48 V nominal) |
| Capacity | 1,000 Wh / 20.8 Ah |
| Cell spec | 3.2 V, 20 Ah prismatic (e.g. CALB CA20FI) |
| Cell count | 60 cells |
| Max charge current | 10 A (0.5 C) |
| Max discharge current | 60 A (3 C continuous) |
| Mass | ~10 kg |
| Cycle life | 3,000 cycles @ 80 % DoD |
| BMS | Daly Smart BMS 48 V 100 A |

## Solar Integration Details

- Panel: Thin-film CIGS flexible module, 150 Wp
- Dimensions: 800 × 400 mm (fits on bike canopy)
- Efficiency: ~10.5 %
- Daily yield (4.5 peak sun hours, 800 W/m²): ~67 Wh
- MPPT controller: 40 A, 12–48 V input
- Solar charge fraction: ~7 % of daily 1,000 Wh capacity

## Energy Budgeting

At 30 km/h cruise, total power draw:

| Load | Power (W) |
|------|----------:|
| Maglev stabilisation | 75 |
| Hub motor propulsion (cruise) | 270 |
| Control electronics | 15 |
| Lighting | 10 |
| **Total** | **370** |

Range at 30 km/h: 1,000 Wh / 370 W × 30 km/h = **81 km** (theoretical)  
Practical range (80 % DoD, efficiency losses): ~**26 km**

## Charge Management

1. **Grid charging**: 10 A × 54.75 V = 547 W max → 3 h full charge.
2. **Solar top-up**: 67 Wh/day → ~7 % SoC added per day parked.
3. **Regenerative braking**: ~20 braking events × 0.15 Wh each = 3 Wh/ride (minor).
4. **Charging priority**: BMS enforces cell balance during charge.
   Each cell must remain 2.50–3.65 V. BMS disconnects at either limit.
