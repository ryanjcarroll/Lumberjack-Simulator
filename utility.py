import pygame as pg

def remove_padding_and_scale(sprite_image):
    """
    Given a sprite image, remove any transparent padding and then scale the image back to its original size.
    """
    rect = sprite_image.get_rect()
    mask = pg.mask.from_surface(sprite_image)
    non_transparent_rect = mask.get_bounding_rects()[0]

    # Create a new surface with the size of the bounding rectangle
    new_surface = pg.Surface((non_transparent_rect.width, non_transparent_rect.height), pg.SRCALPHA)

    # Blit the original sprite onto the new surface at the appropriate position
    new_surface.blit(sprite_image, (0, 0), area=non_transparent_rect)

    # Scale up the new surface to the original size
    scaled_image = pg.transform.scale(new_surface, (rect.width, rect.height))

    return scaled_image

def extract_image_from_spritesheet(spritesheet, row_index, col_index, tile_size):
    # Extract a single image from spritesheet
    col_index *= tile_size
    row_index *= tile_size
    tile_rect = pg.Rect(col_index, row_index, tile_size, tile_size)
    return spritesheet.subsurface(tile_rect)