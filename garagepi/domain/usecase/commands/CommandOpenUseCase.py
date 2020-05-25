from garagepi.framework.usecase.CommandUseCase import CommandUseCase


class CommandOpenUseCase(CommandUseCase):
    """Open command use case."""

    def __call__(self):
        if self.garage_door.is_open:
            self.logger.warning('Garage is already closed')
            return False
        else:
            self.logger.warning('Opening')
            self.write_pin()
            return True
