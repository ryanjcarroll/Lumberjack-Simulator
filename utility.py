import pygame as pg
from settings import *
import math
import random

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


# Interpolate values using smoothstep function
def perlin_noise(x,y):
    
    def smoothstep(t):
        return t * t * (3 - 2 * t)

    def interpolate(a, b, t):
        return a + (b - a) * smoothstep(t)
    
    # Generate random gradient vectors
    vectors = [(random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(4)]

    # Compute dot products between gradient vectors and input coordinates
    dots = [(x - math.floor(x), y - math.floor(y), *vector) for vector in vectors]

    # Compute weights
    weights = [dot[0] * dot[2] + dot[1] * dot[3] for dot in dots]

    # Interpolate along x-axis
    x1 = interpolate(weights[0], weights[1], x - math.floor(x))
    x2 = interpolate(weights[2], weights[3], x - math.floor(x))

    # Interpolate along y-axis
    return interpolate(x1, x2, y - math.floor(y))