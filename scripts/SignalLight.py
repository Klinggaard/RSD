import rtde_io
import time
import random
import finite_state_machine.py

import rtde_io

def lights_on_of():
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

def light_tower(state):
    if state=='Stopping' or state=='Stopped':
        rtde_io.setStandardDigitalOut(3,True)
        rtde_io.setStandardDigitalOut(2,False)
        rtde_io.setStandardDigitalOut(1,False)
    elif state=='Aborting' or state=='Aborted' or state=='Clearing':
        while (True):
            rtde_io.setStandardDigitalOut(3,True)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            sleep(1)
    elif  state=='Resetting':
         while True:
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,True)
            rtde_io.setStandardDigitalOut(1,False)
            sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            sleep(1)
    elif state=='Suspending' or state=='Suspended':
        rtde_io.setStandardDigitalOut(2,True)
        rtde_io.setStandardDigitalOut(3,False)
        rtde_io.setStandardDigitalOut(1,False)
    elif state=='Idle':
         while (True):
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,True)
            sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            sleep(1)
    elif state=='Starting' or state=='Executing' or state=='Unholding' or state=='Unsuspending':
        rtde_io.setStandardDigitalOut(1,True)
        rtde_io.setStandardDigitalOut(3,False)
        rtde_io.setStandardDigitalOut(2,False)
    elif state=='Holding' or state=='Held':
         while (True):
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,True)
            rtde_io.setStandardDigitalOut(1,True)
            sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            sleep(1)

while (True):
    State=FiniteStateMachine.state
    light_tower(State)