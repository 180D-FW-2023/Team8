import numpy as np

class Actor:

    def __init__(self, game_state):
        self.game_state = game_state
        self.x_max = game_state.x_max
        self.y_max = game_state.y_max
        self.position = np.array([0, 0])

    def move(self, y_loc=0):
        pass
