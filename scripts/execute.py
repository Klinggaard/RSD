from scripts.modbus.modbus_client import Client
from scripts.RobotControl import RobotControl
from scripts.RestMiR import RestMiR
from scripts.MesOrder import MesOrder

modbus_client = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020
robot = RobotControl()
mir = RestMiR()
db_orders = MesOrder()
modbus_client.connect()

for order_counter in range(4):
    do_order = db_orders.get_put_order()

    #Dummy order
    #with open("../scripts/PPP/grasp_config.json", 'r') as f:
    #    datastore = json.load(f)
    #do_order = datastore["DummyOrder"]

    reds = do_order["red"]
    blues = do_order["blue"]
    yellows = do_order["yellow"]
    while yellows > 0:
        robot.graspYellow()
        verify = modbus_client.get_brick_colours()[0]
        print("VERIFY: ", verify)
        if verify == 3:
            print("Error, Modbus client / camera problem")
            # add tossing out or going into hold state
        if verify == 2:
            robot.putInBox()
            # add letting go of a block
            # add different positions for different boxes
            yellows -= 1
        elif verify != 2:
            print("Block has different color than expected - toss it out")
            # add tossing out
    while reds > 0:
        robot.graspRed()
        modbus_client.connect()
        verify = modbus_client.get_brick_colours()[0]
        if verify == 3:
            print("Error, Modbus client / camera problem")
            # add tossing out or going into hold state
        if verify == 1:
            robot.putInBox()
            # add different positions for different boxes
            reds -= 1
        elif verify != 1:
            print("Block has different color than expected - toss it out")
            # add tossing out
    while blues > 0:
        robot.graspBlue()
        modbus_client.connect()
        verify = modbus_client.get_brick_colours()[0]
        if verify == 3:
            print("Error, Modbus client / camera problem")
            # add tossing out or going into hold state
        if verify == 0:
            robot.putInBox()
            # add different positions for different boxes
            blues -= 1
        elif verify != 0:
            print("Block has different color than expected - toss it out")
            # add tossing out
    if blues == 0 and yellows == 0 and reds == 0:
        print("Sub-order completed")
        db_orders.delete_order(do_order)
#    if order_counter == 2:
#       mir_mission = mir.get_mission("GoTo6")
#       mir.add_mission_to_queue(mir_mission)
# we calculate based on how many times we delete an order, can be done in a lot of ways
#print("Number of completed orders: " + str(db_orders.counter % 4))
'''
while mir.read_register(1) != 1: # wait for MIR to arrive
mir.read_register(1)
# add function to put boxes on MIR & flag to make sure we are done with packing
mir.write_register(1, 0)  # MIR can go
mir.write_register(2, 1)  # MIR go to base
# change state to completing
'''





