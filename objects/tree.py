import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import random
from glob import glob

class Tree(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self, game.collision_list, game.hittable_list)
        self.game = game

        # the initial x, y is based on topleft coordinate of the sprite
        # howver, the .pos attribute is based on the center coordinate of the sprite
        self.pos = vec(x + TILE_SIZE/2, y + TILE_SIZE/2)       
        self.rect = pg.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.rect.center = self.pos

        self.flipped = random.random() > 0.5

        self.load_texture()
        self.health = TREE_HEALTH

    def load_texture(self):
        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                pg.image.load(
                    random.choice(glob("assets/trees/*.png"))
                )
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)
        self.image = scaled_image
        
    def take_damage(self, dmg):
        self.health -= dmg
        if self.health <= 0:
            self.kill()

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))