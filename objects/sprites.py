import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec

class SpriteObject(pg.sprite.Sprite):
    """
    Sprite objects to be loaded within the game.
    """
    def __init__(self, game, x, y, layer, image=None, collision=False, hittable=False):

        # initiation variables
        self.x = x
        self.y = y
        self.game = game
        self.render_layer = layer
        self.hittable = hittable
        self.collision = collision

        if image:
            self.image = image
        else:
            self.image = self.load_image() # sets self.image

        # set rect for image positioning and collision_rect for collision with player
        self.rect = self.image.get_rect()

        # the initial x, y is based on topleft coordinate of the sprite
        # howver, the .pos attribute is based on the center coordinate of the sprite
        self.width = self.rect.width
        self.height = self.rect.height
        self.pos = vec(self.x + self.width/2, self.y + self.height/2) 
        self.rect.center = self.pos

        # this needs to happen last otherwise there can be a race condition
        # where the SpriteObject is in a game group but isn't fully loaded yet
        self.groups = []
        if collision:
            self.groups.append(game.collision_list)
            self.collision_rect = self.rect
        if hittable:
            self.groups.append(game.hittable_list)
        if not collision and not hittable:
            self.groups.append(game.decor_list)
        pg.sprite.Sprite.__init__(self, self.groups)

    def load_image(self) -> pg.image:
        # overwrite this method to implement custom image loading in a class
        pass

    def draw(self, screen, camera):
        # self.draw_collision_rects(screen, camera)
        screen.blit(self.image, camera.apply(self.rect))

    def draw_collision_rects(self, screen, camera):
        if self.collision_rect:
            pg.draw.rect(screen, RED, camera.apply(self.collision_rect))

    def to_json(self):
        return {
            "topleft":(self.x, self.y),
            "img_path":self.img_path,
            "resize":self.img_resize,
            "collision":self.collision,
            "hittable":self.hittable
        }