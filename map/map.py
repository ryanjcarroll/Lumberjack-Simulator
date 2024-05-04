from settings import *
import threading
from map.chunk import Chunk, SpawnChunk

class Map:
    def __init__(self, game):
        # store chunks in a dictionary
        self.chunks = {}
        self.currently_generating = set()
        self.game = game
        self.lock = threading.Lock() # to prevent two threads (or thread and main) from trying to modify self.chunks at the same time

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
        # if not self.update_thread_running:
        chunk_x = int((x // (CHUNK_SIZE * TILE_SIZE)) * (CHUNK_SIZE * TILE_SIZE))
        chunk_y = int((y // (CHUNK_SIZE * TILE_SIZE)) * (CHUNK_SIZE * TILE_SIZE))
        return f"{chunk_x},{chunk_y}"

    def get_visible_chunks(self, player):
        """
        Get a list of chunks that are on screen, given the player position.
        """
        # visible chunks are defined as anything within 2 tiles of the viewport
        # to test chunk-loading, you can set this value to a negative number
        buffer = TILE_SIZE*2
        # calculate the chunk that each corner of the viewport is in. 
        # as long as chunks are larger than the window, this gives all visible chunks
        corners = [
            (player.pos.x - WINDOW_WIDTH//2 - buffer, player.pos.y - WINDOW_HEIGHT//2 - buffer),
            (player.pos.x - WINDOW_WIDTH//2 - buffer, player.pos.y + WINDOW_HEIGHT//2 + buffer),
            (player.pos.x + WINDOW_WIDTH//2 + buffer, player.pos.y - WINDOW_HEIGHT//2 - buffer),
            (player.pos.x + WINDOW_WIDTH//2 + buffer, player.pos.y + WINDOW_HEIGHT//2 + buffer)
        ]
        return set([self.get_chunk_id(*corner) for corner in corners])
