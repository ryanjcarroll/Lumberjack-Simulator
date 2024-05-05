from settings import *
import pygame as pg

class BackpackInventoryMenu:
    def __init__(self, game):
        self.game = game

        # draw menu
        self.width = BACKPACK_TILE_SIZE * self.game.player.backpack.row_capacity
        self.height = BACKPACK_TILE_SIZE * self.game.player.backpack.num_rows
        self.x = BACKPACK_MENU_PADDING
        self.y = WINDOW_HEIGHT - self.height - BACKPACK_MENU_PADDING  # Top padding of 10 pixels
        
        self.surface = pg.Surface((self.width, self.height))
        self.wood_image = self.game.sprites.load("assets/decor/logs/Log2.png")
        
    def update_capacity(self):
        self.width = BACKPACK_TILE_SIZE * self.game.player.backpack.row_capacity
        self.height = BACKPACK_TILE_SIZE * self.game.player.backpack.num_rows
        self.x = BACKPACK_MENU_PADDING
        self.y = WINDOW_HEIGHT - self.height - BACKPACK_MENU_PADDING  # Top padding of 10 pixels
        
        self.surface = pg.Surface((self.width, self.height))
    
    def draw(self, screen):
        # draw the menu background
        pg.draw.rect(self.surface, (255, 255, 255), (0, 0, self.width, self.height))

        # Draw gridlines for the squares
        square_size = self.width // self.game.player.backpack.row_capacity # Calculate size of each square
        for row in range(self.game.player.backpack.num_rows):
            for col in range(self.game.player.backpack.row_capacity):
                index = col + (row*self.game.player.backpack.row_capacity)
                x = col * square_size
                y = row * square_size
                square_rect = pg.Rect(x, y, square_size, square_size)
                pg.draw.rect(self.surface, (100, 100, 100), square_rect, 1)  # Draw gridline

                # draw log images
                if index < self.game.player.backpack.wood:
                    image_x = x + (square_size - self.wood_image.get_width()) // 2
                    image_y = y + (square_size - self.wood_image.get_height()) // 2
                    self.surface.blit(self.wood_image, (image_x, image_y))
                
        screen.blit(self.surface, (self.x, self.y))

class CampInventoryMenu:
    def __init__(self, game):
        self.game = game

        # draw menu
        self.width = CAMP_MENU_WIDTH
        self.height = CAMP_MENU_HEIGHT
        self.x = CAMP_MENU_PADDING
        self.y = WINDOW_HEIGHT - self.height - CAMP_MENU_PADDING - BACKPACK_MENU_PADDING - (BACKPACK_TILE_SIZE*self.game.player.backpack.num_rows) # Top padding of 10 pixels
        
        self.surface = pg.Surface((self.width, self.height))

        self.font = pg.font.Font(None, 36)
        self.camp_image = self.game.sprites.load("assets/decor/camp/1.png")
        
    def draw(self, screen):
        # draw the menu background
        text_rect = pg.draw.rect(self.surface, (255, 255, 255), (0, 0, self.width, self.height))

        text = self.font.render(f"{self.game.camp.wood}", True, BLACK)
        text_x = text_rect.centerx - text.get_width() // 2  # Center the text horizontally within the rectangle
        text_y = text_rect.centery - text.get_height() // 2  # Center the text vertically within the rectangle
        self.surface.blit(text, (text_x, text_y))

        screen.blit(self.surface, (self.x, self.y))