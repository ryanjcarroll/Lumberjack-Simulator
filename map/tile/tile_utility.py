from settings import *
import pygame as pg

texture_positions = {
    "grass":(0,0),
    "dirt":(0,1),
    "water":(0,2),
    "snow":(0,3),
    "default":(0,4)
}

# TILE UTILITY METHODS:
def get_texture_from_neighbors(n):
    texture = {}

    # configurations for all-one-texture
    if len(set(n)) == 1:
        texture['base'] = texture_positions[n[0]]

    # configurations for mixed textures
    else:
       # if not water, fill with a base dirt texture
        if not "water" in n:
            texture['base'] = texture_positions['dirt']
                    
        # if water, use a water/dirt shoreline as the base texture instead
        else:
            n_water = ["water" if ter == "water" else "other" for ter in n]
            startrow = 1

            if n_water == ["water","water","water","water"]:
                texture['water'] = (0,2)
            if n_water == ["other", "other", "other", 'water']:
                texture['water'] = (startrow+1, 3)
            elif n_water == ["other", "other", 'water', "other"]:
                texture['water'] = (startrow+1, 4)
            elif n_water == ["other", 'water', 'water', 'water']:
                texture['water'] = (startrow+2, 2)
            elif n_water == ["other", 'water', "other", "other"]:
                texture['water'] = (startrow+2, 3)
            elif n_water == ["other", "other", 'water', 'water']:
                texture['water'] = (startrow+2, 1)
            elif n_water == ["other", 'water', "other", 'water']:
                texture['water'] = (startrow+1, 2)
            elif n_water == ["other", 'water', 'water', "other"]:
                texture['water'] = (startrow, 4)
            elif n_water == ['water', 'water', 'water', "other"]:
                texture['water'] = (startrow, 0)
            elif n_water == ['water', 'water', "other", 'water']:
                texture['water'] = (startrow, 2)
            elif n_water == ['water', "other", "other", "other"]:
                texture['water'] = (startrow+2, 4)
            elif n_water == ['water', "other", 'water', 'water']:
                texture['water'] = (startrow+2, 0)
            elif n_water == ['water', 'water', "other", "other"]:
                texture['water'] = (startrow, 1)
            elif n_water == ['water', "other", 'water', "other"]:
                texture['water'] = (startrow+1, 0)
            elif n_water == ['water', "other", "other", 'water']:
                texture['water'] = (startrow, 3)

        if "grass" in n:
            n_grass = ["grass" if ter in ["grass","snow"] else "other" for ter in n]
            startrow = 4

            if n_grass == ['grass', 'grass', 'grass', 'grass']:
                texture['grass'] = (startrow+1, 1)
            elif n_grass == ['grass', 'grass', 'grass', 'other']:
                texture['grass'] = (startrow+1, 3)
            elif n_grass == ['grass', 'grass', 'other', 'grass']:
                texture['grass'] = (startrow+1, 4)
            elif n_grass == ['grass', 'other', 'other', 'other']:
                texture['grass'] = (startrow+2, 2)
            elif n_grass == ['grass', 'other', 'grass', 'grass']:
                texture['grass'] = (startrow+2, 3)
            elif n_grass == ['grass', 'grass', 'other', 'other']:
                texture['grass'] = (startrow+2, 1)
            elif n_grass == ['grass', 'other', 'grass', 'other']:
                texture['grass'] = (startrow+1, 2)
            elif n_grass == ['grass', 'other', 'other', 'grass']:
                texture['grass'] = (startrow, 4)
            elif n_grass == ['other', 'other', 'other', 'grass']:
                texture['grass'] = (startrow, 0)
            elif n_grass == ['other', 'other', 'grass', 'other']:
                texture['grass'] = (startrow, 2)
            elif n_grass == ['other', 'grass', 'grass', 'grass']:
                texture['grass'] = (startrow+2, 4)
            elif n_grass == ['other', 'grass', 'other', 'other']:
                texture['grass'] = (startrow+2, 0)
            elif n_grass == ['other', 'other', 'grass', 'grass']:
                texture['grass'] = (startrow, 1)
            elif n_grass == ['other', 'grass', 'other', 'grass']:
                texture['grass'] = (startrow+1, 0)
            elif n_grass == ['other', 'grass', 'grass', 'other']:
                texture['grass'] = (startrow, 3)

        if "snow" in n:
            n_snow = ["snow" if ter =="snow" else "other" for ter in n]
            startrow = 7

            if n_snow == ['snow', 'snow', 'snow', 'snow']:
                texture['snow'] = (startrow+1, 1)
            elif n_snow == ['snow', 'snow', 'snow', 'other']:
                texture['snow'] = (startrow+1, 3)
            elif n_snow == ['snow', 'snow', 'other', 'snow']:
                texture['snow'] = (startrow+1, 4)
            elif n_snow == ['snow', 'other', 'other', 'other']:
                texture['snow'] = (startrow+2, 2)
            elif n_snow == ['snow', 'other', 'snow', 'snow']:
                texture['snow'] = (startrow+2, 3)
            elif n_snow == ['snow', 'snow', 'other', 'other']:
                texture['snow'] = (startrow+2, 1)
            elif n_snow == ['snow', 'other', 'snow', 'other']:
                texture['snow'] = (startrow+1, 2)
            elif n_snow == ['snow', 'other', 'other', 'snow']:
                texture['snow'] = (startrow, 4)
            elif n_snow == ['other', 'other', 'other', 'snow']:
                texture['snow'] = (startrow, 0)
            elif n_snow == ['other', 'other', 'snow', 'other']:
                texture['snow'] = (startrow, 2)
            elif n_snow == ['other', 'snow', 'snow', 'snow']:
                texture['snow'] = (startrow+2, 4)
            elif n_snow == ['other', 'snow', 'other', 'other']:
                texture['snow'] = (startrow+2, 0)
            elif n_snow == ['other', 'other', 'snow', 'snow']:
                texture['snow'] = (startrow, 1)
            elif n_snow == ['other', 'snow', 'other', 'snow']:
                texture['snow'] = (startrow+1, 0)
            elif n_snow == ['other', 'snow', 'snow', 'other']:
                texture['snow'] = (startrow, 3)

    return texture

