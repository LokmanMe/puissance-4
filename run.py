# -*- coding: utf-8 -*-
from game import game


# Launch the game 
if __name__ == "__main__":
    G = game(N = 6, K = 7, width = 600, use_mcts = True, human_player = False, first_player = 1)
    G.run()

# Show the game's decision tree
# G.mcts.tree.show(show_labels = True)