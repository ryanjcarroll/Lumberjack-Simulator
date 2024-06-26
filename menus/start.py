from settings import *
import pygame as pg

class StartMenu:
    def __init__(self, game):
        self.game = game
        self.build_elements()

    def build_elements(self):
        # background    
        self.background_image = pg.transform.scale(self.game.sprites.load("assets/ui/main_menu.png"), (WINDOW_WIDTH, WINDOW_HEIGHT))
    
        # title
        self.title_text = pg.font.Font(None, 128).render(f"LUMBERJACK", True, BLACK)
        self.title_text_x = WINDOW_WIDTH // 2 - self.title_text.get_width() // 2
        self.title_text_y = WINDOW_HEIGHT // 3

        # Define start button rectangle
        start_button_width = 200
        start_button_height = 50
        start_button_x = (WINDOW_WIDTH - start_button_width) // 2
        start_button_y = (WINDOW_HEIGHT - start_button_height) //2 # 100 pixels from the bottom
        self.start_button = pg.Rect(start_button_x, start_button_y, start_button_width, start_button_height)

        self.font = pg.font.Font(None, 36)
        self.start_text = self.font.render(f"New Game", True, BLACK)
        self.start_text_x = self.start_button.centerx - self.start_text.get_width() // 2  # Center the text horizontally within the rectangle
        self.start_text_y = self.start_button.centery - self.start_text.get_height() // 2  # Center the text vertically within the rectangle

    def update(self):
        pass

    def draw(self):
        self.game.screen.blit(self.background_image, (0,0))
        self.game.screen.blit(self.title_text, (self.title_text_x, self.title_text_y))

        # Draw the "New Game" button
        pg.draw.rect(self.game.screen, RED, self.start_button)
        self.game.screen.blit(self.start_text, (self.start_text_x, self.start_text_y))
        pg.display.flip()

    def handle_click(self, pos):
        if self.start_button.collidepoint(pos):
            self.game.at_start_menu = False  # progress to the next phase
            self.start_text = self.font.render(f"Loading...", True, BLACK)
            self.start_text_x = self.start_button.centerx - self.start_text.get_width() // 2  # Center the text horizontally within the rectangle
            self.start_text_y = self.start_button.centery - self.start_text.get_height() // 2  # Center the text vertically within the rectangle
            self.draw() # draw again to update with Loading text during buffer time