corner_positions = { # where to blit each corner
    0:(0,0),
    1:(TILE_SIZE//2, 0),
    2:(0, TILE_SIZE//2),
    3:(TILE_SIZE//2, TILE_SIZE//2)
}

def get_image_from_texture(texture, sprite_manager, spritesheets:str):
    image = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)

    # if all neighbor tiles are in the same biome, we can load directly from their spritesheet.
    if len(set(spritesheets)) == 1:
        
        if "base" in texture:
            # set single-texture and water/grass base images
            image.blit(sprite_manager.load_from_tilesheet(
                path=spritesheets[0],  # TODO may need to do this by corners also
                row_index=texture['base'][0],
                col_index=texture['base'][1],
                tile_size=16,
                resize=(TILE_SIZE, TILE_SIZE)
            )
            ,(0,0)
        )

        # blit the water layer, if applicable
        if "water" in texture:
            image.blit(
                sprite_manager.load_from_tilesheet(
                    spritesheets[0],
                    row_index=texture['water'][0],
                    col_index=texture['water'][1],
                    tile_size=16,
                    resize=(TILE_SIZE, TILE_SIZE)
                ),
                (0,0)
            )
        # blit the grass layer, if applicable
        if "grass" in texture:
            image.blit(
                sprite_manager.load_from_tilesheet(
                    spritesheets[0],
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
                    spritesheets[0],
                    row_index=texture['snow'][0],
                    col_index=texture['snow'][1],
                    tile_size=16,
                    resize=(TILE_SIZE, TILE_SIZE)
                ),
                (0,0)
            )

    # if neighbors are from multiple biomes, build a composite texture from multiple spritesheets
    else:
        if "base" in texture:
            for corner_idx, corner_pos in corner_positions.items():
                # set single-texture and water/grass base images
                image.blit(sprite_manager.load_from_tilesheet(
                        path=spritesheets[corner_idx],  # TODO may need to do this by corners also
                        row_index=2*texture['base'][0] + (1 if corner_idx in [2,3] else 0),
                        col_index=2*texture['base'][1] + (1 if corner_idx in [1,3] else 0),
                        tile_size=8,
                        resize=(TILE_SIZE//2, TILE_SIZE//2)
                    )
                    ,corner_pos
                )

        # blit the water layer, if applicable
        if "water" in texture:
            for corner_idx, corner_pos in corner_positions.items():
                image.blit(
                    sprite_manager.load_from_tilesheet(
                        spritesheets[corner_idx],
                        row_index=2*texture['water'][0] + (1 if corner_idx in [2,3] else 0),
                        col_index=2*texture['water'][1] + (1 if corner_idx in [1,3] else 0),
                        tile_size=8,
                        resize=(TILE_SIZE//2, TILE_SIZE//2)
                    ),
                    corner_pos
                )
        # blit the grass layer, if applicable
        if "grass" in texture:
            for corner_idx, corner_pos in corner_positions.items():
                image.blit(
                    sprite_manager.load_from_tilesheet(
                        spritesheets[corner_idx],
                        row_index=2*texture['grass'][0] + (1 if corner_idx in [2,3] else 0),
                        col_index=2*texture['grass'][1] + (1 if corner_idx in [1,3] else 0),
                        tile_size=8,
                        resize=(TILE_SIZE//2, TILE_SIZE//2)
                    ),
                    corner_pos
                )
        # blit the snow layer, if applicable
        if "snow" in texture:
            for corner_idx, corner_pos in corner_positions.items():
                image.blit(
                    sprite_manager.load_from_tilesheet(
                        spritesheets[corner_idx],
                        row_index=2*texture['snow'][0] + (1 if corner_idx in [2,3] else 0),
                        col_index=2*texture['snow'][1] + (1 if corner_idx in [1,3] else 0),
                        tile_size=8,
                        resize=(TILE_SIZE//2, TILE_SIZE//2)
                    ),
                    corner_pos
                )
            
    return image