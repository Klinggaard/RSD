import threading
import time

from scripts.modbus.modbus_client import Client
from scripts.RobotControl import RobotControl
from scripts.RestMiR import RestMiR
from scripts.MesOrder import MesOrder
from scripts.finite_state_machine import FiniteStateMachine as FSM
import logging
import json

BLUE, RED, YELLOW, ERROR = (i for i in range(4))


class ExecuteOrder():

    def __init__(self):
        self.robot = RobotControl.getInstance()
        logging.info("[PackOrders] Connecting to ModBus")
        self.modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
        if not self.modbus_client:
            logging.ERROR("[PackOrders] Cannot connect to modbus")
        self.modbus_client.connect()
        self.stateMachine = FSM.getInstance()
        logging.info("[PackOrders] Connecting to MiR")
        self.mir = RestMiR()
        logging.info("[PackOrders] Connecting to MES server")
        self.db_orders = MesOrder()

        self.refill_yellow = 18
        self.refill_red = 18
        self.refill_blue = 18
        self.current_order = False
        self.order_counter = 0
        self.order_prepared = False

    def prepare_orders(self):
        while self.order_counter < 4:
            if not self.current_order:
                do_order = self.db_orders.get_put_order()
                self.current_order = True

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
                    logging.error("[MainThread] Error, Modbus client / camera problem")
                    self.robot.dumpBrick()
                if verify == YELLOW:
                    self.robot.putInBox(self.order_counter)
                    yellows -= 1
                    self.refill_yellow -= 1
                else:
                    self.robot.dumpBrick()
                    self.refill_yellow -= 1
                    logging.info("[MainThread] Block has different color than expected - toss it out")
                if self.refill_yellow == 0:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("[MainThread] Fill in yellow blocks container")

            while reds > 0:
                if self.stateMachine.state != "Execute":
                    break
                self.robot.graspRed()
                self.modbus_client.connect()
                verify = self.modbus_client.get_brick_colours()[0]
                if verify == 3:
                    logging.error("[MainThread] Error, Modbus client / camera problem")
                    self.robot.dumpBrick()
                if verify == 1:
                    self.robot.putInBox(self.order_counter)
                    reds -= 1
                    self.refill_red -= 1
                elif verify != 1:
                    self.robot.dumpBrick()
                    self.refill_red -= 1
                    logging.info("[MainThread] Block has different color than expected - toss it out")
                if self.refill_red == 0:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("[MainThread] Fill in red blocks container")

            while blues > 0:
                if self.stateMachine.state != "Execute":
                    break
                self.robot.graspBlue()
                self.modbus_client.connect()
                verify = self.modbus_client.get_brick_colours()[0]
                if verify == 3:
                    logging.error("[MainThread] Error, Modbus client / camera problem")
                    # add tossing out or going into hold state
                    self.robot.dumpBrick()
                if verify == 0:
                    self.robot.putInBox(self.order_counter)
                    blues -= 1
                    self.refill_blue -= 1
                elif verify != 0:
                    self.robot.dumpBrick()
                    self.refill_blue -= 1
                    logging.info("[MainThread] Block has different color than expected - toss it out")
                if self.refill_blue == 0:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("[MainThread] Fill in blue blocks container")

            if self.stateMachine.state != "Execute":
                break
            if self.robot.isEmergencyStopped():
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                return False

            logging.info("Sub-order completed")
            self.order_counter += 1
            self.db_orders.delete_order(do_order)
            # 3rd order ready, call MIR
            if self.order_counter == 2 and self.stateMachine.state == 'Execute':
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
        self.order_counter = 0
        self.order_prepared = True
        #self.modbus_client.close() # we connect when class object is created

    def pack_orders(self):
        while self.mir.read_register(6) != 1:
            logging.info("Wait for MIR")
        # START PACKING
        self.robot.loadUnloadMIR()
        # DONE PACKING
        self.mir.write_register(6, 0)  # MIR can go
        logging.info("MIR departures")

    def main_thread_loop(self):
        while True:

            #Running: RT = 2, SM = 1
            #Emergncy: RT = 4, SM = 7
            #Cleared: RT 4, SM = 1

            time.sleep(1)
            if self.robot.isEmergencyStopped() and self.stateMachine.state != 'Aborted':
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
            execute_state = self.stateMachine.state
            print("[State] : ", self.stateMachine.state)
            if execute_state == 'Starting':
                self.stateMachine.change_state('SC', 'Starting', 'Execute')
            if execute_state == 'Idle':
                pass
            elif execute_state == 'Execute':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                elif not self.order_prepared:
                    self.prepare_orders()
                else:
                    self.stateMachine.change_state('Suspend', 'Execute', 'Suspending')
            elif execute_state == 'Completing':
                self.stateMachine.change_state('SC', 'Completing', 'Complete')
            elif execute_state == 'Complete':
                self.stateMachine.change_state('Reset', 'Complete', 'Resetting')
            elif execute_state == 'Resetting':
                self.robot.moveRobot("Reset")  # to discuss if we want to do it here or after trigger
                self.robot.openGripper()
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                self.stateMachine.change_state('SC', 'Resetting', 'Idle')
            elif execute_state == 'Aborting':
                self.stateMachine.change_state('SC', 'Aborting', 'Aborted')
            elif execute_state == 'Aborted':
                if not self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Clear', 'Aborted', 'Clearing')
            elif execute_state == 'Clearing':
                if self.robot.getRuntimeState() == 4 or self.robot.getRuntimeState() == 1:
                    self.robot.reInitializeRTDE()
                    self.robot.reconnect()
                if self.robot.getRuntimeState() == 2:
                    self.stateMachine.change_state('SC', 'Clearing', 'Stopped')
            elif execute_state == 'Stopping':
                self.stateMachine.change_state('SC', 'Stopping', 'Stopped')
            elif execute_state == 'Holding':
                self.robot.moveRobot("Reset")
                self.robot.openGripper()
                self.stateMachine.change_state('SC', 'Holding', 'Held')
            elif execute_state == 'Unholding':
                self.refill_blue = 18
                self.refill_red = 18
                self.refill_yellow = 18
                self.stateMachine.change_state('SC', 'Unholding', 'Execute')
            elif execute_state == 'Suspending':
                self.stateMachine.change_state('SC', 'Suspending', 'Suspended')
            elif execute_state == 'Suspended':
                self.pack_orders()
                self.order_prepared = False #Set the order prepared to false after it has been packed
                self.stateMachine.change_state('Unsuspend', 'Suspended', 'Unsuspending')
            elif execute_state == 'Unsuspending':
                self.order_prepared = False
                self.stateMachine.change_state('SC', 'Unsuspending', 'Execute')
