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


class ExecuteOrder():
    robot = RobotControl.getInstance()
    modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
    # CHANGE THAT EXCEPTION
    #if not modbus_client:
    #    logging.ERROR("[PackOrders] Cannot connect to modbus")
    modbus_client.connect()
    stateMachine = FSM.getInstance()
    mir = RestMiR()
    db_orders = MesOrder()

    refill_yellow = 18
    refill_red = 18
    refill_blue = 18
    current_order = False

    def prepare_orders(self):
        for order_counter in range(4):
            if not self.current_order:
                do_order = self.db_orders.get_put_order()
                self.current_order = True
            # Dummy order(FOR TESTING OUTSIDE 4.0)
            # with open("../scripts/PPP/grasp_config.json", 'r') as f:
            #     datastore = json.load(f)
            # do_order = datastore["DummyOrder"]
            reds = do_order["red"]
            blues = do_order["blue"]
            yellows = do_order["yellow"]

            while yellows > 0:
                if self.stateMachine.state != "Execute":
                    break
                self.robot.graspYellow()
                verify = self.modbus_client.get_brick_colours()[0]
                print("VERIFY: ", verify)
                if verify == ERROR:
                    logging.error("Error, Modbus client / camera problem")
                    self.robot.dumpBrick()
                if verify == YELLOW:
                    self.robot.putInBox(order_counter)
                    yellows -= 1
                    self.refill_yellow -= 1
                else:
                    self.robot.dumpBrick()
                    self.refill_yellow -= 1
                    logging.info("Block has different color than expected - toss it out")
                if self.refill_yellow == 0:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("Fill in yellow blocks container")

            while reds > 0:
                if self.stateMachine.state != "Execute":
                    break
                self.robot.graspRed()
                self.modbus_client.connect()
                verify = self.modbus_client.get_brick_colours()[0]
                if verify == 3:
                    logging.error("Error, Modbus client / camera problem")
                    self.robot.dumpBrick()
                if verify == 1:
                    self.robot.putInBox(order_counter)
                    reds -= 1
                    self.refill_red -= 1
                elif verify != 1:
                    self.robot.dumpBrick()
                    self.refill_red -= 1
                    logging.info("Block has different color than expected - toss it out")
                if self.refill_red == 0:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("Fill in red blocks container")

            while blues > 0:
                if self.stateMachine.state != "Execute":
                    break
                self.robot.graspBlue()
                self.modbus_client.connect()
                verify = self.modbus_client.get_brick_colours()[0]
                if verify == 3:
                    logging.error("Error, Modbus client / camera problem")
                    # add tossing out or going into hold state
                    self.robot.dumpBrick()
                if verify == 0:
                    self.robot.putInBox(order_counter)
                    blues -= 1
                    self.refill_blue -= 1
                elif verify != 0:
                    self.robot.dumpBrick()
                    self.refill_blue -= 1
                    logging.info("Block has different color than expected - toss it out")
                if self.refill_blue == 0:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("Fill in blue blocks container")

            logging.info("Sub-order completed")
            self.db_orders.delete_order(do_order)
            # 3rd order ready, call MIR
            if order_counter == 2:
                try:
                    mir_mission = self.mir.get_mission("GoTo6")
                    self.mir.add_mission_to_queue(mir_mission)
                    guid = self.mir.get_mission("GoTo6")
                    self.mir.add_mission_to_queue(guid)
                except ():
                    logging.info("Calling MIR unsuccessful")
                    self.stateMachine.change_state('Stop', 'Execute', 'Stopping')
                else:
                    logging.info("MIR ordered")
        self.current_order = False
        #self.modbus_client.close() # we connect when class object is created

    def pack_orders(self):
        while self.mir.read_register(6) != 1:
            logging.info("Wait for MIR")
        self.stateMachine.change_state('Unsuspend', 'Suspended', 'Unsuspending')
        self.stateMachine.change_state('SC', 'Unsuspending', 'Execute')

        # START PACKING

        # DONE PACKING

        self.mir.write_register(6, 0)  # MIR can go
        logging.info("MIR departures")
        # change state to complete ??
        # stateMachine.change_state('SC', 'Execute', 'Completing')

    def main_thread_loop(self):
        while True:
            logging.info(str('[State] {}').format(self.stateMachine.state))
            execute_state = self.stateMachine.state

            if execute_state == 'Starting':
                # Check if indeed we can start = safety
                self.stateMachine.change_state('SC', 'Starting', 'Execute')

            elif execute_state == 'Execute':
                self.prepare_orders()
                self.stateMachine('Suspend', 'Execute', 'Suspending')
                self.stateMachine.change_state('SC', 'Suspending', 'Suspended')
                self.pack_orders()
                self.stateMachine.change_state('SC', 'Execute', 'Completing')

            elif execute_state == 'Completing':
                self.stateMachine.change_state('SC', 'Completing', 'Complete')

            elif execute_state == 'Complete':
                self.stateMachine.change_state('Reset', 'Complete', 'Resetting')

            elif execute_state == 'Resetting':
                self.robot.moveRobot("Reset")  # to discuss if we want to do it here or after trigger
                self.robot.openGripper()
                self.stateMachine.change_state('SC', 'Resetting', 'Idle')

            elif execute_state == 'Aborting':
                # Do some aborting stuff, like stopping the robot and change to aborted
                self.robot.stopRobot()
                self.robot.openGripper()
                self.stateMachine.change_state('SC', 'Aborting', 'Aborted')

            elif execute_state == 'Aborted':
                self.stateMachine.change_state('SC', 'Aborting', 'Aborted')

            elif execute_state == 'Clearing':
                # Stop MES and do some clearing after an abort
                self.stateMachine.change_state('SC', 'Clearing', 'Stopped')

            elif execute_state == 'Stopping':
                # Stop MES
                self.stateMachine.change_state('SC', 'Stopping', 'Stopped')

            elif execute_state == 'Stopped':
                self.stateMachine.change_state('Reset', 'Stopped', 'Resetting')

            elif execute_state == 'Holding':
                # logging.info('Holding state - stop robot')
                self.robot.moveRobot("Reset")
                self.robot.openGripper()
                self.robot.stopRobot()
                self.stateMachine.change_state('SC', 'Holding', 'Held')

            elif execute_state == 'Unholding':
                self.stateMachine.change_state('SC', 'Unholding', 'Execute')
                self.refill_blue = 18
                self.refill_red = 18
                self.refill_yellow = 18

            #elif execute_state == 'Suspending':
            #    self.stateMachine.change_state('SC', 'Suspending', 'Suspended')

            #elif execute_state == 'Suspended':
            #    self.stateMachine.change_state('Unsuspend', 'Suspended', 'Unsuspending')

            #elif execute_state == 'Unsuspending':
            #    self.stateMachine.change_state('SC', 'Unsuspending', 'Execute')

            # TODO: REMOVE THIS SLEEP WHEN NOT TESTING ANYMORE
            time.sleep(1)



