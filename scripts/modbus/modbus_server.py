#!/usr/bin/env python3
'''
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
'''
#---------------------------------------------------------------------------#
# import the modbus libraries we need
#---------------------------------------------------------------------------#
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

#---------------------------------------------------------------------------#
# import the twisted libraries we need
#---------------------------------------------------------------------------#
from twisted.internet.task import LoopingCall

#---------------------------------------------------------------------------#
# import image related libraries
#---------------------------------------------------------------------------#
import cv2 as cv
from scripts.imageprocessing.image_processing import check_bricks

#---------------------------------------------------------------------------#
# configure the service logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# define your callback process
#---------------------------------------------------------------------------#


def get_coils(slave, address, n):
    ''' Returns a list of coils

    :param slave: A client context
    :param address: The starting address
    :param n: The amount of values to retrieve
    :return: The requested values from address:address+n
    '''
    return slave.getValues(1, address, n)  # 1 is defined by pymodbus


def set_coils(slave, address, value):
    ''' Sets coils to value

    :param slave: A client context
    :param address: The starting address
    :param value: List of values
    '''
    slave.setValues(1, address, value)  # 1 is defined by pymodbus


def get_holdings(slave, address, n):
    ''' Returns a list of holding registers

    :param slave: A client context
    :param address: The starting address
    :param n: The amount of values to retrieve
    :return: The requested values from address:address+n
    '''
    return slave.getValues(3, address, n)  # 3 is defined by pymodbus


def set_holdings(slave, address, value):
    ''' Sets registers to value

    :param slave: A client context
    :param address: The starting address
    :param value: List of values
    '''
    slave.setValues(3, address, value)  # 3 is defined by pymodbus


def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    '''
    log.debug("updating the context")
    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 0x10
    #print(get_coils(context[slave_id], 0, 1), "\n", get_holdings(context[slave_id], 0, 3))
    if get_coils(context[slave_id], 0, 1)[0]:  # System asked for brick info
        colours = check_bricks()
        set_holdings(context[slave_id], 0, colours)
        set_coils(context[slave_id], 0, [False])

#---------------------------------------------------------------------------#
# initialize your data store
#---------------------------------------------------------------------------#
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*2),
    co=ModbusSequentialDataBlock(0, [False]*2),
    hr=ModbusSequentialDataBlock(0, [1]*4),
    ir=ModbusSequentialDataBlock(0, [0]*2))
context = ModbusServerContext(slaves=store, single=True)

#---------------------------------------------------------------------------#
# initialize the server information
#---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName  = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'

#---------------------------------------------------------------------------#
# run the server you want
#---------------------------------------------------------------------------#
time = 0.1 # 5 seconds delay
loop = LoopingCall(f=updating_writer, a=(context,))
loop.start(time, now=False) # initially delay by time
StartTcpServer(context, identity=identity, address=("192.168.0.20", 5020))
