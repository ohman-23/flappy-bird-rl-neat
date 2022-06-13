import pygame
from sprites import Pipe, Bird, Button
from config import Config
from pygame.sprite import Sprite, Group
import random
import numpy as np

def draw_text(screen, text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x,y))

def draw_and_update_sprites(screen, sprite_groups):
    for sprite_group in sprite_groups:
        sprite_group.draw(screen)
        sprite_group.update()
        
def update_score(bird_group, pipe_group):
    if pipe_group:
        closest_bird = bird_group.sprites()[0]
        closest_pipe_right = pipe_group.sprites()[0].rect.right
        bird_left = closest_bird.rect.left
        
        if bird_left > closest_pipe_right and not GameInstance.pipe_passed:
            GameInstance.score += 1
            GameInstance.pipe_passed = True
        
        if bird_left <= closest_pipe_right and GameInstance.pipe_passed:
            GameInstance.pipe_passed = False


def detect_and_handle_collisons(bird_group, pipe_group):
    closest_bird = bird_group.sprites()[0]
    
    # print out velocity, and distance to top and bottom of pipe
    def distance(bird, pipe):
        bird_x, bird_y = bird.rect.center
        if pipe.is_bottom_pipe:
            pipe_x, pipe_y = pipe.rect.topleft
        else:
            pipe_x, pipe_y = pipe.rect.bottomleft
        return np.sqrt((bird_x - pipe_x)**2 + (bird_y - pipe_y)**2)
    
    if closest_bird.rect.bottom > Config.FLOOR_HEIGHT:
        GameInstance.game_over = True
        GameInstance.game_started = False
    
    if pipe_group:
        bottom_closest_pipe = pipe_group.sprites()[0]
        top_closest_pipe = pipe_group.sprites()[1]
        if not GameInstance.game_over:
            print(closest_bird.velocity, distance(closest_bird, bottom_closest_pipe), distance(closest_bird, top_closest_pipe))
        if closest_bird.check_collision(bottom_closest_pipe) or closest_bird.check_collision(top_closest_pipe):
            GameInstance.game_over = True
            
def reset_game(pipe_group, bird_group):
    # reset pipes
    pipe_group.empty()
    # reset birds
    bird_group.empty()    
    flappy_bird = Bird(100, int(Config.SCREEN_HEIGHT/2))
    bird_group.add(flappy_bird)

# define game variables
class GameInstance:
    ground_scroll = 0
    game_started = False
    game_over = False
    last_pipe_generation = 0
    score = 0
    pipe_passed = False

pygame.init()

# configure clock and framerate
clock = pygame.time.Clock()

# define font
font = pygame.font.SysFont("Bauhaus 93", 60)
white = (255,255,255)

# import images
background = pygame.image.load(f"{Config.IMG_PATH}/bg.png")
ground = pygame.image.load(f"{Config.IMG_PATH}/ground.png")
button_img = pygame.image.load(f"{Config.IMG_PATH}/restart.png")

button = Button(Config.SCREEN_WIDTH//2-50, Config.SCREEN_HEIGHT//2-100, button_img)

# add bird sprites - init_game
bird_group = Group()
flappy_bird = Bird(100, int(Config.SCREEN_HEIGHT/2))
bird_group.add(flappy_bird)

# add pipe sprites
pipe_group = Group()

# set screen size and display window
screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Demo")

# game loop
run = True
while run:
    
    clock.tick(Config.FPS)
    
    # draw background
    screen.blit(background, (0,0))
    
    # draw and update sprites
    draw_and_update_sprites(screen, [bird_group, pipe_group])
    
    # collision checks - need to change later
    detect_and_handle_collisons(bird_group, pipe_group)
            
    # score checking
    update_score(bird_group, pipe_group)
    draw_text(screen, str(GameInstance.score), font, white, int(Config.SCREEN_WIDTH/2), 20)
    
    # draw and scroll the ground
    screen.blit(ground, (GameInstance.ground_scroll, Config.FLOOR_HEIGHT))
    if not GameInstance.game_over and GameInstance.game_started:
        time_now = pygame.time.get_ticks()
        if time_now - GameInstance.last_pipe_generation > Config.PIPE_FREQUENCY:
            pipe_height = random.randint(int(Config.PIPE_GAP/2)+100, int(Config.FLOOR_HEIGHT-Config.PIPE_GAP/2-100))
            bottom_pipe = Pipe(Config.SCREEN_WIDTH, pipe_height, bottom_pipe=True)
            top_pipe = Pipe(Config.SCREEN_WIDTH, pipe_height, bottom_pipe=False)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            GameInstance.last_pipe_generation = time_now
        GameInstance.ground_scroll = 0 if abs(GameInstance.ground_scroll) > 35 else (GameInstance.ground_scroll - Config.SCROLL_SPEED)
    
    # event handling
    if GameInstance.game_over:
        button.draw(screen)
        if button.was_clicked():
            # reset game:
            GameInstance.game_over = False
            GameInstance.game_started = False
            GameInstance.score = 0
            reset_game(pipe_group, bird_group)
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not GameInstance.game_started:
                GameInstance.game_started = True
        
        if event.type == pygame.QUIT:
            run = False   
    pygame.display.update()
pygame.quit()
