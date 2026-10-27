# Control System Guide — Barrot HoverBike MK-I

## System Architecture

```
Raspberry Pi 4B (main controller)
├── I2C bus
│   ├── 0x42 → Arduino Mega (coil driver + ultrasonic)
│   ├── 0x43 → Arduino Nano (power manager)
│   └── 0x68 → MPU-9250 IMU
├── UART → Arduino Pico (sensor fusion output)
├── USB-CAN → VESC #1 (left hub motor)
├── USB-CAN → VESC #2 (right hub motor)
└── GPIO → Emergency cut-off relay
```

## Flight Controller Setup

1. Flash Raspberry Pi OS Lite (64-bit) to MicroSD.
2. Enable I2C: `sudo raspi-config` → Interfaces → I2C → Enable.
3. Enable UART: disable serial console, enable UART hardware.
4. Install dependencies: `pip install smbus2 pyserial pyvesc`.
5. Clone firmware repo and run `python -m control_firmware` for initial test.

## Sensor Calibration

### IMU Calibration
```bash
python -m control_firmware --calibrate-imu
```
Place bike on level surface. The script averages 1,000 samples to compute
accelerometer and gyroscope bias offsets. Saved to `~/.hover_bike/imu_cal.json`.

### Ultrasonic Calibration
Measure actual gap with ruler. Run:
```bash
python -m control_firmware --calibrate-ultrasonic --known-gap-mm 150
```
Computes offset correction for each of the 4 sensors.

## PID Tuning

Default gains: Kp=1.20, Ki=0.05, Kd=0.08 (gap control)

**Manual tuning procedure (Ziegler-Nichols ultimate gain method):**
1. Set Ki=0, Kd=0. Increase Kp until sustained oscillation observed (= Ku).
2. Measure oscillation period Tu.
3. Apply: Kp = 0.6×Ku, Ki = 2×Kp/Tu, Kd = Kp×Tu/8.

**Stability indicators:**
- Stable: gap settles within ±5 mm in < 2 s after step disturbance.
- Too much Kp: oscillation (bouncing). Reduce Kp 20 %.
- Too little Kd: slow settling after disturbance. Increase Kd 15 %.

## Firmware Flashing

### Arduino Mega (coil driver)
```bash
arduino-cli compile --fqbn arduino:avr:mega firmware/stabilization_controller.ino
arduino-cli upload  --fqbn arduino:avr:mega -p /dev/ttyUSB0 firmware/stabilization_controller.ino
```

### ATtiny85 (safety monitor)
```bash
arduino-cli compile --fqbn ATTinyCore:avr:attinyx5 firmware/safety_protocols.ino
# Program via USBasp or Arduino as ISP
```

## Testing Procedures

1. **Bench test**: Connect all electronics with bike on a stand (no magnets active).
   Verify I2C communication, VESC responses, IMU readings.
2. **Tethered hover**: Secure with safety tethers at 30 cm height.
   Gradually increase coil power. Observe gap sensors stabilise.
3. **Free hover**: Remove tethers. Test at 15 cm gap for 5 minutes.
4. **Dynamic test**: Apply gentle push; observe PID correction response.
5. **Propulsion test**: Test each motor independently at 10 % throttle.
   Then test both together at progressively higher throttle.
