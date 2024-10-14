import json
from objects.sprites import SpriteObject
import pygame as pg
import math
import random
from settings import *

class Bat(SpriteObject):
    def __init__(self, game, x, y):
        self.color = "purple"
        self.width = 36
        self.height = 36
        self.frames = {}

        super().__init__(game, x, y, layer=SPRITE_LAYER, image=None)


        # position and movement variables
        self.pos = (x,y)
        self.move_distance = 3
        self.collision_rect = self.rect
        
        self.health = 4

        # animation variables
        self.animation_timer = 0
        self.current_frame_index = -1
        self.action = "walk"
        self.direction = "down"
        self.animation_speed = PLAYER_ANIMATION_SPEED

        # knockback variables
        self.knockback_direction = None
        self.knockback_timer = 0  # Duration for knockback
        self.knockback_duration = 15  # Number of frames for knockback effect

        self.game.can_axe_list.add(self)
        self.game.can_sword_list.add(self)

    def load_image(self):
        self.load_animations()
        return self.frames[f"walk_down"][0]

    def load_animations(self):       
        # load the spritesheet key to determine which rows go with which animations               
        with open("assets/npcs/bat/spritesheet_key.json") as f_in:
            row_key = json.load(f_in)
        
        for action, info in row_key.items():
            self.frames[action] = []

            for col in range(info['num_frames']):
                # load the component frame and add to images list
                self.frames[action].append(
                    pg.transform.scale(
                        self.game.sprites.load_from_tilesheet(
                            path=f"assets/npcs/bat/bat_{self.color}.png",
                            row_index=info['row'],
                            col_index=col,
                            tile_size=16
                        ),
                        (self.width, self.height)
                    )
                )

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
        elif self.action == "sleep":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = 0
                self.animation_timer = 0
        elif self.action == "die":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames["die"])
                self.animation_timer = 0
                if self.current_frame_index >= len(self.frames['die'])-1:
                    self.die()

    def die(self):
        self.kill()

    def move(self):
        # Get the player's current position
        player_pos = self.game.player.pos
        bat_x, bat_y = self.pos
        player_x, player_y = player_pos

        # Post-knockback movement
        if self.knockback_timer > 0:
            if self.knockback_direction:
                # Apply knockback distance
                move_distance = self.move_distance
                self.pos = (
                    bat_x + self.knockback_direction[0] * move_distance,
                    bat_y + self.knockback_direction[1] * move_distance
                )
            self.knockback_timer -= 1

            # Stop knockback if the timer has expired
            if self.knockback_timer <= 0:
                self.knockback_direction = None
        
        # Normal movement
        else:
            # Calculate distance to player
            diff_x = player_x - bat_x
            diff_y = player_y - bat_y
            distance = math.sqrt(diff_x ** 2 + diff_y ** 2)

            # Set an aggression radius (how far the bat can detect the player)
            aggression_radius = 300  # Bat starts moving towards player if within this range
            stop_radius = 50         # Bat slows down/stops when it's very close to player

            if distance < aggression_radius:
                if distance > stop_radius:
                    self.action = "walk"
                    # Normalize the direction towards the player
                    dir_x = diff_x / distance
                    dir_y = diff_y / distance

                    # Add some randomness to the movement to make it less linear
                    sway = random.uniform(-0.5, 0.5)
                    dir_x += sway * 0.1  # Random swaying to the left or right
                    dir_y += sway * 0.1

                    # Normalize direction again after sway
                    norm = math.sqrt(dir_x ** 2 + dir_y ** 2)
                    dir_x /= norm
                    dir_y /= norm

                    # Implement acceleration: gradually increase speed the further the bat is from the player
                    speed_multiplier = min(distance / aggression_radius, 1.5)  # Max speed multiplier is 1.5
                    move_distance = self.move_distance * speed_multiplier

                    # Update bat's position
                    self.pos = (bat_x + dir_x * move_distance, bat_y + dir_y * move_distance)

                    # Set direction for animation purposes
                    if abs(diff_x) > abs(diff_y):
                        self.direction = "right" if diff_x > 0 else "left"
                    else:
                        self.direction = "down" if diff_y > 0 else "up"
                else:
                    # If the bat is very close to the player, it slows down
                    self.pos = (bat_x, bat_y)  # Stops or hovers near player
            else:
                # Idle or patrol behavior if player is out of range (could add further logic here)
                self.action = "sleep"  # Example: bat could sleep or wander

    def register_hit(self, damage):
        """
        Take damage and/or start the death animation.
        """
        self.health -= damage
        if self.health <= 0:
            self.current_frame_index = 0
            self.action = "die"
        else:
            self.apply_knockback()

    def apply_knockback(self):
        """
        Push the bat away from the player slightly after a hit.
        """
        player_pos = self.game.player.pos
        bat_x, bat_y = self.pos
        player_x, player_y = player_pos

        # Calculate the direction from player to bat (for knockback, reverse the vector)
        diff_x = bat_x - player_x
        diff_y = bat_y - player_y
        distance = math.sqrt(diff_x ** 2 + diff_y ** 2)

        # Normalize the direction
        if distance != 0:
            self.knockback_direction = (diff_x / distance, diff_y / distance)
            self.knockback_timer = self.knockback_duration  # Set the knockback timer

    def update(self):
        """
        Called each game step to update this object.
        """
        self.set_animation_counters(self.game.dt)
        if self.action != "die":
            self.move()

        # set the frame for animations
        if self.action in ["walk"]:
            self.image = self.frames[f"{self.action}_{self.direction}"][self.current_frame_index]
        elif self.action == "sleep":
            self.image = self.frames["sleep"][0]
        elif self.action == "die":
            self.image = self.frames["die"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.pos)