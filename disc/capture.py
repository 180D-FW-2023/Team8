import cv2 as cv # could be cv2
import numpy as np
import os
from config import config
import matplotlib.pyplot as plt
import time
import math
import platform

flag = 0
weighted_moving_average_x = []
weighted_moving_average_y = []

def initialize_camera():
    if "macOS" in platform.platform():
        flip = -1
        camera = 1
    else:
        flip = 1
        camera = 2

    threshold = ((40, 60, 20), (100, 255, 198))
    while True:
        if config.state_signals['CAL_SIG'] == 1:
            CaptureDisc(threshold, flip, camera)
        if config.state_signals['BEGIN_CAL_SIG'] == 1:
            threshold = calibrate(camera, threshold)
        if config.state_signals['GAME_SIG'] == 1:
            CaptureDisc(threshold, flip, camera)
        time.sleep(0.01)
    return

def calibrate(camera, threshold):
    config.state_signals['THRESH'] = 0
    flag = 0
    # I was running into an issue where the countours object (which is an array of arrays I think) was 
    # initialized as empty on the first run through, or atleast the compiler believed it to be. So, the
    # purpose of the flag is to halt the cnt = contours[i] code until contours is correctly populated
    counter = 0
    total_count = 0
    MIN_MATCH_COUNT = 5
    lower_green = np.array([40,60,25])
    upper_green = np.array([100,255,198])
    cap = cv.VideoCapture(camera)
    while(1):
        if config.state_signals['BEGIN_CAL_SIG'] == 0:
            cv.destroyAllWindows()
            #print(threshold)
            return (np.array(threshold[0]), np.array(threshold[1]))
        # Standard setup for OpenCV video processing
        _, frame = cap.read()
        frame_Gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        height, width, _ = frame.shape
        # Threshold the HSV image to get only green colors, threshold values were received from the max 
        # and min observed values from an online color picker, with a  sample image of the target object
        mask = cv.inRange(frame_hsv, lower_green, upper_green)
        blur = cv.medianBlur(mask,29)
        # median blur to remove salt and pepper noise
        blur2 = cv.blur(blur,(20,20))
        # standard blur appears to be sufficient for our case. 20,20 was chosen experimentally
        edges = cv.Canny(blur, 100, 200)
        contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            cnt = max(contours, key = cv.contourArea)
            x,y,w,h = cv.boundingRect(cnt)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        path = os.path.join('disc', 'assets', 'ThresholdStriker.png')
        Extracted_Striker_Frame = cv.imread(path)
        Extracted_Striker_Frame_Gray = cv.cvtColor(Extracted_Striker_Frame, cv.COLOR_BGR2GRAY)
        # Initiate SIFT detector
        sift = cv.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(blur,None)
        kp2, des2 = sift.detectAndCompute(Extracted_Striker_Frame_Gray,None)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        # store all the good matches as per Lowe's ratio test.
        # We chose 0.7 experimentally, strict enough to only give good matches not too strict so that we get no matches.
        good = []
        for m,n in matches:
            if m.distance < 0.70*n.distance:
                good.append(m)
        if len(good)>=MIN_MATCH_COUNT:
            # Was running into an issue where lighting flare from camera startup was leading to incorrect behavior.
            # Requiring atleast one run through with the flag eliminated this issue.
            if flag == 1:
                print ("Good Threshold Found, Exiting", lower_green, upper_green)
                config.state_signals['THRESH'] = 1
                config.state_signals['BEGIN_CAL_SIG'] = 0
                config.state_signals['CAL_SIG'] = 0
                cv.destroyAllWindows()
                return(lower_green, upper_green)
                #exit()
        else:
            print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
        if counter >= 5:
            avg_hsv = cv.mean(frame_hsv, blur)
            #print(avg_hsv)
            #cv.imshow("masked frame", masked_frame)
            # This is the process that adjusts the thresholding based on the SIFT result. 
            # Basically, if less than 10% of the image is non-zero, we need to widen the threshold
            # If not, we make the threshold narrower, and skewed toward the average HSV value of the SIFT output image
            if cv.countNonZero(blur) <= 20736/3:
                if (avg_hsv[0]-lower_green[0]) < (upper_green[0] - avg_hsv[0]):
                    lower_green[0] = lower_green[0] - 5
                    #upper_green[0] = upper_green[0] - 5
                if (avg_hsv[0]-lower_green[0]) > (upper_green[0] - avg_hsv[0]):
                    #lower_green[0] = lower_green[0] + 5
                    upper_green[0] = upper_green[0] + 5
                if (avg_hsv[1]-lower_green[1]) < (upper_green[1] - avg_hsv[1]):
                    lower_green[1] = lower_green[1] - 5
                    #upper_green[1] = upper_green[1] - 5
                if (avg_hsv[1]-lower_green[1]) > (upper_green[1] - avg_hsv[1]):
                    #lower_green[1] = lower_green[1] + 5
                    upper_green[1] = upper_green[1] + 5
                if (avg_hsv[2]-lower_green[2]) < (upper_green[2] - avg_hsv[2]):
                    lower_green[2] = lower_green[2] - 5
                    #upper_green[2] = upper_green[2] - 5
                if (avg_hsv[2]-lower_green[2]) > (upper_green[2] - avg_hsv[2]):
                    #lower_green[2] = lower_green[2] + 5
                    upper_green[2] = upper_green[2] + 5
                #print("widening")
                counter = 0
            else:    
                if (avg_hsv[0]-lower_green[0]) < (upper_green[0] - avg_hsv[0]):
                    #lower_green[0] = lower_green[0] - 5
                    upper_green[0] = upper_green[0] - 5
                if (avg_hsv[0]-lower_green[0]) > (upper_green[0] - avg_hsv[0]):
                    lower_green[0] = lower_green[0] + 5
                    #upper_green[0] = upper_green[0] + 5
                if (avg_hsv[1]-lower_green[1]) < (upper_green[1] - avg_hsv[1]):
                    #lower_green[1] = lower_green[1] - 5
                    upper_green[1] = upper_green[1] - 5
                if (avg_hsv[1]-lower_green[1]) > (upper_green[1] - avg_hsv[1]):
                    lower_green[1] = lower_green[1] + 5
                    #upper_green[1] = upper_green[1] + 5
                if (avg_hsv[2]-lower_green[2]) < (upper_green[2] - avg_hsv[2]):
                    #lower_green[2] = lower_green[2] - 5
                    upper_green[2] = upper_green[2] - 5
                if (avg_hsv[2]-lower_green[2]) > (upper_green[2] - avg_hsv[2]):
                    lower_green[2] = lower_green[2] + 5
                    #upper_green[2] = upper_green[2] + 5
                #print("changing Thresholding: New Lower Green", lower_green , "New Upper Green", upper_green)
                counter = 0
        else:
            counter = counter+1
        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                    singlePointColor = None,
                    flags = 2)
        img3 = cv.drawMatches(blur,kp1,Extracted_Striker_Frame_Gray,kp2,good,None,**draw_params)
        img3_small = cv.resize(img3, (0, 0), fx = 0.5, fy = 0.5)
        #cv.imshow('matching',img3_small)
        #cv.imshow('frame',frame)
        #cv.imshow('Extractedstriker' , Extracted_Striker_Frame)
        #cv.imshow('mask',mask)
        #cv.imshow('blur',blur)
        #cv.imshow('blur2', blur2)
        total_count = total_count+1 
        #print(total_count) 
        # Safeguard against the positive feedback loop or runaway case. If the calibration runs too long, 
        # restart with the default values. 
        if total_count >= 70:
            lower_green = np.array([40,60,25])
            upper_green = np.array([100,255,198])
            total_count = 0
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
        if flag == 0:
            flag = 1
        #time.sleep(0.5)
    cv.destroyAllWindows()
    #return ((40, 60, 20), (100, 255, 198))

