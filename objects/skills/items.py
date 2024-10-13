import pygame as pg
from settings import *
from objects.sprites import SpriteObject


class Item(SpriteObject):
    def __init__(self, game, x, y):

        super().__init__(
            game, 
            x, 
            y, 
            layer=SPRITE_LAYER, 
            image=None,
            can_collect=True
        )

class Boots(Item):
    def __init__(self, game, x, y):

        super().__init__(game, x, y)

    def load_image(self):
        return pg.transform.scale(
            self.game.sprites.load("assets/items/upgrades/boots.png"),
            (PLAYER_SPRITE_WIDTH//2, PLAYER_SPRITE_HEIGHT//2)
        )