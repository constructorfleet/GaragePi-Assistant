from garagepi.framework.usecase import UseCase


class SetGarageDoorPositionUseCase(UseCase):
    """Sets the position of the garage door."""

    __slots__ = ['garage_door', 'notify_state']

    def __init__(self, garage_door, notify_state):
        """Initialize use case for setting garage door position."""
        super().__init__()
        self.garage_door = garage_door
        self.notify_state = notify_state

    def __call__(self, position):
        self.garage_door.set_position(position)
        self.notify_state(self.garage_door)
