from objects.sprites import SpriteObject
from settings import *

class Torch(SpriteObject):
    def __init__(self, game, x, y, tile, light_level=1):
        self.game = game
        self.x = x
        self.y = y
        self.tile = tile
        self.light_level = light_level
        super().__init__(self.game, self.x, self.x, self.tile, layer=DECOR_LAYER)

        self.game.light_list.add(self)

    def load_image(self):
        return self.game.sprites.load(
            "assets/decor/fence/9.png",
            resize=(16,32)
        )
    
    def to_json(self):
        return {
            "type":type(self).__name__,
            "topleft":(self.x, self.y),
            "light_level": 1
        }