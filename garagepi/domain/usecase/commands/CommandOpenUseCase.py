from garagepi.framework.usecase.CommandUseCase import CommandUseCase


class CommandOpenUseCase(CommandUseCase):
    """Open command use case."""

    def __call__(self):
        if self.garage_door.is_open:
            self.logger.info('Garage is already closed')
            return False
        else:
            self.logger.info('Opening')
            self.write_pin()
            return True
