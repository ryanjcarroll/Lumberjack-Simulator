import threading
import os
from settings import *
from glob import glob
import json
from map.chunk import Chunk

class MapEcho:
    """
    This class stores limited information on unloaded map chunks and tiles.
    Specifically, this is used to display minimap information for chunks which are no longer in memory,
        because the player is too far away from them for them to remain loaded.
    """
    def __init__(self, game):
        self.game = game

        self.chunks = {}

        self.currently_loading = set() # track chunk_ids that are currently loading so we don't try to double-load them
        self.lock = threading.Lock() # to prevent two threads (or thread and main) from trying to modify self.chunks at the same time

        # check for saved chunks and load any which are not already in the MapEcho
        for filepath in glob(f"data/saves/{self.game.game_id}/chunks/*"):
            chunk_id = os.path.basename(filepath).split(".")[0]
            if chunk_id not in self.chunks \
                    and chunk_id not in self.game.map.chunks \
                    and chunk_id not in self.game.map.currently_loading \
                    and chunk_id not in self.currently_loading:
                self.currently_loading.add(chunk_id)
                generate_thread = threading.Thread(target=self.load_chunk_from_disk, args=(chunk_id,))
                generate_thread.start()

    def add_chunk(self, chunk):
        self.chunks[chunk.id] = ChunkEcho(chunk)

    def remove_chunk(self, chunk_id):
        with self.lock:
            del self.chunks[chunk_id]

    def load_chunk_from_disk(self, chunk_id):
        """
        Load a chunk that was unloaded and saved to disk.
        """
        # read saved chunk data
        filepath = f"data/saves/{self.game.game_id}/chunks/{chunk_id}.json"
        
        if os.path.exists(filepath):
            with self.lock:              
                chunk_x, chunk_y = chunk_id.split(",")
                chunk_x, chunk_y = int(chunk_x), int(chunk_y)
                self.chunks[chunk_id] = ChunkEcho(Chunk(self.game, chunk_x, chunk_y, load_objects=False)) # don't load objects in the echo  
                self.currently_loading.remove(chunk_id)
        
class ChunkEcho:
    def __init__(self, chunk):
        self.tiles = [TileEcho(tile) for tile in chunk.tiles]
        
class TileEcho:
    def __init__(self, tile):
        self.color = tile.color
        self.x = tile.x
        self.y = tile.y
        self.is_explored = tile.is_explored