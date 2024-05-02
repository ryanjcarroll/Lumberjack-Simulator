import pygame as pg
from settings import *
from pygame import Vector2 as vec

class Tree(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.tree_list, game.sprite_list
        pg.sprite.Sprite.__init__(self, self.groups)
        game.sprite_list.change_layer(self, TREE_LAYER)

        self.game = game
        self.image = pg.image.load("assets/tree.png")
        self.pos = vec(x + TILE_SIZE/2, y + TILE_SIZE/2)
        
        self.rect_radius = 20
        self.rect = pg.Rect(0, 0, self.rect_radius * 2, self.rect_radius * 2)
        self.rect.center = self.pos

        self.health = TREE_HEALTH

    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.kill()