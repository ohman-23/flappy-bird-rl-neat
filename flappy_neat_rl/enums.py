from enum import Enum


class BaseEnum(Enum):
    def __str__(self):
        return self.value


class PlayerType(Enum):
    HUMAN = 0
    NEURAL_NETWORK = 1


class GameType(BaseEnum):
    PLAY_GAME = "PLAY"
    PERFORM_NEAT = "NEAT"
    VIEW_RESULT = "VIEW_AI"


GAME_TYPE_MAP = {str(_type): _type for _type in GameType}
