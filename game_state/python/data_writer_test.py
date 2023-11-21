import matplotlib.pyplot as plt
import numpy as np
import os
import time

file_path = "../../input_output/sensor_data.csv"
full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
i = 0
while True:
    with open(full_path, 'w') as file:
        loc = np.sin(2*np.pi*i/1000)
        file.write(str(loc))
        file.close()
    if i == 1000:
        i = 0
    else:
        i += 1
    time.sleep(0.01)
