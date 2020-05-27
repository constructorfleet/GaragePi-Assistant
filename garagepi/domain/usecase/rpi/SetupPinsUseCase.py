from garagepi.data.rpi import gpio
from garagepi.framework.usecase import UseCase


class SetupPinsUseCase(UseCase):
    """Use case for setting up GPIO pins."""

    __slots__ = ['out_pins', 'in_pins', 'in_down_pins', 'in_up_pins']

    def __init__(self, out_pins=None, in_pins=None, in_down_pins=None, in_up_pins=None):
        """Initialize use case for setting up pins."""
        super().__init__()
        self.out_pins = out_pins or []
        self.in_pins = in_pins or []
        self.in_down_pins = in_down_pins or []
        self.in_up_pins = in_up_pins or []

    def __call__(self, *args, **kwargs):
        self.logger.warning("Setting up pins")
        gpio.setmode(gpio.BCM)
        for pin in self.out_pins:
            if pin is None:
                continue
            self.logger.warning('Setting up %s as in %s', str(pin), 'out')
            gpio.setup(pin, gpio.OUT)
        for pin in self.in_pins:
            if pin is None:
                continue
            self.logger.warning('Setting up %s as in %s', str(pin), 'in')
            gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_OFF)
            self.logger.warning('GPIO IN (PUD-OFF) %s is %s', str(pin), gpio.input(pin))
        for pin in self.in_down_pins:
            if pin is None:
                continue
            self.logger.warning('Setting up %s as in %s', str(pin), 'in down')
            gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
            self.logger.warning('GPIO IN (PUD-DOWN) %s is %s', str(pin), gpio.input(pin))
        for pin in self.in_up_pins:
            if pin is None:
                continue
            self.logger.warning('Setting up %s as in %s', str(pin), 'in up')
            gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)
            self.logger.warning('GPIO IN (PUD-IN) %s is %s', str(pin), gpio.input(pin))
