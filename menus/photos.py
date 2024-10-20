from settings import *
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
        self.left_button = pg.Rect(50, WINDOW_HEIGHT // 2 - 25, 50, 50)  # Left triangle
        self.right_button = pg.Rect(WINDOW_WIDTH - 100, WINDOW_HEIGHT // 2 - 25, 50, 50)  # Right triangle

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_p:
            self.game.at_photo_menu = False

        if event.type == pg.MOUSEBUTTONDOWN:
            if self.left_button.collidepoint(event.pos):
                self.current_photo_index = (self.current_photo_index - 1) % len(self.game.player.phototaker.photos)
            elif self.right_button.collidepoint(event.pos):
                self.current_photo_index = (self.current_photo_index + 1) % len(self.game.player.phototaker.photos)

    def update(self):
        # Check mouse position for hover
        mouse_pos = pg.mouse.get_pos()
        self.left_hovered = self.left_button.collidepoint(mouse_pos)
        self.right_hovered = self.right_button.collidepoint(mouse_pos)

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

        
        # Draw triangle buttons with hover effect
        left_color = (255, 0, 0) if self.left_hovered else (0, 0, 0)  # Red if hovered, else black
        right_color = (255, 0, 0) if self.right_hovered else (0, 0, 0)  # Red if hovered, else black

        # Draw triangle buttons
        pg.draw.polygon(screen, left_color, [(self.left_button.left, self.left_button.centery), 
                                                      (self.left_button.right, self.left_button.top), 
                                                      (self.left_button.right, self.left_button.bottom)])  # Left triangle
        pg.draw.polygon(screen, right_color, [(self.right_button.right, self.right_button.centery), 
                                                      (self.right_button.left, self.right_button.top), 
                                                      (self.right_button.left, self.right_button.bottom)])  # Right triangle

        # Display photo index (e.g., "1/10") at the top right
        photo_count_text = self.photo_count_font.render(f"{self.current_photo_index + 1 if len(self.game.player.phototaker.photos) > 0 else 0}/{len(self.game.player.phototaker.photos)}", True, (0, 0, 0))
        screen.blit(photo_count_text, (WINDOW_WIDTH - 100, 30))

        pg.display.flip()