from settings import *
import pygame as pg

class SkillTreeMenu:
    def __init__(self, game):
        self.game = game
        self.skill_tree = self.game.player.skill_tree

        self.build_elements() # calls self.layout_nodes()

    def update(self, mouse_pos):
        for node in self.skill_tree.flattened:
            node.is_hovered = node.button.collidepoint(mouse_pos)

    def build_elements(self):
        # Set font for title and other text
        title_font = pg.font.Font(None, 36)  # Font size for the title
        self.subtitle_font = pg.font.Font(None, 24)  # Font size for "Points Available" and tree labels
        self.points_font = pg.font.Font(None, 16) # font size for the "0/3" point indicators

        # Draw the title "Skills" at the top center
        self.title_surface = title_font.render("Skills", True, (0, 0, 0))  # Black text
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))  # Centered at the top

        # Draw the Points Available text box, right-justified
        self.points_text = f"Points Available: {self.game.player.skill_points_available}"
        self.points_surface = self.subtitle_font.render(self.points_text, True, (0, 0, 0))  # Black text
        self.points_rect = self.points_surface.get_rect(topright=(WINDOW_WIDTH - 20, self.title_rect.bottom + 10))  # Right-justified
        
        # Draw tree labels
        tree_1_label = "Survival"
        self.tree_1_label_surface = self.subtitle_font.render(tree_1_label, True, (0, 0, 0))
        self.tree_1_label_rect = self.tree_1_label_surface.get_rect(center=(3*WINDOW_WIDTH // 19, self.points_rect.bottom + 30))

        tree_2_label = "Combat"
        self.tree_2_label_surface = self.subtitle_font.render(tree_2_label, True, (0, 0, 0))
        self.tree_2_label_rect = self.tree_2_label_surface.get_rect(center=(WINDOW_WIDTH // 2, self.points_rect.bottom + 30))

        tree_3_label = "Nature"
        self.tree_3_label_surface = self.subtitle_font.render(tree_3_label, True, (0, 0, 0))
        self.tree_3_label_rect = self.tree_3_label_surface.get_rect(center=(15*WINDOW_WIDTH // 19, self.points_rect.bottom + 30))

        self.layout_nodes()

    def layout_nodes(self):
        """
        Each node will store its own button rect to make it easier to iterate across the tree when drawing.
        """
        button_width = WINDOW_WIDTH // 19

        for node in self.skill_tree.flattened:
            # Calculate the position for each node based on its row and col
            button_x = (button_width * node.col * 2) + WINDOW_WIDTH // 2 - button_width // 2
            button_y = (button_width * node.row * 2) + self.tree_3_label_rect.bottom
            node.button = pg.Rect(button_x, button_y, button_width, button_width)

            points_label = f"{node.current_points}/{node.total_points}"
            points_label_surface = self.points_font.render(points_label, True, (255,255,255))
            points_label_rect = points_label_surface.get_rect(bottomright=node.button.bottomright)
            node.points_label_surface = points_label_surface
            node.points_label_rect = points_label_rect

    def handle_click(self, mouse_pos):
        for node in self.skill_tree.flattened:
            if node.button.collidepoint(mouse_pos):
                if node.status!="not_active" and self.game.player.skill_points_available > 0 and node.current_points < node.total_points:
                    self.game.player.skill_points_available -= 1
                    node.add_point()

                    # regenerate the points available textbox
                    self.points_text = f"Points Available: {self.game.player.skill_points_available}"
                    self.points_surface = self.subtitle_font.render(self.points_text, True, (0, 0, 0))  # Black text
                    self.points_rect = self.points_surface.get_rect(topright=(WINDOW_WIDTH - 20, self.title_rect.bottom + 10))  # Right-justified

                    # regenerate the "0/3" points label
                    points_label = f"{node.current_points}/{node.total_points}"
                    points_label_surface = self.points_font.render(points_label, True, (255,255,255))
                    points_label_rect = points_label_surface.get_rect(bottomright=node.button.bottomright)
                    node.points_label_surface = points_label_surface
                    node.points_label_rect = points_label_rect

    def draw_description_box(self, node):
        # Define the size and position of the description box
        font = pg.font.Font(None, 24)  # Change the font size as needed
        text_surface = font.render(node.description, True, (0, 0, 0))  # Black text
        text_rect = text_surface.get_rect(center=(node.button.centerx, node.button.bottom + 20))  # Centered below the node

        # Screen dimensions
        screen_width, screen_height = self.game.screen.get_size()

        # Adjust the position to keep the description box within screen bounds
        if text_rect.right > screen_width:
            text_rect.right = screen_width - 10  # Keep some padding from the right edge
        if text_rect.left < 0:
            text_rect.left = 10  # Keep some padding from the left edge
        if text_rect.bottom > screen_height:
            text_rect.bottom = screen_height - 10  # Keep some padding from the bottom edge
        if text_rect.top < 0:
            text_rect.top = 10  # Keep some padding from the top edge

        # Draw a semi-transparent rectangle as the background for the text box
        box_padding = 5
        box_rect = pg.Rect(text_rect.x - box_padding, text_rect.y - box_padding,
                        text_rect.width + box_padding * 2, text_rect.height + box_padding * 2)
        pg.draw.rect(self.game.screen, (255, 255, 255), box_rect)  # White background
        pg.draw.rect(self.game.screen, (0, 0, 0), box_rect, 2)  # Black border

        # Draw the text on the screen
        self.game.screen.blit(text_surface, text_rect)

    def draw(self):
        self.game.screen.fill(LIGHTER_GREY)  # background

        self.game.screen.blit(self.title_surface, self.title_rect)
        self.game.screen.blit(self.points_surface, self.points_rect)

        self.game.screen.blit(self.tree_1_label_surface, self.tree_1_label_rect)
        self.game.screen.blit(self.tree_2_label_surface, self.tree_2_label_rect)
        self.game.screen.blit(self.tree_3_label_surface, self.tree_3_label_rect)        

        for node in self.skill_tree.flattened:
            # skip the root node
            if node.description == 'root':
                continue

            # Draw node arrows between nodes
            for child in node.children:
                start_pos = node.button.center
                end_pos = child.button.center
                pg.draw.line(self.game.screen, DARK_GREY, start_pos, end_pos, 3)

            # Draw node, with color based on hover state
            node_color = node.active_color if (node.status == "active" or node.is_hovered) else node.color
            pg.draw.rect(self.game.screen, node_color, node.button)
            self.game.screen.blit(node.points_label_surface, node.points_label_rect)

            if node.is_hovered:
                self.draw_description_box(node)
            
        pg.display.flip()