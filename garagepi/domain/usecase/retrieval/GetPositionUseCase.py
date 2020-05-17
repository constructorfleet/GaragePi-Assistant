from garagepi.data.rpi import gpio
from garagepi.framework.usecase import UseCase


class GetPositionUseCase(UseCase):
    """Use case to get the current position of the garage door."""

    __slots__ = ['pin_position_map', 'on_level']

    def __init__(self, pin_position_map, on_level):
        """Initialize get position use case."""
        self.pin_position_map = pin_position_map
        self.on_level = on_level

    def __call__(self, *args, **kwargs):
        """Determine position from input pins."""
        for pin, position in self.pin_position_map:
            if gpio.input(pin) == self.on_level:
                return position
        return 0
