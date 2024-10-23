import pygame as pg
from settings import *
from map.tile import *

class MapMenu:
    def __init__(self, game):
        self.game = game

        # scale and draw variables
        self.scale_factor = 0.1  # Scale the map to 10% of original size for the mini-map

        # click and drag variables
        self.drag_offset_x, self.drag_offset_y = 0,0
        self.dragging = False
        self.last_mouse_pos = (0,0)

        self.build_elements()

    def build_elements(self):
        # set fonts
        self.title_font = pg.font.Font(None, 36)  # Font size for the title
        self.photo_count_font = pg.font.Font(None, 24)  # Font for photo count display

        # title text
        self.title_surface = self.title_font.render("Map", True, (0, 0, 0))  # Black text
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))  # Centered at the top
  
    def handle_event(self, event):
        # menu exit events
        if event.type == pg.KEYDOWN and event.key == pg.K_m:
            self.game.at_map_menu = False

        # scroll wheel zoom
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scale_factor *= 1.1  # Zoom in
            elif event.button == 5:  # Scroll down
                self.scale_factor /= 1.1  # Zoom out
        # drag start
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.dragging = True
                self.last_mouse_pos = event.pos
        # drag end
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.dragging = False
        # drag and move
        if event.type == pg.MOUSEMOTION:
            if self.dragging:
                # Calculate the movement and update the offsets
                mouse_x, mouse_y = event.pos
                dx = mouse_x - self.last_mouse_pos[0]
                dy = mouse_y - self.last_mouse_pos[1]
                self.drag_offset_x += dx
                self.drag_offset_y += dy
                self.last_mouse_pos = event.pos  # Update last mouse position
    
    def draw_map(self, screen):
        
        # Calculate the player's position in the mini-map
        player_pos_x = self.game.player.pos.x * self.scale_factor
        player_pos_y = self.game.player.pos.y * self.scale_factor

        # Offset based on player position and dragging
        offset_x = (WINDOW_WIDTH // 2) - player_pos_x + self.drag_offset_x
        offset_y = (WINDOW_HEIGHT // 2) - player_pos_y + self.drag_offset_y

        # draw the chunks which are currently loaded in memory
        for chunk_id, chunk in self.game.map.chunks.items():
            for tile in chunk.get_tiles():
                if tile.is_explored:
                    tile_mini = pg.Rect(
                        round((tile.x * self.scale_factor) + offset_x), # round calculations to avoid gridlines
                        round((tile.y * self.scale_factor) + offset_y),
                        round(TILE_SIZE * self.scale_factor) + 1,
                        round(TILE_SIZE * self.scale_factor) + 1
                    )
                    pg.draw.rect(screen, tile.color, tile_mini)

        # draw the chunks which are saved to disk (using data from the MapEcho)
        for chunk_id, chunk in self.game.map_echo.chunks.items():
            for tile in chunk.get_tiles():
                if tile.is_explored:
                    tile_mini = pg.Rect(
                        round((tile.x * self.scale_factor) + offset_x),
                        round((tile.y * self.scale_factor) + offset_y),
                        round(TILE_SIZE * self.scale_factor) + 1,
                        round(TILE_SIZE * self.scale_factor) + 1
                    )
                    pg.draw.rect(screen, tile.color, tile_mini)

        # Draw the player as a red dot
        pg.draw.circle(
            screen, 
            RED, 
            (WINDOW_WIDTH//2 + self.drag_offset_x, WINDOW_HEIGHT//2 + self.drag_offset_y), 
            radius=5
        )

        # Draw the spawn as a blue dot
        pg.draw.circle(
            screen, 
            BLUE, 
            (
                (self.game.camp.rect.center[0] * self.scale_factor) + offset_x, 
                (self.game.camp.rect.center[1] * self.scale_factor) + offset_y
            ),
            radius=5
        )


    def draw(self):
        screen = self.game.screen
        screen.fill(LIGHTER_GREY)  # background

        screen.blit(self.title_surface, self.title_rect)

        self.draw_map(screen)

        pg.display.flip()