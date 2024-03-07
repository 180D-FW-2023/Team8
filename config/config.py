import queue

# Queues initialized for passing data between code running in different threads
# Because the queues are essentially global

shared = queue.Queue()
camera = queue.Queue()
imu = queue.Queue()

# Global variables

threshold = ((40, 60, 20), (100, 255, 198))
state_signals = {'CAL_SIG' : 0, 'BEGIN_CAL_SIG': 0, 'GAME_SIG' : 0}
