"""
control_firmware.py - Hover Bike Flight Controller (Raspberry Pi / Arduino)

Implements stabilisation algorithms, sensor fusion, motor control,
and safety protocols for the hover bike control system.
Compatible with Raspberry Pi 4 (primary) and Arduino Nano (co-processor).
"""

import math
from dataclasses import dataclass, field
from typing import Callable


# ---------------------------------------------------------------------------
# Sensor data structures
# ---------------------------------------------------------------------------

@dataclass
class IMUData:
    """Raw IMU readings (6-DOF)."""
    accel_x: float = 0.0   # m/s²
    accel_y: float = 0.0
    accel_z: float = 9.81  # Z includes gravity at rest
    gyro_x: float = 0.0    # rad/s
    gyro_y: float = 0.0
    gyro_z: float = 0.0
    timestamp_s: float = 0.0


@dataclass
class AltitudeData:
    """Combined altitude sensor readings."""
    ultrasonic_mm: float = 15.0   # HC-SR04 reading
    barometric_pa: float = 101325.0  # BMP280 reading
    timestamp_s: float = 0.0


@dataclass
class VehicleState:
    """Full estimated vehicle state."""
    height_mm: float = 15.0
    height_rate_mm_s: float = 0.0
    roll_rad: float = 0.0
    pitch_rad: float = 0.0
    yaw_rad: float = 0.0
    roll_rate: float = 0.0
    pitch_rate: float = 0.0
    yaw_rate: float = 0.0
    vx_ms: float = 0.0
    vy_ms: float = 0.0


# ---------------------------------------------------------------------------
# Complementary / Mahony sensor fusion
# ---------------------------------------------------------------------------

class SensorFusion:
    """
    Complementary filter for IMU attitude estimation.
    Combines gyroscope integration with accelerometer tilt correction.
    """

    def __init__(self, alpha: float = 0.98, dt_s: float = 0.001):
        self.alpha = alpha      # Complementary filter coefficient
        self.dt = dt_s
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        # Mahony integral terms
        self._ix = 0.0
        self._iy = 0.0
        self._iz = 0.0
        self.Ki = 0.005
        self.Kp = 2.0

    def update(self, imu: IMUData) -> tuple[float, float, float]:
        """
        Update attitude estimate from IMU data.
        Returns (roll_rad, pitch_rad, yaw_rad).
        """
        # Accel-based tilt
        accel_norm = math.sqrt(imu.accel_x ** 2 + imu.accel_y ** 2
                               + imu.accel_z ** 2)
        if accel_norm < 1e-6:
            accel_norm = 9.81

        roll_accel = math.atan2(imu.accel_y, imu.accel_z)
        pitch_accel = math.atan2(-imu.accel_x,
                                 math.sqrt(imu.accel_y ** 2 + imu.accel_z ** 2))

        # Complementary filter
        self.roll = (self.alpha * (self.roll + imu.gyro_x * self.dt)
                     + (1 - self.alpha) * roll_accel)
        self.pitch = (self.alpha * (self.pitch + imu.gyro_y * self.dt)
                      + (1 - self.alpha) * pitch_accel)
        self.yaw += imu.gyro_z * self.dt  # No magnetometer, integrate only

        return self.roll, self.pitch, self.yaw


# ---------------------------------------------------------------------------
# PID controller
# ---------------------------------------------------------------------------

