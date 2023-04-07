# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 18:19:12 2023

@author: marti
"""

import serial

serialPort = '\\\\.\\COM6' 
baudrate   = 0 # value is ignored for usbfs interface
time_out   = 1


def verify_firmware_version( ser_obj ):
    
    print_firmware_version_command  = b'a'
    firmware_version_strlen = 3
    
    ser_obj.write( print_firmware_version_command )
    psoc_response = ser.read( firmware_version_strlen )
    assert( psoc_response == b'0.1' )


def verify_chip_id( ser_obj ):

    print_chip_id_command  = b'b'
    chip_id_strlen = 27
    
    ser.write( print_chip_id_command )
    psoc_response = ser.read( chip_id_strlen )
    #print( psoc_response )
    assert( psoc_response == b' 26  15  19 126   1   5  20' )
    

def run_test_wave( ser_obj ):
    run_test_wave_command  = b'c'
    ser.write( run_test_wave_command )


try:
    ser = serial.Serial( serialPort, baudrate, timeout=time_out) 
   
    verify_firmware_version( ser )
    verify_chip_id( ser )
    
    run_test_wave( ser )
    
finally:
    ser.close()
