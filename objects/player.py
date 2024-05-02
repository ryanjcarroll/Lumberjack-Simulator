import pygame as pg
from settings import *
from pygame import Vector2 as vec
import math

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.sprite_list
        pg.sprite.Sprite.__init__(self, self.groups)
        game.sprite_list.change_layer(self, PLAYER_LAYER)

        self.game = game

        # set player position, image, and hitbox
        self.pos = vec(x + TILE_SIZE/2, y + TILE_SIZE/2) # position the player in the center of its starting tile
        self.image = pg.image.load("assets/spritesheets/Walk Up.png")
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.angle = 0
        self.hitbox = PLAYER_HITBOX
        self.hitbox.center = self.pos

        # set default values
        self.move_distance = PLAYER_MOVE_DISTANCE
        self.attack_distance = PLAYER_ATTACK_DISTANCE
        self.slash_damage = PLAYER_ATTACK_DAMAGE

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
        # load spritesheet(s) for animations
        self.spritesheets = {
            "walk_up":pg.transform.scale(pg.image.load("assets/spritesheets/Walk Up.png"), (72*12, 72)),
            "walk_down":pg.transform.scale(pg.image.load("assets/spritesheets/Walk Down.png"), (72*12, 72)),
            "walk_left":pg.transform.scale(pg.image.load("assets/spritesheets/Walk Left.png"), (72*12, 72)),
            "walk_right":pg.transform.scale(pg.image.load("assets/spritesheets/Walk Right.png"), (72*12, 72)),
            "slash_up":pg.transform.scale(pg.image.load("assets/spritesheets/Slash Up.png"), (72*5, 72)),
            "slash_down":pg.transform.scale(pg.image.load("assets/spritesheets/Slash Down.png"), (72*5, 72)),
            "slash_left":pg.transform.scale(pg.image.load("assets/spritesheets/Slash Left.png"), (72*5, 72)),
            "slash_right":pg.transform.scale(pg.image.load("assets/spritesheets/Slash Right.png"), (72*5, 72)),
            "sword_up":pg.transform.scale(pg.image.load("assets/spritesheets/Sword Up.png"), (72*5, 72)),
            "sword_down":pg.transform.scale(pg.image.load("assets/spritesheets/Sword Down.png"), (72*5, 72)),
            "sword_left":pg.transform.scale(pg.image.load("assets/spritesheets/Sword Left.png"), (72*5, 72)),
            "sword_right":pg.transform.scale(pg.image.load("assets/spritesheets/Sword Right.png"), (72*5, 72)),
        }
        self.frames = {
            "walk_up":self.get_frames(12),
            "walk_down":self.get_frames(12),
            "walk_left":self.get_frames(12),
            "walk_right":self.get_frames(12),
            "slash_up":self.get_frames(5),
            "slash_down":self.get_frames(5),
            "slash_left":self.get_frames(5),
            "slash_right":self.get_frames(5),
            "sword_up":self.get_frames(5),
            "sword_down":self.get_frames(5),
            "sword_left":self.get_frames(5),
            "sword_right":self.get_frames(5),
        }

    def get_frames(self, n:int):
        # given a spritesheet length (the number of 24x24 pixel frames), return the coordinates for each frame
        return [
            pg.Rect(i, 0, PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)
            for i in range(0, n*PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)
        ]

    def check_keys(self):
        """
        Check for keyboard input and update movement and angle information accordingly. 
        """
        
        keys = pg.key.get_pressed()
        movement = self.get_movement(keys)

        if movement.length_squared() > 0:
            self.hitbox.center += movement
            
            # wall_collisions = pg.sprite.spritecollide(self.hitbox, self.game.tree_list, False)
            # if wall_collisions:
            if any(self.hitbox.colliderect(tree.rect) for tree in self.game.tree_list):
                # TODO some possible improvements here - we probably don't need to check EVERY tree for collision with the player
                    # undo movement if it would result in a wall collision
                    self.hitbox.center -= movement
            else:
                self.pos += movement

            # always update angle, regardless of collision
            self.angle = math.degrees(math.atan2(-movement.y, movement.x))
            self.rect.center = self.pos
            self.hitbox.center = self.pos

        self.update_animation(self.game.dt)

    def get_movement(self, keys) -> vec:
        """
        Check for keyboard input, set action and direction, and return movement vector. 
        """
        movement = vec(0, 0)

        # if slash attack is ongoing, don't exceute any movements
        if self.action == "slash":
            return movement

        if keys[pg.K_SPACE]:
            self.current_frame_index = -1 # start the slash animation sequence for new inputs
            self.action = "slash"
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
        # Calculate the position and radius of the attack swing
        attack_pos = self.pos + vec(
            self.attack_distance * math.cos(math.radians(self.angle)),
            -self.attack_distance * math.sin(math.radians(self.angle))
        )
        attack_radius_rect = pg.Rect(
            attack_pos.x - self.attack_distance/2, 
            attack_pos.y - self.attack_distance/2, 
            self.attack_distance, 
            self.attack_distance
        )

        # Check for tree collisions at the attack position and reduce tree HP accordingly
        for tree in self.game.tree_list:
            if tree.rect.colliderect(attack_radius_rect):
                # Reduce the health of the collided tree
                tree.take_damage(self.slash_damage)

    def update_animation(self, dt):
        self.animation_timer += dt

        # if not moving
        if self.action == "slash":
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
        if self.action == "walk":
            # set the frame for walk animations
            self.image = self.spritesheets[f"walk_{self.direction}"].subsurface(self.frames[f"walk_{self.direction}"][self.current_frame_index])
        elif self.action == "slash":
            
            # based on the direction the player is facing, offset the sword so it appears in the player's hand
            if self.direction == "right":
                sword_offset = vec(18,7).rotate(-self.angle)
                player_on_top = True
            elif self.direction == "left":
                sword_offset = vec(-16,4)
                player_on_top = True
            elif self.direction == "up":
                sword_offset = vec(8,-12)
                player_on_top = True
            elif self.direction == "down":
                sword_offset = vec(-10,22)
                player_on_top = False

            player_sprite = self.spritesheets[f"slash_{self.direction}"].subsurface(self.frames[f"slash_{self.direction}"][self.current_frame_index])
            sword_sprite = self.spritesheets[f"sword_{self.direction}"].subsurface(self.frames[f"sword_{self.direction}"][self.current_frame_index])

            # combine the sword and player sprites into one pg.Surface object
            combined_surface = pg.Surface((PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT), pg.SRCALPHA)
            if player_on_top:
                combined_surface.blit(sword_sprite, sword_offset)
                combined_surface.blit(player_sprite, vec(0,0))
            else:
                combined_surface.blit(player_sprite, vec(0,0))
                combined_surface.blit(sword_sprite, sword_offset)
                
            self.image = combined_surface
        else:
            # to stand, set to the first frame of the directional walk animation
            self.image = self.spritesheets[f"walk_{self.direction}"].subsurface(self.frames[f"walk_{self.direction}"][0])
        
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.center = self.pos
        self.hitbox.center = self.pos