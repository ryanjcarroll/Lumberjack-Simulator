import pygame as pg

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
        x = self.game.player.pos.x - int(round(self.width / 2))
        y = self.game.player.pos.y - int(round(self.height / 2))
        self.rect.topleft = (x,y)

    def is_visible(self, entity):
        if hasattr(object, "draw_rect"):
            if self.rect.colliderect(object.draw_rect):
                return True
        elif self.rect.colliderect(entity.rect):
            return True
        elif hasattr(object, "shadow_rect"):
            if self.rect.colliderect(object.shadow_rect):
                return True
        return False