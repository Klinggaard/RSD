import threading

from scripts.GUI.mesGUI import MainApp
from scripts.execute import main_thread_loop
from scripts.finite_state_machine import FiniteStateMachine as FSM
from scripts.SignalLight import light_tower

#Instanciate the state machine
stateMachine = FSM(FSM.states_packml, FSM.transition)

#Create a packml thread which runs the state logic
executeThread = threading.Thread(target=main_thread_loop, args=[])
executeThread.start()

#create a lighttower thread (THIS IS NOT TESTED)
lightTowerThread = threading.Thread(target=light_tower(), args=[])

#run the gui which uses the states of the statemachine
MainApp().run()