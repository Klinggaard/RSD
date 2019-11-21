from scripts.MesOrder import MesOrder
import requests
import json
import time
from scripts.RobotControl import RobotControl
from scripts.finite_state_machine import FiniteStateMachine as FSM
#mes = MesOrder()
#mes.get_put_order()

#
# robot = RobotControl()
# #robot.putInBox(0)
# robot.velocity = 0.8
# robot.takeBoxesFromFeeder()
# robot.moveRobot("TEST")
# robot.putBoxesInFeeder()
#
# while True:
#     robot.takeBoxesFromFeeder()
#     robot.moveRobot("TEST")
#     robot.putBoxesInFeeder()
#     time.sleep(0.5)

#TEST OF STATEMACHING USING SINGLETON
stateMachine = FSM(FSM.states_packml, FSM.transition)
print("SM1: " , stateMachine.state)
stateMachine.change_state('Start', 'Idle', 'Starting')

stateMachine2 = FSM.getInstance()

print("SM1: " , stateMachine.state)
print("SM2: " , stateMachine2.state)
stateMachine2.change_state('SC', 'Starting', 'Execute')

print("SM1: " , stateMachine.state)
print("SM2: " , stateMachine2.state)




#Yellow pregrasp: [-1.803497616444723, -2.109267850915426, -1.9879026412963867, 4.164214773769043, -1.4250472227679651, -1.5656560103045862]
#red Pregrasp: [-1.9112704435931605, -2.1204258404173792, -1.9661626815795898, 4.152594252223633, -1.5325735251056116, -1.5585368315326136]
#blue pregrasp:[-2.0210230986224573, -2.1399675808348597, -1.9278478622436523, 4.133639021510742, -1.642069164906637, -1.5513938109027308]
#yellow grasp:[-1.8129132429706019, -2.158292909661764, -1.891798973083496, 4.117009802455566, -1.4344127813922327, -1.5652244726764124]
#red grasp:[-1.9157775084124964, -2.169213434258932, -1.8703527450561523, 4.10557143270459, -1.5370038191424769, -1.5584405104266565]
#blue grasp:[-2.0179665724383753, -2.185594221154684, -1.837937355041504, 4.089404745692871, -1.6389926115619105, -1.5517891089068812]
#Over camera:[-1.8916152159320276, -2.0121876202025355, -2.1760873794555664, 4.2543989855, -1.513028923665182, -1.559387509022848]


#[-1.5170014540301722, -1.8291217289366664, -2.2756662368774414, 4.1437341409870605, -1.1269868055926722, -0.9615510145770472] b3
#[-1.573902432118551, -1.9200340710081996, -2.1352434158325195, 4.093268080348633, -1.1838343779193323, -0.9594185988055628] b2
#[-1.708949391041891, -1.9418302975096644, -2.30062198638916, 4.278164549464844, -1.3191388289081019, -0.9533689657794397] b1
#[-1.7428534666644495, -2.0182868442931117, -2.156460762023926, 4.210152311916016, -1.3529866377459925, -0.9524453322040003] b0

#Pre box 0-1 grasp:  [-1.9551776091205042, -2.0517031155028285, -1.9313173294067383, 5.59340380409316, 2.3160595893859863, 0.007204532623291016]
#Grasp box 0-1: [-1.8224509398089808, -2.107445379296774, -1.9647588729858398, 5.773718821793356, 2.191310405731201, 0.1647167205810547]


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