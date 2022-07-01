import argparse

from flappy_neat_rl.config import Config
from flappy_neat_rl.enums import GAME_TYPE_MAP, GameType
from flappy_neat_rl.game_types import HumanPlayableGame

parser = argparse.ArgumentParser()
parser.add_argument(
    "--game_type", type=str, required=False, choices=[str(_type) for _type in GameType]
)
parser.add_argument("--iterations", type=str, required=False)
parser.add_argument("--player_count", type=int, required=False)

parser.set_defaults(
    game_type="PLAY",
)

import os

os.environ["SDL_VIDEODRIVER"] = "x11"


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


def parse_cmd_line_args():
    args = parser.parse_args()
    input_config = vars(args)
    return InputConfig(input_config)


def main():
    config = parse_cmd_line_args()
    if config.game_type == GameType.PLAY_GAME:
        # create logic to play a game
        HumanPlayableGame().run()


if __name__ == "__main__":
    main()
