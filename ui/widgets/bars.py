from settings import *
import pygame as pg
from pygame import Vector2 as vec

class HealthBarWidget:
    def __init__(self, game):
        self.game = game
    
        self.image = self.game.sprites.load("assets/ui/apple.png", resize=(36,36))
        self.icon_rect = self.image.get_rect()

        # x and y are defined as the top left of the icon below the bar
        self.x = WINDOW_WIDTH - RBAR_PADDING - self.icon_rect.width
        self.y = WINDOW_HEIGHT - RBAR_PADDING - self.icon_rect.height
        self.max_height = 200

        self.color = RED
        self.pos = vec(self.x, self.y)
        self.icon_rect.topleft = self.pos
        self.update()

    def update(self):
        """
        Called to update the values displayed by the healthbar on the next draw step.
        """
        self.bar_width = 20
        # check player health to determine new height
        self.bar_height = int(self.max_height * (self.game.player.health / self.game.player.max_health))
        self.rect_x = self.x + (self.icon_rect.width - self.bar_width) // 2  # center rectangle horizontally
        self.rect_y = self.y - self.bar_height - RBAR_PADDING # position rectangle above the icon
        self.bar_rect = pg.Rect(self.rect_x, self.rect_y, self.bar_width, self.bar_height)
        
    def draw(self, screen):
        # Draw the red rectangle above the apple icon
        pg.draw.rect(screen, RED, self.bar_rect)

        # Draw the apple icon
        screen.blit(self.image, (self.icon_rect.x, self.icon_rect.y))