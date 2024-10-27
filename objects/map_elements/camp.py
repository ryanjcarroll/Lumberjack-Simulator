from settings import *
from objects.sprites import SpriteObject
import pygame as pg

class Camp(SpriteObject):
    def __init__(self, game, x, y, tile):
        self.game = game        
        super().__init__(
            game=game,
            x=x,
            y=y,
            tile=tile,
            layer=SPRITE_LAYER,
        )
    
        self.wood = 0

        # separate (smaller) collision rect for better player collisions
        self.collision_rect = pg.Rect(
            0,
            0,
            self.width // 2,
            self.height // 2
        )
        self.collision_rect.center = self.rect.center
        self.game.can_collide_list.add(self)
    
    def load_image(self):
        return self.game.sprites.load("assets/decor/camp/1.png", resize=(TILE_SIZE, TILE_SIZE))

    def add_wood(self, n=1):
        self.wood += n