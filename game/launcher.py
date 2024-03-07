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
        self.latest_reading = (-1,-1)
        self.settings_data = [0,0,0] 
        self.diff = 0

        return
    def display_to_screen(self, path):
        path = os.path.join('game', 'assets', path)
        self.img = pygame.transform.scale(pygame.image.load(path), (self.x_res, self.y_res))
        rect = self.img.get_rect()
        rect.center = (self.x_res/2, self.y_res/2)
        self.screen.blit(self.img, rect)
        pygame.display.flip()

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

        path = os.path.join('game', 'assets', 'title.png')
        self.img = pygame.transform.scale(pygame.image.load(path), (self.x_res, self.y_res))
        rect = self.img.get_rect()
        rect.center = (self.x_res/2, self.y_res/2)
        self.screen.blit(self.img, rect)
        pygame.display.flip()

        while True:
            self.display_to_screen('title.png')
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        self.countdown()
                        return
                    elif keys[pygame.K_1]:
                        self.calibrate()
                    elif keys[pygame.K_2]:
                        self.settings()
            time.sleep(1 / self.frame_rate)

    def settings(self):
        path = os.path.join('game', 'assets', 'settings', 'settings_' + ''.join(map(str, self.settings_data)) + '.png')
        self.img = pygame.transform.scale(pygame.image.load(path), (self.x_res, self.y_res))
        rect = self.img.get_rect()
        rect.center = (self.x_res/2, self.y_res/2)
        self.screen.blit(self.img, rect)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_1]:
                        self.settings_data[0] = 1 - self.settings_data[0]
                        self.display_to_screen(os.path.join('settings', 'settings_' + ''.join(map(str, self.settings_data))) + '.png')
                    elif keys[pygame.K_2]:
                        self.settings_data[1] = 1 - self.settings_data[1]
                        self.display_to_screen(os.path.join('settings', 'settings_' + ''.join(map(str, self.settings_data))) + '.png')
                    elif keys[pygame.K_3]:
                        self.settings_data[2] = 1 - self.settings_data[2]
                        self.diff = self.settings_data[2]
                        self.display_to_screen(os.path.join('settings', 'settings_' + ''.join(map(str, self.settings_data))) + '.png')
                    elif keys[pygame.K_ESCAPE]:
                        return
            time.sleep(1 / self.frame_rate)

    def end_screen(self, win = True):
        end_screens = ['win.png', 'lose.png']
        self.display_to_screen(end_screens[int(win)])

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE] or keys[pygame.K_RETURN] or keys[pygame.K_ESCAPE]:
                        return
            time.sleep(1 / self.frame_rate)
        return
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

        path = os.path.join('game', 'assets', 'diff.png')
        self.img = pygame.transform.scale(pygame.image.load(path), (self.x_res, self.y_res))
        rect = self.img.get_rect()
        rect.center = (self.x_res/2, self.y_res/2)
        self.screen.blit(self.img, rect)

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

        path = os.path.join('game', 'assets', 'ready.png')
        self.img = pygame.transform.scale(pygame.image.load(path), (self.x_res, self.y_res))
        rect = self.img.get_rect()
        rect.center = (self.x_res/2, self.y_res/2)
        self.screen.blit(self.img, rect)

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
    
    def begin_calibration(self):
        path = os.path.join('game', 'assets', 'ready.png')
        self.img = pygame.transform.scale(pygame.image.load(path), (self.x_res, self.y_res))
        rect = self.img.get_rect()
        rect.center = (self.x_res/2, self.y_res/2)
        self.screen.blit(self.img, rect)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE]:
                        self.calibrate()
                        return                   
            time.sleep(1 / self.frame_rate)
    
    def calibrate(self):
        config.state_signals['CAL_SIG'] = 1

        self.latest_reading = (-1,-1)

        cal_rect = pygame.Rect(0, 0, self.x_res*0.9, self.y_res*0.2)
        cal_rect.center = (self.x_res/2, 0.6*self.y_res)

        instr_text = self.instr_font.render('Please center the striker at the red dot.', True, 'white')

        while True:
            self.screen.fill('black')
            self.screen.blit(instr_text, instr_text.get_rect(center=(self.x_res/2, 0.3*self.y_res)))
            pygame.draw.rect(self.screen, 'white', cal_rect, width=int(self.x_res/150))

            if not config.shared.empty():
                self.latest_reading = config.shared.get_nowait()
            loc_x = 0.9*self.x_res*1/2*(1+self.latest_reading[0])
            loc_y = 0.7*self.y_res - 0.1*self.y_res*(1+self.latest_reading[1])
            pygame.draw.circle(self.screen, 'white', (loc_x, loc_y), self.x_res/35)
            pygame.draw.circle(self.screen, 'red', (self.x_res/2, 0.6*self.y_res), self.x_res/100)
            if np.linalg.norm((loc_x-self.x_res/2, loc_y-0.6*self.y_res)) < self.x_res/100:
                self.screen.fill('black')
                pygame.draw.rect(self.screen, 'white', cal_rect, width=int(self.x_res/150))
                pygame.draw.circle(self.screen, 'white', (loc_x, loc_y), self.x_res/35)
                pygame.draw.circle(self.screen, 'red', (self.x_res/2, 0.6*self.y_res), self.x_res/100)

                instr_text = self.instr_font.render('Calibrating...', True, 'white')
                self.screen.blit(instr_text, instr_text.get_rect(center=(self.x_res/2, 0.3*self.y_res)))
                pygame.display.flip()
                config.state_signals['CAL_SIG'] = 0
                config.state_signals['BEGIN_CAL_SIG'] = 1
                time.sleep(3)
                config.state_signals['BEGIN_CAL_SIG'] = 0
                return
            pygame.display.flip()
            time.sleep(1 / self.frame_rate)




        
        

        



        
