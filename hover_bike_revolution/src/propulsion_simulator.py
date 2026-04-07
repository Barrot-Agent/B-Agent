"""
propulsion_simulator.py - Multi-Propulsion System Modelling & Analysis

Simulates and compares magnetic linear motor, hub motor, and
electromagnetic pulse drive propulsion for the hover bike.
"""

import math
from dataclasses import dataclass


G = 9.81
RHO_AIR = 1.225  # kg/m³ at sea level


# ---------------------------------------------------------------------------
# Aerodynamics helper
# ---------------------------------------------------------------------------

def aero_drag(speed_ms: float, Cd: float = 0.30,
              frontal_area_m2: float = 0.70) -> float:
    """Aerodynamic drag force [N]."""
    return 0.5 * RHO_AIR * Cd * frontal_area_m2 * speed_ms ** 2


def rolling_resistance(mass_kg: float, Crr: float = 0.005) -> float:
    """Rolling/hovering resistance [N] (small for hover bike)."""
    return Crr * mass_kg * G


# ---------------------------------------------------------------------------
# Hub motor model
# ---------------------------------------------------------------------------

@dataclass
class HubMotor:
    rated_power_w: float = 500.0
    rated_voltage_v: float = 48.0
    kv_rpm_per_volt: float = 50.0
    efficiency: float = 0.87
    pole_pairs: int = 15
    wheel_diameter_mm: float = 550.0

    @property
    def no_load_rpm(self) -> float:
        return self.kv_rpm_per_volt * self.rated_voltage_v

    @property
    def wheel_circumference_m(self) -> float:
        return math.pi * self.wheel_diameter_mm / 1000

    def speed_at_rpm(self, rpm: float) -> float:
        """Linear speed [m/s] for given motor RPM."""
        return rpm * self.wheel_circumference_m / 60

    def thrust_at_speed(self, speed_ms: float, throttle: float = 1.0) -> float:
        """Thrust force [N] at given speed and throttle [0-1]."""
        rpm = min(self.no_load_rpm * throttle,
                  speed_ms * 60 / self.wheel_circumference_m + 10)
        power_mech = self.rated_power_w * throttle * self.efficiency
        if speed_ms < 0.1:
            return power_mech / 1.0
        return power_mech / speed_ms

    def electrical_power(self, thrust_n: float, speed_ms: float) -> float:
        """Electrical power consumed [W]."""
        mech_power = thrust_n * speed_ms
        return mech_power / self.efficiency


# ---------------------------------------------------------------------------
# Linear motor (primary magnetic propulsion)
# ---------------------------------------------------------------------------

@dataclass
class LinearMotor:
    pole_pitch_m: float = 0.05
    air_gap_flux_t: float = 0.8
    pole_area_m2: float = 0.004
    efficiency: float = 0.88

    def thrust_force(self, current_a: float, power_factor: float = 0.9) -> float:
        """
        Thrust: F = (3/2)·(π/τ)·B²·A·I·cos(φ)
        """
        return (1.5 * (math.pi / self.pole_pitch_m)
                * self.air_gap_flux_t ** 2
                * self.pole_area_m2
                * current_a
                * power_factor)

    def current_for_thrust(self, thrust_n: float,
                           power_factor: float = 0.9) -> float:
        """Inverse of thrust_force."""
        denom = (1.5 * (math.pi / self.pole_pitch_m)
                 * self.air_gap_flux_t ** 2
                 * self.pole_area_m2
                 * power_factor)
        return thrust_n / denom

    def power_for_thrust(self, thrust_n: float, speed_ms: float) -> float:
        """Electrical power [W] for given thrust at given speed."""
        mech_power = thrust_n * speed_ms
        return mech_power / self.efficiency


# ---------------------------------------------------------------------------
# Electromagnetic pulse drive
# ---------------------------------------------------------------------------

