# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 21:02:45 2023

@author: marti
"""

import serial
import time

serialPort = '\\\\.\\COM3'
baudrate = 1382400
timeout_ = 1
bufInputSize = 64

""" start measurement on PSoC and get data """
try: # open and interact with serial port 

    ser = serial.Serial( serialPort, baudrate, timeout=timeout_)

    ser.write( b'A' )
    time.sleep(0.001)

    
    # get data as byte stream 
    adc_data_bin = ser.read(bufInputSize)

    print( len( adc_data_bin ))
    print( adc_data_bin )
    
finally: # close serial port
    ser.close()