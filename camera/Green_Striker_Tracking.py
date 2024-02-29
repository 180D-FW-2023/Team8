import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import math

#file_path = os.path.join("..", "input_output", "sensor_data.csv")
#dir_path = os.path.dirname(__file__)
#os.chdir(dir_path)
#full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))
#print(file_path)
#print(os.getcwd())
#print(full_path)
flag = 0
# I was running into an issue where the countours object (which is an array of arrays I think) was 
# initialized as empty on the first run through, or atleast the compiler believed it to be. So, the
# purpose of the flag is to halt the cnt = contours[i] code until contours is correctly populated
MIN_MATCH_COUNT = 6
lower_green = np.array([40,60,20])
upper_green = np.array([100,255,198])
cap = cv.VideoCapture(2)
while(1):
    # Standard setup for OpenCV video processing
    _, frame = cap.read()
    frame_Gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    height, width, _ = frame.shape
    # Threshold the HSV image to get only green colors, threshold values were received from the max 
    # and min observed values from an online color picker, with a  sample image of the target object
    mask = cv.inRange(frame_hsv, lower_green, upper_green)
    #ret1, mask = cv.threshold(grayscale,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    blur = cv.medianBlur(mask,23)
    # median blur to remove salt and pepper noise
    blur2 = cv.blur(blur,(20,20))
    # standard blur appears to be sufficient for our case. 20,20 was chosen experimentally
    edges = cv.Canny(blur, 100, 200)
    contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    Extracted_Striker_Frame = cv.imread('ThresholdStriker.png')
    Extracted_Striker_Frame_Gray = cv.cvtColor(Extracted_Striker_Frame, cv.COLOR_BGR2GRAY)
    # Initiate SIFT detector
    sift = cv.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(blur2,None)
    kp2, des2 = sift.detectAndCompute(Extracted_Striker_Frame_Gray,None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.9*n.distance:
            good.append(m)
    if len(good)>MIN_MATCH_COUNT:
        #src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        #dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        #M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
        #matchesMask = mask.ravel().tolist()
        #h,w = blur2.shape
        #pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        #dst = cv.perspectiveTransform(pts,M)
        #blur2 = cv.polylines(blur2,[np.int32(dst)],True,255,3, cv.LINE_AA)
        print ("Good Threshold Found, Exiting")
        exit()
    else:
        print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
        matchesMask = None
        
    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)
    img3 = cv.drawMatches(blur2,kp1,Extracted_Striker_Frame_Gray,kp2,good,None,**draw_params)
    img3_small = cv.resize(img3, (0, 0), fx = 0.5, fy = 0.5)
    cv.imshow('matching',img3_small)
    cv.imshow('frame',frame)
    cv.imshow('Extractedstriker' , Extracted_Striker_Frame)
    cv.imshow('mask',mask)
    cv.imshow('blur',blur)
    cv.imshow('blur2', blur2)
    #plt.imshow(img3, 'gray'),plt.show()
    """
    minHessian = 400
    detector = cv.xfeatures2d_SURF.create(hessianThreshold=minHessian)
    keypoints_obj, descriptors_obj = detector.detectAndCompute(Extracted_Striker_Frame, None)
    keypoints_scene, descriptors_scene = detector.detectAndCompute(frame, None)
    matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
    knn_matches = matcher.knnMatch(descriptors_obj, descriptors_scene, 2)
    ratio_thresh = 0.75
    good_matches = []
    for m,n in knn_matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)
    img_matches = np.empty((max(Extracted_Striker_Frame.shape[0], frame.shape[0]), Extracted_Striker_Frame.shape[1]+frame.shape[1], 3), dtype=np.uint8)
    cv.drawMatches(Extracted_Striker_Frame, keypoints_obj, frame, keypoints_scene, good_matches, img_matches, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    obj = np.empty((len(good_matches),2), dtype=np.float32)
    scene = np.empty((len(good_matches),2), dtype=np.float32)
    for i in range(len(good_matches)):
    #-- Get the keypoints from the good matches
        obj[i,0] = keypoints_obj[good_matches[i].queryIdx].pt[0]
        obj[i,1] = keypoints_obj[good_matches[i].queryIdx].pt[1]
        scene[i,0] = keypoints_scene[good_matches[i].trainIdx].pt[0]
        scene[i,1] = keypoints_scene[good_matches[i].trainIdx].pt[1]
    H, _ =  cv.findHomography(obj, scene, cv.RANSAC)
    obj_corners = np.empty((4,1,2), dtype=np.float32)
    obj_corners[0,0,0] = 0
    obj_corners[0,0,1] = 0
    obj_corners[1,0,0] = Extracted_Striker_Frame.shape[1]
    obj_corners[1,0,1] = 0
    obj_corners[2,0,0] = Extracted_Striker_Frame.shape[1]
    obj_corners[2,0,1] = Extracted_Striker_Frame.shape[0]
    obj_corners[3,0,0] = 0
    obj_corners[3,0,1] = Extracted_Striker_Frame.shape[0]
    scene_corners = cv.perspectiveTransform(obj_corners, H)
    cv.line(img_matches, (int(scene_corners[0,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[0,0,1])),\
        (int(scene_corners[1,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[1,0,1])), (0,255,0), 4)
    cv.line(img_matches, (int(scene_corners[1,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[1,0,1])),\
        (int(scene_corners[2,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[2,0,1])), (0,255,0), 4)
    cv.line(img_matches, (int(scene_corners[2,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[2,0,1])),\
        (int(scene_corners[3,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[3,0,1])), (0,255,0), 4)
    cv.line(img_matches, (int(scene_corners[3,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[3,0,1])),\
        (int(scene_corners[0,0,0] + Extracted_Striker_Frame.shape[1]), int(scene_corners[0,0,1])), (0,255,0), 4)
    cv.imshow('Good Matches & Object detection', img_matches)
    """

    #cv.waitKey()
    #print(width) <- deprecated code to tell the size of video output
    # HSV gives better thresholding results, so below is the code to convert to HSV
    #hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    #lower_green = np.array([40,51,51])
    #upper_green = np.array([85,230,153])
    #Values above are for my laptop camera, values below are for USB camera (for project)
    #lower_green = np.array([33,16,126])
    #upper_green = np.array([67,107,199])
    # Threshold the HSV image to get only green colors, threshold values were received from the max 
    # and min observed values from an online color picker, with a  sample image of the target object
    #mask = cv.inRange(hsv, lower_green, upper_green)
    #lur = cv.medianBlur(mask,29)
    # median blur to remove salt and pepper noise
    #blur2 = cv.blur(blur,(20,20))
    # standard blur appears to be sufficient for our case. 20,20 was chosen experimentally
    #edges = cv.Canny(blur, 100, 200)
    #contours, _ = cv.findContours(blur2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # This is a doozy. Basically, if contours is populated correctly 
    # (which is what flag == 1 and len(contours)>1 is supposed to guarantee)
    # we initialize a set of placeholder variables, whose purpose is to basically
    # identify which bounding box from a specific entry of contours is the largest.
    # Upon finding a w_temp and h_temp larger than the previously recorded maximums
    # we save the i that these values were recorded at, and update the new maxes.
    # This could possibly be made better using the area function in OpenCV? 
    # Basically this doesn't account for when the box becomes shorter but wider, or inverse.
    #if flag == 1 and len(contours) > 0:
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
        #cnt = max(contours, key = cv.contourArea)
        #cnt = contours[len(contours)-1] <- I swear to god I have no idea what I was testing with this, 
        # but maybe I was cooking so I'll leave it.
        #x,y,w,h = cv.boundingRect(cnt)
        #cv.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        #cv.line(frame,(x,y),(x+w,y+h),(0,0,255),2)
        # I could write my own pythagorean theorem program, but for now, importing math for hypot is fine.
        #diagonal = math.hypot(w,h)
        #centroidx = x+(w//2)
        #centroidy = y+(h//2)
        #cv.circle(frame, (centroidx, centroidy), 5, (0,0,255), -1)
        #scaled_centroidx = ((centroidx/(width//2))-1)
        #print(diagonal)
        #print("x:", scaled_centroidx)
        #print(x , y, w, h)
        #olddiagonal = diagonal
        #sigma = diagonal - olddiagonal
        #distance_estimate = 460.7*7.1/w
        #print("y:", distance_estimate)
        #with open(full_path, 'w') as file:
            #file.write(str(scaled_centroidx))
            #file.close()
    #cv.imshow('frame',frame)
    #cv.imshow('Extractedstriker' , Extracted_Striker_Frame)
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