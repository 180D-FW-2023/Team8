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
    manager_instance.game_loop()


if __name__ == "__main__":
    main()