#import Adafruit_PCA9685
import time

# Instantiate a singleton representing the PWM board
#pwm = Adafruit_PCA9685.PCA9685()

# Holds the last-set brightness of all LEDs
brightnesses = [0.0] * 15


def _validate_led(led):
    if led < 0 or led > 15:
        raise ValueError("led is a number between 0 and 15")


def _validate_brightness(brightness):
    if brightness < 0.0 or brightness > 1.0:
        raise ValueError("Brightness is a number between 0.0 and 1.0")


def _convert_brightness(brightness):
    return int(4096.0 * brightness)


def get_brightness(led):
    """
    Gets the current brightness of an LED.
    :param led: The pin number for the LED on the board (0..15)
    :type led: int
    :return: the brightness where 0.0 represents darkness and 1.0 the brightest.
    """
    _validate_led(led)

    return brightnesses[led]


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

    prev = brightnesses[led]
    if brightness != prev:
        # Only send the instruction to the board if the new value is different
        #pwm.set_pwm(led, 0, _convert_brightness(brightness))
        brightnesses[led] = brightness
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

    def set_brightness(self, brightness):
        """
        Sets the LED brightness
        :param brightness: from 0.0 to 1.0. 0.0 means the dark
        :type brightness: float
        :return: The previous brightness value of the LED
        """
        print("    Setting {} -> {:04.3f}".format(self, brightness))
        return set_brightness(self.led, brightness)

    def __str__(self):
        return "LED#{} [Target {:04.3f}]".format(self.led, self.brightness)


class Transition(object):
    """
    Represents a series of LEDs changing values over a specific duration
    """
    def __init__(self, sequence, duration):
        """
        Creates a new Transition of the specified duration
        :param sequence: The parent Sequence object
        :type sequence: Sequence
        :param duration: the duration in seconds
        :type duration: float
        """
        if duration < 0.0:
            raise ValueError("The duration in a Transition must be greater "
                             "than 0.0")
        self.sequence = sequence
        self.duration = duration
        self.targets = []

    def target(self, led, brightness):
        """
        Add a new LED target to the Transition, specifying the LED and its
        brightness
        :param led: The LED to target, 0..15
        :type led: int
        :param brightness: The brightess of the LED, 0.0 to 1.0
        :type brightness: float
        :return: This Transition object
        """
        self.targets.append(LEDTarget(led, brightness))
        return self

    def next(self):
        """"""
        return self.sequence

    def fade(self):
        """
        Run a crossfade over multiple LEDs
        """
        print("Starting {}".format(self))

        if not self.targets:
            # This transition has no LEDs to cross-fade, so simply sleep
            time.sleep(self.duration)
            return

        start = time.time()
        original = list(brightnesses)

        while True:
            length = time.time() - start
            if length >= self.duration:
                # Handles the case where duration == 0
                fraction = 1.0
            else:
                fraction = length / float(self.duration)

            print "  Complete: {:02.0f}%".format(fraction*100)
            for target in self.targets:
                led = target.led
                brightness = target.brightness
                brightness = _interpolate(original[led], brightness, fraction)
                target.set_brightness(brightness)

            if length > self.duration:
                break

            time.sleep(0.1)

    def __str__(self):
        if self.targets:
            targets = ""
            for target in self.targets:
                targets += ", " + str(target)
            return "Transition over {}s [{}]".format(self.duration, targets[2:])
        else:
            return "Transition [Pause of {}s]".format(self.duration)


class Sequence(object):
    """
    Represents a list of Transitions to run sequentially

    Add Transitions by calling Sequence.transition:

        sequence = Sequence()\
            .transition(5).target(0, 1.0).target(1, 0.5).next()\
            .transition(2).target(0, 0.0).target(1, 1.0).next()\
            .transition(1).next()\
            .transition(5).target(1, 0.0)

        sequence.run()
    """
    def __init__(self):
        self.transitions = []

    def transition(self, duration):
        """
        Creates and adds a new Transition to this Sequence
        :param duration: The duration of the Transition
        :type duration: float
        :return: The newly created Transition
        """
        trans = Transition(self, duration)
        self.transitions.append(trans)
        return trans

    def run(self):
        """Runs the Sequence of Transitions"""
        for transition in self.transitions:
            transition.fade()

    def __str__(self):
        ret = "Sequence:\n"
        for transition in self.transitions:
            ret += "    " + transition
        return ret

if __name__ == "__main__":
    sequence = Sequence()
    sequence \
        .transition(0.5).target(0, 1.0).target(1, 0.5).next() \
        .transition(1.0).target(0, 0.0).target(1, 1.0).next() \
        .transition(1.0).next() \
        .transition(2.0).target(1, 0.5).next() \
        .transition(0.0).target(1, 0.0)

    sequence.run()