def CaptureDisc(threshold, flip, camera):

    flag = 0
    # I was running into an issue where the countours object (which is an array of arrays I think) was 
    # initialized as empty on the first run through, or atleast the compiler believed it to be. So, the
    # purpose of the flag is to halt the cnt = contours[i] code until contours is correctly populated
    cap = cv.VideoCapture(camera)
    while(1):
        if config.state_signals['CAL_SIG'] == 0 and config.state_signals['GAME_SIG'] == 0:
            cv.destroyAllWindows()
            return
        # Standard setup for OpenCV video processing
        _, frame = cap.read()
        frame = cv.flip(frame, 0)
        height, width, _ = frame.shape
        #print(width) <- deprecated code to tell the size of video output
        # HSV gives better thresholding results, so below is the code to convert to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # Grab the threshold values from the passed input from calibration. Default if calibration has not been run
        lower_green = threshold[0]
        upper_green = threshold[1]
        # Threshold the HSV image to get only green colors
        mask = cv.inRange(hsv, lower_green, upper_green)
        blur = cv.medianBlur(mask,23)
        # median blur to remove salt and pepper noise
        blur2 = cv.blur(blur,(20,20))
        # standard blur appears to be sufficient for our case. 20,20 was chosen experimentally
        # Helps to "homogenize" the striker image. 
        # Basically if its like missing a chunk from its center, this helps to make sure that doesn't 
        # get completely split into two seperate shapes for the purposes of cv.findcontours
        edges = cv.Canny(blur, 100, 200)
        contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # Tried with both blur2 and edges. blur2 results were generally better.
        #contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        # This is a doozy. Basically, if contours is populated correctly 
        # (which is what flag == 1 and len(contours)>1 is supposed to guarantee)
        # we initialize a set of placeholder variables, whose purpose is to basically
        # identify which bounding box from a specific entry of contours is the largest.
        # Upon finding a w_temp and h_temp larger than the previously recorded maximums
        # we save the i that these values were recorded at, and update the new maxes.
        # This could possibly be made better using the area function in OpenCV? 
        # Basically this doesn't account for when the box becomes shorter but wider, or inverse.
        if flag == 1 and len(contours) > 0:
            #w_max=0
            #h_max = 0
            #holder = 0
            #for i in range(len(contours)):
            #    cnt = contours[i]
            #    x_temp,y_temp,w_temp,h_temp = cv.boundingRect(cnt)
            #    if w_temp >= w_max and h_temp >= h_max:
            #        w_max = w_temp
            #        h_max = h_temp
            #        holder = i
            #cnt = contours[holder]
            #See above comment, found a better way to do this, see below. Accomplishes same task, 
            #less bloat. Possibly more performant.
            cnt = max(contours, key = cv.contourArea)
            # Once we have found the bounding rectangle with the largest area, we need to identify its centroid.
            x,y,w,h = cv.boundingRect(cnt)
            cv.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            cv.line(frame,(x,y),(x+w,y+h),(0,0,255),2)
            centroidx = x+(w//2)
            centroidy = y+(h//2)
            cv.circle(frame, (centroidx, centroidy), 5, (0,0,255), -1)
            # Once we have the centroid we need to scale it to between -1 and 1, for the purposes of the game state.
            # We do this by comparing it's position to the width of the frame. 
            # If its at x=0, (0/(w/2))-1=0-1=-1, 
            # If it's at x=max width, i.e. the far edge of the frame across from the zero position, (w/(w/2))-1=2-1=1
            scaled_centroidx = ((centroidx/(width//2))-1)
            #print("x:", scaled_centroidx)
            #print(x , y, w, h)
            # This is the distance estimation using the known dimensions of the striker and the FOV of the camera. 
            # By dividing this by the observed width of the striker, w, we can make a good estimate for distance.
            distance_estimate = 350.5*7.1/w
            # basically this is to combat the issue where an object further away has to travel further 
            # in order to reach the edges of the frame, it's a linear relationship scaling with distance.
            antiparallax_x = scaled_centroidx*distance_estimate/3.9
            if antiparallax_x > 1:
                antiparallax_x = 1
            if antiparallax_x < -1:
                antiparallax_x = -1
            weighted_moving_average_x.append(antiparallax_x)
            #print(len(weighted_moving_average_x))
            #print(weighted_moving_average_x)
            # This is the moving average implementation. Smooths the jitter on the data readout quite well.
            # You can probably rewrite this so that it works even when not fully populated (possibly with a for loop?)
            # But since the game state runs so fast, time to populate is so minuscule that this implementation works 
            # perfectly fine and is virtually indistinguishable
            while len(weighted_moving_average_x) > 4:
                weighted_moving_average_x.pop(0)
                #print("popping")    
            if len(weighted_moving_average_x) == 4:
                final_x = (weighted_moving_average_x[3]+0.75*weighted_moving_average_x[2]+0.50*weighted_moving_average_x[1]+0.25*weighted_moving_average_x[0])/2.50
                #print("using avg")
            else:
                final_x = antiparallax_x
            if final_x > 1:
                final_x = 1
            if final_x < -1:
                final_x = -1
            #print("x:", final_x)
            #print("x:", antiparallax_x)
            #print("y:", distance_estimate)
            scaled_y = distance_estimate*0.385-5.77
            if scaled_y > 1:
                scaled_y = 1
            if scaled_y < -1:
                scaled_y = -1
            weighted_moving_average_y.append(scaled_y)
            while len(weighted_moving_average_y) > 4:
                #print("popping")
                weighted_moving_average_y.pop(0)    
            if len(weighted_moving_average_y) == 4:
                final_y = (weighted_moving_average_y[3]+0.75*weighted_moving_average_y[2]+0.50*weighted_moving_average_y[1]+0.25*weighted_moving_average_y[0])/2.50
                #print("here")
            else:
                final_y = scaled_y
            if final_y > 1:
                final_y = 1
            if final_y < -1:
                final_y = -1
            #print("scaled y:", scaled_y)
            #print("final x:", final_x)
            #print("final y", final_y)
            config.camera.put([final_x*flip, -1*final_y])

        #cv.imshow('frame',frame)
        #cv.imshow('mask',mask)
        #cv.imshow('blur',blur)
        #cv.imshow('blur2', blur2)
        #cv.imshow('edges', edges)
        #cv.imshow('res',res)
        k = cv.waitKey(5) & 0xFF
        if k == 27:
            break
        if flag == 0:
            flag = 1
        #time.sleep(0.5)
    cv.destroyAllWindows()