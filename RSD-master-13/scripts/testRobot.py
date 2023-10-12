import rtde_control
import rtde_receive
import rtde_io
import time, json
import logging
import rootpath
from scripts.RobotControl import RobotControl

robot = RobotControl()

robot.moveRobot("PushPreUp")

