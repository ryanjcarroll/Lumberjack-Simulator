from settings import *
import threading
from map.chunk import Chunk, SpawnChunk
from pygame import Vector2 as vec
from glob import glob
import json

class Map:
    def __init__(self, game):
        self.game = game
        
        self.chunks = {} # store chunks in a dictionary
        self.currently_loading = set() # track chunk_ids that are currently loading so we don't try to double-load them
        self.lock = threading.Lock() # to prevent two threads (or thread and main) from trying to modify self.chunks at the same time

    def new(self):
        # generate the starting chunk with the top left corner at (0,0)
        self.load_chunk(0,0, type=SpawnChunk)

    def update(self):
        """
        Check if new chunks need to be generated based on the player's position.
        """
        # Generate new chunks as soon as they come into view
        visible_chunks = self.get_visible_chunks()
        for chunk_id in visible_chunks:
            with self.lock:
                chunk_x, chunk_y = tuple(int(val) for val in chunk_id.split(","))
                # load (from save) or build (from new) the chunk if not currently in memory
                if chunk_id not in self.chunks and chunk_id not in self.currently_loading:
                    generate_thread = threading.Thread(target=self.load_chunk, args=(chunk_x, chunk_y))
                    generate_thread.start()

        chunks_to_unload = [chunk_id for chunk_id in self.chunks if chunk_id not in visible_chunks]
        for chunk_to_unload in chunks_to_unload:
            self.unload_chunk(chunk_to_unload)

    def unload_chunk(self, chunk_id):
        self.chunks[chunk_id].save()
        self.chunks[chunk_id].unload()
        del self.chunks[chunk_id]

    def load_chunk(self, x, y, type=Chunk):
        self.currently_loading.add(f"{x},{y}")
        chunk = type(self.game, x, y)
        with self.lock: # prevent race condition
            self.chunks[chunk.id] = chunk
            self.currently_loading.remove(chunk.id)

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

    def get_visible_chunks(self):
        """
        Get a list of chunks that are on screen, given the player position.

        buffer given in pixels
        """
        # visible chunks are defined as anything within 2 tiles of the viewport
        # to test chunk-loading, you can set this value to a negative number

        # calculate the coords for opposite corners of the viewport (with an additional buffer area)
        screen_topleft = self.get_chunk_coords(self.game.player.pos.x - WINDOW_WIDTH//2, self.game.player.pos.y - WINDOW_HEIGHT//2)
        screen_botright = self.get_chunk_coords(self.game.player.pos.x + WINDOW_WIDTH//2, self.game.player.pos.y + WINDOW_HEIGHT//2)

        # calculate the chunk coords for those same corners
        topleft_chunk = vec(self.get_chunk_coords(*screen_topleft))
        botright_chunk = vec(self.get_chunk_coords(*screen_botright))

        # calculate the diagonal difference between the top left and bottom right corners as a vector
        difference = botright_chunk - topleft_chunk
        chunks_spanned = difference // (CHUNK_SIZE*TILE_SIZE)
        
        # build a list of chunks in the range of values between TL and BR corner
        chunks_spanned += vec(1,1) # iterate once more to include the original chunk
        chunks = []
        for x in range(int(chunks_spanned[0])):
            for y in range(int(chunks_spanned[1])):
                chunks.append(
                    topleft_chunk + vec(x*CHUNK_SIZE*TILE_SIZE, y*CHUNK_SIZE*TILE_SIZE)
                )

        return set([f"{int(v.x)},{int(v.y)}" for v in chunks])