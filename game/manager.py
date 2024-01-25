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


class Manager:
    def __init__(self):
        self.initial = 0.5
        self.frame_rate = 120 * 2  # frames per second
        self.ball_velocity = 3  # proportion of board x max per second
        # Initialize game state object

        self.game_state = game_details.GameState(self.ball_velocity / self.frame_rate)
        self.latest_reading = 0
        self.right_striker_loc = 0
    
    def frame_update(self, frame):
        if not config.shared.empty():
            self.latest_reading = config.shared.get_nowait()
        left_striker_loc = self.latest_reading
        self.game_state.update_state(left_striker_loc, self.right_striker_loc)
        self.game_state.refresh_display()
        time.sleep(1 / self.frame_rate)
        return self.game_state.ax
    
    def game_loop(self):
        ani = anim.FuncAnimation(self.game_state.fig, self.frame_update, frames=list(np.linspace(0, 2)), blit=False, interval=1)
        return
    
    def open_window(self):
        plt.show()