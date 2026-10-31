# Magnetic System Theory — Halbach Array Levitation

## Halbach Array Physics

A Halbach array is a special arrangement of permanent magnets that concentrates magnetic flux on one side while nearly cancelling it on the other. For a linear array of N magnets per spatial wavelength λ, the magnetisation direction of the k-th magnet is rotated by k × (2π/N) radians.

### Field Equations

The magnetic flux density at height z above an ideal infinite Halbach array:

```
B(z) = B₀ × exp(−kz)
```

Where:
- `B₀ = Br × (1 − exp(−kh)) × sin(π/N)/(π/N)` — peak surface field
- `Br` = remanent flux density (N52: 1.45 T)
- `k = 2π/λ` — spatial wavenumber
- `h` = magnet height (m)
- `N` = number of poles per wavelength

### Inductrack Lift Force (Post & Ryutov, 2000)

For a Halbach array moving at velocity v over a thin conducting sheet with sheet resistance Σ:

```
Lift pressure = (B₀² / 2μ₀) × (v/vₓ) / √(1 + (v/vₓ)²)
Drag pressure = (B₀² / 2μ₀) × (vₓ/v) / √(1 + (vₓ/v)²)
```

Characteristic velocity: `vₓ = Σ × λ / (2π)`  
Where `Σ = ρ/d` (track sheet resistance, Ω/sq), ρ = resistivity, d = track thickness.

For aluminium track (ρ = 2.65×10⁻⁸ Ω·m, d = 6 mm):
- Σ ≈ 4.4×10⁻⁶ Ω/sq
- vₓ ≈ 2.8 m/s for λ = 200 mm

## Stability Mathematics

The passive Halbach system has a **negative vertical stiffness** (destabilising): increasing the gap reduces lift, which further reduces lift. Active stabilisation corrects this via Hall sensor feedback + correction coils.

Linearised gap error dynamics:

```
m × z̈ + c_active × ż + k_magnet × z = F_disturbance
```

Where:
- `k_magnet = ∂L/∂z` < 0 (destabilising magnetic spring)
- `c_active` = active damping from correction coils (must be > 0)

PID stability criterion (simplified): Kp > |k_magnet|/m × τ  
where τ is the sensor + actuator delay.

## Experimental Validation Methods

1. Measure B field vs. gap with a Gaussmeter; compare to `B₀ exp(−kz)`.
2. Mount array on spring scale; drive over aluminium track at known speeds.
3. Record lift force vs. speed; fit to Inductrack model.
4. Measure power consumption of correction coils at various gap setpoints.
5. Perform step-response test: perturb gap by ±20 mm; measure settling time.
