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

        self.rect = Rect(x, y, CHUNK_SIZE*TILE_SIZE, CHUNK_SIZE*TILE_SIZE)
        self.draw_rect = Rect(x+TILE_SIZE//2, y+TILE_SIZE//2, CHUNK_SIZE*TILE_SIZE, CHUNK_SIZE*TILE_SIZE)
        self.id = f"{self.rect.topleft[0]},{self.rect.topleft[1]}"

        # Load from Save File
        if os.path.exists(f"data/saves/{self.game.game_id}/chunks/{self.id}.json"):
            with open(f"data/saves/{self.game.game_id}/chunks/{self.id}.json","r") as f:
                chunk_data = json.load(f)
                
                for tiledata in chunk_data['tiles']:
                    tile_type = globals()[tiledata['type']]
                    tile = tile_type(
                        self.game, 
                        self, 
                        *tiledata["position"], 
                        is_explored=tiledata['is_explored'],
                        tile_type=tiledata['tile_type'],
                        texture=tiledata['texture']
                    )
                    if self.load_objects and LOAD_OBJECTS:
                        tile.load_objects(objects=tiledata['objects'])
                    self.tiles[tiledata["position"][0]][tiledata["position"][1]] = tile
                
                for tile in self.get_tiles():
                    tile.update_texture()
        # Build New Chunk
        else:
            self.load_tiles()

    def load_tiles(self):
        # fill the chunk with Tiles
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                self.tiles[row][col] = self.get_tile_type(row, col)(
                    game = self.game,
                    chunk= self,
                    row = row,
                    col = col
                )
                if self.load_objects and LOAD_OBJECTS:
                    self.tiles[row][col].load_objects()

        if self.id == "0,0":
            self.build_spawn()

        # load initial tile textures
        # this will be incomplete for tiles on the bottom and right edges
        for tile in self.get_tiles():
            tile.update_texture()

    def check_neighboring_edges(self):
        # check chunk above to see if its edges need to be regenerated
        chunk_above_coords = self.rect.topleft - vec(0,TILE_SIZE*CHUNK_SIZE)
        chunk_above_id = f"{int(chunk_above_coords.x)},{int(chunk_above_coords.y)}"
        if chunk_above_id in self.game.map.chunks:
            chunk_above = self.game.map.chunks[chunk_above_id]
            bottom_row = chunk_above.tiles[-1]
            for tile in bottom_row:
                if not tile.texture:
                    tile.update_texture()

        # check chunk to left to see if its edges need to be regenerated
        chunk_to_left_coords = self.rect.topleft - vec(TILE_SIZE*CHUNK_SIZE,0)
        chunk_to_left_id = f"{int(chunk_to_left_coords.x)},{int(chunk_to_left_coords.y)}"
        if chunk_to_left_id in self.game.map.chunks:
            chunk_to_left = self.game.map.chunks[chunk_to_left_id]
            for tile_row in chunk_to_left.tiles:
                right_tile = tile_row[-1]
                if not right_tile.texture:
                    right_tile.update_texture()

        # check chunk to topleft to see if its bottom right corner needs to be regenerated
        chunk_to_topleft_coords = self.rect.topleft - vec(TILE_SIZE*CHUNK_SIZE,TILE_SIZE*CHUNK_SIZE)
        chunk_to_topleft_id = f"{int(chunk_to_topleft_coords.x)},{int(chunk_to_topleft_coords.y)}"
        if chunk_to_topleft_id in self.game.map.chunks:
            chunk_to_topleft = self.game.map.chunks[chunk_to_topleft_id]
            bottom_right_tile = chunk_to_topleft.tiles[-1][-1]
            if not bottom_right_tile.texture:
                bottom_right_tile.update_texture()
    
    def build_spawn(self):
        # set up Spawn Chunk with Campsite
        if self.id == "0,0":
            camp_tile = self.get_tile(CHUNK_SIZE//2, CHUNK_SIZE//2 + 1)
            self.game.camp = Camp(self.game, *camp_tile.rect.topleft, camp_tile)
            camp_tile.objects.append(self.game.camp)
     
            for row in range(CHUNK_SIZE//2 - 1, CHUNK_SIZE//2 + 2):
                for col in range(CHUNK_SIZE//2 - 1, CHUNK_SIZE//2 + 2):
                    tile = self.get_tile(row, col)
                    tile.set_tile_type("sand")

            # for row in range(CHUNK_SIZE//2 - 4, CHUNK_SIZE//2 - 1):
            #     for col in range(CHUNK_SIZE//2 - 1, CHUNK_SIZE//2 + 2):
            #         tile = self.get_tile(row, col)
            #         tile.set_tile_type("clay")

    def get_tiles(self):
        return [tile for row in self.tiles for tile in row]

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