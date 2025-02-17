from settings import *
import pygame as pg
from ui.button import Button

class PauseMenu:
    def __init__(self, game):
        self.game = game

        # darkness surface in order to tint the screen while game is paused
        # only need to draw this once during init since it won't change while paused
        self.darkness_surface = pg.Surface(size=(WINDOW_WIDTH, WINDOW_HEIGHT), flags=pg.SRCALPHA)
        self.darkness_alpha = 100 
        self.darkness_surface.fill((*BLACK, self.darkness_alpha))
        self.game.screen.blit(self.darkness_surface, (0,0))

        self.build_elements()

    def build_elements(self):
        # Build the Resume button
        self.resume_button = Button(
            screen=self.game.screen,
            rect=(
                (WINDOW_WIDTH - 200) // 2, 
                WINDOW_HEIGHT // 2,  # N pixels from the bottom
                200, 
                50
            ),
            color=(255, 0, 0),
            hover_color=(0, 255, 0),
            text="Resume",
            on_click=lambda: setattr(self.game, 'at_pause_menu', False)
        )

    def handle_event(self, event):
        self.resume_button.handle_event(event)

        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.game.at_pause_menu = False

    def draw(self):        
        self.resume_button.draw()

        pg.display.flip()
