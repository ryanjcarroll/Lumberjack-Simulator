import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import random
from glob import glob

class Tree(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.tree_list, game.sprite_list
        pg.sprite.Sprite.__init__(self, self.groups)
        game.sprite_list.change_layer(self, TREE_LAYER)

        self.game = game
        self.img_file = random.choice(glob("assets/trees/*.png"))
        self.image = pg.transform.scale(
            remove_padding_and_scale(
                pg.image.load(self.img_file)
            ),
            (TILE_SIZE,TILE_SIZE)
        )
        self.pos = vec(x + TILE_SIZE/2, y + TILE_SIZE/2)
               
        self.rect_width, self.rect_height = 72, 72
        self.rect = pg.Rect(0, 0, self.rect_width, self.rect_height)
        self.rect.center = self.pos

        self.health = TREE_HEALTH

    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.kill()