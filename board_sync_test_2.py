# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 21:02:45 2023

@author: marti
"""

import serial
import time

serialPort = '\\\\.\\COM18'
baudrate = 1382400
timeout_ = 0.2
bufInputSize = 60000


adc_data_direct = []
adc_data_indirect = []

if 'last_adc_data_indirect' not in globals():
    last_adc_data_indirect = []
    
""" start measurement on PSoC and get data """
try: # open and interact with serial port 

    ser = serial.Serial( serialPort, baudrate, timeout=timeout_)

    adc_data_full = []
    for i in range(100):
        # 1) get adc data directly
        ser.write( b'Y' + bytes([ 0, i]) )
        time.sleep(0.001)
        adc_data = ser.read(bufInputSize)
        adc_data_full += adc_data


        # 3) Verify
        print( len( adc_data_full ))
    print( adc_data_full )

    
finally: # close serial port
    ser.close()