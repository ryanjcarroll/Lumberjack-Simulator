import json
from objects.sprites import SpriteObject
import pygame as pg
from pygame import Vector2 as vec
from settings import *
import random

class Grasshopper(SpriteObject):
    def __init__(self, game, x, y, tile):
        self.width = 36
        self.height = 36
        self.frames = {}

        super().__init__(game, x, y, tile, layer=GROUND_NPC_LAYER, image=None)

        # position and movement variables
        self.pos = vec(x,y)
        self.jump_distance = 12 # total distance per jump
        self.jump_duration = 6 # in frames
        self.idle_time_far = 4 # idle time when player is far, in seconds
        self.idle_time_near = 1 # idle time when player is near, in seconds
        self.next_direction_chosen = True # toggle to see if direction has already been set for next jump

        # animation variables
        self.action = "idle"
        self.direction = "right"
        self.animation_timer = 0
        self.current_frame_index = -1
        self.animation_speed = PLAYER_ANIMATION_SPEED

        # state variables
        self.idle_timer = 0
        self.jump_frame_counter = 0

    def load_image(self):
        self.load_animations()
        return self.frames[f"jump_right"][0]

    def load_animations(self):       
        # load the spritesheet key to determine which rows go with which animations               
        with open("assets/npcs/bugs/spritesheet_key.json") as f_in:
            row_key = json.load(f_in)
        
        for action, info in row_key.items():
            self.frames[action] = []

            for col in range(info['num_frames']):
                # load the component frame and add to images list
                self.frames[action].append(
                    pg.transform.scale(
                        self.game.sprites.load_from_tilesheet(
                            path=f"assets/npcs/bugs/grasshopper.png",
                            row_index=info['row'],
                            col_index=col,
                            tile_size=18
                        ),
                        (self.width, self.height)
                    )
                )

    def move(self):
        movement_frames = [2,3]

        if self.current_frame_index in movement_frames:
            if self.direction == "right":
                move_vec = vec(self.jump_distance / len(movement_frames), 0)
            elif self.direction == "left":
                move_vec = vec(-self.jump_distance / len(movement_frames), 0)

            self.pos += move_vec

    def die(self):
        self.kill()

    def set_animation_counters(self, dt):
        """
        Increment the animation counters if enough time has passed since the last update.
        """
        if self.action == "idle":
            self.idle_timer += dt
            
            to_player = self.game.player.pos - self.pos

            # jump more rapidly when player is nearby
            if self.idle_timer >= self.idle_time_near and to_player.length() < TILE_SIZE * 3:
                if to_player.x > 0:
                    self.direction = "left"
                else:
                    self.direction = "right"

                # switch to jumping
                self.action = "jump"
                self.current_frame_index = 0
                self.idle_timer = 0
                self.jump_frame_counter = 0
        
            # if player is far, jump less often and in random direction
            elif self.idle_timer >= self.idle_time_far//2 and not self.next_direction_chosen:
                
                # otherwise, move semi-randomly, favoring preferred direction
                self.direction = random.choice(["right","left"])
                self.next_direction_chosen = True

            elif self.idle_timer >= self.idle_time_far:
                # After 2 seconds, switch to jumping
                self.action = "jump"
                self.current_frame_index = 0
                self.idle_timer = 0
                self.jump_frame_counter = 0

        elif self.action == "jump":
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                # Progress the jump animation
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"jump_{self.direction}"])
                self.animation_timer = 0
                self.jump_frame_counter += 1

                # Move during jump
                self.move()

                # If 6 frames of jumping are complete, return to idle
                if self.jump_frame_counter >= self.jump_duration:
                    self.action = "idle"
                    self.current_frame_index = 0
                    self.next_direction_chosen = False

    def update(self):
        """
        Called each game step to update this object.
        """
        self.set_animation_counters(self.game.dt)

        # set the frame for animations
        if self.action in ["jump"]:
            self.move()
            self.image = self.frames[f"{self.action}_{self.direction}"][self.current_frame_index]
        elif self.action == "idle":
            self.image = self.frames[f"jump_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.pos)
        self.collision_rect = self.rect