import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math
from utility import *
from objects.items.inventory import Backpack
from objects.resources.tree import Tree
from objects.resources.rock import Rock
from objects.sprites import SpriteObject
from objects.items.items import SkillPoint
from objects.player.skills import SkillTree
from objects.player.phototaker import Phototaker

class Player(SpriteObject):
    """
    Player x and y refers to the center of the Player sprite.
    """
    def __init__(self, game, x:int, y:int, loadout:dict):
        self.loadout = loadout

        # set Player's home tile at the center of the spawn Chunk    
        tile = game.map.chunks["0,0"].get_tile(CHUNK_SIZE//2, CHUNK_SIZE//2 + 1)

        super().__init__(game, x, y, tile, layer=SPRITE_LAYER, image=None)

        # set player attributes
        self.backpack = Backpack()
        self.health = PLAYER_STARTING_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.skill_points_available = 0
        self.skill_tree = SkillTree(game)

        # set position variables
        self.angle = 0
        self.sprite_offset = vec(0, -int(PLAYER_SPRITE_HEIGHT*3/8))
        self.water_offset_current = 0
        self.snow_offset_current = 0
        self.water_offset_target = vec(0,15)
        self.snow_offset_target = vec(0,-15)

        # collision_rect is for collision detection, rect is for sprite/image positioning
        self.collision_rect = PLAYER_COLLISION_RECT
        self.collision_rect.center = self.pos
        self.last_movement = vec(0,0)

        # set default values (some of these can be changed by skills)
        self.move_distance = PLAYER_MOVE_DISTANCE
        self.move_distance_over_water = PLAYER_MOVE_DISTANCE - 2
        self.weapon_stats = {
            "sword":{
                "attack_damage":PLAYER_SWORD_ATTACK_DAMAGE,
                "attack_distance":PLAYER_SWORD_ATTACK_DISTANCE
            },
            "axe":{
                "attack_damage":PLAYER_AXE_ATTACK_DAMAGE,
                "attack_distance":PLAYER_AXE_ATTACK_DISTANCE
            },
            "pick":{
                "attack_damage":PLAYER_PICK_ATTACK_DAMAGE,
                "attack_distance":PLAYER_PICK_ATTACK_DISTANCE
            },
            "hoe":{
                "attack_damage":0,
                "attack_distance":PLAYER_PICK_ATTACK_DISTANCE
            }
        }
        self.fruit_hp = 5
        self.wood_per_tree = 1
        self.dodge_chance = 0
        self.crit_chance = 0

        # photos taken
        self.phototaker = Phototaker(self.game, self)

        # initialize animation settings
        self.animation_timer = 0
        self.current_frame_index = -1
        self.direction = "down"
        self.action = "stand"
        self.animation_speed = PLAYER_ANIMATION_SPEED
        
        self.rect = self.image.get_rect(center=self.pos + self.sprite_offset)

    def load_image(self):
        self.load_animations(self.loadout)
        return self.frames[f"walk_down"][0]

    def load_animations(self, loadout:dict):
        """
        Load spritesheets and animation frames.
        """
        # load the spritesheet key to determine which rows go with which animations
        row_key = self.game.jsons.read("assets/player/spritesheet_key.json")

        frames_to_load = {}
        # Iterate over original dictionary
        for key, value in row_key.items():
            # Check if any substring is present in the key
            if any(substring in key for substring in ACTIONS_TO_LOAD + WEAPONS_TO_LOAD):
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
                        self.game.sprites.load_from_tilesheet(
                            path=f"assets/player/{attribute}/{d_loadout['category']}.png",
                            row_index=row,
                            col_index=col,
                            tile_size=SPRITESHEET_TILE_SIZE,
                            resize=(PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)
                        )
                    )

                # combine cimponents into a single animation frame and add to the frames library
                self.frames[action].append((combine_images(images)))
        
    def handle_event(self, event):
        """
        Handle events based on a keypress, but not a held-down key
        """
        # left mouse button clicked while camera open
        if self.game.weapon_menu.get_weapon_name() == 'camera':
            if event.type == pg.MOUSEWHEEL:
                self.phototaker.adjust_lens(event.y)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button==1:
                lens = self.phototaker.get_lens()

                # Capture the area as a photo (Surface object)
                photo_width = lens.width - (2 * self.phototaker.line_width)
                photo_height = lens.height - (2 * self.phototaker.line_width)
                photo = pg.Surface((photo_width, photo_height))
                photo.blit(
                    self.game.screen, 
                    (0, 0), 
                    (  # crop out the red Phototaker rectangle
                        lens.x + self.phototaker.line_width, 
                        lens.y + self.phototaker.line_width, 
                        photo_width, 
                        photo_height
                    )
                )

                # Add the photo to the player's album
                self.phototaker.take_photo(photo)

    def handle_keys(self, keys:list):
        """
        Handle movement commands (including held-down keys like WASD)
        """
        movement = vec(0, 0)

        # if an attack/tool is ongoing, don't exceute any movements
        if self.action in WEAPONS_TO_LOAD:
            return False

        if keys[pg.K_SPACE]:
            self.current_frame_index = -1 # start the animation sequence for new inputs
            self.action = self.game.weapon_menu.get_weapon_name()
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
            return False
            
        self.apply_movement(movement)

    def apply_movement(self, movement:vec):
        # normalize diagonal walking movements
        if movement.length_squared() > self.move_distance:
            movement = movement.normalize() * self.move_distance
            self.last_movement = movement
            self.action = "walk"
        # if horizontal/vertical movement, set the action
        else:
            self.action = "walk"

        if self.get_current_tile().terrain == "water":
            movement = movement.normalize() * self.move_distance_over_water

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

        # check if movement would put player at camp
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
                self.game.save()
            self.collision_rect.center -= movement

    def check_can_collect(self):        
        for obj in self.game.can_collect_list:
            if self.collision_rect.colliderect(obj.rect):
                if type(obj)== SkillPoint:
                    self.skill_points_available += 1
                    self.game.sounds.play("skillpoint",0)
                    self.game.skilltree_menu.update_points_available()
                obj.kill()

    def get_equipped_weapon_stats(self):
        weapon_stats = self.weapon_stats[self.game.weapon_menu.get_weapon_name()]
        return weapon_stats["attack_distance"], weapon_stats["attack_damage"]

    def get_attack_area(self):
        attack_circles = []

        attack_distance, attack_damage = self.get_equipped_weapon_stats()

        # Create circles based on angles
        # for angle in [self.angle - 45, self.angle, self.angle + 45]:
        for angle in [self.angle]:
            # Calculate the center position of the attack circle
            attack_center = (
                self.pos[0] + attack_distance * math.cos(math.radians(angle)),
                self.pos[1] - attack_distance * math.sin(math.radians(angle))  # Y-axis inverted in Pygame
            )
            # Append the circle (center and radius) to the list
            attack_circles.append((attack_center, attack_distance))

        return attack_circles
    
    def get_damage(self):
        """
        Get a value to apply for damage on the currently equipped weapon.
        """
        if self.action in self.weapon_stats:
            attack_distance, base_damage = self.get_equipped_weapon_stats()
            # apply +/- 25% randomness to damage
            multiplier = random.uniform(0.75, 1.25)
            damage = int(base_damage * multiplier)

            # apply crit for sword attacks
            if self.action == "sword":
                if random.random() < self.crit_chance:
                    damage *= 2

            return damage
        else:
            return None
    
    def apply_weapon(self):
        """
        Called once an axe swing animation has finished.
        Determines whether anything was hit and deals damage.
        """
        # Check for collisions at the attack position and reduce enemy/tree HP accordingly
        attack_circles = self.get_attack_area()

        # check for axe-able objects in attack area
        if self.action == "axe":
            damage = self.get_damage()
            hit_a_tree = False
            felled_a_tree = False
            
            for obj in self.game.can_axe_list:
                if any([circle_collides(center, radius, obj.collision_rect) for center, radius in attack_circles]):
                    obj.register_hit(damage)

                    if not hit_a_tree:
                        if isinstance(obj, Tree):
                            hit_a_tree = True
                    if not felled_a_tree:
                        if obj.health <=0:
                            felled_a_tree = True

            # play sound effects for trees
            # do this here so we don't have overlapping sound effects for trees
            if felled_a_tree:
                self.game.sounds.play_random("fell_tree")   
            elif hit_a_tree:
                self.game.sounds.play_random("chop_tree")
        
        # check for sword-able objects in attack area
        elif self.action == "sword":
            damage = self.get_damage()
            for obj in self.game.can_sword_list:
                if any([circle_collides(center, radius, obj.collision_rect) for center, radius in attack_circles]):
                    obj.register_hit(damage)

        # check for pick-able objects in attack area
        elif self.action == "pick":
            damage = self.get_damage()
            hit_a_rock = False
            felled_a_rock = False

            for obj in self.game.can_pick_list:
                if any([circle_collides(center, radius, obj.collision_rect) for center, radius in attack_circles]):
                    obj.register_hit(damage)

                    if not hit_a_rock:
                        if isinstance(obj, Rock):
                            hit_a_rock = True
                    if not felled_a_rock:
                        if obj.health <=0:
                            felled_a_rock = True
            
            if felled_a_rock:
                self.game.sounds.play_random("fell_rock")   
            elif hit_a_rock:
                self.game.sounds.play_random("chop_rock")

        elif self.action == "hoe":
            for chunk_id in self.game.map.get_visible_chunks():
                chunk = self.game.map.chunks[chunk_id]
                for tile in chunk.get_tiles():
                    if any([circle_collides(center, radius, tile.rect)for center, radius in attack_circles]):
                        tile.set_terrain("dirt")

    def set_animation_counters(self, dt):
        """
        Increment the animation counters for axe swing and walking animations.
        """
        self.animation_timer += dt

        # if not moving
        if self.action in WEAPONS_TO_LOAD:
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index += 1
                self.animation_timer = 0
                # finish the attack operations when the animation reaches the final frame
                if self.current_frame_index == len(self.frames[f"{self.action}_{self.direction}"]):
                    if self.action in WEAPONS_TO_LOAD:
                        self.apply_weapon()
                    self.action = "stand"
        elif self.action == "walk":
            # update walk animation frame if enough time has passed
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"{self.action}_{self.direction}"])
                self.animation_timer = 0
        elif self.action == "idle":
            if self.animation_timer >= self.animation_speed:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.frames[f"{self.action}"])
                self.animation_timer = 0

    def modify_health(self, n):
        self.health = min(self.health + n, self.max_health)
        self.game.health_bar.update()

    def register_hit(self, n):
        if random.random() > self.dodge_chance:
            self.modify_health(-n)
            self.game.sounds.play_random("player_damage")
        else:
            self.game.sounds.play_random("player_dodge")

    def update(self):
        """
        Called each game step to update the Player object.
        """
        self.set_animation_counters(self.game.dt)

        # set the frame for animations
        if self.action in ["walk"] + WEAPONS_TO_LOAD:
            self.image = self.frames[f"{self.action}_{self.direction}"][self.current_frame_index]
        elif self.action == "idle":
            self.image = self.frames["idle"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        # apply snow and water position offsets
        current_terrain = self.get_current_tile().terrain
        if current_terrain == "water":
            if self.water_offset_current < self.water_offset_target.length():
                self.apply_movement(self.water_offset_target.normalize())
                self.water_offset_current += 1
        elif current_terrain == "snow":
            if self.snow_offset_current < self.snow_offset_target.length():
                self.apply_movement(self.snow_offset_target.normalize())
                self.snow_offset_current += 1
        else:
            if self.water_offset_current > 0:
                self.apply_movement(-self.water_offset_target.normalize())
                self.water_offset_current -= 1
            if self.snow_offset_current > 0:
                self.apply_movement(-self.snow_offset_target.normalize())
                self.snow_offset_current -= 1
     

        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.pos + self.sprite_offset
        self.collision_rect.center = self.pos

        # update phototaker
        if self.game.weapon_menu.get_weapon_name() == 'camera':
            self.phototaker.update()

        self.check_can_collect()

        # if player health reaches 0 or lower, end the game
        if self.health <= 0:
            self.game.playing = False

    def get_current_tile(self):
        """
        Returns the tile the player is standing on.
        """
        current_chunk_topleft = self.game.map.get_chunk_coords(self.pos.x, self.pos.y)
        current_chunk_id = self.game.map.get_chunk_id(self.pos.x, self.pos.y)
        
        rel_pos = self.pos - current_chunk_topleft
        current_tile = self.game.map.chunks[current_chunk_id].get_tile(
            row=int(rel_pos.y // TILE_SIZE),
            col=int(rel_pos.x // TILE_SIZE)
        )
        return current_tile
        

    def draw(self, screen, camera):
        # self.draw_hitboxes(screen, camera)
        # pg.draw.rect(screen, RED, camera.apply(self.collision_rect))
        screen.blit(self.image, camera.apply(self.rect))
        
        # draw phototaker
        if self.game.weapon_menu.get_weapon_name() == 'camera':
            self.phototaker.draw(screen)
            
    def draw_hitboxes(self, screen, camera):
        """
        Debugging method to show player attack collision areas.
        """
        attack_distance, attack_damage = self.get_equipped_weapon_stats()

        # Draw grey collision areas for every angle except the active one
        for angle in [-180, -135, -90, -45, 0, 45, 90, 135]:
            if angle == self.angle:
                continue
            
            # Calculate the position for the attack swing
            attack_pos = (
                self.pos[0] + attack_distance * math.cos(math.radians(angle)),
                self.pos[1] - attack_distance * math.sin(math.radians(angle))  # Negative sin because Y-axis is inverted in Pygame
            )

            # Draw the attack area as a circle
            pg.draw.circle(screen, LIGHT_GREY, camera.apply_point(attack_pos), attack_distance, 1)

        # Draw the actual attack area based on the current angle
        attack_circles = self.get_attack_area()
        for center, radius in attack_circles:
            pg.draw.circle(screen, RED, camera.apply_point(center), radius, 1)  # Draw outline circle

        pg.draw.rect(screen, GREEN, camera.apply(self.collision_rect))  # Draw the player's collision rect

    def game_over_update(self):
        self.action = "idle"
        self.current_frame_index = 0
        self.update()
        self.game.game_over_menu.draw(self.game.screen)

    def to_json(self):
        return {
            "type":type(self).__name__,

        }