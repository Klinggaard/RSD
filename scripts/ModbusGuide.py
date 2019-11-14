"""
This is an example code for the people who want to connect via modbus.

The Client class inherent all functionality from ModbusTcpClient
but add a function to make reading holding registers easier
"""

from scripts.modbus_client import Client

c = Client(ip="192.168.0.20", port=5020)  # The port will stay 5020

#while not c.connect():  # connects the client to the server
print(c.connect())
print(c.get_brick_colours())

c.close()  # closing the client - NOT NECESSARY
