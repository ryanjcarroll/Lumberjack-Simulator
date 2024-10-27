from settings import *
from objects.sprites import SpriteObject
from map.tile.tile_types import *
import random

class Item(SpriteObject):
    def __init__(self, game, x, y, tile):

        super().__init__(
            game, 
            x, 
            y, 
            tile,
            layer=SPRITE_LAYER, 
            image=None,
        )
        self.game.can_collect_list.add(self)
        self.collision_rect = self.rect

class SkillPoint(Item):
    def __init__(self, game, x, y, tile):

        super().__init__(game, x, y, tile)

    def load_image(self):
        if self.tile.biome == "Swamp":
            row, col = (8,8)
        elif self.tile.biome == "Desert":
            row, col = (8,7)
        elif self.tile.biome == "Forest":
            row, col = random.choice([(8,1),(8,2),(8,3)])
        elif self.tile.biome == "Rainforest":
            row, col = random.choice([(8,4),(8,5)])
        elif self.tile.biome == "Grassland":
            row, col = (8,0)
        elif self.tile.biome == "Tundra":
            row, col = (8,6)
        elif self.tile.biome == "Mountain":
            row, col = (8,9)
        else:
            print(self.tile.biome)
        
        return self.game.sprites.load_from_tilesheet(
                path="assets/trees/global.png",
                row_index=row,
                col_index=col,
                tile_size=16,
                resize=(24,24)
            )