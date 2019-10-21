#!/usr/bin/env python3
import getpass as gp
import cv2

is_pi = False
img_path = ""
img = None
if gp.getuser() == "pi":
    import picamera
    is_pi = True
else:
    img_path = "C:/Users/olive/Desktop/kawasaki.png"
    img = cv2.imread(img_path)



cv2.imshow("img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

