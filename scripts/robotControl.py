import rtde_control
import rtde_receive
import time, json

#over camera/pregrasp: [-1.8969367186175745, -2.0070206127562464, -2.13478946685791, 4.114851637477539, -1.5151179472552698, -1.5469110647784632]
#Large brick grasp: [-1.8101142088519495, -2.1542002163329066, -1.856816291809082, 4.01967112600293, -1.4238227049456995, -1.5479300657855433]
#Medium brick grasp: [-1.9142192045794886, -2.168049474755758, -1.8302984237670898, 4.0065552431293945, -1.527867619191305, -1.547138516102926]
#small brick grasp: [-2.0131247679339808, -2.18654265026235, -1.794539451599121, 3.989055796260498, -1.6267221609698694, -1.5463479200946253]
#over box grasp: [-1.6843403021441858, -1.7713800869383753, -2.538630485534668, 4.318931265468262, -1.2982853094684046, -1.547690216694967]

class RobotControl:
    def __init__(self):
        self.rtde_c = rtde_control.RTDEControlInterface("192.168.0.99")
        self.rtde_r = rtde_receive.RTDEReceiveInterface("192.168.0.99")
        self.velocity = 0.5
        self.acceleration = 1.2

    def moveRobot(self, pose, vel, acc):
        self.velocity = vel
        self.acceleration = acc
        self.rtde_c.moveJ(pose, self.velocity, self.acceleration)

    def moveRobot(self, pose):
        self.rtde_c.moveJ(pose, self.velocity, self.acceleration)

    def moveRobot(self, graspConfigString):
        datastore = ""
        with open("../scripts/PPP/grasp_config.json", 'r') as f:
            try:
                datastore = json.load(f)
            except ValueError as e:
                print("Cannot retrieve json, got the following error: " + e)

        pose = datastore[[str(graspConfigString)]["q"]]
        self.rtde_c.moveJ(pose, self.velocity, self.acceleration)

    def getQ(self):
        return self.rtde_r.getActualQ()

    def stopRobot(self):
        self.rtde_c.stopRobot()

    def speedStop(self):
        self.rtde_c.speedStop()