import pygame as pg
from settings import *
from glob import glob
from utility import point_inside_triangle, combine_images
import os
import random
import json

"""
This class is relatively complex but boils down to two objects - self.assets and self.buttons.
They have the following structure:

Attribute - the folder name of the asset class, ie "hair"
Category - the spritesheet for the asset, ie "braids"
Style - the column within the spritesheet, ie 'green' (styles don't actually have names)

self.assets = {
    "body":
        0:{
            "name":"char1",
            "styles":{
                0:<pg.image>,
                ...
            }
        },
        ...
}

self.buttons = {
    "body":{
        "row_rect":<pg.Rect>,
        "left_arrow_rect":<pg.Rect>,
        "right_arrow_rect":<pg.Rect>,
        "left_arrow_color":BLACK,
        "right_arrow_color":BLACK,
        "left_arrow_points":[(...),(...),(...)],
        "right_arrow_points":[(...),(...),(...)],
    },
    ...
}

"""

class LoadoutMenu:
    def __init__(self, game):
        self.game = game
        self.attributes = LAYER_ORDER

        # build a dictionary of category options for the player to choose between
        self.assets = {}
        for attribute in self.attributes:
            self.assets[attribute] = {}

            # load the assets within each attribute, category, and style
            for category_id, path in enumerate(glob(f"assets/player/{attribute}/*.png")):
                spritesheet = self.game.sprites.load(path)
                num_variations = spritesheet.get_width() // (SPRITESHEET_TILE_SIZE * SPRITESHEET_NUM_COLUMNS)

                # within each category, there may be any number of variations
                self.assets[attribute][category_id] = {
                    "name":os.path.basename(path).split(".")[0],
                    "styles":{
                            style_id : pg.transform.scale_by(
                                self.game.sprites.load_from_spritesheet(
                                    path=path,
                                    row_index=0,
                                    col_index=style_id * SPRITESHEET_NUM_COLUMNS, # extract method already accounts for tile size
                                    tile_size=SPRITESHEET_TILE_SIZE
                                ),factor = 4
                            )
                        for style_id in range(num_variations)
                    }
                }

            # for everything except the base character model, have a blank default option at the end
            # we'll manually set the list to start here
            if attribute != "body":
                next_index = len(self.assets[attribute])
                self.assets[attribute][next_index] = {
                    "name":"none",
                    "styles":{
                        0:pg.Surface((SPRITESHEET_TILE_SIZE*4, SPRITESHEET_TILE_SIZE*4), pg.SRCALPHA)
                    }
                }
                
        # build the default selections (category, style)
        self.selections = self.get_random_selections()
        

        self.buttons = {}
        self.update_image()
        self.build_elements()

    def get_random_selections(self):
        selections = {}
        for attribute in self.attributes:
            category = random.randint(0, len(self.assets[attribute])-1)
            style = random.randint(0, len(self.assets[attribute][category]['styles'])-1)
            selections[attribute]= (category, style)
        return selections

    def get_loadout(self):
        return {
            attribute:{
                "category":self.assets[attribute][category]['name'],
                "style":style
            }
            for attribute, (category, style) in self.selections.items()
        }

    def build_elements(self):
        # determine position of the character preview model
        self.char_image_rect = self.char_image.get_rect()
        char_image_x = (WINDOW_WIDTH//2) - (self.char_image_rect.width//2)
        char_image_y = 16
        self.char_image_rect.topleft = (char_image_x, char_image_y)

        # define row dimensions
        row_width = WINDOW_WIDTH // 2
        row_height = 50
        row_margin = 20
        row_y = self.char_image_rect.bottom + row_margin  # Adjusted row_y calculation
        h_arrow_size = 24 # side length
        h_arrow_padding = 96 # from edge of window

        for attribute in self.attributes:
            # Build the selector box and the horizontal category selector arrows
            self.buttons[attribute] = {}
            row_rect = pg.Rect((WINDOW_WIDTH - row_width) // 2, row_y, row_width, row_height)  # Adjusted x-coordinate
            left_arrow_rect = pg.Rect(h_arrow_padding, row_y + row_height // 4, row_height // 2, row_height // 2)
            right_arrow_rect = pg.Rect(WINDOW_WIDTH - row_height // 2 - h_arrow_padding, row_y + row_height // 4, row_height // 2, row_height // 2)  # Adjusted x-coordinate
            self.buttons[attribute]["row_rect"] = row_rect 
            self.buttons[attribute]["left_arrow_rect"] = left_arrow_rect
            self.buttons[attribute]["right_arrow_rect"] = right_arrow_rect
            self.buttons[attribute]["left_arrow_color"] = BLACK
            self.buttons[attribute]["right_arrow_color"] = BLACK
            row_y += row_height + row_margin

            left_arrow_points = [(left_arrow_rect.centerx - h_arrow_size, left_arrow_rect.centery),
                                (left_arrow_rect.centerx + h_arrow_size, left_arrow_rect.centery - h_arrow_size),
                                (left_arrow_rect.centerx + h_arrow_size, left_arrow_rect.centery + h_arrow_size)]
            right_arrow_points = [(right_arrow_rect.centerx + h_arrow_size, right_arrow_rect.centery),
                                (right_arrow_rect.centerx - h_arrow_size, right_arrow_rect.centery - h_arrow_size),
                                (right_arrow_rect.centerx - h_arrow_size, right_arrow_rect.centery + h_arrow_size)]
            self.buttons[attribute]["left_arrow_points"] = left_arrow_points
            self.buttons[attribute]["right_arrow_points"] = right_arrow_points

            # Build the vertical style selector arrows
            v_arrow_size = 14  # side length
            v_arrow_padding = 5  # padding from the right edge of row_rect
            v_arrow_top_y = row_rect.top + v_arrow_padding
            v_arrow_bottom_y = row_rect.bottom - v_arrow_padding - v_arrow_size
            v_arrow_x = row_rect.right - v_arrow_padding - v_arrow_size

            # Save arrow button positions and colors
            self.buttons[attribute]["v_arrows_active"] = True
            self.buttons[attribute]["up_arrow_rect"] = pg.Rect(v_arrow_x, v_arrow_top_y, v_arrow_size, v_arrow_size)
            self.buttons[attribute]["down_arrow_rect"] = pg.Rect(v_arrow_x, v_arrow_bottom_y, v_arrow_size, v_arrow_size)
            self.buttons[attribute]["up_arrow_color"] = BLACK
            self.buttons[attribute]["down_arrow_color"] = BLACK

            # Save arrow button points for drawing
            self.buttons[attribute]["up_arrow_points"] = [(v_arrow_x + v_arrow_size // 2, v_arrow_top_y),
                                                            (v_arrow_x + v_arrow_size, v_arrow_top_y + v_arrow_size),
                                                            (v_arrow_x, v_arrow_top_y + v_arrow_size)]
            self.buttons[attribute]["down_arrow_points"] = [(v_arrow_x, v_arrow_bottom_y),
                                                                (v_arrow_x + v_arrow_size, v_arrow_bottom_y),
                                                                (v_arrow_x + v_arrow_size // 2, v_arrow_bottom_y + v_arrow_size)]
            
            # Build the Start button
            # Define start button rectangle
            start_button_width = 200
            start_button_height = 50
            start_button_x = (WINDOW_WIDTH - start_button_width) // 2
            start_button_y = WINDOW_HEIGHT - start_button_height - 16  # 100 pixels from the bottom
            self.start_button = pg.Rect(start_button_x, start_button_y, start_button_width, start_button_height)

            self.font = pg.font.Font(None, 36)
            self.start_text = self.font.render(f"Start", True, BLACK)
            self.start_text_x = self.start_button.centerx - self.start_text.get_width() // 2  # Center the text horizontally within the rectangle
            self.start_text_y = self.start_button.centery - self.start_text.get_height() // 2  # Center the text vertically within the rectangle

    
    def handle_click(self, mouse_pos):  
 
        # take appropriate actions when buttons are clicked
        for attribute, d in self.buttons.items():
            (category, style) = self.selections[attribute]

            # click left arrow (decrement category category)
            if point_inside_triangle(mouse_pos, d["left_arrow_points"]):
                # we count of styles in the new category to make sure we don't overflow when coming from one with more styles
                new_category = (category-1) % len(self.assets[attribute])
                num_styles = len(self.assets[attribute][new_category]['styles']) 
                new_style = style if num_styles > style else 0
                self.selections[attribute] = (new_category, new_style)
            # click right arrow (increment category category)
            elif point_inside_triangle(mouse_pos, d["right_arrow_points"]):
                # we count of styles in the new category to make sure we don't overflow when coming from one with more styles
                new_category = (category+1) % len(self.assets[attribute])
                num_styles = len(self.assets[attribute][new_category]['styles'])
                new_style = style if num_styles > style else 0
                self.selections[attribute] = (new_category, new_style)
            # click up arrow (increment style)
            elif point_inside_triangle(mouse_pos, d["up_arrow_points"]) and self.buttons[attribute]["v_arrows_active"]:
                style = (style+1) % len(self.assets[attribute][category]['styles'])
                self.selections[attribute] = (category, style)
            # click down arrow (decrement style)
            elif point_inside_triangle(mouse_pos, d["down_arrow_points"]) and self.buttons[attribute]["v_arrows_active"]:
                style = (style-1) % len(self.assets[attribute][category]['styles'])
                self.selections[attribute] = (category, style)
            else:
                continue
            self.update_image()

        # handle start button click
        if self.start_button.collidepoint(mouse_pos):
            self.game.at_loadout_menu = False  # progress to the next phase
            self.start_text = self.font.render(f"Loading...", True, BLACK)
            self.start_text_x = self.start_button.centerx - self.start_text.get_width() // 2  # Center the text horizontally within the rectangle
            self.start_text_y = self.start_button.centery - self.start_text.get_height() // 2  # Center the text vertically within the rectangle
            self.draw() # draw again to update with Loading text during buffer time

    def update_image(self):
        images = []
        
        # build the list of images to combine into the rendered player character
        for attribute, (category, style) in self.selections.items():
            images.append(
                self.assets[attribute][category]['styles'][style]
            )

        # base character preview image
        self.char_image = combine_images(images)

    def update(self, mouse_pos):
        # update button color if mouse is hovering over them
        for attribute, d in self.buttons.items():
            for dir in ["left","right"]:
                self.buttons[attribute][f"v_arrows_active"] = True
                self.buttons[attribute][f"{dir}_arrow_color"] = \
                    RED if point_inside_triangle(mouse_pos, d[f"{dir}_arrow_points"]) \
                    else BLACK
            for dir in ["up","down"]:
                (category, style) = self.selections[attribute]
                if len(self.assets[attribute][category]['styles']) > 1:
                    self.buttons[attribute][f"v_arrows_active"] = True
                    self.buttons[attribute][f"{dir}_arrow_color"] = \
                        RED if point_inside_triangle(mouse_pos, d[f"{dir}_arrow_points"]) \
                        else BLACK
                else:
                    self.buttons[attribute][f"v_arrows_active"] = False # if there are no styles in the current category, disable the vertical arrows
                    self.buttons[attribute][f"{dir}_arrow_color"] = LIGHT_GREY

    def draw(self):
        self.game.screen.fill(LIGHTER_GREY)  # White background
        self.game.screen.blit(self.char_image, self.char_image_rect)

        for attribute, d in self.buttons.items():
            # draw middle rectangle and text
            pg.draw.rect(self.game.screen, LIGHT_GREY, d["row_rect"])
            
            # attribute title text
            text_surface = pg.font.Font(None, 18).render(f"{attribute.title()}:",True, BLACK)
            text_rect = text_surface.get_rect(topleft=d["row_rect"].topleft)
            self.game.screen.blit(text_surface, text_rect)
            
            # current selection text
            selection_text = self.assets[attribute][self.selections[attribute][0]]['name']
            text_surface = pg.font.Font(None, 36).render(
                selection_text.replace("_"," ").title(), # get the name of the current selection
                True, BLACK
            )
            text_rect = text_surface.get_rect(center=d["row_rect"].center)
            self.game.screen.blit(text_surface, text_rect)

            # draw category selector arrows
            pg.draw.polygon(self.game.screen, d["left_arrow_color"], d["left_arrow_points"])
            pg.draw.polygon(self.game.screen, d["right_arrow_color"], d["right_arrow_points"])

            # draw style selector arrows
            pg.draw.polygon(self.game.screen, d["up_arrow_color"], d["up_arrow_points"])
            pg.draw.polygon(self.game.screen, d["down_arrow_color"], d["down_arrow_points"])

        # draw start button
        pg.draw.rect(self.game.screen, RED, self.start_button)
        self.game.screen.blit(self.start_text, (self.start_text_x, self.start_text_y))
        
        pg.display.flip()