import pygame as pg
from settings import *

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILE_SIZE
        self.height = self.tileheight * TILE_SIZE

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_to_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        self.x = -target.rect.centerx + int(WIDTH / 2)  ##amount to offset, negative if moving right
        self.y = -target.rect.centery + int(HEIGHT / 2)

        self.x = min(0, self.x)
        self.y = min(0, self.y)
        self.x = max(WIDTH - self.width, self.x)
        self.y = max(HEIGHT - self.height, self.y)

        self.camera = pg.Rect(self.x, self.y, self.width, self.height)

    def reverse(self, pos):
        return(pos[0] + self.camera.topleft[0], pos[1] + self.camera.topleft[1])