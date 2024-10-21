import pygame as pg
from utility import point_inside_triangle
from settings import *

class Button:
    def __init__(self, screen, rect, color=BLACK, hover_color=RED, text='', font=None, text_color=(0, 0, 0), on_click=None, on_hover=None):
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


class TriangleButton(Button):
    def __init__(self, screen, rect, direction="up", color=BLACK, hover_color=RED, text='', font=None, text_color=(0, 0, 0), on_click=None, on_hover=None):
        """
        Initialize a triangular button.
        
        points: List of 3 tuples representing the vertices of the triangle.
        """

        self.direction = direction
        self.rect = pg.Rect(rect)
        self.points = self.get_points()  # Store the triangle points

        # Call the parent constructor with a default rect that won't be used, as this is a triangle
        super().__init__(screen, rect=(0, 0, 1, 1), color=color, hover_color=hover_color, text=text, font=font, text_color=text_color, on_click=on_click, on_hover=on_hover)
        # also calls self.render_text()
    
    def get_points(self):
        if self.direction == "up":
            points = [
                (self.rect.left, self.rect.bottom),  # bottom left
                (self.rect.centerx, self.rect.top),  # center top
                (self.rect.right, self.rect.bottom)  # bottom right
            ]
        elif self.direction == "down":
            points = [
                (self.rect.left, self.rect.top),       # top left
                (self.rect.centerx, self.rect.bottom), # center bottom
                (self.rect.right, self.rect.top)       # top right
            ]
        elif self.direction == "left":
            points = [
                (self.rect.right, self.rect.top),    # top right
                (self.rect.left, self.rect.centery), # center left
                (self.rect.right, self.rect.bottom)  # bottom right
            ]
        elif self.direction == "right":
            points = [
                (self.rect.left, self.rect.top),      # top left
                (self.rect.right, self.rect.centery), # center right
                (self.rect.left, self.rect.bottom)    # bottom left
            ]

        return points

    def render_text(self):
        """Renders the button's text and positions it inside the triangle."""
        self.text_surface = self.font.render(self.text, True, self.text_color)
        # Position the text centered within the bounding box of the triangle
        self.text_rect = self.text_surface.get_rect(center=self.get_triangle_center())

    def get_triangle_center(self):
        """Calculate the center point of the triangle by averaging its vertices."""
        x = (self.points[0][0] + self.points[1][0] + self.points[2][0]) // 3
        y = (self.points[0][1] + self.points[1][1] + self.points[2][1]) // 3
        return (x, y)

    def draw(self):
        """Draw the triangle button on the screen."""
        current_color = self.hover_color if self.is_hovered else self.color
        pg.draw.polygon(self.screen, current_color, self.points)
        self.screen.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        """Handle hover and click events for the triangle button."""
        # Hover detection
        if event.type == pg.MOUSEMOTION:
            self.is_hovered = point_inside_triangle(event.pos, self.points)
            if self.is_hovered and self.on_hover:
                self.on_hover()

        # Click detection
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and point_inside_triangle(event.pos, self.points):  # Left-click
                if self.on_click:
                    self.text = "Loading..."
                    self.draw()
                    self.on_click()