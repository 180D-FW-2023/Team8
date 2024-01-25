import numpy as np
from game import striker
import pygame

class StrikerCPU(striker.Striker):
    def move(self, loc):
        max_velocity = self.max_velocity * 10
        ball_y_loc = self.game_state.ball.position[1] - self.y_dim / 2
        ball_x_loc = self.game_state.ball.position[0]
        x_boundary = (4 / 5) * self.game_state.x_max
        previous_y_pos = self.position[1]
        previous_x_pos = self.position[0]
        inertia = self.inertia

        # Calculate next y position based on inertia, ball current y position, and velocity
        next_y_position = (inertia) * previous_y_pos + (1 - inertia) * (ball_y_loc) + (inertia) * self.velocity[1]

        # Calculate next x position based on inertia, ball current distance to the right edge, and velocity
        normalized_distance_to_boundary = np.min(((x_boundary - ball_x_loc) / x_boundary, 1))
        next_x_position = (inertia) * previous_x_pos + (1 - inertia) * (x_boundary + (
                    self.game_state.x_max - x_boundary - self.x_dim) * normalized_distance_to_boundary) + (inertia) * \
                          self.velocity[0] * 0.4 * (1 / (0.5 + normalized_distance_to_boundary))

        is_in_bounds = (next_y_position + self.y_dim < self.game_state.y_max) and (next_y_position > 0)

        # Update instantaneous velocity
        self.velocity = np.array([next_x_position - previous_x_pos, next_y_position - previous_y_pos])

        # Update striker x, y position based
        if is_in_bounds:
            if np.abs(self.velocity[1]) < max_velocity:
                self.position[1] = next_y_position
            else:
                self.position[1] += np.sign(self.velocity[1]) * max_velocity

        self.position[0] = next_x_position

        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))
