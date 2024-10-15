import pygame as pg

class Button:
    def __init__(self, screen, rect, color, hover_color, text='', font=None, text_color=(0, 0, 0), on_click=None, on_hover=None):
        """
        Initialize a Menu button with size, colors, and actions.

        rect: Tuple (x, y, width, height) - Button position and size
        color: (r, g, b) - Button color
        hover_color: (r, g, b) - Color when the mouse hovers over the button
        text: str - Optional text to display on the button
        font: pygame.font.Font - Font to render the text (can be None if no text)
        text_color: (r, g, b) - Color of the button text
        on_click: Function to call when the button is clicked
        on_hover: Function to call when the button is hovered over
        """
        self.screen = screen
        self.rect = pg.Rect(rect)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.font = font if font else pg.font.Font(None, 36)
        self.text_color = text_color
        self.on_click = on_click
        self.on_hover = on_hover
        self.is_hovered = False

        self.render_text()

    def render_text(self):
        """Renders the button's text."""
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self):
        """Draw the button on the screen."""
        current_color = self.hover_color if self.is_hovered else self.color
        pg.draw.rect(self.screen, current_color, self.rect)
        self.screen.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        # Hover
        if event.type == pg.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.is_hovered = True
                if self.on_hover:
                    self.on_hover()
            else:
                self.is_hovered = False

        # Click
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):  # Left-click
                if self.on_click:
                    self.text = "Loading..."
                    self.draw()
                    self.on_click()