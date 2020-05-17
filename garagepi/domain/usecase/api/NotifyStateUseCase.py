from garagepi.framework.usecase import UseCase


class NotifyStateUseCase(UseCase):
    """Use case to notify API of state change."""

    __slots__ = ['api']

    def __init__(self, api):
        """Initialize use case."""
        self.api = api

    def __call__(self, garage_door):
        """Invoke data method to report state."""
        self.api.report_state(garage_door)
