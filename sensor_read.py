# import board
# import adafruit_tcs34725
# import time

# class ColorSensor:
#     def __init__(self):
#         self.sensor = self._initialize_sensor()
        
#     def _initialize_sensor(self):
#         i2c = board.I2C()
#         try:
#             sensor = adafruit_tcs34725.TCS34725(i2c)
#              # print(f"sensor {sensor}")
#             sensor.integration_time = 50  # 50ms
        
#             sensor.gain = 4  # 4x gain
#             return sensor
#         except ValueError:
#             raise RuntimeError("TCS34725 not found. Check connections.")
    
#     def get_raw_rgbc(self):
#         """Return (R, G, B, C) as integers"""
#         return self.sensor.color_raw

# # Test the sensor
# if __name__ == "__main__":
#     sensor = ColorSensor()
#     while True:
#         r, g, b, c = sensor.get_raw_rgbc()
#         print(f"R: {r:4d}  G: {g:4d}  B: {b:4d}  C: {c:4d}")
#         time.sleep(0.5)

import smbus2
import time

class TCS34725:
    def __init__(self, bus=1):
        self.bus = smbus2.SMBus(bus)
        self.addr = 0x29
        
        # Initialize sensor
        self._write(0x80 | 0x00, 0x03)  # Enable power and RGBC
        self._write(0x80 | 0x01, 0x00)  # 50ms integration time
        self._write(0x80 | 0x0F, 0x00)  # 4x gain
        time.sleep(0.7)  # Initial stabilization

    def _write(self, reg, value):
        self.bus.write_byte_data(self.addr, reg, value)

    def read_raw(self):
        data = self.bus.read_i2c_block_data(self.addr, 0x80 | 0x14, 8)
        c = (data[1] << 8) | data[0]
        r = (data[3] << 8) | data[2]
        g = (data[5] << 8) | data[4]
        b = (data[7] << 8) | data[6]
        return r, g, b, c

if __name__ == "__main__":
    sensor = TCS34725(bus=1)
    while True:
        r, g, b, c = sensor.read_raw()
        print(f"R: {r:4d}  G: {g:4d}  B: {b:4d}  C: {c:4d}")
        time.sleep(0.5)