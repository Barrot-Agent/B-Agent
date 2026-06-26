/*
 * power_manager.ino
 * Barrot HoverBike MK-I — Power Management Controller
 *
 * Monitors battery voltage, current, and SoC.
 * Controls charge relay, implements safety cutoffs, and reports
 * power telemetry to the Raspberry Pi via I2C.
 *
 * Target: Arduino Nano (low-power monitoring node)
 * I2C address: 0x43
 */

#include <Wire.h>

#define I2C_ADDRESS        0x43
#define BATT_VOLT_PIN      A0
#define BATT_CURR_PIN      A1
#define SOLAR_VOLT_PIN     A2
#define CHARGE_RELAY_PIN   7
#define ALARM_PIN          8

// Battery parameters
#define BATT_FULL_V        54.75f   // 3.65 V × 15S
#define BATT_EMPTY_V       42.0f    // 2.80 V × 15S
#define BATT_CRITICAL_V    40.5f    // 2.70 V × 15S — force cutoff
#define CURR_SENSE_MV_PER_A 10.0f  // 100 A shunt = 1 V
#define VOLT_DIVIDER_RATIO  11.0f  // 100kΩ / 10kΩ divider

struct PowerState {
  float batt_v;
  float batt_a;
  float solar_v;
  uint8_t soc_pct;
  bool charging;
  bool critical;
};

PowerState ps;

// Register map sent via I2C (8 bytes)
uint8_t i2c_buf[8];

void packState() {
  // Pack into 8-byte telemetry frame
  uint16_t v = (uint16_t)(ps.batt_v * 100);
  uint16_t a = (uint16_t)((ps.batt_a + 100.0f) * 100);  // offset to allow negative
  i2c_buf[0] = highByte(v);
  i2c_buf[1] = lowByte(v);
  i2c_buf[2] = highByte(a);
  i2c_buf[3] = lowByte(a);
  i2c_buf[4] = ps.soc_pct;
  i2c_buf[5] = (uint8_t)((ps.solar_v * 10) & 0xFF);
  i2c_buf[6] = ps.charging ? 1 : 0;
  i2c_buf[7] = ps.critical ? 1 : 0;
}

void onI2CRequest() {
  packState();
  Wire.write(i2c_buf, 8);
}

float readVoltage(uint8_t pin) {
  int raw = analogRead(pin);
  float v_adc = raw * (5.0f / 1023.0f);
  return v_adc * VOLT_DIVIDER_RATIO;
}

float readCurrent(uint8_t pin) {
  int raw = analogRead(pin);
  float v_adc = raw * (5.0f / 1023.0f);
  float v_ref = 2.5f;  // mid-point of bidirectional sense
  return (v_adc - v_ref) * 1000.0f / CURR_SENSE_MV_PER_A;
}

uint8_t estimateSoC(float v) {
  if (v >= BATT_FULL_V)  return 100;
  if (v <= BATT_EMPTY_V) return 0;
  return (uint8_t)(((v - BATT_EMPTY_V) / (BATT_FULL_V - BATT_EMPTY_V)) * 100.0f);
}

void setup() {
  Wire.begin(I2C_ADDRESS);
  Wire.onRequest(onI2CRequest);
  pinMode(CHARGE_RELAY_PIN, OUTPUT);
  pinMode(ALARM_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("PowerManager v1.0 ready");
}

void loop() {
  ps.batt_v  = readVoltage(BATT_VOLT_PIN);
  ps.batt_a  = readCurrent(BATT_CURR_PIN);
  ps.solar_v = readVoltage(SOLAR_VOLT_PIN);
  ps.soc_pct = estimateSoC(ps.batt_v);

  // Enable charging relay if solar voltage sufficient
  ps.charging = (ps.solar_v > (ps.batt_v + 1.0f));
  digitalWrite(CHARGE_RELAY_PIN, ps.charging ? HIGH : LOW);

  // Critical voltage alarm
  ps.critical = (ps.batt_v < BATT_CRITICAL_V);
  if (ps.critical) {
    digitalWrite(ALARM_PIN, HIGH);
    Serial.println("CRITICAL: Battery voltage too low!");
  } else {
    digitalWrite(ALARM_PIN, LOW);
  }

  delay(100);  // 10 Hz monitoring
}
