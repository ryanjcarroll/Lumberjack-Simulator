import pygame as pg
from datetime import datetime
from settings import *

class DatetimeWidget:
    def __init__(self, game):
        self.game = game
        self.font = pg.font.Font(None, 36) 
        self.color = WHITE
        self.update_time(self.game.datetime)

    def update_time(self, dt):
        self.current_time_text = dt.strftime("%H:%M")
        self.rendered_text = self.font.render(self.current_time_text, True, self.color)

    def draw(self, screen):
        screen.blit(self.rendered_text, (WINDOW_WIDTH-(10+self.rendered_text.get_width()), 10))  # top right with padding