class PIDController:
    """General-purpose PID controller with anti-windup."""

    def __init__(self, kp: float, ki: float, kd: float,
                 output_min: float = -float("inf"),
                 output_max: float = float("inf"),
                 integral_limit: float = 100.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.integral_limit = integral_limit
        self._integral = 0.0
        self._prev_error = 0.0

    def compute(self, setpoint: float, measurement: float,
                dt: float) -> float:
        """Compute PID output."""
        error = setpoint - measurement
        self._integral = max(-self.integral_limit,
                             min(self.integral_limit,
                                 self._integral + error * dt))
        derivative = (error - self._prev_error) / max(dt, 1e-6)
        self._prev_error = error
        output = (self.kp * error + self.ki * self._integral
                  + self.kd * derivative)
        return max(self.output_min, min(self.output_max, output))

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0


# ---------------------------------------------------------------------------
# Flight controller
# ---------------------------------------------------------------------------

class FlightController:
    """
    Main stabilisation loop for the hover bike.
    Controls 4 electromagnet coils for height and attitude.
    """

    # Coil indices: 0=FL, 1=FR, 2=RL, 3=RR (Front/Rear × Left/Right)
    N_COILS = 4

    def __init__(self, dt_s: float = 0.001):
        self.dt = dt_s
        self.sensor_fusion = SensorFusion(dt_s=dt_s)

        # Height hold PID
        self.height_pid = PIDController(
            kp=2.5, ki=0.5, kd=0.8,
            output_min=-100.0, output_max=100.0)

        # Attitude PIDs
        self.roll_pid = PIDController(
            kp=5.0, ki=0.3, kd=1.2,
            output_min=-50.0, output_max=50.0)
        self.pitch_pid = PIDController(
            kp=5.0, ki=0.3, kd=1.2,
            output_min=-50.0, output_max=50.0)

        # Setpoints
        self.target_height_mm = 15.0
        self.target_roll = 0.0
        self.target_pitch = 0.0

        # Coil base current [%]
        self.base_current_pct = 50.0

        # Safety state
        self.armed = False
        self.fault_flags: list[str] = []
        self.loop_count = 0

    def arm(self):
        """Arm the control system (enable motor outputs)."""
        self.armed = True
        self.fault_flags.clear()
        print("  [FLIGHT CTRL] ARMED")

    def disarm(self):
        """Disarm — set all outputs to zero."""
        self.armed = False
        print("  [FLIGHT CTRL] DISARMED")

    def compute_coil_outputs(self, imu: IMUData,
                             altitude: AltitudeData) -> list[float]:
        """
        Main control law.
        Returns list of 4 coil current percentages [0-100].
        """
        if not self.armed:
            return [0.0] * self.N_COILS

        # 1. Sensor fusion
        roll, pitch, _ = self.sensor_fusion.update(imu)

        # 2. Height controller
        h_correction = self.height_pid.compute(
            self.target_height_mm, altitude.ultrasonic_mm, self.dt)

        # 3. Attitude controllers
        roll_correction = self.roll_pid.compute(self.target_roll, roll, self.dt)
        pitch_correction = self.pitch_pid.compute(self.target_pitch, pitch, self.dt)

        # 4. Mixer: distribute corrections to 4 coils
        # FL, FR, RL, RR
        base = self.base_current_pct + h_correction
        coils = [
            base - roll_correction + pitch_correction,   # FL
            base + roll_correction + pitch_correction,   # FR
            base - roll_correction - pitch_correction,   # RL
            base + roll_correction - pitch_correction,   # RR
        ]

        # 5. Clamp outputs
        coils = [max(0.0, min(100.0, c)) for c in coils]

        # 6. Safety checks
        self._safety_checks(altitude, imu)

        self.loop_count += 1
        return coils

    def _safety_checks(self, altitude: AltitudeData, imu: IMUData):
        """Detect and flag safety violations."""
        flags = []

        # Too low (crash risk)
        if altitude.ultrasonic_mm < 5.0:
            flags.append("ALTITUDE_CRITICAL_LOW")

        # Too high (runaway)
        if altitude.ultrasonic_mm > 200.0:
            flags.append("ALTITUDE_EXCEEDED")

        # Excessive tilt
        roll = abs(self.sensor_fusion.roll)
        pitch = abs(self.sensor_fusion.pitch)
        if roll > math.radians(30) or pitch > math.radians(30):
            flags.append("EXCESSIVE_TILT")

        if flags and not self.fault_flags:
            print(f"  [SAFETY] Faults detected: {flags}")
        self.fault_flags = flags

    @property
    def is_safe(self) -> bool:
        return len(self.fault_flags) == 0


# ---------------------------------------------------------------------------
# Motor speed controller interface
# ---------------------------------------------------------------------------

@dataclass
class ESCCommand:
    """Electronic Speed Controller command."""
    motor_id: int
    throttle_pct: float  # 0-100
    direction: int = 1   # 1=forward, -1=reverse


class MotorController:
    """
    Abstraction layer for 4 hub motors + 4 stabilisation coils.
    In production: sends PWM signals via GPIO.
    """

    def __init__(self, n_drive_motors: int = 2, n_coils: int = 4):
        self.n_drive = n_drive_motors
        self.n_coils = n_coils
        self.drive_throttle = [0.0] * n_drive_motors
        self.coil_current = [0.0] * n_coils
        self.total_power_w = 0.0

    def set_drive(self, motor_id: int, throttle_pct: float):
        if 0 <= motor_id < self.n_drive:
            self.drive_throttle[motor_id] = max(0.0, min(100.0, throttle_pct))

    def set_coil(self, coil_id: int, current_pct: float):
        if 0 <= coil_id < self.n_coils:
            self.coil_current[coil_id] = max(0.0, min(100.0, current_pct))

    def estimate_power_w(self) -> float:
        """Estimate total electrical power consumption."""
        drive_power = sum(t / 100 * 500 for t in self.drive_throttle)
        coil_power = sum(c / 100 * 20 for c in self.coil_current)
        self.total_power_w = drive_power + coil_power
        return self.total_power_w

    def status(self) -> dict:
        return {
            "drive_throttle_pct": [round(t, 1) for t in self.drive_throttle],
            "coil_current_pct": [round(c, 1) for c in self.coil_current],
            "estimated_power_w": round(self.estimate_power_w(), 1),
        }


# ---------------------------------------------------------------------------
# Firmware simulation / demonstration
# ---------------------------------------------------------------------------

def simulate_control_loop(steps: int = 500,
                           target_height_mm: float = 15.0) -> dict:
    """
    Simulate the closed-loop control system.
    Returns performance metrics from the simulation.
    """
    fc = FlightController(dt_s=0.001)
    mc = MotorController()
    fc.arm()
    fc.target_height_mm = target_height_mm

    # Simulated state
    height = 5.0        # Start at 5mm
    height_rate = 0.0
    roll = 0.02         # Small initial tilt

    height_errors = []
    coil_history = []
    power_history = []

    for i in range(steps):
        t = i * fc.dt

        # Fake IMU with small disturbance
        imu = IMUData(
            accel_x=math.sin(t * 0.5) * 0.1,
            accel_y=math.cos(t * 0.3) * 0.05,
            accel_z=9.81,
            gyro_x=0.01 * math.sin(t),
            gyro_y=0.005 * math.cos(t),
            gyro_z=0.0,
            timestamp_s=t,
        )
        alt = AltitudeData(ultrasonic_mm=height, timestamp_s=t)

        coils = fc.compute_coil_outputs(imu, alt)

        # Simple plant: height responds to average coil current
        avg_coil = sum(coils) / len(coils)
        lift_correction = (avg_coil - 50.0) * 0.01  # mm/ms per %
        height_rate += lift_correction * 10 - 0.5   # gravity drag
        height = max(0.0, height + height_rate * fc.dt)
        height_rate *= 0.95  # Damping

        for c_id, c_val in enumerate(coils):
            mc.set_coil(c_id, c_val)

        if i % 50 == 0:
            height_errors.append(abs(target_height_mm - height))
            coil_history.append([round(c, 1) for c in coils])
            power_history.append(mc.estimate_power_w())

    settling_idx = next((i for i, e in enumerate(height_errors) if e < 1.0),
                        len(height_errors) - 1)

    return {
        "target_height_mm": target_height_mm,
        "final_height_mm": round(height, 2),
        "final_error_mm": round(abs(target_height_mm - height), 2),
        "settling_steps_x50": settling_idx,
        "avg_power_w": round(sum(power_history) / len(power_history), 1),
        "is_safe": fc.is_safe,
        "loop_count": fc.loop_count,
        "sample_coils": coil_history[-1] if coil_history else [],
    }


if __name__ == "__main__":
    import json
    from pathlib import Path

    print("=" * 55)
    print("BARROT HOVER BIKE — CONTROL FIRMWARE SIMULATION")
    print("=" * 55)

    results = simulate_control_loop(steps=2000, target_height_mm=15.0)
    print(f"\nSimulation Results (2000 steps @ 1kHz):")
    for k, v in results.items():
        print(f"  {k:<30} {v}")

    out = Path(__file__).parent.parent / "models" / "control_simulation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved → {out}")