@dataclass
class EMPulseDrive:
    capacitance_f: float = 1.0       # Supercapacitor bank [F]
    charge_voltage_v: float = 48.0   # Charge voltage
    coil_inductance_h: float = 0.005 # 5 mH coil
    coil_resistance_ohm: float = 0.2

    @property
    def stored_energy_j(self) -> float:
        """E = ½CV² [J]."""
        return 0.5 * self.capacitance_f * self.charge_voltage_v ** 2

    def peak_current_a(self) -> float:
        """Peak discharge current through coil."""
        return self.charge_voltage_v / self.coil_resistance_ohm

    def pulse_thrust_n(self, projectile_mass_kg: float = 0.01,
                       coil_length_m: float = 0.1) -> float:
        """Estimate impulse-based thrust from a single EM pulse."""
        I_peak = self.peak_current_a()
        B_coil = (4e-7 * math.pi * I_peak / (2 * coil_length_m))
        force = I_peak * B_coil * coil_length_m
        return force

    def pulse_frequency_hz(self, charge_time_s: float = 1.0) -> float:
        """Maximum pulse repetition rate."""
        return 1.0 / charge_time_s

    def average_thrust_n(self, pulse_force_n: float,
                         freq_hz: float, impulse_duration_s: float = 0.005) -> float:
        """Average thrust = F_pulse × duty_cycle."""
        return pulse_force_n * freq_hz * impulse_duration_s


# ---------------------------------------------------------------------------
# Propulsion comparison and simulation
# ---------------------------------------------------------------------------

def simulate_acceleration_run(
        mass_kg: float = 90.0,
        target_speed_kmh: float = 50.0,
        hub_motor: HubMotor | None = None,
        linear_motor: LinearMotor | None = None,
        dt: float = 0.1,
        max_time_s: float = 60.0) -> dict:
    """
    Simulate 0 → target_speed with given propulsion system.
    Returns time-history and performance metrics.
    """
    if hub_motor is None:
        hub_motor = HubMotor()
    if linear_motor is None:
        linear_motor = LinearMotor()

    v = 0.0
    t = 0.0
    energy_wh = 0.0
    history = []
    target_ms = target_speed_kmh / 3.6

    while v < target_ms and t < max_time_s:
        drag = aero_drag(v)
        crr = rolling_resistance(mass_kg)
        resistance = drag + crr

        # Combined thrust (hub + linear motor)
        thrust_hub = hub_motor.thrust_at_speed(v, throttle=1.0)
        thrust_linear = linear_motor.thrust_force(current_a=20.0)
        thrust_total = thrust_hub + thrust_linear
        thrust_net = max(0.0, thrust_total - resistance)

        acceleration = thrust_net / mass_kg
        v = min(v + acceleration * dt, target_ms)
        t += dt

        p_hub = hub_motor.electrical_power(thrust_hub, max(v, 0.1))
        p_lin = linear_motor.power_for_thrust(thrust_linear, max(v, 0.1))
        p_total = p_hub + p_lin
        energy_wh += p_total * dt / 3600

        if len(history) % 10 == 0:
            history.append({
                "time_s": round(t, 1),
                "speed_kmh": round(v * 3.6, 1),
                "acceleration_ms2": round(acceleration, 3),
                "thrust_n": round(thrust_total, 1),
                "power_w": round(p_total, 1),
            })

    return {
        "time_to_target_s": round(t, 2),
        "target_speed_kmh": target_speed_kmh,
        "energy_used_wh": round(energy_wh, 3),
        "mass_kg": mass_kg,
        "history": history,
    }


