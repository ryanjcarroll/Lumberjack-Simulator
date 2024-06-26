import pygame as pg
from settings import *
from map.map import Map
from map.camera import Camera
import sys
from objects.player import Player
from objects.inventory import *
from ui.compass import Compass
from ui.bars import HealthBar
from ui.inventory import BackpackInventoryMenu, CampInventoryMenu
from menus.start import StartMenu
from menus.loadout import LoadoutMenu
from menus.game_over import GameOverMenu
from objects.assets import SpriteAssetManager, SoundAssetManager
from objects.music import MusicPlayer
from objects.builder import Builder
pg.init()

class Game:
    def __init__(self):
        """
        Initialize game object and settings.
        """
        pg.init()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(TITLE)


        # initialize the timers and event scheduling variables
        self.clock = pg.time.Clock()
        self.dt = 0
        self.map_reload_timer = 0
        self.health_tick_timer = 0

        # sprite asset manager
        self.sprites = SpriteAssetManager()  
        self.sounds = SoundAssetManager()

        self.at_loadout_menu = False
        self.at_start_menu = False
        self.at_game_over = False

    def new(self, loadout:dict):
        """
        Create a new game by initializing sprite lists and loading game objects based on the mapfile.
        """
        # initialize sprite lists and the map 
        # IMPORTANT: Map must go after sprite lists because it creates sprites
        self.sprite_list = pg.sprite.Group() # all sprites to render go in this list
        self.character_list = pg.sprite.Group()
        self.can_collide_list = pg.sprite.Group() # objects the player can collide with
        self.can_hit_list = pg.sprite.Group() # objects the player can hit with their axe
        self.buildings_list = pg.sprite.Group() # buildings
        self.map = Map(self)
        self.map.new()
        self.compass = Compass(self)

        # initialize necessary game objects and variables
        self.player = Player(self, (CHUNK_SIZE*TILE_SIZE)//2, (CHUNK_SIZE*TILE_SIZE)//2, loadout)
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.backpack = Backpack()
        self.builder = Builder(self)

        self.backpack_inventory_menu = BackpackInventoryMenu(self)
        self.camp_inventory_menu = CampInventoryMenu(self)
        self.health_bar = HealthBar(self)
    
    def update(self):
        """
        Update sprites and camera.
        """

        # update timers and dt        
        self.dt = self.clock.tick(FPS) / 1000
        self.map_reload_timer += self.dt
        self.health_tick_timer += self.dt

        # call .update() on all sprites
        self.sprite_list.update()
        self.camera.update(self.player)
    
        # every N seconds, update the map to see if new chunks need to be generated
        if self.map_reload_timer >= 1:
            self.map.update()
            self.map_reload_timer = 0
        if self.health_tick_timer >= 15:
            self.player.modify_health(-5)
            self.health_tick_timer = 0

    def draw_layer_if(self, layer, condition=lambda x:True):
        """
        Draw all tiles in visible chunks, passing a layer parameter.
        If a condition is passed, only draw objects if the tile meets that condition.
        """
        tiles = []
        for chunk_id in self.map.get_visible_chunks(self.player):
            with self.map.lock:
                if chunk_id in self.map.chunks:
                    chunk = self.map.chunks[chunk_id]
                else:
                    continue
            for tile in chunk.tiles:
                if condition(tile):
                    tiles.append(tile)
        # draw tiles in order by ascending y coordinate
        for tile in sorted(tiles, key=lambda t: t.y):
            tile.draw(layer, self.screen, self.camera)

    def draw(self):
        """
        Draw images and sprites.
        """
        self.screen.fill(BG_COLOR)

        # draw tiles if they are visible on screen
        for chunk_id in self.map.get_visible_chunks(self.player):
            if chunk_id in self.map.chunks: 
                for tile in self.map.chunks[chunk_id].tiles:
                    if self.camera.is_visible(tile):
                        tile.draw(self.screen, self.camera)

        # draw on-screen objects in layer order, and by ascending Y-coordinate
        for sprite in sorted(
            [sprite for sprite in self.sprite_list if self.camera.is_visible(sprite)]
            ,key = lambda sprite:(sprite.layer, sprite.rect.center[1])
        ):
            sprite.draw(self.screen, self.camera)

        # draw menus 
        self.backpack_inventory_menu.draw(self.screen)
        self.camp_inventory_menu.draw(self.screen)
        self.compass.draw(self.screen) 
        self.health_bar.draw(self.screen)

        if self.at_game_over:
            self.player.game_over_update()

        pg.display.flip()
            
    def events(self):
        """
        Check for mouse events.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()    
            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.at_start_menu:
                    self.start_menu.handle_click(pg.mouse.get_pos())
                elif self.at_loadout_menu:
                    self.loadout_menu.handle_click(pg.mouse.get_pos()) 
                elif self.at_game_over:
                    self.game_over_menu.handle_click(pg.mouse.get_pos())
                # else:
                #     self.builder.add_building()

    def start_screen(self):
        """
        Screen to let the user start a new game.
        """
        self.start_menu = StartMenu(self)
        self.at_start_menu = True
        while self.at_start_menu:
            self.events()
            self.start_menu.update()
            self.start_menu.draw()
        self.at_start_menu = False

    def loadout_screen(self):
        """
        Screen to let the user choose character customization options.
        """
        self.loadout_menu = LoadoutMenu(self)
        self.at_loadout_menu = True
        while self.at_loadout_menu:
            self.events()
            self.loadout_menu.update(pg.mouse.get_pos())
            self.loadout_menu.draw()
        # afterwards, start the gameplay loop
        self.at_loadout_menu = False
        self.new(self.loadout_menu.get_loadout())
        self.run()

    def run(self):
        """
        Main game loop.
        """
        self.playing = True

        while(self.playing):
            self.events()
            self.update()
            self.draw()
        
        # handle game over
        self.at_game_over = True
        self.game_over_menu = GameOverMenu(self)
        while self.at_game_over:
            self.events()
            self.draw()
        self.at_game_over = False
        self.start_screen()

# initialize a game object and start running
game = Game()
menu_loop = True
# loop multiple games in a row if necessary
while menu_loop:
    if DEBUG_MODE:
        loadout = {'body': {'category': 'body1', 'style': 0}, 'hair': {'category': 'bob ', 'style': 0}, 'face': {'category': 'eyes', 'style': 0}, 'shirt': {'category': 'basic', 'style': 0}, 'pants': {'category': 'pants', 'style': 0}, 'accessories': {'category': 'beard', 'style': 0}}
    else:
        game.start_screen()
        loadout = game.loadout_screen()
    game.new(loadout)
    game.run()