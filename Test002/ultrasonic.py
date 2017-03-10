##
# Ultrasonic library for MicroPython's pyboard.
# Compatible with HC-SR04 and SRF04.
#
# Copyright 2014 - Sergio Conde Gómez <skgsergio@gmail.com>
# Improved by Mithru Vigneshwara
# Modified by orsisam <orsi.amax@gmail.com> for
# compatibility with esp8266
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
import machine
import time

class ultrasonic(object):
    def __init__(self, tPin, ePin):
        # WARNING: Don't use PA4-X5 or PA5-X6 as echo pin without a 1k resistor (Attention for PyBoard)
        self.triggerPin = tPin
        self.echoPin = ePin

        # Init trigger pin (out)
        self.trigger = machine.Pin(self.triggerPin)
        self.trigger.init(machine.Pin.OUT, pull=None, value=0)
        #self.trigger.PULL_DOWN()

        # Init echo pin (in)
        self.echo = machine.Pin(self.echoPin)
        self.echo.init(machine.Pin.IN, pull=None)

    def distance_in_inches(self):
        return (self.distance_in_cm() * 0.3937)

    def distance_in_cm(self):
        start = 0
        end = 0

        # Create a microseconds counter.
        #micros = pyb.Timer(2, prescaler=83, period=0x3fffffff)
        #micros.counter(0)

        # Send a 10us pulse.
        self.trigger.high()
        time.sleep_us(10)
        #pyb.udelay(10)
        self.trigger.low()

        # Wait 'till whe pulse starts.
        while self.echo.value() == 0:
            start = time.ticks_us()

        # Wait 'till the pulse is gone.
        while self.echo.value() == 1:
            end = time.ticks_us()

        # Deinit the microseconds counter
        # micros.deinit()

        # take time different between start and end pulse.
        differ = time.ticks_diff(start, end)

        # Calc the duration of the recieved pulse, divide the result by
        # 2 (round-trip) and divide it by 29 (the speed of sound is
        # 340 m/s and that is 29 us/cm).
        dist_in_cm = (differ / 2) / 29

        return dist_in_cm