
import getpass as gp
assert gp.getuser() == "pi", "Can't run on other equipment pi"

import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

BLUE, RED, YELLOW, ERROR = (i for i in range(4))
_colour_thresh = 0.5


# Colour ranges in HSV
# TODO: Find correct colour ranges
_colour_ranges = {
    "BLUE": ((240, 100, 80), (240, 100, 80)),
    "RED": ((0, 100, 80), (0, 100, 80)),
    "YELLOW": ((60, 100, 80), (60, 100, 80)),
    "WOOD": ((0, 0, 0), (0, 0, 0))  # possible remove
}

# TODO: Set coordinate ranges for different bricks
_brick_coords = {
    "B22": ((0, 0), (200, 200)),
    "B24": ((0, 0), (200, 200)),
    "B26": ((0, 0), (200, 200))
}


def _colour_segmentation(frame, colour_range):
    if frame is None:
        return None
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    return cv.inRange(frame_HSV, colour_range)



def _capture_image():
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    # allow the camera to warmup
    time.sleep(0.1)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")

    cv.imshow("img", rawCapture.array)
    cv.waitKey(0)
    return rawCapture.array


def _check_brick(frame, brick):
    crop_frame = frame[brick[1][0]:brick[1][1], brick[0][0]:brick[0][1]]
    ret_list = []
    count = 0

    for c in _colour_ranges:
        binary_image = _colour_segmentation(crop_frame, _colour_ranges[c])
        average = binary_image.mean(axis=0).mean(axis=0)

        if average > _colour_thresh:
            ret_list.append(count)
        count += 1

    if len(ret_list) > 1:
        return ERROR
    return count


def check_bricks():
    frame = _capture_image()
    ret_list = []

    for brick in _brick_coords:
        ret_list.append(_check_brick(frame, _brick_coords[brick]))
    return ret_list  # Code for the colour of the bricks in the feeder
