import numpy as np
from game import actor

class Ball(actor.Actor):
    def __init__(self, game_state):
        actor.Actor.__init__(self, game_state)
        super().__init__(game_state)
        self.v_mag = self.game_state.v_mag
        self.position_history = np.zeros((2, 5))
        self.velocity = self.game_state.v_mag * np.array([-np.sqrt(2) / 2, -np.sqrt(2) / 2])
        self.plot = self.game_state.ax.scatter([], [], color='red')
        self.position = np.array([self.game_state.x_max / 2, self.game_state.y_max / 2])

    def bounce_ball(self):
        next_position = self.position + self.velocity
        left_striker = self.game_state.left_striker
        right_striker = self.game_state.right_striker

        hit_left_edge = next_position[0] >= self.x_max - 1
        hit_right_edge = next_position[0] <= 0
        hit_top_edge = next_position[1] >= self.y_max - 1
        hit_bottom_edge = next_position[1] <= 0

        if hit_left_edge:
            self.velocity[0] = -1 * self.velocity[0]
            self.game_state.score_point(is_left_point=False)
        elif hit_right_edge:
            self.velocity[0] = -1 * self.velocity[0]
            self.game_state.score_point(is_left_point=True)

        if hit_top_edge or hit_bottom_edge:
            self.velocity[1] = -1 * self.velocity[1]

        if (left_striker.position[1] < self.position[1] < left_striker.position[1] + left_striker.y_dim) and (
                self.position[0] >= left_striker.position[0] + left_striker.x_dim) and (
                next_position[0] <= left_striker.position[0] + left_striker.x_dim):
            self.velocity[0] = -1 * self.velocity[0]
        if (right_striker.position[1] < self.position[1] < right_striker.position[1] + right_striker.y_dim) and (
                self.position[0] <= right_striker.position[0]) and (next_position[0] >= right_striker.position[0]):
            self.velocity[0] = -1 * self.velocity[0]
        return

    def move(self, loc=0):
        self.position = self.position + self.velocity
        self.position_history = self.position_history[:, 1:]
        self.position_history = np.column_stack((self.position_history, self.position))
        return

    def draw(self):
        self.plot.set_offsets(self.position_history.T)
        self.plot.set_alpha([0.2, 0.4, 0.6, 0.8, 1])
