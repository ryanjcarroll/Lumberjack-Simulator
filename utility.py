import pygame as pg
from settings import *

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
    x = col_index * tile_size
    y = row_index * tile_size

    tile_rect = pg.Rect(x, y, tile_size, tile_size)
    return spritesheet.subsurface(tile_rect)

def point_inside_triangle(point, triangle_points):
    """
    Check if a point is inside a triangle defined by three points.
    """
    x, y = point
    x1, y1 = triangle_points[0]
    x2, y2 = triangle_points[1]
    x3, y3 = triangle_points[2]

    # Calculate barycentric coordinates
    denominator = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    beta = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / denominator
    gamma = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / denominator
    alpha = 1 - beta - gamma

    # Check if point is inside the triangle
    return 0 <= alpha <= 1 and 0 <= beta <= 1 and 0 <= gamma <= 1

def combine_images(images):
    # Get the dimensions of the first image
    width, height = images[0].get_width(), images[0].get_height()
    
    # Create a blank surface with the same dimensions
    combined_surface = pg.Surface((width, height), pg.SRCALPHA)
    
    # Overlay each image on top of the previous ones
    for image in images:
        combined_surface.blit(image, (0, 0))
    
    return combined_surface