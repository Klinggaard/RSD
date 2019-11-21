import threading

from scripts.GUI.mesGUI import MainApp
from scripts.execute import main_thread_loop
from scripts.finite_state_machine import FiniteStateMachine as FSM


#Instanciate the state machine
stateMachine = FSM(FSM.states_packml, FSM.transition)
#Create a packml thread which runs the state logic
executeThread = threading.Thread(target=main_thread_loop, args=[])
executeThread.start()
#run the gui which uses the states of the statemachine
MainApp().run()