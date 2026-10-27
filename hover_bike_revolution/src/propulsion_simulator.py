"""
propulsion_simulator.py — Multi-propulsion system modelling for the hover bike.

Simulates BLDC hub motor performance, electromagnetic pulse drive dynamics,
and optional ion thruster auxiliary thrust.  All calculations use SI units
internally.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

GRAVITY = 9.81  # m/s²
AIR_DENSITY = 1.225  # kg/m³ (sea level, 15 °C)


# ---------------------------------------------------------------------------
# BLDC Hub Motor model
# ---------------------------------------------------------------------------


@dataclass
class BLDCMotor:
    """
    Brushless DC hub-motor model.

    Parameters
    ----------
    rated_power_w:
        Rated continuous power output (W).
    peak_power_w:
        Short-term peak power (W).
    kv_rpm_per_v:
        Motor speed constant (RPM/V, unloaded).
    winding_resistance_ohm:
        Phase resistance R (Ω).
    efficiency_percent:
        Peak efficiency at rated operating point.
    wheel_radius_m:
        Effective wheel radius for speed/torque calculations (m).
    n_motors:
        Number of identical motors in the drivetrain.
    """

    rated_power_w: float = 750.0
    peak_power_w: float = 1_500.0
    kv_rpm_per_v: float = 50.0
    winding_resistance_ohm: float = 0.15
    efficiency_percent: float = 88.0
    wheel_radius_m: float = 0.20
    n_motors: int = 2

    # ------------------------------------------------------------------
    # Derived quantities
    # ------------------------------------------------------------------

    @property
    def rated_torque_nm(self) -> float:
        """Torque at rated power and rated no-load speed at 48 V."""
        omega = self._omega_at_voltage(48.0)
        if omega == 0:
            return 0.0
        return (self.rated_power_w * self.efficiency_percent / 100) / omega

    @property
    def total_rated_power_w(self) -> float:
        return self.rated_power_w * self.n_motors

    def _omega_at_voltage(self, voltage_v: float) -> float:
        """Angular velocity (rad/s) at the given supply voltage (no-load)."""
        rpm = self.kv_rpm_per_v * voltage_v
        return rpm * 2 * math.pi / 60

    def torque_at_current(self, current_a: float, kt_nm_per_a: float | None = None) -> float:
        """
        Motor torque from current.  Kt is derived from Kv if not provided:
            Kt = 1 / (Kv × 2π/60)
        """
        if kt_nm_per_a is None:
            kt_nm_per_a = 1.0 / (self.kv_rpm_per_v * 2 * math.pi / 60)
        return current_a * kt_nm_per_a

    def speed_ms_at_power(self, power_w: float, voltage_v: float = 48.0) -> float:
        """
        Translational wheel speed (m/s) for a given electrical input power
        at the wheel rim.
        """
        if power_w <= 0:
            return 0.0
        mech_power = power_w * self.efficiency_percent / 100
        omega = self._omega_at_voltage(voltage_v)
        if omega == 0:
            return 0.0
        tangential_speed = omega * self.wheel_radius_m
        return min(tangential_speed, math.sqrt(2 * mech_power / (AIR_DENSITY * 0.5)))

    def acceleration(
        self,
        total_mass_kg: float,
        throttle_frac: float = 1.0,
        rolling_resistance: float = 0.02,
    ) -> float:
        """
        Translational acceleration (m/s²) at the given throttle fraction.
        """
        force_n = (
            self.total_rated_power_w
            * throttle_frac
            * self.efficiency_percent
            / 100
            / max(self._omega_at_voltage(48.0) * self.wheel_radius_m, 0.1)
        )
        drag_n = rolling_resistance * total_mass_kg * GRAVITY
        net_force = max(force_n - drag_n, 0.0)
        return net_force / total_mass_kg

    def time_to_speed(
        self,
        target_speed_ms: float,
        total_mass_kg: float,
        throttle_frac: float = 1.0,
        rolling_resistance: float = 0.02,
        dt: float = 0.1,
    ) -> float:
        """
        Simulate time (s) to reach *target_speed_ms* using an Euler integration.
        """
        v = 0.0
        t = 0.0
        max_iter = 10_000
        for _ in range(max_iter):
            if v >= target_speed_ms:
                break
            a = self.acceleration(total_mass_kg, throttle_frac, rolling_resistance)
            v += a * dt
            t += dt
        return t

    def regenerative_power_w(
        self,
        speed_ms: float,
        braking_deceleration_ms2: float = 1.5,
        total_mass_kg: float = 120.0,
    ) -> float:
        """
        Estimated electrical power recovered during regenerative braking (W).
        """
        braking_force_n = total_mass_kg * braking_deceleration_ms2
        mech_power = braking_force_n * speed_ms
        return mech_power * self.efficiency_percent / 100


# ---------------------------------------------------------------------------
# Electromagnetic pulse drive
# ---------------------------------------------------------------------------


@dataclass
class EMPulseDrive:
    """
    Electromagnetic pulse drive using supercapacitor-powered coil pulses
    for burst acceleration.

    The drive works by discharging a supercapacitor bank through an
    electromagnet coil array, inducing a repulsive/attractive interaction
    with the magnet array below the bike frame.  This provides forward
    impulse without a rotating component.

    Parameters
    ----------
    capacitance_f:
        Total supercapacitor capacitance (F).
    charge_voltage_v:
        Capacitor bank charge voltage (V).
    coil_inductance_h:
        Pulse coil inductance (H).
    coil_resistance_ohm:
        Coil resistance (Ω).
    pulse_frequency_hz:
        Pulse repetition frequency (Hz).
    """

    capacitance_f: float = 0.1  # 100 mF supercapacitor
    charge_voltage_v: float = 48.0
    coil_inductance_h: float = 0.005  # 5 mH
    coil_resistance_ohm: float = 0.5
    pulse_frequency_hz: float = 20.0
    magnetic_coupling_factor: float = 0.15  # fraction of pulse energy → thrust

    @property
    def stored_energy_j(self) -> float:
        """Energy stored in the capacitor bank (J)."""
        return 0.5 * self.capacitance_f * self.charge_voltage_v**2

    @property
    def peak_current_a(self) -> float:
        """Peak discharge current (A) — LC circuit resonance."""
        omega = 1.0 / math.sqrt(self.coil_inductance_h * self.capacitance_f)
        return self.charge_voltage_v / (self.coil_resistance_ohm + omega * self.coil_inductance_h)

    # Effective magnetic coupling travel distance for pulse force estimate (m)
    _EFFECTIVE_TRAVEL_M: float = 0.10  # 10 cm — typical magnet interaction range

    @property
    def peak_force_n(self) -> float:
        """
        Peak thrust force per pulse (N) — simplified impulse approximation.
        Actual force depends on field geometry; this is an order-of-magnitude estimate.
        The effective travel distance (10 cm) represents the axial range over which
        the magnetic field does useful work during a pulse discharge.
        """
        energy_to_thrust = self.stored_energy_j * self.magnetic_coupling_factor
        pulse_duration_s = 1.0 / (2 * self.pulse_frequency_hz)
        return energy_to_thrust / (pulse_duration_s * self._EFFECTIVE_TRAVEL_M)

    @property
    def average_thrust_n(self) -> float:
        """Average thrust (N) = peak force × duty cycle."""
        duty = 0.05  # 5 % duty cycle
        return self.peak_force_n * duty

    @property
    def average_power_draw_w(self) -> float:
        """Average electrical power consumed by the pulse drive (W)."""
        return self.stored_energy_j * self.pulse_frequency_hz


# ---------------------------------------------------------------------------
# Ion thruster auxiliary model (optional / experimental)
# ---------------------------------------------------------------------------


@dataclass
class IonThruster:
    """
    Simplified gridded ion thruster model for auxiliary thrust.

    Realistic for very low-mass auxiliary propulsion; not a primary driver.
    Xenon or argon propellant, electrostatic acceleration.

    Parameters
    ----------
    discharge_power_w:
        Electrical power to the discharge chamber (W).
    beam_voltage_v:
        Ion acceleration voltage (V).
    propellant:
        Propellant gas name.
    specific_impulse_s:
        Isp of the thruster (s).  Typical gridded ion: 1500–10 000 s.
    """

    discharge_power_w: float = 200.0
    beam_voltage_v: float = 1_200.0
    propellant: str = "Argon"
    specific_impulse_s: float = 3_000.0
    total_efficiency: float = 0.65

    @property
    def exhaust_velocity_ms(self) -> float:
        return self.specific_impulse_s * GRAVITY

    @property
    def thrust_n(self) -> float:
        """
        Thrust (N) from power-thrust relationship:
            T = sqrt(2 × P × η × m_dot × v_e) = 2 × P × η / v_e
        (using P = 0.5 × m_dot × v_e², T = m_dot × v_e)
        """
        return 2.0 * self.discharge_power_w * self.total_efficiency / self.exhaust_velocity_ms

    @property
    def thrust_to_power_n_per_kw(self) -> float:
        return (self.thrust_n / self.discharge_power_w) * 1000.0

    def propellant_consumption_g_per_h(self) -> float:
        """Mass flow rate of propellant (g/h)."""
        m_dot_kg_s = self.thrust_n / self.exhaust_velocity_ms
        return m_dot_kg_s * 3600 * 1000


# ---------------------------------------------------------------------------
# Multi-propulsion system analyser
# ---------------------------------------------------------------------------


@dataclass
class PropulsionSystem:
    """
    Combines all propulsion subsystems and reports total performance metrics.
    """

    bldc: BLDCMotor = field(default_factory=BLDCMotor)
    em_pulse: EMPulseDrive = field(default_factory=EMPulseDrive)
    ion: IonThruster | None = None  # optional experimental system
    total_mass_kg: float = 120.0
    drag_coefficient: float = 0.35
    frontal_area_m2: float = 0.60

    def aerodynamic_drag_n(self, speed_ms: float) -> float:
        """Aerodynamic drag force (N) at the given speed."""
        return 0.5 * AIR_DENSITY * self.drag_coefficient * self.frontal_area_m2 * speed_ms**2

    def total_thrust_n(self, throttle_frac: float = 1.0) -> float:
        """
        Combined thrust from all active propulsion systems (N).
        """
        thrust = self.bldc.acceleration(self.total_mass_kg, throttle_frac) * self.total_mass_kg
        thrust += self.em_pulse.average_thrust_n
        if self.ion is not None:
            thrust += self.ion.thrust_n
        return thrust

    def max_speed_ms(self, throttle_frac: float = 1.0) -> float:
        """
        Terminal velocity (m/s): solve thrust = drag iteratively.
        """
        v = 0.1
        for _ in range(10_000):
            drag = self.aerodynamic_drag_n(v)
            thrust = self.total_thrust_n(throttle_frac)
            if drag >= thrust:
                break
            v += 0.05
        return v

    def performance_report(self) -> dict[str, Any]:
        return {
            "bldc_motors": {
                "count": self.bldc.n_motors,
                "rated_power_w": self.bldc.rated_power_w,
                "peak_power_w": self.bldc.peak_power_w,
                "rated_torque_nm": self.bldc.rated_torque_nm,
                "total_rated_power_w": self.bldc.total_rated_power_w,
                "0_to_30kmh_s": self.bldc.time_to_speed(30 / 3.6, self.total_mass_kg),
                "regen_at_30kmh_w": self.bldc.regenerative_power_w(30 / 3.6),
            },
            "em_pulse_drive": {
                "stored_energy_j": self.em_pulse.stored_energy_j,
                "peak_current_a": self.em_pulse.peak_current_a,
                "average_thrust_n": self.em_pulse.average_thrust_n,
                "average_power_draw_w": self.em_pulse.average_power_draw_w,
            },
            "ion_thruster": (
                {
                    "thrust_n": self.ion.thrust_n,
                    "specific_impulse_s": self.ion.specific_impulse_s,
                    "thrust_to_power_n_kw": self.ion.thrust_to_power_n_per_kw,
                    "propellant_g_per_h": self.ion.propellant_consumption_g_per_h(),
                }
                if self.ion
                else "not installed"
            ),
            "system": {
                "total_mass_kg": self.total_mass_kg,
                "max_speed_kmh": self.max_speed_ms() * 3.6,
                "aerodynamic_drag_at_30kmh_n": self.aerodynamic_drag_n(30 / 3.6),
            },
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    system = PropulsionSystem(ion=IonThruster())
    report = system.performance_report()
    print(json.dumps(report, indent=2))
