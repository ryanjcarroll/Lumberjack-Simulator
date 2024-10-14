from settings import *
from utility import closer_to_white
import pygame as pg

class SkillNode:
    def __init__(self, row, col, description, color, points=1, func=None):
        self.description = description

        self.status = "not_active"  # inactive, next_up, active
        self.active_color = color
        self.color = DARK_GREY

        self.current_points = 0
        self.total_points = points

        self.row = row
        self.col = col
        self.is_hovered = False

        # UI elements for displaying in the SkillTreeMenu
        self.button = None 
        self.points_label_surface = None
        self.points_label_rect = None

        # function to call once this skill is activated
        self.func = func

        # children of this node
        self.children = []

    def add_point(self):
        self.status = "active"
        self.current_points += 1
        if self.func:
            self.func() 
        
        # stage the "next up" skills as needed
        if self.current_points >= self.total_points:
            for child in self.children:
                if child.status == "not_active":
                    child.status = "next_up"
                    child.color = closer_to_white(child.active_color, 0.5)

class SkillTree:
    """
    		-	-	-	-	-	-  root	-	-	-	-	-	-		
            v						v						v		
            0						7						14		
            V						V						V		
    2a	<	1	>	2b		9a	<	8	>	9b		16a	<	15	>	16b
    V				V		V				V		V				V
    3a	>	4a	<	3b		10a	>	11a	<	10b		17a	>	18a	<	17b
    V		V		V		V		V		V		V		V		V
    4b	>	5	<	4c		11b	>	12	<	11c		18b	>	19	<	18c
            V						V						V		
            6						13						20		
    """
    def __init__(self, game):

        self.game = game
        
        self.root = SkillNode(-1,0,"root", None)

        # Nodes of the left tree
        color = FOREST_GREEN
        node_0 =  SkillNode(0, -3, "More HP From Apple Trees", color, points=2, func=lambda: setattr(self.game.player, 'fruit_hp', self.game.player.fruit_hp + 2.5))                      
        node_1 =  SkillNode(1, -3, "Arrow Toward Camp", color, func=lambda: setattr(self.game.compass, "active", True))
        node_2a = SkillNode(1, -4, "Faster Movespeed", color, points=3, func=lambda: setattr(self.game.player, 'move_distance', self.game.player.move_distance + 1)) 
        # TODO node_2b = SkillNode(1, -2, "Deal More Damage to Dead Trees", color, points=2, func=lambda: setattr(self.game.player, "burned_tree_axe_damage", self.game.player.burned_tree_axe_damage + 1)) 
        node_2b = SkillNode(1, -2, "Node 2b", color)
        node_3a = SkillNode(2, -4, "Node 3a", color) 
        node_3b = SkillNode(2, -2, "Node 3b", color)
        node_4a = SkillNode(2, -3, "Node 4a", color)
        node_4b = SkillNode(3, -4, "Node 4b", color)
        node_4c = SkillNode(3, -2, "Node 4c", color)
        node_5 =  SkillNode(3, -3, "Node 5", color)
        node_6 =  SkillNode(4, -3, "Node 6", color)
        # Nodes of the center tree
        color = ORANGE
        node_7 =   SkillNode(0, 0, "+5% Dodge Chance", color, points=3, func=lambda: setattr(self.game.player, "dodge_chance", self.game.player.dodge_chance + .05))
        node_8 =   SkillNode(1, 0, "+10% Crit Chance", color, points=3, func=lambda: setattr(self.game.player, "crit_chance",  self.game.player.crit_chance + .10))
        node_9a =  SkillNode(1, -1, "Increase Sword Range", color, points=3, func=lambda: self.change_weapon_stats("sword","attack_distance",2))
        node_9b =  SkillNode(1, 1, "Node 9b", color)
        node_10a = SkillNode(2, -1, "Node 10a", color)
        node_10b = SkillNode(2, 1, "Node 10b", color)
        node_11a = SkillNode(2, 0, "Node 11a", color)
        node_11b = SkillNode(3, -1, "Node 11b", color)
        node_11c = SkillNode(3, 1, "Node 11c", color)
        node_12 =  SkillNode(3, 0, "Node 12", color)
        node_13 =  SkillNode(4, 0, "Node 13", color)
        # Nodes of the right tree
        color = SKY_BLUE
        node_14 =  SkillNode(0, 3, "Node 14", color)
        node_15 =  SkillNode(1, 3, "Node 15", color)
        node_16a = SkillNode(1, 2, "Node 16a", color)
        node_16b = SkillNode(1, 4, "Node 16b", color)
        node_17a = SkillNode(2, 2, "Node 17a", color)
        node_17b = SkillNode(2, 4, "Node 17b", color)
        node_18a = SkillNode(2, 3, "Node 18a", color)
        node_18b = SkillNode(3, 2, "Node 18b", color)
        node_18c = SkillNode(3, 4, "Node 18c", color)
        node_19 =  SkillNode(3, 3, "Node 19", color)
        node_20 =  SkillNode(4, 3, "Node 20", color)

        # Define the relationships
        self.root.children = [node_0, node_7, node_14]
        # Left tree
        node_0.children = [node_1]
        node_1.children = [node_2a, node_2b]
        node_2a.children = [node_3a]
        node_2b.children = [node_3b]
        node_3a.children = [node_4a, node_4b]
        node_3b.children = [node_4a, node_4c]
        node_4a.children = [node_5]
        node_4b.children = [node_5]
        node_4c.children = [node_5]
        node_5.children = [node_6]
        # Center tree
        node_7.children = [node_8]
        node_8.children = [node_9a, node_9b]
        node_9a.children = [node_10a]
        node_9b.children = [node_10b]
        node_10a.children = [node_11a, node_11b]
        node_10b.children = [node_11a, node_11c]
        node_11a.children = [node_12]
        node_11b.children = [node_12]
        node_11c.children = [node_12]
        node_12.children = [node_13]
        # Right tree
        node_14.children = [node_15]
        node_15.children = [node_16a, node_16b]
        node_16a.children = [node_17a]
        node_16b.children = [node_17b]
        node_17a.children = [node_18a, node_18b]
        node_17b.children = [node_18a, node_18c]
        node_18a.children = [node_19]
        node_18b.children = [node_19]
        node_18c.children = [node_19]
        node_19.children = [node_20]

        self.root.add_point()

        self.flattened = []
        self.flatten_tree(self.root)

    def flatten_tree(self, node):
        self.flattened.append(node)  # Add the current node to the flat list
        for child in node.children:  # Recursively add all children
            if child not in self.flattened:
                self.flatten_tree(child)

    def change_weapon_stats(self, weapon_name, stat_name, delta):
        self.game.player.weapon_stats[weapon_name][stat_name] += delta
