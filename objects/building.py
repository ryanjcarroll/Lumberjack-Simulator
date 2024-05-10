from objects.sprites import SpriteObject
from settings import *
import random
import pygame as pg
from pygame import Vector2 as vec

class Building(SpriteObject):
    """
    Buildings have three rect attributes.

    self.rect - The area on which the sprite is drawn.
    self.build_rect - The area which is claimed for this building where no others may be built.
    self.collision_rect - The area that defines where the player will collide against the building.
    """
    def __init__(self, game, build_x, build_y, size):
        self.size = size
        super().__init__(game, build_x+TILE_SIZE, build_y+TILE_SIZE, layer=SPRITE_LAYER, image=None, can_collide=True)
        
        # rectangle for clearing a build area is equal to the image size
        self.build_rect = pg.Rect(
            build_x,
            build_y,
            self.rect.width + (TILE_SIZE),
            self.rect.height + (2*TILE_SIZE)
        )

        # rectangle for calculating collisions is smaller and shifted down
        self.collision_rect = pg.Rect(
            0,
            0,
            self.rect.width,
            self.rect.height
        )
        self.collision_rect.bottomleft = self.rect.bottomleft

        # add to buildings sprite group
        self.game.buildings_list.add(self)

    def load_image(self):
        sprite_loc = {"topleft": (128, 48), "width": 32, "height": 32}
        return pg.transform.scale(
            self.game.sprites.load_from_spritesheet(
                    path="assets/buildings/buildings.png",
                    topleft=sprite_loc['topleft'],
                    width=sprite_loc['width'],
                    height=sprite_loc['height']
                ),
                (TILE_SIZE*self.size[0], TILE_SIZE*(self.size[1]-1))
        )

    def build(self):
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

        self.image = pg.transform.scale(
            self.game.sprites.load_from_spritesheet(
                "assets/buildings/buildings.png",
                topleft=sprite_loc['topleft'],
                width=sprite_loc['width'],
                height=sprite_loc['height']
            ),
            (TILE_SIZE*self.size[0], TILE_SIZE*self.size[1])
        )
        self.rect = self.image.get_rect()
        self.rect = pg.Rect(
            self.collision_rect.left, 
            self.build_rect.top,
            self.image.get_width(),
            self.image.get_height()
        )
    
    def draw(self, screen, camera):
        # pg.draw.rect(screen, RED, camera.apply(self.build_rect))
        # pg.draw.rect(screen, BLUE, camera.apply(self.collision_rect))
        # pg.draw.rect(screen, GREEN, camera.apply(self.rect))
        super().draw(screen, camera)