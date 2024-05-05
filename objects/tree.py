import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import random
from objects.sprite_object import SpriteObject

import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import random
from objects.sprite_object import SpriteObject

class Tree(SpriteObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, img_path=None, collision=True, hittable=True)
        
        self.health = TREE_HEALTH

    def load_texture(self):
       
        self.flipped = random.random() > 0.5

        tree_type_weights = {
            "Burned_tree1":5,
            "Burned_tree2":5,
            "Burned_tree3":5,
            "Christmas_tree1":10,
            "Christmas_tree2":10,
            "Christmas_tree3":10,
            "Flower_tree1":1,
            "Flower_tree2":1,
            "Flower_tree3":1,
            "Fruit_tree1":3,
            "Fruit_tree2":3,
            "Fruit_tree3":3,
            "Moss_tree1":20,
            "Moss_tree2":20,
            "Moss_tree3":20,
            "Tree1":50,
            "Tree2":50,
            "Tree3":50,
            "TreeDecor":50,
        }
        self.tree_type = random.choices(
            population = list(tree_type_weights.keys()),
            weights = list(tree_type_weights.values())
        )[0]

        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                pg.image.load(f"assets/trees/{self.tree_type}.png")
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)
        self.image = scaled_image