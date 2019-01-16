# -*- coding: utf-8 -*-
import numpy as np
import networkx as nx

class tree():
    # Tree of the game
    # ---------------
    # Initialisation:
    # ---------------
    # state (matrix): Board of the game
    # player_turn (int): ID of the current player
    
    def __init__(self, state, player_turn):
        self.nb_lines = state.shape[0]
        self.nb_columns = state.shape[1]
        
        # Create the graph and add the root of the tree (first node)
        G = nx.Graph()
        player_turn = 1 + player_turn % 2
        untried_moves = list(range(self.nb_columns))
        G.add_node(1, node_id = 1, move = None, visits = 1, reward = 0, state =  state,
                   untried_moves = untried_moves, player_turn = player_turn, terminal = False)
        self.body = G
        
    def add_node(self, i, j, move):
        # Add a new node to the tree
        # ---------------
        # Inputs : 
        # ---------------
        # i (int): ID of the parent
        # j (int): ID of the child
        # move (int): Game action leading up to the new node's state (the chosen column)
        
        state = self.body.nodes[i]["state"].copy() # Store the parent node's game state
        tmp = list(np.where(state[:, move] == 0))[0]
        pos = tmp[-1] 
        player_turn = 1 + self.body.nodes[i]["player_turn"] % 2 # Swap player turn
        state[pos, move] = player_turn # Add a token to the board using the selected column
        
        # Remove the selected column from the parent node's untried move list so it cannot be selected anymore
        untried_moves = list(range(self.nb_columns))
        untried_moves_updated = self.body.nodes[i]["untried_moves"].copy()
        untried_moves_updated.remove(move)
        self.body.nodes[i]["untried_moves"] = untried_moves_updated
        
        # Check whether or not the new node's game state is terminal
        terminal = self.is_terminal(state)
        
        # Create the new node and connect it to its parent
        self.body.add_node(j, node_id = j, move = move, visits = 1, 
                           reward = 0, state = state,
                           untried_moves = untried_moves,
                           player_turn = player_turn, terminal = terminal)
        self.body.add_edge(i, j)

    def next_move(self, node):
        # Return a move from a node that hasn't been previously selected 
        
        # Retrieve all the available  column (not full) 
        available_moves = np.where(node["state"][0,:] == 0)[0] 
        untried_moves = node["untried_moves"]
        
        # Select a move that hasn't been previously selected that is also an available column
        possible_moves = np.intersect1d(untried_moves, available_moves) # Intersection between unselected column and available column
        move = np.random.choice(possible_moves)
        
        return move
    
    def check_winner(self, state):
        # Search the board for a potential winner
        # ---------------
        # Return:
        # ---------------
        #   - False : If no winners are detected
        #   - Else, the ID of the winner 
        
        # Search all lines
        for i in range(self.nb_lines):
            for j in range(4):
                tmp = list(set(state[i, j:4+j]))
                if len(tmp) == 1 and tmp[0]!=0:
                    return tmp[0]
                
        # Search all columns         
        for j in range(self.nb_columns):
            for i in range(3):
                tmp = list(set(state[i:4+i, j]))
                if len(tmp) == 1 and tmp[0]!=0:
                    return tmp[0]
        
        # Search all diagonales           
        state_tmp = np.reshape(state, (1, self.nb_lines * self.nb_columns))[0]
        for j in range(self.nb_lines - 3) :
            for i in range(self.nb_columns - 3) :
                tmp =  [state_tmp[self.nb_columns * j+i],
                        state_tmp[self.nb_columns * j + i + self.nb_columns + 1],
                        state_tmp[self.nb_columns*j + i + 2 * self.nb_columns + 2],
                        state_tmp[self.nb_columns * j + i + 3 * self.nb_columns + 3]]
                tmp = list(set(tmp))
                if len(tmp) == 1 and tmp[0]!=0:
                    return tmp[0]
                    
        for j in range(self.nb_lines - 3, self.nb_lines) :
            for i in range(self.nb_columns - 3) :
                tmp = [state_tmp[self.nb_columns * j + i],
                       state_tmp[self.nb_columns * j + i - self.nb_columns + 1],
                       state_tmp[self.nb_columns * j + i - 2 * self.nb_columns + 2],
                       state_tmp[self.nb_columns * j + i - 3 * self.nb_columns + 3]]
                tmp = list(set(tmp))
                if len(tmp) == 1 and tmp[0]!=0:
                    return tmp[0] 
        return False
    
    def update_node(self, i, reward):
        # Update the node's visits and rewards after the backup
        self.body.nodes[i]["visits"] += 1
        self.body.nodes[i]["reward"] += reward
        
    def children(self, node):
        # Return all the children of a given node
        neightbors = np.array(list(self.body.adj[node["node_id"]]))
        return np.sort(neightbors[neightbors > node["node_id"]])
    
    def parents(self, node):
        # Return the parent of a given node
        neightbors = np.array(list(self.body.adj[node["node_id"]]))
        return neightbors[neightbors < node["node_id"]]
    
    def fully_expanded(self, node):
        # Check weither a node is fully expended or not
        available_moves = np.where(node["state"][0,:] == 0)[0] 
        untried_moves = node["untried_moves"]
        possible_moves = np.intersect1d(untried_moves, available_moves) # Intersection between unselected column and available column
        return len(self.children(node)) == self.nb_columns or len(possible_moves) == 0
    
    def is_terminal(self, state):
        # Check weither or not a state is terminal (Tie or winner)
        available_moves = np.where(state[0,:] == 0)[0]
        check_winner = self.check_winner(state)
        return len(available_moves) == 0 or (check_winner != False) 
        
    
    def show(self, show_labels):
        # Plot the tree
        color_map = ["green"] # The root is shown in green
        
        # Retrieve colors depending on the node's player (yellow or red)
        for node in range(2, self.body.number_of_nodes() + 1):
            if self.body.nodes[node]["player_turn"] == 1:
                color_map.append('yellow')
            else: 
                color_map.append('red')    
                
        # Plot the graph using force directed graph drawing method        
        nx.draw_kamada_kawai(self.body, node_size=100, 
                             alpha=0.65, node_color=color_map, 
                             with_labels = show_labels)
        
    def simulation(self, state, player_turn):
        # Simulate a game of connect four using a given state and return the reward

        state_tmp = state.copy()
        player_turn_tmp = player_turn
        check_winner = self.check_winner(state_tmp)
        
        while check_winner == False:
            available_moves = np.where(state_tmp[0,:] == 0)[0] # Retrieve all available columns
            
            if len(available_moves) == 0 and check_winner == False: 
                return 0 # Tie value is 0
            move = np.random.choice(available_moves) # Randomly select an available column
            
            player_turn_tmp = 1 + player_turn_tmp % 2 # Swap player's turn
            
            pos = np.where(state_tmp[:,move] == 0)[0][-1] 
            state_tmp[pos, move] = player_turn_tmp # Add a token to the board
            
            
            check_winner = self.check_winner(state_tmp) # Search the board for a potential winner
            
        if check_winner == player_turn: 
            return  1 # Win value
        else:
            return -1 # Lose value 