from objects.sprite_object import SpriteObject
from settings import *
import pygame as pg

class Backpack:
    def __init__(self):
        self.wood = 0

        self.row_capacity = BACKPACK_ROW_CAPACITY
        self.num_rows = BACKPACK_NUM_ROWS

    def add_wood(self, n=1):
        self.wood += n
        self.wood = min(self.wood, self.row_capacity*self.num_rows)

    def unpack(self, camp):
        camp.add_wood(n=self.wood)
        self.wood = 0

class Camp(SpriteObject):
    def __init__(self, game, x ,y):
        super().__init__(
            game=game,
            x=x,
            y=y,
            layer=SPRITE_LAYER,
            img_path="assets/decor/camp/1.png",
            img_resize=(72,72),
            collision=True
        )

        self.wood = 0
        self.collision_rect = self.rect

    def add_wood(self, n=1):
        self.wood += n