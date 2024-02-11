import numpy as np
from game import actor
import pygame
import random

class Ball(actor.Actor):
    def __init__(self, game_state):
        actor.Actor.__init__(self, game_state)
        super().__init__(game_state)
        self.v_mag = self.game_state.v_mag
        self.position_history = np.zeros((2, 5))
        self.inital_velocity = self.game_state.v_mag * np.array([-np.sqrt(2) / 2, -np.sqrt(2) / 2])
        self.velocity = self.inital_velocity.copy()
        #self.plot = self.game_state.ax.scatter([], [], color='red')
        self.position = np.array([self.game_state.x_max / 2, self.game_state.y_max / 2])
        self.radius = self.x_max/50
        self.friction_coeff = self.game_state.friction_coeff
        self.g = self.game_state.g
        self.loss =  self.game_state.loss

    def bounce_ball(self):
        next_position = self.position + self.velocity
        left_striker = self.game_state.left_striker
        right_striker = self.game_state.right_striker

        hit_left_edge = next_position[0] >= self.x_max - 1
        hit_right_edge = next_position[0] <= 0
        hit_top_edge = next_position[1] >= self.y_max - 1
        hit_bottom_edge = next_position[1] <= 0

        if hit_left_edge:
            self.velocity = self.inital_velocity.copy()
            self.game_state.score_point(is_left_point=False)
            return
        elif hit_right_edge:
            self.velocity = -1 * self.inital_velocity.copy()
            self.game_state.score_point(is_left_point=True)
            return

        if hit_top_edge or hit_bottom_edge:
            self.velocity[1] = -1 * self.velocity[1]
            self.velocity = self.velocity * (1 - self.loss)
        '''
        if (np.linalg.norm(left_striker.position - self.position) < left_striker.radius+self.radius):
            self.velocity = self.game_state.calculate_collision(left_striker, self.velocity)
        elif (np.linalg.norm(right_striker.position - self.position) < right_striker.radius+self.radius):
            self.velocity = self.game_state.calculate_collision(right_striker, self.velocity)
        '''
        '''
        if (left_striker.position[1] < self.position[1] < left_striker.position[1] + left_striker.y_dim) and (
                self.position[0] >= left_striker.position[0] + left_striker.x_dim) and (
                next_position[0] <= left_striker.position[0] + left_striker.x_dim) and self.velocity[0] < 0:
            self.velocity[0] = -1 * self.velocity[0]
            #self.velocity[1] += left_striker.velocity[1]
        if (right_striker.position[1] < self.position[1] < right_striker.position[1] + right_striker.y_dim) and (
                self.position[0] <= right_striker.position[0] + right_striker.x_dim) and (
                next_position[0] >= right_striker.position[0] + right_striker.x_dim) and self.velocity[0] > 0:
            self.velocity[0] = -1 * self.velocity[0] #+ right_striker.velocity[0]
            #self.velocity[1] += right_striker.velocity[1] * 0.3
        '''
        if (next_position[0] < left_striker.position[0] + left_striker.x_dim < self.position[0]) and (left_striker.position[1] + left_striker.y_dim > np.min((next_position[1], self.position[1]))) and (left_striker.position[1] < np.max((next_position[1], self.position[1]))):
            self.velocity[0] = -1 * self.velocity[0]
            self.velocity = self.velocity * (1 - self.loss)
            self.velocity += 0.3*left_striker.avg_velocity
        elif (next_position[0] > right_striker.position[0] > self.position[0]) and (right_striker.position[1] + right_striker.y_dim > np.min((next_position[1], self.position[1]))) and (right_striker.position[1] < np.max((next_position[1], self.position[1]))):
            self.velocity[0] = -1 * self.velocity[0]
            self.velocity = self.velocity * (1 - self.loss)
            self.velocity += 0.3*right_striker.avg_velocity        
        return

    def move(self, y_loc=0):
        self.position = self.position + self.velocity
        self.position_history = self.position_history[:, 1:]
        self.position_history = np.column_stack((self.position_history, self.position))

        # Friction
        new_x_velocity = self.velocity[0] - self.friction_coeff * np.sign(self.velocity[0])
        self.velocity[0] = new_x_velocity * (np.sign(new_x_velocity) == np.sign(self.velocity[0]))
        new_y_velocity = self.velocity[1] - self.friction_coeff * np.sign(self.velocity[1])
        self.velocity[1] = new_y_velocity * (np.sign(new_y_velocity) == np.sign(self.velocity[1]))

        # Gravity
        if self.position[0] < self.x_max / 2:
            self.velocity[0] += self.g * self.inital_velocity[0] * 1 / (0.5 + self.position[0] / self.x_max)
        else:
            self.velocity[0] += -self.g * self.inital_velocity[0] * 1 / (
                        0.5 + (self.x_max / 2 - self.position[0]) / self.x_max)
        return

    def draw(self):
        #self.plot.set_offsets(self.position_history[[1, 0]].T)
        #self.plot.set_alpha([0.2, 0.4, 0.6, 0.8, 1])

        #pygame_pos = pygame.Vector2(self.position[1], self.x_max - self.position[0])
        alpha = [0.2, 0.4, 0.6, 0.8, 1]
        alpha_i = 0

        if np.linalg.norm(self.velocity) > self.x_max/200:
            random_color_1 = np.random.randint(1,5)
            random_color_2 = np.random.randint(1,5)
            random_color_3 = np.random.randint(1,5)
            
            if self.velocity[0] > 0:
                msg_text = self.game_state.msg_font.render('NICE HIT!', True, (int(255/random_color_1), int(255/random_color_3), int(255/random_color_2)))
                self.game_state.screen.blit(msg_text, msg_text.get_rect(center=(self.y_max/2, self.x_max/2)))

        else:
            random_color_1 = 1
            random_color_2 = 1
            random_color_3 = 1

        for hist in self.position_history.T:
            pygame_pos = pygame.Vector2(hist[1], self.x_max - hist[0])
            hex_value = 255*alpha[alpha_i]
            pygame.draw.circle(self.game_state.screen, (int(hex_value/random_color_1), int(hex_value/random_color_3), int(hex_value/random_color_2)), pygame_pos, self.radius)
            alpha_i += 1