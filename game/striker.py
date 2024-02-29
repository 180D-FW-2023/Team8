import numpy as np
from game import actor
import pygame
import os

class Striker(actor.Actor):
    def __init__(self, game_state, is_left_striker, inertia):
        actor.Actor.__init__(self, game_state)
        # Define constants
        super().__init__(game_state)
        self.x_dim = self.game_state.x_max / 25
        self.y_dim = self.game_state.y_max / 5
        self.inertia = inertia
        edge_offset = 1 / 20
        self.max_velocity = self.y_max
        self.is_left_striker = is_left_striker
        self.radius = self.x_max/10
        self.max_steps = 10

        img_scaler = 1.3
        if self.game_state.diff == 1 and not self.is_left_striker:
            image_name = 'extreme_cpu_striker.png'
        else:
            image_name = 'striker.png'
        path = os.path.join('game', 'assets', image_name)
        self.img = pygame.transform.scale(pygame.image.load(path), (self.y_dim*img_scaler, self.x_dim*1.5))

        # Create plot
        if is_left_striker:
            x_pos = self.game_state.x_max * edge_offset
            striker_color = 'blue'
        else:
            x_pos = self.game_state.x_max * (1 - edge_offset)
            striker_color = 'green'
        #self.plot, = self.game_state.ax.plot([], [], color=striker_color)

        self.position = np.array([x_pos, 0])
        self.velocity = np.array([0, 0])
        self.instant_velocity = self.velocity
        self.avg_velocity = self.velocity
        self.velocity_history = np.zeros((2, 15))
        self.displacement = np.array([0, 0])
        self.displacement_steps = 0
        self.previous_position = self.position

    def move(self, loc):
        x_loc = loc[1]
        y_loc = loc[0]
        normalized_x_loc = self.x_max / 20 + (x_loc + 1) / 2 * self.x_max / 5
        normalized_y_loc = (y_loc + 1) / 2 * (self.y_max - self.y_dim)
        inertia = self.inertia * 0

        previous_x_pos = self.position[0]
        next_x_position = (inertia) * self.position[1] + (1 - inertia) * (normalized_x_loc)

        previous_y_pos = self.position[1]
        next_y_position = (inertia) * self.position[1] + (1 - inertia) * (normalized_y_loc)
        
        self.instant_velocity = np.array([next_x_position - previous_x_pos, next_y_position - previous_y_pos])
        self.velocity = self.instant_velocity
        
        # Update average velocity
        self.displacement_steps += 1
        if self.displacement_steps == self.max_steps:
            self.displacement_steps = 0
            self.displacement = np.array([next_x_position, next_y_position]) - self.previous_position
            self.previous_position = np.array([next_x_position, next_y_position])
            self.avg_velocity = self.displacement/self.max_steps
        

        if np.abs(self.velocity[1]) < self.max_velocity:
            self.position[1] = next_y_position
        else:
            self.position[1] += np.sign(self.velocity[1]) * self.max_velocity

        if np.abs(self.velocity[0]) < self.max_velocity:
            self.position[0] = next_x_position
        else:
            self.position[0] += np.sign(self.velocity[0]) * self.max_velocity

        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))
        
        # Check ball collisions
        ball = self.game_state.ball
        '''
        if (self.position[1] < ball.position[1] < self.position[1] + self.y_dim) and (
                ball.position[0] >= previous_x_pos + self.x_dim) and (
                ball.position[0] <= self.position[0] + self.x_dim):
            if ball.velocity[0] < 0:
                ball.position[0] = self.position[0] + self.x_dim
                ball.velocity[0] = -1 * self.velocity[0]
                #ball.velocity[1] += self.velocity[1]
            else:
                ball.position[0] = self.position[0] + self.x_dim
        '''
        if (previous_x_pos + self.x_dim < ball.position[0] < next_x_position + self.x_dim) and (np.max((previous_y_pos, next_y_position)) < ball.position[1] < np.min((previous_y_pos + self.y_dim, next_y_position + self.y_dim))):
            ball.position[0] = self.position[0] + self.x_dim
            if ball.velocity[0] < 0:
                ball.velocity[0] = -1 * ball.velocity[0]
                ball.velocity = ball.velocity * (1 - self.game_state.loss)
            ball.velocity += 0.3*self.avg_velocity

        
    def draw(self):
        #self.plot.set_data(self.verticies[[1, 0]])
        
        # Pygame draw
        pygame_pos = pygame.Vector2(self.position[1], self.x_max - self.position[0])

        flipped_verticies = self.verticies
        flipped_verticies[0] = self.x_max - flipped_verticies[0]
        flipped_verticies = flipped_verticies[[1, 0]]
        pygame_points = (flipped_verticies[:, 0], flipped_verticies[:, 1], flipped_verticies[:, 2], flipped_verticies[:, 3])
        if not self.is_left_striker:
            color = "green"
        else:
            color = 'blue'
        #pygame.draw.polygon(self.game_state.screen, color, pygame_points)
        #rect = pygame.Rect(self.position[1], self.x_max - self.position[0] - self.x_dim, self.y_dim, self.x_dim)
        rect = self.img.get_rect()
        center = (self.position[1] + self.y_dim/2, self.x_max - self.position[0] - self.x_dim/2)
        rect.center = center
        self.game_state.screen.blit(self.img, rect)
        #pygame.draw.circle(self.game_state.screen, color, pygame_pos, self.radius)