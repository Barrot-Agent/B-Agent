# Barrot Revolution Hover Bike — Assembly Guide

**Total build time:** ~17h  
**Total steps:** 18


## ⚠️ Safety Procedures

- MAGNETS: Always handle N52 neodymium magnets with gloves. Keep >300mm from pacemakers.
- BATTERY: Never short LiPo terminals. Store at 50% SOC if unused >1 week.
- ELECTRICAL: Always disconnect battery before working on circuits.
- FIRMWARE: Test all code on bench before installing in vehicle.
- RIDING: Wear helmet and full protective gear at all times.
- SPEED: Do not exceed 20 km/h until >5 hours of ride time logged.
- SURFACE: Only operate on smooth flat surfaces (concrete/asphalt).
- OBSERVER: Never ride without a safety observer present.
- EMERGENCY: Emergency stop = cut main fuse. Location: battery enclosure left side.
- FIRE: Keep Class D / CO2 extinguisher nearby during first power tests.

## 🔧 Assembly Steps


### Step 1: Print and post-process frame sections
**Phase:** Frame Assembly | **Time:** 180 min

Print all 4 frame sections using CF-PLA at 0.2mm layer height, 40% gyroid infill. Remove supports carefully with flush cutters. Sand joining surfaces to 400 grit.

### Step 2: Install titanium heat-set inserts
**Phase:** Frame Assembly | **Time:** 30 min

Using soldering iron at 200°C, press M8 titanium inserts into all mounting holes. Inserts should be flush or 0.2mm below surface.

### Step 3: Join frame sections
**Phase:** Frame Assembly | **Time:** 45 min

Align front and rear frame halves. Apply structural epoxy (JB Weld) to joint faces. Bolt together with M8×50mm titanium bolts, torque to 15 N·m.

### Step 4: Print and inspect magnet housings
**Phase:** Magnetic System | **Time:** 90 min

Print 4 magnet housings in PETG at 0.15mm, 80% infill. Verify all magnet pockets are within ±0.1mm tolerance using digital calipers.

### Step 5: Assemble Halbach arrays
**Phase:** Magnetic System | **Time:** 60 min

Insert N52 neodymium magnets into housings following Halbach configuration: rotate each magnet 90° clockwise from previous. Sequence: [N↑] [N→] [N↓] [N←] repeat. Lock with non-magnetic stainless screws.

### Step 6: Mount arrays to frame
**Phase:** Magnetic System | **Time:** 45 min

Bolt 4 magnet arrays to underside of frame at marked positions (FL, FR, RL, RR). Arrays should be co-planar within ±1mm. Shim if needed.

### Step 7: Install battery enclosure
**Phase:** Power System | **Time:** 20 min

Mount 3D-printed battery enclosure to frame centre (lowest point for CoG). Install rubber vibration isolators at 4 mounting points.

### Step 8: Wire power system
**Phase:** Power System | **Time:** 90 min

Install battery → BMS → main bus bar wiring. Use 10AWG silicone wire for main power runs. All positive wires: red. All ground: black. Install 40A main fuse within 15cm of battery positive terminal.

### Step 9: Install solar panel and DC-DC converter
**Phase:** Power System | **Time:** 30 min

Mount thin-film solar panel to top of frame. Connect to 48V charge controller input. Install DC-DC 48V→12V converter for electronics power rail.

### Step 10: Install supercapacitor bank
**Phase:** Power System | **Time:** 20 min

Mount supercapacitor bank near motor controllers (minimise wire length). Connect in parallel with main battery bus via balancing circuit.

### Step 11: Install hub motors
**Phase:** Propulsion | **Time:** 45 min

Press hub motors into 3D-printed wheel hub adapters. Bolt adapter to wheel with M6×20 bolts at 6-point pattern. Torque to 10 N·m. Check for <0.3mm runout.

### Step 12: Wire motor controllers (ESC)
**Phase:** Propulsion | **Time:** 45 min

Connect each motor phase to ESC (any order - adjust in firmware). Connect ESC power to main bus. Connect ESC signal to Raspberry Pi GPIO.

### Step 13: Mount Raspberry Pi and sensors
**Phase:** Control System | **Time:** 60 min

Install Raspberry Pi in control pod with standoffs. Mount IMU (MPU-6050) at Centre of Gravity of frame. Mount 4 ultrasonic sensors at corners (pointing down). Mount Hall effect sensors adjacent to each magnet array.

### Step 14: Flash and configure firmware
**Phase:** Control System | **Time:** 90 min

Install Raspberry Pi OS Lite. Copy control_firmware.py to /home/pi/. Install dependencies: pip install RPi.GPIO smbus. Configure I2C in raspi-config. Flash Arduino coprocessor with sensor_fusion.ino.

### Step 15: Calibrate sensors
**Phase:** Control System | **Time:** 30 min

Run IMU calibration: place bike on flat surface, run calibration script 60s. Zero ultrasonic sensors at known height (use 15mm block). Calibrate Hall sensors with no-load (record zero-current offset).

### Step 16: Static levitation test
**Phase:** Testing | **Time:** 30 min

With bike unloaded (no rider), power on control system. Enable levitation at low power. Verify stable hover at 10-20mm. Check all 4 corner heights are equal (±2mm).

### Step 17: Load testing (incremental)
**Phase:** Testing | **Time:** 60 min

Add weight in 10kg increments (use sandbags). Verify system holds height and remains stable at each increment. Record current draw and height at each load step.

### Step 18: Dynamic stability and propulsion test
**Phase:** Testing | **Time:** 60 min

With rider at low speed (5 km/h), verify attitude control maintains stability. Gradually increase to 20 km/h. Check for oscillations or twitchiness.

## 🔍 Troubleshooting


**Hover height oscillates / hunting**  
Cause: PID gains too aggressive (Kp too high)  
Fix: Reduce Kp by 20%. Increase Kd slightly. Check IMU is rigidly mounted.

**System fails to lift at target height**  
Cause: Halbach arrays not co-planar OR magnet orientation wrong  
Fix: Re-verify array mounting with straight edge. Check Halbach sequence: each magnet 90° from previous.

**Motor runs hot (>70°C after 10 min)**  
Cause: ESC current limit too high OR poor motor cooling  
Fix: Reduce ESC current limit by 10A. Verify motor can spin freely (no mechanical friction).

**Battery drains in <10km**  
Cause: Levitation taking excessive power OR battery health degraded  
Fix: Log coil currents - if >60% continuously, re-tune height PID. Check battery voltage under load.

**IMU drift causing tilt over time**  
Cause: Gyroscope drift (normal) - alpha value too high  
Fix: Reduce complementary filter alpha from 0.98 to 0.95. Recalibrate IMU on level surface.

**Hall sensors reading incorrectly**  
Cause: Sensor too close to permanent magnets  
Fix: Move Hall sensors to side of Halbach array, not underneath. Minimum 15mm from magnet face.