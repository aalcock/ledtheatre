ledtheatre
==========

A simple application to control the `Adafruit PCA9685 PWM`_ control board.

You can control up to 16 LEDs. Build a simple, fluent-style data object 
describing the changes to each LED intensity and how long the change takes, and 
set it running.

    >>> # load the library and initialise
    >>> import ledtheatre
    >>> ledtheatre.init(pca9685)
    >>>
    >>> # Create a Sequence object
    >>> sequence = Sequence()
    >>>
    >>> # Initialise it with a half-second transition, setting
    >>> #    LED#0 to fade up to 100% brightness, and
    >>> #    LED#1 to fade up to target 50% brightness
    >>> sequence.transition(0.5).target(0, 1.0).target(1, 0.5)
    >>>
    >>> # Add another transition, this time over 1 second
    >>> #    LED#0 to fade completely out, and
    >>> #    LED#1 to target 100% brightness
    >>> sequence.transition(1.0).target(0, 0.0).target(1, 1.0)
    >>>
    >>> # Transitions without any targets are essentially pauses
    >>> sequence.transition(1.0)
    >>>
    >>> # New Transition, over 2 seconds, targeting ONLY LED#1 at 50%
    >>> sequence.transition(2.0).target(1, 0.5)
    >>>
    >>> # Transitions without a duration (or with a 0 second duration) change
    >>> # LEDs instantaneously
    >>> sequence.transition().target(1, 0.0)
    >>>
    >>> # And get those LEDs fading in and out!
    >>> sequence.run()


.. _Adafruit PCA9685 PWM: https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all