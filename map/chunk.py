from settings import *
from map.tile import Tile
from objects.tree import Tree
from objects.decor import Decor

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
        super().__init__(game, x, y)

    def render_objects(self):
        for tile in self.tiles:
            if abs(CHUNK_SIZE//2-tile.row) > 1 or abs(CHUNK_SIZE//2-tile.col) > 1:
                tile.objects.append(Tree(self.game, *tile.rect.topleft))
            if tile.row == CHUNK_SIZE//2 and tile.col == CHUNK_SIZE//2:
                tile.objects.append(Decor(self.game, *tile.rect.topleft, "assets/flag.png"))