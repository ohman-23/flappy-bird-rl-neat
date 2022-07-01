import os


class Config:
    IMG_PATH = f"{os.getcwd()}/flappy_neat_rl/images"
    SCROLL_SPEED = 4
    FPS = 30
    FLAP_COOLDOWN = 5
    SCREEN_WIDTH = 864
    SCREEN_HEIGHT = 936
    FLOOR_HEIGHT = 768
    GRAVITY = 0.75
    GRAVITY_LIMIT = 15  # 15 before
    JUMP_STRENGTH = 5  # 12 before
    PIPE_GAP = 150
    PIPE_FREQUENCY = 3500  # 1500 before # in milliseconds
    SAVE_DIRECTORY = ""
