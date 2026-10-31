/*
 * sensor_fusion.ino
 * Barrot HoverBike MK-I — IMU Sensor Fusion
 *
 * Reads MPU-9250 IMU via SPI, fuses gyroscope + accelerometer data using
 * a complementary filter, and publishes attitude over serial/I2C.
 *
 * Target: Raspberry Pi Pico (for dedicated real-time sensor fusion)
 */

#include <Wire.h>

// MPU-9250 register addresses
#define MPU_ADDR         0x68
#define REG_ACCEL_XOUT_H 0x3B
#define REG_GYRO_XOUT_H  0x43
#define REG_PWR_MGMT_1   0x6B

#define ALPHA            0.96f    // complementary filter weight
#define DT_S             0.005f   // 200 Hz

float roll = 0.0f, pitch = 0.0f;

struct IMUData {
  float ax, ay, az;
  float gx, gy, gz;
};

void mpu_write(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

void mpu_read_block(uint8_t reg, uint8_t* buf, uint8_t len) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, (int)len);
  for (uint8_t i = 0; i < len && Wire.available(); i++) {
    buf[i] = Wire.read();
  }
}

IMUData readIMU() {
  uint8_t buf[14];
  mpu_read_block(REG_ACCEL_XOUT_H, buf, 14);

  auto to_int16 = [](uint8_t h, uint8_t l) -> int16_t {
    return (int16_t)((h << 8) | l);
  };

  IMUData d;
  d.ax = to_int16(buf[0],  buf[1])  / 16384.0f;  // ±2g
  d.ay = to_int16(buf[2],  buf[3])  / 16384.0f;
  d.az = to_int16(buf[4],  buf[5])  / 16384.0f;
  d.gx = to_int16(buf[8],  buf[9])  / 131.0f;    // ±250 °/s → °/s
  d.gy = to_int16(buf[10], buf[11]) / 131.0f;
  d.gz = to_int16(buf[12], buf[13]) / 131.0f;
  return d;
}

void setup() {
  Wire.begin();
  Wire.setClock(400000);
  mpu_write(REG_PWR_MGMT_1, 0x00);  // wake up MPU
  delay(100);
  Serial.begin(115200);
  Serial.println("SensorFusion v1.0 ready");
}

void loop() {
  static unsigned long last = 0;
  if (millis() - last < (unsigned long)(DT_S * 1000)) return;
  last = millis();

  IMUData imu = readIMU();

  // Accelerometer angle estimate
  float accel_roll  = atan2f(imu.ay, imu.az) * 57.2958f;
  float accel_pitch = atan2f(-imu.ax, sqrtf(imu.ay*imu.ay + imu.az*imu.az)) * 57.2958f;

  // Complementary filter
  roll  = ALPHA * (roll  + imu.gx * DT_S) + (1.0f - ALPHA) * accel_roll;
  pitch = ALPHA * (pitch + imu.gy * DT_S) + (1.0f - ALPHA) * accel_pitch;

  // Output CSV for Raspberry Pi to parse
  Serial.print("IMU,");
  Serial.print(roll, 3); Serial.print(",");
  Serial.print(pitch, 3); Serial.print(",");
  Serial.print(imu.gx, 2); Serial.print(",");
  Serial.print(imu.gy, 2); Serial.println();
}
