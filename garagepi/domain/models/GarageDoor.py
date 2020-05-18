import logging
from enum import Enum

_LOGGER = logging.getLogger(__name__)

ATTR_POSITION = 'position'


class DoorState(Enum):
    """State enumerable."""
    CLOSED = 'closed',
    OPENING = 'opening',
    STOPPED = 'stopped',
    OPEN = 'open',
    CLOSING = 'closing'


class GarageDoor:
    """Class representing a garage door instance."""

    in_motion = False
    _position = 0
    _prev_position = 0

    def __init__(self, entity_id, initial_position):
        self.entity_id = entity_id
        self._position = self._prev_position = initial_position

    @property
    def is_closed(self):
        return self._position == 0

    @property
    def is_open(self):
        return self._position == 100

    @property
    def position(self):
        return int(self._position)

    @property
    def prev_position(self):
        return int(self._prev_position)

    @property
    def state(self):
        if not self.in_motion \
                and self.position not in [0, 100]:
            return DoorState.STOPPED.value
        if self.position == self.prev_position:
            self.in_motion = False
            if self.position == 0:
                return DoorState.CLOSED.value
            if 100 == self.position:
                return DoorState.OPEN.value
        if self.position > self.prev_position and self.in_motion:
            return DoorState.OPENING.value
        if self.position < self.prev_position and self.in_motion:
            return DoorState.CLOSING.value

    @property
    def attributes(self):
        return {
            ATTR_POSITION: self._position
        }

    def set_position(self, position):
        self._prev_position = self._position
        self._position = position
        self.in_motion = self._position != self._prev_position
