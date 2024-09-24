import pygame as pg
from settings import *
from pygame import Vector2 as vec

class SpriteObject(pg.sprite.Sprite):
    """
    Sprite objects to be loaded within the game.
    """
    def __init__(self, game, x, y, layer, image=None, can_collide=False, can_hit=False, is_building=False):
        super().__init__()

        # initiation variables
        self.x = x
        self.y = y
        self.game = game

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
        self.layer = layer
        self.game.sprite_list.add(self)
        if can_collide:
            self.game.can_collide_list.add(self)
            self.collision_rect = self.rect
        if can_hit:
            self.game.can_hit_list.add(self)
        if is_building:
            self.game.buildings_list.add(self)
        

    def load_image(self) -> pg.image:
        # overwrite this method to implement custom image loading in a class
        pass

    def update(self):
        pass

    def draw(self, screen, camera):
        # self.draw_collision_rects(screen, camera)
        screen.blit(self.image, camera.apply(self.rect))

    def draw_collision_rects(self, screen, camera):
        if self.collision_rect:
            pg.draw.rect(screen, RED, camera.apply(self.collision_rect))

    def to_json(self):
        return {
            "type":type(self).__name__,
            "topleft":(self.x, self.y)
        }