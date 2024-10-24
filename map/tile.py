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

texture_positions = {
    "grass":(0,0),
    "sand":(0,1),
    "clay":(0,2),
    "water":(0,3),
    "snow":(0,4)
}

class Tile(ABC):
    def __init__(self, game, chunk, row, col, load_decor=False, is_explored=False, tile_type="grass", texture={}):
        self.game = game
        self.chunk = chunk
        self.objects = []
        self.decor = []

        # texture variables        
        self.tile_type = tile_type
        self.texture = texture # will be set to a spritesheet tuple once neighbors are loaded
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
        if load_decor:
            self.load_decor()

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
            if neighbor:
                neighbor.update_texture()

    def update_texture(self):
        neighbors = {
            direction:self.get_neighbors(direction=direction) 
            for direction in ['right','bottom','bottomright']
        }
        # ensure all neighbors are loaded before attempting to set texture
        if None in neighbors.values():
            return None

        n = [self.tile_type, neighbors['right'].tile_type, neighbors['bottom'].tile_type, neighbors['bottomright'].tile_type]
        self.texture = get_texture_from_neighbors(n)
        self.image = get_image_from_texture(self.texture, self.game.sprites, "assets/textures/tile2.png")
    
    def modify_image(self):
        TILE_NOISE_FACTOR = .005
        darkness = 215 + (30 * opensimplex.noise2(self.x*TILE_NOISE_FACTOR, self.y*TILE_NOISE_FACTOR))
        # Create a semi-transparent black surface with the same size as the image
        dark_surface = pg.Surface(self.image.get_size(), pg.SRCALPHA)
        dark_surface.fill((darkness,darkness,darkness+10, 200))  # Fill with semi-transparent black

        # Blend the original image with the dark surface
        darkened_image = pg.Surface(self.image.get_size(), pg.SRCALPHA)
        darkened_image.blit(self.image, (0, 0))  # Blit the original image onto the darkened surface
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
        
            if DRAW_GRID:
                pg.draw.rect(
                    screen, 
                    BLUE if self.tile_type == "water" \
                        else GREEN if self.tile_type=="grass" \
                        else YELLOW if self.tile_type=="sand" \
                        else RED if self.tile_type == "clay"\
                        else LIGHT_GREY if self.tile_type == "snow"
                        else BLACK, 
                    camera.apply(self.rect), width=1
                )
            if DRAW_GRID:
                pg.draw.rect(
                    screen, 
                    RED if self.chunk.id == "0,0" and self.col == CHUNK_SIZE//2 and self.row == CHUNK_SIZE//2 \
                        else BLUE if self.tile_type == "water" \
                        else GREEN if self.tile_type=="grass" \
                        else YELLOW if self.tile_type=="sand" \
                        else RED if self.tile_type == "clay"\
                        else LIGHT_GREY if self.tile_type == "snow"
                        else BLACK, 
                    camera.apply(self.rect), width=1
                )
        else:
            self.update_texture()
            # if image isn't set, try once more to update the texture
            if self.image:
                self.draw(screen, camera)
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
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture={}):
        self.tree_density = 0.8
        self.rock_density = 0.07
        self.tree_type = ForestTree
        self.decor_weights = {
            "butterfly" : 2,
            "flower"    : 3,
            "grass"     : 30,
            "pebble"    : 5,
        }

        super().__init__(game, chunk, row, col, load_decor, is_explored, tile_type, texture)

        self.color = (119,177,82)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"

class IceForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="snow", texture={}):
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
    
    # def modify_image(self):
    #     pass

    def get_spritesheet_path(self) -> str:
        return "assets/textures/tile2.png"
    
    def load_decor(self):
        # load decor only a percentage of the time
        if random.random() > 0.5:
            super().load_decor()
    
class AutumnForestTile(Tile):
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture={}):
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
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="grass", texture={}):
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
    def __init__(self, game, chunk, row, col, load_decor=True, is_explored=False, tile_type="water", texture={}):
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


