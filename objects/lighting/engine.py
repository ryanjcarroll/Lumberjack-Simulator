import pygame as pg
from settings import *

class LightingEngine:
    def __init__(self, game):
        self.game = game
        self.darkness_surface = pg.Surface(size=(WINDOW_WIDTH, WINDOW_HEIGHT), flags=pg.SRCALPHA)
        self.base_darkness_alpha = 225

    def update(self, camera):
        # darkness surface
        self.darkness_surface.fill((0, 0, 0, self.base_darkness_alpha))

        # player lighting effect
        player_light_surface = self.create_light_surface(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
            min_radius=TILE_SIZE,
            max_radius=3 * TILE_SIZE,
            min_alpha=0,
            max_alpha=self.base_darkness_alpha,
            layers=100
        )
        
        # blend player lighting
        self.darkness_surface.blit(player_light_surface, (0, 0), special_flags=pg.BLEND_RGBA_MIN)

        # draw light circles for other light sources
        for source in self.game.light_list:
            source_center = camera.apply_point((source.rect.centerx, source.rect.centery))
            light_surface = self.create_light_surface(
                center=source_center,
                min_radius=TILE_SIZE * source.light_level // 2,
                max_radius=TILE_SIZE * source.light_level,
                min_alpha=0,
                max_alpha=self.base_darkness_alpha,
                layers=source.light_level * 50
            )
            
            # blend each light source onto the darkness surface
            self.darkness_surface.blit(light_surface, (0, 0), special_flags=pg.BLEND_RGBA_MIN)

    def create_light_surface(self, center, min_radius, max_radius, min_alpha, max_alpha, layers=10):
        # Create a temporary surface to draw the gradient circle
        light_surface = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), flags=pg.SRCALPHA)
        light_surface.fill((0, 0, 0, self.base_darkness_alpha))  # start with full darkness

        # Draw gradient circles from outer to inner to create a smooth gradient
        for i in range(layers, 0, -1):
            radius = min_radius + (max_radius - min_radius) * (i / layers)
            alpha = min_alpha + (max_alpha - min_alpha) * (i / layers)
            color = (0, 0, 0, int(alpha))
            pg.draw.circle(light_surface, color, center, int(radius))

        return light_surface

    def draw(self, screen):
        screen.blit(self.darkness_surface, (0,0))