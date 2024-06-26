import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math
from utility import *
from objects.inventory import Backpack
from objects.tree import Tree
import json
from objects.sprites import SpriteObject

class Player(SpriteObject):
    """
    Player x and y refers to the center of the Player sprite.
    """
    def __init__(self, game, x:int, y:int, loadout:dict):
        self.loadout = loadout
        super().__init__(game, x, y, layer=SPRITE_LAYER, image=None)

        # set player attributes
        self.backpack = Backpack()
        self.health = PLAYER_STARTING_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        # set position variables
        self.angle = 0
        self.sprite_offset = vec(0, -int(PLAYER_SPRITE_HEIGHT*3/8))

        # collision_rect is for collision detection, rect is for sprite/image positioning
        self.collision_rect = PLAYER_COLLISION_RECT
        self.collision_rect.center = self.pos
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
        
        self.rect = self.image.get_rect(center=self.pos + self.sprite_offset)
        self.game.character_list.add(self)

    def load_image(self):
        self.load_animations(self.loadout)
        return self.frames[f"walk_down"][0]

    def load_animations(self, loadout:dict):
        """
        Load spritesheets and animation frames.
        """
        # load the spritesheet key to determine which rows go with which animations
        with open("assets/player/spritesheet_key.json") as f_in:
            row_key = json.load(f_in)

        frames_to_load = {}
        # Iterate over original dictionary
        for key, value in row_key.items():
            # Check if any substring is present in the key
            if any(substring in key for substring in ACTIONS_TO_LOAD):
                # Include the key-value pair in the filtered dictionary
                frames_to_load[key] = value


        self.frames = {}
        # load and build the combined animation frames for each action
        for action, d_action in frames_to_load.items():
            row = d_action['row']
            num_frames = d_action['num_frames']
            
            self.frames[action] = []
        
            # get each combined animation frame for the given action
            for n in range(num_frames):
                images = []  # a list of component images for a single frame

                # load an animation frame for each attribute (e.g. body, hair, etc)
                for attribute, d_loadout in loadout.items():

                    # skip any attribute that was left unselected
                    if d_loadout['category'] == "none":
                        continue
                    
                    # account for style offset
                    col = n + (d_loadout['style'] * SPRITESHEET_NUM_COLUMNS)
                    
                    # load the component frame and add to images list
                    images.append(
                        pg.transform.scale(
                            self.game.sprites.load_from_tilesheet(
                                path=f"assets/player/{attribute}/{d_loadout['category']}.png",
                                row_index=row,
                                col_index=col,
                                tile_size=SPRITESHEET_TILE_SIZE
                            ),
                            (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)
                        )
                    )

                # combine cimponents into a single animation frame and add to the frames library
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

        # check for collision in the X direction
        self.collision_rect.center += movement_x_only
        flag=False
        for obj in self.game.can_collide_list:
            try:
                if self.collision_rect.colliderect(obj.collision_rect):
                    flag = True
            except TypeError as e:
                print(self.collision_rect)
                print(obj.collision_rect, type(obj))
                raise(e)
        if flag:
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

    def check_at_camp(self, movement):
        # before adjusting for collisions, check if colliding with camp
        # we only need to check if we actually have something to unpack
        if self.backpack.wood:
            self.collision_rect.center += movement
            if self.collision_rect.colliderect(self.game.camp.rect):
                self.backpack.unpack(self.game.camp)
                self.game.sounds.play("unpack",0)
            self.collision_rect.center -= movement

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
            movement = movement.normalize() * PLAYER_MOVE_DISTANCE
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
        already_damaged = []

        felled_a_tree = False

        trees_hit = set()
        for rect in attack_rects:
            for obj in self.game.can_hit_list:
                if obj.collision_rect.colliderect(rect):
                    if isinstance(obj, Tree):
                        trees_hit.add(obj)
                        # tree_type = obj.tree_type
                        # hit_a_tree = True

                        # if obj not in already_damaged:
                        #     obj.register_hit(PLAYER_ATTACK_DAMAGE)
                        #     already_damaged.append(obj)
                        # if obj.health <= 0:
                        #     # obj.kill()
                        #     felled_a_tree = True
                        #     if "Flower" in tree_type:
                        #         # self.backpack.row_capacity = min(self.backpack.row_capacity+1, 20)
                        #         # self.game.backpack_inventory_menu.update_capacity()
                        #         pass
                        #     elif "Fruit" in tree_type:
                        #         self.health = min(self.health + 10, self.max_health)
                        #         self.game.health_bar.update()
                        #     elif "Apple" in tree_type:
                        #         self.health = min(self.health + 20, self.max_health)
                        #         self.game.health_bar.update()
                        #     self.backpack.add_wood(1)
        # register hits
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

    def modify_health(self, n):
        self.health = min(self.health + n, self.max_health)
        self.game.health_bar.update()

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
        elif self.action == "sleep":
            self.image = self.frames["sleep"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.pos + self.sprite_offset
        self.collision_rect.center = self.pos

        # if player health reaches 0 or lower, end the game
        if self.health <= 0:
            self.game.playing = False

    def draw(self, screen, camera):
        # self.draw_collision_rects(screen, camera)
        screen.blit(self.image, camera.apply(self.rect))
    
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