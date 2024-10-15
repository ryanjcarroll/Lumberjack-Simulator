from settings import *
import pygame as pg
from menus.button import Button

class GameOverMenu:
    def __init__(self, game):
        self.game = game

        self.build_elements()

    def build_elements(self):
        # Build the Start button
        self.main_menu_button = Button(
            screen=self.game.screen,
            rect=(
                (WINDOW_WIDTH - 200) // 2, 
                (WINDOW_HEIGHT - 50) - 100,  # N pixels from the bottom
                200, 
                50
            ),
            color=(255, 0, 0),
            hover_color=(0, 255, 0),
            text="Main Menu",
            on_click=lambda: setattr(self.game, 'at_game_over', False)
        )

        # Game Over text
        self.title_text = pg.font.Font(None, 128).render(f"Game Over", True, BLACK)
        self.title_text_x = WINDOW_WIDTH // 2 - self.title_text.get_width() // 2
        self.title_text_y = WINDOW_HEIGHT // 3

    def handle_event(self, event):
        self.main_menu_button.handle_event(event)

    def draw(self, screen):
        self.main_menu_button.draw()
        screen.blit(self.title_text, (self.title_text_x, self.title_text_y))