"""
control_firmware.py — Hover bike stabilisation controller (Python simulation).

Implements the flight stabilisation algorithms, sensor fusion, PID control loops,
and safety protocols that would be deployed on a Raspberry Pi 4B.

This module is designed for simulation and testing; actual deployment would
compile the control loop into a real-time thread with hard timing guarantees.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Sensor models
# ---------------------------------------------------------------------------


@dataclass
class IMUReading:
    """Inertial measurement unit data packet."""

    roll_rad: float = 0.0  # rotation around X-axis
    pitch_rad: float = 0.0  # rotation around Y-axis
    yaw_rad: float = 0.0  # rotation around Z-axis
    accel_x_ms2: float = 0.0
    accel_y_ms2: float = 0.0
    accel_z_ms2: float = 9.81  # gravity in z-up body frame
    gyro_x_rads: float = 0.0
    gyro_y_rads: float = 0.0
    gyro_z_rads: float = 0.0
    timestamp_s: float = field(default_factory=time.time)


@dataclass
class AltitudeSensors:
    """Altitude measurement from barometer + ultrasonic sensors."""

    baro_altitude_m: float = 0.0
    ultrasonic_front_m: float = 0.15
    ultrasonic_rear_m: float = 0.15
    ultrasonic_left_m: float = 0.15
    ultrasonic_right_m: float = 0.15

    @property
    def avg_gap_m(self) -> float:
        readings = [
            self.ultrasonic_front_m,
            self.ultrasonic_rear_m,
            self.ultrasonic_left_m,
            self.ultrasonic_right_m,
        ]
        return sum(readings) / len(readings)

    @property
    def gap_variance(self) -> float:
        avg = self.avg_gap_m
        readings = [
            self.ultrasonic_front_m,
            self.ultrasonic_rear_m,
            self.ultrasonic_left_m,
            self.ultrasonic_right_m,
        ]
        return sum((r - avg) ** 2 for r in readings) / len(readings)


# ---------------------------------------------------------------------------
# PID controller
# ---------------------------------------------------------------------------


class PIDController:
    """
    Discrete-time PID controller with anti-windup.

    Parameters
    ----------
    kp, ki, kd:
        Proportional, integral, derivative gains.
    setpoint:
        Desired output value.
    output_limits:
        (min, max) clamp on the controller output.
    integral_limits:
        (min, max) clamp on the integral term (anti-windup).
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        setpoint: float = 0.0,
        output_limits: tuple[float, float] = (-1.0, 1.0),
        integral_limits: tuple[float, float] = (-10.0, 10.0),
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_limits = output_limits
        self.integral_limits = integral_limits

        self._integral: float = 0.0
        self._prev_error: float = 0.0
        self._prev_time: float | None = None

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = None

    def update(self, measured: float, dt: float | None = None) -> float:
        """
        Compute the next control output.

        Parameters
        ----------
        measured:
            Current measured value.
        dt:
            Time step (s).  If None, uses wall-clock time since last call.
        """
        now = time.monotonic()
        if dt is None:
            dt = (now - self._prev_time) if self._prev_time is not None else 0.01
        self._prev_time = now

        error = self.setpoint - measured
        self._integral = max(
            self.integral_limits[0],
            min(self.integral_limits[1], self._integral + error * dt),
        )
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        return max(self.output_limits[0], min(self.output_limits[1], output))

    @property
    def last_error(self) -> float:
        return self._prev_error


# ---------------------------------------------------------------------------
# Sensor fusion (complementary filter)
# ---------------------------------------------------------------------------


class ComplementaryFilter:
    """
    Simple complementary filter for attitude estimation.

    Blends accelerometer (low-frequency accurate) with gyroscope
    (high-frequency accurate) data.

    alpha:
        Weight given to the gyroscope term (0.95–0.98 typical).
    """

    def __init__(self, alpha: float = 0.96) -> None:
        self.alpha = alpha
        self.roll = 0.0
        self.pitch = 0.0

    def update(self, imu: IMUReading, dt: float) -> tuple[float, float]:
        """Return (roll, pitch) in radians."""
        # Accelerometer-based angle estimate
        accel_roll = math.atan2(imu.accel_y_ms2, imu.accel_z_ms2)
        accel_pitch = math.atan2(
            -imu.accel_x_ms2,
            math.sqrt(imu.accel_y_ms2**2 + imu.accel_z_ms2**2),
        )

        # Gyroscope integration
        gyro_roll = self.roll + imu.gyro_x_rads * dt
        gyro_pitch = self.pitch + imu.gyro_y_rads * dt

        # Blend
        self.roll = self.alpha * gyro_roll + (1 - self.alpha) * accel_roll
        self.pitch = self.alpha * gyro_pitch + (1 - self.alpha) * accel_pitch
        return self.roll, self.pitch


# ---------------------------------------------------------------------------
# Stabilisation controller
# ---------------------------------------------------------------------------


