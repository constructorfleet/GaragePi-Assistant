import logging

from garagepi.framework.usecase.CommandUseCase import CommandUseCase

_LOGGER = logging.getLogger(__name__)


class CommandCloseUseCase(CommandUseCase):
    """Close command use case."""

    def __call__(self, garage_door):
        if garage_door.is_closed:
            _LOGGER.info('Garage is already closed')
            return False
        else:
            self.write_pin()
            return True
