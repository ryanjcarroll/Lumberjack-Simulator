import pygame as pg
from settings import *
from utility import remove_padding
from pygame import Vector2 as vec
import math
import random
from objects.sprites import SpriteObject

class Tree(SpriteObject):
    def __init__(self, game, x, y, tile, image_name=None, flipped=None):
        
        self.image_name = image_name
        self.flipped = flipped

        # variables for shake effect
        self.shaking = False
        self.shake_timer = 0
        self.shake_duration = 0.3 # in seconds
        self.shake_amplitude = 1 # in pixels
        self.shake_speed = 40
        self.shake_seed = random.random() * 2 * math.pi # unique value to differentiate this shake from others

        # variables for fall effect
        self.angle = 0
        self.falling = False
        self.fall_timer = 0
        self.fall_duration = 1
        self.fall_direction = 1
        self.fall_speed = 2 + (random.random() * 3)

        super().__init__(game, x, y, tile=tile, layer=SPRITE_LAYER, image=None)
        self.set_shadow()

        self.draw_rect = self.rect  # .draw_rect may be different while shaking, but .rect will stay the same
        self.fall_image = self.image

        # settings for taking damage from axes
        self.health = TREE_HEALTH
        self.collision_rect = pg.Rect(
            0,
            0,
            1 * self.rect.width //3,
            1 * self.rect.height //3
        )
        self.collision_rect.topleft = (self.rect.topleft[0] + self.rect.width//3, self.rect.topleft[1] + 2*self.rect.width//3)

        self.game.can_collide_list.add(self)
        self.game.can_axe_list.add(self)

    def load_image(self):
        # load/set image name
        if not self.image_name:
            weights = self.get_spawn_weights()
            self.image_name = random.choices(list(weights.keys()), list(weights.values()))[0]

        # load sprite that corresponds with image name
        key = self.game.jsons.read("assets/trees/spritesheet_key.json")
        found = False
        for spritesheet in key:
            for sprite in spritesheet['sprites']:
                if sprite['name'] == self.image_name:
                    loadout = {
                        "path":spritesheet['path'],
                        "tile_size":spritesheet['tile_size'],
                        **sprite
                    }
                    found = True
                    break
            if found:
                break
        if not found:
            raise Exception(f"Couldn't find sprite for Tree `{self.image_name}`")

        # load and remove padding from image        
        scaled_image = self.game.sprites.load_from_tilesheet(
            path=loadout['path'],
            row_index=loadout['row_index'],
            col_index=loadout['col_index'],
            tile_size=loadout['tile_size'],
            resize=(TILE_SIZE*2, TILE_SIZE*2),
            remove_padding=True
        )

        # flip on vertical mirror if applicable
        if type(self.flipped) != bool:
            self.flipped = random.random() > 0.5
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)

        return scaled_image
    
    def set_shadow(self):
        # drop shadow
        self.shadow_color = (0, 0, 0, 50)
        self.shadow_width = int(self.rect.width * 0.6)  # 3/5 of the Tree width
        self.shadow_height = int(self.shadow_width / 3)  # 1/3 of the shadow width
        self.shadow_surface = pg.Surface((self.shadow_width, self.shadow_height), pg.SRCALPHA)

        # for checking isvisible() - want to render Tile if shadow is visible (otherwise shadow disappears when Tree goes out of view)
        self.shadow_topleft = (self.rect.centerx - self.shadow_width // 2, self.rect.bottom - 3 - self.shadow_height // 2)
        self.shadow_rect = pg.Rect(
            self.shadow_topleft[0],
            self.shadow_topleft[1],
            self.shadow_width,
            self.shadow_height
        )
        self.shadow_rect.topleft = self.shadow_topleft

        # draw the shadow onto the surface
        pg.draw.ellipse(self.shadow_surface, self.shadow_color, 
                        (0, 0, self.shadow_width, self.shadow_height))

    def update(self):
        # update falling animation after killed
        if self.falling:
            if self.fall_timer < self.fall_duration:
                self.angle += self.fall_speed * self.fall_direction
                self.image = pg.transform.rotate(self.fall_image, self.angle)
                self.draw_rect = self.image.get_rect(midbottom=self.rect.midbottom)
                if self.angle >= 360:
                    self.angle = 0
                self.fall_timer += self.game.dt
            else:
                self.fall_timer = 0
                self.falling = False
                self.die()

        # update shake animation after hit
        elif self.shaking:
            if self.shake_timer < self.shake_duration:
                # Calculate the displacement based on sine and cosine functions
                displacement_x = self.shake_amplitude * math.sin((self.shake_timer*self.shake_speed)+self.shake_seed)  # Adjust frequency for faster shaking
                displacement_y = self.shake_amplitude * math.cos((self.shake_timer*self.shake_speed)+self.shake_seed)
                # Apply the displacement to the Tree's position
                self.draw_rect.x += displacement_x
                self.draw_rect.y += displacement_y
                # Increment the timer
                self.shake_timer += self.game.dt
            else:
                # Reset the shake timer and position
                self.shake_timer = 0
                self.shaking = False
                self.draw_rect.x = self.rect[0]
                self.draw_rect.y = self.rect[1]

    def die(self):
        self.game.player.backpack.add_wood(self.game.player.wood_per_tree)
        
        if "Fruit" in self.image_name:
            self.game.player.modify_health(self.game.player.fruit_hp)
        elif "Apple" in self.image_name:
            self.game.player.modify_health(self.game.player.fruit_hp)

        self.kill()

    def draw(self, screen, camera):
        if not self.falling:
            screen.blit(self.shadow_surface, self.game.camera.apply_point(self.shadow_topleft))
        screen.blit(self.image, camera.apply(self.draw_rect))
        # self.draw_collision_rects(screen, camera)

    def register_hit(self, damage):
        """
        Take damage and/or start the shake cycle.
        """
        self.health -= damage
        if self.health <= 0:
            self.fall_timer = 0
            self.falling = True
            self.fall_direction = 1 if self.game.player.pos[0] > self.pos[0] else -1
            self.game.can_collide_list.remove(self)
            self.game.can_axe_list.remove(self)
        else:
            self.shake_timer = 0
            self.shaking = True

    def to_json(self):
        return {
            "type":type(self).__name__,
            "topleft":(self.x, self.y),
            "image_name":self.image_name,
            "flipped":self.flipped,
        }