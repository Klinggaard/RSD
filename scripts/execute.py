import threading
import time

from scripts.modbus.modbus_client import Client
from scripts.RobotControl import RobotControl
from scripts.RestMiR import RestMiR
from scripts.MesOrder import MesOrder
import logging
from scripts.finite_state_machine import FiniteStateMachine as FSM
import json

#The same as in image processing TODO: Make a global define file
BLUE, RED, YELLOW, ERROR = (i for i in range(4))
def packOrders():
    modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
    robot = RobotControl()
    db_orders = MesOrder()
    modbus_client.connect()
    #mir = RestMiR() TODO IMPLEMENT THIS

    for order_counter in range(4):
        do_order = db_orders.get_put_order()

        #Dummy order(FOR TESTING OUTSIDE 4.0)
        # with open("../scripts/PPP/grasp_config.json", 'r') as f:
        #     datastore = json.load(f)
        # do_order = datastore["DummyOrder"]

        reds = do_order["red"]
        blues = do_order["blue"]
        yellows = do_order["yellow"]
        # TODO make into function
        while yellows > 0:
            robot.graspYellow()
            verify = modbus_client.get_brick_colours()[0]
            print("VERIFY: ", verify)
            if verify == ERROR:
                logging.error("Error, Modbus client / camera problem")
                # add tossing out or going into hold state
            if verify == YELLOW:
                robot.putInBox(order_counter)
                # add letting go of a block
                # add different positions for different boxes
                yellows -= 1
            else:
                logging.info("Block has different color than expected - toss it out")
                # add tossing out
        while reds > 0:
            robot.graspRed()
            modbus_client.connect()
            verify = modbus_client.get_brick_colours()[0]
            if verify == 3:
                logging.error("Error, Modbus client / camera problem")
                # add tossing out or going into hold state
            if verify == 1:
                robot.putInBox(order_counter)
                # add different positions for different boxes
                reds -= 1
            elif verify != 1:
                logging.info("Block has different color than expected - toss it out")
                # add tossing out
        while blues > 0:
            robot.graspBlue()
            modbus_client.connect()
            verify = modbus_client.get_brick_colours()[0]
            if verify == 3:
                logging.error("Error, Modbus client / camera problem")
                # add tossing out or going into hold state
            if verify == 0:
                robot.putInBox(order_counter)
                # add different positions for different boxes
                blues -= 1
            elif verify != 0:
                logging.info("Block has different color than expected - toss it out")
                # add tossing out
        logging.info("Sub-order completed")
        db_orders.delete_order(do_order)


def main_thread_loop():
    stateMachine = FSM.getInstance()
    while True:
        logging.info(str('[State] {}').format(stateMachine.state))
        execute_state = stateMachine.state
        if (execute_state == 'Starting'):
            stateMachine.change_state('SC', 'Starting', 'Execute')
        elif (execute_state == 'Execute'):
            # Execute the main process here
            packOrders()
            # and change the state to either: holding, suspending or completing
            stateMachine.change_state('SC', 'Execute', 'Completing')
        elif (execute_state == 'Completing'):
            stateMachine.change_state('SC', 'Completing', 'Complete')
        elif (execute_state == 'Resetting'):
            # Do some resetting procedure here
            stateMachine.change_state('SC', 'Resetting', 'Idle')
        elif (execute_state == 'Aborting'):
            # Do some aborting stuff, like stopping the robot and change to aborted
            stateMachine.change_state('SC', 'Aborting', 'Aborted')
        elif (execute_state == 'Clearing'):
            # Stop MES and do some clearing after an abort
            stateMachine.change_state('SC', 'Clearing', 'Stopped')
        elif (execute_state == 'Stopping'):
            # Stop MES
            stateMachine.change_state('SC', 'Stopping', 'Stopped')

        # TODO: REMOVE THIS SLEEP WHEN NOT TESTING ANYMORE
        time.sleep(1)

#    if order_counter == 2:
#        order_counter = 0
#       mir_mission = mir.get_mission("GoTo6")
#       mir.add_mission_to_queue(mir_mission)
# we calculate based on how many times we delete an order, can be done in a lot of ways
#print("Number of completed orders: " + str(db_orders.counter % 4))
'''
while mir.read_register(1) != 1: # wait for MIR to arrive
mir.read_register(1)
# add function to put boxes on MIR & flag to make sure we are done with packing
mir.write_register(1, 0)  # MIR can go
mir.write_register(2, 1)  # MIR go to base
# change state to completing
'''


