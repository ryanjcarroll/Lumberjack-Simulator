from settings import *

class Backpack:
    def __init__(self, wood=0):
        self.wood = 0

        self.row_capacity = BACKPACK_ROW_CAPACITY
        self.num_rows = BACKPACK_NUM_ROWS

    def add_wood(self, n=1):
        self.wood += n
        self.wood = min(self.wood, self.row_capacity*self.num_rows)

    def unpack(self, camp):
        camp.add_wood(n=self.wood)
        self.wood = 0