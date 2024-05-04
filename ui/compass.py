from settings import *
import pygame as pg
from pygame import Vector2 as vec
import math

class Compass:
    def __init__(self, game):

        self.game = game

        self.width = COMPASS_WIDTH
        self.height = COMPASS_HEIGHT
        self.x = WINDOW_WIDTH//2 - self.width//2
        self.y = WINDOW_HEIGHT - self.height - COMPASS_PADDING

        self.pos = vec(self.x, self.y)
        self.image = pg.image.load("assets/ui/arrow.png")
        self.rect = self.image.get_rect(topleft=self.pos)

    def draw(self, screen):
        direction = (self.game.camp.pos - self.game.player.pos)
        if math.sqrt(direction.length_squared()) >= WINDOW_WIDTH//4:
            # Calculate angle between vector and positive x-axis
            angle = direction.angle_to(vec(1, 0))

            # Rotate arrow image
            rotated_arrow = pg.transform.rotate(self.image, angle)
            rotated_rect = rotated_arrow.get_rect(center=self.rect.center)

            # Draw rotated arrow on screen
            screen.blit(rotated_arrow, rotated_rect)

        