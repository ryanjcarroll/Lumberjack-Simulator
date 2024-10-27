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
		-	-	-	-	-	-	root	-	-	-	-	-	-		
		v						v						v		
		0						0						0		
		v						v						v		
1	<	2	>	3		1	<	2	>	3		1	<	2	>	3
v				v		v				v		v				v
4	>	5	<	6		4	>	5	<	6		4	>	5	<	6
v		v		v		v		v		v		v		v		v
7	>	8	<	9		7	>	8	<	9		7	>	8	<	9
		v						v						v		
		10						10						10		

    """
    def __init__(self, game):

        self.game = game
        
        self.root = SkillNode(-1,0,"root", None)
        self.nodes = {}

        # Nodes of the left tree
        color = FOREST_GREEN
        self.nodes["0_left"] = SkillNode(0, -3, "More HP From Apple Trees", color, points=2,
                                        func=lambda: setattr(self.game.player, 'fruit_hp', self.game.player.fruit_hp + 2.5))
        self.nodes["1_left"] = SkillNode(1, -4, "Node 1", color)
        self.nodes["2_left"] = SkillNode(1, -3, "Faster Movespeed", color, points=3,
                                        func=lambda: setattr(self.game.player, 'move_distance', self.game.player.move_distance + 1))
        self.nodes["3_left"] = SkillNode(1, -2, "Node 3", color)
        self.nodes["4_left"] = SkillNode(2, -4, "Node 4", color)
        self.nodes["5_left"] = SkillNode(2, -3, "Node 5", color)
        self.nodes["6_left"] = SkillNode(2, -2, "Node 6", color)
        self.nodes["7_left"] = SkillNode(3, -4, "Node 7", color)
        self.nodes["8_left"] = SkillNode(3, -3, "Node 8", color)
        self.nodes["9_left"] = SkillNode(3, -2, "Node 9", color)
        self.nodes["10_left"] = SkillNode(4, -3, "Node 10", color)

        # Nodes of the center tree
        color = ORANGE
        self.nodes["0_center"] = SkillNode(0, 0, "+5% Dodge Chance", color, points=3,
                                            func=lambda: setattr(self.game.player, "dodge_chance", self.game.player.dodge_chance + .05))
        self.nodes["1_center"] = SkillNode(1, -1, "+10% Crit Chance", color, points=3,
                                            func=lambda: setattr(self.game.player, "crit_chance", self.game.player.crit_chance + .10))

        self.nodes["2_center"] = SkillNode(1, 0, "Increase Sword Range", color, points=3,
                                            func=lambda: self.change_weapon_stats("sword", "attack_distance", 2))
        self.nodes["3_center"] = SkillNode(1, 1, "Node 3", color)
        self.nodes["4_center"] = SkillNode(2, -1, "Node 4", color)
        self.nodes["5_center"] = SkillNode(2, 0, "Node 5", color)
        self.nodes["6_center"] = SkillNode(2, 1, "Node 6", color)
        self.nodes["7_center"] = SkillNode(3, -1, "Node 7", color)
        self.nodes["8_center"] = SkillNode(3, 0, "Node 8", color)
        self.nodes["9_center"] = SkillNode(3, 1, "Node 9", color)
        self.nodes["10_center"] = SkillNode(4, 0, "Node 10", color)

        # Nodes of the right tree
        color = SKY_BLUE
        self.nodes["0_right"] = SkillNode(0, 3, "Node 0", color)
        self.nodes["1_right"] = SkillNode(1, 2, "Node 1", color)
        self.nodes["2_right"] = SkillNode(1, 3, "Node 2", color)
        self.nodes["3_right"] = SkillNode(1, 4, "Node 3", color)
        self.nodes["4_right"] = SkillNode(2, 2, "Node 4", color)
        self.nodes["5_right"] = SkillNode(2, 3, "Node 5", color)
        self.nodes["6_right"] = SkillNode(2, 4, "Node 6", color)
        self.nodes["7_right"] = SkillNode(3, 2, "Node 7", color)
        self.nodes["8_right"] = SkillNode(3, 3, "Node 8", color)
        self.nodes["9_right"] = SkillNode(3, 4, "Node 9", color)
        self.nodes["10_right"] = SkillNode(4, 3, "Node 10", color)

        # Define the root note relationships
        self.root.children = [self.nodes["0_left"], self.nodes["0_center"], self.nodes["0_right"]]

        # Left tree
        self.nodes["0_left"].children = [self.nodes["2_left"]]
        self.nodes["1_left"].children = [self.nodes["4_left"]]
        self.nodes["2_left"].children = [self.nodes["1_left"], self.nodes["3_left"]]
        self.nodes["3_left"].children = [self.nodes["6_left"]]
        self.nodes["4_left"].children = [self.nodes["5_left"], self.nodes["7_left"]]
        self.nodes["5_left"].children = [self.nodes["8_left"]]
        self.nodes["6_left"].children = [self.nodes["5_left"],self.nodes["9_left"]]
        self.nodes["7_left"].children = [self.nodes["8_left"]]
        self.nodes["8_left"].children = [self.nodes["10_left"]]
        self.nodes["9_left"].children = [self.nodes["8_left"]]
        

        # Center tree
        self.nodes["0_center"].children = [self.nodes["2_center"]]
        self.nodes["1_center"].children = [self.nodes["4_center"]]
        self.nodes["2_center"].children = [self.nodes["1_center"], self.nodes["3_center"]]
        self.nodes["3_center"].children = [self.nodes["6_center"]]
        self.nodes["4_center"].children = [self.nodes["5_center"], self.nodes["7_center"]]
        self.nodes["5_center"].children = [self.nodes["8_center"]]
        self.nodes["6_center"].children = [self.nodes["5_center"],self.nodes["9_center"]]
        self.nodes["7_center"].children = [self.nodes["8_center"]]
        self.nodes["8_center"].children = [self.nodes["10_center"]]
        self.nodes["9_center"].children = [self.nodes["8_center"]]
       
        # Right tree
        self.nodes["0_right"].children = [self.nodes["2_right"]]
        self.nodes["1_right"].children = [self.nodes["4_right"]]
        self.nodes["2_right"].children = [self.nodes["1_right"], self.nodes["3_right"]]
        self.nodes["3_right"].children = [self.nodes["6_right"]]
        self.nodes["4_right"].children = [self.nodes["5_right"], self.nodes["7_right"]]
        self.nodes["5_right"].children = [self.nodes["8_right"]]
        self.nodes["6_right"].children = [self.nodes["5_right"],self.nodes["9_right"]]
        self.nodes["7_right"].children = [self.nodes["8_right"]]
        self.nodes["8_right"].children = [self.nodes["10_right"]]
        self.nodes["9_right"].children = [self.nodes["8_right"]]
        self.root.add_point()

    #     self.flattened = []
    #     self.flatten_tree(self.root)

    # def flatten_tree(self, node):
    #     self.flattened.append(node)  # Add the current node to the flat list
    #     for child in node.children:  # Recursively add all children
    #         if child not in self.flattened:
    #             self.flatten_tree(child)

    def change_weapon_stats(self, weapon_name, stat_name, delta):
        self.game.player.weapon_stats[weapon_name][stat_name] += delta
