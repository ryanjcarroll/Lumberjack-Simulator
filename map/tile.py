import pygame as pg
from pygame import Vector2 as vec
from settings import *

class Tile:
    def __init__(self, game, x, y, row, col, terrain_type="grass_outlined"):
        self.game = game
        
        self.terrain_type = terrain_type
        self.image = self.load_texture()
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(x,y)
        self.row = row # row within the chunk
        self.col = col # col within the chunk
        self.objects = []

    def load_texture(self):
        if self.terrain_type == "grass_outlined":
            return pg.transform.scale(pg.image.load("assets/textures/grass_outlined.png"), (TILE_SIZE, TILE_SIZE))
        elif self.terrain_type == "grass":
            return pg.transform.scale(pg.image.load("assets/textures/grass.png"), (TILE_SIZE, TILE_SIZE))
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