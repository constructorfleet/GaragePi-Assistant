from time import sleep

from garagepi.framework.usecase.CommandUseCase import CommandUseCase


class CommandCloseUseCase(CommandUseCase):
    """Close command use case."""

    def __call__(self, garage_door):
        if garage_door.is_closed:
            self.logger.info('Garage is already closed')
            return False
        else:
            self.logger.info('Closing')
            self.write_pin()
            return True
