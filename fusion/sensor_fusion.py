from config import config
import time

def run_fusion():
    camera_reading = 0
    while 1:
        if not config.camera.empty():
            previous_reading = camera_reading
            camera_reading = config.camera.get_nowait()
            if camera_reading != previous_reading:
                config.shared.put(camera_reading)
        if not config.imu.empty():
            imu_reading = config.imu.get_nowait()
        time.sleep(0.01)
            
                
    