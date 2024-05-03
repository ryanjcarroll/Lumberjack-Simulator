from pygame import Rect
from datetime import timedelta

# colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
GREEN = (0, 255, 0)
FOREST_GREEN = (34, 139, 34)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255,215,0)
ORANGE = (255,165,0)

# game settings
WINDOW_WIDTH = 72 * 9
WINDOW_HEIGHT = 72 * 9
CHUNK_SIZE = 15
TILE_SIZE = 72
TITLE = "LUMBERJACK SIMULATOR"
BG_COLOR = LIGHT_GREY
FPS = 60

# player settings
PLAYER_ATTACK_DAMAGE = 10
PLAYER_MOVE_DISTANCE = 3
PLAYER_ATTACK_DISTANCE = 32
PLAYER_SPRITE_HEIGHT = 72
PLAYER_SPRITE_WIDTH = 72
PLAYER_ANIMATION_SPEED = 0.1
PLAYER_HITBOX = Rect(0,0,15,15)

# tree settings
TREE_HEALTH = 2