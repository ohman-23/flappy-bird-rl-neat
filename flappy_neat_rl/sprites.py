import pygame
from pygame.sprite import Group, Sprite

from flappy_neat_rl.config import Config
from flappy_neat_rl.enums import PlayerType


class Bird(Sprite):
    def __init__(self, x, y, player):
        Sprite.__init__(self)  # this must be done in this format
        self.images = []
        self.image_index = 0
        self.counter = 0
        for num in range(1, 4):
            self.images.append(pygame.image.load(f"{Config.IMG_PATH}/bird{num}.png"))
        self.image = self.images[self.image_index]

        # position of bird sprite
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        # physics variables
        self.velocity = 0
        self.unique_jump = True

        # set player object
        self.player = player

        # state variables
        self.alive = True
        self.state_vector = []

    def _apply_gravity(self):
        self.velocity = (
            Config.GRAVITY_LIMIT
            if self.velocity > Config.GRAVITY_LIMIT
            else self.velocity + Config.GRAVITY
        )
        if self.rect.bottom < 768 and self.rect.top >= 0:
            self.rect.y += int(self.velocity)

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

    def update_state_vector(self, vector):
        self.state_vector = vector

    def check_jump(self):
        player_type = self.player.method()
        if player_type == PlayerType.HUMAN:
            if self.player.jump():
                return True

        elif player_type == PlayerType.NEURAL_NETWORK:
            if self.player.jump(input_vector=self.state_vector):
                return True

        elif player_type == PlayerType.NEAT:
            if self.player.jump(input_vector=self.state_vector):
                return True

    def update(self, game_instance):
        if not game_instance.game_over:
            if game_instance.game_started:
                self._apply_gravity()

            # jump handling
            if self.check_jump():
                self.velocity -= Config.JUMP_STRENGTH

            # handle the animation of the bird
            self.counter += 1
            if self.counter >= Config.FLAP_COOLDOWN:
                self.counter = 0
                self.image_index += 1

            if self.image_index >= len(self.images):
                self.image_index = 0

            # set image and rotation
            self.image = pygame.transform.rotate(self.images[self.image_index], -4 * self.velocity)
        else:
            self.image = pygame.transform.rotate(self.images[self.image_index], -90)
            self._apply_gravity()

    def check_collision(self, pipe):
        PIPE_RECT = pipe.rect
        has_collided = self.rect.colliderect(PIPE_RECT)
        if has_collided:
            return True
        return False


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def was_clicked(self):
        action = False
        # get mouse postion
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
            action = True
        return action


class Pipe(Sprite):
    def __init__(self, x, y, bottom_pipe=True):
        Sprite.__init__(self)  # this must be done in this format
        self.image = pygame.image.load(f"{Config.IMG_PATH}/pipe.png")
        self.is_bottom_pipe = bottom_pipe
        if bottom_pipe:
            self.rect = self.image.get_rect()
            self.rect.topleft = [x, y + int(Config.PIPE_GAP / 2)]
        else:
            # given the pipe is coming from the top, we need to flips the original image on the y axis
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect()
            self.rect.bottomleft = [x, y - int(Config.PIPE_GAP / 2)]

    def update(self, game_instance):
        if not game_instance.game_over:
            self.rect.x -= Config.SCROLL_SPEED
            if self.rect.right < 0:
                self.kill()  # reduce buffer holding pipes by deleting them once they're off screen
