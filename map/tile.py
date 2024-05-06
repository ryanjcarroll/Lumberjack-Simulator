import pygame as pg
from pygame import Vector2 as vec
from settings import *
from utility import extract_image_from_spritesheet
import random
from glob import glob
from objects.sprite_object import SpriteObject
import opensimplex
from abc import ABC, abstractmethod
from objects.tree import Tree, IceTree, AutumnTree

class Tile(ABC):
    def __init__(self, game, chunk, row, col, has_decor):
        self.game = game
        self.chunk = chunk
        self.objects = []

        # row & col position within chunk        
        self.row = row
        self.col = col

        # store the y coordinate for layer ordering during rendering
        self.x = chunk.rect.topleft[0] + (col * TILE_SIZE)
        self.y = chunk.rect.topleft[1] + (row * TILE_SIZE)
        
        # set image textures and load object sprites
        self.image = self.get_texture()
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(self.x,self.y)  
        if has_decor:
            self.load_decor()

    @abstractmethod
    def get_texture(self) -> pg.image:
        # must return a pg.image to use as tile base layer
        pass

    @abstractmethod
    def get_decor_weights(self) -> dict:        
        # returns a dictionary of decor asset paths and their random choice weights
        pass
    
    @abstractmethod
    def load_objects(self, tree_density=0.9):
        # render objects within a tile
        pass

    def load_decor(self):
        decor_weights = self.get_decor_weights()

        item_type = random.choices(
            population = list(decor_weights.keys()),
            weights = list(decor_weights.values())
        )[0]

        decor_x = random.randint(self.rect.left, self.rect.right)
        decor_y = random.randint(self.rect.top, self.rect.bottom)
        self.objects.append(
            SpriteObject(
                game=self.game,
                x = decor_x,
                y = decor_y,
                img_path = random.choice(glob(f"assets/decor/{item_type}/*.png")),
                layer = DECOR_LAYER
        ))

    def get_neighbors(self):
        """
        Get the 8 adjacent tiles to this 
        """
        neighbors = []

        # find neighboring tiles by coordinate offsetss
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

    def draw(self, layer, screen, camera):
        # draw self.image for base layer
        if layer == BASE_LAYER:
            screen.blit(self.image, camera.apply(self.rect))

        # for other layers, draw all objects in that layer
        for obj in self.objects:
            if obj.alive() and obj.render_layer == layer:
                obj.draw(screen, camera)

    def to_json(self):
        return {
            "type":type(self),
            "topleft":self.rect.topleft,
            "objects":[obj.to_json for obj in self.objects]
        }

class ForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        super().__init__(game, chunk, row, col, has_decor)

    def get_texture(self):
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

        return pg.transform.scale(
            extract_image_from_spritesheet(
                spritesheet=self.game.sprites.load("assets/textures/forest_tileset.png"),
                row_index=row_index,
                col_index=col_index,
                tile_size=32
            )
            ,(TILE_SIZE, TILE_SIZE)
        )

    def get_decor_weights(self):
        # weights for various decor paths
        # assets/decor/{item_type}/*.png
        return {
            "butterfly" : 2,
            "flower"    : 3,
            "grass"     : 30,
            "patch"     : 20,
            "pebble"    : 5,
        }
    
    def load_objects(self):
        # spawn trees everywhere except the 3x3 square around the spawn location
        spawn_attempts = 3
        buffer = TILE_SIZE//2
        max_offset = TILE_SIZE//2

        if TILE_SIZE*((CHUNK_SIZE//2)-1) <= self.x <= TILE_SIZE*((CHUNK_SIZE//2)+1)\
            and TILE_SIZE*((CHUNK_SIZE//2)-1) <= self.y <= TILE_SIZE*((CHUNK_SIZE//2)+1) :
            # spawn nothing in the Camp area
            pass
        else:  
            if random.random() < 0.7: # spawn only on a percentage of tiles         
                neighbors = self.get_neighbors()
                neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]
                for i in range(spawn_attempts):
                    try_pos = vec(
                        self.rect.topleft[0] + random.randrange(0,max_offset), 
                        self.rect.topleft[1] + random.randrange(0,max_offset)
                    )
                    spawn = True
                    for obj in [obj for obj in neighbor_objs if isinstance(obj, Tree)]:
                        if try_pos.distance_to(obj.pos) <= buffer:
                            spawn = False
                            break

                    if spawn:
                        self.objects.append(Tree(self.game, *try_pos))
                        break


class IceForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        super().__init__(game, chunk, row, col, has_decor)

    def get_texture(self):
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

        return pg.transform.scale(
            extract_image_from_spritesheet(
                spritesheet=self.game.sprites.load("assets/textures/ice_forest_tileset.png"),
                row_index=row_index,
                col_index=col_index,
                tile_size=32
            )
            ,(TILE_SIZE, TILE_SIZE)
        )

    def get_decor_weights(self):
        return {
            "pebble":10,
            "dirt":2,
            "grass":10,
            "stone":5
        }
    
    def load_objects(self):
        # spawn trees everywhere except the 3x3 square around the spawn location
        spawn_attempts = 3
        buffer = TILE_SIZE//2
        max_offset = TILE_SIZE//2
    
        neighbors = self.get_neighbors()
        neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]

        # spawn trees
        if random.random() < 0.4: # spawn only on a percentage of tiles         
            for i in range(spawn_attempts):
                try_pos = vec(
                    self.rect.topleft[0] + random.randrange(0,max_offset), 
                    self.rect.topleft[1] + random.randrange(0,max_offset)
                )
                spawn = True
                for obj in [obj for obj in neighbor_objs if isinstance(obj, Tree)]:
                    if try_pos.distance_to(obj.pos) <= buffer:
                        spawn = False
                        break

                if spawn:
                    self.objects.append(IceTree(self.game, *try_pos))
                    break


class AutumnForestTile(Tile):
    def __init__(self, game, chunk, row, col, has_decor=True):
        super().__init__(game, chunk, row, col, has_decor)

    def get_texture(self):
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

        return pg.transform.scale(
            extract_image_from_spritesheet(
                spritesheet=self.game.sprites.load("assets/textures/autumn_forest_tileset.png"),
                row_index=row_index,
                col_index=col_index,
                tile_size=32
            )
            ,(TILE_SIZE, TILE_SIZE)
        )

    def get_decor_weights(self):
        return {
            "pebble":10,
            "flower":10,
            "grass":100,
            "patch":100,
            "butterfly":5
        }
    
    def load_decor(self):
        decor_weights = self.get_decor_weights()

        for i in range(2):
            item_type = random.choices(
                population = list(decor_weights.keys()),
                weights = list(decor_weights.values())
            )[0]

            decor_x = random.randint(self.rect.left, self.rect.right)
            decor_y = random.randint(self.rect.top, self.rect.bottom)
            self.objects.append(
                SpriteObject(
                    game=self.game,
                    x = decor_x,
                    y = decor_y,
                    img_path = random.choice(glob(f"assets/decor/{item_type}/*.png")),
                    layer = DECOR_LAYER
            ))
    
    def load_objects(self):
        # spawn trees everywhere except the 3x3 square around the spawn location
        spawn_attempts = 3
        buffer = TILE_SIZE//2
        max_offset = TILE_SIZE//2
    
        neighbors = self.get_neighbors()
        neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]

        # spawn trees
        if random.random() < 0.8: # spawn only on a percentage of tiles         
            for i in range(spawn_attempts):
                try_pos = vec(
                    self.rect.topleft[0] + random.randrange(0,max_offset), 
                    self.rect.topleft[1] + random.randrange(0,max_offset)
                )
                spawn = True
                for obj in [obj for obj in neighbor_objs if isinstance(obj, Tree)]:
                    if try_pos.distance_to(obj.pos) <= buffer:
                        spawn = False
                        break

                if spawn:
                    self.objects.append(AutumnTree(self.game, *try_pos))
                    break
 