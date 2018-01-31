# ledtheatre is Licensed under the MIT License
# Copyright 2017 Andrew Alcock
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ledtheatre import init, Sequence

try:
    # Initialise
    from Adafruit_PCA9685 import PCA9685
    init(PCA9685())
except ImportError:
    # This is not important - ledtheatre will issue a warning later
    # We will fall back to simulating the PCA9685
    pass

# A list of all the LED#s used in this example
ALL = [0, 1, 2]

# Two helper Sequences for turning all the LEDs on or off
on = Sequence().led(ALL, 1)
off = Sequence().led(ALL, 0)

# A sample Sequence
fade = Sequence() \
    .led(ALL, 0) \
    .transition(0.5).led(0, 1) \
    .transition(1).led(1, 1).led(0, 0) \
    .transition(1).led(2, 1).led(1, 0) \
    .transition(0.5).led(2, 0) \
    .sleep(1) \
    .snap().led(ALL, 1) \
    .sleep(0.2) \
    .snap().led(ALL, 0)

# Run our Sequence
fade.execute()

# A programmatic example: Chasing LEDs

MAX_LEDS = 16
chase = Sequence()
for i in range(0, MAX_LEDS):
    chase.transition(0.5)
    chase.led(i, 0)
    chase.led((i + 1) % MAX_LEDS, 0.5)
    chase.led((i + 2) % MAX_LEDS, 1.0)

# Run the chase 10 times
chase.execute(10)
