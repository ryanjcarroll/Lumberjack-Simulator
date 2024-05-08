from settings import *
import threading
from map.chunk import Chunk, SpawnChunk
from pygame import Vector2 as vec
import pygame as pg

class Map:
    def __init__(self, game):
        # store chunks in a dictionary
        self.chunks = {}
        self.currently_generating = set()
        self.game = game
        self.lock = threading.Lock() # to prevent two threads (or thread and main) from trying to modify self.chunks at the same time

    def new(self):
        # generate the starting chunk with the top left corner at (0,0)
        self.generate_chunk(0,0, type=SpawnChunk)

    def update(self):
        """
        Check if new chunks need to be generated based on the player's position.
        """
        # Generate new chunks as soon as they come into view
        for chunk_id in self.get_visible_chunks(self.game.player):
            with self.lock:
                chunk_x, chunk_y = tuple(int(val) for val in chunk_id.split(","))
                if chunk_id not in self.chunks and chunk_id not in self.currently_generating:
                    generate_thread = threading.Thread(target=self.generate_chunk, args=(chunk_x, chunk_y))
                    generate_thread.start()

    def generate_chunk(self, x, y, type=Chunk):
        self.currently_generating.add(f"{x},{y}")
        chunk = type(self.game, x,y)
        with self.lock: # prevent race condition
            self.chunks[chunk.id] = chunk
            self.currently_generating.remove(chunk.id)

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
    
    def get_chunk_intersections(self, rect):
        with self.lock:
            return [
                chunk_id for chunk_id, chunk in self.chunks.items()
                if pg.Rect.colliderect(chunk.rect, rect)
            ]

    def get_visible_chunks(self, player):
        """
        Get a list of chunks that are on screen, given the player position.
        """
        # visible chunks are defined as anything within 2 tiles of the viewport
        # to test chunk-loading, you can set this value to a negative number
        buffer = TILE_SIZE*2

        # calculate the coords for opposite corners of the viewport (with an additional buffer area)
        screen_topleft = self.get_chunk_coords(player.pos.x - WINDOW_WIDTH//2 - buffer, player.pos.y - WINDOW_HEIGHT//2 - buffer)
        screen_botright = self.get_chunk_coords(player.pos.x + WINDOW_WIDTH//2 + buffer, player.pos.y + WINDOW_HEIGHT//2 + buffer)

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

        # print(len(chunks), chunks)
        return set([f"{int(v.x)},{int(v.y)}" for v in chunks])
