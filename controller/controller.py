from threading import Thread
import subprocess
import time
import os
import queue
from game_state.python import update_state as u
import traceback


def run_subprocesses():
    #data_writer_test_path = os.path.join("..", "game_state", "python", "data_writer_test.py")
    update_state_path = os.path.join("..", "game_state", "python", "update_state.py")
    striker_tracking_path = os.path.join("..", "camera", "Green_Striker_Tracking.py")

    #data_writer_test = subprocess.Popen(['python', data_writer_test_path])
    striker_tracking = subprocess.Popen(['python', striker_tracking_path])
    update_state = subprocess.Popen(['python', update_state_path])

    time.sleep(15)
    #data_writer_test.kill()
    update_state.kill()
    striker_tracking.kill()
    return

shared = queue.Queue()

def test1():
    for i in range(-10,10,1):
        data = f"Data: {i/10.0}"
        shared.put(data)
        time.sleep(3)

def test2():
    count = 0
    while True:
        if shared.empty():
            time.sleep(0.1)
            count += 1
            if count > 1000:
                print("complete")
                break
        else:
            data = shared.get()
            shared.task_done()
            count = 0
            try:
                f = float(data.split(": ")[1])
                x = u.Update_initial(f)
                print(f"New value: {x}")
            except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
            # Call update_state


def run_threads():

    # Queue objects in Python are thread-safe
    thread1 = Thread(target=test1)
    thread2 = Thread(target=test2)
    thread3 = Thread(target=u.UpdateFunc())


    # Begin threads
    thread1.start()
    thread2.start()
    thread3.start()

    # End threads
    thread1.join()
    thread2.join()
    thread3.join()


