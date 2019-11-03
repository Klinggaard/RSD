#!/usr/bin/env python
from pymodbus.client.sync import ModbusTcpClient as ModbusClient


def read_registers(client, address, amount=1):
    '''
    :param client: A ModbusTcpClient
    :param address: The first address
    :param amount: The amount of registers that should be read
    :return: A list of the values read
    '''
    return client.read_holding_registers(address, amount).registers


def write_register(client, address, val):
    '''
    :param client: A ModbusTcpClient
    :param address: The first address
    :param val: a list of values to be written

    NOTE:
    It is possible to write to more than one register by parsing a list with more than one object
    '''
    client.write_registers(address, val)


if __name__ == "__main__":
    client = ModbusClient('localhost', port=5020)

    client.connect()

    write_register(client, 0, [1,2,3])
    print(read_registers(client,0,3))

    client.close()