import abc

from garagepi.data.rpi import gpio
from garagepi.framework.usecase import UseCase


class PinEventUseCase(UseCase, abc.ABC):
    """Base class for retrieval use cases."""

    __slots__ = ['pins']

    def __init__(self, pins):
        """Initialize retrieval use case."""
        self.pins = pins

    def __call__(self, *args, **kwargs):
        for pin in self.pins:
            gpio.add_event_detect(pin, gpio.RISING)
            gpio.add_event_callback(pin, self._pin_event_callback)

    def _pin_event_callback(self, pin):
        self.on_event(pin, gpio.input(pin))

    @abc.abstractmethod
    def on_event(self, pin, value):
        """Pin event callback."""
        pass