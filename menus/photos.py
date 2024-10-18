from settings import *
import pygame as pg

class PhotoMenu:
    def __init__(self, game):
        self.game = game
        self.build_elements()

    def build_elements(self):
        # Set font for title and other text
        title_font = pg.font.Font(None, 36)  # Font size for the title

        # Draw the title "Skills" at the top center
        self.title_surface = title_font.render("Photos", True, (0, 0, 0))  # Black text
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))  # Centered at the top

    def update(self, mouse_pos):
        pass

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_p:
            self.game.at_photo_menu = False

    def draw(self):
        self.game.screen.fill(LIGHTER_GREY)  # background

        self.game.screen.blit(self.title_surface, self.title_rect)

        pg.display.flip()