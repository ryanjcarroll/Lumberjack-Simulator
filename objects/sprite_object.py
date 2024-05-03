import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec

class SpriteObject(pg.sprite.Sprite):
    """
    Sprite objects to be loaded within the game.
    """
    def __init__(self, game, x, y, img_path, img_resize:tuple=None, collision=False, hittable=False):

        groups = []
        if collision:
            groups.append(game.collision_list)
        if hittable:
            groups.append(game.hittable_list)
        if not collision and not hittable:
            groups.append(game.decor_list)
        pg.sprite.Sprite.__init__(self, groups)

        self.x = x
        self.y = y
        self.game = game

        self.hittable = hittable
        self.collision = collision

        self.img_path = img_path
        self.img_resize = img_resize
        self.load_texture()

        # the initial x, y is based on topleft coordinate of the sprite
        # howver, the .pos attribute is based on the center coordinate of the sprite
        self.width = self.rect.width
        self.height = self.rect.height
        self.pos = vec(self.x + self.width/2, self.y + self.height/2) 
        self.rect.center = self.pos

    def load_texture(self):
        """
        Set the image based on the image path. If resize was passed, transform the sprite to match the new dimensions.
        """
        # crop and resize if passed
        if self.img_resize:
            self.image = pg.transform.scale(
                remove_padding_and_scale(
                    pg.image.load(
                        self.img_path
                    )
                )
                ,self.img_resize
            )
            self.rect = pg.Rect(0, 0, *self.img_resize)
        # otherwise, load as current size
        else:
            self.image = pg.image.load(
                self.img_path
            )
            self.rect = self.image.get_rect()


    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))

    def to_json(self):
        return {
            "topleft":(self.x, self.y),
            "img_path":self.img_path,
            "resize":self.img_resize,
            "collision":self.collision,
            "hittable":self.hittable
        }