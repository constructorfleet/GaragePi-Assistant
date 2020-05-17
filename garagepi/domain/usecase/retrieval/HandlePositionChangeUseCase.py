from garagepi.framework.usecase.PinEventUseCase import PinEventUseCase


class HandlePositionChangeUseCase(PinEventUseCase):
    """Use case for handling position change."""

    __slots__ = ['pin_position_map', 'set_position']

    def __init__(self, pin_position_map, set_position):
        super().__init__(pin_position_map.keys())
        self.pin_position_map = pin_position_map
        self.set_position = set_position

    def on_event(self, pin, value):
        position = self.pin_position_map.get(pin, None)
        if position is None:
            return
        self.set_position(position)
