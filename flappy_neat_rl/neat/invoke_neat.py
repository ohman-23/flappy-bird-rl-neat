import os
import pickle

from flappy_neat_rl.games.game_classes import NEATGame

import neat


# TODO: Add functionality to birds to jump based on neat outputs (create a neat player)
class NEATRunner:
    @classmethod
    def eval_genomes(cls, genomes, config):
        # each genome returned has both a (genome_id, genome obj) associated with it
        game = NEATGame(genomes, config)
        game.run()

    @classmethod
    def run(cls):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "neat_config.txt")
        neat_config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path,
        )

        population = neat.Population(neat_config)

        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        winner = population.run(cls.eval_genomes, 50)
        print(f"Best Genome:\n{winner}")
        with open("best_neat.obj", "wb") as file:
            pickle.dump(winner, file)
