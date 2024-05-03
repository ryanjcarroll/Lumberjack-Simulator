import pygame as pg
import math
import datetime

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

def get_frames(spritesheet, row_index, num_frames, tile_size):
    # Extract frames from spritesheet
    frames = [
        extract_image_from_spritesheet(spritesheet, row_index, i, tile_size)
        for i in range(num_frames)
    ]
    return frames

# def calculate_day_night_color_cycle(time_of_day:datetime.datetime) -> tuple:
#     """
#     Calculate the RGB filter for a day/night cycle based on the time of day.

#     Args:
#     - time_of_day: Float value representing the time of day (0.0 to 1.0).
#                    0.0 corresponds to midnight, 0.5 corresponds to noon,
#                    and 1.0 corresponds to midnight again.

#     Returns:
#     - RGB filter tuple (r, g, b) representing the color filter to apply.
#     """

#     # convert into a value between 0 and 1, where 0 is midnight and 1 is noon
#     minutes_from_midnight = (time_of_day.hour * 60) + time_of_day.minute
#     minutes_to_midnight = 24*60 - minutes_from_midnight
#     bright_ratio = min(minutes_from_midnight, minutes_to_midnight) / (24*60)

#     # results in a smooth curve from 0.5 to 1 and back, 
#     # instead of sharp curves bottoming out at 0 brightness
#     # brightness = 0.5 * math.sin(math.pi * bright_ratio) + 0.5
#     brightness = (-2*((bright_ratio - 0.5)**2)) + 1
#     print(time_of_day.time(), round(bright_ratio,1), round(brightness,1))

#     # peak daytime: (255,200,100)
#     # peak nighttime: (50,100,255)
#     r = ((255 - 50) * brightness) + 50
#     g = ((255 - 100) * brightness) + 100
#     b = ((255 - 255) * brightness) + 255

#     return (r, g, b)