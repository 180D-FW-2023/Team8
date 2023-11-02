import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim
import time

class GameState:
    def __init__(self):
        self.x_max = 5000
        self.y_max = 4000
        self.v_mag = 50
        
        self.fig, self.ax = plt.subplots()
        self.display, = self.ax.plot([], [], 'ro')
        self.ax.set_xlim(0,self.x_max)
        self.ax.set_ylim(0,self.y_max)
        
        self.ball = Ball(self.x_max, self.y_max, self.v_mag)
        self.game_board = np.zeros((self.x_max, self.y_max))
        return

    def update_state(self):
        self.ball.bounce_ball()
        self.ball.move_ball()

        self.game_board = np.zeros((self.x_max, self.y_max))
        self.game_board[self.ball.ball_position[0]][self.ball.ball_position[1]] = 1
    
    def refresh_display(self):
        self.display.set_data(self.ball.ball_position_history)
        self.display.set_color(np.array([1, .5, .25, .125, .0625]))

class Actor:
    def __init__(self, x_max, y_max):
        self.x_max = x_max
        self.y_max = y_max

class Striker(Actor):
    def __init__(self, x_max, y_max):
        Actor.__init__(self, x_max, y_max)        
 
class Ball(Actor):
    def __init__(self, x_max, y_max, v_mag):
        Actor.__init__(self, x_max, y_max)
        self.v_mag = v_mag        
        self.ball_position = np.array([2, 2])
        self.ball_position_history = np.zeros((2, 5))
        self.ball_velocity = self.v_mag*np.array([-1, -1])

    def bounce_ball(self):
        next_ball_position = self.ball_position + self.ball_velocity
        if next_ball_position[0] >= self.x_max-1 or next_ball_position[0] <= 0:
            self.ball_velocity[0] = -1*self.ball_velocity[0]
        if next_ball_position[1] >= self.y_max-1 or next_ball_position[1] <= 0:
            self.ball_velocity[1] = -1*self.ball_velocity[1]
        return

    def move_ball(self):
        self.ball_position = self.ball_position + self.ball_velocity
        self.ball_position_history = self.ball_position_history[:, 1:]
        self.ball_position_history = np.column_stack((self.ball_position_history, self.ball_position))
        return
        

game_state = GameState()

def update(frame):
    # update(ball_position, ball_velocity, game_board)
    global game_state
    
    game_state.update_state()
    game_state.refresh_display()

    #time.sleep(1)
    #print(game_board)
    return game_state.display

ani = anim.FuncAnimation(game_state.fig, update, frames=np.linspace(0, 2*np.pi, 128), blit=False, interval = 1)
plt.show()