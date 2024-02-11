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


class Manager:
    def __init__(self):
        self.initial = 0.5
        self.frame_rate = 120 * 2  # frames per second
        self.ball_velocity = 1  # proportion of board x max per second
        self.resolution = 700
        self.aspect_ratio = 4/7
        self.diff = -1

    def frame_update(self, frame):
        if not config.shared.empty():
            self.latest_reading = config.shared.get_nowait()
        left_striker_loc = self.latest_reading
        self.game_state.update_state(left_striker_loc, self.right_striker_loc)
        self.game_state.refresh_display()
        time.sleep(1 / self.frame_rate)
        return #self.game_state.ax
    
    def game_loop(self):
        # Initialize game state object
        self.game_state = game_details.GameState(self.ball_velocity / self.frame_rate, self.resolution, self.aspect_ratio, self.diff)
        self.latest_reading = [0,0]
        self.right_striker_loc = 0

        while 1:
            self.frame_update(1)
        #ani = anim.FuncAnimation(self.game_state.fig, self.frame_update, frames=list(np.linspace(0, 2)), blit=False, interval=1)
        return 1
    
    def startup(self):
        x_res = self.resolution * self.aspect_ratio
        y_res = self.resolution
        pygame.init()
        screen = pygame.display.set_mode((x_res, y_res))
        screen.fill("black")
        pygame.font.init()

        title_font = pygame.font.Font(None, 50)
        instr_font = pygame.font.Font(None, 36)
        option1_font = pygame.font.Font(None, 36)
        option2_font = pygame.font.Font(None, 36)

        title_text = title_font.render('VIRTUAL AIR HOCKEY', True, 'white')
        screen.blit(title_text, title_text.get_rect(center=(x_res/2, 0.3*y_res)))

        instr_text = instr_font.render('Select the opponent difficulty:', True, 'white')
        screen.blit(instr_text, instr_text.get_rect(center=(x_res/2, 0.5*y_res)))

        option1_text = option1_font.render('Easy :D [1]', True, 'white')
        screen.blit(option1_text, option1_text.get_rect(center=(x_res/2, 0.6*y_res)))

        option2_text = option2_font.render('Extreme >:) [2]', True, 'red')
        screen.blit(option2_text, option2_text.get_rect(center=(x_res/2, 0.7*y_res)))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_1]:
                        self.diff = 0
                        break
                    elif keys[pygame.K_2]:
                        self.diff = 1
                        break
            if self.diff != -1:
                break
            time.sleep(1 / self.frame_rate)
                
        screen.fill("black")

        title_text = title_font.render('VIRTUAL AIR HOCKEY', True, 'white')
        screen.blit(title_text, title_text.get_rect(center=(x_res/2, 0.3*y_res)))

        instr_text = instr_font.render('Press the space key to play!', True, 'white')
        screen.blit(instr_text, instr_text.get_rect(center=(x_res/2, 0.5*y_res)))

        option1_text = option1_font.render('PLAY', True, 'white')
        screen.blit(option1_text, option1_text.get_rect(center=(x_res/2, 0.6*y_res)))

        pygame.display.flip()

        start = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        start = True
            if start:
                break
                                    
            time.sleep(1 / self.frame_rate)
    
        for i in range(3):
            screen.fill('black')
            title_text = title_font.render(str(4-(i+1)), True, 'white')
            screen.blit(title_text, title_text.get_rect(center=(x_res/2, 0.5*y_res)))
            pygame.display.flip()
            time.sleep(1)
        return

    def open_window(self):
        plt.show()