from settings import *
import pygame as pg

class GameOverMenu:
    def __init__(self, game):
        self.game = game

        self.build_elements()

    def build_elements(self):
        # return button rectangle
        return_button_width = 200
        return_button_height = 50
        return_button_x = (WINDOW_WIDTH - return_button_width) // 2
        return_button_y = WINDOW_HEIGHT - 100  # 100 pixels from the bottom
        self.return_button = pg.Rect(return_button_x, return_button_y, return_button_width, return_button_height)

        # return button text
        self.return_text = pg.font.Font(None, 36).render(f"Main Menu", True, BLACK)
        self.return_text_x = self.return_button.centerx - self.return_text.get_width() // 2  # Center the text horizontally within the rectangle
        self.return_text_y = self.return_button.centery - self.return_text.get_height() // 2  # Center the text vertically within the rectangle

        # Game Over text
        self.title_text = pg.font.Font(None, 128).render(f"Game Over", True, BLACK)
        self.title_text_x = WINDOW_WIDTH // 2 - self.title_text.get_width() // 2
        self.title_text_y = WINDOW_HEIGHT // 3

    def handle_click(self, pos):
        if self.return_button.collidepoint(pos):
            self.game.at_game_over = False  # progress to the next phase
            self.start_text = pg.font.Font(None, 36).render(f"Loading...", True, BLACK)
            self.start_text_x = self.return_button.centerx - self.return_text.get_width() // 2  # Center the text horizontally within the rectangle
            self.start_text_y = self.return_button.centery - self.return_text.get_height() // 2  # Center the text vertically within the rectangle
            self.draw(self.game.screen) # draw again to update with Loading text during buffer time

    def draw(self, screen):
        pg.draw.rect(screen, RED, self.return_button)
        screen.blit(self.return_text, (self.return_text_x, self.return_text_y))
        screen.blit(self.title_text, (self.title_text_x, self.title_text_y))