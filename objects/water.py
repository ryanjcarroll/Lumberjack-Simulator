from settings import *
import pygame as pg
from pygame import Vector2 as vec

class Water(pg.sprite.Sprite):
    def __init__(self, game, x, y, tile):
        super().__init__()

        self.game = game
        self.x = x
        self.y = y
        self.tile = tile
        
        self.rect = pg.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        # self.collision_rect = self.rect

        self.width = self.rect.width
        self.height = self.rect.height
        self.pos = vec(self.x + self.width/2, self.y + self.height/2) 

        # make collidable
        # self.game.can_collide_list.add(self)