/*
 * stabilization_controller.ino
 * Barrot HoverBike MK-I — Active Stabilisation Controller
 *
 * Reads Hall effect sensors and ultrasonic distance sensors,
 * then drives correction coils via PWM to maintain hover height and attitude.
 *
 * Target hardware: Arduino Mega 2560 (coil driver) + Raspberry Pi 4B (high-level control)
 * Communication:   I2C slave (address 0x42) — receives PID commands from RPi
 *
 * Pin assignments:
 *   A0–A11  : Hall sensor inputs (12 sensors)
 *   2–5     : Ultrasonic trigger pins (4 sensors)
 *   22–25   : Ultrasonic echo pins (4 sensors)
 *   6–13    : Correction coil PWM outputs (8 coils)
 *   LED_BUILTIN : Status LED
 */

#include <Wire.h>

// ---- Configuration -------------------------------------------------------
#define N_HALL_SENSORS    12
#define N_ULTRASONIC      4
#define N_COILS           8
#define I2C_ADDRESS       0x42
#define LOOP_PERIOD_MS    5       // 200 Hz

// ---- Pin maps ------------------------------------------------------------
const uint8_t HALL_PINS[N_HALL_SENSORS] = {A0,A1,A2,A3,A4,A5,A6,A7,A8,A9,A10,A11};
const uint8_t TRIG_PINS[N_ULTRASONIC]   = {2, 3, 4, 5};
const uint8_t ECHO_PINS[N_ULTRASONIC]   = {22,23,24,25};
const uint8_t COIL_PINS[N_COILS]        = {6, 7, 8, 9, 10,11,12,13};

// ---- State ---------------------------------------------------------------
volatile uint8_t coil_duty[N_COILS];   // 0-255 PWM duty from I2C
uint16_t hall_raw[N_HALL_SENSORS];
float    gap_mm[N_ULTRASONIC];

// ---- I2C receive ---------------------------------------------------------
void onI2CReceive(int nBytes) {
  if (nBytes < N_COILS) return;
  for (int i = 0; i < N_COILS; i++) {
    coil_duty[i] = Wire.read();
  }
}

// ---- Ultrasonic measurement ----------------------------------------------
float measureGap(uint8_t trigPin, uint8_t echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 25000UL);  // 25 ms timeout → ~4.3 m max range
  if (duration == 0) return -1.0f;
  return (duration * 0.0343f) / 2.0f;  // mm
}

// ---- Setup ---------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(onI2CReceive);

  for (int i = 0; i < N_ULTRASONIC; i++) {
    pinMode(TRIG_PINS[i], OUTPUT);
    pinMode(ECHO_PINS[i], INPUT);
  }
  for (int i = 0; i < N_COILS; i++) {
    pinMode(COIL_PINS[i], OUTPUT);
    coil_duty[i] = 0;
  }
  memset(hall_raw, 0, sizeof(hall_raw));
  Serial.println("StabilisationController v1.0 ready");
}

// ---- Main loop -----------------------------------------------------------
void loop() {
  unsigned long t0 = millis();

  // 1. Read Hall sensors
  for (int i = 0; i < N_HALL_SENSORS; i++) {
    hall_raw[i] = analogRead(HALL_PINS[i]);
  }

  // 2. Read ultrasonic sensors (interleaved to reduce cross-talk)
  for (int i = 0; i < N_ULTRASONIC; i++) {
    gap_mm[i] = measureGap(TRIG_PINS[i], ECHO_PINS[i]);
  }

  // 3. Apply coil PWM outputs (set by Raspberry Pi via I2C)
  for (int i = 0; i < N_COILS; i++) {
    analogWrite(COIL_PINS[i], coil_duty[i]);
  }

  // 4. Safety override — if gap too small, max coil power on front pair
  bool gap_critical = false;
  for (int i = 0; i < N_ULTRASONIC; i++) {
    if (gap_mm[i] > 0 && gap_mm[i] < 40.0f) {
      gap_critical = true;
      break;
    }
  }
  if (gap_critical) {
    analogWrite(COIL_PINS[0], 255);
    analogWrite(COIL_PINS[1], 255);
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    digitalWrite(LED_BUILTIN, LOW);
  }

  // 5. Transmit telemetry over serial (debug)
  if (millis() % 500 < LOOP_PERIOD_MS) {
    Serial.print("GAP:");
    for (int i = 0; i < N_ULTRASONIC; i++) {
      Serial.print(gap_mm[i]); Serial.print(",");
    }
    Serial.println();
  }

  // 6. Maintain loop timing
  unsigned long elapsed = millis() - t0;
  if (elapsed < LOOP_PERIOD_MS) {
    delay(LOOP_PERIOD_MS - elapsed);
  }
}
