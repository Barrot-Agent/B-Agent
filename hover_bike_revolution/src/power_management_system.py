"""
power_management_system.py - Energy System Optimisation & Power Distribution

Models battery performance, solar integration, kinetic recovery,
and real-time power distribution for the hover bike.
"""

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Battery model
# ---------------------------------------------------------------------------

@dataclass
class LiPoCell:
    nominal_voltage_v: float = 48.0
    capacity_ah: float = 10.0
    internal_resistance_mohm: float = 30.0
    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.97
    max_discharge_rate_c: float = 10.0
    max_charge_rate_c: float = 1.0
    cycle_life: int = 800
    soc: float = 1.0

    @property
    def capacity_wh(self) -> float:
        return self.nominal_voltage_v * self.capacity_ah

    @property
    def max_discharge_current_a(self) -> float:
        return self.capacity_ah * self.max_discharge_rate_c

    @property
    def max_charge_current_a(self) -> float:
        return self.capacity_ah * self.max_charge_rate_c

    def voltage_at_soc(self) -> float:
        return self.nominal_voltage_v * (0.85 + 0.15 * self.soc)

    def available_energy_wh(self) -> float:
        usable_soc = max(0.0, self.soc - 0.20)
        return usable_soc * self.capacity_wh

    def discharge(self, power_w: float, dt_s: float) -> float:
        current = power_w / max(self.voltage_at_soc(), 0.1)
        if current > self.max_discharge_current_a:
            current = self.max_discharge_current_a
        energy_wh = current * self.voltage_at_soc() * dt_s / 3600
        self.soc = max(0.0, self.soc - energy_wh / self.capacity_wh)
        return current * self.voltage_at_soc()

    def charge(self, power_w: float, dt_s: float):
        current = power_w / max(self.voltage_at_soc(), 0.1)
        current = min(current, self.max_charge_current_a)
        energy_wh = (current * self.voltage_at_soc()
                     * dt_s / 3600 * self.charge_efficiency)
        self.soc = min(1.0, self.soc + energy_wh / self.capacity_wh)

    def time_to_empty_h(self, power_w: float) -> float:
        return self.available_energy_wh() / max(power_w, 0.1)

    def range_km(self, power_w: float, speed_kmh: float) -> float:
        return self.time_to_empty_h(power_w) * speed_kmh


# ---------------------------------------------------------------------------
# Solar panel model
# ---------------------------------------------------------------------------

@dataclass
class SolarPanel:
    area_m2: float = 0.5
    efficiency: float = 0.22
    temperature_coefficient: float = -0.004
    stc_irradiance_w_m2: float = 1000.0

    def output_power_w(self, irradiance_w_m2: float = 800.0,
                       temperature_c: float = 25.0) -> float:
        t_correction = 1 + self.temperature_coefficient * (temperature_c - 25)
        return self.area_m2 * self.efficiency * irradiance_w_m2 * t_correction

    def daily_energy_wh(self, peak_sun_hours: float = 5.0) -> float:
        return self.output_power_w() * peak_sun_hours


# ---------------------------------------------------------------------------
# Kinetic energy recovery
# ---------------------------------------------------------------------------

class KineticEnergyRecovery:
    def __init__(self, efficiency: float = 0.70):
        self.efficiency = efficiency

    def braking_energy_j(self, mass_kg: float, v_initial_ms: float,
                         v_final_ms: float = 0.0) -> float:
        return 0.5 * mass_kg * (v_initial_ms ** 2 - v_final_ms ** 2)

    def recovered_energy_j(self, mass_kg: float, v_initial_ms: float,
                           v_final_ms: float = 0.0) -> float:
        return (self.braking_energy_j(mass_kg, v_initial_ms, v_final_ms)
                * self.efficiency)

    def recovered_energy_wh(self, mass_kg: float, v_initial_ms: float,
                            v_final_ms: float = 0.0) -> float:
        return self.recovered_energy_j(mass_kg, v_initial_ms, v_final_ms) / 3600


# ---------------------------------------------------------------------------
# Supercapacitor buffer
# ---------------------------------------------------------------------------

@dataclass
class SupercapacitorBank:
    capacitance_f: float = 100.0
    max_voltage_v: float = 16.0
    esr_mohm: float = 5.0
    voltage: float = 16.0

    @property
    def stored_energy_j(self) -> float:
        return 0.5 * self.capacitance_f * self.voltage ** 2

    def discharge_pulse(self, power_w: float, dt_s: float) -> float:
        current = power_w / max(self.voltage, 0.1)
        dv = current * dt_s / self.capacitance_f
        v_new = max(0.0, self.voltage - dv)
        energy = 0.5 * self.capacitance_f * (self.voltage ** 2 - v_new ** 2)
        self.voltage = v_new
        return energy

    def charge_from_regen(self, power_w: float, dt_s: float):
        current = power_w / max(self.voltage, 0.1)
        dv = current * dt_s / self.capacitance_f
        self.voltage = min(self.max_voltage_v, self.voltage + dv)


# ---------------------------------------------------------------------------
# Power management controller
# ---------------------------------------------------------------------------

