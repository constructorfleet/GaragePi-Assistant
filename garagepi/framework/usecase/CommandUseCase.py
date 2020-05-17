from time import sleep

from garagepi.data.rpi import gpio
from garagepi.framework.usecase import UseCase

DEFAULT_ON_TIME = 10


class CommandUseCase(UseCase):
    """Base class for command use cases."""

    __slots__ = ['pin', 'on_time', 'invert']

    def __init__(
            self,
            pin,
            on_time=DEFAULT_ON_TIME,
            invert=False):
        """Initialize use case."""
        self.pin = pin
        self.on_time = on_time
        self.invert = invert

    def write_pin(self):
        gpio.output(
            self.pin,
            gpio.HIGH if self.invert else gpio.LOW)
        sleep(self.on_time)
        gpio.output(
            self.pin,
            gpio.LOW if self.invert else gpio.HIGH)

    def __call__(self, garage_door):
        """Invoke command use case."""
        self.write_pin()
        return True
