import pygame as pg
from settings import *

class LightingEngine:
    def __init__(self, game):
        self.game = game
        self.darkness_surface = pg.Surface(size=(WINDOW_WIDTH, WINDOW_HEIGHT), flags=pg.SRCALPHA)
        self.darkness_alpha = 0
        self.daytime_darkness_alpha = 0
        self.nighttime_darkness_alpha = 225

        # in hours, of 24-hour clock
        self.sunrise_start = 7
        self.sunrise_end = 9
        self.sunset_start = 19
        self.sunset_end = 21
        
    def set_time_of_day(self, dt):
        # nighttime hours
        if dt < dt.replace(hour=self.sunrise_start, minute=0) or dt > dt.replace(hour=self.sunset_end, minute=0):
            self.darkness_alpha = self.nighttime_darkness_alpha
        # sunrise hours
        elif dt.replace(hour=self.sunrise_start, minute=0) <= dt <= dt.replace(hour=self.sunrise_end, minute=0):
            sunrise_total_minutes = (dt.replace(hour=self.sunrise_end, minute=0) - dt.replace(hour=self.sunrise_start, minute=0)).total_seconds() // 60
            sunrise_elapsed_minutes =  (dt - dt.replace(hour=self.sunrise_start, minute=0)).total_seconds() // 60
            self.darkness_alpha = int((1-(sunrise_elapsed_minutes / sunrise_total_minutes)) * (self.nighttime_darkness_alpha - self.daytime_darkness_alpha)) + self.daytime_darkness_alpha
        # sunset hours
        elif dt.replace(hour=self.sunset_start, minute=0) <= dt <= dt.replace(hour=self.sunset_end, minute=0):
            sunset_total_minutes = (dt.replace(hour=self.sunset_end, minute=0) - dt.replace(hour=self.sunset_start, minute=0)).total_seconds() // 60
            sunset_elapsed_minutes =  (dt - dt.replace(hour=self.sunset_start, minute=0)).total_seconds() // 60     
            self.darkness_alpha = int((sunset_elapsed_minutes / sunset_total_minutes) * (self.nighttime_darkness_alpha - self.daytime_darkness_alpha)) + self.daytime_darkness_alpha
        # daytime hours
        else:
            self.darkness_alpha = self.daytime_darkness_alpha

    def update(self, camera):
        if self.darkness_alpha > 0:
            self.darkness_surface.fill((*BLACK, self.darkness_alpha))

            # player lighting effect
            player_light_surface = self.create_light_surface(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
                min_radius=TILE_SIZE,
                max_radius=3 * TILE_SIZE,
                min_alpha=0,
                max_alpha=self.darkness_alpha,
                layers=100
            )
            self.darkness_surface.blit(player_light_surface, (0, 0), special_flags=pg.BLEND_RGBA_MIN)

            # draw light circles for other light sources
            for source in self.game.light_list:
                source_center = camera.apply_point((source.rect.centerx, source.rect.centery))
                light_surface = self.create_light_surface(
                    center=source_center,
                    min_radius=TILE_SIZE * source.light_level // 2,
                    max_radius=TILE_SIZE * source.light_level,
                    min_alpha=0,
                    max_alpha=self.darkness_alpha,
                    layers=source.light_level * 50
                )
                self.darkness_surface.blit(light_surface, (0, 0), special_flags=pg.BLEND_RGBA_MIN)

    def create_light_surface(self, center, min_radius, max_radius, min_alpha, max_alpha, layers=10):
        # Create a temporary surface to draw the gradient circle
        light_surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), flags=pg.SRCALPHA)
        light_surface.fill((*BLACK, self.darkness_alpha))  # start with full darkness

        # Draw gradient circles from outer to inner to create a smooth gradient
        for i in range(layers, 0, -1):
            radius = min_radius + (max_radius - min_radius) * (i / layers)
            alpha = min_alpha + (max_alpha - min_alpha) * (i / layers)
            color = (*BLACK, int(alpha))
            pg.draw.circle(light_surface, color, center, int(radius))

        return light_surface

    def draw(self, screen):
        if self.darkness_alpha > 0:
            screen.blit(self.darkness_surface, (0,0))