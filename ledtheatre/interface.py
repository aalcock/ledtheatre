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

from time import time, sleep

# How long to sleep each time round the loop while performing a fade
QUANTUM = 0.05
# How many addressable LED PWMs on the board?
LED_COUNT = 16
# The max value for on/off passed to the PWM - represents 1.0 as max brightness
PCA6685_MAX_BRIGHTNESS = 4095.0

# Holds the last-set brightness of all LEDs
_brightnesses = [None] * LED_COUNT
_pwm = None
_pull_up = False
_warned = False
_default_brightness = 0.0


def init(pwm, pull_up=False):
    """
    Initialse this library by passing in a PCA9685 object
    :param pwm: The Adafruit_PCA9685.PCA9685 object whose LEDs are to be managed
    :param pull_up: Is the PWM pin connected to source or sink on the LED? If
                    the PWM is the sink, and the anode is connected to the VCC
                    pin, then set to True. If the PWM pin provides the anode,
                    then set to False.
    :type pull_up: bool
    """
    if not pwm:
        raise ValueError("A Adafruit_PCA9685.PCA9685 object is required")
    global _pwm, _pull_up, _warned, _default_brightness
    _pwm = pwm
    _pull_up = pull_up
    if _pull_up:
        _default_brightness = 1.0
    else:
        _default_brightness = 0.0
    _warned = False


def _validate_led(led):
    if led < 0 or led > (LED_COUNT - 1):
        raise ValueError("led is a number between 0 and 15")


def _validate_brightness(brightness):
    if brightness < 0.0 or brightness > 1.0:
        raise ValueError("Brightness is a number between 0.0 and 1.0")


def _convert_brightness(brightness):
    return int(PCA6685_MAX_BRIGHTNESS * brightness)


def set_brightness(led, brightness):
    """
    Sets the brightness of an LED returning the previous value.
    :param led: The pin number for the LED on the board (0..15)
    :type led: int
    :param brightness: The brightness, from 0.0 to 1.0
    :type brightness: float:
    :return: the previous brightness
    """
    _validate_led(led)
    _validate_brightness(brightness)

    prev = _brightnesses[led]
    if brightness != prev:
        print("    Setting LED#{} -> {:04.3f}".format(led, brightness))
        # Only send the instruction to the board if the new value is different
        _brightnesses[led] = brightness
        if _pwm:
            if _pull_up:
                _pwm.set_pwm(led, _convert_brightness(brightness), 0)
            else:
                _pwm.set_pwm(led, 0, _convert_brightness(brightness))
        else:
            global _warned
            if not _warned:
                _warned = True
                print "===================================================" \
                      "==================================================="
                print "WARNING: ledtheater has not been initialised with a " \
                      "PCA9685 object - simulating LED brightness changes"
                print "===================================================" \
                      "==================================================="
    return prev


def _interpolate(a, b, fraction):
    """
    Calculate the intermediate value between two values, a and b, if we
    are fraction of the way from a to b
    :param a: Initial value
    :param b: Final value
    :param fraction: How much of b vs. a. 0.0 implies all a. 1.0 means all b
    :return: The intermediate value between a and b
    """
    delta = (b - a) * fraction
    return a + delta


class LEDTarget(object):
    """
    Represents an intended brightness on one LED.
    """
    def __init__(self, led, brightness):
        """

        :param led: The LED number, 0..15
        :type led: int
        :param brightness: The brightness from 0.0 to 1.0
        :type brightness: float
        """
        _validate_led(led)
        _validate_brightness(brightness)
        self.led = led
        self.brightness = brightness

    def __str__(self):
        current = _brightnesses[self.led]
        if current is not None:
            return "LED#{} [Current: {:04.3f}, Target: {:04.3f}]".\
                format(self.led, current, self.brightness)
        else:
            return "LED#{} [Current: Unknown, Target: {:04.3f}]". \
                format(self.led, self.brightness)


