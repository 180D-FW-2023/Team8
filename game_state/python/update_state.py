import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim
import matplotlib.patches as patches
import time
import os
import pygame

class GameState:
    def __init__(self, ball_velocity):
        # Set constants
        resolution = 700
        self.x_max = 1*resolution
        self.y_max = 4/7*resolution
        self.v_mag = ball_velocity*self.x_max
        
        # Setup figure and axes
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal")
        self.ax.set_xlim(0,self.y_max)
        self.ax.set_ylim(0,self.x_max)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.x_max, self.y_max))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.Font(None, 36)

        # Draw Scene
        center_line = np.array([[0, self.y_max], [self.x_max/2, self.x_max/2]])
        center_circle = patches.Circle((self.y_max/2, self.x_max/2), radius = self.y_max/10, edgecolor = 'gray', fill = False, linewidth = 1, zorder = 1)
        self.ax.add_patch(center_circle)
        self.ax.plot(center_line[0, :], center_line[1, :], color = 'gray', linewidth = 1, zorder = 1)

        
        # Create actors
        self.ball = Ball(self)
        self.left_striker = Striker(self, is_left_striker=True, inertia = 0)
        self.right_striker = StrikerCPU(self, is_left_striker=False, inertia = 0.98)
        self.score = [0,0]
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
        self.ball.position = np.array([self.x_max/2, self.y_max/2])
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

# Base class for actors
class Actor:
    def __init__(self, game_state):
        self.game_state = game_state
        self.x_max = game_state.x_max
        self.y_max = game_state.y_max
        self.position = np.array([0, 0])
    
    def move(self):
        pass

class Striker(Actor):
    def __init__(self, game_state, is_left_striker, inertia):
        Actor.__init__(self, game_state)  
        # Define constants
        self.x_dim = self.game_state.x_max/100
        self.y_dim = self.game_state.y_max/5
        self.inertia = inertia
        edge_offset = 1/20
        self.max_velocity = self.y_max/100
       
        # Create plot
        if is_left_striker:
            x_pos = self.game_state.x_max*edge_offset
            striker_color = 'blue'
        else:
            x_pos = self.game_state.x_max*(1-edge_offset)
            striker_color = 'green'
        self.plot, = self.game_state.ax.plot([], [], color = striker_color)
        
        self.position = np.array([x_pos, 0])
        self.velocity = np.array([0,0])
    
    def move(self, loc):
        inertia = self.inertia*0
        previous_pos = self.position[1]
        next_pos = (inertia)*self.position[1] + (1-inertia)*(loc+1)/2*(self.y_max-self.y_dim)
        self.velocity = next_pos - previous_pos
        if np.abs(self.velocity) < self.max_velocity:
            self.position[1] = next_pos
        else:
            self.position[1] += np.sign(self.velocity)*self.max_velocity

        self.verticies = np.column_stack((self.position + np.array([0,0]), self.position + np.array([0,self.y_dim]), self.position + np.array([self.x_dim,self.y_dim]), self.position + np.array([self.x_dim,0]), self.position + np.array([0,0])))
        
    def draw(self):
        self.plot.set_data(self.verticies[[1,0]])
        pygame_points = (self.verticies[:, 0], self.verticies[:, 1], self.verticies[:, 2], self.verticies[:, 3])  
        pygame.draw.polygon(self.game_state.screen, "green", pygame_points)

class StrikerCPU(Striker):
    def move(self, loc):
        max_velocity = self.max_velocity*10
        ball_y_loc = self.game_state.ball.position[1] - self.y_dim/2
        ball_x_loc = self.game_state.ball.position[0]
        x_boundary = (4/5)*self.game_state.x_max
        previous_y_pos = self.position[1]
        previous_x_pos = self.position[0]
        inertia = self.inertia
        
        # Calculate next y position based on inertia and ball current location
        next_y_position = (inertia)*previous_y_pos + (1-inertia)*(ball_y_loc) + (inertia)*self.velocity[1]

        normalized_distance_to_boundary = np.min(((x_boundary-ball_x_loc)/x_boundary, 1))
        next_x_position = (inertia)*previous_x_pos + (1-inertia)*(x_boundary + (self.game_state.x_max-x_boundary-self.x_dim)*normalized_distance_to_boundary) + (inertia)*self.velocity[0]*0.1
        
        is_in_bounds = (next_y_position + self.y_dim < self.game_state.y_max) and (next_y_position > 0)

        # Update instantaneous velocity
        self.velocity = np.array([next_x_position - previous_x_pos, next_y_position - previous_y_pos])
        
        # Update striker x, y position based
        if is_in_bounds: 
            if np.abs(self.velocity[1]) < max_velocity:    
                self.position[1] = next_y_position
            else:
                self.position[1] += np.sign(self.velocity[1])*max_velocity
        
        self.position[0] = next_x_position
        
        self.verticies = np.column_stack((self.position + np.array([0,0]), self.position + np.array([0,self.y_dim]), self.position + np.array([self.x_dim,self.y_dim]), self.position + np.array([self.x_dim,0]), self.position + np.array([0,0])))

        
