from scripts.robotControl import RobotControl
import time

from scripts.modbus_client import Client
from scripts.robotControl import RobotControl
from Rest_MiR import Rest_MiR
from scripts.clienttest import MesOrder

mes = MesOrder()
mes.get_put_order()


#robot = RobotControl()
#Yellow pregrasp: [-1.803497616444723, -2.109267850915426, -1.9879026412963867, 4.164214773769043, -1.4250472227679651, -1.5656560103045862]
#red Pregrasp: [-1.9112704435931605, -2.1204258404173792, -1.9661626815795898, 4.152594252223633, -1.5325735251056116, -1.5585368315326136]
#blue pregrasp:[-2.0210230986224573, -2.1399675808348597, -1.9278478622436523, 4.133639021510742, -1.642069164906637, -1.5513938109027308]
#yellow grasp:[-1.8129132429706019, -2.158292909661764, -1.891798973083496, 4.117009802455566, -1.4344127813922327, -1.5652244726764124]
#red grasp:[-1.9157775084124964, -2.169213434258932, -1.8703527450561523, 4.10557143270459, -1.5370038191424769, -1.5584405104266565]
#blue grasp:[-2.0179665724383753, -2.185594221154684, -1.837937355041504, 4.089404745692871, -1.6389926115619105, -1.5517891089068812]
#Over camera:[-1.8916152159320276, -2.0121876202025355, -2.1760873794555664, 4.2543989855, -1.513028923665182, -1.559387509022848]

#robot.putInBox()

# robot.moveRobot("BluePreGrasp")
# robot.moveRobot("BlueGrasp")

# while True:
#     robot.graspBlue()
#     robot.putInBox()
#
#     robot.graspRed()
#     robot.putInBox()
#
# robot.graspYellow()
# robot.graspBlue()
#robot.graspRed()
#     robot.putInBox()


#Connect to modbus
# modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
# modbus_client.connect()
#
# print("modbus result: ", modbus_client.get_brick_colours()[0])