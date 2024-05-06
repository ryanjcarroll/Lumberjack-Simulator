from settings import *
from map.tile import *
from objects.tree import Tree
from objects.sprite_object import SpriteObject
from objects.inventory import Camp
from pygame import Vector2 as vec
import pygame as pg
import random
import opensimplex

opensimplex.seed(random.randint(0,100000))

class Chunk:
    def __init__(self, game, x, y):
        self.game = game
        
        self.tiles = []
        self.rect = Rect(x, y, x+CHUNK_SIZE*TILE_SIZE, y+CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

        self.render_tiles()

    def render_tiles(self):
        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                x = self.rect.topleft[0] + col*TILE_SIZE
                y = self.rect.topleft[1] + row*TILE_SIZE
                biome_noise = opensimplex.noise2(x*BIOME_NOISE_FACTOR, y*BIOME_NOISE_FACTOR)
                if biome_noise > 0.33:
                    tile_type = ForestTile
                elif biome_noise < -0.33:
                    tile_type = IceForestTile
                else:
                    tile_type = ForestTile
                tile = tile_type(
                    game = self.game,
                    chunk=self,
                    row = row,
                    col = col
                )
                tile.load_objects()
                self.tiles.append(tile)

    def save(self):
        pass

    def to_json(self):
        return {
            "type":type(self),
            "id":self.id,
            "position":[self.rect.topleft[0],self.rect.topleft[1]],
            "tiles":[
                tile.to_json() for tile in self.tiles
            ]
        }
    
class SpawnChunk(Chunk):
    def __init__(self, game,x, y):
        super().__init__(game, x, y)

        for tile in self.tiles:
            # spawn the camp
            if CHUNK_SIZE//2 == tile.row and CHUNK_SIZE//2 + 1== tile.col:
                self.game.camp = Camp(self.game, *tile.rect.topleft)
                tile.objects.append(self.game.camp)

    def render_tiles(self):
        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                if CHUNK_SIZE//2 - 1 == row and CHUNK_SIZE//2 - 1 == col:
                    terrain_type = "stone_topleft" 
                elif CHUNK_SIZE//2 - 1 == row and CHUNK_SIZE//2 == col:
                    terrain_type = "stone_top" 
                elif CHUNK_SIZE//2 - 1 == row and CHUNK_SIZE//2 + 1== col:
                    terrain_type = "stone_topright" 
                elif CHUNK_SIZE//2 == row and CHUNK_SIZE//2 - 1 == col:
                    terrain_type = "stone_left" 
                elif CHUNK_SIZE//2 == row and CHUNK_SIZE//2 == col:
                    terrain_type = "stone_center" 
                elif CHUNK_SIZE//2 == row and CHUNK_SIZE//2 + 1== col:
                    terrain_type = "stone_right" 
                elif CHUNK_SIZE//2 + 1 == row and CHUNK_SIZE//2 - 1 == col:
                    terrain_type = "stone_bottomleft" 
                elif CHUNK_SIZE//2 + 1 == row and CHUNK_SIZE//2 == col:
                    terrain_type = "stone_bottom" 
                elif CHUNK_SIZE//2 + 1 == row and CHUNK_SIZE//2 + 1== col:
                    terrain_type = "stone_bottomright" 
                else:
                    terrain_type = "grass"
                tile = ForestTile(
                    game = self.game,
                    chunk=self,
                    row = row,
                    col = col,
                    has_decor=True if terrain_type == "grass" else False
                )
                tile.load_objects()

                self.tiles.append(tile)