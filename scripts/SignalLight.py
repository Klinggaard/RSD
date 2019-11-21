import rtde_io as io
import time
import random
from scripts.finite_state_machine import FiniteStateMachine as FSM

rtde_io = io.RTDEIOInterface("192.168.0.99")
period = 0.5

def lights(l1=False, l2=False, l3=False):
    rtde_io.setStandardDigitalOut(1, l1)
    rtde_io.setStandardDigitalOut(2, l2)
    rtde_io.setStandardDigitalOut(3, l3)


def light_tower():

    while True:
        stateMachine = FSM.getInstance()
        state = stateMachine.state
        if state=='Stopping' or state=='Stopped':
            lights(True,False,False)
            time.sleep(1)
        elif state=='Aborting' or state=='Aborted' or state=='Clearing':
            lights(False, False, True)
            time.sleep(period)
            lights()
            time.sleep(period)
        elif  state=='Resetting':
            lights(False, True, False)
            time.sleep(period)
            lights()
            time.sleep(period)
        elif state=='Suspending' or state=='Suspended':
            lights(False, True, False)
            time.sleep(period)
        elif state=='Idle':
            lights(True, False, False)
            time.sleep(period)
            lights()
            time.sleep(period)
        elif state=='Starting' or state=='Executing' or state=='Unholding' or state=='Unsuspending':
            lights(True, False, False)
            time.sleep(period)
        elif state=='Holding' or state=='Held':
            lights(True, True, False)
            time.sleep(period)
            lights()
            time.sleep(period)