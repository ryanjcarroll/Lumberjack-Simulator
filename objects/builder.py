import pygame as pg
from settings import *
import random
from objects.building import Building

class Builder:
    def __init__(self, game):
        self.game = game
        self.plan_buildings()


    def add_building(self):
        building_size = random.choice([(2,2),(3,2),(1,2),(4,3)])  # TODO choose this randomly

        # pick two non-cancelling directions to travel while trying to spawn a new building
        directions_to_try = [random.choice(["north","south"]), random.choice(["east", "west"])]
        
        if len(self.game.buildings_list):
            # propose an area for the building to go
            try_build_rect = pg.Rect(
                0,
                0,
                building_size[0] * TILE_SIZE,
                building_size[1] * TILE_SIZE
            )
            start_point = random.choice(list(self.game.buildings_list))
            try_build_rect.bottomleft = start_point.build_rect.bottomleft

            # if the proposed area would collide with an existing build_rect, move it and try again
            while any([try_build_rect.colliderect(bld.build_rect) for bld in self.game.buildings_list]):
                direction = random.choice(directions_to_try)
                if direction == "north":
                    try_build_rect.bottomleft = (try_build_rect.bottomleft[0], try_build_rect.bottomleft[1] - TILE_SIZE)
                elif direction == "south":
                    try_build_rect.bottomleft = (try_build_rect.bottomleft[0], try_build_rect.bottomleft[1] + TILE_SIZE)
                elif direction == "east":
                    try_build_rect.bottomleft = (try_build_rect.bottomleft[0] + TILE_SIZE, try_build_rect.bottomleft[1])
                elif direction == "west":
                    try_build_rect.bottomleft = (try_build_rect.bottomleft[0] - TILE_SIZE, try_build_rect.bottomleft[1])

            # once we find a good area to spawn a new building, spawn it
            chunk = self.game.map.chunks[self.game.map.get_chunk_id(try_build_rect[0], try_build_rect[1])]
            for tile in chunk.tiles:
                if tile.rect.bottomleft[0] == try_build_rect.bottomleft[0] and tile.rect.bottomleft[1] == try_build_rect.bottomleft[1]:
                    tile.objects.append(
                        Building(
                            game=self.game,
                            x=try_build_rect.topleft[0],
                            y=try_build_rect.topleft[1],
                            size=building_size
                        )
                    )
        # if no buildings yet, spawn one
        else:
            for tile in self.game.map.chunks["0,0"].tiles:
                if tile.row == CHUNK_SIZE//2 and tile.col == CHUNK_SIZE//2:
                    tile.objects.append(
                        Building(
                            game=self.game,
                            x=tile.rect.topleft[0],
                            y=tile.rect.topleft[1],
                            size=(2,2)
                        )
                    )
            # try_build_rect.bottomleft = (TILE_SIZE * CHUNK_SIZE//2, TILE_SIZE * CHUNK_SIZE//2)

    def plan_buildings(self):
        for i in range(30):
            self.add_building()
        # building_size = (2,1)  # TODO choose this randomly

        # for tile in self.chunk.tiles:
        #     if tile.row == 10 and tile.col == 10:
        #         tile.objects.append(
        #             Building(
        #                 game=self.game,
        #                 x=tile.rect.bottomleft[0],
        #                 y=tile.rect.bottomleft[1],
        #                 size=(2,1)
        #             )
        #         )