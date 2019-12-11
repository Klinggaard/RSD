import logging
import getpass as gp

assert gp.getuser() == "pi", "Can't run on other equipment pi"

import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import json

camera = PiCamera()

BLUE, RED, YELLOW, ERROR = (i for i in range(4))
_colour_thresh = 0.7 * 256

# Colour ranges in HSV
f = open("config.json", "r")
cfg = json.load(f)

_colour_ranges = {
    "BLUE": ((cfg["blue"]["low_H"], cfg["blue"]["low_S"], cfg["blue"]["low_V"]),
             (cfg["blue"]["high_H"], cfg["blue"]["high_S"], cfg["blue"]["high_V"])),
    "RED": ((cfg["red"]["low_H"], cfg["red"]["low_S"], cfg["red"]["low_V"]),
            (cfg["red"]["high_H"], cfg["red"]["high_S"], cfg["red"]["high_V"])),
    "YELLOW": ((cfg["yellow"]["low_H"], cfg["yellow"]["low_S"], cfg["yellow"]["low_V"]),
               (cfg["yellow"]["high_H"], cfg["yellow"]["high_S"], cfg["yellow"]["high_V"]))
}

_brick_coords = {
    "B22": ((cfg["crop"]["x_min"], cfg["crop"]["x_max"]),
            (cfg["crop"]["y_min"], cfg["crop"]["y_max"]))
}
'''
_colour_ranges = {
    "BLUE": ((72, 45, 0), (116, 255, 255)),
    "RED": ((170, 47, 0), (180, 255, 255)),
    "YELLOW": ((3, 53, 60), (20, 255, 166))
}

_brick_coords = {
    "B22": ((1172, 1792), (1202, 1607))
}
'''


def _colour_segmentation(frame, colour_range):
    if frame is None:
        return None
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    return cv.inRange(frame_HSV, colour_range[0], colour_range[1])


def _capture_image():
    # initialize the camera and grab a reference to the raw camera capture

    # return cv.imread("images/cam.jpg")

    rawCapture = PiRGBArray(camera)
    # allow the camera to warmup
    time.sleep(0.1)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")

    # cv.imshow("img", rawCapture.array)
    # cv.waitKey(0)
    rawCapture = cv.resize(rawCapture.array, (3280, 2464))
    return rawCapture


def _check_brick(frame, brick):
    crop_frame = frame[brick[1][0]:brick[1][1], brick[0][0]:brick[0][1]]
    ret_list = []
    count = 0

    for c in _colour_ranges:
        binary_image = _colour_segmentation(crop_frame, _colour_ranges[c])
        average = binary_image.mean(axis=0).mean(axis=0)
        print("colour avg : " + str(average))
        if average > _colour_thresh:
            ret_list.append(count)
        count += 1
    print(ret_list)
    if len(ret_list) > 1 or len(ret_list) == 0:
        return ERROR
    return ret_list[0]


def check_bricks():
    frame = _capture_image()
    ret_list = []

    for brick in _brick_coords:
        ret_list.append(_check_brick(frame, _brick_coords[brick]))
    return ret_list  # Code for the colour of the bricks in the feeder

# print(check_bricks())
