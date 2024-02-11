import numpy as np
from game import striker
import pygame

class StrikerCPU(striker.Striker):
    def move(self, loc):
        max_velocity = self.max_velocity * 10
        ball_y_loc = self.game_state.ball.position[1] - self.y_dim / 2
        ball_x_loc = self.game_state.ball.position[0]
        x_boundary = (0.75) * self.game_state.x_max
        previous_y_pos = self.position[1]
        previous_x_pos = self.position[0]
        inertia = self.inertia
        
        if self.game_state.diff == 0: 
            self.sensitivity = 13.5
        else:
            self.sensitivity = 10
        
        # Calculate next y position based on inertia, ball current y position, velocity, and urgency
        urgency = 1/(1 + np.exp(self.sensitivity*(0.9*self.x_max-ball_x_loc)/(0.9*self.x_max)))
        #if ball_x_loc > self.x_max/2:
        next_y_position = (1-urgency) * previous_y_pos + (urgency) * (ball_y_loc) + urgency*self.instant_velocity[1]
        #else:
            #next_y_position = previous_y_pos

        # Calculate next x position based on inertia, ball current distance to the right edge, and velocity
        normalized_distance_to_boundary = np.min(((x_boundary - ball_x_loc) / x_boundary, 1))
        next_x_position = (inertia) * previous_x_pos + (1 - inertia) * (x_boundary + (self.game_state.x_max - x_boundary - self.x_dim) * normalized_distance_to_boundary) + (inertia) * self.instant_velocity[0] * 0.1 * (1 / (0.5 + normalized_distance_to_boundary))

        is_in_bounds = (next_y_position + self.y_dim < self.game_state.y_max) and (next_y_position > 0)

        self.instant_velocity = np.array([next_x_position - previous_x_pos, next_y_position - previous_y_pos])
        self.velocity = self.instant_velocity
        
        # Update average velocity
        self.displacement_steps += 1
        if self.displacement_steps == self.max_steps:
            self.displacement_steps = 0
            self.displacement = np.array([next_x_position, next_y_position]) - self.previous_position
            self.previous_position = np.array([next_x_position, next_y_position])
            self.avg_velocity = self.displacement/self.max_steps
        
        # Update striker x, y position based
        if is_in_bounds:
            if np.abs(self.velocity[1]) < max_velocity:
                self.position[1] = next_y_position
            else:
                self.position[1] += np.sign(self.velocity[1]) * max_velocity
                self.instant_velocity[1] = self.max_velocity
        if np.abs(self.velocity[0]) < max_velocity:
            self.position[0] = next_x_position
        else:
            self.position[0] += np.sign(self.velocity[0]) * max_velocity
            self.instant_velocity[0] = self.max_velocity

        #self.position[0] = next_x_position

        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))
        
        # Check ball collisions
        ball = self.game_state.ball
        '''
        if (self.position[1] < ball.position[1] < self.position[1] + self.y_dim) and (
                ball.position[0] <= previous_x_pos) and (
                ball.position[0] >= self.position[0]):
            if ball.velocity[0] > 0:
                ball.position[0] = self.position[0]
                ball.velocity[0] = -1 * self.velocity[0]
                #ball.velocity[1] += self.velocity[1]
            else:
                ball.position[0] = self.position[0]
        '''
        if (previous_x_pos > ball.position[0] > next_x_position) and (np.max((previous_y_pos, next_y_position)) < ball.position[1] < np.min((previous_y_pos + self.y_dim, next_y_position + self.y_dim))):
            ball.position[0] = self.position[0]
            if ball.velocity[0] > 0:
                ball.velocity[0] = -1 * ball.velocity[0]
                ball.velocity = ball.velocity * (1 - self.game_state.loss)
            ball.velocity += 0.3*self.avg_velocity
