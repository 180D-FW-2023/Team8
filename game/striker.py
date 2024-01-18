import numpy as np
from game import actor

class Striker(actor.Actor):

    def __init__(self, game_state, is_left_striker, inertia):
        actor.Actor.__init__(self, game_state)
        # Define constants
        super().__init__(game_state)
        self.x_dim = self.game_state.x_max / 100
        self.y_dim = self.game_state.y_max / 5
        self.inertia = inertia
        edge_offset = 1 / 20

        # Create plot
        if is_left_striker:
            x_pos = self.game_state.x_max * edge_offset
            striker_color = 'blue'
        else:
            x_pos = self.game_state.x_max * (1 - edge_offset)
            striker_color = 'green'
        self.plot, = self.game_state.ax.plot([], [], color=striker_color)

        self.position = np.array([x_pos, 0])
        self.velocity = 0

    def move(self, loc):
        inertia = self.inertia * 0
        previous_pos = self.position[1]
        self.position[1] = (inertia) * self.position[1] + (1 - inertia) * (loc + 1) / 2 * (self.y_max - self.y_dim)
        self.velocity = self.position[1] - previous_pos
        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))

    def draw(self):
        self.plot.set_data(self.verticies)