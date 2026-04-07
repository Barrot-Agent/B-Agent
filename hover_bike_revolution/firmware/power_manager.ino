/*
 * power_manager.ino
 * Barrot Revolution Hover Bike - Power Management Co-Processor
 * Target: Arduino Nano
 *
 * Monitors battery SOC, manages charge controller,
 * implements safety cutoffs, and reports power telemetry.
 */

#include <Wire.h>

// ── Pin Definitions ──────────────────────────────────────────────
#define BATTERY_VOLTAGE_PIN  A0   // Voltage divider: 60V → 3.3V range
#define BATTERY_CURRENT_PIN  A1   // ACS712 current sensor
#define SOLAR_VOLTAGE_PIN    A2   // Solar panel voltage
#define SOLAR_CURRENT_PIN    A3   // Solar current

#define RELAY_MAIN_POWER     4    // Main power relay (HIGH = ON)
#define RELAY_SOLAR_CHARGE   5    // Solar charge relay
#define LED_STATUS           13
#define BUZZER_PIN           7

// ── Calibration ──────────────────────────────────────────────────
const float VBAT_SCALE   = 18.18;  // ADC → actual voltage (for 60V max / 3.3V ADC)
const float IBAT_OFFSET  = 512.0;  // Zero-current ADC value (ACS712 midpoint)
const float IBAT_SCALE   = 0.0664; // ADC counts to Amperes (ACS712 30A = 66mV/A)
const float VSOL_SCALE   = 18.18;

// ── Thresholds ────────────────────────────────────────────────────
const float VBAT_FULL    = 54.6;   // 4.2V × 13 cells
const float VBAT_NOMINAL = 48.0;   // 3.69V × 13 cells
const float VBAT_LOW     = 43.0;   // 3.31V × 13 cells  - warning
const float VBAT_CUTOFF  = 40.0;   // 3.08V × 13 cells  - cutoff
const float IBAT_MAX     = 40.0;   // A - max continuous discharge

// ── State ─────────────────────────────────────────────────────────
float vBat = 0.0, iBat = 0.0, vSol = 0.0, iSol = 0.0;
float soc  = 1.0;         // State of charge [0-1]
float energyUsed_wh = 0.0;
bool  mainPowerOn   = false;
bool  solarCharging = false;
unsigned long lastTime = 0;

enum PowerState { STARTUP, IDLE, OPERATING, LOW_BATTERY, FAULT };
PowerState state = STARTUP;

// ── Read sensors ─────────────────────────────────────────────────
void readSensors() {
  int vBatRaw  = analogRead(BATTERY_VOLTAGE_PIN);
  int iBatRaw  = analogRead(BATTERY_CURRENT_PIN);
  int vSolRaw  = analogRead(SOLAR_VOLTAGE_PIN);
  int iSolRaw  = analogRead(SOLAR_CURRENT_PIN);

  vBat = vBatRaw * (3.3 / 1023.0) * VBAT_SCALE;
  iBat = (iBatRaw - IBAT_OFFSET) * IBAT_SCALE;
  vSol = vSolRaw * (3.3 / 1023.0) * VSOL_SCALE;
  iSol = (iSolRaw - 512.0) * IBAT_SCALE;

  // Simple SOC estimate from voltage (crude - use coulomb counting in production)
  soc = constrain((vBat - VBAT_CUTOFF) / (VBAT_FULL - VBAT_CUTOFF), 0.0, 1.0);
}

// ── Update energy tracking ────────────────────────────────────────
void updateEnergy(float dt_s) {
  float power_w = vBat * iBat;
  if (power_w > 0) {  // Discharging
    energyUsed_wh += power_w * dt_s / 3600.0;
  }
}

// ── Safety checks ────────────────────────────────────────────────
bool safetyCheck() {
  if (vBat < VBAT_CUTOFF) {
    Serial.println("FAULT: BATTERY UNDERVOLTAGE CUTOFF");
    state = FAULT;
    return false;
  }
  if (iBat > IBAT_MAX) {
    Serial.println("FAULT: OVERCURRENT DETECTED");
    state = FAULT;
    return false;
  }
  if (vBat < VBAT_LOW) {
    state = LOW_BATTERY;
    tone(BUZZER_PIN, 1000, 500);
  }
  return true;
}

// ── Setup ─────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  pinMode(RELAY_MAIN_POWER,  OUTPUT);
  pinMode(RELAY_SOLAR_CHARGE, OUTPUT);
  pinMode(LED_STATUS, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(RELAY_MAIN_POWER,   LOW);
  digitalWrite(RELAY_SOLAR_CHARGE, LOW);

  delay(1000);
  readSensors();
  Serial.println("BARROT POWER MANAGER - READY");
  Serial.print("Battery: ");
  Serial.print(vBat); Serial.print("V  SOC: ");
  Serial.print((int)(soc * 100)); Serial.println("%");

  lastTime = millis();
  state = IDLE;
}

// ── Main Loop ─────────────────────────────────────────────────────
void loop() {
  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0;
  if (dt < 0.1) return;  // 10 Hz update rate
  lastTime = now;

  readSensors();
  updateEnergy(dt);

  // Command handler
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "POWER_ON") {
      if (safetyCheck()) {
        digitalWrite(RELAY_MAIN_POWER, HIGH);
        mainPowerOn = true;
        state = OPERATING;
        Serial.println("MAIN POWER: ON");
      }
    } else if (cmd == "POWER_OFF") {
      digitalWrite(RELAY_MAIN_POWER, LOW);
      mainPowerOn = false;
      state = IDLE;
      Serial.println("MAIN POWER: OFF");
    } else if (cmd == "STATUS") {
      reportTelemetry();
    }
  }

  // Solar charging management
  if (vSol > vBat + 2.0 && soc < 0.95) {
    if (!solarCharging) {
      digitalWrite(RELAY_SOLAR_CHARGE, HIGH);
      solarCharging = true;
      Serial.println("SOLAR: Charge relay ON");
    }
  } else {
    if (solarCharging) {
      digitalWrite(RELAY_SOLAR_CHARGE, LOW);
      solarCharging = false;
    }
  }

  // Safety enforcement
  if (!safetyCheck() && mainPowerOn) {
    digitalWrite(RELAY_MAIN_POWER, LOW);
    mainPowerOn = false;
    Serial.println("SAFETY: Main power cut");
  }

  // Status LED blink pattern
  if (state == FAULT) {
    digitalWrite(LED_STATUS, (millis() / 200) % 2);  // Fast blink
  } else if (state == LOW_BATTERY) {
    digitalWrite(LED_STATUS, (millis() / 500) % 2);  // Medium blink
  } else if (state == OPERATING) {
    digitalWrite(LED_STATUS, HIGH);
  }

  // Telemetry every second
  static unsigned long lastTel = 0;
  if (now - lastTel > 1000) {
    lastTel = now;
    reportTelemetry();
  }
}

void reportTelemetry() {
  Serial.print("PWR V="); Serial.print(vBat, 1);
  Serial.print(" I="); Serial.print(iBat, 1);
  Serial.print(" SOC="); Serial.print((int)(soc * 100));
  Serial.print("% Sol="); Serial.print(vSol, 1);
  Serial.print("V Wh="); Serial.println(energyUsed_wh, 1);
}
