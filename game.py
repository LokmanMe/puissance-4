# -*- coding: utf-8 -*-
import numpy as np
import tkinter
import time
from mcts import mcts
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class game():
    # Connect four game
    # ---------------
    # Inputs :
    # ---------------
    # [N,K] (int): Dimensions of the board
    # width (int): Width of the tkinter board  
    # use_mcts (Bool): Whether of not the player want to use MCTS
    def __init__(self, N = 6, K = 7, width = 480, use_mcts = False, human_player = False, first_player = 1):
        
        # Initialisation of the mcts method
        self.use_mcts = use_mcts
        self.mcts = None 
        
        # Game's parameters
        self.human_player = human_player # Allow user to play as yellow if True
        self.nb_lines = N
        self.nb_columns = K
        self.width = width
        self.space = width / 64
        self.radius = (width - (K+1) * self.space ) / (2*K)
        self.height =  2 * N * self.radius + (N+1) * self.space
        
        # Initialisation of the game's state
        self.board = np.zeros((N, K))
        self.possible_moves = np.arange(K)
        self.first_player = first_player
        self.player_turn = first_player # Player 1 (Yellow) starts first
        
        # Player scores
        self.P1_wins = 0
        self.P2_wins = 0
        self.ties = 0
        self.P1_mcts_score = []
        self.P2_mcts_score = []
        
        # Initialisation of the tkinter canvas
        window = tkinter.Tk()
        window.title("Puissance 4")
        self.window = window
        self.grid = tkinter.Canvas(window,
                        width = width,
                        height = self.height,
                        background = "blue4")
        self.create_grid()
        self.grid.pack()
        
        
        
        
    def create_disk(self, x, y, r, col, tag):
        # Add a disk to the tkinter canvas
        # ---------------
        # Inputs :
        # ---------------
        # [x,y] : Coordinates of the disk
        # r, col, tag : radius, color and tag attributes of the disk
        self.grid.create_oval(x-r, y-r, x+r, y+r, fill = col, width = 0,tags = tag)
        
    
    def create_grid(self):
        # Create the grid of the game on the tkinter canvas
        for i in range(self.nb_lines + 1):
            for j in range(self.nb_columns + 1):
                self.create_disk(self.space + self.radius + (j - 1) * (self.space + 2 * self.radius), 
                                 self.space + self.radius + (i - 1) * (self.space + 2 * self.radius), 
                                 self.radius, "ivory2", "hole")
    def highlight(self, pos):
        # Highlight the winning combination
        for n in range(4):
            i = self.nb_lines - pos[0][n]
            j = 1 + pos[1][n] 
            r = self.radius / 3
            self.grid.create_oval(j * (self.space + 2 * self.radius) - self.radius - r,
                                  (self.nb_lines - i + 1) * (self.space + 2 * self.radius) - self.radius - r,
                                  j * (self.space + 2 * self.radius) - self.radius + r,
                                  (self.nb_lines - i + 1) * (self.space + 2 * self.radius) - self.radius + r,
                                  fill = "dark green", width=0, tags = "token")
            self.window.update()
            time.sleep(0.2)
   
    def create_token(self, i, j, col):
        # Add a token to the grid
        # ---------------
        # Inputs :
        # ---------------
        # i (int): Chosen line
        # j (int): Chosen column
        # col (str): Color of the token
        self.create_disk(j * (self.space + 2 * self.radius) - self.radius,
                           (self.nb_lines - i + 1) * (self.space + 2 * self.radius) - self.radius,
                           self.radius, col, "token")
        
    def restart(self):
        # Reset the game's state and clean the grid once the game is over
        self.grid.delete("token")
        self.board = np.zeros((self.nb_lines, self.nb_columns))
        self.player_turn = self.first_player
        self.window.update()
        self.P1_mcts_score = []
        self.P2_mcts_score = []
          
        
    def check_winner(self):
        # Search the board for a potential winner
        # ---------------
        # Return:
        # ---------------
        #   - False : If no winners are detected
        #   - Else, the ID of the winner 
        
        # Search all lines
        for i in range(self.nb_lines):
            for j in range(4):
                tmp = list(set(self.board[i, j:4+j]))
                if len(tmp) == 1 and tmp[0]!=0:
                    self.highlight([[i]*4, list(range(j, 4+j))])
                    return tmp[0]
                
        # Search all columns        
        for j in range(self.nb_columns):
            for i in range(3):
                tmp = list(set(self.board[i:4+i, j]))
                if len(tmp) == 1 and tmp[0]!=0:
                    self.highlight([list(range(i, i+4)), [j]*4])
                    return tmp[0]
                
        # Search all diagonales          
        board_tmp = np.reshape(self.board, (1, self.nb_lines * self.nb_columns))[0]
        
        for j in range(self.nb_lines - 3) :
            for i in range(self.nb_columns - 3) :
                tmp =  [board_tmp[self.nb_columns * j+i],
                        board_tmp[self.nb_columns * j + i + self.nb_columns + 1],
                        board_tmp[self.nb_columns*j + i + 2 * self.nb_columns + 2],
                        board_tmp[self.nb_columns * j + i + 3 * self.nb_columns + 3]]
                tmp = list(set(tmp))
                if len(tmp) == 1 and tmp[0]!=0:
                    self.highlight([[j, j+1, j+2, j+3], [i, i+1, i+2, i+3]])
                    return tmp[0]
                
        for j in range(self.nb_lines - 3, self.nb_lines) :
            for i in range(self.nb_columns - 3) :
                tmp = [board_tmp[self.nb_columns * j + i],
                       board_tmp[self.nb_columns * j + i - self.nb_columns + 1],
                       board_tmp[self.nb_columns * j + i - 2 * self.nb_columns + 2],
                       board_tmp[self.nb_columns * j + i - 3 * self.nb_columns + 3]]
                tmp = list(set(tmp))
                if len(tmp) == 1 and tmp[0]!=0:
                    self.highlight([[j, j-1, j-2, j-3],[i, i+1, i+2, i+3]])
                    return tmp[0] 
        return False
    
    
    def add_token(self, pos):
        # Add a token to the board
        # ---------------
        # Input :
        # ---------------
        # pos (int): The chosen column
        
        tmp = list(np.where(self.board[:, pos] == 0))[0] # 
        i = tmp[-1] # Recovering the first available 0 on the chosen column
        
        self.board[i, pos] = self.player_turn # Adding the current player's ID to the board
        self.possible_moves = np.where(self.board[0, :] == 0)[0] # Updating available columns
        
        # Adding the new token on the tkinter canvas
        col = ["yellow", "red"][self.player_turn - 1]
        self.create_token(self.nb_lines - i, pos + 1, col)
        self.window.update()
        
        # Swapping player's turn
        self.player_turn = 1 + self.player_turn % 2
    
        
    def run(self):
        # Plot the players scores if mcts is used for both
        if self.use_mcts == True and self.human_player == False:
            fig = plt.figure()
            def animate(i):
                xticks = np.arange(len(self.P1_mcts_score) + len(self.P2_mcts_score))
                fig.clear()
                if self.first_player == 1:
                    if len(xticks) < 4:
                        plt.plot(xticks[xticks % 2 == 0], self.P1_mcts_score, 'y.')
                        plt.plot(xticks[xticks % 2 == 1], self.P2_mcts_score, 'r.') 
                    else:
                        plt.plot(xticks[xticks % 2 == 0], self.P1_mcts_score, 'y')
                        plt.plot(xticks[xticks % 2 == 1], self.P2_mcts_score, 'r') 
                else:
                    if len(xticks) < 4:
                        plt.plot(xticks[xticks % 2 == 1], self.P1_mcts_score, 'y.')
                        plt.plot(xticks[xticks % 2 == 0], self.P2_mcts_score, 'r.') 
                    else:
                        plt.plot(xticks[xticks % 2 == 1], self.P1_mcts_score, 'y')
                        plt.plot(xticks[xticks % 2 == 0], self.P2_mcts_score, 'r') 
                plt.ylim((-1.5,1.5))
                plt.grid()
                plt.title("Scores mcts des joueurs en fonction du tour")
                plt.legend(('Score mcts jaune', 'Score mcts rouge'), loc='upper left')
                
            ani = animation.FuncAnimation(fig, animate)
            plt.show()
        # Launch the game and update player's scores after each round
        self.window.update()
        while True:
            if self.human_player == True and self.player_turn == self.first_player:
                pos = int(input("Choix de la colonne : ")) # Allow the user to select a column
                
            elif self.use_mcts == True:
                self.mcts = mcts(self.board, self.player_turn) # Initialisation of a new mcts using the current game's state
                node = self.mcts.utc_search(budget = 1600) # UTC algorithm
                pos = node["move"]
                if self.player_turn == 1:
                    self.P1_mcts_score = self.P1_mcts_score + [node["reward"]/node["visits"]]
                    print("Jaune choisit (" ,pos, ") score mcts: ",np.around(self.P1_mcts_score[-1], 3))
                else:
                    self.P2_mcts_score = self.P2_mcts_score + [node["reward"]/node["visits"]]
                    print("Rouge choisit (", pos, ") score mcts: ",np.around(self.P2_mcts_score[-1], 3))
                
                
            else:
                pos = np.random.choice(self.possible_moves) # Select a random available column if no mcts is used 
                time.sleep(0.5)
                
            self.add_token(pos) # Add the token to the selected column
            check_winner = self.check_winner()# Search the board for a potential winner
            
            if check_winner != False or len(self.possible_moves) == 0:
                
                if len(self.possible_moves) == 0 and check_winner == False: # Tie
                    self.ties = self.ties + 1
                    print("=========== Match nul ===========")
                elif  check_winner == 1: # Yellow wins
                    self.P1_wins = self.P1_wins + 1
                    print("=========== Victoire  jaune ===========")
                elif check_winner == 2: # Red wins
                    self.P2_wins = self.P2_wins + 1
                    print("=========== Victoire rouge ===========")
                
                # Print scores
                print("Score jaune: ", self.P1_wins)        
                print("Score rouge: ", self.P2_wins)
                print("Match nul: ", self.ties)
                
                # Next game
                next_game = input("Nouvelle partie? Y/N ")
                if next_game in [ "n", "N", "No", "no"]:
                    self.window.destroy() # Close the game
                    plt.close() # Close the graph
                    
                    # Print final score
                    print("===================================")
                    print("=========== Jeu terminé ===========")
                    print("===================================")
                    print("Score jaune: ", self.P1_wins)
                    print("Score rouge: ", self.P2_wins)
                    print("Match nul: ", self.ties)
                    break
                else:
                    self.restart()