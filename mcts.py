# -*- coding: utf-8 -*-
import numpy as np
from tree import tree

class mcts():
    # Monte carlos tree search
    # ---------------
    # Initialisation:
    # ---------------
    # current_state (matrix): Current state of the game's board
    # player_turn (int): ID of the current player  
    
    def __init__(self, current_state, player_turn):
        self.scalar = 1 / np.sqrt(2.0) # Exploratory constant
        self.tree = tree(current_state, player_turn) # Initialisation of the game's tree

    def utc_search(self, budget):
        # UTC search method
        # ---------------
        # Return an estimation of the best action to use
        # for the current game state for a given budget
        
        root = self.tree.body.nodes[1] # Initialisation of the tree's root (First node)
        for i in range(budget):
            node = self.tree_policy(root) # Exploration of the tree
            reward = self.default_policy(node["state"], node["player_turn"]) # Simulation of the game using the selected node's state
            self.backup_negamax(node, reward) # Reward backup
        return self.best_child(root, 0)
    
    def tree_policy(self, node):
        # Tree policy function
        # Control the exploration of the game's tree
        while node["terminal"] == False:
            if self.tree.fully_expanded(node) == False: # Add a child to the node if it's not fully expanded yet
                return self.expand(node)
            else:
                node = self.best_child(node, self.scalar) # If the node is fully expanded, retrieve its best child
        return node
    
    """
    def tree_policy(self, node):
        # Tree policy function using an expand trick
        # Control the exploration of the game's tree
        
        while node["terminal"] == False:
            if len(self.tree.children(node)) == 0: # Add a child to the node if it doenst have any
                return self.expand(node)
            elif np.random.uniform(0,1) < 0.5 : # If the node isn't fully expanded, retrieve its best child with a 0.5 probability
                 node = self.best_child(node, self.scalar)
            else:
                if self.tree.fully_expanded(node) == False:  # Add a child to the node if it's not fully expanded yet
                    return self.expand(node)
                else:
                    node = self.best_child(node, self.scalar) # If the node is fully expanded, retrieve its best child
        return node
    """
    
    def expand(self, node):
        
        # Add a new child to the selected node
        new_move = self.tree.next_move(node) # Select an unused move using the node's game state
        node_id = self.tree.body.number_of_nodes() + 1 # ID of the new node
        self.tree.add_node(node["node_id"], node_id, new_move) # Create and connect the new node
        return self.tree.body.nodes[node_id] # Return the node created
    

    def best_child(self, node, c):
        # Select the best child of a given node
        score_list = []
        children_list = []
        
        # Calculate and retrieve  the score of each of the node's children
        for n in self.tree.children(node):
            node_tmp = self.tree.body.nodes[n]
            exploit = node_tmp["reward"] / node_tmp["visits"] # Exploitation score
            explore = np.sqrt(2.0 * np.log(node["visits"]) / node_tmp["visits"]) # Exploration score
            score = exploit + c * explore
            score_list.append(score)
            children_list.append(n)
        return self.tree.body.nodes[children_list[np.argmax(score_list)]] # Return the child with the highest score
    
    def default_policy(self, state, player_turn):
        # Launch the simulation using a given game state
        return self.tree.simulation(state, player_turn)
    
    def backup_negamax(self, node, reward):
        # Backup method for 2 players
    	while len(self.tree.parents(node)) != 0:
            node["visits"] += 1
            node["reward"] += reward
            reward = -reward # Swaping the sign of the reward
            node = self.tree.body.nodes[self.tree.parents(node)[0]]