import cv2 as cv # could be cv2
import numpy as np
import os
from config import config

flag = 0

def CaptureDisc():

    global flag
    flag = 0
    cap = cv.VideoCapture(1)
    while (1):
        _, frame = cap.read()
        height, width, _ = frame.shape
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_green = np.array([40, 51, 51])
        upper_green = np.array([85, 230, 153])
        mask = cv.inRange(hsv, lower_green, upper_green)
        blur = cv.medianBlur(mask, 5)
        blur2 = cv.blur(blur, (20, 20))
        edges = cv.Canny(blur, 100, 200)
        contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if flag == 1 and len(contours) > 0:
            w_max = 0
            h_max = 0
            holder = 0
            for i in range(len(contours)):
                cnt = contours[i]
                x_temp, y_temp, w_temp, h_temp = cv.boundingRect(cnt)
                if w_temp >= w_max and h_temp >= h_max:
                    w_max = w_temp
                    h_max = h_temp
                    holder = i
            cnt = contours[holder]
            x, y, w, h = cv.boundingRect(cnt)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            centroidx = x + (w // 2)
            centroidy = y + (h // 2)
            cv.circle(frame, (centroidx, centroidy), 5, (0, 0, 255), -1)
            scaled_centroidx = ((centroidx / (width // 2)) - 1)
            print(scaled_centroidx)
            config.shared.put(scaled_centroidx)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
        if flag == 0:
            print("here")
            flag = 1
    cv.destroyAllWindows()