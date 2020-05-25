from time import sleep

from garagepi.framework.usecase.CommandUseCase import CommandUseCase


class CommandCloseUseCase(CommandUseCase):
    """Close command use case."""

    def __call__(self):
        if self.garage_door.is_closed:
            self.logger.warning('Garage is already closed')
            return False
        else:
            self.logger.warning('Closing')
            self.write_pin()
            return True
