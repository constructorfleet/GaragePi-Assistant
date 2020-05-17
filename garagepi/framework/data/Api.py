"""Remote Data Implementations."""
import abc
import logging

from garagepi.common.const import SERVICE, SERVICE_DATA, ENTITY_ID, SERVICE_OPEN, SERVICE_CLOSE, \
    COMMAND_OPEN, COMMAND_CLOSE, CONF_ENTITY_ID
from garagepi.common.validation import VALID_COMMANDS


class Api(abc.ABC):
    """Abstract remote data interface."""

    _is_connected = False

    def __init__(self, configuration):
        """Initialize the remote data interface."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = self._validate_configuration(configuration)
        # self._command_listener = command_listener

    @abc.abstractmethod
    def _initialize(self):
        pass

    def _validate_configuration(self, configuration):
        raise NotImplementedError()

    def _process_event(self, event):
        event_type = event.get('event_type', None)
        event_data = event.get('data', {})
        service = event_data.get(SERVICE, None)
        service_data = event_data.get(SERVICE_DATA, None)
        entity_ids = service_data.get(ENTITY_ID, self.config[CONF_ENTITY_ID])
        entity_ids = [entity_ids] if isinstance(entity_ids, list) else entity_ids
        if not (event_type == 'call_service' and
                service in [SERVICE_OPEN, SERVICE_CLOSE] and
                self.config[CONF_ENTITY_ID] in entity_ids):
            return

        self.on_command(COMMAND_OPEN if service == SERVICE_OPEN else COMMAND_CLOSE)

    def report_state(self, garage_door):
        """Report the state of the garage door to the remote data interface."""
        raise NotImplementedError()

    def on_command(self, command):
        """"Handler for receiving a command."""
        if command not in VALID_COMMANDS:
            raise ValueError('Invalid command received')
        self._command_listener.on_command(command)


class CommandListener(abc.ABC):
    """Abstract listener for commands to process."""

    def on_command(self, command):
        pass
