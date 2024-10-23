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
from utility import combine_images

class Tile(ABC):
    def __init__(self, game, chunk, row, col, load_decor=False, is_explored=False, tile_type="grass", texture=None):
        self.game = game
        self.chunk = chunk
        self.objects = []
        self.decor = []

        # texture variables        
        self.tile_type = tile_type
        self.texture = texture # will be set to a spritesheet tuple once neighbors are loaded
        self.base_texture = None
        self.image = None

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

        # the draw rect will be offset by half a tile to the bottom right (bottomright)
        self.draw_rect = pg.Rect(
            self.x + TILE_SIZE//2,
            self.y  + TILE_SIZE//2,
            TILE_SIZE,
            TILE_SIZE
        )
        # if load_decor:
        #     self.load_decor()

        # load water
        if self.tile_type == "water":
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

    @abstractmethod
    def get_spritesheet_path(self) -> str:
        pass

    def set_tile_type(self, tile_type):
        self.tile_type = tile_type
        self.update_texture()
        for neighbor in [self.get_neighbors("top"), self.get_neighbors("left"), self.get_neighbors("topleft")]:
            neighbor.update_texture()

    def update_texture(self):
        # Spawn Chunk
        neighbors = {
            direction:self.get_neighbors(direction=direction) 
            for direction in ['right','bottom','bottomright']
        }

        # set the texture as long as all 4 neighbors of the draw_rect exist
        if all([neighbor is not None for neighbor in neighbors.values()]):
            # 4-tile congfiguration - [topleft, topright, bottomleft, bottomright]
            n = [self.tile_type, neighbors['right'].tile_type, neighbors['bottom'].tile_type, neighbors['bottomright'].tile_type]
            
            # configurations for all-one-texture
            if len(set(n)) == 1:
                if n == ['grass', 'grass', 'grass', 'grass']:
                    self.texture = (0,0)
                elif n == ['water', 'water', 'water', 'water']:
                    self.texture = (0,3)
                elif n == ['sand', 'sand', 'sand', 'sand']:
                    self.texture = (0,1)  
                elif n == ['clay', 'clay', 'clay', 'clay']:
                    self.texture = (0,2)  

            elif set(n) == set(["grass","water"]):
                # 14 possible grass/water configurations of the 4 neighboring tiles of the draw_rect
                if n == ['grass', 'grass', 'grass', 'water']:
                    self.texture = (5, 3)
                elif n == ['grass', 'grass', 'water', 'grass']:
                    self.texture = (5, 4)
                elif n == ['grass', 'water', 'water', 'water']:
                    self.texture = (6, 2)
                elif n == ['grass', 'water', 'grass', 'grass']:
                    self.texture = (6, 3)
                elif n == ['grass', 'grass', 'water', 'water']:
                    self.texture = (6, 1)
                elif n == ['grass', 'water', 'grass', 'water']:
                    self.texture = (5, 2)
                elif n == ['grass', 'water', 'water', 'grass']:
                    self.texture = (4, 4)
                elif n == ['water', 'water', 'water', 'grass']:
                    self.texture = (4, 0)
                elif n == ['water', 'water', 'grass', 'water']:
                    self.texture = (4, 2)
                elif n == ['water', 'grass', 'grass', 'grass']:
                    self.texture = (6, 4)
                elif n == ['water', 'grass', 'water', 'water']:
                    self.texture = (6, 0)
                elif n == ['water', 'water', 'grass', 'grass']:
                    self.texture = (4, 1)
                elif n == ['water', 'grass', 'water', 'grass']:
                    self.texture = (5, 0)
                elif n == ['water', 'grass', 'grass', 'water']:
                    self.texture = (4, 3)

            elif len(set(n)) == 2 and "grass" in n:
                if "sand" in n:
                    self.base_texture = (0,1)
                elif "clay" in n:
                    self.base_texture = (0,2)
                
                # 14 possible grass/other configurations of the 4 neighboring tiles of the draw_rect
                n = ["grass" if t=="grass" else "other" for t in n]
                if n == ['grass', 'grass', 'grass', 'other']:
                    self.texture = (2, 3)
                elif n == ['grass', 'grass', 'other', 'grass']:
                    self.texture = (2, 4)
                elif n == ['grass', 'other', 'other', 'other']:
                    self.texture = (3, 2)
                elif n == ['grass', 'other', 'grass', 'grass']:
                    self.texture = (3, 3)
                elif n == ['grass', 'grass', 'other', 'other']:
                    self.texture = (3, 1)
                elif n == ['grass', 'other', 'grass', 'other']:
                    self.texture = (2, 2)
                elif n == ['grass', 'other', 'other', 'grass']:
                    self.texture = (1, 4)
                elif n == ['other', 'other', 'other', 'grass']:
                    self.texture = (1, 0)
                elif n == ['other', 'other', 'grass', 'other']:
                    self.texture = (1, 2)
                elif n == ['other', 'grass', 'grass', 'grass']:
                    self.texture = (3, 4)
                elif n == ['other', 'grass', 'other', 'other']:
                    self.texture = (3, 0)
                elif n == ['other', 'other', 'grass', 'grass']:
                    self.texture = (1, 1)
                elif n == ['other', 'grass', 'other', 'grass']:
                    self.texture = (2, 0)
                elif n == ['other', 'grass', 'grass', 'other']:
                    self.texture = (1, 3)

        default = (9,7)
        if self.base_texture:
            base = self.game.sprites.load_from_tilesheet(
                path=self.get_spritesheet_path(),
                row_index=self.base_texture[0],
                col_index=self.base_texture[1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
            )
            top = self.game.sprites.load_from_tilesheet(
                    path=self.get_spritesheet_path(),
                    row_index=self.texture[0] if self.texture else default[0],
                    col_index=self.texture[1] if self.texture else default[1],
                    tile_size=16,
                    resize=(TILE_SIZE, TILE_SIZE)
            )
            image = combine_images([base, top])
        else:
            image = self.game.sprites.load_from_tilesheet(
                    path=self.get_spritesheet_path(),
                    row_index=self.texture[0] if self.texture else default[0],
                    col_index=self.texture[1] if self.texture else default[1],
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
            direction (str): The direction of the neighbor (e.g. 'left', or 'bottomright').
        
        Returns:
            dict: A dictionary of with direction as the key and a tile object as the value.
        """
        # Calculate the x and y offsets based on the direction
        d_values = {
            "top":vec(0, -1),
            'bottom':vec(0, 1),
            'right':vec(1, 0),
            'left':vec(-1, 0)
        }
        d_values['topright'] = d_values['top'] + d_values['right']
        d_values['topleft'] = d_values['top'] + d_values['left']
        d_values['bottomright'] = d_values['bottom'] + d_values['right']
        d_values['bottomleft'] = d_values['bottom'] + d_values['left']

        output = {}
        if direction:
            return self.__get_neighbor(int(d_values[direction].x), int(d_values[direction].y))
        else:
            for direction, d_vec in d_values.items():
                output[direction] = self.__get_neighbor(int(d_vec.x), int(d_vec.y))
            return output

    def __get_neighbor(self, dx, dy):
        """
        Private utility method called by get_neighbors()
        """
        neighbor_x, neighbor_y = self.x + dx * TILE_SIZE, self.y + dy * TILE_SIZE
        neighbor_chunk_id = self.game.map.get_chunk_id(neighbor_x, neighbor_y)
        neighbor_col, neighbor_row = (
            int((neighbor_x % (CHUNK_SIZE*TILE_SIZE)) // TILE_SIZE), 
            int((neighbor_y % (CHUNK_SIZE*TILE_SIZE)) // TILE_SIZE)
        )
        
        # if neighbor is in same chunk as currentt
        if neighbor_chunk_id == self.chunk.id:
            return self.chunk.get_tile(neighbor_row, neighbor_col)
        # if neighbor is in a different chunk, and that chunk is loaded
        elif neighbor_chunk_id in self.game.map.chunks:
            return self.game.map.chunks[neighbor_chunk_id].get_tile(neighbor_row, neighbor_col)
        # if neighbor is in a chunk that doesn't exist in memory
        else:
            return None

    def draw(self, screen, camera):
        if self.image:
            screen.blit(self.image, camera.apply(self.draw_rect))
            # pg.draw.rect(
            #     screen, 
            #     BLUE if self.tile_type == "water" else GREEN if self.tile_type=="grass" else YELLOW if self.tile_type=="sand" else RED, 
            #     camera.apply(self.rect), width=1
            # )
        else:
            print("NO IMAGE")

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
            "is_explored":self.is_explored,
            "texture":self.texture,
            "tile_type":self.tile_type
        }

class ForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture=None):
        self.tree_density = 0.8
        self.rock_density = 0.07
        self.tree_type = ForestTree
        self.decor_weights = {
            "butterfly" : 2,
            "flower"    : 3,
            "grass"     : 30,
            "patch"     : 20,
            "pebble"    : 5,
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored, tile_type, texture)

        self.color = (119,177,82)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"

class IceForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture=None):
        self.tree_density = 0.25
        self.rock_density = 0.15
        self.tree_type = IceTree
        self.decor_weights = {
            "pebble":10,
            "print":3,
            "grass":3,
            # "rock":5
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored, tile_type, texture)

        self.color = (237,237,237)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"
    
    def load_decor(self):
        # load decor only a percentage of the time
        if random.random() > 0.5:
            super().load_decor()
    
class AutumnForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture=None):
        self.tree_density = 0.75
        self.rock_density = 0.05
        self.tree_type = AutumnTree
        self.decor_weights = {
            "pebble":2,
            "flower":10,
            "grass":50,
            "butterfly":5
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored, tile_type, texture)

        self.color = (136,177,79)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"
 
class MangroveForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture=None):
        self.tree_density = 0.8
        self.rock_density = 0.05
        self.tree_type = MangroveTree
        self.decor_weights = {}

        super().__init__(game, chunk, row, col, load_decor, is_explored, tile_type, texture)

        self.color = (100,153,61)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"
    
    def load_decor(self):
        # don't load decor on mangrove forest tiles
        pass

class WaterTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="water", texture=None):
        self.decor_weights = {}
        super().__init__(game, chunk, row, col, load_decor, is_explored, tile_type, texture)
        self.tile_type = "water"

        self.color = (54,140,249)

    # unused
    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"
            
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