import pygame as pg
from pygame import Vector2 as vec
from settings import *
from utility import extract_image_from_spritesheet
from map.tile_textures import spritesheets, tile_textures

class Tile:
    def __init__(self, game, x, y, row, col, terrain_type="grass"):
        self.game = game
        
        self.terrain_type = terrain_type
        self.image = self.load_texture()
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(x,y)
        self.row = row # row within the chunk
        self.col = col # col within the chunk
        self.objects = []

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

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
        for object in self.objects:
            if object.alive():
                object.draw(screen, camera)

    def to_json(self):
        return {
            "type":type(self),
            "image":self.img_path,
            "topleft":self.rect.topleft
        }