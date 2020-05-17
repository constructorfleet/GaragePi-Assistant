from garagepi.domain.models.GarageDoor import GarageDoor
from garagepi.framework.usecase import UseCase


class BuildGarageDoorModelUseCase(UseCase):

    __slots__ = ['entity_id']

    def __init__(self, entity_id):
        self.entity_id = entity_id

    def __call__(self, initial_position):
        return GarageDoor(self.entity_id, initial_position)
