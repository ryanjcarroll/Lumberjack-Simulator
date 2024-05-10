import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math
from utility import *
import json
from objects.sprites import SpriteObject

class Character(SpriteObject):
    def __init__(self, game, x, y, loadout):
        self.loadout = loadout        
        super().__init__(game, x, y, layer=SPRITE_LAYER, image=None)

        self.sprite_offset = vec(0, -int(PLAYER_SPRITE_HEIGHT*3/8))

        # collision_rect is for collision detection, rect is for sprite/image positioning
        self.collision_rect = pg.Rect(
            0,
            0,
            CHARACTER_COLLISION_WIDTH,
            CHARACTER_COLLISION_HEIGHT
        )
        self.collision_rect.center = self.pos
        self.last_movement = vec(0,0)
        self.move_distance = PLAYER_MOVE_DISTANCE

        # initialize animation settings
        self.animation_timer = 0
        self.current_frame_index = -1
        self.direction = "down"
        self.action = "stand"
        self.animation_speed = PLAYER_ANIMATION_SPEED

        self.rect = self.image.get_rect(center=self.pos + self.sprite_offset)
        self.game.character_list.add(self)

        # import within the init method to avoid circular import
        from objects.characters.player import Player
        if not isinstance(self, Player):
            self.game.can_collide_list.add(self)

    def move(self, x, y):
        self.pos = vec(x, y)

        self.collision_rect.center = self.pos
        self.rect.center = self.pos + self.sprite_offset

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
            if any(substring in key for substring in self.actions_to_load):
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
        elif self.action in ["walk","pick"]:
            # update animation frame if enough time has passed
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

        if self.action in ["walk","pick"]:
            # set the frame for walk animations
            self.image = self.frames[f"{self.action}_{self.direction}"][self.current_frame_index]
        elif self.action == "axe":               
            self.image = self.frames[f"{self.action}_{self.direction}"][self.current_frame_index]
        elif self.action == "sleep":
            self.image = self.frames[f"{self.action}"][self.current_frame_index]
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.frames[f"walk_{self.direction}"][0]
        
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.pos + self.sprite_offset
        self.collision_rect.center = self.pos

    def draw(self, screen, camera):
        super().draw(screen, camera)

