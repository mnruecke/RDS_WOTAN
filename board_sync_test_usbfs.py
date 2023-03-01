# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 21:02:45 2023

@author: marti
"""

import serial
import time

serialPort1 = '\\\\.\\COM18'
serialPort2 = '\\\\.\\COM6'

baudrate = 1382400
timeout_ = 0.2
bufInputSize = 60000


adc_data_1 = []
adc_data_2 = []

if 'last_adc_data_2' not in globals():
    last_adc_data_2 = []
    
""" start measurement on PSoC and get data """
try: # open and interact with serial port 

    ser1 = serial.Serial( serialPort1, baudrate, timeout=timeout_)
    ser2 = serial.Serial( serialPort2, baudrate, timeout=timeout_)

    for i in range(1000):    
        ser1.write( b'r' )
        time.sleep(0.03)
        
        # 1) get adc data from master
        ser1.write( b'o' )
        time.sleep(0.001)
        adc_data_1 = ser1.read(bufInputSize)
    
        # 2) get adc data from slave1
        ser2.write( b'o' )
        time.sleep(0.001)
        adc_data_2 = ser2.read(bufInputSize)



        # 3) Verify
        print( i )
        print( len( adc_data_1 ))
        print( len( adc_data_2 ))
        print( adc_data_1[1::10000]   ) 
        print( adc_data_2[1::10000] )
        print( last_adc_data_2[1::10000] )#
        last_adc_data_2 = adc_data_2

    
finally: # close serial port
    ser1.close()
    ser2.close()
    
    
    