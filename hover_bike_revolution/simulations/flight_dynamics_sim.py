"""
flight_dynamics_sim.py — 6-DOF hover bike flight dynamics simulation.

Simulates the equations of motion for the hover bike in 3-D space,
including magnetic levitation forces, aerodynamic drag, and propulsion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


GRAVITY = 9.81   # m/s²
AIR_DENSITY = 1.225  # kg/m³


@dataclass
class BikeState:
    """Full 6-DOF rigid body state."""
    # Position (m)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.15  # start at nominal hover height

    # Velocity (m/s)
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

    # Euler angles (rad)
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    # Angular rates (rad/s)
    p: float = 0.0
    q: float = 0.0
    r: float = 0.0

    # Time
    t: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "t": round(self.t, 4),
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "z": round(self.z, 4),
            "vx": round(self.vx, 4),
            "vy": round(self.vy, 4),
            "vz": round(self.vz, 4),
            "roll_deg": round(math.degrees(self.roll), 3),
            "pitch_deg": round(math.degrees(self.pitch), 3),
            "yaw_deg": round(math.degrees(self.yaw), 3),
        }


@dataclass
class BikeParameters:
    """Physical parameters of the hover bike."""
    mass_kg: float = 120.0
    drag_coefficient: float = 0.35
    frontal_area_m2: float = 0.6
    moment_of_inertia_x: float = 25.0  # kg·m²
    moment_of_inertia_y: float = 40.0
    moment_of_inertia_z: float = 15.0
    wheelbase_m: float = 1.1
    magnetic_spring_k: float = 5_000.0   # N/m (vertical magnetic spring stiffness)
    magnetic_damping_c: float = 200.0    # N·s/m


def simulate_flight(
    params: BikeParameters | None = None,
    duration_s: float = 5.0,
    dt: float = 0.005,
    thrust_profile: list[tuple[float, float]] | None = None,
) -> list[dict[str, Any]]:
    """
    Run a simple Euler integration of the hover bike dynamics.

    Parameters
    ----------
    params:
        Bike physical parameters.
    duration_s:
        Simulation duration (s).
    dt:
        Integration time step (s).
    thrust_profile:
        List of (time_s, thrust_N) tuples defining longitudinal thrust over time.

    Returns
    -------
    List of state dictionaries at each time step.
    """
    p = params or BikeParameters()
    state = BikeState()
    records: list[dict[str, Any]] = []

    thrust_events = sorted(thrust_profile or [(0.0, 0.0)], key=lambda e: e[0])

    def get_thrust(t: float) -> float:
        thrust = 0.0
        for t_start, f in thrust_events:
            if t >= t_start:
                thrust = f
        return thrust

    target_z = state.z
    t = 0.0
    step = 0

    while t < duration_s:
        # Aerodynamic drag (x-direction)
        speed = math.sqrt(state.vx**2 + state.vy**2)
        drag = 0.5 * AIR_DENSITY * p.drag_coefficient * p.frontal_area_m2 * speed**2
        drag_x = -math.copysign(drag, state.vx) if state.vx != 0 else 0.0

        # Magnetic levitation force (vertical spring-damper)
        dz = state.z - target_z
        maglev_fz = -p.magnetic_spring_k * dz - p.magnetic_damping_c * state.vz
        gravity_fz = -p.mass_kg * GRAVITY

        # Longitudinal thrust
        thrust = get_thrust(t)
        thrust_x = thrust * math.cos(state.pitch)

        # Net forces
        fx = thrust_x + drag_x
        fz = maglev_fz + gravity_fz + p.mass_kg * GRAVITY  # net levitation

        # Accelerations
        ax = fx / p.mass_kg
        az = fz / p.mass_kg

        # Euler integration
        state.vx += ax * dt
        state.vz += az * dt
        state.x += state.vx * dt
        state.z += state.vz * dt

        # Clamp to ground
        if state.z < 0.0:
            state.z = 0.0
            state.vz = 0.0

        state.t = t
        if step % 10 == 0:  # subsample output
            records.append(state.to_dict())
        t += dt
        step += 1

    return records


if __name__ == "__main__":
    import json

    # Simulate: hover stationary then accelerate at t=1 s
    profile = [(0.0, 0.0), (1.0, 300.0), (4.0, 0.0)]
    states = simulate_flight(duration_s=6.0, thrust_profile=profile)
    print(f"Simulation steps (subsampled): {len(states)}")
    print(f"Final state: {json.dumps(states[-1], indent=2)}")
