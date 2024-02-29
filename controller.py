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
from fusion import sensor_fusion
from imu import imu_reading

def main(self=None):
    config.camera = queue.Queue()
    config.imu = queue.Queue()
    config.shared = queue.Queue()
    config.threshold = ((40, 60, 20), (100, 255, 198))

    
    # Start the threads
    camera_thread = threading.Thread(target=capture.CaptureDisc)
    camera_thread.start()


    imu_thread = threading.Thread(target=imu_reading.run_imu_sub)
    imu_thread.start()

    fusion_thread = threading.Thread(target=sensor_fusion.run_fusion)
    fusion_thread.start()
    
    manager_instance = manager.Manager()
    manager_instance.startup()

    #anim = manager_instance.game_loop()
    manager_instance.game_loop()
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