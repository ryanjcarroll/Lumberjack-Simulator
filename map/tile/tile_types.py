from settings import *
from map.tile.tile import Tile
import pygame as pg

water_color = (8, 140, 201)

class SwampTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="dirt", texture={}):
        self.tree_density = 0.75
        self.rock_density = 0.07

        self.game = game
        self.x = chunk.rect.topleft[0] + (col * TILE_SIZE)
        self.y = chunk.rect.topleft[1] + (row * TILE_SIZE)
        self.terrain = terrain
        self.terrain = self.set_terrain()

        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if terrain=="water" else (64, 89, 8)

    def set_terrain(self):
        noise = self.game.map.rain_noise_gen.noise2(self.x, self.y)
        if noise > 0.1:
            return "water"
        else:
            return self.terrain

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles-swamp.png"
    
    def get_tree_spawn_weights(self):
        return {
            # "CozyBirch1":1,
            "CozyDead1":1,
            "Moss1":1,
            "Moss2":1
        }
    
    def get_decor_weights(self):
        return {}

class DesertTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="dirt", texture={}):
        self.tree_density = 0.05
        self.rock_density = 0.05
        super().__init__(game, chunk, row, col, is_explored, terrain, texture)

        self.color = water_color if terrain=="water" else (173, 162, 31)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles-desert.png"
    
    def get_tree_spawn_weights(self):
        return {
            "Dead1":1,
            "Dead2":1
        }
    
    def get_decor_weights(self):
        return {}

class ForestTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="grass", texture={}):
        self.tree_density = 0.75
        self.rock_density = 0.07
        super().__init__(game, chunk, row, col, is_explored, terrain, texture)
        self.color = water_color if terrain=="water" else (11, 115, 32)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
    
    def get_tree_spawn_weights(self):
        return {
            "Oak1":1,
            "CozyOak1":1,
            "CozyOak2":1,
            "CozyAutumn1":1,

        }
    
    def get_decor_weights(self):
        return {}

class RainforestTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="grass", texture={}):
        self.tree_density = 0.85
        self.rock_density = 0.05
        super().__init__(game, chunk, row, col, is_explored, terrain, texture)

        self.color = water_color if terrain=="water" else (6, 87, 48)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles-rainforest.png"
    
    def get_tree_spawn_weights(self):
        return {
            "Cone1":1,
            "CozyGreen1":3,
        }

    def get_decor_weights(self):
        return {}
 
class GrasslandTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="grass", texture={}):
        self.tree_density = 0.2
        self.rock_density = 0.01
        super().__init__(game, chunk, row, col, is_explored, terrain, texture)

        self.color = water_color if terrain=="water" else (81, 156, 23)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles-grassland.png"
    
    def load_decor(self):
        # for i in range(5):
        #     super().load_decor()
        pass

    def get_tree_spawn_weights(self):
        return {
            "Pink1":1,
            "Pink2":1,
            "CozyPink1":1,
            "CozyRough1":4,
            "Autumn1":1,
            "Autumn2":1
        }
    
    def get_decor_weights(self):
        return {}
    
class TundraTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="snow", texture={}):
        self.tree_density = 0.6
        self.rock_density = 0.05
        super().__init__(game, chunk, row, col, is_explored, terrain, texture)

        self.color = water_color if terrain=="water" else (153, 225, 240)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
        
    def get_tree_spawn_weights(self):
        return {
            "SnowCone1":2,
            "SnowCone2":2,
            "SnowDead1":1,
            "SnowDead2":1
        }
    
    def get_decor_weights(self):
        return {}
    
class MountainTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="snow", texture={}):
        self.tree_density = 0.1
        self.rock_density = 0.25
        super().__init__(game, chunk, row, col, is_explored, terrain, texture)

        self.color = water_color if terrain=="water" else (211, 211, 245)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles-mountain.png"
    
    def get_tree_spawn_weights(self):
        return {
            "SnowDead1":3,
            "SnowDead2":3,
            "SnowCone1":1,
            "SnowCone2":1
        }
    
    def get_decor_weights(self):
        return {}

