import os

from flappy_neat_rl.enums import GAME_TYPE_MAP


class Config:
    IMG_PATH = f"{os.getcwd()}/flappy_neat_rl/images"
    SCROLL_SPEED = 4
    FPS = 60
    FLAP_COOLDOWN = 5
    SCREEN_WIDTH = 550
    SCREEN_HEIGHT = 936
    FLOOR_HEIGHT = 768
    CEILING_HEIGHT = 0
    GRAVITY = 1
    GRAVITY_LIMIT = 10  # 15 before
    JUMP_STRENGTH = 2  # 3 before
    PIPE_GAP = 175
    PIPE_FREQUENCY = 1600  # 1500 before # in milliseconds
    SAVE_DIRECTORY = ""


class InputConfig:
    def __init__(self, config):
        for k, v in config.items():
            setattr(self, k, v)
        self._format_inputs()

    def _format_inputs(self):
        if GAME_TYPE_MAP.get(self.game_type, None) is None:
            raise ValueError(f"{self.game_type} is not an available GameType")
        self.game_type = GAME_TYPE_MAP.get(self.game_type, None)

        # TODO: Configure other attrs

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return print(vars(self))
