import pygame
from flappy_neat_rl.enums import PlayerType
from flappy_neat_rl.players.player import Player


class BirdHumanPlayer(Player):
    def __init__(self):
        self.score = 0
        self.time_alive = 0
        self.unique_jump = True

    def jump(self, *args, **kwargs):
        if pygame.key.get_pressed()[pygame.K_SPACE] and self.unique_jump:
            return True
        if not pygame.key.get_pressed()[pygame.K_SPACE] and not self.unique_jump:
            self.unique_jump = True
        return False

    def set_score(self, score):
        self.score = score

    def set_time_alive(self, time_alive):
        self.time_alive = time_alive

    def method(self):
        return PlayerType.HUMAN
