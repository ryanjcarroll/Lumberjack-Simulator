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

    def update(self, target):
        """
        Update the camera's position to follow the target (player).
        """
        x = target.rect.center[0] - int(self.width / 2)
        y = target.rect.center[1] - int(self.height / 2)
        self.rect.topleft = (x,y)

    def is_visible(self, entity):
        if self.rect.colliderect(entity.rect):
            return True
        elif hasattr(object, "shadow_rect"):
            if self.rect.colliderect(object.shadow_rect):
                return True
        return False