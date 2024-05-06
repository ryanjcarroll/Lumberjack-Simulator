import pygame as pg
from settings import *
from utility import remove_padding_and_scale
from pygame import Vector2 as vec
import math
import random
from objects.sprite_object import SpriteObject

class Tree(SpriteObject):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, layer=SPRITE_LAYER, img_path=None, collision=True, hittable=True)
        
        # settings for taking damage from axes
        self.health = TREE_HEALTH
        if "Burned" in self.tree_type:
            self.health = 1
        self.collision_rect = pg.Rect(
            0,
            0,
            2 * self.rect.width //3,
            2 * self.rect.height //3
        )
        self.collision_rect.topleft = (self.rect.topleft[0] + self.rect.width//6, self.rect.topleft[1] + self.rect.width//3)

        # variables for shake effect
        self.draw_rect = self.rect  # .draw_rect may be different while shaking, but .rect will stay the same
        self.shaking = False
        self.shake_timer = 0
        self.shake_duration = 0.3 # in seconds
        self.shake_amplitude = 1 # in pixels
        self.shake_speed = 40
        self.shake_seed = random.random() * 2 * math.pi # unique value to differentiate this shake from others

    def load_texture(self):
       
        self.flipped = random.random() > 0.5
        tree_type_weights = {
            "Burned_tree1":5,
            "Burned_tree2":5,
            "Burned_tree3":5,
            "Christmas_tree1":10,
            "Christmas_tree2":10,
            "Christmas_tree3":10,
            "Flower_tree1":2,
            "Flower_tree2":2,
            "Flower_tree3":2,
            "Fruit_tree1":3,
            "Fruit_tree2":3,
            "Tree1":50,
            "Tree2":50,
            "Tree3":50,
        }
        self.tree_type = random.choices(
            population = list(tree_type_weights.keys()),
            weights = list(tree_type_weights.values())
        )[0]

        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                self.game.sprites.load(f"assets/trees/{self.tree_type}.png")
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)
        self.image = scaled_image

    def update(self, dt):
        if self.shaking:
            if self.shake_timer < self.shake_duration:
                # Calculate the displacement based on sine and cosine functions
                displacement_x = self.shake_amplitude * math.sin((self.shake_timer*self.shake_speed)+self.shake_seed)  # Adjust frequency for faster shaking
                displacement_y = self.shake_amplitude * math.cos((self.shake_timer*self.shake_speed)+self.shake_seed)
                # Apply the displacement to the Tree's position
                self.draw_rect.x += displacement_x
                self.draw_rect.y += displacement_y
                # Increment the timer
                self.shake_timer += dt
            else:
                # Reset the shake timer and position
                self.shake_timer = 0
                self.shaking = False
                self.draw_rect.x = self.rect[0]
                self.draw_rect.y = self.rect[1]

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.draw_rect))
        # self.draw_collision_rects(screen, camera)

    def register_hit(self, damage):
        """
        Take damage and/or start the shake cycle.
        """
        self.health -= damage
        if self.health <= 0:
            self.kill()
        else:
            self.shake_timer = 0
            self.shaking = True

class IceTree(Tree):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)

    def load_texture(self):     
        self.flipped = random.random() > 0.5
        tree_type_weights = {
            "Burned_tree1":5,
            "Burned_tree2":5,
            "Burned_tree3":5,
            "Snow_christmas_tree1":10,
            "Snow_christmas_tree2":10,
            "Snow_christmas_tree3":10,
            "Snow_tree1":10,
            "Snow_tree2":10,
            "Snow_tree3":10,
        }
        self.tree_type = random.choices(
            population = list(tree_type_weights.keys()),
            weights = list(tree_type_weights.values())
        )[0]

        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                self.game.sprites.load(f"assets/trees/{self.tree_type}.png")
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)
        self.image = scaled_image

class AutumnTree(Tree):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)

    def load_texture(self):     
        self.flipped = random.random() > 0.5
        tree_type_weights = {
            "Burned_tree1":10,
            "Burned_tree2":10,
            "Burned_tree3":10,
            "Autumn_tree1":30,
            "Autumn_tree2":30,
            "Autumn_tree3":30,
            "Tree1":8,
            "Tree2":8,
            "Tree3":8,
            "Fruit_tree1":10,
            "Fruit_tree2":10,
            "Apple_tree":5,
        }
        self.tree_type = random.choices(
            population = list(tree_type_weights.keys()),
            weights = list(tree_type_weights.values())
        )[0]

        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                self.game.sprites.load(f"assets/trees/{self.tree_type}.png")
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)
        self.image = scaled_image

class MangroveTree(Tree):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)

    def load_texture(self):     
        self.flipped = random.random() > 0.5
        tree_type_weights = {
            "Moss_tree1":20,
            "Moss_tree2":20,
            "Moss_tree3":20,
            "Palm_tree1_1":5,
            "Palm_tree1_2":5,
            "Palm_tree2_1":5,
            "Palm_tree2_2":5,
            "Tree1":2,
            "Tree2":2,
            "Tree3":2,
        }
        self.tree_type = random.choices(
            population = list(tree_type_weights.keys()),
            weights = list(tree_type_weights.values())
        )[0]

        # load an image, remove transparent boundaries, and scale it to size
        scaled_image = pg.transform.scale(
            remove_padding_and_scale(
                self.game.sprites.load(f"assets/trees/{self.tree_type}.png")
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # randomly flip 50% of images along their Y-axis
        if self.flipped:
            scaled_image = pg.transform.flip(scaled_image, True, False)
        self.image = scaled_image