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
from map.tile.tile_utility import get_image_from_texture, get_texture_from_neighbors
from map.tile.water import Water

class Tile(ABC):
    def __init__(self, game, chunk, row, col, is_explored=False, terrain="grass", texture={}):
        self.game = game
        self.chunk = chunk
        self.objects = []
        self.decor = []

        # texture variables        
        self.terrain = terrain
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

        self.load_decor()

        # load water
        if self.terrain == "water":
            water = Water(
                game=self.game,
                x=self.x,
                y=self.y,
                tile=self,
            )
            self.objects.append(water)

    @abstractmethod
    def get_spritesheet_path(self) -> str:
        pass

    @abstractmethod
    def get_tree_spawn_weights(self) -> str:
        pass

    def set_terrain(self, terrain):
        self.terrain = terrain
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

        n = [self.terrain, neighbors['right'].terrain, neighbors['bottom'].terrain, neighbors['bottomright'].terrain]
        self.texture = get_texture_from_neighbors(n)

        # pass in each neighbor spritesheet so corners can be rendered as the correct biome
        spritesheets = [self.get_spritesheet_path(), neighbors['right'].get_spritesheet_path(), neighbors['bottom'].get_spritesheet_path(), neighbors['bottomright'].get_spritesheet_path()]
        self.image = get_image_from_texture(self.texture, self.game.sprites, spritesheets)

        self.modify_image()
    
    def modify_image(self):
        # Overlay one of the pre-generated tile noise options on top of the tile image
        self.image.blit(
            random.choice(self.game.map.tile_noise_options), 
            (0, 0), 
            special_flags=pg.BLEND_RGBA_MULT
        )
        
    def can_spawn(self, spawn_attempts=3, max_offset=TILE_SIZE//2, buffer=3*TILE_SIZE//5):
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
                kwargs = {
                    "game":self.game, 
                    "x":d['topleft'][0],
                    "y":d['topleft'][1],
                    "tile":self
                }
                
                if "image_name" in d:
                    kwargs['image_name'] = d["image_name"]
                if "flipped" in d:
                    kwargs['flipped'] = d["flipped"]
                if "layer" in d:
                    kwargs['layer'] = d['layer']
                
                self.objects.append(
                    object_type(**kwargs)
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
                    tree_types = self.get_tree_spawn_weights()
                    tree_img_name = random.choices(population=list(tree_types.keys()), weights=list(tree_types.values()))[0]
                    if spawn_loc:
                        self.objects.append(Tree(self.game, *spawn_loc, self, image_name=tree_img_name))
                # # Spawn Bats
                # elif random.random() < .01:
                #     spawn_loc = self.can_spawn()
                #     if spawn_loc:
                #         self.objects.append(Bat(self.game, *spawn_loc, self))                
                # # Spawn Slimes
                # elif random.random() < .01:
                #     spawn_loc = self.can_spawn()
                #     if spawn_loc:
                #         self.objects.append(Slime(self.game, *spawn_loc, self))                
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
        decor_weights = self.get_decor_weights()

        if not self.terrain == "water" and decor_weights:
            item_type = random.choices(
                population = list(decor_weights.keys()),
                weights = list(decor_weights.values())
            )[0]

            decor_x = self.rect.center[0] + random.random() * TILE_SIZE//2
            decor_y = self.rect.center[1] + random.random() * TILE_SIZE//2

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
                    BLUE if self.terrain == "water" \
                        else GREEN if self.terrain=="grass" \
                        else RED if self.terrain == "dirt"\
                        else LIGHT_GREY if self.terrain == "snow"
                        else BLACK, 
                    camera.apply(self.rect), width=1
                )
            if DRAW_GRID:
                pg.draw.rect(
                    screen, 
                    RED if self.chunk.id == "0,0" and self.col == CHUNK_SIZE//2 and self.row == CHUNK_SIZE//2 \
                        else BLUE if self.terrain == "water" \
                        else GREEN if self.terrain=="grass" \
                        else RED if self.terrain == "dirt"\
                        else LIGHT_GREY if self.terrain == "snow"
                        else BLACK, 
                    camera.apply(self.rect), width=1
                )
        else:
            self.update_texture()
            # if image isn't set, try once more to update the texture
            if self.image:
                self.draw(screen, camera)

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
            "objects":[obj.to_json() for obj in self.objects if not isinstance(obj, Water)],
            "is_explored":self.is_explored,
            "texture":self.texture,
            "terrain":self.terrain
        }