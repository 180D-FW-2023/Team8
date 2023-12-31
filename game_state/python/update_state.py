import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim
import matplotlib.patches as patches
import time
import os

class GameState:
    def __init__(self, ball_velocity):
        # Set constants
        resolution = 700000
        self.x_max = 1*resolution
        self.y_max = 4/7*resolution
        self.v_mag = ball_velocity*self.x_max
        
        # Setup figure and axes
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal")
        self.ax.set_xlim(0,self.x_max)
        self.ax.set_ylim(0,self.y_max)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        # Draw Scene
        center_line = np.array([[self.x_max/2, self.x_max/2], [0, self.y_max]])
        center_circle = patches.Circle((self.x_max/2, self.y_max/2), radius = self.x_max/10, edgecolor = 'gray', fill = False, linewidth = 1, zorder = 1)
        self.ax.add_patch(center_circle)
        self.ax.plot(center_line[0, :], center_line[1, :], color = 'gray', linewidth = 1, zorder = 1)

        
        # Create actors
        self.ball = Ball(self)
        self.left_striker = Striker(self, is_left_striker=True, inertia = 0)
        self.right_striker = StrikerCPU(self, is_left_striker=False, inertia = 0.95)
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
        # Draw actor plots
        self.ball.draw()
        self.left_striker.draw()
        self.right_striker.draw()

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
       
        # Create plot
        if is_left_striker:
            x_pos = self.game_state.x_max*edge_offset
            striker_color = 'blue'
        else:
            x_pos = self.game_state.x_max*(1-edge_offset)
            striker_color = 'green'
        self.plot, = self.game_state.ax.plot([], [], color = striker_color)
        
        self.position = np.array([x_pos, 0])
        self.velocity = 0
    
    def move(self, loc):
        inertia = self.inertia*0
        previous_pos = self.position[1]
        self.position[1] = (inertia)*self.position[1] + (1-inertia)*(loc+1)/2*(self.y_max-self.y_dim)
        self.velocity = self.position[1] - previous_pos
        self.verticies = np.column_stack((self.position + np.array([0,0]), self.position + np.array([0,self.y_dim]), self.position + np.array([self.x_dim,self.y_dim]), self.position + np.array([self.x_dim,0]), self.position + np.array([0,0])))
        
    def draw(self):
        self.plot.set_data(self.verticies)

class StrikerCPU(Striker):
    def move(self, loc):
        max_velocity = 1/100*self.game_state.y_max
        ball_loc = self.game_state.ball.position[1] - self.y_dim/2
        previous_pos = self.position[1]
        inertia = self.inertia
        
        next_position = (inertia)*self.position[1] + (1-inertia)*(ball_loc)
        
        is_in_bounds = (next_position + self.y_dim < self.game_state.y_max) and (next_position > 0)

        self.velocity = next_position - previous_pos
        
        if is_in_bounds: 
            if np.abs(self.velocity) < max_velocity:    
                self.position[1] = next_position
            if self.velocity > max_velocity:
                self.position[1] += max_velocity
            if self.velocity < -max_velocity:
                self.position[1] += -max_velocity
        
        self.verticies = np.column_stack((self.position + np.array([0,0]), self.position + np.array([0,self.y_dim]), self.position + np.array([self.x_dim,self.y_dim]), self.position + np.array([self.x_dim,0]), self.position + np.array([0,0])))

        
class Ball(Actor):
    def __init__(self, game_state):
        Actor.__init__(self, game_state)
        self.v_mag = self.game_state.v_mag        
        self.position_history = np.zeros((2, 5))
        self.velocity = self.game_state.v_mag*np.array([-np.sqrt(2)/2, -np.sqrt(2)/2])
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
            self.velocity[0] = -1*self.velocity[0]
            self.game_state.score_point(is_left_point = False)
        elif hit_right_edge:
            self.velocity[0] = -1*self.velocity[0]
            self.game_state.score_point(is_left_point = True)

        if hit_top_edge or hit_bottom_edge:
            self.velocity[1] = -1*self.velocity[1]
        
        if (left_striker.position[1] < self.position[1] < left_striker.position[1] + left_striker.y_dim) and (self.position[0] >= left_striker.position[0] + left_striker.x_dim) and (next_position[0] <= left_striker.position[0] + left_striker.x_dim):
            self.velocity[0] = -1*self.velocity[0]
        if (right_striker.position[1] < self.position[1] < right_striker.position[1] + right_striker.y_dim) and (self.position[0] <= right_striker.position[0]) and (next_position[0] >= right_striker.position[0]):
            self.velocity[0] = -1*self.velocity[0]
        return

    def move(self):
        self.position = self.position + self.velocity
        self.position_history = self.position_history[:, 1:]
        self.position_history = np.column_stack((self.position_history, self.position))
        return
    
    def draw(self):
        self.plot.set_offsets(self.position_history.T)
        self.plot.set_alpha([0.2, 0.4, 0.6, 0.8, 1])


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