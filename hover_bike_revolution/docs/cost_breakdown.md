# Cost Breakdown — Barrot HoverBike MK-I

## Summary

| Category | Cost (USD) |
|----------|----------:|
| Magnetic levitation components | $482 |
| Propulsion (motors + ESCs + wiring) | $692 |
| Power system (battery + BMS + solar) | $491 |
| Control electronics | $199 |
| Mechanical hardware | $122 |
| 3D printing filament | $298 |
| Electricity (printing ~80 h) | $3 |
| Miscellaneous consumables | $80 |
| **TOTAL** | **~$2,367** |

## Detailed Breakdown

### Magnetic Levitation ($482)
- 64× N52 magnets (50×25×10 mm): $320
- 12× Hall effect sensors: $15
- Correction coil wire: $32
- Epoxy: $24
- Non-magnetic jig/tools: $91

### Propulsion ($692)
- 2× 750 W BLDC hub motors: $440
- 2× VESC 75/300 ESC: $200
- Motor phase wire + connectors: $52

### Power System ($491)
- 60× LiFePO4 cells (3.2 V 20 Ah): $480 → offset by bulk pricing → $350
- Daly Smart BMS: $55
- MPPT charge controller: $35
- Thin-film solar module: $120
- XT90 + 8 AWG wire + fuses: $36 (already included above at $491)

### Control Electronics ($199)
- Raspberry Pi 4B (4 GB): $55
- 2× MPU-9250 IMU: $16
- BMP388 barometer: $7
- 4× HC-SR04 ultrasonic: $10
- DC-DC buck converter: $12
- Emergency cut-off switch: $15
- MicroSD 32 GB: $8
- Misc wiring + PCB: $76

### Mechanical Hardware ($122)
- Heat-set inserts (titanium M8): $44
- Bolt/nut assortments: $32
- Foam pads: $12
- Tyres: $30 (bike shop)
- Other hardware: $4

## Budget Optimisation Strategies

1. **Cells**: Source Grade A LiFePO4 cells from Chinese manufacturers (CALB, EVE) via group buy for ~$5/cell vs. $8 retail. Saves ~$180.
2. **Motors**: QSMotor on AliExpress is ~40 % cheaper than Western distributors.
3. **SLS printing**: Use university makerspaces or community labs for free/subsidised SLS access.
4. **ESCs**: Flipsky VESC clones (~$60 each) are half the price of Trampa originals with comparable performance.
5. **Filament**: Buy in 5 kg spools; $22/kg PETG vs. $35/kg in 1 kg spools.

**Optimised build cost: ~$2,000 USD**  
**Standard build cost: ~$2,400 USD**  
**Premium components build: ~$3,500 USD**
