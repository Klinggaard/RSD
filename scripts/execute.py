from scripts.modbus.modbus_client import Client
from scripts.RobotControl import RobotControl
from scripts.RestMiR import RestMiR
from scripts.MesOrder import MesOrder
from scripts.finite_state_machine import FiniteStateMachine as FSM
import logging


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
        self.robot.velocity = 0.25

        self.refill_yellow = 18
        self.refill_red = 18
        self.refill_blue = 18
        self.current_order = False
        self.order_counter = 0
        self.order_prepared = False
        self.order_packed = False
        self.waiting_for_mir = False
        self.fail_to_call_mir = False
        self.reds = 0
        self.blues = 0
        self.yellows = 0
        self.do_order = []
        self.full_orders = 0

    def prepare_orders(self):
        while self.order_counter < 4:
            self.order_prepared = False
            if not self.current_order:
                self.do_order = self.db_orders.get_put_order()
                self.current_order = True
                self.reds = self.do_order["red"]
                self.blues = self.do_order["blue"]
                self.yellows = self.do_order["yellow"]

            while self.yellows > 0:
                if self.stateMachine.state != "Execute":
                    break
                if self.refill_yellow > 0:
                    self.robot.graspYellow()
                    verify = self.modbus_client.get_brick_colours()[0]
                    if verify == ERROR:
                        logging.error("[MainThread] Error, Modbus client / camera problem")
                        self.robot.dumpBrick()
                        self.refill_yellow -= 1
                    if verify == YELLOW:
                        self.robot.putInBox(self.order_counter)
                        self.yellows -= 1
                        self.refill_yellow -= 1
                    else:
                        self.robot.dumpBrick()
                        self.refill_yellow -= 1
                        logging.info("[MainThread] Block has different color than expected - toss it out")
                    if self.refill_yellow == 0:
                        self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                        logging.info("[MainThread] Fill in yellow blocks container")
                else:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("[MainThread] Fill in yellow blocks container")

            while self.reds > 0:
                if self.stateMachine.state != "Execute":
                    break
                if self.refill_red > 0:
                    self.robot.graspRed()
                    self.modbus_client.connect()
                    verify = self.modbus_client.get_brick_colours()[0]
                    if verify == 3:
                        logging.error("[MainThread] Error, Modbus client / camera problem")
                        self.robot.dumpBrick()
                        self.refill_red -= 1
                    if verify == 1:
                        self.robot.putInBox(self.order_counter)
                        self.reds -= 1
                        self.refill_red -= 1
                    elif verify != 1:
                        self.robot.dumpBrick()
                        self.refill_red -= 1
                        logging.info("[MainThread] Block has different color than expected - toss it out")
                    if self.refill_red == 0:
                        self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                        logging.info("[MainThread] Fill in red blocks container")
                else:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("[MainThread] Fill in red blocks container")

            while self.blues > 0:
                if self.stateMachine.state != "Execute":
                    break
                if self.refill_blue > 0:
                    self.robot.graspBlue()
                    self.modbus_client.connect()
                    verify = self.modbus_client.get_brick_colours()[0]
                    if verify == 3:
                        logging.error("[MainThread] Error, Modbus client / camera problem")
                        self.robot.dumpBrick()
                        self.refill_blue -= 1
                    if verify == 0:
                        self.robot.putInBox(self.order_counter)
                        self.blues -= 1
                        self.refill_blue -= 1
                    elif verify != 0:
                        self.robot.dumpBrick()
                        self.refill_blue -= 1
                        logging.info("[MainThread] Block has different color than expected - toss it out")
                    if self.refill_blue == 0:
                        self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                        logging.info("[MainThread] Fill in blue blocks container")
                else:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("[MainThread] Fill in blue blocks container")

            if self.stateMachine.state != "Execute":
                break
            if self.robot.isEmergencyStopped():
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                return False

            logging.info("[MainThread] Sub-order completed")
            self.order_counter += 1
            self.db_orders.delete_order(self.do_order)

            # 3rd order ready, call MIR
            if self.order_counter == 3 and self.stateMachine.state == 'Execute':
                try:
                    guid = self.mir.get_mission("GoTo6")
                    self.mir.add_mission_to_queue(guid)
                except ():
                    logging.info("[MainThread] Calling MIR unsuccessful")
                    self.stateMachine.change_state('Stop', 'Execute', 'Stopping')
                    self.fail_to_call_mir = True
                else:
                    logging.info("[MainThread] MIR ordered")
                    self.waiting_for_mir = True

            # if we failed to call MIR before
            if self.order_counter == 4 and self.fail_to_call_mir and self.stateMachine.state == 'Execute':
                try:
                    guid = self.mir.get_mission("GoTo6")
                    self.mir.add_mission_to_queue(guid)
                except ():
                    logging.info("[MainThread] Calling MIR again unsuccessful")
                    self.stateMachine.change_state('Stop', 'Execute', 'Stopping')
                else:
                    logging.info("[MainThread] MIR ordered")
                    self.waiting_for_mir = True
                    self.fail_to_call_mir = False

            self.current_order = False
            if self.order_counter == 4:
                self.order_counter = 0
                self.order_prepared = True
                break

    def pack_orders(self):
        if self.stateMachine.state == "Execute":
            self.order_packed = False
            self.robot.loadUnloadMIR()
            self.mir.write_register(6, 0)  # MIR can go
            self.order_packed = True
            logging.info("[MainThread] MIR departures")
        else:
            logging.info("[MainThread] Go to stop, as packing_orders must be done in Execute state")
            self.stateMachine.change_state('Stop', 'Execute', 'Stopping')

    def main_thread_loop(self):
        while True:
            if self.robot.isEmergencyStopped() and self.stateMachine.state != 'Aborted':
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
            execute_state = self.stateMachine.state
            print("[State] : ", self.stateMachine.state)

            if execute_state == 'Starting':
                self.robot.moveRobot("Reset")
                self.robot.openGripper()
                self.stateMachine.change_state('SC', 'Starting', 'Execute')

            if execute_state == 'Idle':
                pass

            elif execute_state == 'Execute':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                elif self.full_orders <= 1000:
                    if not self.order_prepared:
                        self.prepare_orders()
                    if self.waiting_for_mir:
                        if self.mir.read_register(6) == 1:
                            if not self.order_packed:
                                self.pack_orders()
                        if self.mir.read_register(6) == 0 and not self.order_packed:
                            self.stateMachine.change_state('Suspend', 'Execute', 'Suspending')
                    if self.order_prepared and self.order_packed:
                        self.order_prepared = False
                        self.order_packed = False
                        self.waiting_for_mir = False
                        self.full_orders += 1
                if self.full_orders > 1000:
                    self.stateMachine.change_state('SC', 'Execute', 'Completing')

            elif execute_state == 'Completing':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.stateMachine.change_state('SC', 'Completing', 'Complete')

            elif execute_state == 'Complete':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.stateMachine.change_state('Reset', 'Complete', 'Resetting')

            elif execute_state == 'Resetting':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.robot.moveRobot("Reset")  # to discuss if we want to do it here or after trigger
                    self.robot.openGripper()
                    self.stateMachine.change_state('SC', 'Resetting', 'Idle')
                    if self.order_prepared and not self.waiting_for_mir:
                        self.waiting_for_mir = True

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
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.robot.moveRobot("Reset")
                    self.robot.openGripper()
                    self.stateMachine.change_state('SC', 'Holding', 'Held')

            elif execute_state == 'Unholding':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.refill_blue = 18
                    self.refill_red = 18
                    self.refill_yellow = 18
                    self.stateMachine.change_state('SC', 'Unholding', 'Execute')

            elif execute_state == 'Suspending':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.stateMachine.change_state('SC', 'Suspending', 'Suspended')

            elif execute_state == 'Suspended':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    if self.mir.read_register(6) != 1:
                        logging.info("[MainThread] Waiting for MIR")
                        print("[State] : ", self.stateMachine.state)
                    if self.mir.read_register(6) == 1:
                        logging.info("MIR arrived")
                        self.stateMachine.change_state('Unsuspend', 'Suspended', 'Unsuspending')

            elif execute_state == 'Unsuspending':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                else:
                    self.stateMachine.change_state('SC', 'Unsuspending', 'Execute')

            elif execute_state == 'Held':
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
