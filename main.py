import pygame as pg
from settings import *
from map.map import Map
from map.camera import Camera
import sys
from objects.player.player import Player
from objects.inventory import *
from ui.compass import Compass
from ui.bars import HealthBar
from ui.inventory import BackpackInventoryMenu, CampInventoryMenu
from ui.weapon import WeaponMenu
from menus.start import StartMenu
from menus.loadout import LoadoutMenu
from menus.game_over import GameOverMenu
from menus.skill_tree import SkillTreeMenu
from objects.assets import SpriteAssetManager, SoundAssetManager
from objects.npcs.bat import Bat
import uuid
import os
from utility import write_json
import opensimplex
import random
import json
pg.init()


class Game:
    def __init__(self):
        """
        Initialize window and menu settings.
        """
        pg.init()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(TITLE)

        # intitialize the asset managers
        self.sprites = SpriteAssetManager()  
        self.sounds = SoundAssetManager()

        self.game_id = None
        self.playing = False
        self.at_loadout_menu = False
        self.at_start_menu = False
        self.at_game_over = False
        self.at_skilltree_menu = False

    def start_game(self):
        """
        Initialize game objects and settings.
        If a game with this ID exists in the save data, load it.
        If not, create a new game from scratch.
        """
        # initialize the timers and event scheduling variables
        self.clock = pg.time.Clock()
        self.dt = 0
        self.map_reload_timer = 0
        self.health_tick_timer = 0

        # initialize sprite lists and the map 
        # IMPORTANT: Map must go after sprite lists because it creates sprites
        self.sprite_list = pg.sprite.Group() # all sprites to render go in this list
        self.can_collide_list = pg.sprite.Group() # objects the player can collide with, stopping movement
        self.can_collect_list = pg.sprite.Group() # objects the player can collect by colliding with, but should not stop movement
        self.can_axe_list = pg.sprite.Group() # objects the player can hit with their axe
        self.can_sword_list = pg.sprite.Group() # objects the player can hit with their sword
        
        # initialize input-agnostic game objects
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.backpack = Backpack()

        # Load from Save
        if self.game_id:
            if os.path.exists(f"data/saves/{self.game_id}"):

                with open(f"data/saves/{self.game_id}/game.json", "r") as f:
                    game_data = json.load(f)
                    self.seed = game_data.get("seed")
                    opensimplex.seed(self.seed)

                # build map
                self.map = Map(self)
                self.map.new()

                # initialize necessary game objects and variables
                with open(f"data/saves/{self.game_id}/player.json", "r") as f:
                    player_data = json.load(f)
                    saved_loadout = player_data.get("loadout")
                    self.player = Player(self, (CHUNK_SIZE*TILE_SIZE)//2, (CHUNK_SIZE*TILE_SIZE)//2, saved_loadout)

        # Start New Game
        else:
            # set game variables
            self.game_id = str(uuid.uuid4())
            self.seed = random.randint(0,100000)
            opensimplex.seed(self.seed)

            loadout = self.loadout_screen()

            # build map
            self.map = Map(self)
            self.map.new()

            # initialize Player and Player-dependent game objects after loadout is selected
            self.player = Player(self, (CHUNK_SIZE*TILE_SIZE)//2, (CHUNK_SIZE*TILE_SIZE)//2, loadout)
        
        self.backpack_inventory_menu = BackpackInventoryMenu(self)
        self.camp_inventory_menu = CampInventoryMenu(self)
        self.health_bar = HealthBar(self)
        self.weapon_menu = WeaponMenu(self)
        self.compass = Compass(self)

        # move on from the start menu
        self.at_start_menu = False
        self.playing = True

    def save(self):
        """
        Save the current Game data to disk.
        """
        # game data
        write_json(f"data/saves/{self.game_id}/game.json",
            {
                "game_id":self.game_id,
                "seed":self.seed
            }
        )

        # player data
        write_json(f"data/saves/{self.game_id}/player.json",
            {
                "loadout":self.player.loadout,
            }
        )

        # chunk data
        for chunk_id, chunk in self.map.chunks.items():
            chunk.save()
            
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
            # self.player.modify_health(-5) # removed since bats are now added
            self.health_tick_timer = 0

    def draw_layer_if(self, layer, condition=lambda x:True):
        """
        Draw all tiles in visible chunks, passing a layer parameter.
        If a condition is passed, only draw objects if the tile meets that condition.
        """
        tiles = []
        for chunk_id in self.map.get_visible_chunks(self.player, tile_buffer=0):
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
        for chunk_id in self.map.get_visible_chunks():
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
        self.weapon_menu.draw(self.screen)

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

            elif self.at_start_menu:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.start_menu.handle_click(pg.mouse.get_pos())
            elif self.at_loadout_menu:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.loadout_menu.handle_click(pg.mouse.get_pos()) 
            elif self.playing and not self.at_skilltree_menu:
                # open the skilltree menu if I 
                if event.type == pg.KEYDOWN and event.key == pg.K_i:
                    self.skilltree_screen()
                elif event.type == pg.KEYDOWN and pg.K_0 <= event.key <= pg.K_9:
                    self.weapon_menu.handle_keys(event)
            elif self.at_game_over:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.game_over_menu.handle_click(pg.mouse.get_pos())
            elif self.at_skilltree_menu:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.skilltree_menu.handle_click(pg.mouse.get_pos())
                elif event.type == pg.KEYDOWN and event.key == pg.K_i:
                    self.at_skilltree_menu = False

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
        self.start_game()

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
        return self.loadout_menu.get_loadout()

    def skilltree_screen(self):
        """
        Screen where the player can apply skill points they've earned.
        """
        self.skilltree_menu = SkillTreeMenu(self)
        self.at_skilltree_menu = True
        while self.at_skilltree_menu:
            self.events()
            self.skilltree_menu.update(pg.mouse.get_pos())
            self.skilltree_menu.draw()

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
    game.start_screen()
    game.run()