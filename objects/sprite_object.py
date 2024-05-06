import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import math
import threading

class SpriteAssetManager:
    def __init__(self):
        self.images = {}
        self.lock = threading.Lock()

    def load(self, path):
        with self.lock:
            if path not in self.images:
                # add new entries to the saved images
                image = pg.image.load(path)
                self.images[path] = image

            # hand out copies to avoid race conditions
            # TODO there's probably a better way but not sure what it is right now
            return self.images[path].copy()

    def load_from_spritesheet(self, path, row_index, col_index, tile_size):
        with self.lock:
            if path not in self.images:
                sheet = pg.image.load(path)
                self.images[path] = sheet

            tile_path = f"{path}?{row_index},{col_index},{tile_size}"
            if tile_path not in self.images:
                # Extract a single image from spritesheet
                x = col_index * tile_size
                y = row_index * tile_size

                tile_rect = pg.Rect(x, y, tile_size, tile_size)
                self.images[tile_path] = self.images[path].subsurface(tile_rect)

            return self.images[tile_path]
                
class SpriteObject(pg.sprite.Sprite):
    """
    Sprite objects to be loaded within the game.
    """
    def __init__(self, game, x, y, img_path, layer, img_resize:tuple=None, collision=False, hittable=False):

        # initiation variables
        self.x = x
        self.y = y
        self.game = game
        self.render_layer = layer
        self.hittable = hittable
        self.collision = collision

        self.img_path = img_path
        self.img_resize = img_resize
        self.load_texture() # sets self.image

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

    def load_texture(self):
        """
        Set the image based on the image path. If resize was passed, transform the sprite to match the new dimensions.
        """
        # crop and resize if passed
        if self.img_resize:
            self.image = pg.transform.scale(
                remove_padding_and_scale(
                    self.game.sprites.load(
                        self.img_path
                    )
                )
                ,self.img_resize
            )
        # otherwise, load as current size
        else:
            self.image = pg.image.load(
                self.img_path
            )

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