import cv2 as cv # could be cv2
import numpy as np
import os
from config import config
import time

flag = 0

def CaptureDisc():

    global flag
    flag = 0
    cap = cv.VideoCapture(0)

    while (1):
        # Standard setup for OpenCV video processing
        _, frame = cap.read()
        height, width, _ = frame.shape
        # print(width) <- deprecated code to tell the size of video output
        # HSV gives better thresholding results, so below is the code to convert to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_green = np.array([40,51,51])
        upper_green = np.array([85,230,153])
        # Values above are for my laptop camera, values below are for USB camera (for project)
        #lower_green = np.array([33, 16, 126])
        #upper_green = np.array([67, 107, 199])
        # Threshold the HSV image to get only green colors, threshold values were received from the max
        # and min observed values from an online color picker, with a  sample image of the target object
        mask = cv.inRange(hsv, lower_green, upper_green)
        blur = cv.medianBlur(mask, 69)
        # median blur to remove salt and pepper noise
        blur2 = cv.blur(blur, (20, 20))
        # standard blur appears to be sufficient for our case. 20,20 was chosen experimentally
        edges = cv.Canny(blur, 100, 200)
        contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # This is a doozy. Basically, if contours is populated correctly
        # (which is what flag == 1 and len(contours)>1 is supposed to guarantee)
        # we initialize a set of placeholder variables, whose purpose is to basically
        # identify which bounding box from a specific entry of contours is the largest.
        # Upon finding a w_temp and h_temp larger than the previously recorded maximums
        # we save the i that these values were recorded at, and update the new maxes.
        # This could possibly be made better using the area function in OpenCV?
        # Basically this doesn't account for when the box becomes shorter but wider, or inverse.
        if flag == 1 and len(contours) > 0:
            # w_max=0
            # h_max = 0
            # holder = 0
            # for i in range(len(contours)):
            #    cnt = contours[i]
            #    x_temp,y_temp,w_temp,h_temp = cv.boundingRect(cnt)
            #    if w_temp >= w_max and h_temp >= h_max:
            #        w_max = w_temp
            #        h_max = h_temp
            #        holder = i
            # cnt = contours[holder]
            # See above comment, found a better way to do this, see below. Accomplishes same task,
            # less bloat. Possibly more performant.
            cnt = max(contours, key=cv.contourArea)
            # cnt = contours[len(contours)-1] <- I swear to god I have no idea what I was testing with this,
            # but maybe I was cooking so I'll leave it.
            x, y, w, h = cv.boundingRect(cnt)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.line(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # I could write my own pythagorean theorem program, but for now, importing math for hypot is fine.
            # diagonal = math.hypot(w,h)
            centroidx = x + (w // 2)
            centroidy = y + (h // 2)
            cv.circle(frame, (centroidx, centroidy), 5, (0, 0, 255), -1)
            scaled_centroidx = ((centroidx / (width // 2)) - 1)
            #print("x:", scaled_centroidx)
            distance_estimate = 460.7 * 7.1 / w
            #print("y:", distance_estimate)
            scaled_centroidx *= -1
            print(scaled_centroidx)
            config.shared.put(scaled_centroidx)
        cv.imshow('frame', frame)
        cv.imshow('mask', mask)
        #cv.imshow('blur', blur)
        cv.imshow('blur2', blur2)
        #cv.imshow('edges', edges)
        #cv.imshow('res',res)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
        if flag == 0:
            flag = 1
        #time.sleep(0.5)
    cv.destroyAllWindows()