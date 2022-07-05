import random
from typing import List

import numpy as np
from flappy_neat_rl.config import Config, InputConfig
from flappy_neat_rl.enums import GameType
from flappy_neat_rl.games.game import Game
from flappy_neat_rl.players.player_classes import (
    BirdHumanPlayer,
    BirdNEATPlayer,
    BirdNN,
    BirdNNPlayer,
)
from flappy_neat_rl.sprites import Bird, Pipe
from flappy_neat_rl.utils import bird_to_pipe_distance, bird_to_pipe_xy, norm_vector
from pygame.sprite import Group, Sprite


class HumanPlayableGame(Game):
    def __init__(self):
        super(HumanPlayableGame, self).__init__(GameType.PLAY_GAME)

    def create_bird_sprites(self, bird_group, **kwargs):
        human_player = BirdHumanPlayer()
        bird_group.add(Bird(100, int(Config.SCREEN_HEIGHT / 2), human_player))

    def detect_and_handle_collisons(self, bird_group, pipe_group):
        closest_bird = bird_group.sprites()[0]

        # check if the main bird has hit the bottom of the screen
        if closest_bird.rect.bottom > Config.FLOOR_HEIGHT:
            self.game_instance.game_over = True
            self.game_instance.game_started = False

        # check if the main bird has hit the pipe closest to the bird (aka first-index pipe)
        if pipe_group:
            bottom_closest_pipe = pipe_group.sprites()[0]
            top_closest_pipe = pipe_group.sprites()[1]
            if closest_bird.check_collision(bottom_closest_pipe) or closest_bird.check_collision(
                top_closest_pipe
            ):
                self.game_instance.game_over = True

    def perform_game_clean_up(self, pipe_group, bird_group):
        print("CONSOLE: Do you wish to play again?")
        while True:
            user_input = input().strip().lower()
            if user_input == "yes":
                self.game_instance.game_over = False
                self.game_instance.game_started = False
                self.game_instance.score = 0
                self.reset_game(pipe_group, bird_group)
                return True
            elif user_input == "no":
                return False
            else:
                print("CONSOLE: Please enter 'yes' or 'no' (case-insensitive)")

    def reset_game(self, pipe_group, bird_group):
        # reset game timers
        self.ticks = 0
        # reset pipes
        pipe_group.empty()
        # reset birds
        bird_group.empty()
        self.create_bird_sprites(bird_group)
        self.game_instance.last_pipe_generation = 0


