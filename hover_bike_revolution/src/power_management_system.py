"""
power_management_system.py — Energy system optimisation for the hover bike.

Models battery performance, solar integration, kinetic energy recovery,
and real-time power distribution.  All calculations use SI units.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Battery model (LiFePO4)
# ---------------------------------------------------------------------------


@dataclass
class BatteryPack:
    """
    LiFePO4 battery pack model.

    Parameters
    ----------
    capacity_wh:
        Nominal capacity in watt-hours.
    nominal_voltage_v:
        Pack nominal voltage (V).
    max_charge_rate_c:
        Maximum charge rate in C (e.g. 0.5 C = half capacity per hour).
    max_discharge_rate_c:
        Maximum continuous discharge rate in C.
    internal_resistance_mohm:
        Cell internal resistance per cell (mΩ).
    series_cells:
        Number of cells in series.
    parallel_cells:
        Number of parallel cell strings.
    cell_nominal_v:
        Nominal voltage of a single cell (V).  LiFePO4 ≈ 3.2 V.
    cell_capacity_ah:
        Capacity of a single cell (Ah).
    cycle_life:
        Expected full-cycle life.
    """

    capacity_wh: float = 1_000.0
    nominal_voltage_v: float = 48.0
    max_charge_rate_c: float = 0.5
    max_discharge_rate_c: float = 3.0
    internal_resistance_mohm: float = 8.0  # per cell
    series_cells: int = 15  # 15S ≈ 48 V nominal
    parallel_cells: int = 4
    cell_nominal_v: float = 3.2
    cell_capacity_ah: float = 20.0  # 20 Ah LiFePO4 prismatic
    cycle_life: int = 3_000

    @property
    def capacity_ah(self) -> float:
        return self.capacity_wh / self.nominal_voltage_v

    @property
    def max_charge_current_a(self) -> float:
        return self.capacity_ah * self.max_charge_rate_c

    @property
    def max_discharge_current_a(self) -> float:
        return self.capacity_ah * self.max_discharge_rate_c

    @property
    def pack_mass_kg(self) -> float:
        """Rough mass estimate: ~7 Wh/kg for LiFePO4 pouch cells."""
        return self.capacity_wh / 100.0  # ~100 Wh/kg

    def voltage_at_soc(self, soc: float) -> float:
        """
        Open-circuit voltage as a function of state-of-charge (0..1).
        Simplified linear model between 2.8 V (empty) and 3.65 V (full) per cell.
        """
        soc = max(0.0, min(1.0, soc))
        v_min, v_max = 2.8, 3.65
        cell_v = v_min + (v_max - v_min) * soc
        return cell_v * self.series_cells

    def terminal_voltage(self, current_a: float, soc: float) -> float:
        """Terminal voltage under load (V)."""
        r_pack = (self.internal_resistance_mohm / 1000) * self.series_cells / self.parallel_cells
        return self.voltage_at_soc(soc) - current_a * r_pack

    def capacity_fade_factor(self, cycles: int) -> float:
        """
        Remaining capacity fraction after *cycles* full cycles.
        Uses a simple linear degradation model to 80 % at rated cycle life.
        """
        return max(0.8, 1.0 - 0.20 * cycles / self.cycle_life)

    def range_estimate_km(
        self,
        avg_power_w: float,
        speed_kmh: float,
        soc_start: float = 1.0,
        soc_end: float = 0.20,
    ) -> float:
        """
        Usable range (km) between *soc_start* and *soc_end* at constant power.
        """
        usable_wh = self.capacity_wh * (soc_start - soc_end)
        if avg_power_w <= 0:
            return float("inf")
        hours = usable_wh / avg_power_w
        return hours * speed_kmh


# ---------------------------------------------------------------------------
# Solar integration
# ---------------------------------------------------------------------------


@dataclass
class SolarPanel:
    """
    Thin-film solar panel model for the hover bike canopy.

    Parameters
    ----------
    peak_power_wp:
        Peak power rating (W_p) under standard test conditions (STC).
    panel_area_m2:
        Physical panel area (m²).
    efficiency_percent:
        Panel conversion efficiency (%).
    temperature_coefficient_pct_per_c:
        Power temperature coefficient (% / °C, typically negative for Si).
    mppt_efficiency_percent:
        MPPT charge controller efficiency (%).
    """

    peak_power_wp: float = 150.0
    panel_area_m2: float = 0.32  # ~0.8 × 0.4 m canopy
    efficiency_percent: float = 10.5  # thin-film CIGS ≈ 10–13 %
    temperature_coefficient_pct_per_c: float = -0.30
    mppt_efficiency_percent: float = 96.0

    def power_at_irradiance(
        self,
        irradiance_w_m2: float = 1_000.0,
        panel_temp_c: float = 45.0,
        stc_temp_c: float = 25.0,
    ) -> float:
        """
        Actual power output (W) at given irradiance and cell temperature.
        """
        power_stc = self.peak_power_wp * (irradiance_w_m2 / 1_000.0)
        temp_delta = panel_temp_c - stc_temp_c
        temp_factor = 1 + (self.temperature_coefficient_pct_per_c / 100) * temp_delta
        raw_power = power_stc * temp_factor
        return raw_power * self.mppt_efficiency_percent / 100

    def daily_energy_wh(
        self,
        peak_sun_hours: float = 4.5,
        irradiance_w_m2: float = 800.0,
    ) -> float:
        """
        Estimated daily energy yield (Wh) based on peak sun hours.
        """
        return self.power_at_irradiance(irradiance_w_m2) * peak_sun_hours

    def charge_time_h(
        self,
        battery: BatteryPack,
        current_soc: float = 0.20,
        irradiance_w_m2: float = 800.0,
    ) -> float:
        """
        Time (h) to fully charge *battery* from *current_soc* using solar only.
        """
        needed_wh = battery.capacity_wh * (1 - current_soc)
        solar_power = self.power_at_irradiance(irradiance_w_m2)
        if solar_power <= 0:
            return float("inf")
        return needed_wh / solar_power


# ---------------------------------------------------------------------------
# Kinetic energy recovery
# ---------------------------------------------------------------------------


@dataclass
class KineticRecovery:
    """
    Models regenerative braking and gravity-assist energy recovery.
    """

    motor_efficiency_percent: float = 88.0
    regen_fraction: float = 0.70  # fraction of braking energy captured

    def energy_from_braking(
        self,
        mass_kg: float,
        speed_from_ms: float,
        speed_to_ms: float = 0.0,
    ) -> float:
        """
        Energy recovered (Wh) when slowing from *speed_from_ms* to *speed_to_ms*.
        """
        ke = 0.5 * mass_kg * (speed_from_ms**2 - max(speed_to_ms, 0.0) ** 2)
        if ke <= 0:
            return 0.0
        return ke * self.regen_fraction * (self.motor_efficiency_percent / 100) / 3600

    def energy_from_descent(
        self,
        mass_kg: float,
        height_m: float,
        efficiency: float | None = None,
    ) -> float:
        """
        Energy recovered (Wh) descending *height_m* via regenerative motor.
        """
        eff = efficiency or self.motor_efficiency_percent / 100
        pe = mass_kg * 9.81 * height_m
        return pe * self.regen_fraction * eff / 3600

    def daily_recovery_wh(
        self,
        braking_events: int = 20,
        avg_speed_ms: float = 8.0,
        mass_kg: float = 120.0,
    ) -> float:
        """
        Rough estimate of daily energy recovered from braking events (Wh).
        """
        energy_per_brake = self.energy_from_braking(mass_kg, avg_speed_ms, 0.0)
        return energy_per_brake * braking_events


# ---------------------------------------------------------------------------
# Power distribution controller
# ---------------------------------------------------------------------------


@dataclass
class PowerManagementSystem:
    """
    Integrates battery, solar, kinetic recovery, and load management into
    a unified power model for the hover bike.
    """

    battery: BatteryPack = field(default_factory=BatteryPack)
    solar: SolarPanel = field(default_factory=SolarPanel)
    regen: KineticRecovery = field(default_factory=KineticRecovery)

    # Loads
    maglev_idle_w: float = 75.0  # active stabilisation
    propulsion_cruise_w: float = 270.0  # motors at cruise
    control_electronics_w: float = 15.0
    lighting_w: float = 10.0

    def total_load_w(self) -> float:
        return (
            self.maglev_idle_w
            + self.propulsion_cruise_w
            + self.control_electronics_w
            + self.lighting_w
        )

    def net_power_w(
        self,
        irradiance_w_m2: float = 0.0,
        regen_w: float = 0.0,
    ) -> float:
        """
        Net power draw from battery (W).  Negative means charging.
        """
        sources = self.solar.power_at_irradiance(irradiance_w_m2) + regen_w
        return self.total_load_w() - sources

    def simulation_step(
        self,
        soc: float,
        dt_h: float,
        irradiance_w_m2: float = 0.0,
        regen_w: float = 0.0,
    ) -> tuple[float, float]:
        """
        Advance simulation by *dt_h* hours.

        Returns
        -------
        (new_soc, energy_delta_wh)
        """
        net = self.net_power_w(irradiance_w_m2, regen_w)
        energy_delta_wh = net * dt_h
        delta_soc = energy_delta_wh / self.battery.capacity_wh
        new_soc = max(0.0, min(1.0, soc - delta_soc))
        return new_soc, energy_delta_wh

    def simulate_ride(
        self,
        duration_h: float = 2.0,
        dt_h: float = 1 / 60,  # 1-minute steps
        initial_soc: float = 1.0,
        daytime: bool = False,
        braking_events_per_h: int = 15,
        avg_speed_ms: float = 8.0,
    ) -> dict[str, Any]:
        """
        Simulate an entire ride and return energy accounting.
        """
        soc = initial_soc
        time_h: list[float] = []
        soc_trace: list[float] = []
        irrad = 600.0 if daytime else 0.0
        mass_kg = 120.0

        for step in range(int(duration_h / dt_h)):
            regen_w = (
                self.regen.energy_from_braking(mass_kg, avg_speed_ms)
                / dt_h
                * (braking_events_per_h * dt_h)
            )
            soc, _ = self.simulation_step(soc, dt_h, irrad, regen_w)
            time_h.append(step * dt_h)
            soc_trace.append(soc)
            if soc <= 0.05:
                break

        return {
            "initial_soc": initial_soc,
            "final_soc": soc,
            "consumed_wh": (initial_soc - soc) * self.battery.capacity_wh,
            "duration_simulated_h": time_h[-1] if time_h else 0.0,
            "range_at_speed_km": time_h[-1] * avg_speed_ms * 3.6 if time_h else 0.0,
            "total_load_w": self.total_load_w(),
            "solar_contribution_w": self.solar.power_at_irradiance(irrad) if daytime else 0.0,
            "steps": len(time_h),
        }

    def power_budget_report(self) -> dict[str, Any]:
        """Full power budget summary."""
        return {
            "battery": {
                "capacity_wh": self.battery.capacity_wh,
                "nominal_voltage_v": self.battery.nominal_voltage_v,
                "max_discharge_a": self.battery.max_discharge_current_a,
                "pack_mass_kg": self.battery.pack_mass_kg,
                "cycle_life": self.battery.cycle_life,
                "range_km_cruise": self.battery.range_estimate_km(self.total_load_w(), 30.0),
            },
            "solar": {
                "peak_power_wp": self.solar.peak_power_wp,
                "daily_energy_wh": self.solar.daily_energy_wh(),
                "full_charge_solar_only_h": self.solar.charge_time_h(self.battery),
            },
            "kinetic_recovery": {
                "daily_recovery_wh": self.regen.daily_recovery_wh(),
                "energy_per_brake_wh": self.regen.energy_from_braking(120.0, 8.0),
            },
            "loads_w": {
                "maglev_stabilisation": self.maglev_idle_w,
                "propulsion_cruise": self.propulsion_cruise_w,
                "control_electronics": self.control_electronics_w,
                "lighting": self.lighting_w,
                "total": self.total_load_w(),
            },
            "net_power_daytime_w": self.net_power_w(600.0, 20.0),
            "net_power_night_w": self.net_power_w(0.0, 0.0),
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    pms = PowerManagementSystem()
    print("=== Power Budget Report ===")
    print(json.dumps(pms.power_budget_report(), indent=2))
    print("\n=== Ride Simulation (daytime, 2 h) ===")
    print(json.dumps(pms.simulate_ride(daytime=True), indent=2))
