import pygame as pg
from pygame import Vector2 as vec
from settings import *
import random
from glob import glob
from objects.sprites import SpriteObject
from abc import ABC, abstractmethod
from objects.tree import *
import opensimplex
from objects.items.items import SkillPoint
from objects.npcs.bat import Bat

class Tile(ABC):
    def __init__(self, game, chunk, row, col, has_decor):
        self.game = game
        self.chunk = chunk
        self.objects = []

        self.is_road = False

        # row & col position within chunk        
        self.row = row
        self.col = col

        # store the y coordinate for layer ordering during rendering
        self.x = chunk.rect.topleft[0] + (col * TILE_SIZE)
        self.y = chunk.rect.topleft[1] + (row * TILE_SIZE)
        
        # set image textures and load object sprites
        self.image = self.load_texture()
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(self.x,self.y)  
        if has_decor:
            self.load_decor()

    @abstractmethod
    def get_spritesheet_path(self) -> str:
        pass

    def load_texture(self):
        # set specific textures for Camp in the spawn chunk
        if self.chunk.id == "0,0":
            if CHUNK_SIZE//2 - 1 == self.row and CHUNK_SIZE//2 - 1 == self.col:
                row_index, col_index = (0,5) # top left
            elif CHUNK_SIZE//2 - 1 == self.row and CHUNK_SIZE//2 == self.col:
                row_index, col_index = (0,6) # top
            elif CHUNK_SIZE//2 - 1 == self.row and CHUNK_SIZE//2 + 1== self.col:
                row_index, col_index = (0,7) # top right
            elif CHUNK_SIZE//2 == self.row and CHUNK_SIZE//2 - 1 == self.col:
                row_index, col_index = (1,5) # left
            elif CHUNK_SIZE//2 == self.row and CHUNK_SIZE//2 == self.col:
                row_index, col_index = (2,2) # center
            elif CHUNK_SIZE//2 == self.row and CHUNK_SIZE//2 + 1== self.col:
                row_index, col_index = (1,7) # right
            elif CHUNK_SIZE//2 + 1 == self.row and CHUNK_SIZE//2 - 1 == self.col:
                row_index, col_index = (2,5) # bot left
            elif CHUNK_SIZE//2 + 1 == self.row and CHUNK_SIZE//2 == self.col:
                row_index, col_index = (2,6) # bot
            elif CHUNK_SIZE//2 + 1 == self.row and CHUNK_SIZE//2 + 1== self.col:
                row_index, col_index = (2,7) # bot right
            else:
                row_index, col_index = (4,5) # grass
        else:
            row_index, col_index = (4,5) # grass

        image = pg.transform.scale(
            self.game.sprites.load_from_tilesheet(
                path=self.get_spritesheet_path(),
                row_index=row_index,
                col_index=col_index,
                tile_size=32
            )
            ,(TILE_SIZE, TILE_SIZE)
        )
        # return image

        TILE_NOISE_FACTOR = .005
        darkness = 215 + (30 * opensimplex.noise2(self.x*TILE_NOISE_FACTOR, self.y*TILE_NOISE_FACTOR))
        # Create a semi-transparent black surface with the same size as the image
        dark_surface = pg.Surface(image.get_size(), pg.SRCALPHA)
        dark_surface.fill((darkness,darkness,darkness+10, 200))  # Fill with semi-transparent black

        # Blend the original image with the dark surface
        darkened_image = pg.Surface(image.get_size(), pg.SRCALPHA)
        darkened_image.blit(image, (0, 0))  # Blit the original image onto the darkened surface
        darkened_image.blit(dark_surface, (0, 0), special_flags=pg.BLEND_MULT)  # Multiply blend the dark surface

        return darkened_image

    def load_objects(self):
        """
        Uses the following params to calibrate:

        self.tree_density
        self.tree_type
        """
        # spawn trees everywhere except the 3x3 square around the spawn location
        spawn_attempts = 3
        buffer = TILE_SIZE//2
        max_offset = TILE_SIZE//2

        if TILE_SIZE*((CHUNK_SIZE//2)-1) <= self.x <= TILE_SIZE*((CHUNK_SIZE//2)+1)\
            and TILE_SIZE*((CHUNK_SIZE//2)-1) <= self.y <= TILE_SIZE*((CHUNK_SIZE//2)+1) :
            # spawn nothing in the Camp area
            pass
        else:  
            r = random.random()
            # Spawn Trees
            if r < self.tree_density: # spawn only on a percentage of tiles         
                neighbors = self.get_neighbors()
                neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]
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
                        self.objects.append(self.tree_type(self.game, *try_pos))
                        break
            # Spawn Bats
            elif r > 0.99:
                neighbors = self.get_neighbors()
                neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]
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
                        self.objects.append(Bat(self.game, *try_pos))                
                        break
            # Spawn Skill Points
            elif r > 0.98: # spawn an SkillPoint item on a small percentage of tiles which don't have a tree
                neighbors = self.get_neighbors()
                neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]
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
                        self.objects.append(SkillPoint(self.game, *try_pos))                
                        break
                
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
        self.objects.append(
            SpriteObject(
                game=self.game,
                x = decor_x,
                y = decor_y,
                layer = DECOR_LAYER,
                image = self.game.sprites.load(random.choice(glob(f"assets/decor/{item_type}/*.png"))),
        ))

    def get_neighbors(self):
        """
        Get the 8 adjacent tiles to this 
        """
        neighbors = []

        # find neighboring tiles by coordinate offsets
        offsets = [(drow, dcol) for drow in [-1, 0, 1] for dcol in [-1, 0, 1] if (drow,dcol)!=(0,0)]

        # if we need to access any chunks besides the current one, store them in a dict by id for quick re-access
        current_chunk = self.chunk
        neighboring_chunks = {} 

        for offset in offsets:
            drow, dcol = offset
            row = self.row + drow
            col = self.col + dcol

            # if neighbor is in the same chunk, we can use row and col indexes to find it
            if row > 0 and row < CHUNK_SIZE and col > 0 and col < CHUNK_SIZE:
                for tile in current_chunk.tiles:
                    if tile.row == row and tile.col == col:
                        neighbors.append(tile)
            # if the neighbor would be in another chunk, attempt to load it from that chunk (if that chunk exists)
            else:
                row %= CHUNK_SIZE
                col %= CHUNK_SIZE

                # find the neighbor-chunk
                chunk_id = self.game.map.get_chunk_id(
                    self.rect.topleft[0] + dcol*TILE_SIZE, 
                    self.rect.topleft[1] + drow*TILE_SIZE
                )
                if chunk_id in self.game.map.chunks:
                    # attempt to load referece from dictionary for subsequent uses
                    if chunk_id in neighboring_chunks:
                        chunk = neighboring_chunks[chunk_id]
                    # save reference to the dictionary if first time seeing this neighbor-chunk
                    else:
                        chunk = self.game.map.chunks[chunk_id]
                        neighboring_chunks[chunk_id] = chunk
                
                    # find the tile by row/col index within the neighbor-chunk
                    for tile in chunk.tiles:
                        if tile.row == row and tile.col == col:
                            neighbors.append(tile)
                else:
                    # if the chunk is not loaded, don't try to load its neighbor tiles
                    pass

        return neighbors

    def get_neighbor(self, direction):
        """
        Get the neighbor of this tile in the specified direction.
        
        Args:
            direction (str): The direction of the neighbor ('north', 'south', 'east', or 'west').
        
        Returns:
            Tile or None: The neighbor tile if it exists, otherwise None.
        """
        # Calculate the row and col offsets based on the direction
        if direction == 'north':
            d_row, d_col = -1, 0
        elif direction == 'south':
            d_row, d_col = 1, 0
        elif direction == 'east':
            d_row, d_col = 0, 1
        elif direction == 'west':
            d_row, d_col = 0, -1
        else:
            raise ValueError("Invalid direction. Please use 'north', 'south', 'east', or 'west'.")

        # Calculate the row and col of the neighbor tile
        neighbor_row = self.row + d_row
        neighbor_col = self.col + d_col

        # If the neighbor tile is within the bounds of the chunk
        if 0 <= neighbor_row < CHUNK_SIZE and 0 <= neighbor_col < CHUNK_SIZE:
            # Find the neighbor tile in the current chunk
            for tile in self.chunk.tiles:
                if tile.row == neighbor_row and tile.col == neighbor_col:
                    return tile
        else:
            # If the neighbor tile is outside the current chunk, attempt to load it from another chunk
            neighbor_row %= CHUNK_SIZE
            neighbor_col %= CHUNK_SIZE

            # Calculate the position of the neighbor tile in the game world
            neighbor_x = self.rect.topleft[0] + d_col * TILE_SIZE
            neighbor_y = self.rect.topleft[1] + d_row * TILE_SIZE
            
            # Get the chunk ID corresponding to the position
            chunk_id = self.game.map.get_chunk_id(neighbor_x, neighbor_y)

            # If the chunk is loaded
            if chunk_id in self.game.map.chunks:
                # Get the chunk
                chunk = self.game.map.chunks[chunk_id]

                # Find the neighbor tile in the chunk
                for tile in chunk.tiles:
                    if tile.row == neighbor_row and tile.col == neighbor_col:
                        return tile

        return None  # If the neighbor tile is not found, return None

    def draw(self, screen, camera):
        # draw self.image for base layer
        # if layer == BASE_LAYER:
        screen.blit(self.image, camera.apply(self.rect))

        # # for other layers, draw all objects in that layer
        # for obj in self.objects:
        #     if obj.alive() and obj.render_layer == layer:
        #         obj.draw(screen, camera)

    def to_json(self):
        return {
            "type":type(self),
            "topleft":self.rect.topleft,
            "objects":[obj.to_json for obj in self.objects]
        }

class ForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        self.tree_density = 0.6
        self.tree_type = Tree
        self.decor_weights = {
            "butterfly" : 2,
            "flower"    : 3,
            "grass"     : 30,
            "patch"     : 20,
            "pebble"    : 5,
        }

        super().__init__(game, chunk, row, col, has_decor)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/forest_tileset.png"

class IceForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        self.tree_density = 0.5
        self.tree_type = IceTree
        self.decor_weights = {
            "pebble":10,
            "print":3,
            "grass":3,
            "stone":5
        }

        super().__init__(game, chunk, row, col, has_decor)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/ice_forest_tileset.png"
    
    def load_decor(self):
        # load decor only a percentage of the time
        if random.random() > 0.5:
            super().load_decor()
    
class AutumnForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        self.tree_density = 0.7
        self.tree_type = AutumnTree
        self.decor_weights = {
            "pebble":2,
            "flower":10,
            "grass":50,
            "butterfly":5
        }

        super().__init__(game, chunk, row, col, has_decor)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/autumn_forest_tileset.png"
    
    # def load_decor(self):
    #     # load decor multiple times
    #     for i in range(2):
    #         super().load_decor()
    
 
class MangroveForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        self.tree_density = 0.8
        self.tree_type = MangroveTree
        self.decor_weights = {}

        super().__init__(game, chunk, row, col, has_decor)

    def get_spritesheet_path(self) -> str:
        return "assets/textures/mangrove_forest_tileset.png"
    
    def load_decor(self):
        # don't load decor on mangrove forest tiles
        pass

class WaterTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        self.decor_weights = {}
        super().__init__(game, chunk, row, col, has_decor)

    # unused
    def get_spritesheet_path(self) -> str:
        return ""

    def load_texture(self):
        return pg.transform.scale(
            self.game.sprites.load("assets/textures/water.png"),
            (TILE_SIZE, TILE_SIZE)
        )

    def load_decor(self):
        # dont load decor on water tiles
        pass

    def load_objects(self):
        self.objects.append(SpriteObject(
            game=self.game,
            x=self.x,
            y=self.y,
            image=self.game.sprites.load("assets/textures/transparent.png"),
            layer=BASE_LAYER,
            can_collide=True
        ))