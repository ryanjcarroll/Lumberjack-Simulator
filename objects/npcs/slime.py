from settings import *
from pygame import Vector2 as vec
import json
import pygame as pg
import math
from objects.sprites import SpriteObject
import random

class Slime(SpriteObject):
    def __init__(self, game, x, y, tile):
        self.color = "rainbow"
        self.width = 36
        self.height = 36
        self.frames = {}

        super().__init__(game, x, y, tile, layer=GROUND_NPC_LAYER, image=None)

        # position and movement variables
        self.pos = vec(x,y)
        self.move_distance = 2
        self.collision_rect = self.rect
        
        self.health = 40

        # animation variables
        self.animation_timer = 0
        self.current_frame_index = -1
        self.action = "idle"
        self.direction = "down"
        self.animation_speed = PLAYER_ANIMATION_SPEED

        # attack variables
        self.attack_distance = 12
        self.attack_damage = 10
        self.attack_timer = 0
        self.attack_cooldown = 0 # number of seconds to wait before attacking

        # knockback variables
        self.knockback_direction = None
        self.knockback_timer = 0  # Duration for knockback
        self.knockback_duration = 18  # Number of frames for knockback effect

        self.game.can_sword_list.add(self)
        self.game.can_axe_list.add(self)

    def load_image(self):
        self.load_animations()
        return self.frames[f"walk_down"][0]

    def load_animations(self):       
        # load the spritesheet key to determine which rows go with which animations               
        with open("assets/npcs/slime/spritesheet_key.json") as f_in:
            row_key = json.load(f_in)
        
        for action, info in row_key.items():
            self.frames[action] = []

            for col in range(info['num_frames']):
                # load the component frame and add to images list
                self.frames[action].append(
                    pg.transform.scale(
                        self.game.sprites.load_from_tilesheet(
                            path=f"assets/npcs/slime/slime_{self.color}.png",
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
        elif self.action == "idle":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames["idle"])
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
        player_pos = vec(self.game.player.pos)
        slime_pos = vec(self.pos)

        # Post-knockback movement
        if self.knockback_timer > 0:
            if self.knockback_direction:
                # Apply knockback distance (slower for slimes)
                knockback_vec = vec(self.knockback_direction) * (self.move_distance * 2)
                slime_pos += knockback_vec
                self.pos = vec(slime_pos.x, slime_pos.y)  # Update slime position
            
            self.knockback_timer -= 1

            # Stop knockback if the timer has expired
            if self.knockback_timer <= 0:
                self.knockback_direction = None

        # Normal movement (bouncing)
        else:
            # Calculate vector to the player
            to_player = player_pos - slime_pos
            distance_to_player = to_player.length()

            # Set an aggression radius (how far the slime can detect the player)
            aggression_radius = 300  # Slime starts moving towards player if within this range

            # Attack if near enough
            if distance_to_player < self.attack_distance:
                self.attack_player(distance_to_player, player_pos.x, player_pos.y)

            # Aggro if near enough
            elif distance_to_player < aggression_radius:
                self.action = "walk"

                # Normalize the direction towards the player
                to_player = to_player.normalize()

                # Add randomness to the movement (sluggish sway for slimes)
                sway = vec(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
                to_player += sway

                # Sinusoidal movement to create bounce effect
                bounce_speed = abs(math.sin(pg.time.get_ticks() * 0.005))  # Oscillating speed
                move_vec = to_player * self.move_distance * bounce_speed * 0.8  # Slime is slower

                # Update slime's position
                slime_pos += move_vec
                self.pos = vec(slime_pos.x, slime_pos.y)

                # Set direction for animation purposes
                if abs(player_pos.x - slime_pos.x) > abs(player_pos.y - slime_pos.y):
                    self.direction = "right" if player_pos.x > slime_pos.x else "left"
                else:
                    self.direction = "down" if player_pos.y > slime_pos.y else "up"

            # Optional idle or patrol behavior if player is out of range
            else:
                self.action = "idle"  # Example: slime could stay put or wobble slightly

    def attack_player(self, distance, player_x, player_y):
        if distance < self.attack_distance:
            # Damage the player
            self.game.player.register_hit(self.attack_damage)
            
            # apply self knockback
            self.apply_knockback()

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
        self.game.sounds.play_random("slime")

    def apply_knockback(self):
        """
        Push the slime away from the player slightly after a hit, with a sinusoidal bounce.
        """
        player_pos = self.game.player.pos
        slime_x, slime_y = self.pos
        player_x, player_y = player_pos

        # Calculate the direction from player to slime (for knockback, reverse the vector)
        diff_x = slime_x - player_x
        diff_y = slime_y - player_y
        distance = math.sqrt(diff_x ** 2 + diff_y ** 2)

        # Normalize the direction
        if distance != 0:
            self.knockback_direction = (diff_x / distance, diff_y / distance)
            self.knockback_timer = self.knockback_duration  # Set the knockback timer

            # Add an initial bounce speed to start the sinusoidal effect on knockback
            self.bounce_timer = 0  # Track time for sinusoidal bounce during knockback

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
        elif self.action == "idle":
            self.image = self.frames["idle"][0]
        elif self.action == "die":
            self.image = self.frames["die"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.pos)
        self.collision_rect = self.rect