# UTILITY METHODS:
def get_texture_from_neighbors(n):
    texture = {}

    # configurations for all-one-texture
    if len(set(n)) == 1:
        texture['base'] = texture_positions[n[0]]

    elif set(n) == set(["grass","water"]):
        # 14 possible grass/water configurations of the 4 neighboring tiles of the draw_rect
        if n == ['grass', 'grass', 'grass', 'water']:
            texture['base'] = (5, 3)
        elif n == ['grass', 'grass', 'water', 'grass']:
            texture['base'] = (5, 4)
        elif n == ['grass', 'water', 'water', 'water']:
            texture['base'] = (6, 2)
        elif n == ['grass', 'water', 'grass', 'grass']:
            texture['base'] = (6, 3)
        elif n == ['grass', 'grass', 'water', 'water']:
            texture['base'] = (6, 1)
        elif n == ['grass', 'water', 'grass', 'water']:
            texture['base'] = (5, 2)
        elif n == ['grass', 'water', 'water', 'grass']:
            texture['base'] = (4, 4)
        elif n == ['water', 'water', 'water', 'grass']:
            texture['base'] = (4, 0)
        elif n == ['water', 'water', 'grass', 'water']:
            texture['base'] = (4, 2)
        elif n == ['water', 'grass', 'grass', 'grass']:
            texture['base'] = (6, 4)
        elif n == ['water', 'grass', 'water', 'water']:
            texture['base'] = (6, 0)
        elif n == ['water', 'water', 'grass', 'grass']:
            texture['base'] = (4, 1)
        elif n == ['water', 'grass', 'water', 'grass']:
            texture['base'] = (5, 0)
        elif n == ['water', 'grass', 'grass', 'water']:
            texture['base'] = (4, 3)

    elif len(set(n)) > 1:   
        # extract only the base textures
        base_textures = [None if tex in["grass","snow"] else tex for tex in n]

        texture['base_corners'] = []
        for i, corner in enumerate(base_textures):
            if corner != None:
                sheet_pos = texture_positions[corner]
                texture['base_corners'].append(sheet_pos)
            else:
                texture['base_corners'].append(None)

        # apply grass textures in a layer over base and snow tiles
        if "grass" in n:
            n_grass = ["top" if t in ["grass","snow"] else "bottom" for t in n]
            if n_grass == ['top', 'top', 'top', 'top']:
                texture['grass'] = (2, 1)
            elif n_grass == ['top', 'top', 'top', 'bottom']:
                texture['grass'] = (2, 3)
            elif n_grass == ['top', 'top', 'bottom', 'top']:
                texture['grass'] = (2, 4)
            elif n_grass == ['top', 'bottom', 'bottom', 'bottom']:
                texture['grass'] = (3, 2)
            elif n_grass == ['top', 'bottom', 'top', 'top']:
                texture['grass'] = (3, 3)
            elif n_grass == ['top', 'top', 'bottom', 'bottom']:
                texture['grass'] = (3, 1)
            elif n_grass == ['top', 'bottom', 'top', 'bottom']:
                texture['grass'] = (2, 2)
            elif n_grass == ['top', 'bottom', 'bottom', 'top']:
                texture['grass'] = (1, 4)
            elif n_grass == ['bottom', 'bottom', 'bottom', 'top']:
                texture['grass'] = (1, 0)
            elif n_grass == ['bottom', 'bottom', 'top', 'bottom']:
                texture['grass'] = (1, 2)
            elif n_grass == ['bottom', 'top', 'top', 'top']:
                texture['grass'] = (3, 4)
            elif n_grass == ['bottom', 'top', 'bottom', 'bottom']:
                texture['grass'] = (3, 0)
            elif n_grass == ['bottom', 'bottom', 'top', 'top']:
                texture['grass'] = (1, 1)
            elif n_grass == ['bottom', 'top', 'bottom', 'top']:
                texture['grass'] = (2, 0)
            elif n_grass == ['bottom', 'top', 'top', 'bottom']:
                texture['grass'] = (1, 3)

        # apply snow textures in a layer over base and grass tiles
        if "snow" in n:
            n_snow = ["top" if t in ["snow"] else "bottom" for t in n]
            if n_snow == ['top', 'top', 'top', 'top']:
                texture['snow'] = (8, 1)
            elif n_snow == ['top', 'top', 'top', 'bottom']:
                texture['snow'] = (8, 3)
            elif n_snow == ['top', 'top', 'bottom', 'top']:
                texture['snow'] = (8, 4)
            elif n_snow == ['top', 'bottom', 'bottom', 'bottom']:
                texture['snow'] = (9, 2)
            elif n_snow == ['top', 'bottom', 'top', 'top']:
                texture['snow'] = (9, 3)
            elif n_snow == ['top', 'top', 'bottom', 'bottom']:
                texture['snow'] = (9, 1)
            elif n_snow == ['top', 'bottom', 'top', 'bottom']:
                texture['snow'] = (8, 2)
            elif n_snow == ['top', 'bottom', 'bottom', 'top']:
                texture['snow'] = (7, 4)
            elif n_snow == ['bottom', 'bottom', 'bottom', 'top']:
                texture['snow'] = (7, 0)
            elif n_snow == ['bottom', 'bottom', 'top', 'bottom']:
                texture['snow'] = (7, 2)
            elif n_snow == ['bottom', 'top', 'top', 'top']:
                texture['snow'] = (9, 4)
            elif n_snow == ['bottom', 'top', 'bottom', 'bottom']:
                texture['snow'] = (9, 0)
            elif n_snow == ['bottom', 'bottom', 'top', 'top']:
                texture['snow'] = (7, 1)
            elif n_snow == ['bottom', 'top', 'bottom', 'top']:
                texture['snow'] = (8, 0)
            elif n_snow == ['bottom', 'top', 'top', 'bottom']:
                texture['snow'] = (7, 3)

    return texture

def get_image_from_texture(texture, sprite_manager, spritesheet:str):
    image = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)

    # set the base image
    if "base" in texture:

        # set single-texture and water/grass base images
        img = sprite_manager.load_from_tilesheet(
            path=spritesheet,
            row_index=texture['base'][0],
            col_index=texture['base'][1],
            tile_size=16,
            resize=(TILE_SIZE, TILE_SIZE)
        )
        image.blit(img, (0,0))

    # set multi-texture base images
    elif "base_corners" in texture:
        image = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        blit_positions = { # where to blit each corner
            0:(0,0),
            1:(TILE_SIZE//2, 0),
            2:(0, TILE_SIZE//2),
            3:(TILE_SIZE//2, TILE_SIZE//2)
        }
        for i, tex in enumerate(texture['base_corners']):
            if tex is not None:
                image.blit(
                    sprite_manager.load_from_tilesheet(
                        spritesheet,
                        row_index=tex[0],
                        col_index=tex[1],
                        tile_size=16,
                        resize=(TILE_SIZE//2, TILE_SIZE//2)
                    ),
                    blit_positions[i]
                )

    # blit the grass layer, if applicable
    if "grass" in texture:
        image.blit(
            sprite_manager.load_from_tilesheet(
                spritesheet,
                row_index=texture['grass'][0],
                col_index=texture['grass'][1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
            ),
            (0,0)
        )
    # blit the snow layer, if applicable
    if "snow" in texture:
        image.blit(
            sprite_manager.load_from_tilesheet(
                spritesheet,
                row_index=texture['snow'][0],
                col_index=texture['snow'][1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
            ),
            (0,0)
        )
    return image
