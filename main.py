import pygame as pg
from settings import *
from map.map import Map
from map.camera import Camera
import sys
from objects.player import Player
import datetime
# from utility import calculate_day_night_color_cycle
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
        self.delta_t = 0
        self.map_reload_timer = 0
        # self.time_of_day_timer = 0

        # self.time_of_day = datetime.datetime.combine(
        #     datetime.datetime.today().date(),
        #     datetime.time(6,0,0)
        # )
        # self.time_of_day_filter = calculate_day_night_color_cycle(self.time_of_day)
        
    def new(self):
        """
        Create a new game by initializing sprite lists and loading game objects based on the mapfile.
        """
        # initialize sprite lists and the map 
        # IMPORTANT: Map must go after sprite lists because it creates sprites
        self.collision_list = pg.sprite.Group() # objects the player can collide with
        self.decor_list = pg.sprite.Group() # objects the player can walk through and is not able to hit with their axe
        self.hittable_list = pg.sprite.Group() # objects the player can hit with their axe
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

        while(self.playing):
            self.events()
            self.update()
            self.draw()

    def update(self):
        """
        Update sprites and camera.
        """
        self.player.update()
        self.camera.update(self.player)

        self.delta_t = self.clock.tick(FPS) / 1000
        self.map_reload_timer += self.delta_t
        # self.time_of_day_timer += self.delta_t

        # every N seconds, update the map to see if new chunks need to be generated
        if self.map_reload_timer >= 1:
            self.map.update()
            self.map_reload_timer = 0

        # # every N seconds, update the time of day
        # if self.time_of_day_timer >= 0.1:
        #     self.time_of_day += datetime.timedelta(minutes=15)
        #     self.time_of_day_filter = calculate_day_night_color_cycle(self.time_of_day)
        #     self.time_of_day_timer = 0

    def draw(self):
        """
        Draw images and sprites.
        """
        self.screen.fill(BG_COLOR)

        # draw Tiles if they are in visible Chunks
        for (chunk_x, chunk_y) in self.map.get_visible_chunks(self.player):
            chunk_id = f"{chunk_x},{chunk_y}"
            with self.map.lock:
                if chunk_id in self.map.chunks:
                    chunk = self.map.chunks[chunk_id]
                else:
                    continue
            for tile in chunk.tiles:
                tile.draw_base(self.screen, self.camera)
            for tile in chunk.tiles:
                tile.draw_objects(self.screen, self.camera)

        # draw player
        self.player.draw(self.screen, self.camera)

        # # apply time of day filter
        # self.screen.fill(
        #     self.time_of_day_filter, 
        #     special_flags = pg.BLEND_MULT
        # )

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

# initialize a game object and start running
game = Game()
game.start_screen()
game.new()
game.run() 