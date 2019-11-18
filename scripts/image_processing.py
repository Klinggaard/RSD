
import getpass as gp
assert gp.getuser() == "pi", "Can't run on other equipment pi"

import cv2 as cv
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

camera = PiCamera()

BLUE, RED, YELLOW, ERROR = (i for i in range(4))
_colour_thresh = 0.8 * 255


# Colour ranges in HSV
# TODO: Find correct colour ranges
_colour_ranges = {
    "BLUE": ((101, 93, 0), (180, 198, 52)),
    "RED": ((130, 0, 0), (180, 255, 255)),
    "YELLOW": ((15, 0, 18), (29, 255, 124))  # possible remove
}

# TODO: Set coordinate ranges for different bricks
_brick_coords = {
    "B22": ((1512, 2096), (1192, 1554))
}


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
    rawCapture = cv.resize(rawCapture.array, (3280,2464))
    return rawCapture


def _check_brick(frame, brick):
    crop_frame = frame[brick[1][0]:brick[1][1], brick[0][0]:brick[0][1]]
    ret_list = []
    count = 0

    for c in _colour_ranges:
        binary_image = _colour_segmentation(crop_frame, _colour_ranges[c])
        average = binary_image.mean(axis=0).mean(axis=0)

        if average > _colour_thresh:
            print(average)
            ret_list.append(count)
        count += 1

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
