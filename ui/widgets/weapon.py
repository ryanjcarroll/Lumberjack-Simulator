import pygame as pg
from settings import *

class WeaponWidget:
    def __init__(self, game):
        self.game = game
        
        # Define the weapon names and initial selection
        self.weapons = WEAPONS_TO_LOAD + ["camera"]
        self.selected_weapon = 0  # Index of the selected weapon
        
        # Define the dimensions for the hotbar slots
        self.slot_width = 56
        self.slot_height = 56
        self.spacing = 4
        self.hotbar_x = (self.game.screen.get_width() - (self.slot_width * 3 + self.spacing * 2)) // 2
        self.hotbar_y = self.game.screen.get_height() - self.slot_height - 10  # Near the bottom of the screen

        # Set up fonts
        self.font = pg.font.Font(None, 36)

    def get_weapon_name(self):
        return self.weapons[self.get_weapon_index()]
    
    def get_weapon_index(self, name:str=None):
        """
        If no name is passed, return index of the currently equipped weapon.
        """
        if not name:
            return self.selected_weapon
        else:
            for i, weapon in enumerate(self.weapons):
                if weapon == name:
                    return i

    def handle_event(self, event):
        # Check for number key presses to switch between weapons
        if event.type == pg.KEYDOWN and pg.K_1 <= event.key <= pg.K_9:            
            number_pressed = event.key - pg.K_0
            if number_pressed <= len(self.weapons):
                self.selected_weapon = number_pressed - 1 # for zero-indexed list

    def draw(self, screen):
        # Loop through and draw each slot
        for i, weapon in enumerate(self.weapons):
            slot_x = self.hotbar_x + i * (self.slot_width + self.spacing)
            slot_y = self.hotbar_y

            # Highlight the selected weapon slot
            if i == self.selected_weapon:
                pg.draw.rect(screen, (255, 255, 0), (slot_x, slot_y, self.slot_width, self.slot_height), 3)  # Yellow border
            else:
                pg.draw.rect(screen, (255, 255, 255), (slot_x, slot_y, self.slot_width, self.slot_height), 2)  # White border

            # Render the weapon name
            text_surface = self.font.render(weapon, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(slot_x + self.slot_width // 2, slot_y + self.slot_height // 2))
            screen.blit(text_surface, text_rect)