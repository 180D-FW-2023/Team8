import queue

shared = queue.Queue()
camera = queue.Queue()
imu = queue.Queue()
threshold = ((40, 60, 20), (100, 255, 198))
state_signals = {'CAL_SIG' : 0, 'BEGIN_CAL_SIG': 0, 'GAME_SIG' : 0}
