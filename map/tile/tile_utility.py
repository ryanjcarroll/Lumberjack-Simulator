from settings import *
import pygame as pg

texture_positions = {
    "grass":(0,0),
    "sand":(0,1),
    "clay":(0,2),
    "water":(0,3),
    "snow":(0,4)
}

# TILE UTILITY METHODS:
def get_texture_from_neighbors(n):
    texture = {}

    # configurations for all-one-texture
    if len(set(n)) == 1:
        texture['base'] = texture_positions[n[0]]

    # render shorelines against water
    elif len(set(n)) == 2 and "water" in n and any([x in n for x in ["grass","sand","clay"]]):
        shore = [tex for tex in n if tex != "water"][0]
        if shore == "grass":
            startrow = 4
        elif shore == "sand":
            startrow = 10
        elif shore == "clay":
            startrow = 13

        # 14 possible shore/water configurations of the 4 neighboring tiles of the draw_rect
        if n == [shore, shore, shore, 'water']:
            texture['base'] = (startrow+1, 3)
        elif n == [shore, shore, 'water', shore]:
            texture['base'] = (startrow+1, 4)
        elif n == [shore, 'water', 'water', 'water']:
            texture['base'] = (startrow+2, 2)
        elif n == [shore, 'water', shore, shore]:
            texture['base'] = (startrow+2, 3)
        elif n == [shore, shore, 'water', 'water']:
            texture['base'] = (startrow+2, 1)
        elif n == [shore, 'water', shore, 'water']:
            texture['base'] = (startrow+1, 2)
        elif n == [shore, 'water', 'water', shore]:
            texture['base'] = (startrow, 4)
        elif n == ['water', 'water', 'water', shore]:
            texture['base'] = (startrow, 0)
        elif n == ['water', 'water', shore, 'water']:
            texture['base'] = (startrow, 2)
        elif n == ['water', shore, shore, shore]:
            texture['base'] = (startrow+2, 4)
        elif n == ['water', shore, 'water', 'water']:
            texture['base'] = (startrow+2, 0)
        elif n == ['water', 'water', shore, shore]:
            texture['base'] = (startrow, 1)
        elif n == ['water', shore, 'water', shore]:
            texture['base'] = (startrow+1, 0)
        elif n == ['water', shore, shore, 'water']:
            texture['base'] = (startrow, 3)

    elif len(set(n)) > 1:   
        # extract only the base textures
        base_textures = [None if tex in["grass","snow"] else tex for tex in n]

        texture['base_corners'] = []
        for i, corner in enumerate(base_textures):
            if corner != None:
                sheet_pos = texture_positions[corner]
                texture['base_corners'].append(sheet_pos)
            else:
                texture['base_corners'].append(None)

        # apply grass textures in a layer over base and snow tiles
        if "grass" in n:
            n_grass = ["top" if t in ["grass","snow"] else "bottom" for t in n]
            if n_grass == ['top', 'top', 'top', 'top']:
                texture['grass'] = (2, 1)
            elif n_grass == ['top', 'top', 'top', 'bottom']:
                texture['grass'] = (2, 3)
            elif n_grass == ['top', 'top', 'bottom', 'top']:
                texture['grass'] = (2, 4)
            elif n_grass == ['top', 'bottom', 'bottom', 'bottom']:
                texture['grass'] = (3, 2)
            elif n_grass == ['top', 'bottom', 'top', 'top']:
                texture['grass'] = (3, 3)
            elif n_grass == ['top', 'top', 'bottom', 'bottom']:
                texture['grass'] = (3, 1)
            elif n_grass == ['top', 'bottom', 'top', 'bottom']:
                texture['grass'] = (2, 2)
            elif n_grass == ['top', 'bottom', 'bottom', 'top']:
                texture['grass'] = (1, 4)
            elif n_grass == ['bottom', 'bottom', 'bottom', 'top']:
                texture['grass'] = (1, 0)
            elif n_grass == ['bottom', 'bottom', 'top', 'bottom']:
                texture['grass'] = (1, 2)
            elif n_grass == ['bottom', 'top', 'top', 'top']:
                texture['grass'] = (3, 4)
            elif n_grass == ['bottom', 'top', 'bottom', 'bottom']:
                texture['grass'] = (3, 0)
            elif n_grass == ['bottom', 'bottom', 'top', 'top']:
                texture['grass'] = (1, 1)
            elif n_grass == ['bottom', 'top', 'bottom', 'top']:
                texture['grass'] = (2, 0)
            elif n_grass == ['bottom', 'top', 'top', 'bottom']:
                texture['grass'] = (1, 3)

        # apply snow textures in a layer over base and grass tiles
        if "snow" in n:
            n_snow = ["top" if t in ["snow"] else "bottom" for t in n]
            if n_snow == ['top', 'top', 'top', 'top']:
                texture['snow'] = (8, 1)
            elif n_snow == ['top', 'top', 'top', 'bottom']:
                texture['snow'] = (8, 3)
            elif n_snow == ['top', 'top', 'bottom', 'top']:
                texture['snow'] = (8, 4)
            elif n_snow == ['top', 'bottom', 'bottom', 'bottom']:
                texture['snow'] = (9, 2)
            elif n_snow == ['top', 'bottom', 'top', 'top']:
                texture['snow'] = (9, 3)
            elif n_snow == ['top', 'top', 'bottom', 'bottom']:
                texture['snow'] = (9, 1)
            elif n_snow == ['top', 'bottom', 'top', 'bottom']:
                texture['snow'] = (8, 2)
            elif n_snow == ['top', 'bottom', 'bottom', 'top']:
                texture['snow'] = (7, 4)
            elif n_snow == ['bottom', 'bottom', 'bottom', 'top']:
                texture['snow'] = (7, 0)
            elif n_snow == ['bottom', 'bottom', 'top', 'bottom']:
                texture['snow'] = (7, 2)
            elif n_snow == ['bottom', 'top', 'top', 'top']:
                texture['snow'] = (9, 4)
            elif n_snow == ['bottom', 'top', 'bottom', 'bottom']:
                texture['snow'] = (9, 0)
            elif n_snow == ['bottom', 'bottom', 'top', 'top']:
                texture['snow'] = (7, 1)
            elif n_snow == ['bottom', 'top', 'bottom', 'top']:
                texture['snow'] = (8, 0)
            elif n_snow == ['bottom', 'top', 'top', 'bottom']:
                texture['snow'] = (7, 3)

    return texture

