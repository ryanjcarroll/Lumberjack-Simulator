from objects.sprites import SpriteObject
from settings import *
import pygame as pg
import random

class Grass(SpriteObject):
    def __init__(self, game, x, y, tile):
        super().__init__(game, x, y, tile, layer=DECOR_LAYER)

        self.collision_rect = self.rect

        # angle for interaction
        self.base_angle = 0
        self.current_angle = 0
        self.max_angle = 30

        self.sway_speed = 3  # speed to rotate away when touched
        self.spring_back_speed = 1  # speed to return to base

        self.original_image = self.image  # Store original image for rotation
        self.angle_changed = False

    def load_image(self):
        return self.game.sprites.load(
            random.choice([
                "assets/decor/grass/12.png",
                "assets/decor/grass/13.png"
            ])
        )

    def interact(self, player):
        if player.collision_rect.colliderect(self.collision_rect):
            target_angle = self.max_angle if player.rect.centerx >= self.rect.centerx else -self.max_angle

            # Smooth transition to target angle and check if the angle changes
            new_angle = self.current_angle + (target_angle - self.current_angle) * 0.2
            if abs(new_angle - self.current_angle) > 0.1:  # Only change if significant
                self.current_angle = new_angle
                self.angle_changed = True

        else:
            # Gradually return to base angle when not touching the player
            if abs(self.current_angle - self.base_angle) > 0.1:
                self.current_angle += (self.base_angle - self.current_angle) * self.spring_back_speed
                self.angle_changed = True
            else:
                self.current_angle = self.base_angle  # Snap back if close enough

    def update(self):
        # Only rotate if there is a change in angle
        if self.angle_changed:
            self.image = pg.transform.rotate(self.original_image, self.current_angle)
            self.rect = self.image.get_rect(center=self.rect.center)  # Adjust position
            self.angle_changed = False  # Reset flag

    # def draw(self, screen, camera):
    #     # pg.draw.rect(screen, RED, camera.apply(self.rect))