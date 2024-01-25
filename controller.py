import threading
from threading import Thread
import subprocess
import os
import queue
import traceback
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim
import time
from disc import capture
from game import game_details
from config import config


initial = 0.5
frame_rate = 120 * 2  # frames per second
ball_velocity = 3  # proportion of board x max per second
# Initialize game state object

#game_state = game_details.GameState(ball_velocity / frame_rate)
#ani = anim.FuncAnimation

def update(frame):

    global latest_reading, right_striker_loc
    # update(position, velocity, game_board)
    global game_state
    global latest_reading
    if not config.shared.empty():
        latest_reading = config.shared.get_nowait()
    left_striker_loc = latest_reading
    game_state.update_state(left_striker_loc, right_striker_loc)
    game_state.refresh_display()
    time.sleep(1 / frame_rate)
    return game_state.ax

def main(self=None):

    global game_state
    global ani

    config.shared = queue.Queue()

    global latest_reading, right_striker_loc
    # update(position, velocity, game_board)
    global latest_reading
    latest_reading = 0
    right_striker_loc = 0
    game_state = game_details.GameState(ball_velocity / frame_rate)
    ani = anim.FuncAnimation(game_state.fig, update, frames=list(np.linspace(0, 2)), blit=False, interval=1)
    plt.show()

    # Start the threads
    camera_thread = threading.Thread(target=capture.CaptureDisc)
    camera_thread.start()

    while True:
        '''
        #if not config.shared.empty():
        #    latest_reading = config.shared.get_nowait()
        #game_state.refresh_display()
        
        '''

        time.sleep(1 / frame_rate)
        # Redraw the Matplotlib figure
        plt.pause(0.01)

    camera_thread.join()


if __name__ == "__main__":
    main()