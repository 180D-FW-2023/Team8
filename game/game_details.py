import numpy as np
from matplotlib import patches, pyplot as plt
from game import ball
from game import striker
from game import striker_cpu
import pygame
import os
import time


class GameState:
    def __init__(self, ball_velocity, resolution, aspect_ratio, diff, sfx, screen):
        # Set constants
        self.x_max = 1 * resolution
        self.y_max = aspect_ratio * resolution
        self.v_mag = ball_velocity * self.x_max
        self.friction_coeff = 0.01*0
        self.g = 0.001*0
        self.striker_inertia = 0.25
        self.loss = 0.1
        self.diff = diff
        self.sfx = sfx
        
        self.goal_sound = pygame.mixer.Sound(os.path.join('game', 'assets', 'sounds', 'goal.wav'))


        # Create shared objects
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.score_font = pygame.font.Font(None, 36)
        self.msg_font = pygame.font.Font(None, 36)

        # Draw Scene
        self.draw_scene()

        # Create actors
        self.ball = ball.Ball(self)
        self.left_striker = striker.Striker(self, is_left_striker=True, inertia=0)
        self.right_striker = striker_cpu.StrikerCPU(self, is_left_striker=False, inertia=self.striker_inertia)
        self.score = [0, 0]
        return

    def update_state(self, left_striker_loc, right_striker_loc):
        # Move actors
        self.ball.bounce_ball()
        self.ball.move()
        self.left_striker.move(left_striker_loc)
        self.right_striker.move(right_striker_loc)

    def score_point(self, is_left_point):
        self.score[is_left_point] += 1
        self.ball.position = np.array([self.x_max / 2, self.y_max / 2])
        self.ball.velocity[1] = 0

        pygame.mixer.Sound.play(self.goal_sound)
        pygame.mixer.music.stop()
        
        return
        if is_left_point:
            self.ball.position = self.left_striker.position
        else:
            self.ball.position = self.right_striker.position

    def refresh_display(self):
        
        # Draw actor plots
        self.draw_scene()
        self.ball.draw()
        self.left_striker.draw()
        self.right_striker.draw()

        score_text = self.score_font.render(f'SCORE {self.score[0]} : {self.score[1]}', True, 'white')
        self.screen.blit(score_text, score_text.get_rect(center=(self.y_max/2, 0.02*self.x_max)))

        pygame.display.flip()

    def calculate_collision(self, striker, v):
        # Left Striker
        c2 = self.ball.position
        c1 = striker.position
        r2 = self.ball.radius
        r1 = striker.radius
        #inter1 = 1/2*(c1+c2) + (r1**2 - r2**2)/(2*r**2)*(c2-c1) + 1/2*np.sqrt(2*(r1**2+r2**2)/r**2 - (r1**2 - r2**2)**2/r**4 - 1)*(c2 - c1)[[1,0]]
        #inter2 = 1/2*(c1+c2) + (r1**2 - r2**2)/(2*r**2)*(c2-c1) - 1/2*np.sqrt(2*(r1**2+r2**2)/r**2 - (r1**2 - r2**2)**2/r**4 - 1)*(c2 - c1)[[1,0]]

        n = (c1-c2)/np.linalg.norm(c1-c2)
        p = 2*np.dot(v, n)/(0.3+0.7)
        new_v = v - p*(0.7*n - 0.3*n)
        new_v = new_v/np.linalg.norm(new_v)*self.ball.inital_velocity

        return new_v
    
    def draw_scene(self):
        self.screen.fill("black")
        line_width = np.max((1, int(self.y_max/300)))
        pygame.draw.line(self.screen, 'white', (0, self.x_max/2), (self.y_max, self.x_max/2), width=line_width)
        pygame.draw.circle(self.screen, 'white', (self.y_max/2, self.x_max/2), self.y_max/4, width=line_width)
        pass
