import pygame as pg
from settings import *

class Camera:
    def __init__(self, game, width, height):
        self.game = game
        self.rect = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        """
        Position an entity's rectangle attribute using relative coordinates within the camera frame.
        """
        return pg.Rect(
            rect.topleft[0] - self.rect.topleft[0],
            rect.topleft[1] - self.rect.topleft[1],
            rect.width,
            rect.height
        )
    
    def apply_point(self, pos):
        """
        Adjust a position using relative coordinates within the camera frame.
        """
        adjusted_x = pos[0] - self.rect.topleft[0]
        adjusted_y = pos[1] - self.rect.topleft[1]
        return (adjusted_x, adjusted_y)  # Return the adjusted position and radius

    def update(self):
        """
        Update the camera's position to follow the target (player).
        """
        x = (self.game.player.pos.x - int(round(self.width / 2)))
        y = (self.game.player.pos.y - int(round(self.height / 2)))
        self.rect.topleft = (x, y)

    def is_visible(self, entity):
        if hasattr(entity, "draw_rect") and self.rect.colliderect(entity.draw_rect):
            return True
        elif hasattr(entity, "shadow_rect") and self.rect.colliderect(entity.shadow_rect):
            return True
        elif self.rect.colliderect(entity.rect):
            return True
        else:
            return False