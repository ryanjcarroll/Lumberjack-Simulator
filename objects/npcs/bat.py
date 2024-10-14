import json
from objects.sprites import SpriteObject
import pygame as pg
import math
import random
from pygame import Vector2 as vec
from settings import *

class Bat(SpriteObject):
    def __init__(self, game, x, y, tile):
        self.color = "purple"
        self.width = 36
        self.height = 36
        self.frames = {}

        super().__init__(game, x, y, tile, layer=SPRITE_LAYER, image=None)

        # position and movement variables
        self.pos = vec(x,y)
        self.move_distance = 3

        self.health = 30
        self.collision_rect = self.rect

        # animation variables
        self.animation_timer = 0
        self.current_frame_index = -1
        self.action = "sleep"
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
        self.knockback_duration = 15  # Number of frames for knockback effect

        self.game.can_sword_list.add(self)
        self.game.can_axe_list.add(self)

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
        player_pos = vec(self.game.player.pos)
        bat_pos = vec(self.pos)

        # Post-knockback movement
        if self.knockback_timer > 0:
            if self.knockback_direction:
                # Apply knockback distance
                knockback_vec = vec(self.knockback_direction) * self.move_distance
                bat_pos += knockback_vec
                self.pos = vec(bat_pos.x, bat_pos.y)  # Update bat position
            
            self.knockback_timer -= 1

            # Set direction for animation purposes
            if abs(self.knockback_direction[0]) > abs(self.knockback_direction[1]):
                self.direction = "right" if self.knockback_direction[0] > 0 else "left"
            else:
                self.direction = "down" if self.knockback_direction[1] > 0 else "up"

            # Stop knockback if the timer has expired
            if self.knockback_timer <= 0:
                self.knockback_direction = None

        # Normal movement
        else:
            # Calculate vector to the player
            to_player = player_pos - bat_pos
            distance_to_player = to_player.length()

            # Set an aggression radius (how far the bat can detect the player)
            aggression_radius = 300  # Bat starts moving towards player if within this range

            # Attack if near enough
            if distance_to_player < self.attack_distance:
                # self.attack_timer += self.game.dt
                # if self.attack_timer >= self.attack_cooldown:
                self.attack_player(distance_to_player, player_pos.x, player_pos.y)
                    # self.attack_timer = 0

            # Aggro if near enough
            elif distance_to_player < aggression_radius:
                # if transitioning from sleep to walk, play wakeup sound
                if self.action == "sleep":
                    self.game.sounds.play_random("bat_wake")

                # self.attack_timer = 0  # Reset the attack timer anytime the bat is no longer in attack range
                self.action = "walk"

                # Normalize the direction towards the player
                to_player = to_player.normalize()

                # Separation vector: Push away from nearby Bats
                separation_vec = vec(0, 0)
                clump_radius = 50  # Define how close other bats can get before they push away

                for enemy in self.game.can_sword_list:
                    if enemy != self:
                        enemy_pos = vec(enemy.pos)
                        to_enemy = bat_pos - enemy_pos
                        distance_to_enemy = to_enemy.length()

                        if distance_to_enemy < clump_radius:
                            # Push away from the other bat
                            separation_vec += to_enemy.normalize()

                # Add randomness to the movement (sway) to make it less linear
                sway = vec(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
                to_player += sway

                # Add the separation vector to the movement direction
                if separation_vec.length() > 0:
                    to_player += separation_vec.normalize() * 0.5  # Weight the separation force

                # Re-normalize direction after sway and separation
                to_player = to_player.normalize()

                # Implement acceleration: gradually increase speed the further the bat is from the player
                speed_multiplier = min(distance_to_player / aggression_radius, 1.5)  # Max speed multiplier is 1.5
                move_vec = to_player * self.move_distance * speed_multiplier

                # Update bat's position
                bat_pos += move_vec
                self.pos = vec(bat_pos.x, bat_pos.y)

                # Set direction for animation purposes
                if abs(player_pos.x - bat_pos.x) > abs(player_pos.y - bat_pos.y):
                    self.direction = "right" if player_pos.x > bat_pos.x else "left"
                else:
                    self.direction = "down" if player_pos.y > bat_pos.y else "up"

            # Optional idle or patrol behavior if player is out of range
            else:
                self.action = "sleep"  # Example: bat could sleep or wander

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
            self.game.sounds.play_random("bat_die")
        else:
            self.apply_knockback()
            self.game.sounds.play_random("bat_damage")

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
        self.collision_rect = self.rect