from scripts.OEE import OEE
from scripts.modbus.modbus_client import Client
from scripts.RobotControl import RobotControl
from scripts.RestMiR import RestMiR
from scripts.MesOrder import MesOrder
from scripts.finite_state_machine import FiniteStateMachine as FSM
import logging
import time


BLUE, RED, YELLOW, ERROR = (i for i in range(4))


class ExecuteOrder():

    def __init__(self):
        self.robot = RobotControl.getInstance()
        logging.info("PackOrders : " + " Connecting to ModBus")
        self.modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
        if not self.modbus_client:
            logging.ERROR("PackOrders : " + " Cannot connect to modbus")
        self.modbus_client.connect()
        self.stateMachine = FSM.getInstance()
        self.stateMachine.change_state('Stop', 'Execute', 'Stopping')
        logging.info("PackOrders : " + "Connecting to MiR")
        self.mir = RestMiR()
        logging.info("PackOrders : " + "Connecting to MES server")
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
        # Init the registers on the mir
        self.mir.write_register(6, 0)
        self.mir.write_register(60, 0)
        self.mir_unloaded = False

        self.started_packing = False

        self.oeeInstance = OEE.getInstance()

    def call_mir(self):
        try:
            guid = self.mir.get_mission("GoToGr6")
            result = self.mir.add_mission_to_queue(guid)
            logging.info("MainThread :" + "  MIR ordered")
            self.waiting_for_mir = True
            return True
        except :
            logging.info("MainThread : " + "Calling MIR unsuccessful")
            self.stateMachine.change_state('Stop', 'Execute', 'Stopping')
            self.fail_to_call_mir = True
            return False

    def clear_system(self):
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
        # Init the registers on the mir
        self.mir.write_register(6, 0)
        self.mir.write_register(60, 0)
        self.mir_unloaded = False
        self.started_packing = False

    def prepare_orders(self):
        # TODO: Time this. The orders should not take more than 10 minutes. If timeout is reached, dump orders
        # self.order_counter = 0  # To ensure that we reset the order_counter if an order was not finished CANNOT DO THAT - reset it in clearing
        while self.order_counter < 4:
            self.started_packing = True
            if self.mir.is_timeout():
                self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                logging.info("Going to hold instead of preparing order because of timeout")
                if self.started_packing:  # OEE now only adds a reject if the order was started
                    self.oeeInstance.update(sys_up=True, task=self.stateMachine.state, update_order=True, order_status=OEE.REJECTED)
                mir_id = self.mir.get_mission("GoToGr6")
                self.mir.delete_from_queue(mir_id)
                break

            # TODO: check if this change is OK, I think it's enough - take care of everything in clearing
            if self.robot.isEmergencyStopped():
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                break

            if not self.current_order:
                self.do_order = self.db_orders.get_put_order()
                self.db_orders.log_order_start(self.do_order['id'])
                self.current_order = True
                self.reds = self.do_order["red"]
                self.blues = self.do_order["blue"]
                self.yellows = self.do_order["yellow"]

            # YELLOW
            while self.yellows > 0:
                # Update OEE
                self.oeeInstance.update(sys_up=True, task=self.stateMachine.state)
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                    return False
                if self.stateMachine.state != "Execute":
                    break
                if self.refill_yellow > 0:
                    self.robot.graspYellow()
                    verify = self.modbus_client.get_brick_colours()[0]
                    if verify == ERROR:
                        logging.error("MainThread : " + " Error, Modbus client / camera problem")
                        self.robot.dumpBrick()
                        self.refill_yellow -= 1
                    if verify == YELLOW:
                        self.robot.putInBox(self.order_counter)
                        self.yellows -= 1
                        self.refill_yellow -= 1
                    else:
                        self.robot.dumpBrick()
                        self.refill_yellow -= 1
                        logging.info("MainThread : " + "Block has different color than expected - toss it out")
                    if self.refill_yellow == 0:
                        self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                        logging.info("MainThread : " + " Fill in yellow blocks container")
                else:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("MainThread : " + "Fill in yellow blocks container")

            # RED
            while self.reds > 0:
                # Update OEE
                self.oeeInstance.update(sys_up=True, task=self.stateMachine.state)
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                    return False

                if self.stateMachine.state != "Execute":
                    break
                if self.refill_red > 0:
                    self.robot.graspRed()
                    self.modbus_client.connect()
                    verify = self.modbus_client.get_brick_colours()[0]
                    if verify == 3:
                        logging.error("MainThread :" + "  Error, Modbus client / camera problem")
                        self.robot.dumpBrick()
                        self.refill_red -= 1
                    if verify == 1:
                        self.robot.putInBox(self.order_counter)
                        self.reds -= 1
                        self.refill_red -= 1
                    elif verify != 1:
                        self.robot.dumpBrick()
                        self.refill_red -= 1
                        logging.info("MainThread : Block has different color than expected - toss it out")
                    if self.refill_red == 0:
                        self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                        logging.info("MainThread : " + "Fill in red blocks container")
                else:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("MainThread : " + "Fill in red blocks container")

            # BLUE
            while self.blues > 0:
                # Update OEE
                self.oeeInstance.update(sys_up=True, task=self.stateMachine.state)
                if self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                    return False
                if self.stateMachine.state != "Execute":
                    break
                if self.refill_blue > 0:

                    self.robot.graspBlue()
                    self.modbus_client.connect()
                    verify = self.modbus_client.get_brick_colours()[0]
                    if verify == 3:
                        logging.error("MainThread :" + " Error, Modbus client / camera problem")
                        self.robot.dumpBrick()
                        self.refill_blue -= 1
                    if verify == 0:
                        self.robot.putInBox(self.order_counter)
                        self.blues -= 1
                        self.refill_blue -= 1
                    elif verify != 0:
                        self.robot.dumpBrick()
                        self.refill_blue -= 1
                        logging.info("MainThread : Block has different color than expected - toss it out")
                    if self.refill_blue == 0:
                        self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                        logging.info("MainThread : Fill in blue blocks container")
                else:
                    self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                    logging.info("MainThread : Fill in blue blocks container")

            if self.stateMachine.state != "Execute":
                break
            if self.robot.isEmergencyStopped():
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')
                return False

            logging.info("MainThread : Sub-order completed")
            self.db_orders.delete_order(self.do_order)
            self.order_counter += 1
            self.db_orders.log_order_done(self.do_order['id'])
            self.current_order = False
            if self.order_counter == 4:
                self.order_counter = 0
                self.started_packing = False
                self.order_prepared = True
                break

    def pack_orders(self):
        if self.stateMachine.state == "Execute":
            self.order_packed = False
            self.robot.loadMIR()
            self.mir.release_mir()
            self.order_packed = True
            logging.info("MainThread :" + " MIR departures")
        else:
            logging.info("MainThread :" + " Go to stop, as packing_orders must be done in Execute state")
            self.stateMachine.change_state('Stop', 'Execute', 'Stopping')

    def main_thread_loop(self):
        while True:
            time.sleep(0.1)
            self.robot.reconnect()
            if self.stateMachine.state == 'Execute' and not self.robot.getSafetyMode() == 5:
                self.oeeInstance.update(sys_up=True, task=self.stateMachine.state)
            else:
                self.oeeInstance.update(sys_up=False, task=self.stateMachine.state)

            if self.robot.isEmergencyStopped() and self.stateMachine.state != 'Aborted':
                self.stateMachine.change_state('Abort', self.stateMachine.state, 'Aborting')

            execute_state = self.stateMachine.state
            logging.info("State : " + self.stateMachine.state)

            if execute_state == 'Starting':
                self.robot.moveRobot("Reset")
                self.robot.openGripper()
                self.stateMachine.change_state('SC', 'Starting', 'Execute')

            if execute_state == 'Idle':
                pass

            elif execute_state == 'Execute':
                if not self.mir.is_docked() and not self.waiting_for_mir:  # no need to go to suspend at the beginning
                    self.call_mir()
                if self.mir.is_docked():
                    if not self.order_prepared:
                        if not self.mir_unloaded:
                            self.robot.unloadMIR()
                            self.mir_unloaded = True
                            self.prepare_orders()
                        else:
                            self.prepare_orders()
                        if self.mir.get_time() < 500 and self.order_prepared:
                            self.pack_orders()
                        if self.mir.get_time() > 500 and not self.order_packed:
                            self.stateMachine.change_state('Hold', 'Execute', 'Holding')
                            logging.info("Going to hold instead of packing, not enough time, MIR departures")
                            self.oeeInstance.update(sys_up=True, task=self.stateMachine.state, update_order=True, order_status=OEE.REJECTED)
                            mir_id = self.mir.get_mission("GoToGr6")
                            self.mir.delete_from_queue(mir_id)
                if self.order_prepared and self.order_packed:
                    self.order_prepared = False
                    self.order_packed = False
                    self.waiting_for_mir = False
                    self.full_orders += 1
                    self.db_orders.log_order_done(self.do_order['id'])
                    self.mir_unloaded = False
                    self.oeeInstance.update(sys_up=True, task=self.stateMachine.state, update_order=True, order_status=OEE.COMPLETED)

                if not self.mir.is_docked() and not self.order_packed:
                    self.stateMachine.change_state('Suspend', 'Execute', 'Suspending')

            elif execute_state == 'Completing':
                self.stateMachine.change_state('SC', 'Completing', 'Complete')

            elif execute_state == 'Complete':
                self.stateMachine.change_state('Reset', 'Complete', 'Resetting')

            elif execute_state == 'Resetting':
                self.robot.moveRobot("Reset")
                self.robot.openGripper()
                self.stateMachine.change_state('SC', 'Resetting', 'Idle')
                if self.order_prepared and not self.waiting_for_mir:
                    self.waiting_for_mir = True

            elif execute_state == 'Aborting':
                if self.started_packing:
                    self.oeeInstance.update(sys_up=True, task=self.stateMachine.state, update_order=True, order_status=OEE.REJECTED)
                self.started_packing = False
                self.stateMachine.change_state('SC', 'Aborting', 'Aborted')

            elif execute_state == 'Aborted':
                if not self.robot.isEmergencyStopped():
                    self.stateMachine.change_state('Clear', 'Aborted', 'Clearing')

            # TODO: reinitalize the class or change all globals to false and so on
            elif execute_state == 'Clearing':
                self.clear_system()
                if self.robot.getRuntimeState() == 4 or self.robot.getRuntimeState() == 1:
                    self.robot.reInitializeRTDE()
                    self.robot.reconnect()
                    mir_id = self.mir.get_mission("GoToGr6")
                    self.mir.delete_from_queue(mir_id)
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
                if not self.mir.is_docked():
                    logging.info("MainThread : Waiting for MIR")
                    self.call_mir()
                    self.waiting_for_mir = True
                    time.sleep(1)
                else:
                    logging.info("MIR arrived")
                    self.waiting_for_mir = False
                    self.stateMachine.change_state('Unsuspend', 'Suspended', 'Unsuspending')

            elif execute_state == 'Unsuspending':
                self.stateMachine.change_state('SC', 'Unsuspending', 'Execute')

            elif execute_state == 'Held':
                pass
