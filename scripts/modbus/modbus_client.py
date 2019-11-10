#!/usr/bin/env python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import time


class Client(ModbusClient):
    def __init__(self, ip="localhost", port=5020):
        super().__init__(host=ip, port=port)

    def read_registers(self, address, amount=1):
        '''
        :param client: A ModbusTcpClient
        :param address: The first address
        :param amount: The amount of registers that should be read
        :return: A list of the values read
        '''
        return self.read_holding_registers(address, amount).registers

    def get_brick_colours(self):
        """

        :return: A list of colour codes
        """
        self.write_coil(0, True)  # Setting coil 0 to True will tell the RPi to take and process and image
        while self.read_coils(0, 1):  # RPi working - coil will be set to False when RPi is done
            time.sleep(0.3)

        return self.read_registers(address=3, amount=3)
