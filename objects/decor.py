import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec

class Decor(pg.sprite.Sprite):
    """
    Static objects which provide no collision or interactivity.
    """
    def __init__(self, game, x, y, img_path, width, height):
        pg.sprite.Sprite.__init__(self, game.decor_list)
        self.game = game

        self.img_path = img_path
        self.width = width
        self.height = height

        # the initial x, y is based on topleft coordinate of the sprite
        # howver, the .pos attribute is based on the center coordinate of the sprite
        self.pos = vec(x + width/2, y + height/2)       
        self.rect = pg.Rect(0, 0, width, height)
        self.rect.center = self.pos

        self.image = self.load_texture()

    def load_texture(self):
        return pg.transform.scale(
            remove_padding_and_scale(
                pg.image.load(
                    self.img_path
                )
            )
            ,(self.width, self.height)
        )

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))