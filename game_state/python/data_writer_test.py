import matplotlib.pyplot as plt
import numpy as np
import os
import time

# Get sensor data file path
file_path = os.path.join("..", "..", "input_output", "sensor_data.csv")
dir_path = os.path.dirname(__file__)
os.chdir(dir_path)
full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))

# Create loc value and write to data file
velocity = 1/2 # proportion of board y max per second
period = 2/velocity # 2*y max covered every period
iters = 1000 # number of iterations in a period
iter_time = period/iters # time per interation

i = 0 
while True:
    # open data file for writing
    with open(full_path, 'w') as file: 
        loc = np.sin(2*np.pi*i*1/iters)
        file.write(str(loc))
        file.close()
    if i == iters:
        i = 0
    else:
        i += 1
    time.sleep(iter_time)

