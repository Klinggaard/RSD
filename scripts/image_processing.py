
import getpass as gp
assert gp.getuser() == "pi", "Can't run on other equipment pi"

import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# Colour ranges in HSV
# TODO: Find correct colour ranges
_BLUE   = ((240, 100, 80), (240, 100, 80))
_RED    = ((0, 100, 80), (0, 100, 80))
_YELLOW = ((60, 100, 80), (60, 100, 80))
_WOOD   = ((0, 0, 0), (0, 0, 0))


def _colour_segmentation(frame, colour_range):
    if frame is None:
        return None
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    frame_threshold = cv.inRange(frame_HSV, colour_range)

    # TODO: Check if colour is found in correct location in frame
    # TODO: Define correct locations


def capture_image():
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    # allow the camera to warmup
    time.sleep(0.1)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    return rawCapture.array

def check_bricks():
    # TODO: Implement this function
    # TODO: Determine codes for colours
    return [0,0,0] # Code for the colour of the bricks in the feeder