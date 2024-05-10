from pygame import Rect

DEBUG_MODE = True
DEFAULT_LOADOUT = {'body': {'category': 'body1', 'style': 0}, 'hair': {'category': 'bob ', 'style': 0}, 'face': {'category': 'eyes', 'style': 0}, 'shirt': {'category': 'basic', 'style': 0}, 'pants': {'category': 'pants', 'style': 0}, 'accessories': {'category': 'beard', 'style': 0}}

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
LAYER_ORDER = ["body","hair","face","shirt","pants","accessories"]

# render layer settings (0 is drawn first)
BASE_LAYER = 0
DECOR_LAYER = 1
SPRITE_LAYER = 2

# player settings
PLAYER_ATTACK_DAMAGE = 100 if DEBUG_MODE else 1
PLAYER_MOVE_DISTANCE = 8 if DEBUG_MODE else 4
PLAYER_ATTACK_DISTANCE = 24
PLAYER_SPRITE_HEIGHT = 72
PLAYER_SPRITE_WIDTH = 72
PLAYER_ANIMATION_SPEED = 0.1
PLAYER_STARTING_HEALTH = 80
PLAYER_MAX_HEALTH = 100

CHARACTER_COLLISION_WIDTH = 32
CHARACTER_COLLISION_HEIGHT = 32
NPC_MOVE_DISTANCE = 1

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