class Ball(Actor):
    def __init__(self, game_state):
        Actor.__init__(self, game_state)
        self.v_mag = self.game_state.v_mag        
        self.position_history = np.zeros((2, 5))
        self.inital_velocity = self.game_state.v_mag*np.array([-np.sqrt(2)/2, -np.sqrt(2)/2])
        self.velocity = self.inital_velocity.copy()
        self.plot = self.game_state.ax.scatter([], [], color = 'red')
        self.position = np.array([self.game_state.x_max/2, self.game_state.y_max/2])


    def bounce_ball(self):
        next_position = self.position + self.velocity
        left_striker = self.game_state.left_striker
        right_striker = self.game_state.right_striker

        hit_left_edge = next_position[0] >= self.x_max-1
        hit_right_edge = next_position[0] <= 0
        hit_top_edge = next_position[1] >= self.y_max-1
        hit_bottom_edge = next_position[1] <= 0

        if hit_left_edge:
            self.velocity = self.inital_velocity.copy()
            self.game_state.score_point(is_left_point = False)
            return
        elif hit_right_edge:
            self.velocity = -1*self.inital_velocity.copy()
            self.game_state.score_point(is_left_point = True)
            return

        if hit_top_edge or hit_bottom_edge:
            self.velocity[1] = -1*self.velocity[1]
        
        if (left_striker.position[1] < self.position[1] < left_striker.position[1] + left_striker.y_dim) and (self.position[0] >= left_striker.position[0] + left_striker.x_dim) and (next_position[0] <= left_striker.position[0] + left_striker.x_dim):
            self.velocity[0] = -1*self.velocity[0] 
            self.velocity[1] += left_striker.velocity
        if (right_striker.position[1] < self.position[1] < right_striker.position[1] + right_striker.y_dim) and (self.position[0] <= right_striker.position[0] + right_striker.x_dim) and (next_position[0] >= right_striker.position[0]):
            self.velocity[0] = -1*self.velocity[0] + right_striker.velocity[0]
            self.velocity[1] += right_striker.velocity[1]*0.3

        self.velocity = self.velocity*0.999
        return

    def move(self):
        self.position = self.position + self.velocity
        self.position_history = self.position_history[:, 1:]
        self.position_history = np.column_stack((self.position_history, self.position))
        return
    
    def draw(self):
        self.plot.set_offsets(self.position_history[[1,0]].T)
        self.plot.set_alpha([0.2, 0.4, 0.6, 0.8, 1])

        pygame_pos = pygame.Vector2(self.position[0], self.position[1])
        pygame.draw.circle(self.game_state.screen, "red", pygame_pos, self.game_state.x_max/100)


# Initialize game state object
frame_rate = 120*2 # frames per second
ball_velocity = 3 # proportion of board x max per second

game_state = GameState(ball_velocity/frame_rate)

# Get sensor data file path
file_path = os.path.join("..", "..", "input_output", "sensor_data.csv")
dir_path = os.path.dirname(__file__)
os.chdir(dir_path)
full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))

latest_reading = 0 # keep track of previous reading in case data file is empty

def update(frame):
    # update(position, velocity, game_board)
    global game_state
    global latest_reading

    # open data file for reading
    with open(full_path, 'r') as file:
        reading = file.read()
        if reading != '': # make sure reading is valid; if not, use previous reading
            reading = float(reading)
        else:
            reading = latest_reading

        left_striker_loc = reading
        latest_reading = reading
        file.close()
    right_striker_loc = 0
    game_state.update_state(left_striker_loc, right_striker_loc)
    game_state.refresh_display()
    time.sleep(1/frame_rate)
    return game_state.ax

ani = anim.FuncAnimation(game_state.fig, update, frames=np.linspace(0, 2), blit=False, interval = 1)
#ani.save('game_state.gif', writer="pillow writer")

plt.show()