def get_image_from_texture(texture, sprite_manager, spritesheet:str):
    image = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)

    # set the base image
    if "base" in texture:

        # set single-texture and water/grass base images
        img = sprite_manager.load_from_tilesheet(
            path=spritesheet,
            row_index=texture['base'][0],
            col_index=texture['base'][1],
            tile_size=16,
            resize=(TILE_SIZE, TILE_SIZE)
        )
        image.blit(img, (0,0))

    # set multi-texture base images
    elif "base_corners" in texture:
        image = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        blit_positions = { # where to blit each corner
            0:(0,0),
            1:(TILE_SIZE//2, 0),
            2:(0, TILE_SIZE//2),
            3:(TILE_SIZE//2, TILE_SIZE//2)
        }
        for i, tex in enumerate(texture['base_corners']):
            if tex is not None:
                image.blit(
                    sprite_manager.load_from_tilesheet(
                        spritesheet,
                        row_index=tex[0],
                        col_index=tex[1],
                        tile_size=16,
                        resize=(TILE_SIZE//2, TILE_SIZE//2)
                    ),
                    blit_positions[i]
                )

    # blit the grass layer, if applicable
    if "grass" in texture:
        image.blit(
            sprite_manager.load_from_tilesheet(
                spritesheet,
                row_index=texture['grass'][0],
                col_index=texture['grass'][1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
            ),
            (0,0)
        )
    # blit the snow layer, if applicable
    if "snow" in texture:
        image.blit(
            sprite_manager.load_from_tilesheet(
                spritesheet,
                row_index=texture['snow'][0],
                col_index=texture['snow'][1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
            ),
            (0,0)
        )
    return image
