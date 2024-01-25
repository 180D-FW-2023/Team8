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
from game import manager
from game import launcher
from config import config

def main(self=None):

    config.shared = queue.Queue()

    launcher_instance = launcher.Launcher()

    manager_instance = manager.Manager()
    manager_instance.game_loop()

    # Start the threads
    camera_thread = threading.Thread(target=capture.CaptureDisc)
    camera_thread.start()

    manager_instance.open_window()

    while True:
        '''
        #if not config.shared.empty():
        #    latest_reading = config.shared.get_nowait()
        #game_state.refresh_display()
        
        '''

        time.sleep(1)

    camera_thread.join()


if __name__ == "__main__":
    main()