from settings import *
import pygame as pg
from glob import glob
import tkinter as tk
from tkinter import filedialog
import os
from ui.button import Button

class StartMenu:
    def __init__(self, game):
        self.game = game
        self.build_elements()

    def build_elements(self):
        # background    
        self.background_image = self.game.sprites.load("assets/ui/main_menu.png", resize=(WINDOW_WIDTH, WINDOW_HEIGHT))
    
        # title
        self.title_text = pg.font.Font(None, 128).render(f"LUMBERJACK", True, BLACK)
        self.title_text_x = WINDOW_WIDTH // 2 - self.title_text.get_width() // 2
        self.title_text_y = WINDOW_HEIGHT // 3

        # Create buttons with actions
        self.new_game_button = Button(
            screen=self.game.screen,
            rect=((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT // 2, 200, 50),
            color=(255, 0, 0),
            hover_color=(0, 255, 0),
            text="New Game",
            on_click=self.start_new_game
        )
        self.continue_button = Button(
            screen=self.game.screen,
            rect=((WINDOW_WIDTH - 200) // 2, WINDOW_HEIGHT // 2 + 60, 200, 50),
            color=(255, 0, 0),
            hover_color=(0, 255, 0),
            text="Continue",
            on_click=self.continue_game_from_save
        )

    def handle_event(self, event):
        self.new_game_button.handle_event(event)
        self.continue_button.handle_event(event)

    def draw(self):
        self.game.screen.blit(self.background_image, (0,0))
        self.game.screen.blit(self.title_text, (self.title_text_x, self.title_text_y))

        # Draw the "New Game" buttons
        self.new_game_button.draw()
        self.continue_button.draw()
        pg.display.flip()

    def start_new_game(self):
        self.game.at_start_menu = False  # progress to the next phase
        
    def continue_game_from_save(self):
        self.game.at_start_menu = False  # progress to the next phase  

        root = tk.Tk()
        root.withdraw()  # Hide the tkinter root window
        folder_path = filedialog.askdirectory(
            title="Select Save Folder",
            initialdir='data/saves'
        )
        # Check if a folder was selected
        if folder_path:  # If the user didn't cancel the dialog
            self.game.game_id = os.path.basename(folder_path) # Load the game from id