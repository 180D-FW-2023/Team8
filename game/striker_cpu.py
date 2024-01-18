import numpy as np
from game import striker

class StrikerCPU(striker.Striker):
    def move(self, loc):
        max_velocity = 1 / 100 * self.game_state.y_max
        ball_loc = self.game_state.ball.position[1] - self.y_dim / 2
        previous_pos = self.position[1]
        inertia = self.inertia

        next_position = (inertia) * self.position[1] + (1 - inertia) * (ball_loc)

        is_in_bounds = (next_position + self.y_dim < self.game_state.y_max) and (next_position > 0)

        self.velocity = next_position - previous_pos

        if is_in_bounds:
            if np.abs(self.velocity) < max_velocity:
                self.position[1] = next_position
            if self.velocity > max_velocity:
                self.position[1] += max_velocity
            if self.velocity < -max_velocity:
                self.position[1] += -max_velocity

        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))

