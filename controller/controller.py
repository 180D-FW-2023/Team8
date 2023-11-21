from threading import Thread
import subprocess
import time
import os

data_writer_test_path = os.path.join("..", "game_state", "python", "data_writer_test.py")
update_state_path = os.path.join("..", "game_state", "python", "update_state.py")

data_writer_test = subprocess.Popen(['python', data_writer_test_path])
update_state = subprocess.Popen(['python', update_state_path])

time.sleep(15)
data_writer_test.kill()
update_state.kill()