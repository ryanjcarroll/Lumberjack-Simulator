import pygame as pg
from pygame import Vector2 as vec
from settings import *
from utility import extract_image_from_spritesheet
from map.tile_textures import tile_textures
import random
from glob import glob
from objects.sprite_object import SpriteObject

class Tile:
    def __init__(self, game, x, y, row, col, terrain_type="grass", has_decor=True):
        self.game = game
        
        self.terrain_type = terrain_type
        self.image = self.load_texture()
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(x,y)
        self.row = row # row within the chunk
        self.col = col # col within the chunk
        self.objects = []

        if has_decor:
            self.load_decor()

    def load_texture(self):
        if self.terrain_type in tile_textures:
            texture = tile_textures[self.terrain_type]
            return pg.transform.scale(
                extract_image_from_spritesheet(
                    spritesheet=texture['source'],
                    row_index=texture['row'],
                    col_index=texture['column'],
                    tile_size=texture['tile_size']
                )
                ,(TILE_SIZE, TILE_SIZE)
            )
        else:
            return pg.transform.scale(pg.image.load("assets/textures/bedrock.png"), (TILE_SIZE, TILE_SIZE))
        
    def load_decor(self):
        # generate between 0 and 2 decorative items to randomly place on the tile
        item_type_weights = {
            # "bush"      : 2,
            "butterfly" : 2,
            # "camp":,
            # "decor"     : 1,
            # "fence"     : 1,
            "flower"    : 3,
            "grass"     : 30,
            "patch"     : 50,
            "pebble"    : 5,
            # "signpost"  : 1,
            # "stone"     : 2,
        }
        item_type = random.choices(
            population = list(item_type_weights.keys()),
            weights = list(item_type_weights.values())
        )[0]

        decor_x = random.randint(self.rect.left, self.rect.right)
        decor_y = random.randint(self.rect.top, self.rect.bottom)
        self.objects.append(
            SpriteObject(
                game=self.game,
                x = decor_x,
                y = decor_y,
                img_path = random.choice(glob(f"assets/decor/{item_type}/*.png"))     
        ))

    def draw_base(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))

    def draw_objects(self, screen, camera):
        for object in self.objects:
            if object.alive():
                object.draw(screen, camera)

    def to_json(self):
        return {
            "type":type(self),
            "image":self.img_path,
            "topleft":self.rect.topleft,
            "objects":[obj.to_json for obj in self.objects]
        }