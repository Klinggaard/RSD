import rtde_io
import time
import random

import rtde_io
rtde_io = rtde_io.RTDEIOInterface("192.168.0.99")

print("TURNING ON THE LIGHTS")
rtde_io.setStandardDigitalOut(0, True)
rtde_io.setStandardDigitalOut(1, True)
rtde_io.setStandardDigitalOut(2, True)

while(True):
    time.sleep(1)
    rtde_io.setStandardDigitalOut(0, False)
    rtde_io.setStandardDigitalOut(1, False)
    rtde_io.setStandardDigitalOut(2, False)
    time.sleep(1)
    rtde_io.setStandardDigitalOut(0, True)
    rtde_io.setStandardDigitalOut(1, True)
    rtde_io.setStandardDigitalOut(2, True)

