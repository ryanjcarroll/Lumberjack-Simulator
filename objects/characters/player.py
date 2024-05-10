import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math
from utility import *
from objects.inventory import Backpack
from objects.tree import Tree
import json
from objects.sprites import SpriteObject
from objects.characters import Character

class Player(Character):
    """
    Player x and y refers to the center of the Player sprite.
    """
    def __init__(self, game, x:int, y:int, loadout:dict):
        self.actions_to_load = ["walk","axe","sleep"]
        super().__init__(game, x, y, loadout=loadout)

        # set player attributes
        self.backpack = Backpack(self.game)
        self.health = PLAYER_STARTING_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        # set position variables
        self.angle = 0

        # set default values
        self.attack_distance = PLAYER_ATTACK_DISTANCE
        self.axe_damage = PLAYER_ATTACK_DAMAGE

    def check_keys(self):
        """
        Check for keyboard input and update movement and angle information accordingly. 
        """
        keys = pg.key.get_pressed()
        movement = self.get_movement(keys)

        # # always update angle, regardless of collision and movement
        # self.angle = math.degrees(math.atan2(-movement.y, movement.x))

        self.check_at_camp(movement)
        
        # break movement into X and Y component vectors
        movement_x_only = vec(movement.x, 0)
        movement_y_only = vec(0, movement.y)

        # check for collision in the X direction
        self.collision_rect.center += movement_x_only
        if any(self.collision_rect.colliderect(obj.collision_rect) for obj in self.game.can_collide_list):
            movement -= movement_x_only
        self.collision_rect.center -= movement_x_only

        # check for collision in the Y direction
        self.collision_rect.center += movement_y_only
        if any(self.collision_rect.colliderect(obj.collision_rect) for obj in self.game.can_collide_list):
            movement -= movement_y_only
        self.collision_rect.center -= movement_y_only

        # after removing collisions, apply remaining movement vector
        if movement.length_squared() > 0:
            self.collision_rect.center += movement
            self.pos += movement
            self.rect.center = self.pos + self.sprite_offset
            self.collision_rect.center = self.pos

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
        if movement.length_squared() > self.move_distance:
            movement = movement.normalize() * self.move_distance
            self.last_movement = movement
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

        # Update player angle based on the last movement direction
        self.angle = math.degrees(math.atan2(-self.last_movement.y, self.last_movement.x))

        return movement
    
    def check_at_camp(self, movement):
        # before adjusting for collisions, check if colliding with camp
        # we only need to check if we actually have something to unpack
        if self.backpack.wood:
            self.collision_rect.center += movement
            if any([self.collision_rect.colliderect(character.collision_rect) for character in self.game.character_list if not isinstance(character, Player)]):
                self.backpack.unpack()
                self.game.sounds.play("unpack",0)
            self.collision_rect.center -= movement
           
    def get_attack_rects(self):
        attack_rects = []
        for angle in [self.angle-45, self.angle, self.angle+45]:
            # Calculate the position and radius of the attack swing
            attack_pos = (
                self.pos[0] + self.attack_distance * math.cos(math.radians(angle)),
                self.pos[1] - self.attack_distance * math.sin(math.radians(angle))  # Negative sin because Y-axis is inverted in Pygame
            )
            # Calculate the top-left corner of the square area
            top_left_corner = (
                attack_pos[0] - self.attack_distance / 2,
                attack_pos[1] - self.attack_distance / 2
            )
            attack_rects.append(pg.Rect(top_left_corner, (self.attack_distance, self.attack_distance)))

        return attack_rects
        
    def attack(self):
        """
        Called once an axe swing animation has finished.
        Determines whether anything was hit and deals damage.
        """
        # Check for tree collisions at the attack position and reduce tree HP accordingly
        attack_rects = self.get_attack_rects()

        # Reduce the health of the collided tree(s)
        felled_a_tree = False

        trees_hit = set()
        for rect in attack_rects:
            for obj in self.game.can_hit_list:
                if obj.collision_rect.colliderect(rect):
                    if isinstance(obj, Tree):
                        trees_hit.add(obj)

        for tree in trees_hit:
            tree.register_hit(PLAYER_ATTACK_DAMAGE)
        # determine if any trees were felled
        for tree in trees_hit:
            if tree.health <= 0:
                felled_a_tree = True
                break 

        # play sound effects
        if felled_a_tree:
            self.game.sounds.play_random("fell_tree")   
        elif len(trees_hit):
            self.game.sounds.play_random("chop_tree")

    def modify_health(self, n):
        self.health = min(self.health + n, self.max_health)
        self.game.health_bar.update()

    def update(self):
        """
        Called each game step to update the Player object.
        """
        self.check_keys()
        super().update()

        # if player health reaches 0 or lower, end the game
        if self.health <= 0:
            self.game.playing = False

    def draw(self, screen, camera):
        # self.draw_collision_rects(screen, camera)
        super().draw(screen, camera)
    
    def draw_collision_rects(self, screen, camera):
        """
        Debugging method to show player attack collision_rectes
        """
        # Draw grey collision_rects in every angle except the active one
        for angle in [-180, -135, -90, -45, 0, 45, 90, 135]:
            if angle == self.angle:
                continue
            # Calculate the position and radius of the attack swing
            attack_pos = (
                self.pos[0] + self.attack_distance * math.cos(math.radians(angle)),
                self.pos[1] - self.attack_distance * math.sin(math.radians(angle))  # Negative sin because Y-axis is inverted in Pygame
            )
            # Calculate the top-left corner of the square area
            top_left_corner = (
                attack_pos[0] - self.attack_distance / 2,
                attack_pos[1] - self.attack_distance / 2
            )
            attack_rect = pg.Rect(top_left_corner, (self.attack_distance, self.attack_distance))
            pg.draw.rect(screen, LIGHT_GREY, camera.apply(attack_rect))
        
        attack_collision_rects = self.get_attack_rects()
        for collision_rect in attack_collision_rects:
            pg.draw.rect(screen, RED, camera.apply(collision_rect))

        pg.draw.rect(screen, GREEN, camera.apply(self.collision_rect))

    def game_over_update(self):
        self.action = "sleep"
        self.current_frame_index = 0
        self.update()
        self.game.game_over_menu.draw(self.game.screen)