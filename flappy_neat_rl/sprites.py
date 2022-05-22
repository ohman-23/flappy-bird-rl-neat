import pygame
from config import Config
from pygame.sprite import Sprite, Group
from enums import PlayerType

class Bird(Sprite):
    def __init__(self, x, y, player):
        Sprite.__init__(self) # this must be done in this format
        self.images = []
        self.image_index = 0
        self.counter = 0
        for num in range(1, 4):
            self.images.append(pygame.image.load(f"{Config.IMG_PATH}/bird{num}.png"))
        self.image = self.images[self.image_index]
        
        # position of bird sprite
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        
        # physics variables
        self.velocity = 0
        self.unique_jump = True

        # set player object
        self.player = player
    
    def _apply_gravity(self):
        self.velocity = Config.GRAVITY_LIMIT if self.velocity > Config.GRAVITY_LIMIT else self.velocity+Config.GRAVITY
        if self.rect.bottom < 768 and self.rect.top >= 0:
            self.rect.y += int(self.velocity)

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
    
    def update(self, GameInstance):
        if not GameInstance.game_over:
            if GameInstance.game_started:
                self._apply_gravity()

            # TODO - figure out how to pass in input vectors to NN
            # jump handling
            player_type = self.player.method()
            if player_type == PlayerType.HUMAN:
                if self.player.jump():
                    self.velocity -= Config.JUMP_STRENGTH

            if player_type == PlayerType.NEURAL_NETWORK:
                if self.player.jump():
                    self.velocity -= Config.JUMP_STRENGTH
            # handle the animation of the bird
            self.counter += 1
            if self.counter >= Config.FLAP_COOLDOWN:
                self.counter = 0
                self.image_index += 1

            if self.image_index >= len(self.images):
                self.image_index = 0

            # set image and rotation
            self.image = pygame.transform.rotate(self.images[self.image_index], -4*self.velocity)
        else: 
            self.image = pygame.transform.rotate(self.images[self.image_index], -90)
            self._apply_gravity()
            
    def check_collision(self, pipe):
        PIPE_RECT = pipe.rect
        has_collided = self.rect.colliderect(PIPE_RECT)
        if has_collided:
            return True
        return False

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
    
    def was_clicked(self):
        action = False
        # get mouse postion
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
            action = True
        return action    