@dataclass
class StabilisationConfig:
    """Tunable parameters for the stabilisation controller."""

    target_gap_m: float = 0.15  # desired hover height (m)
    max_gap_m: float = 0.30
    min_gap_m: float = 0.05
    max_roll_rad: float = 0.35  # ~20 degrees
    max_pitch_rad: float = 0.35
    update_rate_hz: float = 200.0

    # PID gains — gap control
    gap_kp: float = 1.20
    gap_ki: float = 0.05
    gap_kd: float = 0.08

    # PID gains — attitude stabilisation
    roll_kp: float = 0.80
    roll_ki: float = 0.02
    roll_kd: float = 0.06

    pitch_kp: float = 0.80
    pitch_ki: float = 0.02
    pitch_kd: float = 0.06

    # Safety
    emergency_land_tilt_rad: float = 0.60  # ~34 degrees — auto emergency land


class StabilisationController:
    """
    Main stabilisation controller for the hover bike.

    Runs a 200 Hz control loop that:
    1. Reads sensor data (IMU + altitude)
    2. Runs sensor fusion (complementary filter)
    3. Executes three PID loops (gap, roll, pitch)
    4. Sends correction signals to the active stabilisation coils
    5. Monitors safety thresholds and triggers failsafe if needed

    Parameters
    ----------
    config:
        Stabilisation configuration parameters.
    coil_output_callback:
        Optional callback that receives the (gap_cmd, roll_cmd, pitch_cmd) tuple.
        In production this drives the coil driver hardware via PWM/I2C.
    """

    def __init__(
        self,
        config: StabilisationConfig | None = None,
        coil_output_callback: Callable[[float, float, float], None] | None = None,
    ) -> None:
        self.config = config or StabilisationConfig()
        self._cb = coil_output_callback

        self._fusion = ComplementaryFilter()
        self._gap_pid = PIDController(
            self.config.gap_kp,
            self.config.gap_ki,
            self.config.gap_kd,
            setpoint=self.config.target_gap_m,
            output_limits=(-1.0, 1.0),
        )
        self._roll_pid = PIDController(
            self.config.roll_kp,
            self.config.roll_ki,
            self.config.roll_kd,
            setpoint=0.0,
            output_limits=(-1.0, 1.0),
        )
        self._pitch_pid = PIDController(
            self.config.pitch_kp,
            self.config.pitch_ki,
            self.config.pitch_kd,
            setpoint=0.0,
            output_limits=(-1.0, 1.0),
        )

        self._fault: str | None = None
        self._cycle_count: int = 0
        self._last_commands: tuple[float, float, float] = (0.0, 0.0, 0.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_faulted(self) -> bool:
        return self._fault is not None

    @property
    def fault_message(self) -> str | None:
        return self._fault

    def clear_fault(self) -> None:
        self._fault = None

    def reset_pids(self) -> None:
        self._gap_pid.reset()
        self._roll_pid.reset()
        self._pitch_pid.reset()

    def step(
        self,
        imu: IMUReading,
        alt: AltitudeSensors,
        dt: float | None = None,
    ) -> tuple[float, float, float] | None:
        """
        Execute one control cycle.

        Returns
        -------
        (gap_cmd, roll_cmd, pitch_cmd) normalised to [-1, 1], or None if faulted.
        gap_cmd > 0 means "increase lift", roll_cmd > 0 means "roll right correction".
        """
        if self._fault:
            return None

        dt = dt or 1.0 / self.config.update_rate_hz

        # 1. Sensor fusion
        roll_rad, pitch_rad = self._fusion.update(imu, dt)

        # 2. Safety checks
        if abs(roll_rad) > self.config.emergency_land_tilt_rad:
            self._fault = f"EMERGENCY: excessive roll {math.degrees(roll_rad):.1f}°"
            return None
        if abs(pitch_rad) > self.config.emergency_land_tilt_rad:
            self._fault = f"EMERGENCY: excessive pitch {math.degrees(pitch_rad):.1f}°"
            return None
        if alt.avg_gap_m < self.config.min_gap_m:
            self._fault = f"EMERGENCY: gap too small {alt.avg_gap_m * 1000:.0f} mm"
            return None

        # 3. PID updates
        gap_cmd = self._gap_pid.update(alt.avg_gap_m, dt)
        roll_cmd = self._roll_pid.update(roll_rad, dt)
        pitch_cmd = self._pitch_pid.update(pitch_rad, dt)

        commands = (gap_cmd, roll_cmd, pitch_cmd)
        self._last_commands = commands
        self._cycle_count += 1

        if self._cb is not None:
            self._cb(*commands)

        return commands

    def run_simulation(
        self,
        duration_s: float = 5.0,
        disturbance_fn: Callable[[float], tuple[float, float, float]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Simulate the stabilisation loop for *duration_s* seconds.

        Parameters
        ----------
        duration_s:
            Simulation duration (s).
        disturbance_fn:
            Optional function(t) → (gap_disturbance_m, roll_disturbance_rad, pitch_disturbance_rad).

        Returns
        -------
        List of per-step state dictionaries.
        """
        dt = 1.0 / self.config.update_rate_hz
        self.reset_pids()
        self.clear_fault()
        self._fusion = ComplementaryFilter()

        imu = IMUReading()
        alt = AltitudeSensors()
        records: list[dict[str, Any]] = []

        gap = self.config.target_gap_m
        roll = 0.0
        pitch = 0.0

        t = 0.0
        while t < duration_s:
            # Apply optional disturbance
            if disturbance_fn:
                d_gap, d_roll, d_pitch = disturbance_fn(t)
                gap += d_gap
                roll += d_roll
                pitch += d_pitch

            # Update virtual sensors — synthesise realistic IMU readings from plant state.
            # Z-up body frame: accel_z = g*cos(roll) when level.
            accel_y = math.sin(roll) * 9.81
            accel_z = math.cos(roll) * 9.81
            imu = IMUReading(
                roll_rad=roll,
                pitch_rad=pitch,
                accel_y_ms2=accel_y,
                accel_z_ms2=accel_z,
            )
            alt = AltitudeSensors(
                ultrasonic_front_m=gap,
                ultrasonic_rear_m=gap,
                ultrasonic_left_m=gap,
                ultrasonic_right_m=gap,
            )

            cmds = self.step(imu, alt, dt)

            if cmds is None:
                records.append(
                    {"t": t, "fault": self._fault, "gap": gap, "roll": roll, "pitch": pitch}
                )
                break

            gap_cmd, roll_cmd, pitch_cmd = cmds

            # Simple plant model: commands partially correct state
            gap += gap_cmd * 0.001  # 1 mm per unit command
            roll -= roll_cmd * 0.01  # 10 mrad per unit command
            pitch -= pitch_cmd * 0.01

            records.append(
                {
                    "t": round(t, 4),
                    "gap_m": round(gap, 5),
                    "roll_deg": round(math.degrees(roll), 3),
                    "pitch_deg": round(math.degrees(pitch), 3),
                    "gap_cmd": round(gap_cmd, 4),
                    "roll_cmd": round(roll_cmd, 4),
                    "pitch_cmd": round(pitch_cmd, 4),
                }
            )
            t += dt

        return records


# ---------------------------------------------------------------------------
# Safety protocol definitions
# ---------------------------------------------------------------------------

SAFETY_PROTOCOLS: list[dict[str, Any]] = [
    {
        "id": "SP-01",
        "name": "Gap Floor Cutoff",
        "trigger": "Measured hover gap < 50 mm",
        "action": "Immediately increase coil power to max; alert rider via haptic feedback.",
        "priority": "CRITICAL",
    },
    {
        "id": "SP-02",
        "name": "Excessive Tilt Emergency Land",
        "trigger": "Roll or pitch > 34° for > 200 ms",
        "action": "Cut propulsion; allow soft landing via magnetic cushion.",
        "priority": "CRITICAL",
    },
    {
        "id": "SP-03",
        "name": "Battery Low Warning",
        "trigger": "Battery SoC < 15 %",
        "action": "Flash amber LED; limit propulsion to 50 %; sound buzzer.",
        "priority": "HIGH",
    },
    {
        "id": "SP-04",
        "name": "Battery Critical Cutoff",
        "trigger": "Battery SoC < 5 %",
        "action": "Hard stop: cut propulsion; maintain maglev for 30 s for soft landing.",
        "priority": "CRITICAL",
    },
    {
        "id": "SP-05",
        "name": "IMU Communication Fault",
        "trigger": "No valid IMU packet for > 50 ms",
        "action": "Switch to accelerometer-only mode; limit tilt authority; alert rider.",
        "priority": "HIGH",
    },
    {
        "id": "SP-06",
        "name": "Over-speed Limit",
        "trigger": "Speed > 55 km/h",
        "action": "Ramp throttle limit to 0 over 3 s; maintain hover.",
        "priority": "MEDIUM",
    },
    {
        "id": "SP-07",
        "name": "Rider Absent",
        "trigger": "Seat pressure sensor indicates no rider for > 2 s while moving",
        "action": "Emergency stop; activate parking mode.",
        "priority": "HIGH",
    },
]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    def bump(t: float) -> tuple[float, float, float]:
        """Simulate a small bump at t=1 s."""
        if 1.000 <= t < 1.005:  # single 5 ms impulse
            return (-0.005, 0.008, 0.005)
        return (0.0, 0.0, 0.0)

    ctrl = StabilisationController()
    records = ctrl.run_simulation(duration_s=3.0, disturbance_fn=bump)

    print(f"Simulated {len(records)} steps")
    print(f"Final gap: {records[-1].get('gap_m', 'N/A')} m")
    print(f"Final roll: {records[-1].get('roll_deg', 'N/A')}°")
    print(f"Fault: {ctrl.fault_message}")
    print(json.dumps(SAFETY_PROTOCOLS[:2], indent=2))
