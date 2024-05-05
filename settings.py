from pygame import Rect
from datetime import timedelta

# colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
LIGHTER_GREY = (200,200,200)
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

# sprite settings
SPRITESHEET_TILE_SIZE = 32
SPRITESHEET_NUM_COLUMNS = 8
ACTIONS_TO_LOAD = ["walk","axe","sleep"]
LAYER_ORDER = ["body","hair","face","shirt","pants","accessories"]

# render layer settings (0 is drawn first)
BASE_LAYER = 0
DECOR_LAYER = 1
SPRITE_LAYER = 2

# player settings
PLAYER_ATTACK_DAMAGE = 1
PLAYER_MOVE_DISTANCE = 3
PLAYER_ATTACK_DISTANCE = 36
PLAYER_SPRITE_HEIGHT = 72
PLAYER_SPRITE_WIDTH = 72
PLAYER_ANIMATION_SPEED = 0.1
PLAYER_HITBOX = Rect(0,0,15,15)
PLAYER_STARTING_HEALTH = 80
PLAYER_MAX_HEALTH = 100

# inventory menu settings
BACKPACK_TILE_SIZE = 28
BACKPACK_MENU_PADDING = 10
BACKPACK_ROW_CAPACITY = 4
BACKPACK_NUM_ROWS = 2
CAMP_MENU_PADDING = 10
CAMP_MENU_WIDTH = 28 * 2
CAMP_MENU_HEIGHT = 28

# interface settings
COMPASS_WIDTH = 72
COMPASS_HEIGHT = 72
COMPASS_PADDING = 10
RBAR_WIDTH = 36
RBAR_PADDING = 10

# tree settings
TREE_HEALTH = 5