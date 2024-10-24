import pygame as pg
from settings import *
from objects.sprites import SpriteObject

class Item(SpriteObject):
    def __init__(self, game, x, y, tile):

        super().__init__(
            game, 
            x, 
            y, 
            tile,
            layer=SPRITE_LAYER, 
            image=None,
        )
        self.game.can_collect_list.add(self)
        self.collision_rect = self.rect

class SkillPoint(Item):
    def __init__(self, game, x, y, tile):

        super().__init__(game, x, y, tile)

    def load_image(self):
        return self.game.sprites.load_from_spritesheet(
                "assets/items/global_shadow.png",
                topleft=(131,160),
                width=10,
                height=16,
                resize=(20,32)
            )