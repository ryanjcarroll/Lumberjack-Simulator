import pygame as pg
from settings import *

class Phototaker:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        
        self.photos = []

        # lens settings
        self.apperture_min_width = 30
        self.lens_max_width = 150
        self.lens_width = 70
        self.lens_height = self.lens_width
        self.line_width = 4
        self.max_distance = TILE_SIZE*4

        self.update() # sets self.lens
    
    def take_photo(self, photo):
        self.photos.append(photo)
        self.game.sounds.play("shutter",0)

        # print("---")
        for obj in self.game.sprite_list:
            if self.game.camera.apply(obj.rect).colliderect(self.get_lens()):
                # print(type(obj))
                pass

        self.game.photo_menu.current_photo_index = len(self.photos)-1 # start on the most recent photo
        
    def adjust_lens(self, scroll_delta):
        """
        Adjust the camera lens (height) based on scroll input.
        scroll_delta > 0 means scroll up, scroll_delta < 0 means scroll down.
        """
        self.lens_width += scroll_delta * 10  # Change the factor to adjust sensitivity
        self.lens_width = max(self.apperture_min_width, min(self.lens_width, self.lens_max_width))
        self.lens_height = self.lens_width
        self.update()

    def get_lens(self):
        return self.lens

    def update(self):
        self.lens = pg.Rect(0, 0, self.lens_width, self.lens_height)
        
        # Calculate the distance from the player to the mouse position
        mouse_pos = pg.mouse.get_pos()
        player_pos = self.game.camera.apply_point(self.player.collision_rect.center) # Assuming the player has a rect attribute
        distance_x = mouse_pos[0] - player_pos[0]
        distance_y = mouse_pos[1] - player_pos[1]

        # Calculate the total distance
        distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

        # If the distance exceeds the maximum allowed distance, adjust the lens position
        if distance > 72:
            # Normalize the direction and multiply by the maximum distance
            direction_x = distance_x / distance
            direction_y = distance_y / distance

            # Set the lens position to be 72 pixels away from the player in the direction of the mouse
            lens_x = player_pos[0] + direction_x * 72
            lens_y = player_pos[1] + direction_y * 72
            self.lens = pg.Rect(0, 0, self.lens_width, self.lens_height)
            self.lens.center = (lens_x, lens_y)
        else:
            # If within bounds, set lens to mouse position
            self.lens = pg.Rect(0, 0, self.lens_width, self.lens_height)
            self.lens.center = mouse_pos

    def draw(self, screen):
        # Draw a red rectangle outline at the mouse position
        pg.draw.rect(screen, (255, 0, 0), self.lens, width=self.line_width)