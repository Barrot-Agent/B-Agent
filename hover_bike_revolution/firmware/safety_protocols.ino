/*
 * safety_protocols.ino
 * Barrot HoverBike MK-I — Dedicated Safety Monitor
 *
 * Runs independently of the main control loop to ensure that
 * critical safety cutoffs cannot be overridden by software faults.
 *
 * Target: ATtiny85 (minimal, reliable, independent of main MCU)
 */

// Pins (ATtiny85 physical pin → function)
#define PIN_TILT_IN      1   // Analog: tilt sensor (KX023 MEMS, SPI too complex for ATtiny)
#define PIN_GAP_IN       2   // Analog: secondary gap sense (resistive divider from HC-SR04)
#define PIN_BATT_IN      3   // Analog: battery voltage divider
#define PIN_CUTOFF_OUT   0   // Digital output: HIGH = system OK, LOW = emergency cutoff
#define PIN_ALARM_OUT    4   // Digital output: buzzer alarm

// Thresholds (ADC counts, 10-bit, Vref = 5 V)
#define TILT_MAX_ADC     614   // ~3 V ≈ 30° tilt (empirically calibrated)
#define GAP_MIN_ADC      51    // ~0.25 V ≈ 40 mm minimum gap
#define BATT_MIN_ADC     819   // ~4 V ≈ 38.4 V after divider (10:1)

bool systemOK = true;
unsigned long alarmSince = 0;

void setup() {
  pinMode(PIN_CUTOFF_OUT, OUTPUT);
  pinMode(PIN_ALARM_OUT,  OUTPUT);
  digitalWrite(PIN_CUTOFF_OUT, HIGH);  // allow normal operation
  digitalWrite(PIN_ALARM_OUT,  LOW);
}

void loop() {
  int tilt = analogRead(PIN_TILT_IN);
  int gap  = analogRead(PIN_GAP_IN);
  int batt = analogRead(PIN_BATT_IN);

  bool tilt_fault = tilt > TILT_MAX_ADC;
  bool gap_fault  = gap  < GAP_MIN_ADC;
  bool batt_fault = batt < BATT_MIN_ADC;

  if (tilt_fault || gap_fault || batt_fault) {
    if (alarmSince == 0) alarmSince = millis();
    // Only cut off after fault persists for >200 ms (debounce)
    if (millis() - alarmSince > 200) {
      systemOK = false;
      digitalWrite(PIN_CUTOFF_OUT, LOW);
    }
    // Always sound alarm immediately
    digitalWrite(PIN_ALARM_OUT, HIGH);
  } else {
    alarmSince = 0;
    if (systemOK) {
      digitalWrite(PIN_CUTOFF_OUT, HIGH);
    }
    // Latching: once tripped, require manual reset (power cycle)
    digitalWrite(PIN_ALARM_OUT, LOW);
  }

  delay(10);  // 100 Hz check
}
