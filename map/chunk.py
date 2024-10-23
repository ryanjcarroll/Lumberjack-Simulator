from settings import *
from map.tile import *
from objects.inventory import Camp
import opensimplex
import os
import json
from utility import write_json

class Chunk:
    def __init__(self, game, x, y, load_objects=True):
        self.game = game
        self.load_objects = load_objects

        # store a list of rows, each of which contains a list of Tiles
        self.tiles = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)] 

        self.rect = Rect(x, y, x+CHUNK_SIZE*TILE_SIZE, y+CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

        # Load from Save File
        if os.path.exists(f"data/saves/{self.game.game_id}/chunks/{self.id}.json"):
            with open(f"data/saves/{self.game.game_id}/chunks/{self.id}.json","r") as f:
                chunk_data = json.load(f)
                
                for tiledata in chunk_data['tiles']:
                    tile_type = globals()[tiledata['type']]
                    tile = tile_type(self.game, self, *tiledata["position"], is_explored=tiledata['is_explored'])
                    if self.load_objects:
                        tile.load_objects(objects=tiledata['objects'])
                    self.tiles[tiledata["position"][0]][tiledata["position"][1]] = tile
        # Build New Chunk
        else:
            self.load_tiles()

        if self.id == "0,0":
            self.build_spawn()

    def build_spawn(self):
        # set up Spawn Chunk with Campsite
        if self.id == "0,0":
            camp_tile = self.get_tile(CHUNK_SIZE//2, CHUNK_SIZE//2 + 1)
            self.game.camp = Camp(self.game, *camp_tile.rect.topleft, camp_tile)
            camp_tile.objects.append(self.game.camp)

    def get_tiles(self):
        return [tile for row in self.tiles for tile in row]

    def load_tiles(self):
        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            tile_row = []
            for col in range(CHUNK_SIZE):
                tile = self.get_tile_type(row, col)(
                    game = self.game,
                    chunk=self,
                    row = row,
                    col = col
                )
                if self.load_objects:
                    tile.load_objects()
                self.tiles[row][col] = tile

        for tile in self.get_tiles():
            tile.load_texture()

    def get_tile(self, row, col) -> Tile:
        return self.tiles[row][col]

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
        write_json(f"data/saves/{self.game.game_id}/chunks/{self.id}.json", self.to_json())

    def unload(self):
        for tile in self.get_tiles():
            tile.unload()
        self.tiles = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)] 

    def to_json(self):
        return {
            "type":type(self).__name__,
            "id":self.id,
            "position":[self.rect.topleft[0],self.rect.topleft[1]],
            "tiles":[
                tile.to_json() for tile in self.get_tiles()
            ]
        }
    
class SpawnChunk(Chunk):
    def __init__(self, game,x, y):
        super().__init__(game, x, y)

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

    # def load_tiles(self):
    #     # fill the chunk with Tiles
    #     for row in range(CHUNK_SIZE):
    #         for col in range(CHUNK_SIZE):
    #             if CHUNK_SIZE//2 - 1 == row and CHUNK_SIZE//2 - 1 == col:
    #                 terrain_type = "rock_topleft" 
    #             elif CHUNK_SIZE//2 - 1 == row and CHUNK_SIZE//2 == col:
    #                 terrain_type = "rock_top" 
    #             elif CHUNK_SIZE//2 - 1 == row and CHUNK_SIZE//2 + 1== col:
    #                 terrain_type = "rock_topright" 
    #             elif CHUNK_SIZE//2 == row and CHUNK_SIZE//2 - 1 == col:
    #                 terrain_type = "rock_left" 
    #             elif CHUNK_SIZE//2 == row and CHUNK_SIZE//2 == col:
    #                 terrain_type = "rock_center" 
    #             elif CHUNK_SIZE//2 == row and CHUNK_SIZE//2 + 1== col:
    #                 terrain_type = "rock_right" 
    #             elif CHUNK_SIZE//2 + 1 == row and CHUNK_SIZE//2 - 1 == col:
    #                 terrain_type = "rock_bottomleft" 
    #             elif CHUNK_SIZE//2 + 1 == row and CHUNK_SIZE//2 == col:
    #                 terrain_type = "rock_bottom" 
    #             elif CHUNK_SIZE//2 + 1 == row and CHUNK_SIZE//2 + 1== col:
    #                 terrain_type = "rock_bottomright" 
    #             else:
    #                 terrain_type = "basic"
    #             tile = self.get_tile_type(row, col)(
    #                 game = self.game,
    #                 chunk=self,
    #                 row = row,
    #                 col = col,
    #                 load_decor=True if terrain_type == "basic" else False
    #             )
    #             if terrain_type == "basic":
    #                 tile.load_objects()

    #             self.tiles.append(tile)
    
    #     # self.update_tile_textures()