import threading
from threading import Thread
import subprocess
import time
import os
import queue
from game_state.python import update_state as u
import traceback
import cv2 as cv # could be cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim
import matplotlib.patches as patches
import time

# Part 1: Sensor data

file_path = os.path.join("..", "input_output", "sensor_data.csv")
dir_path = os.path.dirname(__file__)
os.chdir(dir_path)
full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
print(file_path)
print(os.getcwd())
print(full_path)
flag = 0
shared = queue.Queue()

def CaptureDisc():
    # I was running into an issue where the countours object (which is an array of arrays I think) was
    # initialized as empty on the first run through, or atleast the compiler believed it to be. So, the
    # purpose of the flag is to halt the cnt = contours[i] code until contours is correctly populated

    flag = 0
    cap = cv.VideoCapture(1)
    while(1):
        # Standard setup for OpenCV video processing
        _, frame = cap.read()
        height, width, _ = frame.shape
        #print(width) <- deprecated code to tell the size of video output
        # HSV gives better thresholding results, so below is the code to convert to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_green = np.array([40,51,51])
        upper_green = np.array([85,230,153])
        # Threshold the HSV image to get only green colors, threshold values were received from the max
        # and min observed values from an online color picker, with a sample image of the target object
        mask = cv.inRange(hsv, lower_green, upper_green)
        blur = cv.medianBlur(mask,5)
        # median blur to remove salt and pepper noise
        blur2 = cv.blur(blur,(20,20))
        # standard blur appears to be sufficient for our case. 20,20 was chosen experimentally
        edges = cv.Canny(blur, 100, 200)
        contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # This is a doozy. Basically, if contours is populated correctly
        # (which is what flag == 1 and len(contours)>1 is supposed to guarantee)
        # we initialize a set of placeholder variables, whose purpose is to basically
        # identify which bounding box from a specific entry of contours is the largest.
        # Upon finding a w_temp and h_temp larger than the previously recorded maximums
        # we save the i that these values were recorded at, and update the new maxes.
        # This could possibly be made better using the area function in OpenCV?
        # Basically this doesn't account for when the box becomes shorter but wider, or inverse.
        if flag == 1 and len(contours) > 0:
            w_max=0
            h_max = 0
            holder = 0
            for i in range(len(contours)):
                cnt = contours[i]
                x_temp,y_temp,w_temp,h_temp = cv.boundingRect(cnt)
                if w_temp >= w_max and h_temp >= h_max:
                    w_max = w_temp
                    h_max = h_temp
                    holder = i
            cnt = contours[holder]
            #cnt = contours[len(contours)-1] <- I swear to god I have no idea what I was testing with this,
            # but maybe I was cooking so I'll leave it.
            x,y,w,h = cv.boundingRect(cnt)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            centroidx = x+(w//2)
            centroidy = y+(h//2)
            cv.circle(frame, (centroidx, centroidy), 5, (0,0,255), -1)
            scaled_centroidx = ((centroidx/(width//2))-1)
            print(scaled_centroidx)
            #print(x , y, w, h)
            shared.put(scaled_centroidx)
            """
            //  with open(full_path, 'w') as file:
                file.write(str(scaled_centroidx))
                file.close()
                
            """

        cv.imshow('frame',frame)
        cv.imshow('mask',mask)
        cv.imshow('blur',blur)
        cv.imshow('blur2', blur2)
        cv.imshow('edges', edges)
        #cv.imshow('res',res)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
        if flag == 0:
            print("here")
            flag = 1
    cv.destroyAllWindows()


class GameState:
    def __init__(self, ball_velocity):
        # Set constants
        resolution = 700000
        self.x_max = 1 * resolution
        self.y_max = 4 / 7 * resolution
        self.v_mag = ball_velocity * self.x_max

        # Setup figure and axes
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal")
        self.ax.set_xlim(0, self.x_max)
        self.ax.set_ylim(0, self.y_max)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        # Draw Scene
        center_line = np.array([[self.x_max / 2, self.x_max / 2], [0, self.y_max]])
        center_circle = patches.Circle((self.x_max / 2, self.y_max / 2), radius=self.x_max / 10, edgecolor='gray',
                                       fill=False, linewidth=1, zorder=1)
        self.ax.add_patch(center_circle)
        self.ax.plot(center_line[0, :], center_line[1, :], color='gray', linewidth=1, zorder=1)

        # Create actors
        self.ball = Ball(self)
        self.left_striker = Striker(self, is_left_striker=True, inertia=0)
        self.right_striker = StrikerCPU(self, is_left_striker=False, inertia=0.95)
        self.score = [0, 0]
        return

    def update_state(self, left_striker_loc, right_striker_loc):
        # Move actors
        self.ball.bounce_ball()
        self.ball.move()
        self.left_striker.move(left_striker_loc)
        self.right_striker.move(right_striker_loc)

        # Update text
        self.ax.set_title('SCORE\n' + str(self.score[0]) + ' : ' + str(self.score[1]))

    def score_point(self, is_left_point):
        self.score[is_left_point] += 1
        self.ball.position = np.array([self.x_max / 2, self.y_max / 2])
        return
        if is_left_point:
            self.ball.position = self.left_striker.position
        else:
            self.ball.position = self.right_striker.position

    def refresh_display(self):
        # Draw actor plots
        self.ball.draw()
        self.left_striker.draw()
        self.right_striker.draw()


# Base class for actors
class Actor:
    def __init__(self, game_state):
        self.game_state = game_state
        self.x_max = game_state.x_max
        self.y_max = game_state.y_max
        self.position = np.array([0, 0])

    def move(self):
        pass


class Striker(Actor):
    def __init__(self, game_state, is_left_striker, inertia):
        Actor.__init__(self, game_state)
        # Define constants
        self.x_dim = self.game_state.x_max / 100
        self.y_dim = self.game_state.y_max / 5
        self.inertia = inertia
        edge_offset = 1 / 20

        # Create plot
        if is_left_striker:
            x_pos = self.game_state.x_max * edge_offset
            striker_color = 'blue'
        else:
            x_pos = self.game_state.x_max * (1 - edge_offset)
            striker_color = 'green'
        self.plot, = self.game_state.ax.plot([], [], color=striker_color)

        self.position = np.array([x_pos, 0])
        self.velocity = 0

    def move(self, loc):
        inertia = self.inertia * 0
        previous_pos = self.position[1]
        self.position[1] = (inertia) * self.position[1] + (1 - inertia) * (loc + 1) / 2 * (self.y_max - self.y_dim)
        self.velocity = self.position[1] - previous_pos
        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))

    def draw(self):
        self.plot.set_data(self.verticies)


class StrikerCPU(Striker):
    def move(self, loc):
        max_velocity = 1 / 100 * self.game_state.y_max
        ball_loc = self.game_state.ball.position[1] - self.y_dim / 2
        previous_pos = self.position[1]
        inertia = self.inertia

        next_position = (inertia) * self.position[1] + (1 - inertia) * (ball_loc)

        is_in_bounds = (next_position + self.y_dim < self.game_state.y_max) and (next_position > 0)

        self.velocity = next_position - previous_pos

        if is_in_bounds:
            if np.abs(self.velocity) < max_velocity:
                self.position[1] = next_position
            if self.velocity > max_velocity:
                self.position[1] += max_velocity
            if self.velocity < -max_velocity:
                self.position[1] += -max_velocity

        self.verticies = np.column_stack((self.position + np.array([0, 0]), self.position + np.array([0, self.y_dim]),
                                          self.position + np.array([self.x_dim, self.y_dim]),
                                          self.position + np.array([self.x_dim, 0]), self.position + np.array([0, 0])))


class Ball(Actor):
    def __init__(self, game_state):
        Actor.__init__(self, game_state)
        self.v_mag = self.game_state.v_mag
        self.position_history = np.zeros((2, 5))
        self.velocity = self.game_state.v_mag * np.array([-np.sqrt(2) / 2, -np.sqrt(2) / 2])
        self.plot = self.game_state.ax.scatter([], [], color='red')
        self.position = np.array([self.game_state.x_max / 2, self.game_state.y_max / 2])

    def bounce_ball(self):
        next_position = self.position + self.velocity
        left_striker = self.game_state.left_striker
        right_striker = self.game_state.right_striker

        hit_left_edge = next_position[0] >= self.x_max - 1
        hit_right_edge = next_position[0] <= 0
        hit_top_edge = next_position[1] >= self.y_max - 1
        hit_bottom_edge = next_position[1] <= 0

        if hit_left_edge:
            self.velocity[0] = -1 * self.velocity[0]
            self.game_state.score_point(is_left_point=False)
        elif hit_right_edge:
            self.velocity[0] = -1 * self.velocity[0]
            self.game_state.score_point(is_left_point=True)

        if hit_top_edge or hit_bottom_edge:
            self.velocity[1] = -1 * self.velocity[1]

        if (left_striker.position[1] < self.position[1] < left_striker.position[1] + left_striker.y_dim) and (
                self.position[0] >= left_striker.position[0] + left_striker.x_dim) and (
                next_position[0] <= left_striker.position[0] + left_striker.x_dim):
            self.velocity[0] = -1 * self.velocity[0]
        if (right_striker.position[1] < self.position[1] < right_striker.position[1] + right_striker.y_dim) and (
                self.position[0] <= right_striker.position[0]) and (next_position[0] >= right_striker.position[0]):
            self.velocity[0] = -1 * self.velocity[0]
        return

    def move(self):
        self.position = self.position + self.velocity
        self.position_history = self.position_history[:, 1:]
        self.position_history = np.column_stack((self.position_history, self.position))
        return

    def draw(self):
        self.plot.set_offsets(self.position_history.T)
        self.plot.set_alpha([0.2, 0.4, 0.6, 0.8, 1])


initial = 0.5
frame_rate = 120 * 2  # frames per second
ball_velocity = 3  # proportion of board x max per second
# Initialize game state object
game_state = GameState(ball_velocity / frame_rate)
ani = anim.FuncAnimation

def UpdateFunc():
    global game_state
    global ani
    game_state = GameState(ball_velocity / frame_rate)
    ani = anim.FuncAnimation(game_state.fig, update, frames=list(np.linspace(0, 2)), blit=False, interval=1)
    # ani.save('game_state.gif', writer="pillow writer")
    plt.show()

left_striker_loc = initial  # 1
latest_reading = initial  # 2
right_striker_loc = 0

def update(frame):

    global left_striker_loc, latest_reading, right_striker_loc
    # update(position, velocity, game_board)
    global game_state
    global latest_reading
    if not shared.empty():
        latest_reading = shared.get_nowait()
    left_striker_loc = latest_reading
    game_state.update_state(left_striker_loc, right_striker_loc)
    game_state.refresh_display()
    time.sleep(1 / frame_rate)
    return game_state.ax

def run_threads():

    # Queue objects in Python are thread-safe
    """
    thread1 = Thread(target=test1)
    thread2 = Thread(target=test2)
    :return:
    """

    thread1 = Thread(target=u.UpdateFunc)
    thread2 = Thread(target=CaptureDisc)

    # Begin threads
    thread1.start()
    thread2.start()

    # End threads
    thread1.join()
    thread2.join()

def run_subprocesses():
    #data_writer_test_path = os.path.join("..", "game_state", "python", "data_writer_test.py")
    update_state_path = os.path.join("..", "game_state", "python", "update_state.py")
    striker_tracking_path = os.path.join("..", "camera", "Green_Striker_Tracking.py")

    #data_writer_test = subprocess.Popen(['python', data_writer_test_path])
    striker_tracking = subprocess.Popen(['python', striker_tracking_path])
    update_state = subprocess.Popen(['python', update_state_path])

    time.sleep(15)
    update_state.kill()
    striker_tracking.kill()
    return


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


def main():

    global game_state
    global ani
    global left_striker_loc, latest_reading, right_striker_loc
    # update(position, velocity, game_board)
    global latest_reading
    game_state = GameState(ball_velocity / frame_rate)
    ani = anim.FuncAnimation(game_state.fig, update, frames=list(np.linspace(0, 2)), blit=False, interval=1)
    # ani.save('game_state.gif', writer="pillow writer")
    plt.show()

    # Start the threads
    camera_thread = threading.Thread(target=CaptureDisc)
    camera_thread.start()

    while True:
        # Update game state and refresh display
        # if not shared.empty():
            #
            #return game_state.ax

        if not shared.empty():
            latest_reading = shared.get_nowait()
            left_striker_loc = latest_reading
            game_state.update_state(left_striker_loc, right_striker_loc)
            game_state.refresh_display()
        time.sleep(1 / frame_rate)
        # Redraw the Matplotlib figure
        plt.pause(0.01)

    camera_thread.join()


if __name__ == "__main__":
    main()