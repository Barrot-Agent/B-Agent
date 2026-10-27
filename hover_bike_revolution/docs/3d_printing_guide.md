# 3D Printing Guide — Barrot HoverBike MK-I

## Printer Requirements

- Build volume: minimum **300 × 300 × 350 mm** (XYZ)
- Nozzle: **0.6 mm hardened steel** for CF-PLA/ABS-CF; 0.4 mm brass for PETG/TPU
- Enclosure: **required** for ABS-CF; recommended for CF-PLA
- Direct drive: **required** for TPU-95A
- Heated bed: up to **110 °C** for ABS-CF

## Print Settings by Component

### Frame Sections (CF-PLA)
| Parameter | Value |
|-----------|-------|
| Nozzle temp | 220 °C |
| Bed temp | 60 °C |
| Print speed | 45 mm/s |
| Layer height | 0.20 mm |
| Infill | 40 % gyroid |
| Cooling | 30 % |
| Supports | Tree supports |

### Battery & Electronics Enclosures (PETG)
| Parameter | Value |
|-----------|-------|
| Nozzle temp | 235 °C |
| Bed temp | 80 °C |
| Print speed | 50 mm/s |
| Layer height | 0.20 mm |
| Infill | 35 % gyroid |

### Wheel Hubs (ABS-CF)
| Parameter | Value |
|-----------|-------|
| Nozzle temp | 245 °C |
| Bed temp | 110 °C |
| Print speed | 40 mm/s |
| Layer height | 0.15 mm |
| Infill | 55 % cubic |
| Enclosure | Required |

### Magnet Housings (Nylon PA12 — SLS preferred)
Upload STL to Shapeways / Sculpteo and select **White Strong & Flexible (PA12)**.  
Tolerance: ±0.1 mm. FDM alternative: Nylon PA12 with dry box, 270 °C / 90 °C bed.

### Vibration Dampers (TPU-95A)
| Parameter | Value |
|-----------|-------|
| Nozzle temp | 230 °C |
| Bed temp | 45 °C |
| Print speed | 20 mm/s |
| Layer height | 0.25 mm |
| Direct drive | Required |

## Post-Processing Instructions

1. **Sanding**: Sand frame sections with 120 → 220 → 400 grit for smooth finish.
2. **Heat-set inserts**: Use soldering iron at 200 °C; press slowly and squarely.
3. **Epoxy bonding**: Use West System 105/207 for structural joints.
4. **Primer + paint**: Epoxy primer + polyurethane topcoat for UV and weather resistance.
5. **Wheel hubs**: Bore motor bore to tolerance using a drill press with a 60 mm boring bit.

## Quality Control Checklist

- [ ] All heat-set inserts flush with surface
- [ ] No visible delamination on CF-PLA parts
- [ ] All cavities clear of support material
- [ ] Magnet housing pockets dimensionally correct (50.2 × 25.2 × 10.2 mm)
- [ ] Wheel hub bore diameter 60.0 ± 0.05 mm
- [ ] No warping on ABS-CF parts (flatness ≤ 1 mm)
