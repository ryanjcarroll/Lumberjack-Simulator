from pygame import Rect

DEBUG_MODE = False

# colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
LIGHTER_GREY = (200,200,200)
GREEN = (0, 255, 0)
FOREST_GREEN = (34, 139, 34)
RED = (255, 0, 0)
BLUE = (0,0,255)
YELLOW = (255, 255, 0)
GOLD = (255,215,0)
ORANGE = (255,165,0)

# game settings
WINDOW_WIDTH = 72 * 9
WINDOW_HEIGHT = 72 * 9
CHUNK_SIZE = 32
TILE_SIZE = 72
TITLE = "LUMBERJACK SIMULATOR"
BG_COLOR = LIGHT_GREY
FPS = 60
BIOME_NOISE_FACTOR = .0005

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
PLAYER_ATTACK_DAMAGE = 100 if DEBUG_MODE else 1
PLAYER_MOVE_DISTANCE = 8 if DEBUG_MODE else 3
PLAYER_ATTACK_DISTANCE = 24
PLAYER_SPRITE_HEIGHT = 72
PLAYER_SPRITE_WIDTH = 72
PLAYER_ANIMATION_SPEED = 0.1
PLAYER_COLLISION_RECT = Rect(0,0,0,0) if DEBUG_MODE else Rect(0,0,32,32)
PLAYER_STARTING_HEALTH = 80
PLAYER_MAX_HEALTH = 100

# inventory menu settings
BACKPACK_TILE_SIZE = 28
BACKPACK_MENU_PADDING = 10
BACKPACK_ROW_CAPACITY = 10
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
TREE_HEALTH = 3