# NOTE: you will have to find a place to save the distace vector for all of the birds!
class GeneticAlgorithmGame(Game):
    def __init__(self, config: InputConfig):
        super(GeneticAlgorithmGame, self).__init__(GameType.PERFORM_GA)
        self.config = config
        self.fallen_birds = []
        self.new_generation_weights = []
        # you are going to need to define other factors here as well (like a dead bird buffer)

        # this needs to be set so in game effects are applied immediately
        self.game_instance.game_started = True

    def create_bird_sprites(self, bird_group, **kwargs):
        # !TODO: populate bird nn with input arguments (hidden_layers, inner_dims, activation, weights)
        nn_players: List[BirdNNPlayer] = kwargs.get("nn_players", None)
        for i in range(self.config.generation_size):
            if nn_players is None:
                ai_player = BirdNNPlayer(BirdNN())
            else:
                ai_player = nn_players[i]
            # add random starting heights?

            bird_group.add(Bird(100, random.randint(10, 500), ai_player))

    def _handle_bird_death(self, bird):
        self.fallen_birds.insert(0, bird.player)
        bird.kill()

    def detect_and_handle_collisons(self, bird_group, pipe_group):
        # NOTE: The fitness function is how long a bird survives, this implemented by having the
        # birds that survive the longest appeart in ealier indexes
        for bird in bird_group.sprites():
            # check if the main bird has hit the bottom of the screen
            # We do not want birds who hit the top of the screen to move on
            if bird.rect.bottom > Config.FLOOR_HEIGHT - 10:
                bird.player.update_fitness(-1)
                self._handle_bird_death(bird)

            if bird.rect.top == Config.CEILING_HEIGHT:
                bird.player.update_fitness(-1)
                self._handle_bird_death(bird)

            bottom_closest_pipe = pipe_group.sprites()[0]
            top_closest_pipe = pipe_group.sprites()[1]
            if bird.check_collision(bottom_closest_pipe) or bird.check_collision(top_closest_pipe):
                self._handle_bird_death(bird)

            # give bird small reward for staying alive:
            bird.player.update_fitness(0.01)

            # check if bird has made it through a pipe
            if self.game_instance.score > bird.player.past_score:
                bird.player.past_score = self.game_instance.score
                bird.player.update_fitness(1)

            # bird is still alive, so update the state vector for the bird NN (this helps it)
            # to determine whether to jump or not
            bottom_x, bottom_y = bird_to_pipe_xy(bird, bottom_closest_pipe)
            top_x, top_y = bird_to_pipe_xy(bird, top_closest_pipe)
            bird.state_vector = np.array([bird.velocity, top_x, top_y, bottom_y])

        if not bird_group:
            self.game_instance.game_over = True
            self.game_instance.game_started = False

    def _get_parent_indexes(self):
        parent1_ind = random.randint(0, 9)
        parent2_ind = random.randint(0, 9)
        while parent1_ind == parent2_ind:
            parent2_ind = random.randint(0, 9)
        return parent1_ind, parent2_ind

    def _create_new_generation(self, bird_list: List[BirdNNPlayer]):
        # take the top 10 birds and randomly mate them to create (generation size)
        # new birds
        new_generation_ai_players = []
        for _ in range(self.config.generation_size):
            ind1, ind2 = self._get_parent_indexes()
            nn_player1, nn_player2 = bird_list[ind1], bird_list[ind2]
            new_generation_ai_players.append(nn_player1.mate(nn_player2))

        return new_generation_ai_players

    def perform_game_clean_up(self, pipe_group, bird_group):
        self.config.iterations -= 1
        if not self.config.iterations:
            # Write outputs and show where training dir is?
            return False
        self.game_instance.game_over = False
        self.game_instance.game_started = False
        self.game_instance.score = 0
        self.reset_game(pipe_group, bird_group)
        return True

    def reset_game(self, pipe_group, bird_group):
        # reset game timers
        self.ticks = 0
        # reset pipes
        pipe_group.empty()
        # reset birds
        bird_group.empty()

        # mating procedure - create a fiter generation
        self.fallen_birds = list(
            sorted(self.fallen_birds, key=lambda player: player.fitness, reverse=True)
        )
        new_bird_nn_players = self._create_new_generation(self.fallen_birds)
        self.create_bird_sprites(bird_group, nn_players=new_bird_nn_players)

        # clear fallen birds queue
        self.fallen_birds.clear()
        # clear new weights queue
        self.new_generation_weights.clear()
        # this has to be present for the game to immediately begin after reset
        self.game_instance.game_started = True
        self.game_instance.last_pipe_generation = 0


class NEATGame(Game):
    def __init__(self, genomes, neat_config):
        super(NEATGame, self).__init__(GameType.PERFORM_NEAT)
        self.genomes = genomes
        self.config = neat_config

        # this needs to be set so in game effects are applied immediately
        self.game_instance.game_started = True

    def create_bird_sprites(self, bird_group, **kwargs):
        for genome_id, genome in self.genomes:

            ai_player = BirdNEATPlayer(genome, self.config)
            bird_group.add(Bird(100, random.randint(10, 500), ai_player))

    def _handle_bird_death(self, bird):
        bird.kill()

    def detect_and_handle_collisons(self, bird_group, pipe_group):
        for bird in bird_group.sprites():
            # check if the main bird has hit the bottom of the screen
            # We do not want birds who hit the top of the screen to move on
            if bird.rect.bottom > Config.FLOOR_HEIGHT - 5:
                bird.player.update_fitness(-1)
                self._handle_bird_death(bird)

            if bird.rect.top == Config.CEILING_HEIGHT:
                bird.player.update_fitness(-1)
                self._handle_bird_death(bird)

            # check if the main bird has hit the pipe closest to the bird (aka first-index pipe)

            bottom_closest_pipe = pipe_group.sprites()[0]
            top_closest_pipe = pipe_group.sprites()[1]
            if bird.check_collision(bottom_closest_pipe) or bird.check_collision(top_closest_pipe):
                self._handle_bird_death(bird)

            # give bird small reward for staying alive:
            bird.player.update_fitness(0.001)

            # check if bird has made it through a pipe
            if self.game_instance.score > bird.player.past_score:
                bird.player.past_score = self.game_instance.score
                bird.player.update_fitness(1)

            # bird is still alive, so update the state vector for the bird NN (this helps it)
            # to determine whether to jump or not
            bottom_x, bottom_y = bird_to_pipe_xy(bird, bottom_closest_pipe)
            top_x, top_y = bird_to_pipe_xy(bird, top_closest_pipe)

            # update internal state vector
            bird.state_vector = (bird.velocity, top_x, top_y, bottom_y)

        if not bird_group:
            self.game_instance.game_over = True
            self.game_instance.game_started = False

    def perform_game_clean_up(self, *args, **kwargs):
        # we want to destroy this game instance and have the NEAT package update its genomes
        return False

    def reset_game(self):
        pass


class AIDemoGame(Game):
    pass
