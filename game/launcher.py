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
import pygame
import time


class Launcher:
    def __init__(self, frame_rate, resolution, aspect_ratio, screen):
        self.resolution = resolution
        self.aspect_ratio = aspect_ratio
        self.screen = screen
        self.x_res = self.resolution * self.aspect_ratio
        self.y_res = self.resolution
        self.frame_rate = frame_rate
        return
    
    def open_launcher(self):
        x_res = self.resolution * self.aspect_ratio
        y_res = self.resolution
        pygame.init()
        screen = pygame.display.set_mode((x_res, y_res))
        screen.fill("black")
        pygame.font.init()

        self.title_font = pygame.font.Font(None, 50)
        self.instr_font = pygame.font.Font(None, 36)
        self.option1_font = pygame.font.Font(None, 36)
        self.option2_font = pygame.font.Font(None, 36)
    
    def choose_difficulty(self):
        title_font = self.title_font
        instr_font = self.instr_font
        option1_font = self.option1_font
        option2_font = self.option2_font
        x_res = self.x_res
        y_res = self.y_res
        frame_rate = self.frame_rate
        screen = self.screen


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
                        return self.diff
                    elif keys[pygame.K_2]:
                        self.diff = 1
                        return self.diff
            time.sleep(1 / self.frame_rate)

    def play(self):  
        title_font = self.title_font
        instr_font = self.instr_font
        option1_font = self.option1_font
        option2_font = self.option2_font
        x_res = self.x_res
        y_res = self.y_res
        frame_rate = self.frame_rate
        screen = self.screen

        screen.fill("black")

        title_text = title_font.render('VIRTUAL AIR HOCKEY', True, 'white')
        screen.blit(title_text, title_text.get_rect(center=(x_res/2, 0.3*y_res)))

        instr_text = instr_font.render('Press the space key to play!', True, 'white')
        screen.blit(instr_text, instr_text.get_rect(center=(x_res/2, 0.5*y_res)))

        option1_text = option1_font.render('PLAY', True, 'white')
        screen.blit(option1_text, option1_text.get_rect(center=(x_res/2, 0.6*y_res)))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        return                   
            time.sleep(1 / self.frame_rate)
    
    def countdown(self):
        title_font = self.title_font
        instr_font = self.instr_font
        option1_font = self.option1_font
        option2_font = self.option2_font
        x_res = self.x_res
        y_res = self.y_res
        frame_rate = self.frame_rate
        screen = self.screen

        for i in range(3):
            screen.fill('black')
            title_text = title_font.render(str(4-(i+1)), True, 'white')
            screen.blit(title_text, title_text.get_rect(center=(x_res/2, 0.5*y_res)))
            pygame.display.flip()
            time.sleep(1)
        return