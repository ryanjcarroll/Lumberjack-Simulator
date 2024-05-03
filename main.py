import pygame as pg
from settings import *
from map.map import Map
from map.camera import Camera
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
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick() / 1000
        
    def new(self):
        """
        Create a new game by initializing sprite lists and loading game objects based on the mapfile.
        """
        # initialize sprite lists and the map 
        # IMPORTANT: Map must go after sprite lists because it creates sprites
        self.tree_list = pg.sprite.Group()
        self.map = Map(self)

        # initialize necessary game objects and variables
        self.player = Player(self, CHUNK_SIZE*TILE_SIZE//2, CHUNK_SIZE*TILE_SIZE//2)
        self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.visible_chunks = []

    def run(self):
        """
        Main game loop.
        """
        self.playing = True
        timer = 0
        while(self.playing):
            self.dt = self.clock.tick(FPS) / 1000
            # every N seconds, update the map to see if new chunks need to be generated
            timer += self.dt
            if timer >= 1.0:
                self.map.update()
                timer = 0
            self.events()
            self.update()
            self.draw()

    def update(self):
        """
        Update sprites and camera.
        """
        self.player.update()
        self.camera.update(self.player)

    def draw(self):
        """
        Draw images and sprites.
        """
        self.screen.fill(BG_COLOR)
        with self.map.lock:
            for id, chunk in self.map.chunks.items():

                # TODO only draw nearby chunks and strictly visible tiles - could optimize here

                for tile in chunk.tiles:
                    tile.draw(self.screen, self.camera)
                
        self.player.draw(self.screen, self.camera)
                
        pg.display.flip()
            
    def events(self):
        """
        Check for mouse events.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()        

    def start_screen(self):
        pass

    def game_over_screen(self):
        pass

# initialize a game object and start running
game = Game()
game.start_screen()
game.new()
game.run() 