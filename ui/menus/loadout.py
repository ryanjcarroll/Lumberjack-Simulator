import pygame as pg
from settings import *
from glob import glob
from utility import point_inside_triangle, combine_images
import os
import random
from ui.button import Button, TriangleButton


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
        "left_arrow":<TriangleButton>,
        "right_arrow":<TriangleButton>,
        "up_arrow":<TriangleButton>,
        "down_arrow":<TriangleButton>,
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
                            style_id : self.game.sprites.load_from_tilesheet(
                                    path=path,
                                    row_index=0,
                                    col_index=style_id * SPRITESHEET_NUM_COLUMNS, # extract method already accounts for tile size
                                    tile_size=SPRITESHEET_TILE_SIZE,
                                    resize = (SPRITESHEET_TILE_SIZE*4, SPRITESHEET_TILE_SIZE*4)
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
            selections[attribute] = (category, style)
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
        # title
        self.title_text = pg.font.Font(None, 48).render(f"Build Your Character", True, BLACK)
        self.title_text_x = WINDOW_WIDTH // 2 - self.title_text.get_width() // 2
        self.title_text_y = 10

        # determine position of the character preview model
        self.char_image_rect = self.char_image.get_rect()
        char_image_x = (WINDOW_WIDTH//2) - (self.char_image_rect.width//2)
        char_image_y = 16
        self.char_image_rect.topleft = (char_image_x, char_image_y)

        # define row dimensions
        row_width = WINDOW_WIDTH // 2
        row_height = 50
        row_margin = 20
        row_y = self.char_image_rect.bottom + row_margin # y-coord to start at
        h_arrow_padding = 96 # from edge of window

        for attribute in self.attributes:
            # Build the selector box and the horizontal category selector arrows
            self.buttons[attribute] = {}
            self.buttons[attribute]['row_rect'] = pg.Rect((WINDOW_WIDTH - row_width) // 2, row_y, row_width, row_height)  # Adjusted x-coordinate

            # build the left and right TriangleButtons to cycle each attribute
            self.buttons[attribute]["left_arrow"] = TriangleButton(
                screen=self.game.screen,
                rect=(h_arrow_padding, row_y + row_height // 4, row_height // 2, row_height // 2),
                direction="left",
                on_click = lambda attr=attribute: self.increment_category(attr, -1)
            )
            self.buttons[attribute]["right_arrow"] = TriangleButton(
                screen=self.game.screen,
                rect=(WINDOW_WIDTH - row_height // 2 - h_arrow_padding, row_y + row_height // 4, row_height // 2, row_height // 2),
                direction="right",
                on_click = lambda attr=attribute: self.increment_category(attr, 1)
            )
            row_y += row_height + row_margin
            
            # build the vertical style selector TriangleButtons
            v_arrow_size = 14  # side length
            v_arrow_padding = 5  # padding from the right edge of row_rect
            v_arrow_top_y = self.buttons[attribute]['row_rect'].top + v_arrow_padding
            v_arrow_bottom_y = self.buttons[attribute]['row_rect'].bottom - v_arrow_padding - v_arrow_size
            v_arrow_x = self.buttons[attribute]['row_rect'].right - v_arrow_padding - v_arrow_size

            self.buttons[attribute]['up_arrow'] = TriangleButton(
                screen=self.game.screen,
                rect=(v_arrow_x, v_arrow_top_y, v_arrow_size, v_arrow_size),
                direction="up",
                on_click = lambda attr=attribute: self.increment_style(attr, 1)
            )
            self.buttons[attribute]['down_arrow'] = TriangleButton(
                screen=self.game.screen,
                rect=(v_arrow_x, v_arrow_bottom_y, v_arrow_size, v_arrow_size),
                direction="down",
                on_click = lambda attr=attribute: self.increment_style(attr, -1)
            )

            # Build the Start button
            self.start_button = Button(
                screen=self.game.screen,
                rect=(
                    (WINDOW_WIDTH - 200) // 2, 
                    (WINDOW_HEIGHT - 50) - 16,  # N pixels from the bottom
                    200, 
                    50
                ),
                color=(255, 0, 0),
                hover_color=(0, 255, 0),
                text="Start",
                on_click=lambda: setattr(self.game, 'at_loadout_menu', False)
            )

    def handle_event(self, event):  
        # handle mousebutton clicks
        if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEMOTION:
            self.start_button.handle_event(event)

            # take appropriate actions when navigation buttons are clicked
            for attribute, d in self.buttons.items():
                d['left_arrow'].handle_event(event)
                d['right_arrow'].handle_event(event)
                d['up_arrow'].handle_event(event)
                d['down_arrow'].handle_event(event)

            self.update_image()

    def increment_category(self, attribute, n):
        """
        Called when the left and right arrows are clicked.
        """
        (category, style) = self.selections[attribute]

        # cycle the category
        new_category = (category+n) % len(self.assets[attribute])
        num_styles = len(self.assets[attribute][new_category]['styles']) 
        new_style = style if num_styles > style else 0
        self.selections[attribute] = (new_category, new_style)

    def increment_style(self, attribute, n):
        """
        Called when the up and down arrows are clicked
        """
        (category, style) = self.selections[attribute]

        # cycle the style within the active categorey
        style = (style+n) % len(self.assets[attribute][category]['styles'])
        self.selections[attribute] = (category, style)
    
    def update_image(self):
        images = []
        
        # build the list of images to combine into the rendered player character
        for attribute, (category, style) in self.selections.items():
            images.append(
                self.assets[attribute][category]['styles'][style]
            )

        # base character preview image
        self.char_image = combine_images(images)
                
    def draw(self):
        self.game.screen.fill(LIGHTER_GREY)  # background
        self.game.screen.blit(self.title_text, (self.title_text_x, self.title_text_y))
        self.game.screen.blit(self.char_image, self.char_image_rect)

        for attribute, d in self.buttons.items():
            (category, style) = self.selections[attribute]

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

            # draw navigation arrows
            d['left_arrow'].draw()
            d['right_arrow'].draw()

            # draw vertical arrows (as long as there are styles in the current category)
            if len(self.assets[attribute][category]['styles']) > 1:
                d['up_arrow'].draw()
                d['down_arrow'].draw()

        # draw start button
        self.start_button.draw()
        
        pg.display.flip()