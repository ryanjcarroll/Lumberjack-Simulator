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
        self.points_font = pg.font.Font(None, 24)  # Font size for points
        tree_font = pg.font.Font(None, 24)  # Font size for tree labels

        # Draw the title "Skills" at the top center
        self.title_surface = title_font.render("Skills", True, (0, 0, 0))  # Black text
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 30))  # Centered at the top

        # Draw the Points Available text box, right-justified
        self.points_text = f"Points Available: {self.game.player.skill_points_available}"
        self.points_surface = self.points_font.render(self.points_text, True, (0, 0, 0))  # Black text
        self.points_rect = self.points_surface.get_rect(topright=(WINDOW_WIDTH - 20, self.title_rect.bottom + 10))  # Right-justified
        
        # Draw tree labels
        tree_1_label = "Tree 1"
        self.tree_1_label_surface = tree_font.render(tree_1_label, True, (0, 0, 0))
        self.tree_1_label_rect = self.tree_1_label_surface.get_rect(center=(3*WINDOW_WIDTH // 19, self.points_rect.bottom + 30))

        tree_2_label = "Tree 2"
        self.tree_2_label_surface = tree_font.render(tree_2_label, True, (0, 0, 0))
        self.tree_2_label_rect = self.tree_2_label_surface.get_rect(center=(WINDOW_WIDTH // 2, self.points_rect.bottom + 30))

        tree_3_label = "Tree 3"
        self.tree_3_label_surface = tree_font.render(tree_3_label, True, (0, 0, 0))
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

    def handle_click(self, mouse_pos):
        for node in self.skill_tree.flattened:
            if node.button.collidepoint(mouse_pos) and node.status=="next_up" and self.game.player.skill_points_available > 0:
                self.game.player.skill_points_available -= 1
                node.set_active()

                # regenerate the points available textbox
                self.points_text = f"Points Available: {self.game.player.skill_points_available}"
                self.points_surface = self.points_font.render(self.points_text, True, (0, 0, 0))  # Black text
                self.points_rect = self.points_surface.get_rect(topright=(WINDOW_WIDTH - 20, self.title_rect.bottom + 10))  # Right-justified

    def draw_description_box(self, node):
        # Define the size and position of the description box
        font = pg.font.Font(None, 24)  # Change the font size as needed
        text_surface = font.render(node.description, True, (0, 0, 0))  # Black text
        text_rect = text_surface.get_rect(center=(node.button.centerx, node.button.bottom + 20))  # Centered below the node

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

            if node.is_hovered:
                self.draw_description_box(node)
            
        pg.display.flip()