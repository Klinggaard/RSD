import rtde_control
import rtde_receive
import rtde_io
import time, json
import logging
import rootpath
#over camera/pregrasp: [-1.8969367186175745, -2.0070206127562464, -2.13478946685791, 4.114851637477539, -1.5151179472552698, -1.5469110647784632]
#Large brick grasp: [-1.8101142088519495, -2.1542002163329066, -1.856816291809082, 4.01967112600293, -1.4238227049456995, -1.5479300657855433]
#Medium brick grasp: [-1.9142192045794886, -2.168049474755758, -1.8302984237670898, 4.0065552431293945, -1.527867619191305, -1.547138516102926]
#small brick grasp: [-2.0131247679339808, -2.18654265026235, -1.794539451599121, 3.989055796260498, -1.6267221609698694, -1.5463479200946253]
#over box grasp: [-1.6843403021441858, -1.7713800869383753, -2.538630485534668, 4.318931265468262, -1.2982853094684046, -1.547690216694967]

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

    def moveRobot(self, pose, vel, acc):
        self.velocity = vel
        self.acceleration = acc
        self.rtde_c.moveJ(pose, self.velocity, self.acceleration)

    def moveRobotPath(self, graspConfigList):
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

        self.rtde_c.moveJ(path)

    def lights(self, l1=False, l2=False, l3=False):
        try:
            self.rtde_i.setStandardDigitalOut(1, l1)
            self.rtde_i.setStandardDigitalOut(2, l2)
            self.rtde_i.setStandardDigitalOut(3, l3)
        except AttributeError:
            logging.error("[RobotControl] Cannot set IO, not connected to Universal Robot")

    def readInputBits(self):
        return self.rtde_r.getActualDigitalInputBits()

    def moveRobot(self, pose):
        self.rtde_c.moveJ(pose, self.velocity, self.acceleration)

    def moveRobot(self, graspConfigString):
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
        if(boxNumber == 0 or boxNumber == 1 or boxNumber == 2 or boxNumber == 3):
            self.moveRobot("OverBox"+str(boxNumber))
            self.openGripper()
        else:
            logging.error("[RobotControl] Invalid box number")



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
        self.rtde_i.setStandardDigitalOut(0, False)

    def openGripper(self):
        self.rtde_i.setStandardDigitalOut(0, True)

    def getQ(self):
        return self.rtde_r.getActualQ()

    def stopRobot(self):
        self.rtde_c.stopRobot()

    def speedStop(self):
        self.rtde_c.speedStop()