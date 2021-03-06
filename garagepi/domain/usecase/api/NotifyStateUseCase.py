from garagepi.framework.usecase import UseCase


class NotifyStateUseCase(UseCase):
    """Use case to notify API of state change."""

    __slots__ = ['api']

    def __init__(self, api):
        """Initialize use case."""
        super().__init__()
        self.api = api

    def __call__(self, garage_door):
        """Invoke data method to report state."""
        self.logger.warning('Reporting %s', str(garage_door))
        self.api.report_state(garage_door)
