from settings import *
from map.tile import *
from objects.inventory import Camp
import random
import opensimplex
import os
import json

opensimplex.seed(random.randint(0,100000))

class Chunk:
    def __init__(self, game, x, y):
        self.game = game
        
        self.tiles = []
        self.rect = Rect(x, y, x+CHUNK_SIZE*TILE_SIZE, y+CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

        # Load from Save File
        if os.path.exists(f"data/saves/{self.game.game_id}/chunks/{self.id}.json"):
            with open(f"data/saves/{self.game.game_id}/chunks/{self.id}.json","r") as f:
                chunk_data = json.load(f)
                
                for tiledata in chunk_data['tiles']:
                    tile_type = globals()[tiledata['type']]
                    tile = tile_type(self.game, self, *tiledata["position"])
                    tile.load_objects(tiledata['objects'])
                    self.tiles.append(tile)
        # Build New Chunk
        else:
            self.render_tiles()

    def render_tiles(self):
        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                tile = self.get_tile_type(row, col)(
                    game = self.game,
                    chunk=self,
                    row = row,
                    col = col
                )
                tile.load_objects()
                self.tiles.append(tile)

    def get_tile_type(self, row, col) -> type:
        x = self.rect.topleft[0] + col*TILE_SIZE
        y = self.rect.topleft[1] + row*TILE_SIZE
        biome_noise = opensimplex.noise2(x*BIOME_NOISE_FACTOR, y*BIOME_NOISE_FACTOR)

        if (-50*BIOME_NOISE_FACTOR) < biome_noise < (50*BIOME_NOISE_FACTOR):
            tile_type = WaterTile
        elif (-150*BIOME_NOISE_FACTOR) < biome_noise < (150*BIOME_NOISE_FACTOR):
            tile_type = MangroveForestTile
        elif biome_noise > 0.33:
            tile_type = AutumnForestTile
        elif biome_noise < -0.33:
            tile_type = IceForestTile
        else:
            tile_type = ForestTile

        return tile_type

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
                self.game.camp = Camp(self.game, *tile.rect.topleft, tile)
                tile.objects.append(self.game.camp)

    def get_tile_type(self, row, col) -> type:
        x = self.rect.topleft[0] + col*TILE_SIZE
        y = self.rect.topleft[1] + row*TILE_SIZE
        biome_noise = opensimplex.noise2(x*BIOME_NOISE_FACTOR, y*BIOME_NOISE_FACTOR)

        # if -.05 < biome_noise < .05:  # don't spawn water in the spawn chunk
        #     tile_type = WaterTile
        if -0.15 < biome_noise < 0.15:
            tile_type = MangroveForestTile
        elif biome_noise > 0.33:
            tile_type = AutumnForestTile
        elif biome_noise < -0.33:
            tile_type = IceForestTile
        else:
            tile_type = ForestTile

        return tile_type

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
                    terrain_type = "basic"
                tile = self.get_tile_type(row, col)(
                    game = self.game,
                    chunk=self,
                    row = row,
                    col = col,
                    has_decor=True if terrain_type == "basic" else False
                )
                if terrain_type == "basic":
                    tile.load_objects()

                self.tiles.append(tile)