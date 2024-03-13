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
    config.camera.put_nowait((0,0))
    config.imu = queue.Queue()
    config.shared = queue.Queue()
    config.threshold = ((40, 60, 20), (100, 255, 198))
    config.state_signals = {'CAL_SIG' : 0, 'BEGIN_CAL_SIG': 0, 'GAME_SIG' : 0}

    
    # Start the threads
    camera_thread = threading.Thread(target=capture.initialize_camera)
    camera_thread.start()
 

    imu_thread = threading.Thread(target=imu_reading.run_imu_sub)
    imu_thread.start()

    fusion_thread = threading.Thread(target=sensor_fusion.run_fusion)
    fusion_thread.start()
    
    manager_instance = manager.Manager()
    manager_instance.startup()
    manager_instance.game_loop()

    imu_thread.join()
    camera_thread.join()
    fusion_thread.join()

    exit()


if __name__ == "__main__":
    main()