from time import sleep

from garagepi.data.rpi import gpio
from garagepi.framework.usecase import UseCase

DEFAULT_ON_TIME = 10


class CommandUseCase(UseCase):
    """Base class for command use cases."""

    __slots__ = ['pin', 'on_time', 'invert']

    def __init__(self, pin, on_time=DEFAULT_ON_TIME, invert=False):
        """Initialize use case."""
        super().__init__()
        self.pin = pin
        self.on_time = on_time
        self.invert = invert
        self._add_gpio_callbacks()

    def _add_gpio_callbacks(self):
        gpio.add_event_detect(self.pin, gpio.RISING if self.invert else gpio.FALLING)
        gpio.add_event_callback(self.pin, self._pin_event_callback)

    def _pin_event_callback(self, pin, value):
        label = self.__class__.__name__ \
            .replace('Command', '').replace('UseCase', '')
        for idx in range(1, 5):
            self.logger.warning('%s %s', label, str(idx / 5))
            sleep(3)
        self.logger.warning('Closing Garage')
        for position in ['75', '50', '25']:
            if position not in self._position_pins:
                print('{} not in {}'.format(position, self._position_pins))
                continue
            print(position.replace('_pin', ''))
            sleep(3)

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
