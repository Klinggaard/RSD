import rtde_io
import time
import random

import rtde_io
rtde_io = rtde_io.RTDEIOInterface("192.168.0.99")

print("TURNING ON THE LIGHTS")
#Light IO
rtde_io.setStandardDigitalOut(1, True)
rtde_io.setStandardDigitalOut(2, True)
rtde_io.setStandardDigitalOut(3, True)

#Valve IO
rtde_io.setStandardDigitalOut(0,True)


while(True):
    time.sleep(1)
    rtde_io.setStandardDigitalOut(1, False)
    rtde_io.setStandardDigitalOut(2, False)
    rtde_io.setStandardDigitalOut(3, False)
    rtde_io.setStandardDigitalOut(0,True)
    time.sleep(1)
    rtde_io.setStandardDigitalOut(1, True)
    rtde_io.setStandardDigitalOut(2, True)
    rtde_io.setStandardDigitalOut(3, True)
    rtde_io.setStandardDigitalOut(0,True)

