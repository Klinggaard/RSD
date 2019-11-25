import threading
import time

from scripts.modbus.modbus_client import Client
from scripts.RobotControl import RobotControl
from scripts.RestMiR import RestMiR
from scripts.MesOrder import MesOrder
import logging
from scripts.finite_state_machine import FiniteStateMachine as FSM
import json

BLUE, RED, YELLOW, ERROR = (i for i in range(4))
refill_yellow = 18
refill_red = 18
refill_blue = 18

def packOrders():
    robot = RobotControl.getInstance()
    modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
    if not modbus_client:
        logging.ERROR("[PackOrders] Cannot connect to modbus")
    #db_orders = MesOrder()
    modbus_client.connect()
    stateMachine = FSM.getInstance()
    mir = RestMiR() #TODO IMPLEMENT THIS

    for order_counter in range(4):
        if stateMachine.state != "Execute":
            break

        #do_order = db_orders.get_put_order()

        #Dummy order(FOR TESTING OUTSIDE 4.0)
        with open("../scripts/PPP/grasp_config.json", 'r') as f:
             datastore = json.load(f)
        do_order = datastore["DummyOrder"]

        reds = do_order["red"]
        blues = do_order["blue"]
        yellows = do_order["yellow"]

        while yellows > 0:
            if stateMachine.state != "Execute":
                break
            robot.graspYellow()
            verify = modbus_client.get_brick_colours()[0]
            print("VERIFY: ", verify)
            if verify == ERROR:
                logging.error("Error, Modbus client / camera problem")
                robot.dumpBrick()
            if verify == YELLOW:
                robot.putInBox(order_counter)
                yellows -= 1
                global refill_yellow
                refill_yellow -= 1
            else:
                robot.dumpBrick()
                refill_yellow -= 1
                logging.info("Block has different color than expected - toss it out")
            if refill_yellow == 0:
                stateMachine.change_state('Hold', 'Execute', 'Holding')
        while reds > 0:
            if stateMachine.state != "Execute":
                break
            robot.graspRed()
            modbus_client.connect()
            verify = modbus_client.get_brick_colours()[0]
            if verify == 3:
                logging.error("Error, Modbus client / camera problem")
                robot.dumpBrick()
            if verify == 1:
                robot.putInBox(order_counter)
                reds -= 1
                global refill_red
                refill_red -= 1
            elif verify != 1:
                robot.dumpBrick()
                refill_red -= 1
                logging.info("Block has different color than expected - toss it out")
            if refill_red == 0:
                stateMachine.change_state('Hold', 'Execute', 'Holding')
        while blues > 0:
            if stateMachine.state != "Execute":
                break
            robot.graspBlue()
            modbus_client.connect()
            verify = modbus_client.get_brick_colours()[0]
            if verify == 3:
                logging.error("Error, Modbus client / camera problem")
                # add tossing out or going into hold state
                robot.dumpBrick()
            if verify == 0:
                robot.putInBox(order_counter)
                blues -= 1
                global refill_blue
                refill_blue -= 1
            elif verify != 0:
                robot.dumpBrick()
                refill_blue -= 1
                logging.info("Block has different color than expected - toss it out")
            if refill_blue == 0:
                stateMachine.change_state('Hold', 'Execute', 'Holding')
        logging.info("Sub-order completed")
        #db_orders.delete_order(do_order)

        if order_counter == 2:
            mir_mission = mir.get_mission("GoTo6")
            mir.add_mission_to_queue(mir_mission)

    guid = mir.get_mission("GoTo6")
    mir.add_mission_to_queue(guid)
    while mir.read_register(6) != 1: # wait for MIR to arrive
        mir.read_register(1)
    logging.info("mir arrived")
    # add function to put boxes on MIR & flag to make sure we are done with packing
    time.sleep(2)
    mir.write_register(6, 0)  # MIR can go
    logging.info("bye MIR")
    # change state to complete ??
    #stateMachine.change_state('SC', 'Execute', 'Completing')

    modbus_client.close()


def main_thread_loop():
    stateMachine = FSM.getInstance()
    robot = RobotControl.getInstance()
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
            robot.moveRobot("Reset")
            robot.openGripper()
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
        elif (execute_state == 'Holding'):
            logging.info('Holding state - stop robot')
            stateMachine.change_state('SC', 'Holding', 'Held')
        #elif (execute_state == 'Held'):
            #stateMachine.change_state('Unhold', 'Held', 'Unholding')
        elif (execute_state == 'Unholding'):
            stateMachine.change_state('SC', 'Unholding', 'Execute')

        # TODO: REMOVE THIS SLEEP WHEN NOT TESTING ANYMORE
        time.sleep(1)
