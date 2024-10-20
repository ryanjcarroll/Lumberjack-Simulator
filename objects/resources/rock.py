import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import math
import random
from objects.sprites import SpriteObject

class Rock(SpriteObject):
    def __init__(self, game, x, y, tile, image_name=None, flipped=None):

        self.image_name = image_name
        self.flipped = flipped
        self.spawn_weights = self.get_spawn_weights()

        super().__init__(game, x, y, tile=tile, layer=SPRITE_LAYER, image=None)

        self.health = ROCK_HEALTH

        self.collision_rect = pg.Rect(
            0,
            0,
            2 * self.rect.width //3,
            2 * self.rect.height //3
        )
        self.collision_rect.center = self.rect.center

        self.game.can_pick_list.add(self)
        self.game.can_collide_list.add(self)

    def get_spawn_weights(self) -> dict:
        return {
            "7":1,
            "8":1,
            "9":1,
            "10":1,
            "11":1,
            "12":1,
            "13":1,
            "14":1,
            "15":1,
            "16":1,
        }
    
    def load_image(self):
        # only set flipped and image_name if they weren't passed
        if type(self.flipped) != bool:
            self.flipped = random.random() > 0.5
        if not self.image_name:
            self.image_name = random.choices(
                population = list(self.spawn_weights.keys()),
                weights = list(self.spawn_weights.values()),
            )[0]

        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                self.game.sprites.load(f"assets/rock/{self.image_name}.png")
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)

        return scaled_image

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))
        # self.draw_collision_rects(screen, camera)

    def register_hit(self, damage):
        """
        Take damage and/or start the shake cycle.
        """
        self.health -= damage
        if self.health <= 0:
            self.game.can_collide_list.remove(self)
            self.game.can_axe_list.remove(self)
            self.die()
        
    def die(self):
        self.game.player.backpack.add_wood(self.game.player.wood_per_tree)

        self.kill()

    def to_json(self):
        return {
            "type":type(self).__name__,
            "topleft":(self.x, self.y),
            "image_name":self.image_name,
            "flipped":self.flipped
        }