from settings import *
from map.tile import Tile
from objects.tree import Tree
from objects.sprite_object import SpriteObject
from objects.inventory import Camp
import random

class Chunk:
    def __init__(self, game, x, y):
        self.game = game
        
        self.tiles = []
        self.rect = Rect(x, y, x+CHUNK_SIZE*TILE_SIZE, y+CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                self.tiles.append(Tile(
                    game = self.game,
                    x = self.rect.topleft[0] + col*TILE_SIZE,
                    y = self.rect.topleft[1] + row*TILE_SIZE,
                    row = row,
                    col = col
                ))

        self.render_objects()

    def render_objects(self):
        """
        Render objects on Tiles within the chunk.
        """
        # TODO update this method to change how chunks are laid out, what is on each tile, etc
        for tile in self.tiles:
            if random.random() < 0.9:
               tile.objects.append(Tree(self.game, *tile.rect.topleft))

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
        self.game = game
        
        self.tiles = []
        self.rect = Rect(x, y, x+CHUNK_SIZE*TILE_SIZE, y+CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

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
                    x = self.rect.topleft[0] + col*TILE_SIZE,
                    y = self.rect.topleft[1] + row*TILE_SIZE,
                    row = row,
                    col = col,
                    terrain_type=terrain_type,
                    has_decor=True if terrain_type == "grass" else False
                )

                self.tiles.append(tile)

        self.render_objects()

    def render_objects(self):
        for tile in self.tiles:
            # spawn trees everywhere except the 3x3 square around the spawn location
            if abs(CHUNK_SIZE//2-tile.row) > 1 or abs(CHUNK_SIZE//2-tile.col) > 1:
                if random.random() < 0.7:
                    tile.objects.append(Tree(self.game, *tile.rect.topleft))
            # spawn the camp
            if CHUNK_SIZE//2 == tile.row and CHUNK_SIZE//2 + 1== tile.col:
                self.game.camp = Camp(self.game, *tile.rect.topleft)
                tile.objects.append(self.game.camp)