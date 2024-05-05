import pygame as pg
from pygame import Vector2 as vec
from settings import *
from utility import extract_image_from_spritesheet
from map.tile_textures import tile_textures
import random
from glob import glob
from objects.sprite_object import SpriteObject

class Tile:
    def __init__(self, game, chunk, x, y, row, col, terrain_type="grass", has_decor=True):
        self.game = game
        self.chunk = chunk
        
        self.terrain_type = terrain_type
        self.row = row # row within the chunk
        self.col = col # col within the chunk

        # store the y coordinate for layer ordering during rendering
        self.y = y

        # # chunk debugging feature - change texture on chunk-edge tiles
        # if self.row == 0 or self.col == 0 or self.row == CHUNK_SIZE-1 or self.col == CHUNK_SIZE-1:
        #     self.terrain_type = "stone_center"

        self.image = self.load_texture()
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(x,y)     
        self.objects = []

        if has_decor:
            self.load_decor()

    def load_texture(self):
        if self.terrain_type in tile_textures:
            texture = tile_textures[self.terrain_type]
            return pg.transform.scale(
                extract_image_from_spritesheet(
                    spritesheet=texture['source'],
                    row_index=texture['row'],
                    col_index=texture['column'],
                    tile_size=texture['tile_size']
                )
                ,(TILE_SIZE, TILE_SIZE)
            )
        else:
            return pg.transform.scale(pg.image.load("assets/textures/bedrock.png"), (TILE_SIZE, TILE_SIZE))
        
    def load_decor(self):
        # generate between decorative items to randomly place on the tile
        item_type_weights = {
            # "bush"      : 2,
            "butterfly" : 2,
            # "camp":,
            # "decor"     : 1,
            # "fence"     : 1,
            "flower"    : 3,
            "grass"     : 30,
            "patch"     : 20,
            "pebble"    : 5,
            # "signpost"  : 1,
            # "stone"     : 2,
        }
        item_type = random.choices(
            population = list(item_type_weights.keys()),
            weights = list(item_type_weights.values())
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