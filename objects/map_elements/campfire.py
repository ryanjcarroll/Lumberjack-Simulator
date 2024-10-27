from objects.sprites import SpriteObject
from settings import *
import pygame as pg
from utility import remove_padding

class Campfire(SpriteObject):
    def __init__(self, game, x, y):
        self.game = game        
        self.width = 2*TILE_SIZE//3
        self.height = TILE_SIZE
        self.frames = {}

        # set Campfire's home tile
        for tile in game.map.chunks["0,0"].tiles:
            if CHUNK_SIZE//2 == tile.row and CHUNK_SIZE//2 - 1== tile.col:
                break

        super().__init__(
            game=game,
            x=x,
            y=y,
            tile=tile,
            layer=SPRITE_LAYER,
        )
        
        # fuel burn settings
        self.fuel_capacity = 10
        self.fuel = 10
        self.fuel_drain_timer = 0
        self.fuel_drain = 60 # time to drain 1 fuel, in seconds

        # animation settings
        self.current_frame_index = 0
        self.animation_timer = 0
        self.animation_speed = PLAYER_ANIMATION_SPEED * 2

        # separate (smaller) collision rect for better player collisions
        self.collision_rect = pg.Rect(
            0,
            0,
            self.width,
            self.height // 3
        )
        self.collision_rect.bottomleft = self.rect.bottomleft
        self.game.can_collide_list.add(self)

    def load_image(self):
        self.load_animations()

        return self.frames["fire"][0]

    def add_fuel(self):
        if self.fuel < self.fuel_capacity:
            self.fuel += 1
    
    def load_animations(self):       
        # randomly choose a row to load from the butterfly spritesheet
        # TODO add some better choice algos here         
        self.frames['fire'] = []

        # load the component frame and add to images list
        for col in range(4):
            self.frames["fire"].append(
                pg.transform.scale(
                    remove_padding(
                        self.game.sprites.load_from_tilesheet(
                            path=f"assets/fire/campfire.png",
                            row_index=0,
                            col_index=col,
                            tile_size=64
                        )
                    )
                    ,(self.width, self.height)
                )
            )

    def set_animation_counters(self, dt):
        """
        Increment the animation counters if enough time has passed since the last update.
        """
        self.animation_timer += dt

        if self.fuel_capacity > 0:
            # update walk animation frame if enough time has passed
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"fire"])
                self.animation_timer = 0

    def update(self):
        """
        Called each game step to update this object.
        """
        self.set_animation_counters(self.game.dt)
        
        # set the frame for animations
        if self.fuel_capacity > 0:
            self.image = self.frames["fire"][self.current_frame_index]