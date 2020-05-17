import abc
import logging


class UseCase(abc.ABC):
    """Base abstract usecase."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def __call__(self, *args, **kwargs):
        """Implmentation of calling usecase."""
        pass
