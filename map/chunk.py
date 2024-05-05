from settings import *
from map.tile import Tile
from objects.tree import Tree
from objects.sprite_object import SpriteObject
from objects.inventory import Camp
from pygame import Vector2 as vec
import pygame as pg
import random

class Chunk:
    def __init__(self, game, x, y):
        self.game = game
        
        self.tiles = []
        self.rect = Rect(x, y, x+CHUNK_SIZE*TILE_SIZE, y+CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

        self.render_tiles()
        self.render_objects()

    def render_tiles(self):
        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                self.tiles.append(Tile(
                    game = self.game,
                    chunk=self,
                    x = self.rect.topleft[0] + col*TILE_SIZE,
                    y = self.rect.topleft[1] + row*TILE_SIZE,
                    row = row,
                    col = col
                ))

    def render_objects(self, tree_density=0.9):
        """
        Render objects on Tiles within the chunk.
        """
        # spawn trees everywhere except the 3x3 square around the spawn location
        spawn_attempts = 3
        buffer = TILE_SIZE//2
        max_offset = TILE_SIZE//2
    
        for tile in self.tiles:
            if random.random() < 0.7: # spawn only on a percentage of tiles
                if abs(CHUNK_SIZE//2-tile.row) > 1 or abs(CHUNK_SIZE//2-tile.col) > 1: # don't spawn on camp tiles
                
                    neighbors = tile.get_neighbors()
                    neighbor_objs = [obj for n_tile in neighbors for obj in n_tile.objects]
                    for i in range(spawn_attempts):
                        try_pos = vec(
                            tile.rect.topleft[0] + random.randrange(0,max_offset), 
                            tile.rect.topleft[1] + random.randrange(0,max_offset)
                        )
                        spawn = True
                        for obj in [obj for obj in neighbor_objs if type(obj)==Tree]:
                            if try_pos.distance_to(obj.pos) <= buffer:
                                spawn = False
                                break

                        if spawn:
                            tile.objects.append(Tree(self.game, *try_pos))
                            break

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
                tile = Tile(
                    game = self.game,
                    chunk=self,
                    x = self.rect.topleft[0] + col*TILE_SIZE,
                    y = self.rect.topleft[1] + row*TILE_SIZE,
                    row = row,
                    col = col,
                    terrain_type=terrain_type,
                    has_decor=True if terrain_type == "grass" else False
                )

                self.tiles.append(tile)

    def render_objects(self):
        for tile in self.tiles:

            # spawn the camp
            if CHUNK_SIZE//2 == tile.row and CHUNK_SIZE//2 + 1== tile.col:
                self.game.camp = Camp(self.game, *tile.rect.topleft)
                tile.objects.append(self.game.camp)

        super().render_objects(tree_density=0.7)