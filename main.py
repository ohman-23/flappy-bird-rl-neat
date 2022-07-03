import argparse
import os

from flappy_neat_rl.config import Config, InputConfig
from flappy_neat_rl.enums import GameType
from flappy_neat_rl.games.game_classes import HumanPlayableGame, NEATGenerationGame

# NOTE: Activate this environment variable if you are running this progame with WSL and XLaunch
# os.environ["SDL_VIDEODRIVER"] = "x11"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--game_type", type=str, required=False, choices=[str(_type) for _type in GameType]
)
parser.add_argument("--iterations", type=str, required=False)
parser.add_argument("--generation_size", type=int, required=False)

parser.set_defaults(
    game_type="PLAY",
    iterations=200,
    generation_size=300,
)


def parse_cmd_line_args():
    args = parser.parse_args()
    input_config = vars(args)
    return InputConfig(input_config)


def main():
    config = parse_cmd_line_args()
    if config.game_type == GameType.PLAY_GAME:
        # create logic to play a game
        HumanPlayableGame().run()
    elif config.game_type == GameType.PERFORM_NEAT:
        # create logic to run a game
        NEATGenerationGame(config).run()


if __name__ == "__main__":
    main()
