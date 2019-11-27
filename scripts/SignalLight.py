import rtde_io as io
import time
import random
from scripts.finite_state_machine import FiniteStateMachine as FSM
from scripts.RobotControl import RobotControl

period = 0.5

class LightTower:

    def __init__(self):
        self.robot = RobotControl.getInstance()

    def light_tower(self):

        while True:
            stateMachine = FSM.getInstance()
            state = stateMachine.state
            if state=='Stopping' or state=='Stopped':
                self.robot.lights(False,False,True)
                time.sleep(1)
            elif state=='Aborting' or state=='Aborted' or state=='Clearing':
                self.robot.lights(False, False, True)
                time.sleep(period)
                self.robot.lights()
                time.sleep(period)
            elif  state=='Resetting':
                self.robot.lights(False, True, False)
                time.sleep(period)
                self.robot.lights()
                time.sleep(period)
            elif state=='Suspending' or state=='Suspended':
                self.robot.lights(False, True, False)
                time.sleep(period)
            elif state=='Idle':
                self.robot.lights(True, False, False)
                time.sleep(period)
                self.robot.lights()
                time.sleep(period)
            elif state=='Starting' or state=='Execute' or state=='Unholding' or state=='Unsuspending':
                self.robot.lights(True, False, False)
                time.sleep(period)
            elif state=='Holding' or state=='Held':
                self.robot.lights(True, True, False)
                time.sleep(period)
                self.robot.lights()
                time.sleep(period)