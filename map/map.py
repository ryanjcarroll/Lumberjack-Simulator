from settings import *
import threading
from map.chunk import Chunk, SpawnChunk

class Map:
    def __init__(self, game):
        # store chunks in a dictionary
        self.chunks = {}
        self.game = game
        self.lock = threading.Lock() # to prevent two threads (or thread and main) from trying to modify self.chunks at the same time

        # generate the starting chunk with the top left corner at (0,0)
        self.generate_chunk(0,0, type=SpawnChunk)

    def update(self):
        """
        Check if new chunks need to be generated based on the player's position.
        """
        # Generate new chunks as soon as they come into view
        for (chunk_x, chunk_y) in self.get_visible_chunks(self.game.player):
            with self.lock:
                if f"{chunk_x},{chunk_y}" not in self.chunks:
                    generate_thread = threading.Thread(target=self.generate_chunk, args=(chunk_x, chunk_y))
                    generate_thread.start()

    def generate_chunk(self, x, y, type=Chunk):
        chunk = type(self.game, x,y)
        with self.lock: # prevent race condition
            self.chunks[chunk.id] = chunk

    def get_chunk_id(self, x, y):
        """
        Given a coordinate position, return the chunk_id that it resides in.
        """
        # if not self.update_thread_running:
        chunk_x = int((x // (CHUNK_SIZE * TILE_SIZE)) * (CHUNK_SIZE * TILE_SIZE))
        chunk_y = int((y // (CHUNK_SIZE * TILE_SIZE)) * (CHUNK_SIZE * TILE_SIZE))
        return chunk_x, chunk_y

    def get_visible_chunks(self, player):
        """
        Get a list of chunks that are on screen, given the player position.
        """
        # calculate the chunk for each corner of the viewport. These are the visible chunks
        buffer = WINDOW_WIDTH // 2
        corners = [
            (player.pos.x - WINDOW_WIDTH//2 - buffer, player.pos.y - WINDOW_HEIGHT//2 - buffer),
            (player.pos.x - WINDOW_WIDTH//2 - buffer, player.pos.y + WINDOW_HEIGHT//2 + buffer),
            (player.pos.x + WINDOW_WIDTH//2 + buffer, player.pos.y - WINDOW_HEIGHT//2 - buffer),
            (player.pos.x + WINDOW_WIDTH//2 + buffer, player.pos.y + WINDOW_HEIGHT//2 + buffer)
        ]
        return set([self.get_chunk_id(*corner) for corner in corners])
