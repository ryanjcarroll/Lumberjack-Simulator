import pygame as pg

class Camera:
    def __init__(self, width, height):
        self.rect = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        """
        Position an entity's rectangle attribute using relative coordinates within the camera frame.
        """
        return rect.move(self.rect.topleft)

    def update(self, target):
        """
        Update the camera's position to follow the target (player).
        """
        x = -target.rect.center[0] + int(self.width / 2)
        y = -target.rect.center[1] + int(self.height / 2)
        self.rect = pg.Rect(x, y, self.width, self.height)