from objects.sprites import SpriteObject
from settings import *
import random
import pygame as pg
from pygame import Vector2 as vec

class Building(SpriteObject):
    def __init__(self, game, x, y, size):
        self.size = size
        super().__init__(game, x, y, layer=SPRITE_LAYER, image=None, can_collide=True)
        
        # rectangle for clearing a build area is equal to the image size
        self.build_rect = pg.Rect(
            0,
            0,
            self.rect.width,
            self.rect.height
        )
        self.build_rect.bottomleft = self.rect.bottomleft

        # rectangle for calculating collisions is smaller and shifted down
        self.collision_rect = pg.Rect(
            0,
            0,
            self.rect.width,
            self.rect.height - TILE_SIZE
        )
        self.collision_rect.bottomleft = self.rect.bottomleft

        # super().add([self.game.buildings_list])

    def load_image(self):
        if self.size == (2,2):
            sprite_loc = random.choice([
                {"topleft": (0, 39), "width": 63, "height": 73},
                {"topleft": (3, 452), "width": 74, "height": 76},
                {"topleft": (4, 534), "width": 72, "height": 74},
                {"topleft": (674, 448), "width": 77, "height": 80},
            ])
        elif self.size == (3,2):
            sprite_loc = random.choice([
                {"topleft":(971,39),"width":101,"height":73},
                {"topleft":(0,324),"width":112,"height":75}, 
                {"topleft":(0,613),"width":96,"height":75},
                {"topleft":(149,882),"width":133,"height":110},
            ])
        elif self.size == (1,2):
            sprite_loc = random.choice([
                {"topleft":(1032,124),"width":36,"height":68},
                {"topleft":(984,124),"width":36,"height":68},
            ])
        elif self.size == (4,3):
            sprite_loc = random.choice([
                {"topleft":(0,774),"width":127,"height":106},
            ])

        return pg.transform.scale(
            self.game.sprites.load_from_spritesheet(
                "assets/buildings/buildings.png",
                topleft=sprite_loc['topleft'],
                width=sprite_loc['width'],
                height=sprite_loc['height']
            ),
            (TILE_SIZE*self.size[0], TILE_SIZE*self.size[1])
        )
    
    def draw(self, screen, camera):
        # pg.draw.rect(screen, RED, camera.apply(self.build_rect))
        # pg.draw.rect(screen, BLUE, camera.apply(self.collision_rect))
        super().draw(screen, camera)