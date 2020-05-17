import abc


class UseCase(abc.ABC):
    """Base abstract usecase."""

    def __call__(self, *args, **kwargs):
        """Implmentation of calling usecase."""
        pass
