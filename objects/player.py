import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math
from utility import get_frames

class Player(pg.sprite.Sprite):
    """
    Player x and y refers to the center of the Player sprite.
    """
    def __init__(self, game, x, y):
        self.game = game
        self.pos = vec(x, y)
        self.image = pg.image.load("assets/trees/Autumn_tree2.png")
        self.rect = self.image.get_rect(center=self.pos)

        self.angle = 0
        self.hitbox = PLAYER_HITBOX
        self.hitbox.center = self.pos

        # set default values
        self.move_distance = PLAYER_MOVE_DISTANCE
        self.attack_distance = PLAYER_ATTACK_DISTANCE
        self.axe_damage = PLAYER_ATTACK_DAMAGE

        # initialize animation settings
        self.animation_timer = 0
        self.current_frame_index = -1
        self.direction = "up"
        self.action = "stand"
        self.animation_speed = PLAYER_ANIMATION_SPEED
        self.load_animations()
        # run an initial update to set the first frame of the spritesheet
        self.update()

    def load_animations(self):
        """
        Load spritesheets and animation frames.
        """
        # load spritesheet(s) for animations
        self.walk_spritesheet = pg.image.load("assets/spritesheets/axe_sprite_sheet.png")

        self.frames = {
            "walk_up":get_frames(self.walk_spritesheet, 8, 9, 64),
            "walk_down":get_frames(self.walk_spritesheet, 10, 9, 64),
            "walk_left":get_frames(self.walk_spritesheet, 9, 9, 64),
            "walk_right":get_frames(self.walk_spritesheet, 11, 9, 64),
            "axe_up":get_frames(self.walk_spritesheet, 12, 6, 64),
            "axe_down":get_frames(self.walk_spritesheet, 14, 6, 64),
            "axe_left":get_frames(self.walk_spritesheet, 13, 6, 64),
            "axe_right":get_frames(self.walk_spritesheet, 15, 6, 64),
        }

    def check_keys(self):
        """
        Check for keyboard input and update movement and angle information accordingly. 
        """
        
        keys = pg.key.get_pressed()
        movement = self.get_movement(keys)

        # break movement into X and Y component vectors
        movement_x_only = vec(movement.x, 0)
        movement_y_only = vec(0, movement.y)
        
        # check for collision in each of the X and Y directions independently
        # this allows movement with multiple direction inputs, even if there is a collision on one of them
        self.hitbox.center += movement_x_only
        if any(self.hitbox.colliderect(tree.rect) for tree in self.game.tree_list):
            movement -= movement_x_only
        self.hitbox.center -= movement_x_only

        self.hitbox.center += movement_y_only
        if any(self.hitbox.colliderect(tree.rect) for tree in self.game.tree_list):
            movement -= movement_y_only
        self.hitbox.center -= movement_y_only

        if movement.length_squared() > 0:
            self.hitbox.center += movement
            self.pos += movement

            # always update angle, regardless of collision
            self.angle = math.degrees(math.atan2(-movement.y, movement.x))
            self.rect.center = self.pos
            self.hitbox.center = self.pos

    def get_movement(self, keys) -> vec:
        """
        Given a set of keyboard inputs, set action and direction, and return movement vector. 
        """
        movement = vec(0, 0)

        # if axe attack is ongoing, don't exceute any movements
        if self.action == "axe":
            return movement

        if keys[pg.K_SPACE]:
            self.current_frame_index = -1 # start the animation sequence for new inputs
            self.action = "axe"
            return movement
        
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            movement.x -= self.move_distance
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            movement.x += self.move_distance
        if keys[pg.K_w] or keys[pg.K_UP]:
            movement.y -= self.move_distance
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            movement.y += self.move_distance

        # if no movement, set action to stand
        if movement.length_squared() == 0:
            self.action = "stand"
            return movement

        # normalize diagonal walking movements
        if movement.length_squared() > PLAYER_MOVE_DISTANCE:
            movement.normalize() * PLAYER_MOVE_DISTANCE
            self.action = "walk"
        # if horizontal/vertical movement, set the action
        else:
            self.action = "walk"

        # for any walk, set the direction
        # if moving diagonally, we want the L/R sprite animation instead of U/D
        if movement.x > 0:
            self.direction = "right"
        elif movement.x < 0:
            self.direction = "left"
        elif movement.y > 0:
            self.direction = "down"
        elif movement.y < 0:
            self.direction = "up"

        return movement
           
    def attack(self):
        """
        Called once an axe swing animation has finished.
        Determines whether anything was hit and deals damage.
        """
        # Calculate the position and radius of the attack swing
        attack_pos = (
            self.pos[0] + self.attack_distance * math.cos(math.radians(self.angle)),
            self.pos[1] - self.attack_distance * math.sin(math.radians(self.angle))  # Negative sin because Y-axis is inverted in Pygame
        )
        # Calculate the top-left corner of the square area
        top_left_corner = (
            attack_pos[0] - self.attack_distance / 2,
            attack_pos[1] - self.attack_distance / 2
        )
        attack_rect = pg.Rect(top_left_corner, (self.attack_distance, self.attack_distance))

        # Check for tree collisions at the attack position and reduce tree HP accordingly
        trees_hit = [tree for tree in self.game.tree_list if tree.rect.colliderect(attack_rect)]

        # Reduce the health of the collided tree(s)
        for tree in trees_hit:
            tree.take_damage(self.axe_damage / len(trees_hit))

    def set_animation_counters(self, dt):
        """
        Increment the animation counters for axe swing and walking animations.
        """
        self.animation_timer += dt

        # if not moving
        if self.action == "axe":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index += 1
                self.animation_timer = 0
                # finish the attack operations when the animation reaches the final frame
                if self.current_frame_index == len(self.frames[f"{self.action}_{self.direction}"])-1:
                    self.attack()
                    self.action = "stand"
        elif self.action == "walk":
            # update walk animation frame if enough time has passed
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"{self.action}_{self.direction}"])
                self.animation_timer = 0

    def update(self):
        """
        Called each game step to update the Player object.
        """

        self.check_keys()
        self.set_animation_counters(self.game.dt)

        if self.action == "walk":
            # set the frame for walk animations
            self.image = self.frames[f"walk_{self.direction}"][self.current_frame_index]
        elif self.action == "axe":                
            self.image = self.frames[f"axe_{self.direction}"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.pos
        self.hitbox.center = self.pos

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))