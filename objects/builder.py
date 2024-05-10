import pygame as pg
from settings import *
import random
from objects.building import Building
from pygame import Vector2 as vec
from objects.player import Character

"""
When we propose a new plot:

First, get the max bounds of existing build_rects.
Then, start from the bottom left tile of the proposed build_rect.

For each building, both existing and the proposed new one:

Iteratively search hor/vert adjacent tiles - don't search anything that is included on any build_rect. (Don't search anything if it collides with an object that is in collision but not in hittable? Depends on behavior we want with characters)

If we run out of tiles to search, we can immediately veto the proposed plot.

If we reach any coordinate outside the max bounds of existing build_rects, we know there is a path back to that proposed plot. Store all the searched tiles.

If we reach any tile from a previous search, we know there is a good path.
"""

class Builder:
    def __init__(self, game):
        self.game = game

        # the number of logs the player needs to bring for the next building
        self.current_goal = 20

        # the building under construction, if any
        self.building_in_progress = None

        self.original_building = None

    def build(self):
        if self.building_in_progress:
            self.building_in_progress.build()
            self.building_in_progress = None
        else:
            self.building_in_progress = self.plan_building()
            self.game.buddy.move(
                self.building_in_progress.build_rect.bottomleft[0] + TILE_SIZE//2,
                self.building_in_progress.build_rect.bottomleft[1] - TILE_SIZE//2
            )

    def plan_building(self):
        building_size = random.choice([
            (2,2),
            (3,2),
            # (1,2),
            (4,3)
        ])  # TODO update the size choice algorithm

        # pick two non-cancelling directions to travel while trying to spawn a new building
        directions_to_try = [random.choice(["north","south"]), random.choice(["east", "west"])]
        try_build_rect = pg.Rect(
                0,
                0,
                (building_size[0]) * TILE_SIZE,
                (2+building_size[1]) * TILE_SIZE
            )

        if len(self.game.buildings_list):
            # propose an area for the building to go
            start_point = self.original_building
            try_build_rect.topleft = start_point.build_rect.topleft
        else:
            start_point = (TILE_SIZE*CHUNK_SIZE//2, TILE_SIZE*CHUNK_SIZE//2)
            try_build_rect.topleft = start_point
        
        # if the proposed area would collide with an existing build_rect or the player, move it and try again
        while (
            any([try_build_rect.colliderect(existing_bld.build_rect) for existing_bld in self.game.buildings_list]) 
            or any([try_build_rect.colliderect(character.rect) for character in self.game.character_list])
        ):
            direction = random.choice(directions_to_try)
            if direction == "north":
                try_build_rect.topleft = (try_build_rect.topleft[0], try_build_rect.topleft[1] - TILE_SIZE)
            elif direction == "south":
                try_build_rect.topleft = (try_build_rect.topleft[0], try_build_rect.topleft[1] + TILE_SIZE)
            elif direction == "east":
                try_build_rect.topleft = (try_build_rect.topleft[0] + TILE_SIZE, try_build_rect.topleft[1])
            elif direction == "west":
                try_build_rect.topleft = (try_build_rect.topleft[0] - TILE_SIZE, try_build_rect.topleft[1])

        # check that there is a path to the bottom left tile of the build rect
        # print(self.check_path_to_building(*try_build_rect.bottomleft))

        # once we find a good area to spawn a new building, spawn it
        bld = Building(
            game=self.game,
            build_x=try_build_rect.topleft[0],
            build_y=try_build_rect.topleft[1],
            size=building_size
        )
        
        # remove any collidable objects in the building footprint of the new building
        for obj in self.game.can_collide_list:
            if pg.Rect.colliderect(obj.collision_rect, bld.build_rect) and not isinstance(obj, Building) and not isinstance(obj, Character):
                obj.kill()

        # render the building as a child of the tile at its bottom left corner
        chunk = self.game.map.chunks[self.game.map.get_chunk_id(try_build_rect[0], try_build_rect[1])]
        for tile in chunk.tiles:
            if tile.rect.topleft[0] == try_build_rect.topleft[0] and tile.rect.topleft[1] == try_build_rect.topleft[1]:
                tile.objects.append(bld)

        if not self.original_building:
            self.original_building = bld

        return bld

    # def check_building_is_accessible(self, building, visited_tiles):

    #     starting_chunk = self.game.map.chunks[self.game.map.get_chunk_id(*building.build_rect.bottomleft)]
    #     starting_tile = starting_chunk.get_tile_at(building.build_rect.bottomleft)

    #     stack = [starting_tile]

    #     while stack:
    #         current_tile = stack.pop()
    #         visited_tiles.add(current_tile)

    #         # Explore neighboring tiles
    #         for direction in ["east", "west", "north", "south"]:
    #             neighbor = current_tile.get_neighbor(direction)
    #             if neighbor and neighbor not in visited_tiles:
    #                 stack.append(neighbor)

    # def check_buildings_have_paths(self):
    #     # get the furthest bounds where buildings currently exist
    #     # if we can find a valid path to someplace beyond these bounds, we know there is a path to the building.
    #     min_building_x = CHUNK_SIZE//2
    #     max_building_x = CHUNK_SIZE//2
    #     min_building_y = CHUNK_SIZE//2
    #     max_building_y = CHUNK_SIZE//2
    #     for existing in self.game.buildings_list:
    #         if existing.build_rect[0] > max_building_x:
    #             max_building_x = existing.build_rect[0]
    #         if existing.build_rect[0] < min_building_x:
    #             min_building_x = existing.build_rect[0]
    #         if existing.build_rect[1] > max_building_y:
    #             max_building_y = existing.build_rect[1]
    #         if existing.build_rect[1] < min_building_y:
    #             min_building_y = existing.build_rect[1]

    #     # # Identify the starting tile
    #     # starting_chunk = self.game.map.chunks[self.game.map.get_chunk_id(x, y)]
    #     # starting_tile = starting_chunk.get_tile_at(x, y)

    #     # # Perform DFS to find a path to a location outside the bounds of existing buildings
    #     # stack = [starting_tile]
    #     # visited = set()

    #     # while stack:
    #     #     current_tile = stack.pop()
    #     #     if (current_tile.x < min_building_x or current_tile.x > max_building_x or
    #     #             current_tile.y < min_building_y or current_tile.y > max_building_y):
    #     #         return True  # Found a path to a location outside the bounds of existing buildings

    #     #     visited.add(current_tile)

    #     #     # Explore neighboring tiles
    #     #     for direction in ["east", "west", "north", "south"]:
    #     #         neighbor = current_tile.get_neighbor(direction)
    #     #         if neighbor and neighbor not in visited:
    #     #             stack.append(neighbor)

    #     # # Couldn't find a path to a location outside the bounds of existing buildings
    #     # return False