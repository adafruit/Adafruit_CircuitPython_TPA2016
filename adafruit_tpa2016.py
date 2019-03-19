# The MIT License (MIT)
#
# Copyright (c) 2019 Kattni Rembor for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_tpa2016`
================================================================================

CircuitPython driver for TPA2016 Class D Amplifier.


* Author(s): Kattni Rembor

Implementation Notes
--------------------

**Hardware:**

* `Adafruit TPA2016 - I2C Control AGC <https://www.adafruit.com/product/1712>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

from micropython import const
import adafruit_bus_device.i2c_device as i2cdevice
from adafruit_register.i2c_bits import RWBits
from adafruit_register.i2c_bit import RWBit

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_TPA2016.git"


class TPA2016:
    # Compression ratio settings
    COMPRESSION_1_1 = const(0x0)  # Ratio 1:1
    COMPRESSION_2_1 = const(0x1)  # Ratio 2:1
    COMPRESSION_4_1 = const(0x2)  # Ratio 4:1
    COMPRESSION_8_1 = const(0x3)  # Ratio 8:1

    # NoiseGate threshold settings
    NOISEGATE_1 = const(0x0)  # 1mV
    NOISEGATE_4 = const(0x1)  # 4mV
    NOISEGATE_10 = const(0x2)  # 10mV
    NOISEGATE_20 = const(0x3)  # 20mV

    _attack_control = RWBits(6, 0x02, 0)
    _release_control = RWBits(6, 0x03, 0)
    _hold_time_control = RWBits(6, 0x04, 0)
    _fixed_gain_control = RWBits(6, 0x05, 0)
    _output_limiter_level = RWBits(5, 0x05, 0)
    _max_gain = RWBits(4, 0x07, 4)

    speaker_enable_r = RWBit(0x01, 7)
    speaker_enable_l = RWBit(0x01, 6)
    amplifier_shutdown = RWBit(0x01, 5)
    reset_fault_r = RWBit(0x01, 4)
    reset_Fault_l = RWBit(0x01, 3)
    reset_thermal = RWBit(0x01, 2)

    noisegate_enable = RWBit(0x01, 0)
    """Enabled by default. Can only be enabled when compression ratio is NOT 1:1."""
    output_limiter_disable = RWBit(0x06, 7)
    """Enabled by default when compression ratio is NOT 1:1. Can only be disabled if compression ratio is 1:1."""

    noisegate_threshold = RWBits(2, 0x06, 5)
    """Only functional when compression ratio is NOT 1:1."""

    compression_ratio = RWBits(2, 0x07, 0)
    """The compression ratio. Ratio settings are: 1:1. 2:1, 4:1, 8:1. Settings options are: 
    COMPRESSION_1_1, COMPRESSION_2_1, COMPRESSION_4_1, COMPRESSION_8_1. Defaults to 4:1."""

    def __init__(self, i2c_bus, address=0x58):
        self.i2c_device = i2cdevice.I2CDevice(i2c_bus, address)

    @property
    def attack_time(self):
        return 0.1067 * self._attack_control

    @attack_time.setter
    def attack_time(self, value):
        self._attack_control = value

    @property
    def release_time(self):
        return 0.0137 * self._release_control

    @release_time.setter
    def release_time(self, value):
        self._release_control = value

    @property
    def hold_time(self):
        return 0.0137 * self._hold_time_control

    @hold_time.setter
    def hold_time(self, value):
        self._hold_time_control = value

    @property
    def fixed_gain(self):
        return self._fixed_gain_control

    @fixed_gain.setter
    def fixed_gain(self, value):
        if -28 <= value <= 30:
            if self.compression_ratio is not 0:
                ratio = (value & 0x3f)
                self._fixed_gain_control = ratio
            self._fixed_gain_control = value
        else:
            raise ValueError("Gain must be -28 to 30!")

    @property
    def output_limiter_level(self):
        return -6.5 + 0.5 * self._output_limiter_level

    @output_limiter_level.setter
    def output_limiter_level(self, value):
        if -6.5 <= value <= 9:
            output = int((value + 6.5) / 0.5)
            self._output_limiter_level = output
        else:
            raise ValueError("Output limiter level must be -6.5 to 9!")

    @property
    def max_gain(self):
        return self._max_gain + 18

    @max_gain.setter
    def max_gain(self, value):
        if 18 <= value <= 30:
            max = value - 18
            self._max_gain = max
        else:
            raise ValueError("Max gain must be 18 to 30!")
