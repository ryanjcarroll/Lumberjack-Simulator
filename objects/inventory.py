from objects.sprite_object import SpriteObject
from settings import *

class Backpack:
    def __init__(self):
        self.wood = 0

        self.row_capacity = BACKPACK_ROW_CAPACITY
        self.num_rows = BACKPACK_NUM_ROWS

    def add_wood(self, n=1):
        self.wood += n
        self.wood = min(self.wood, self.row_capacity*self.num_rows)

    def unpack(self, camp):
        camp.add_wood(n=self.wood)
        self.wood = 0

class Camp(SpriteObject):
    def __init__(self, game):
        super().__init__(
            game=game,
            x=(CHUNK_SIZE*TILE_SIZE)//2 + TILE_SIZE//2,
            y=(CHUNK_SIZE*TILE_SIZE)//2 - TILE_SIZE//2,
            img_path="assets/decor/camp/1.png",
            img_resize=(72,72),
            collision=True
        )

        self.wood = 0

    def add_wood(self, n=1):
        self.wood += n