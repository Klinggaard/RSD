import rtde_control
import rtde_receive
import rtde_io
import time, json
import logging
import rootpath

class RobotControl:

    __instance = None  # INITIAL INSTANCE OF CLASS

    @staticmethod
    def getInstance():
        """ Static access method. """
        if RobotControl.__instance == None:
            RobotControl()
        return RobotControl.__instance

    def __init__(self):
        self.rtde_c = None
        self.rtde_r = None
        self.rtde_i = None
        try:
            self.rtde_c = rtde_control.RTDEControlInterface("192.168.0.99")
            self.rtde_r = rtde_receive.RTDEReceiveInterface("192.168.0.99")
            self.rtde_i = rtde_io.RTDEIOInterface("192.168.0.99")
        except RuntimeError:
            logging.error("[RobotControl] Cannot connect to Universal robot")

        self.velocity = 0.5
        self.acceleration = 1.2
        self.datastore = ""
        projectPath = rootpath.detect()
        with open(projectPath + "/scripts/PPP/grasp_config.json", 'r') as f:
            self.datastore = json.load(f)

        """ Virtually private constructor. """
        if RobotControl.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            RobotControl.__instance = self

    def moveRobotPath(self, graspConfigList):
        if self.isEmergencyStopped():
            return False
        path = []
        stats = None
        point = None
        for graspConfig in graspConfigList:
            point = self.datastore[str(graspConfig)]['q']
            stats = [self.velocity, self.acceleration, 0.1] #[VEL, ACC, BLEND]
            path.append(point+stats)

        #Set the blend in the endpoint to 0
        path[0][8] = 0
        path[len(graspConfigList)-1][8] = 0

        return self.rtde_c.moveJ(path)

    def lights(self, l1=False, l2=False, l3=False):
        try:
            self.rtde_i.setStandardDigitalOut(1, l1)
            self.rtde_i.setStandardDigitalOut(2, l2)
            self.rtde_i.setStandardDigitalOut(3, l3)
        except AttributeError:
            logging.error("[RobotControl] Cannot set IO, not connected to Universal Robot")

    def readInputBits(self):
        return self.rtde_r.getActualDigitalInputBits()

    def moveRobot(self, graspConfigString):
        if self.isEmergencyStopped():
            return False
        pose = self.datastore[str(graspConfigString)]["q"]
        self.rtde_c.moveJ(pose, self.velocity, self.acceleration)

    def graspYellow(self):
        self.openGripper()
        self.moveRobot("YellowPreGrasp")
        self.moveRobot("YellowGrasp")
        self.closeGripper()
        self.moveRobot("YellowPreGrasp")
        self.moveRobot("OverCameraPose")

    def graspRed(self):
        self.openGripper()
        self.moveRobot("RedPreGrasp")
        self.moveRobot("RedGrasp")
        self.closeGripper()
        self.moveRobot("RedPreGrasp")
        self.moveRobot("OverCameraPose")

    def graspBlue(self):
        self.openGripper()
        self.moveRobot("BluePreGrasp")
        self.moveRobot("BlueGrasp")
        self.closeGripper()
        self.moveRobot("BluePreGrasp")
        self.moveRobot("OverCameraPose")

    def takeBoxesFromFeeder(self):
        self.moveRobot("BoxPreGrasp")
        self.openGripper()
        self.moveRobot("BoxGrasp")
        self.closeGripper()
        self.moveRobot("BoxPreGrasp")

    def putBoxesInFeeder(self):
        self.moveRobot("PostFeeder")
        self.velocity = 0.3
        self.moveRobot("PreFeeder")
        self.moveRobot("PutFeeder")
        self.openGripper()
        self.moveRobot("PreFeeder")
        self.velocity = 0.5
        self.moveRobot("PostFeeder")

    def putInBox(self, boxNumber):
        self.velocity = 1.5
        self.acceleration = 3
        if(boxNumber == 0 or boxNumber == 1 or boxNumber == 2 or boxNumber == 3):
            self.moveRobot("OverBox"+str(boxNumber))
            self.openGripper()
        else:
            logging.error("[RobotControl] Invalid box number")
        self.velocity = 0.5
        self.acceleration = 1.2

    def getRuntimeState(self):
        return self.rtde_r.getRuntimeState()

    def getSafetyMode(self):
        return self.rtde_r.getSafetyMode()

    def reconnect(self):
        while not self.rtde_r.isConnected():
            self.rtde_r.reconnect()
        while not self.rtde_c.isConnected():
            self.rtde_c.reconnect()

    def isEmergencyStopped(self):
        if self.rtde_r.getSafetyMode() == 7:
            return True
        return False

    def reInitializeRTDE(self):
        self.rtde_c = None
        self.rtde_r = None
        self.rtde_i = None
        try:
            self.rtde_c = rtde_control.RTDEControlInterface("192.168.0.99")
            self.rtde_r = rtde_receive.RTDEReceiveInterface("192.168.0.99")
            self.rtde_i = rtde_io.RTDEIOInterface("192.168.0.99")
        except RuntimeError:
            logging.error("[RobotControl] Cannot connect to Universal robot")

    def loadUnloadMIR(self):
        drop0 = ["Load0", "Load1", "Load2", "LoadMir", "MirDropZonePre0", "MirDropZone0"]
        drop1 = ["Load0", "Load1", "Load2", "LoadMir", "MirDropZonePre1", "MirDropZone1"]
        reversePath = ["LoadMir", "Load2", "Load1", "Load0"]
        self.takeBoxesFromFeeder()
        self.moveRobotPath(drop0)
        self.openGripper()
        self.moveRobotPath((["MirDropZonePre0"] + reversePath))
        self.takeBoxesFromFeeder()
        self.moveRobotPath(drop1)
        self.openGripper()

        # Push the boxes together
        self.moveRobot("PushPreUp")
        self.moveRobot("PushPre")
        self.moveRobot("Push")
        self.moveRobot("PushUp")

        # grasp box on mir
        self.moveRobot("MirBoxPreGrasp0")
        self.velocity = 0.3
        self.moveRobot("MirBoxGrasp0")
        self.closeGripper()
        self.moveRobot("MirBoxPreGrasp0")

        # Load the boxes to the feeder
        self.velocity = 0.5
        self.moveRobotPath(reversePath + ["PostFeeder"])
        self.putBoxesInFeeder()

        # make sure the gripper is open
        self.openGripper()

        # move robot to mir
        path = ["Load0", "Load1", "Load2", "LoadMir", "PushPreUp"]
        self.moveRobotPath(path)

        # grasp box on mir
        self.moveRobot("MirBoxPreGrasp1")
        self.velocity = 0.3
        self.moveRobot("MirBoxGrasp1")
        self.closeGripper()
        self.moveRobot("MirBoxPreGrasp1")

        # Load the boxes to the feeder
        self.velocity = 0.5
        self.moveRobotPath(reversePath + ["PostFeeder"])
        self.putBoxesInFeeder()

    def dumpBrick(self):
        self.moveRobot("Dump")
        self.openGripper()

    def closeGripper(self):
        if self.isEmergencyStopped():
            return False
        return self.rtde_i.setStandardDigitalOut(0, False)

    def openGripper(self):
        if self.isEmergencyStopped():
            return False
        return self.rtde_i.setStandardDigitalOut(0, True)

    def getQ(self):
        return self.rtde_r.getActualQ()