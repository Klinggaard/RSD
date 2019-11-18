#!/usr/bin/env python3
import getpass as gp
import cv2 as cv
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
camera = PiCamera()

max_value = 255
max_value_H = 360 // 2
low_H = 0
low_S = 0
low_V = 0
high_H = max_value_H
high_S = max_value
high_V = max_value
window_capture_name = 'Image'
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'




def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H - 1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)

def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H + 1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)

def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S - 1, low_S)
    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)

def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S + 1)
    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)

def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V - 1, low_V)
    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)

def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V + 1)
    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)

frame = PiRGBArray(camera)
# allow the camera to warmup
time.sleep(0.1)
# grab an image from the camera
camera.capture(frame, format="bgr")

# cv.imshow("img", rawCapture.array)
# cv.waitKey(0)
frame = cv.resize(frame.array, (3280,2464))

max_val = frame.shape[1]
max_x = frame.shape[0]
min_x = 0
max_y = frame.shape[1]
min_y = 0

def on_min_x_thresh_trackbar(val):
    global min_x
    global max_x
    min_x = val
    min_x = min(max_x - 1, min_x)
    cv.setTrackbarPos("min x", window_detection_name, min_x)

def on_max_x_thresh_trackbar(val):
    global min_x
    global max_x
    max_x = val
    max_x = max(max_x, min_x+1)
    cv.setTrackbarPos("max x", window_detection_name, max_x)

def on_min_y_thresh_trackbar(val):
    global min_y
    global max_y
    min_y = val
    min_y = min(max_y - 1, min_y)
    cv.setTrackbarPos("min y", window_detection_name, min_y)

def on_max_y_thresh_trackbar(val):
    global min_y
    global max_y
    max_y = val
    max_y = max(max_y, min_y + 1)
    cv.setTrackbarPos("max y", window_detection_name, max_y)


cv.namedWindow(window_capture_name, cv.WINDOW_NORMAL)
cv.namedWindow(window_detection_name, cv.WINDOW_NORMAL)
cv.resizeWindow(window_capture_name, 600, 600)
cv.resizeWindow(window_detection_name, 600, 600)


cv.createTrackbar(low_H_name, window_detection_name, low_H, max_value_H, on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name, window_detection_name, high_H, max_value_H, on_high_H_thresh_trackbar)
cv.createTrackbar(low_S_name, window_detection_name, low_S, max_value, on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name, window_detection_name, high_S, max_value, on_high_S_thresh_trackbar)
cv.createTrackbar(low_V_name, window_detection_name, low_V, max_value, on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name, window_detection_name, high_V, max_value, on_high_V_thresh_trackbar)


cv.createTrackbar("min x", window_detection_name, min_x, max_val, on_min_x_thresh_trackbar)
cv.createTrackbar("max x", window_detection_name, max_x, max_val, on_max_x_thresh_trackbar)
cv.createTrackbar("min y", window_detection_name, min_y, max_val, on_min_y_thresh_trackbar)
cv.createTrackbar("max y", window_detection_name, max_y, max_val, on_max_y_thresh_trackbar)


while True:

    if frame is None:
        break

    crop_frame = frame[min_y:max_y, min_x:max_x]

    frame_HSV = cv.cvtColor(crop_frame, cv.COLOR_BGR2HSV)
    frame_threshold = cv.inRange(frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))

    cv.imshow(window_capture_name, frame_threshold)
    cv.imshow(window_detection_name, frame)

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        break
