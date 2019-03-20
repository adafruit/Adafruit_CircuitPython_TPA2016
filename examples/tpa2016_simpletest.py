import adafruit_tpa2016
import busio
import board

i2c = busio.I2C(board.SCL, board.SDA)
tpa = adafruit_tpa2016.TPA2016(i2c)

tpa.fixed_gain = -16
