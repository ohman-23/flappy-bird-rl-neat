import os
import random
import time
from abc import ABC, abstractmethod

import pygame
from flappy_neat_rl.config import Config
from flappy_neat_rl.sprites import Bird, Button, Pipe
from pygame.sprite import Group


class GameInstance:
    ground_scroll = 0
    game_started = False
    game_over = False
    last_pipe_generation = 0
    score = 0
    pipe_passed = False


class Game(ABC):
    def __init__(self, game_type):
        self.game_instance = GameInstance()
        self.game_type = game_type
        self.ticks = 0

    @abstractmethod
    def create_bird_sprites(self, bird_group, **kwargs):
        pass

    @abstractmethod
    def detect_and_handle_collisons(self, bird_group, pipe_group):
        pass

    @abstractmethod
    def perform_game_clean_up(self):
        pass

    @abstractmethod
    def reset_game(self):
        pass

    def draw_text(self, screen, text, font, text_color, x, y):
        img = font.render(text, True, text_color)
        screen.blit(img, (x, y))

    def draw_and_update_sprites(self, screen, sprite_groups):
        for sprite_group in sprite_groups:
            sprite_group.draw(screen)
            sprite_group.update(self.game_instance)

    def update_score(self, bird_group, pipe_group):
        if pipe_group and bird_group:
            closest_bird = bird_group.sprites()[0]
            closest_pipe_right = pipe_group.sprites()[0].rect.right
            bird_left = closest_bird.rect.left

            if bird_left > closest_pipe_right and not self.game_instance.pipe_passed:
                self.game_instance.score += 1
                self.game_instance.pipe_passed = True

            if bird_left <= closest_pipe_right and self.game_instance.pipe_passed:
                self.game_instance.pipe_passed = False

    def create_pipe_sprite(self, pipe_group, x_coord=Config.SCREEN_WIDTH):
        pipe_height = random.randint(
            int(Config.PIPE_GAP / 2) + 25, int(Config.FLOOR_HEIGHT - Config.PIPE_GAP / 2 - 25)
        )
        bottom_pipe = Pipe(x_coord, pipe_height, bottom_pipe=True)
        top_pipe = Pipe(x_coord, pipe_height, bottom_pipe=False)
        pipe_group.add(bottom_pipe)
        pipe_group.add(top_pipe)

    def run(self):
        pygame.init()

        # configure clock and framerate
        clock = pygame.time.Clock()

        # define font
        font = pygame.font.SysFont("Bauhaus 93", 60)
        white = (255, 255, 255)

        # import images
        background = pygame.image.load(f"{Config.IMG_PATH}/bg.png")
        ground = pygame.image.load(f"{Config.IMG_PATH}/ground.png")

        # initialize bird sprites
        bird_group = Group()
        self.create_bird_sprites(bird_group)

        # add pipe sprites
        pipe_group = Group()

        # set screen size and display window
        screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(f"Flappy Bird - {str(self.game_type)}")
        time.sleep(1)

        run = True
        while run:
            self.ticks += 1
            clock.tick(Config.FPS)

            # we want this logic to run first so that we are guaranteed to have a pipe created before
            # we run collision detection logic
            if not self.game_instance.game_over and self.game_instance.game_started:
                time_now = pygame.time.get_ticks()
                if time_now - self.game_instance.last_pipe_generation > Config.PIPE_FREQUENCY:
                    self.create_pipe_sprite(pipe_group)
                    self.game_instance.last_pipe_generation = time_now
                self.game_instance.ground_scroll = (
                    0
                    if abs(self.game_instance.ground_scroll) > 35
                    else (self.game_instance.ground_scroll - Config.SCROLL_SPEED)
                )

            # draw background
            screen.blit(background, (0, 0))

            # collision checks - need to change later
            self.detect_and_handle_collisons(bird_group, pipe_group)

            # draw and update sprites
            self.draw_and_update_sprites(screen, [bird_group, pipe_group])

            # draw and scroll the ground
            screen.blit(ground, (self.game_instance.ground_scroll, Config.FLOOR_HEIGHT))

            # score checking
            self.update_score(bird_group, pipe_group)
            self.draw_text(
                screen,
                str(self.game_instance.score),
                font,
                white,
                int(Config.SCREEN_WIDTH / 2),
                20,
            )

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_instance.game_started:
                        self.game_instance.game_started = True

                if event.type == pygame.QUIT:
                    run = False
            if self.game_instance.game_over == True:
                play_again = self.perform_game_clean_up(pipe_group, bird_group)
                if not play_again:
                    run = False
            pygame.display.update()
        pygame.quit()
