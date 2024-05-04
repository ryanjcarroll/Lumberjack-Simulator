from settings import *
import pygame as pg




# # Display start screen UI
# while True:
#     self.screen.fill(BG_COLOR)
#     # Draw start screen UI elements
#     # Example: draw start button
#     pg.draw.rect(self.screen, (0, 255, 0), start_button_rect)  # Green color for demonstration
#     self.screen.blit(text, (text_x, text_y))
    
#     # Handle start screen events
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             pg.quit()
#             sys.exit()
#         # Handle mouse clicks on the start button
#         if event.type == pg.MOUSEBUTTONDOWN:
#             if start_button_rect.collidepoint(event.pos):
#                 self.new()  # Initialize game objects
#                 return  # Exit start screen loop and proceed to main game loop

#     pg.display.flip()

class StartMenu:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        
        self.build_elements()

    def build_elements(self):
        # Define start button rectangle
        start_button_width = 200
        start_button_height = 50
        start_button_x = (WINDOW_WIDTH - start_button_width) // 2
        start_button_y = WINDOW_HEIGHT - 100  # 100 pixels from the bottom
        self.start_button = pg.Rect(start_button_x, start_button_y, start_button_width, start_button_height)

        font = pg.font.Font(None, 36)
        self.start_text = font.render(f"NEW GAME", True, BLACK)
        self.start_text_x = self.start_button.centerx - self.start_text.get_width() // 2  # Center the text horizontally within the rectangle
        self.start_text_y = self.start_button.centery - self.start_text.get_height() // 2  # Center the text vertically within the rectangle

    def update(self):
        pass

    def draw(self):
        self.screen.fill(BG_COLOR)
        # Draw the "New Game" button
        pg.draw.rect(self.screen, RED, self.start_button)
        self.screen.blit(self.start_text, (self.start_text_x, self.start_text_y))
        pg.display.flip()

    def handle_click(self, pos):
        if self.start_button.collidepoint(pos):
            self.game.at_start_menu = False  # start the game