from config import config
import time

imu_weight = 0.000045
def run_fusion():
    camera_reading = 0
    while 1:
        if not config.imu.empty():
            imu_reading = config.imu.get_nowait()
            position_change = (imu_reading[0] * imu_weight, imu_reading[2] * imu_weight)
            previous_reading = camera_reading
            camera_reading = config.camera.get_nowait()
            camera_reading = fuse_data(camera_reading, position_change)
            if camera_reading != previous_reading:
                config.shared.put(camera_reading)
        elif not config.camera.empty():
            previous_reading = camera_reading
            camera_reading = config.camera.get_nowait()
            if camera_reading != previous_reading:
                config.shared.put(camera_reading)

        time.sleep(0.01)
            
# Acc simulates velocity
def fuse_data(camera_position, position_change):
    x, y = camera_position
    deltaX, deltaY = position_change
    new_x = x + deltaX
    new_y = y + deltaY
    return new_x, new_y
    