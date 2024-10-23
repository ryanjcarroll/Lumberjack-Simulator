import pygame as pg
from pygame import Vector2 as vec
from settings import *
import random
from glob import glob
from objects.sprites import SpriteObject
from abc import ABC, abstractmethod
from objects.resources.tree import *
from objects.resources.rock import Rock
import opensimplex
from objects.items.items import SkillPoint
from objects.npcs.bat import Bat
from objects.npcs.slime import Slime
from objects.inventory import Camp
from objects.player.player import Player
from objects.npcs.butterfly import Butterfly
from objects.npcs.grasshopper import Grasshopper
from objects.npcs.ladybug import Ladybug

class Tile(ABC):
    def __init__(self, game, chunk, row, col, load_decor=False, is_explored=False):
        self.game = game
        self.chunk = chunk
        self.objects = []
        self.decor = []

        self.is_road = False

        # row & col position within chunk        
        self.row = row
        self.col = col

        # store the y coordinate for layer ordering during rendering
        self.x = chunk.rect.topleft[0] + (col * TILE_SIZE)
        self.y = chunk.rect.topleft[1] + (row * TILE_SIZE)
        self.rect = pg.Rect(
            self.x,
            self.y,
            TILE_SIZE,
            TILE_SIZE
        )

        # minimap variables
        self.color = BLACK
        self.is_explored = is_explored # sets to true once the tile is drawn on scren

        # the draw rect will be offset by half a tile to the bottom right (southeast)
        self.draw_rect = pg.Rect(
            self.x + TILE_SIZE//2,
            self.y  + TILE_SIZE//2,
            TILE_SIZE,
            TILE_SIZE
        )

    @abstractmethod
    def get_spritesheet_path(self) -> str:
        pass

    def load_texture(self):
        # Spawn Chunk
        neighbors = {direction:neighbor for direction, neighbor in self.get_neighbors().items() if direction in ['east','south','southeast']}
        if all([neighbor is not None for direction, neighbor in neighbors.items()]):
            # 14 possible configurations of the 4 neighboring tiles of the draw_rect
            if self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (2,12)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "water":
                index = (13,3)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (13,4)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "water":
                index = (14,2)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (14,3)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "water":
                index = (14,1)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "water":
                index = (13,2)
            elif self.tile_type == "grass" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (15,12)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "water":
                index = (13,12)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (12,0)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "water":
                index = (12,2)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (14,4)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "water":
                index = (14,0)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "water" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (12,1)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "water" \
                    and neighbors['southeast'].tile_type == "grass":
                index = (13,0)
            elif self.tile_type == "water" \
                    and neighbors['east'].tile_type == "grass" \
                    and neighbors['south'].tile_type == "grass" \
                    and neighbors['southeast'].tile_type == "water":
                index = (15,11)
            else:
                index = (2,12)
        else:
            index = (2,12)

        image = self.game.sprites.load_from_tilesheet(
                path=self.get_spritesheet_path(),
                row_index=index[0],
                col_index=index[1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
        )

        TILE_NOISE_FACTOR = .005
        darkness = 215 + (30 * opensimplex.noise2(self.x*TILE_NOISE_FACTOR, self.y*TILE_NOISE_FACTOR))
        # Create a semi-transparent black surface with the same size as the image
        dark_surface = pg.Surface(image.get_size(), pg.SRCALPHA)
        dark_surface.fill((darkness,darkness,darkness+10, 200))  # Fill with semi-transparent black

        # Blend the original image with the dark surface
        darkened_image = pg.Surface(image.get_size(), pg.SRCALPHA)
        darkened_image.blit(image, (0, 0))  # Blit the original image onto the darkened surface
        darkened_image.blit(dark_surface, (0, 0), special_flags=pg.BLEND_MULT)  # Multiply blend the dark surface

        # set image textures and load object sprites 
        self.image = darkened_image
        self.load_decor()
    
    def can_spawn(self, spawn_attempts=3, max_offset=TILE_SIZE//3, buffer=2*TILE_SIZE//3):
        """
        Attempt to find a pos to spawn an object.

        spawn_attempts - number of positions to check
        max_offset - how far from the tile topleft to search
        buffer - how far from other collidable objects to allow
        """
        neighbors = self.get_neighbors() # a dictionary of "direction":Tile
        neighbor_objs = [
            obj 
            for direction, tile in neighbors.items() 
            if hasattr(tile, 'objects') 
            for obj in tile.objects
        ]
        for i in range(spawn_attempts):
            try_pos = vec(
                self.rect.topleft[0] + random.randrange(0,max_offset), 
                self.rect.topleft[1] + random.randrange(0,max_offset)
            )
            spawn = True
            for obj in [obj for obj in neighbor_objs if obj in self.game.can_collide_list]:
                if try_pos.distance_to(obj.pos) <= buffer:
                    spawn = False
                    break

            if spawn:
                return try_pos
            else:
                return False

    def load_objects(self, objects=None):
        """
        Uses the following params to calibrate:
        """
        # Load from Save Data
        if type(objects) == list:
            for d in objects:
                object_type = globals()[d['type']]
                args = [self.game, *d['topleft'], self]
                
                if "image_name" in d:
                    args.append(d["image_name"])
                if "flipped" in d:
                    args.append(d["flipped"])
                    
                self.objects.append(
                    object_type(*args)
                )

        # Create New Objects from Scratch
        else:
            # spawn things everywhere except the 3x3 square around the spawn location
            if TILE_SIZE*((CHUNK_SIZE//2)-1) <= self.x <= TILE_SIZE*((CHUNK_SIZE//2)+1)\
                and TILE_SIZE*((CHUNK_SIZE//2)-1) <= self.y <= TILE_SIZE*((CHUNK_SIZE//2)+1) :
                # spawn nothing in the Camp area
                pass
            else:
                # Spawn Trees
                if random.random() < self.tree_density: # spawn only on a percentage of tiles  
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        self.objects.append(self.tree_type(self.game, *spawn_loc, self))
                # Spawn Bats
                elif random.random() < .01:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        self.objects.append(Bat(self.game, *spawn_loc, self))                
                # Spawn Slimes
                elif random.random() < .01:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        self.objects.append(Slime(self.game, *spawn_loc, self))                
                # Spawn Skill Points
                elif random.random() < .005: # spawn an SkillPoint item on a small percentage of tiles which don't have a tree
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        self.objects.append(SkillPoint(self.game, *spawn_loc, self))      
                # Spawn Rocks
                elif random.random() < self.rock_density: # spawn an SkillPoint item on a small percentage of tiles which don't have a tree
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        self.objects.append(Rock(self.game, *spawn_loc, self))    
                # Spawn Butterflies
                elif random.random() < .05:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        Butterfly(self.game, self.rect.centerx, self.rect.centery, self)     
                # Spawn Grasshoppers
                elif random.random() < .02:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        Grasshopper(self.game, self.rect.centerx, self.rect.centery, self)      
                # Spawn Ladybugs
                elif random.random() < .02:
                    spawn_loc = self.can_spawn()
                    if spawn_loc:
                        Ladybug(self.game, self.rect.centerx, self.rect.centery, self)      
                
    def load_decor(self):
        decor_weights = self.decor_weights

        item_type = random.choices(
            population = list(decor_weights.keys()),
            weights = list(decor_weights.values())
        )[0]

        decor_x = self.rect.center[0] + random.random() * TILE_SIZE//2
        decor_y = self.rect.center[1] + random.random() * TILE_SIZE//2
        # decor_x = random.randint(self.rect.left, self.rect.right)
        # decor_y = random.randint(self.rect.top, self.rect.bottom)
        self.decor.append(
            SpriteObject(
                game=self.game,
                x = decor_x,
                y = decor_y,
                tile = self,
                layer = DECOR_LAYER,
                image = self.game.sprites.load(random.choice(glob(f"assets/decor/{item_type}/*.png"))),
        ))

    def get_neighbors(self, direction=None):
        """
        Get the neighbor(s) of the current tile, indexed by direction.
        If no direction is passed, all 8 neighboring tiles will be returned.
        
        Args:
            direction (str): The direction of the neighbor (e.g. 'north', or 'southwest').
        
        Returns:
            dict: A dictionary of with direction as the key and a tile object as the value.
        """
        # Calculate the row and col offsets based on the direction
        d_values = {
            "north":vec(-1, 0),
            'south':vec(1, 0),
            'east':vec(0, 1),
            'west':vec(0, -1)
        }
        d_values['northeast'] = d_values['north'] + d_values['east']
        d_values['northwest'] = d_values['north'] + d_values['west']
        d_values['southeast'] = d_values['south'] + d_values['east']
        d_values['southwest'] = d_values['south'] + d_values['west']

        output = {}
        if direction:
            return self.__get_neighbor(d_values[direction].x, d_values[direction].y)
        else:
            for direction, d_vec in d_values.items():
                output[direction] = self.__get_neighbor(d_vec.x, d_vec.y)
            return output

    def __get_neighbor(self, d_row, d_col):
        """
        Private utility method called by get_neighbors()
        """
        neighbor_row = self.row + d_row
        neighbor_col = self.col + d_col

        # If neighbor is within the same chunk
        if 0 <= neighbor_row < CHUNK_SIZE and 0 <= neighbor_col < CHUNK_SIZE:
            return self.chunk.get_tile(neighbor_row, neighbor_col)
        
        # If neighbor is in an adjacent chunk, calculate the correct chunk and position
        else:
            d_chunk = vec(0,0)

            # chunk to left
            if self.x < self.chunk.rect.left:
                d_chunk += vec(-1,0)
            # chunk to right
            if self.x > self.chunk.rect.right:
                d_chunk += vec(1,0)
            # chunk above
            if self.y < self.chunk.rect.top:
                d_chunk += vec(0,-1)
            # chunk below
            if self.y > self.chunk.rect.bottom:
                d_chunk += vec(0,1)

            # calculate the id of the neighboring chunk
            neighbor_chunk_x = int(self.chunk.rect.x + (d_chunk.x * CHUNK_SIZE * TILE_SIZE))
            neighbor_chunk_y = int(self.chunk.rect.y + (d_chunk.y * CHUNK_SIZE * TILE_SIZE))
            neighbor_chunk_id = f"{neighbor_chunk_x},{neighbor_chunk_y}"
            
            # If the new chunk is loaded
            if neighbor_chunk_id in self.game.map.chunks:
                neighbor_chunk = self.game.map.chunks[neighbor_chunk_id]

                # Calculate the row/col within the new chunk (wrap around)
                neighbor_row = neighbor_row % CHUNK_SIZE
                neighbor_col = neighbor_col % CHUNK_SIZE

                # Find the tile in the new chunk
                return neighbor_chunk.get_tile(neighbor_row, neighbor_col)
            else:
                return None

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.draw_rect))
        pg.draw.rect(screen, BLUE, camera.apply(self.rect), width=1)
        pg.draw.rect(screen, RED, camera.apply(self.draw_rect), width=1)

        # # for other layers, draw all objects in that layer
        # for obj in self.objects:
        #     if obj.alive() and obj.render_layer == layer:
        #         obj.draw(screen, camera)

    def unload(self):
        for object in self.objects:
            if isinstance(object, Player) or isinstance(object, Camp):
                continue
            else:
                object.kill()

        for decor in self.decor:
            decor.kill()

    def to_json(self):
        return {
            "type":type(self).__name__,
            "position":[self.row, self.col],
            "objects":[obj.to_json() for obj in self.objects],
            "is_explored":self.is_explored
        }

class ForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False):
        self.tree_density = 0.8
        self.rock_density = 0.07
        self.tile_type = "grass"
        self.biome = "forest"
        self.tree_type = ForestTree
        self.decor_weights = {
            "butterfly" : 2,
            "flower"    : 3,
            "grass"     : 30,
            "patch"     : 20,
            "pebble"    : 5,
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored)

        self.color = (119,177,82)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"

class IceForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False):
        self.tree_density = 0.25
        self.rock_density = 0.15
        self.tile_type = "grass"
        self.biome = "ice"
        self.tree_type = IceTree
        self.decor_weights = {
            "pebble":10,
            "print":3,
            "grass":3,
            # "rock":5
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored)

        self.color = (237,237,237)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
    
    def load_decor(self):
        # load decor only a percentage of the time
        if random.random() > 0.5:
            super().load_decor()
    
class AutumnForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False):
        self.tree_density = 0.75
        self.rock_density = 0.05
        self.tile_type = "grass"
        self.biome = "autumn"
        self.tree_type = AutumnTree
        self.decor_weights = {
            "pebble":2,
            "flower":10,
            "grass":50,
            "butterfly":5
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored)

        self.color = (136,177,79)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
 
class MangroveForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False):
        self.tree_density = 0.8
        self.rock_density = 0.05
        self.tile_type = "grass"
        self.biome = "mangrove"
        self.tree_type = MangroveTree
        self.decor_weights = {}

        super().__init__(game, chunk, row, col, load_decor, is_explored)

        self.color = (100,153,61)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
    
    def load_decor(self):
        # don't load decor on mangrove forest tiles
        pass

class WaterTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False):
        self.decor_weights = {}
        self.biome = "water"
        self.tile_type = "water"
        super().__init__(game, chunk, row, col, load_decor, is_explored)

        self.color = (54,140,249)

    # unused
    def get_spritesheet_path(self) -> str:
        return "assets/textures/tiles.png"
            
    def load_decor(self):
        # dont load decor on water tiles
        pass

    def load_objects(self, objects=None):
        # load water
        water = SpriteObject(
            game=self.game,
            x=self.x,
            y=self.y,
            tile=self,
            image=self.game.sprites.load("assets/textures/transparent.png"),
            layer=BASE_LAYER,
        )
        self.game.can_collide_list.add(water)
        self.objects.append(water)