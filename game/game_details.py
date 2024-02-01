import numpy as np
from matplotlib import patches, pyplot as plt
from game import ball
from game import striker
from game import striker_cpu
import pygame


class GameState:
    def __init__(self, ball_velocity):
        # Set constants
        resolution = 700
        self.x_max = 1 * resolution
        self.y_max = 4 / 7 * resolution
        self.v_mag = ball_velocity * self.x_max

        # Setup figure and axes
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal")
        self.ax.set_xlim(0, self.y_max)
        self.ax.set_ylim(0, self.x_max)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.y_max, self.x_max))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.Font(None, 36)

        # Draw Scene
        center_line = np.array([[0, self.y_max], [self.x_max / 2, self.x_max / 2]])
        center_circle = patches.Circle((self.y_max / 2, self.x_max / 2), radius=self.x_max / 10, edgecolor='gray',
                                       fill=False, linewidth=1, zorder=1)
        self.ax.add_patch(center_circle)
        self.ax.plot(center_line[0, :], center_line[1, :], color='gray', linewidth=1, zorder=1)

        # Create actors
        self.ball = ball.Ball(self)
        self.left_striker = striker.Striker(self, is_left_striker=True, inertia=0)
        self.right_striker = striker_cpu.StrikerCPU(self, is_left_striker=False, inertia=0.96)
        self.score = [0, 0]
        return

    def update_state(self, left_striker_loc, right_striker_loc):
        # Move actors
        self.ball.bounce_ball()
        self.ball.move()
        self.left_striker.move(left_striker_loc)
        self.right_striker.move(right_striker_loc)

        # Update text
        self.ax.set_title('SCORE\n' + str(self.score[0]) + ' : ' + str(self.score[1]))

    def score_point(self, is_left_point):
        self.score[is_left_point] += 1
        self.ball.position = np.array([self.x_max / 2, self.y_max / 2])
        return
        if is_left_point:
            self.ball.position = self.left_striker.position
        else:
            self.ball.position = self.right_striker.position

    def refresh_display(self):
        self.screen.fill("white")
        # Draw actor plots
        self.ball.draw()
        self.left_striker.draw()
        self.right_striker.draw()

        score_text = self.font.render(f'Score: {self.score}', True, (0, 0, 0))
        self.screen.blit(score_text, (0, 0))

        pygame.display.flip()