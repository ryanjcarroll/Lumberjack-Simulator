import json
from objects.sprites import SpriteObject
import pygame as pg
from pygame import Vector2 as vec
from settings import *
import random

class Ladybug(SpriteObject):
    def __init__(self, game, x, y, tile):
        self.width = 36
        self.height = 36
        self.frames = {}

        super().__init__(game, x, y, tile, layer=SPRITE_LAYER, image=None)

        # position and movement variables
        self.pos = vec(x,y)
        self.direction = pg.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))

        self.direction_timer = 0
        self.direction_duration = 3 # time to pick a new action, in seconds
        self.speed = 4 # pixels per second

        # animation variables
        self.animation_timer = 0
        self.current_frame_index = -1
        self.animation_speed = PLAYER_ANIMATION_SPEED
        self.action = "walk"
        self.direction = "left"

        # state variables
        self.idle_timer = 0
        self.jump_frame_counter = 0

    def load_image(self):
        self.load_animations()
        return self.frames[f"walk_left"][0]
    
    def load_animations(self):       
        # load the spritesheet key to determine which rows go with which animations               
        with open("assets/npcs/bugs/ladybug/spritesheet_key.json") as f_in:
            row_key = json.load(f_in)
        
        for action, info in row_key.items():
            self.frames[action] = []

            for col in range(info['num_frames']):
                # load the component frame and add to images list
                self.frames[action].append(
                    self.game.sprites.load_from_tilesheet(
                        path=f"assets/npcs/bugs/ladybug/ladybug.png",
                        row_index=info['row'],
                        col_index=col,
                        tile_size=16,
                        resize=(self.width, self.height)
                    )
                )

    def move(self, dt):
        if self.direction == "idle":
            pass
        else:
            if self.direction == "right":
                move_vec = vec(self.speed, 0)
            elif self.direction == "left":
                move_vec = vec(-self.speed, 0)

            self.pos += move_vec * self.speed * dt

            # # Update the rect position to the new position
            self.rect.center = self.pos

    def die(self):
        self.kill()

    def set_animation_counters(self, dt):
        """
        Increment the animation counters if enough time has passed since the last update.
        """
        self.animation_timer += dt

        if self.action == "walk":
            # update walk animation frame if enough time has passed
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"{self.action}_{self.direction}"])
                self.animation_timer = 0
        elif self.action == "idle":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = 0
                self.animation_timer = 0

    def update(self):
        """
        Called each game step to update this object.
        """
        self.set_animation_counters(self.game.dt)
        
        # once timer is up, choose a new action/direction
        self.direction_timer += self.game.dt
        if self.direction_timer >= self.direction_duration:
            self.action = random.choice(["walk","idle"])
            if self.action == "walk":
                self.direction = random.choice(["left","right"])
            self.direction_timer = 0

        # set the frame for animations
        if self.action in ["walk"]:
            self.move(self.game.dt)
            self.image = self.frames[f"{self.action}_{self.direction}"][self.current_frame_index]
        elif self.action == "idle":
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.pos)
        self.collision_rect = self.rect