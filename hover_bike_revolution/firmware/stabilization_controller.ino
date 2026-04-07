/*
 * stabilization_controller.ino
 * Barrot Revolution Hover Bike - Active Stabilisation Firmware
 * Target: Arduino Nano (co-processor) / Raspberry Pi via serial bridge
 *
 * Controls 4 correction electromagnet coils to maintain
 * stable hover height and attitude.
 */

#include <Wire.h>
#include <math.h>

// ── Pin Definitions ──────────────────────────────────────────────
#define COIL_FL  3   // Front-Left PWM output  (D3)
#define COIL_FR  5   // Front-Right PWM output (D5)
#define COIL_RL  6   // Rear-Left PWM output   (D6)
#define COIL_RR  9   // Rear-Right PWM output  (D9)

#define HALL_FL  A0  // Hall effect sensor FL
#define HALL_FR  A1  // Hall effect sensor FR
#define HALL_RL  A2  // Hall effect sensor RL
#define HALL_RR  A3  // Hall effect sensor RR

#define STATUS_LED  13

// ── PID Gains ────────────────────────────────────────────────────
const float KP_HEIGHT  = 2.5;
const float KI_HEIGHT  = 0.5;
const float KD_HEIGHT  = 0.8;
const float KP_ROLL    = 5.0;
const float KD_ROLL    = 1.2;
const float KP_PITCH   = 5.0;
const float KD_PITCH   = 1.2;

// ── Setpoints ────────────────────────────────────────────────────
float targetHeightMm  = 15.0;
float targetRoll      = 0.0;
float targetPitch     = 0.0;

// ── State ────────────────────────────────────────────────────────
float heightErr_integral = 0.0;
float prevHeightErr      = 0.0;
float prevRollErr        = 0.0;
float prevPitchErr       = 0.0;
float roll = 0.0, pitch = 0.0;

unsigned long lastTime = 0;
bool armed = false;

// ── Hall → Gap conversion ─────────────────────────────────────────
// Calibration constants (set during calibration phase)
float hallOffset[4] = {512, 512, 512, 512};
float hallGain[4]   = {0.05, 0.05, 0.05, 0.05};  // mm per ADC count

float hallToGap(int hallRaw, int idx) {
  return (float)(hallRaw - hallOffset[idx]) * hallGain[idx] + targetHeightMm;
}

// ── PID Step ─────────────────────────────────────────────────────
float pidStep(float setpoint, float measured, float &integral,
              float &prevErr, float kp, float ki, float kd, float dt) {
  float err = setpoint - measured;
  integral = constrain(integral + err * dt, -100.0, 100.0);
  float deriv = (err - prevErr) / dt;
  prevErr = err;
  return kp * err + ki * integral + kd * deriv;
}

// ── Setup ─────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Wire.begin();

  pinMode(COIL_FL, OUTPUT);
  pinMode(COIL_FR, OUTPUT);
  pinMode(COIL_RL, OUTPUT);
  pinMode(COIL_RR, OUTPUT);
  pinMode(STATUS_LED, OUTPUT);

  // Zero all coils
  analogWrite(COIL_FL, 0);
  analogWrite(COIL_FR, 0);
  analogWrite(COIL_RL, 0);
  analogWrite(COIL_RR, 0);

  Serial.println("BARROT HOVER BIKE STABILISER - READY");
  Serial.println("Send 'ARM' to enable, 'DISARM' to disable");
  lastTime = millis();
}

// ── Main Loop ─────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  if (dt < 0.001) return;  // 1 kHz max
  lastTime = now;

  // Serial command handler
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "ARM") {
      armed = true;
      digitalWrite(STATUS_LED, HIGH);
      Serial.println("ARMED");
    } else if (cmd == "DISARM") {
      armed = false;
      digitalWrite(STATUS_LED, LOW);
      Serial.println("DISARMED");
    } else if (cmd.startsWith("HEIGHT:")) {
      targetHeightMm = cmd.substring(7).toFloat();
      Serial.print("Target height set: ");
      Serial.println(targetHeightMm);
    }
  }

  if (!armed) {
    analogWrite(COIL_FL, 0);
    analogWrite(COIL_FR, 0);
    analogWrite(COIL_RL, 0);
    analogWrite(COIL_RR, 0);
    return;
  }

  // Read Hall sensors → gap estimates
  float gapFL = hallToGap(analogRead(HALL_FL), 0);
  float gapFR = hallToGap(analogRead(HALL_FR), 1);
  float gapRL = hallToGap(analogRead(HALL_RL), 2);
  float gapRR = hallToGap(analogRead(HALL_RR), 3);
  float avgGap = (gapFL + gapFR + gapRL + gapRR) / 4.0;

  // Estimate roll/pitch from corner gaps
  roll  = atan2(gapFR - gapFL, 300.0);  // 300mm = bike width
  pitch = atan2(gapFL - gapRL, 700.0);  // 700mm = wheelbase/2

  // Height PID
  float hCorr = pidStep(targetHeightMm, avgGap,
                        heightErr_integral, prevHeightErr,
                        KP_HEIGHT, KI_HEIGHT, KD_HEIGHT, dt);

  // Attitude P+D only (no integral for attitude)
  float rCorr = KP_ROLL  * (targetRoll  - roll)  + KD_ROLL  * (-prevRollErr  / dt);
  float pCorr = KP_PITCH * (targetPitch - pitch) + KD_PITCH * (-prevPitchErr / dt);
  prevRollErr  = targetRoll  - roll;
  prevPitchErr = targetPitch - pitch;

  // Mixer: base + corrections → 4 coils
  float base = 128.0 + hCorr;  // 128 = 50% of 255
  float fl = base - rCorr + pCorr;
  float fr = base + rCorr + pCorr;
  float rl = base - rCorr - pCorr;
  float rr = base + rCorr - pCorr;

  // Safety: if any gap critically low, cut power
  if (gapFL < 3.0 || gapFR < 3.0 || gapRL < 3.0 || gapRR < 3.0) {
    Serial.println("SAFETY: CRITICAL GAP - DISARMING");
    armed = false;
    return;
  }

  // Output (clamped 0-255)
  analogWrite(COIL_FL, (int)constrain(fl, 0, 255));
  analogWrite(COIL_FR, (int)constrain(fr, 0, 255));
  analogWrite(COIL_RL, (int)constrain(rl, 0, 255));
  analogWrite(COIL_RR, (int)constrain(rr, 0, 255));

  // Telemetry every 100ms
  static unsigned long lastTelemetry = 0;
  if (now - lastTelemetry > 100) {
    lastTelemetry = now;
    Serial.print("G:");
    Serial.print(avgGap, 1);
    Serial.print(" R:");
    Serial.print(degrees(roll), 1);
    Serial.print(" P:");
    Serial.print(degrees(pitch), 1);
    Serial.print(" C:");
    Serial.print((int)fl); Serial.print(",");
    Serial.print((int)fr); Serial.print(",");
    Serial.print((int)rl); Serial.print(",");
    Serial.println((int)rr);
  }
}
