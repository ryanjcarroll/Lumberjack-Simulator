import pygame as pg
from settings import *
from map import *
from os import path
import sys

from objects.tree import Tree
from objects.player import Player
pg.init()

class Game:
    def __init__(self):
        """
        Initialize game object and settings.
        """
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick() / 1000
        self.load_data()
        
    def load_data(self):
        """
        Set resource paths and load sprite images.
        """
        # set resource paths for game assets
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, "maps")

        # set map file
        self.map = Map(path.join(map_folder, "map.txt"))

    def new(self):
        """
        Create a new game by initializing sprite lists and loading game objects based on the mapfile.
        """
        # lists of objects for the game to render
        self.sprite_list = pg.sprite.LayeredUpdates()
        self.player_list = pg.sprite.Group()
        self.tree_list = pg.sprite.Group()

        # load game objects based on the map file
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == "T":
                    Tree(self, col*TILE_SIZE, row*TILE_SIZE)
                elif tile == "P":
                    self.player = Player(self, col*TILE_SIZE, row*TILE_SIZE)

        # initialize a camera object with the selected map dimensions
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        """
        Main game loop.
        """
        self.playing = True
        while(self.playing):
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            
    def quit(self):
        """
        End the game.
        """
        pg.quit()
        sys.exit()

    def update(self):
        """
        Update sprites and camera.
        """
        self.player_list.update()
        self.camera.update(self.player)

    def draw(self):
        """
        Draw screen background, sprites, health and stamina bars.
        """
        self.screen.fill(BG_COLOR)
        for sprite in self.sprite_list: # TODO this can be improved - we only need to draw the sprites which are actually on-screen
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()
            
    def events(self):
        """
        Check for mouse events.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def start_screen(self):
        pass

    def game_over_screen(self):
        pass

# initialize a game object and start running
game = Game()
game.start_screen()
game.new()
game.run() 