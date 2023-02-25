# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 21:02:45 2023

@author: marti
"""

import serial
import time

serialPort = '\\\\.\\COM3'
baudrate = 1382400
timeout_ = 0.2
bufInputSize = 60000


adc_data_direct = []
adc_data_indirect = []
""" start measurement on PSoC and get data """
try: # open and interact with serial port 

    ser = serial.Serial( serialPort, baudrate, timeout=timeout_)

    # 1) get adc data directly
    ser.write( b'A' )
    time.sleep(0.001)
    adc_data_indirect = ser.read(bufInputSize)

    # 1) get adc data directly
    ser.write( b'o' )
    time.sleep(0.001)
    adc_data_direct = ser.read(bufInputSize)



    # 3) Verify
    print( len( adc_data_indirect ))
    print( adc_data_direct == adc_data_indirect )
    print( adc_data_direct[1::10000]   ) 
    print( adc_data_indirect[1::10000] )
    
finally: # close serial port
    ser.close()