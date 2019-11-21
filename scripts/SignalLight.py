import rtde_io as io
import time
import random
from scripts.finite_state_machine import FiniteStateMachine

rtde_io = io.RTDEIOInterface("192.168.0.99")

def lights_on_of():

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

#TODO IMPLEMENT THIS FOR MINIMAL CODE DUPLICATION
def lights(l1=False, l2=False, l3=False):
    rtde_io.setStandardDigitalOut(1, l1)
    rtde_io.setStandardDigitalOut(2, l2)
    rtde_io.setStandardDigitalOut(3, l3)



def light_tower(state):
    if state=='Stopping' or state=='Stopped':
        lights(True,False,False)
    elif state=='Aborting' or state=='Aborted' or state=='Clearing':
        while (True):
            lights(False,False,True)
            time.sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            time.sleep(1)
    elif  state=='Resetting':
         while True:
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,True)
            rtde_io.setStandardDigitalOut(1,False)
            time.sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            time.sleep(1)
    elif state=='Suspending' or state=='Suspended':
        rtde_io.setStandardDigitalOut(2,True)
        rtde_io.setStandardDigitalOut(3,False)
        rtde_io.setStandardDigitalOut(1,False)
    elif state=='Idle':
         while (True):
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,True)
            time.sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            time.sleep(1)
    elif state=='Starting' or state=='Executing' or state=='Unholding' or state=='Unsuspending':
        rtde_io.setStandardDigitalOut(1,True)
        rtde_io.setStandardDigitalOut(3,False)
        rtde_io.setStandardDigitalOut(2,False)
    elif state=='Holding' or state=='Held':
         while (True):
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,True)
            rtde_io.setStandardDigitalOut(1,True)
            time.sleep(1)
            rtde_io.setStandardDigitalOut(3,False)
            rtde_io.setStandardDigitalOut(2,False)
            rtde_io.setStandardDigitalOut(1,False)
            time.sleep(1)

while (True):
    State=FiniteStateMachine.state
    light_tower(State)