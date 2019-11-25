import threading

from scripts.GUI.mesGUI import MainApp
from scripts.execute import main_thread_loop
from scripts.finite_state_machine import FiniteStateMachine as FSM
from scripts.SignalLight import LightTower
from scripts.RobotControl import RobotControl

#Instanciate the state machine and Robot
stateMachine = FSM(FSM.states_packml, FSM.transition)
robotCtonrol = RobotControl()

#Create a packml thread which runs the state logic
executeThread = threading.Thread(target=main_thread_loop, args=[])
executeThread.start()

#create a lighttower thread (THIS IS NOT TESTED)
light_t = LightTower()
lightTowerThread = threading.Thread(target=light_t.light_tower, args=[])
lightTowerThread.start()

#run the gui which uses the states of the statemachine
MainApp().run()
