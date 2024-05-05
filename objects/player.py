import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math
from utility import extract_image_from_spritesheet, combine_images
from objects.inventory import Backpack
import json

class Player(pg.sprite.Sprite):
    """
    Player x and y refers to the center of the Player sprite.
    """
    def __init__(self, game, x:int, y:int, loadout:dict):
        self.game = game

        # set player attributes
        self.backpack = Backpack()
        self.health = PLAYER_STARTING_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        # set position variables
        self.pos = vec(x, y)
        self.angle = 0
        self.hitbox = PLAYER_HITBOX
        self.hitbox.center = self.pos
        self.last_movement = vec(0,0)

        # set default values
        self.move_distance = PLAYER_MOVE_DISTANCE
        self.attack_distance = PLAYER_ATTACK_DISTANCE
        self.axe_damage = PLAYER_ATTACK_DAMAGE

        # initialize animation settings
        self.animation_timer = 0
        self.current_frame_index = -1
        self.direction = "down"
        self.action = "stand"
        self.animation_speed = PLAYER_ANIMATION_SPEED
        self.load_animations(loadout)

        self.image = self.frames[f"walk_down"][0]
        self.rect = self.image.get_rect(center=self.pos)
        # run an initial update to set the first frame of the spritesheet
        self.update()

    def load_animations(self, loadout:dict):
        """
        Load spritesheets and animation frames.
        """
        # holds a spritesheet for each player attribute to be rendered
        self.spritesheets = {}

        for attribute, d in loadout.items():
            if d['category'] != "none":
                # load the spritesheet for the given asset category based on loadout params
                spritesheet = pg.image.load(f"assets/player/{attribute}/{d['category']}.png")
                
                # if the sheet has multiple columns, crop to the correct one (this selects the style)
                if spritesheet.get_width() > SPRITESHEET_NUM_COLUMNS * SPRITESHEET_TILE_SIZE:
                    cropped_spritesheet = spritesheet.subsurface(pg.Rect(
                        d['style']*SPRITESHEET_TILE_SIZE*SPRITESHEET_NUM_COLUMNS,
                        0,
                        SPRITESHEET_TILE_SIZE*SPRITESHEET_NUM_COLUMNS,
                        spritesheet.get_height()
                    ))
                else:
                    cropped_spritesheet = spritesheet
                self.spritesheets[attribute] = cropped_spritesheet

        self.load_frames()

    def load_frames(self):

        # holds a list of combined images for each animation type
        self.frames = {}

        # actions we want to import
        action_substrings = ACTIONS_TO_LOAD
        layer_order = LAYER_ORDER

        # load the spritesheet key to determine which rows go with which animations
        with open("assets/player/spritesheet_key.json") as f_in:
            row_key = json.load(f_in)
        frames_to_load = {}
        # Iterate over original dictionary
        for key, value in row_key.items():
            # Check if any substring is present in the key
            if any(substring in key for substring in action_substrings):
                # Include the key-value pair in the filtered dictionary
                frames_to_load[key] = value

        # iterate through loadable actions
        for action, d in frames_to_load.items():
            row = d['row']
            num_frames = d['num_frames']

            # initalize an empty list for this action's combined frames
            self.frames[action] = []

            # load all attributes for frame 1, then all for frame 2, etc...
            for i in range(num_frames):
                images = []

                # load in layer order
                for attribute in layer_order:
                    # check that attribute was not left empty
                    if attribute in self.spritesheets.keys():
                        # load each image layer from its spritesheet and combine them
                        sheet = self.spritesheets[attribute]
                        
                        images.append(
                            pg.transform.scale(
                                extract_image_from_spritesheet(
                                    spritesheet=sheet,
                                    row_index=row,
                                    col_index=i,
                                    tile_size=SPRITESHEET_TILE_SIZE
                                ),
                                (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)
                            )
                        )

                self.frames[action].append((combine_images(images)))
        
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

        # check for collision in each of the X and Y directions independently
        # this allows movement with multiple direction inputs, even if there is a collision on one of them
        self.hitbox.center += movement_x_only
        if any(self.hitbox.colliderect(obj.rect) for obj in self.game.collision_list):
            movement -= movement_x_only
        self.hitbox.center -= movement_x_only

        self.hitbox.center += movement_y_only
        if any(self.hitbox.colliderect(obj.rect) for obj in self.game.collision_list):
            movement -= movement_y_only
        self.hitbox.center -= movement_y_only

        if movement.length_squared() > 0:
            self.hitbox.center += movement
            self.pos += movement
            self.rect.center = self.pos
            self.hitbox.center = self.pos

    def check_at_camp(self, movement):
        # before adjusting for collisions, check if colliding with camp
        # we only need to check if we actually have something to unpack
        if self.backpack.wood:
            self.hitbox.center += movement
            if self.hitbox.colliderect(self.game.camp.rect):
                self.backpack.unpack(self.game.camp)
            self.hitbox.center -= movement

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
        trees_hit = [tree for tree in self.game.hittable_list if tree.rect.colliderect(attack_rect)]

        # Reduce the health of the collided tree(s)
        for tree in trees_hit:
            tree.health -= self.axe_damage
            tree_type = tree.tree_type
            if tree.health <= 0:
                tree.kill()
            if "Flower" in tree_type:
                self.backpack.row_capacity = min(self.backpack.row_capacity+1, 20)
                self.game.backpack_inventory_menu.update_capacity()
            elif "Burned" in tree_type:
                # don't add wood
                pass
            elif "Fruit" in tree_type:
                self.health = min(self.health + 10, self.max_health)
                self.game.health_bar.update()
            else:
                self.backpack.add_wood()

        self.health -= 2
        self.game.health_bar.update()

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
                if self.current_frame_index == len(self.frames[f"{self.action}_{self.direction}"]):
                    self.attack()
                    self.action = "stand"
        elif self.action == "walk":
            # update walk animation frame if enough time has passed
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"{self.action}_{self.direction}"])
                self.animation_timer = 0
        elif self.action == "sleep":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"{self.action}"])
                self.animation_timer = 0
                
    def update(self):
        """
        Called each game step to update the Player object.
        """
        self.set_animation_counters(self.game.dt)

        if self.action == "walk":
            # set the frame for walk animations
            self.image = self.frames[f"walk_{self.direction}"][self.current_frame_index]
        elif self.action == "axe":               
            self.image = self.frames[f"axe_{self.direction}"][self.current_frame_index]
        elif self.action == "sleep":
            self.image = self.frames["sleep"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.pos
        self.hitbox.center = self.pos

        # if player health reaches 0 or lower, end the game
        if self.health <= 0:
            self.game.playing = False

    def draw(self, screen, camera):
        # self.draw_hitboxes(screen, camera)
        screen.blit(self.image, camera.apply(self.rect))
    
    def draw_hitboxes(self, screen, camera):
        """
        Debugging method to show player attack hitboxes
        """
        # Draw grey hitboxes in every angle except the active one
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
        
        # Draw red box for current hitbox last (so it will be on top)
        attack_pos = (
            self.pos[0] + self.attack_distance * math.cos(math.radians(self.angle)),
            self.pos[1] - self.attack_distance * math.sin(math.radians(self.angle))  # Negative sin because Y-axis is inverted in Pygame
        )
        top_left_corner = (
            attack_pos[0] - self.attack_distance / 2,
            attack_pos[1] - self.attack_distance / 2
        )
        attack_rect = pg.Rect(top_left_corner, (self.attack_distance, self.attack_distance))
        pg.draw.rect(screen, RED, camera.apply(attack_rect))

    def game_over_update(self):
        self.action = "sleep"
        self.current_frame_index = 0
        self.update()
        self.game.game_over_menu.draw(self.game.screen)