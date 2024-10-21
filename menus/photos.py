from settings import *
from menus.button import TriangleButton
import pygame as pg

class PhotoMenu:
    def __init__(self, game):
        self.game = game
        self.current_photo_index = len(self.game.player.phototaker.photos)-1 # start on the most recent
        self.build_elements()

    def build_elements(self):
        # Set font for title and other text
        self.title_font = pg.font.Font(None, 36)  # Font size for the title
        self.photo_count_font = pg.font.Font(None, 24)  # Font for photo count display

        # Draw the title "Photos" at the top center
        self.title_surface = self.title_font.render("Photos", True, (0, 0, 0))  # Black text
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))  # Centered at the top

        # Triangle buttons for navigation
        self.left_button = TriangleButton(
            screen=self.game.screen, 
            rect=(50, WINDOW_HEIGHT//2 - 25, 50, 50), 
            direction="left",
            on_click = lambda : self.update_current(-1)
        )
        self.right_button = TriangleButton(
            screen=self.game.screen, 
            rect=(WINDOW_WIDTH - 100, WINDOW_HEIGHT // 2 - 25, 50, 50), 
            direction="right",
            on_click = lambda : self.update_current(1)
        )

    def update_current(self, n):
        self.current_photo_index = (self.current_photo_index + n) % len(self.game.player.phototaker.photos)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_p:
            self.game.at_photo_menu = False
        
        self.left_button.handle_event(event)
        self.right_button.handle_event(event)

    def draw(self):
        screen = self.game.screen

        screen.fill(LIGHTER_GREY)  # background
        screen.blit(self.title_surface, self.title_rect)

        # Display current photo
        if self.game.player.phototaker.photos:
            photo = self.game.player.phototaker.photos[self.current_photo_index]

            width = WINDOW_WIDTH // 2
            photo = pg.transform.scale(photo, (width, width))

            # create a white rectangle for the Polaroid effect
            padding = 25
            polaroid_rect = pg.Rect(
                (
                    WINDOW_WIDTH // 2 - width // 2 - padding, # x
                    WINDOW_HEIGHT // 2 - width // 2 - (2*padding), # y
                    width + (padding * 2),  # width
                    width + (padding * 4) # height
                )
            )

            pg.draw.rect(screen, (255, 255, 255), polaroid_rect)
            pg.draw.rect(screen, (200, 200, 200), polaroid_rect, 5)  # Gray border
            photo_rect = photo.get_rect(center=(WINDOW_WIDTH // 2, (WINDOW_HEIGHT // 2)-padding))
            self.game.screen.blit(photo, photo_rect)

        # Draw triangle buttons
        self.left_button.draw()
        self.right_button.draw()

        # Display photo index (e.g., "1/10") at the top right
        photo_count_text = self.photo_count_font.render(f"{self.current_photo_index + 1 if len(self.game.player.phototaker.photos) > 0 else 0}/{len(self.game.player.phototaker.photos)}", True, (0, 0, 0))
        screen.blit(photo_count_text, (WINDOW_WIDTH - 100, 30))

        pg.display.flip()