def cruise_power_analysis(mass_kg: float = 90.0) -> dict:
    """Steady-state power analysis at various cruise speeds."""
    hub_motor = HubMotor()
    linear_motor = LinearMotor()
    results = []

    for speed_kmh in [10, 20, 30, 40, 50, 55]:
        speed_ms = speed_kmh / 3.6
        drag = aero_drag(speed_ms)
        crr = rolling_resistance(mass_kg)
        total_resistance = drag + crr

        # At cruise: thrust = resistance
        p_hub = hub_motor.electrical_power(total_resistance * 0.6, speed_ms)
        p_lin = linear_motor.power_for_thrust(total_resistance * 0.4, speed_ms)
        p_total = p_hub + p_lin
        p_levitation = 80.0  # active stabilisation

        results.append({
            "speed_kmh": speed_kmh,
            "drag_force_n": round(drag, 1),
            "propulsion_power_w": round(p_total, 1),
            "levitation_power_w": p_levitation,
            "total_power_w": round(p_total + p_levitation, 1),
            "efficiency_pct": round(100 * total_resistance * speed_ms / p_total, 1),
        })
    return results


def run_propulsion_analysis() -> dict:
    """Complete propulsion system analysis."""
    print("=" * 55)
    print("BARROT HOVER BIKE — PROPULSION ANALYSIS")
    print("=" * 55)

    hub = HubMotor()
    linear = LinearMotor()
    em_pulse = EMPulseDrive()

    print(f"\nHub Motor Profile:")
    print(f"  Rated power:    {hub.rated_power_w}W")
    print(f"  Efficiency:     {hub.efficiency*100:.0f}%")
    print(f"  No-load RPM:    {hub.no_load_rpm:.0f}")

    print(f"\nLinear Motor Profile:")
    I_for_50N = linear.current_for_thrust(50.0)
    print(f"  Thrust @ 20A:   {linear.thrust_force(20.0):.1f} N")
    print(f"  Current for 50N:{I_for_50N:.1f} A")
    print(f"  Efficiency:     {linear.efficiency*100:.0f}%")

    print(f"\nEM Pulse Drive Profile:")
    print(f"  Stored energy:  {em_pulse.stored_energy_j:.1f} J")
    print(f"  Peak current:   {em_pulse.peak_current_a():.0f} A")
    pulse_force = em_pulse.pulse_thrust_n()
    avg_thrust = em_pulse.average_thrust_n(pulse_force, 0.5)
    print(f"  Pulse force:    {pulse_force:.1f} N")
    print(f"  Avg thrust @0.5Hz: {avg_thrust:.2f} N")

    print(f"\nCruise Power Analysis:")
    cruise = cruise_power_analysis()
    print(f"  {'Speed':>6} | {'Drag':>6} | {'Prop':>6} | {'Lev':>5} | {'Total':>6}")
    print(f"  {'-'*45}")
    for r in cruise:
        print(f"  {r['speed_kmh']:>5}km/h | {r['drag_force_n']:>5}N | "
              f"{r['propulsion_power_w']:>5}W | {r['levitation_power_w']:>4}W | "
              f"{r['total_power_w']:>5}W")

    print(f"\nAcceleration Simulation (0→50 km/h, 90kg rider):")
    accel = simulate_acceleration_run(90.0, 50.0)
    print(f"  Time to 50 km/h: {accel['time_to_target_s']:.1f}s")
    print(f"  Energy used:     {accel['energy_used_wh']:.3f} Wh")

    return {
        "hub_motor": {
            "rated_power_w": hub.rated_power_w,
            "efficiency": hub.efficiency,
            "no_load_rpm": hub.no_load_rpm,
        },
        "linear_motor": {
            "thrust_at_20a_n": linear.thrust_force(20.0),
            "efficiency": linear.efficiency,
        },
        "em_pulse": {
            "stored_energy_j": em_pulse.stored_energy_j,
            "avg_thrust_n": avg_thrust,
        },
        "cruise_analysis": cruise,
        "acceleration": {
            "time_0_to_50_kmh_s": accel["time_to_target_s"],
            "energy_used_wh": accel["energy_used_wh"],
        },
    }


if __name__ == "__main__":
    import json
    from pathlib import Path
    results = run_propulsion_analysis()
    out = Path(__file__).parent.parent / "models" / "propulsion_analysis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved → {out}")
