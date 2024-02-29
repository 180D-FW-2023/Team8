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
import pygame
from disc import capture
from game import game_details
from config import config
from game import launcher


class Manager:
    def __init__(self):
        self.initial = 0.5
        self.frame_rate = 120 * 2  # frames per second
        self.ball_velocity = 1  # proportion of board x max per second
        self.resolution = 850
        self.aspect_ratio = 4/7
        self.diff = -1
        return

    def frame_update(self):
        if not config.shared.empty():
            self.latest_reading = config.shared.get_nowait()
        left_striker_loc = self.latest_reading
        self.game_state.update_state(left_striker_loc, self.right_striker_loc)
        self.game_state.refresh_display()
        time.sleep(1 / self.frame_rate)
        return
    
    def game_loop(self):
        # Initialize game state object
        self.game_state = game_details.GameState(self.ball_velocity / self.frame_rate, self.resolution, self.aspect_ratio, self.diff, self.screen)
        self.latest_reading = [0,0]
        self.right_striker_loc = 0

        while 1:
            self.frame_update()
            if self.game_state.score[0] == 11:
                self.launcher.end_screen(False)
                exit()
            elif self.game_state.score[1] == 11:
                self.launcher.end_screen(True)
                exit()
        exit()
    
    def startup(self):
        x_res = self.resolution * self.aspect_ratio
        y_res = self.resolution
        pygame.init()
        self.screen = pygame.display.set_mode((x_res, y_res))
        self.screen.fill("black")
        pygame.font.init()

        self.launcher = launcher.Launcher(self.frame_rate, self.resolution, self.aspect_ratio, self.screen)
        
        self.launcher.open_launcher()
        self.diff = self.launcher.diff
        return
        
    def open_window(self):
        plt.show()