class PowerManagementController:
    STATES = ["IDLE", "CRUISE", "ACCELERATING", "BRAKING", "SOLAR_CHARGING"]

    def __init__(self, battery: LiPoCell | None = None,
                 solar: SolarPanel | None = None,
                 supercap: SupercapacitorBank | None = None):
        self.battery = battery or LiPoCell()
        self.solar = solar or SolarPanel()
        self.supercap = supercap or SupercapacitorBank()
        self.ker = KineticEnergyRecovery()
        self.state = "IDLE"
        self.total_energy_used_wh = 0.0
        self.total_regen_wh = 0.0

    def update(self, propulsion_demand_w: float, levitation_demand_w: float,
               braking: bool = False, irradiance_w_m2: float = 0.0,
               dt_s: float = 0.1) -> dict:
        total_load_w = propulsion_demand_w + levitation_demand_w
        solar_power = self.solar.output_power_w(irradiance_w_m2)

        if braking:
            self.state = "BRAKING"
            regen_power = propulsion_demand_w * 0.7
            self.battery.charge(regen_power, dt_s)
            self.supercap.charge_from_regen(regen_power * 0.3, dt_s)
            regen_wh = regen_power * dt_s / 3600
            self.total_regen_wh += regen_wh
            return {"state": self.state,
                    "regen_power_w": round(regen_power, 1),
                    "battery_soc": round(self.battery.soc, 3)}

        self.state = ("ACCELERATING" if propulsion_demand_w > 350
                      else "CRUISE" if propulsion_demand_w > 50
                      else "IDLE")
        net_load = max(0.0, total_load_w - solar_power)

        if propulsion_demand_w > 500 and self.supercap.voltage > 8:
            supercap_energy = self.supercap.discharge_pulse(200.0, dt_s)
            net_load -= supercap_energy / dt_s

        actual_power = self.battery.discharge(net_load, dt_s)
        self.total_energy_used_wh += actual_power * dt_s / 3600
        return {
            "state": self.state,
            "total_load_w": round(total_load_w, 1),
            "solar_w": round(solar_power, 1),
            "battery_w": round(net_load, 1),
            "battery_soc": round(self.battery.soc, 3),
            "supercap_v": round(self.supercap.voltage, 1),
        }

    def estimate_range(self, avg_speed_kmh: float = 40.0,
                       avg_power_w: float = 450.0) -> dict:
        range_km = self.battery.range_km(avg_power_w, avg_speed_kmh)
        solar_boost_kmh = (self.solar.output_power_w(600) / avg_power_w
                           * avg_speed_kmh)
        return {
            "battery_range_km": round(range_km, 1),
            "solar_boost_kmh": round(solar_boost_kmh, 1),
            "total_estimated_km": round(range_km + solar_boost_kmh * 0.2, 1),
            "battery_soc_pct": round(self.battery.soc * 100, 1),
        }


def run_power_analysis() -> dict:
    """Complete power system analysis."""
    print("=" * 55)
    print("BARROT HOVER BIKE — POWER MANAGEMENT ANALYSIS")
    print("=" * 55)

    battery = LiPoCell()
    solar = SolarPanel()
    ker = KineticEnergyRecovery()

    print(f"\nBattery Specification:")
    print(f"  Capacity:        {battery.capacity_wh:.0f} Wh")
    print(f"  Max discharge:   {battery.max_discharge_current_a:.0f} A")
    print(f"  Cycle life:      {battery.cycle_life} cycles")

    print(f"\nSolar Panel:")
    print(f"  Peak output:     {solar.output_power_w(1000):.0f} W")
    print(f"  Daily yield:     {solar.daily_energy_wh():.0f} Wh (5h sun)")

    print(f"\nKinetic Recovery (50→0 km/h, 90kg):")
    e_recovered = ker.recovered_energy_wh(90.0, 50.0 / 3.6)
    print(f"  Per stop:        {e_recovered:.3f} Wh")
    print(f"  10 stops/trip:   {e_recovered*10:.2f} Wh")

    print(f"\nRange Estimates (full charge):")
    for speed, power in [(30, 320), (40, 430), (50, 560)]:
        r = battery.range_km(power, speed)
        boost = solar.output_power_w(600) / power * speed * 0.2
        print(f"  {speed}km/h ({power}W): {r:.1f}km battery + {boost:.1f}km solar")

    print(f"\nSimulating 15-minute cruise cycle...")
    pmc = PowerManagementController(LiPoCell(soc=1.0))
    for step in range(900):
        irr = 600.0 if 300 < step < 600 else 0.0
        pmc.update(350.0, 80.0, irradiance_w_m2=irr, dt_s=1.0)
    est = pmc.estimate_range()
    print(f"  After 15min: SOC={est['battery_soc_pct']}%, "
          f"Range={est['total_estimated_km']}km")

    return {
        "battery": {"capacity_wh": battery.capacity_wh,
                    "cycle_life": battery.cycle_life},
        "solar": {"peak_power_w": solar.output_power_w(1000),
                  "daily_yield_wh": solar.daily_energy_wh()},
        "kinetic_recovery": {"per_stop_wh": e_recovered,
                             "efficiency_pct": ker.efficiency * 100},
        "range_estimates": {
            "30kmh_km": battery.range_km(320, 30),
            "40kmh_km": battery.range_km(430, 40),
            "50kmh_km": battery.range_km(560, 50),
        },
    }


if __name__ == "__main__":
    import json
    from pathlib import Path
    results = run_power_analysis()
    out = Path(__file__).parent.parent / "models" / "power_analysis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved → {out}")
