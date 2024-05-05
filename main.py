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

        # default options if no loadout selected
        self.loadout = {
            "character":"char1"
        }

        self.at_loadout_menu = False
        self.at_start_menu = False
        self.at_game_over = False

    def new(self, loadout:dict):
        """
        Create a new game by initializing sprite lists and loading game objects based on the mapfile.
        """
        # initialize sprite lists and the map 
        # IMPORTANT: Map must go after sprite lists because it creates sprites
        self.collision_list = pg.sprite.Group() # objects the player can collide with
        self.decor_list = pg.sprite.Group() # objects the player can walk through and is not able to hit with their axe
        self.hittable_list = pg.sprite.Group() # objects the player can hit with their axe
        self.map = Map(self)
        self.camp = Camp(self)
        self.compass = Compass(self)

        # initialize necessary game objects and variables
        self.player = Player(self, (CHUNK_SIZE*TILE_SIZE)//2, (CHUNK_SIZE*TILE_SIZE)//2, loadout)
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.backpack = Backpack()
        self.visible_chunks = []
        self.backpack_inventory_menu = BackpackInventoryMenu(self)
        self.camp_inventory_menu = CampInventoryMenu(self)
        self.health_bar = HealthBar(self)

    def update(self):
        """
        Update sprites and camera.
        """
        self.player.check_keys()
        self.player.update()
        self.camera.update(self.player)

        self.dt = self.clock.tick(FPS) / 1000
        self.map_reload_timer += self.dt
        self.health_tick_timer += self.dt

        # every N seconds, update the map to see if new chunks need to be generated
        if self.map_reload_timer >= 1:
            self.map.update()
            self.map_reload_timer = 0
        if self.health_tick_timer >= 10:
            self.player.health -= 1
            self.health_bar.update()
            self.health_tick_timer = 0

    def draw(self):
        """
        Draw images and sprites.
        """
        self.screen.fill(BG_COLOR)

        # draw tile bases if they are in visible chunks
        for chunk_id in self.map.get_visible_chunks(self.player):
            with self.map.lock:
                if chunk_id in self.map.chunks:
                    chunk = self.map.chunks[chunk_id]
                else:
                    continue
            for tile in chunk.tiles:
                tile.draw_base(self.screen, self.camera)
        # once bases are drawn, draw objects in visible chunks
        for chunk_id in self.map.get_visible_chunks(self.player):
            with self.map.lock:
                if chunk_id in self.map.chunks:
                    chunk = self.map.chunks[chunk_id]
                else:
                    continue
            for tile in chunk.tiles:
                tile.draw_objects(self.screen, self.camera)

        # draw player
        self.player.draw(self.screen, self.camera)
        self.camp.draw(self.screen, self.camera)
        
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

    def start_screen(self):
        self.start_menu = StartMenu(self)
        self.at_start_menu = True
        while self.at_start_menu:
            self.events()
            self.start_menu.update()
            self.start_menu.draw()
        self.at_start_menu = False
        game.loadout_screen()

    def loadout_screen(self):
        self.loadout_menu = LoadoutMenu(self)
        self.at_loadout_menu = True
        while self.at_loadout_menu:
            self.events()
            self.loadout_menu.update(pg.mouse.get_pos())
            self.loadout_menu.draw()
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
game.start_screen()