class Transition(object):
    """
    Represents a series of LEDs changing values over a specific duration
    """
    def __init__(self, sequence, duration=0.0, closed=False):
        """
        Creates a new Transition of the specified duration
        :param sequence: The parent Sequence object
        :type sequence: Sequence
        :param duration: the duration in seconds
        :type duration: float
        :param closed: If true, no LEDTargets can be added to it
        :type closed: bool
        """
        if duration < 0.0:
            raise ValueError("The duration in a Transition must be greater "
                             "than 0.0")
        self._sequence = sequence
        self._duration = duration
        self._targets = []
        self._closed = closed

    def led(self, led, brightness):
        """
        Add a new LED target to the Transition, specifying the LED and its
        brightness
        :param led: The LED to target, 0..15
        :type led: int
        :param brightness: The brightess of the LED, 0.0 to 1.0
        :type brightness: float
        :return: This Transition object
        """
        if self._closed:
            raise RuntimeError("This Transition cannot have targets set.")
        self._targets.append(LEDTarget(led, brightness))

    def execute(self):
        """
        Run a crossfade over multiple LEDs
        """
        print("Executing {}".format(self))

        if not self._targets:
            # This transition has no LEDs to cross-fade, so simply sleep
            sleep(self._duration)
            return

        start = time()
        original = [ x if x else _default_brightness for x in _brightnesses ]

        while True:
            length = time() - start
            if length >= self._duration:
                # Handles the case where duration == 0
                fraction = 1.0
            else:
                fraction = length / float(self._duration)

            if self._duration:
                print "  Complete: {:02.0f}%".format(fraction*100)

            for target in self._targets:
                led = target.led
                brightness = target.brightness
                brightness = _interpolate(original[led], brightness, fraction)
                set_brightness(led, brightness)

            if length > self._duration:
                break

            sleep(QUANTUM)

    def __str__(self):
        if self._targets:
            targets = ""
            for target in self._targets:
                targets += ", " + str(target)
            if self._duration == 0.0:
                return "Snap: {}".format(targets[2:])
            else:
                return "Transition [Duration: {}s{}]".format(self._duration, targets)
        else:
            return "Pause [Duration: {}s]".format(self._duration)


class Sequence(object):
    """
    Represents a list of Transitions to run sequentially with a fluent builder
    API
    """
    def __init__(self):
        self._transitions = []

    def transition(self, duration=0.0):
        """
        Creates and adds a new Transition to this Sequence
        :param duration: The _duration of the Transition. Leave blank for an
        instantaneous change to the target values
        :type duration: float
        :return: The newly created Transition
        """
        self._transitions.append(Transition(self, duration))
        return self

    def sleep(self, duration):
        """
        Pauses the sequence for the configured number of seconds
        :param duration: Sleeps for this long
        :type duration: float
        :return: Sequence
        """
        self._transitions.append(Transition(self, duration, True))
        return self

    def snap(self):
        """
        Creates an instantaneous transition (a snap) for setting LEDs without
        any fade
        :return: Sequence
        """
        self._transitions.append(Transition(self))
        return self

    def led(self, leds, brightness):
        # type: (object, float) -> Sequence
        """
        Add a new LED target to the Transition, specifying the LED and its
        brightness
        :param led: The LED to target, 0..15, or a list of ints
        :param brightness: The brightess of the LED, 0.0 to 1.0
        :type brightness: float
        :return: This Transition object
        """
        if not self._transitions:
            self._transitions.append(Transition(self))

        transition = self._transitions[-1]

        try:
            for led in leds:
                transition.led(led, brightness)
        except TypeError:
            transition.led(leds, brightness)

        return self

    def execute(self):
        """Executes the Sequence of Transitions"""
        for transition in self._transitions:
            transition.execute()

    def __str__(self):
        ret = "Sequence:\n"
        for transition in self._transitions:
            ret += "    " + transition
        return ret
