import numpy as np
from game import actor
import pygame

class Striker(actor.Actor):
    def __init__(self, game_state, is_left_striker, inertia):
        actor.Actor.__init__(self, game_state)
        # Define constants
        super().__init__(game_state)
        self.x_dim = self.game_state.x_max / 25
        self.y_dim = self.game_state.y_max / 5
        self.inertia = inertia
        edge_offset = 1 / 20
        self.max_velocity = self.y_max / 100

        # Create plot
        if is_left_striker:
            x_pos = self.game_state.x_max * edge_offset
            striker_color = 'blue'
        else:
            x_pos = self.game_state.x_max * (1 - edge_offset)
            striker_color = 'green'
        self.plot, = self.game_state.ax.plot([], [], color=striker_color)

        self.position = np.array([x_pos, 0])
        self.velocity = np.array([0, 0])

    def move(self, loc):
        x_loc = loc[1]
        y_loc = loc[0]
        normalized_x_loc = self.x_max / 20 + (x_loc + 1) / 2 * self.x_max / 5
        normalized_y_loc = (y_loc + 1) / 2 * (self.y_max - self.y_dim)
        inertia = self.inertia * 0

        previous_x_pos = self.position[0]
        next_x_pos = (inertia) * self.position[1] + (1 - inertia) * (normalized_x_loc)

        previous_y_pos = self.position[1]
        next_y_pos = (inertia) * self.position[1] + (1 - inertia) * (normalized_y_loc)

        self.velocity = np.array([next_x_pos - previous_x_pos, next_y_pos - previous_y_pos])
        if np.abs(self.velocity[1]) < self.max_velocity*100:
            self.position[1] = next_y_pos
        else:
            self.position[1] += np.sign(self.velocity[1]) * self.max_velocity

        self.position[0] = next_x_pos

        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))

    def draw(self):
        self.plot.set_data(self.verticies[[1, 0]])
        pygame_points = (self.verticies[:, 0], self.verticies[:, 1], self.verticies[:, 2], self.verticies[:, 3])
        pygame.draw.polygon(self.game_state.screen, "green", pygame_points)