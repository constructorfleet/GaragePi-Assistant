import json

from garagepi import ENTITY_ID, NEW_STATE, OLD_STATE, EVENT_TYPE, STATE_CHANGED_EVENT, EVENT_DATA


class StateChangedEvent(dict):
    """State changed event model."""

    def __init__(self, entity_id, new_state, old_state):
        super().__init__()
        self[EVENT_TYPE] = STATE_CHANGED_EVENT
        self[EVENT_DATA] = {
            ENTITY_ID: entity_id,
            NEW_STATE: new_state
        }
        if old_state:
            self[EVENT_DATA][OLD_STATE] = old_state

    def __str__(self) -> str:
        return json.dumps(self)
