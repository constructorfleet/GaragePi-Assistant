from garagepi.framework.usecase.InputPinEventUseCase import InputPinEventUseCase


class HandlePositionChangeUseCase(InputPinEventUseCase):
    """Use case for handling position change."""

    __slots__ = ['pin_position_map', 'set_position']

    def __init__(self, pin_position_map, set_position):
        super().__init__(pin_position_map.keys())
        self.pin_position_map = pin_position_map
        self.set_position = set_position

    def on_event(self, pin, value):
        self.logger.warning('Pin %s, value %s', str(pin), str(value))
        self.logger.warning(str(self.pin_position_map))
        position = self.pin_position_map.get(pin, None)
        if position is None:
            self.logger.warning('no position')
            return
        self.logger.warning('Set position %s', int(position))
        self.set_position(position)
