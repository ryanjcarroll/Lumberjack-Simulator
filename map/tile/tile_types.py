from settings import *
from map.tile.tile import Tile
from objects.sprites import SpriteObject
import random
from objects.npcs.bat import Bat
from objects.npcs.slime import Slime
from objects.npcs.butterfly import Butterfly
from objects.npcs.grasshopper import Grasshopper
from objects.npcs.ladybug import Ladybug

water_color = (8, 140, 201)

class SwampTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="dirt", texture={}):
        self.biome = "Swamp"
        self.tree_density = 0.75
        self.rock_density = 0.07

        self.chunk = chunk
        self.game = game
        self.x = chunk.rect.topleft[0] + (col * TILE_SIZE)
        self.y = chunk.rect.topleft[1] + (row * TILE_SIZE)
        self.terrain = terrain
        self.set_terrain()

        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if self.terrain=="water" else (64, 89, 8)

    def set_terrain(self):
        noise = self.game.map.rain_noise_gen.noise2(self.x, self.y)
        if noise > 0.1:
            self.terrain = "water"
    
    def load_objects(self, objects=None):
        load_more = super().load_objects(objects)
        if load_more and LOAD_CREATURES:
            # Spawn Slimes
            if random.random() < .01:
                spawn_loc = self.can_spawn()
                if spawn_loc:
                    self.objects.append(Slime(self.game, *spawn_loc, self))   

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
        self.biome = "Desert"
        self.tree_density = 0.05
        self.rock_density = 0.05
        self.game = game
        self.terrain = terrain
        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if terrain=="water" else (173, 162, 31)

    def load_objects(self, objects=None):
        load_more = super().load_objects(objects)
        if load_more and LOAD_CREATURES:
            # Spawn Grasshoppers
            if random.random() < .02:
                spawn_loc = self.can_spawn()
                if spawn_loc:
                    Grasshopper(self.game, self.rect.centerx, self.rect.centery, self)     

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
        self.biome = "Forest"
        self.tree_density = 0.75
        self.rock_density = 0.07
        self.terrain = terrain
        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)
        self.color = water_color if terrain=="water" else (11, 115, 32)

    def load_objects(self, objects=None):
        load_more = super().load_objects(objects)
        if load_more and LOAD_CREATURES:
            # Spawn Butterflies
            if random.random() < .02:
                spawn_loc = self.can_spawn()
                if spawn_loc:
                    Butterfly(self.game, self.rect.centerx, self.rect.centery, self)        
            # Spawn Ladybugs
            elif random.random() < .02:
                spawn_loc = self.can_spawn()
                if spawn_loc:
                    Ladybug(self.game, self.rect.centerx, self.rect.centery, self)        

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
        self.biome = "Rainforest"
        self.tree_density = 0.85
        self.rock_density = 0.05
        self.game = game
        self.x = chunk.rect.topleft[0] + (col * TILE_SIZE)
        self.y = chunk.rect.topleft[1] + (row * TILE_SIZE)
        self.terrain = terrain
        self.set_terrain()
        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if terrain=="water" else (6, 87, 48)

    def set_terrain(self):
        noise = self.game.map.rain_noise_gen.noise2(self.x, self.y)
        if noise > 0.5:
            self.terrain = "dirt"

    def load_objects(self, objects=None):
        load_more = super().load_objects(objects)
        if load_more and LOAD_CREATURES:
            # Spawn Bats
            if random.random() < .01:
                spawn_loc = self.can_spawn()
                if spawn_loc:
                    self.objects.append(Bat(self.game, *spawn_loc, self))  
            # Spawn Butterflies
            elif random.random() < .05:
                spawn_loc = self.can_spawn()
                if spawn_loc:
                    Butterfly(self.game, self.rect.centerx, self.rect.centery, self)        

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
        self.biome = "Grassland"
        self.tree_density = 0.2
        self.rock_density = 0.01
        self.terrain = terrain
        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if terrain=="water" else (81, 156, 23)

    def load_objects(self, objects=None):
        load_more = super().load_objects(objects)
        if load_more and LOAD_CREATURES:
                # Spawn Ladybugs
                if random.random() < .02:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        Ladybug(self.game, self.rect.centerx, self.rect.centery, self)    

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles-grassland.png"
    
    def set_terrain(self, terrain):
        super().set_terrain(terrain)
        
        if terrain != "grass":
            for obj in self.decor:
                obj.kill()
        
    def load_decor(self):
        super().load_decor()

        if self.terrain == "grass":
            for i in range(10):
                pos = (
                    self.rect.topleft[0] + int(random.random() * TILE_SIZE),
                    self.rect.topleft[1] + int(random.random() * TILE_SIZE)
                )
                self.decor.append(
                    SpriteObject(
                        self.game,
                        *pos,
                        tile = self,
                        layer = DECOR_LAYER,
                        image = self.game.sprites.load(random.choice([
                            "assets/decor/grass/12.png",
                            "assets/decor/grass/13.png"
                        ])),
                    )
                )
    
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
        self.biome = "Tundra"
        self.tree_density = 0.5
        self.rock_density = 0.05
        self.terrain = terrain
        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if terrain=="water" else (153, 225, 240)

    def load_objects(self, objects=None):
        load_more = super().load_objects(objects)
        if load_more and LOAD_CREATURES:
                # Spawn Bats
                if random.random() < .05:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        Bat(self.game, self.rect.centerx, self.rect.centery, self)    

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
    
class LakeTile(Tile):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="water", texture={}):
        self.biome = "Lake"
        self.tree_density = 0
        self.rock_density = 0
        self.terrain = terrain
        super().__init__(game, chunk, row, col, is_explored, self.terrain, texture)

        self.color = water_color if terrain=="water" else (211, 211, 245)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
    
    def get_tree_spawn_weights(self):
        return {}
    
    def get_decor_weights(self):
        return {}

