from settings import *
import threading
from map.chunk import Chunk
from pygame import Vector2 as vec
from opensimplex import OpenSimplex
import random
import pygame as pg

class Map:
    def __init__(self, game):
        self.game = game
        
        self.chunks = {} # store chunks in a dictionary
        self.currently_loading = set() # track chunk_ids that are currently loading so we don't try to double-load them
        self.lock = threading.Lock() # to prevent two threads (or thread and main) from trying to modify self.chunks at the same time

        # noise generators for biomes
        self.alt_noise_gen = OpenSimplex(int(self.game.seed.split("-")[0])) # altitude
        self.rain_noise_gen = OpenSimplex(int(self.game.seed.split("-")[1])) # rainfall
        self.river_noise_gen = OpenSimplex(int(self.game.seed.split("-")[2])) # rivers
        self.alt_scale = 0.0002
        self.rain_scale = 0.0002
        self.river_scale = 0.0005

        self.tile_noise_options = [
            self.generate_tile_noise() for i in range(5)
        ]

    def new(self):
        # generate the starting chunk with the top left corner at (0,0)
        self.load_chunk(0,0)

    def update(self):
        """
        Check if new chunks need to be generated based on the player's position.
        """
        # Generate new chunks when the player is within 4 tiles of them
        chunks_to_load = self.get_visible_chunks(buffer=4*TILE_SIZE)

        for chunk_id in chunks_to_load:
            with self.lock:
                chunk_x, chunk_y = tuple(int(val) for val in chunk_id.split(","))
                # load (from save) or build (from new) the chunk if not currently in memory
                if chunk_id not in self.chunks and chunk_id not in self.currently_loading:
                    generate_thread = threading.Thread(target=self.load_chunk, args=(chunk_x, chunk_y))
                    generate_thread.start()

        # keep old chunks until the player gets 8 tiles away
        chunks_to_keep = self.get_visible_chunks(buffer=TILE_SIZE*8)
        chunks_to_unload = [chunk_id for chunk_id in self.chunks if chunk_id not in chunks_to_keep]
        for chunk_to_unload in chunks_to_unload:
            self.unload_chunk(chunk_to_unload)

    def unload_chunk(self, chunk_id):
        with self.lock:
            self.chunks[chunk_id].save()
    
            # add chunk to the map echo before deletion
            if self.game.map_echo:
                self.game.map_echo.add_chunk(self.chunks[chunk_id])

            self.chunks[chunk_id].unload()
            del self.chunks[chunk_id]

    def load_chunk(self, x, y, type=Chunk):
        self.currently_loading.add(f"{x},{y}")
        chunk = type(self.game, x, y)
        with self.lock: # prevent race condition            
            # remove from the map echo once loaded
            if self.game.map_echo and chunk.id in self.game.map_echo.chunks:
                self.game.map_echo.remove_chunk(chunk.id)

            self.chunks[chunk.id] = chunk
            self.chunks[chunk.id].check_neighboring_edges()
            self.currently_loading.remove(chunk.id)

    def get_noise(self, x, y, type:str):
        if type == "alt":
            return self.alt_noise_gen.noise2(x*self.alt_scale,y*self.alt_scale)
        elif type == "rain":
            return self.rain_noise_gen.noise2(x*self.rain_scale,y*self.rain_scale)
        elif type == "river":
            return self.river_noise_gen.noise2(x*self.river_scale,y*self.river_scale)
        
    def generate_tile_noise(self):
        noise_resolution = 4
        transparency = 0.99

        # Create a noise surface that covers the tile at lower resolution
        noise_surface = pg.Surface((TILE_SIZE // noise_resolution, TILE_SIZE // noise_resolution), pg.SRCALPHA)

        # Fill noise surface with random grayscale noise
        for y in range(noise_surface.get_height()):
            for x in range(noise_surface.get_width()):
                gray_value = random.randint(235, 255)
                noise_surface.set_at((x, y), (gray_value, gray_value, gray_value, int(255 * transparency)))
        
        # Scale the noise surface up to match the size of the tile
        noise_surface = pg.transform.scale(noise_surface, (TILE_SIZE, TILE_SIZE))

        return noise_surface

    def get_chunk_id(self, x, y):
        """
        Given a coordinate position, return the top left corner coordinates.
        """
        chunk_x, chunk_y, = self.get_chunk_coords(x, y)
        return f"{chunk_x},{chunk_y}"
    
    def get_chunk_coords(self, x, y):
        """
        Given a coordinate position, return the top left corner coordinates.
        """
        chunk_x = int((x // (CHUNK_SIZE * TILE_SIZE)) * (CHUNK_SIZE * TILE_SIZE))
        chunk_y = int((y // (CHUNK_SIZE * TILE_SIZE)) * (CHUNK_SIZE * TILE_SIZE))
        return chunk_x, chunk_y

    def get_visible_chunks(self, buffer=0):
        """
        Get a list of chunks that are on screen, given the player position.
        Also can give chunks that are just outside the visible area to avoid load delays.
        
        buffer: Number of pixels to overestimate with when calculating the visible area.
        """
        # calculate the coords for opposite corners of the viewport (with an additional preload buffer)
        screen_topleft = self.get_chunk_coords(self.game.player.pos.x - WINDOW_WIDTH//2 - buffer, 
                                            self.game.player.pos.y - WINDOW_HEIGHT//2 - buffer)
        screen_botright = self.get_chunk_coords(self.game.player.pos.x + WINDOW_WIDTH//2 + buffer, 
                                                self.game.player.pos.y + WINDOW_HEIGHT//2 + buffer)

        # calculate the chunk coords for those same corners
        topleft_chunk = vec(self.get_chunk_coords(*screen_topleft))
        botright_chunk = vec(self.get_chunk_coords(*screen_botright))

        # calculate the diagonal difference between the top left and bottom right corners as a vector
        difference = botright_chunk - topleft_chunk
        chunks_spanned = difference // (CHUNK_SIZE * TILE_SIZE)

        # build a list of chunks in the range of values between TL and BR corner
        chunks_spanned += vec(1, 1)  # iterate once more to include the original chunk
        chunks = []
        for x in range(int(chunks_spanned[0])):
            for y in range(int(chunks_spanned[1])):
                chunks.append(
                    topleft_chunk + vec(x * CHUNK_SIZE * TILE_SIZE, y * CHUNK_SIZE * TILE_SIZE)
                )

        return set([f"{int(v.x)},{int(v.y)}" for v in chunks])