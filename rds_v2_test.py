# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 18:19:12 2023

@author: marti
"""

import serial
import time
import numpy as np
import matplotlib.pyplot as plt

serialPort = '\\\\.\\COM6' 
baudrate   = 0 # value is ignored for usbfs interface
time_out   = 1


def verify_firmware_version( ser_obj ):
    
    print_firmware_version_command  = b'a'
    firmware_version_strlen = 3
    
    ser_obj.write( print_firmware_version_command )
    psoc_response = ser_obj.read( firmware_version_strlen )
    assert( psoc_response == b'0.1' )

def verify_chip_id( ser_obj ):

    print_chip_id_command  = b'b'
    chip_id_strlen = 27
    
    ser_obj.write( print_chip_id_command )
    psoc_response = ser_obj.read( chip_id_strlen )
    #print( psoc_response )
    assert( psoc_response == b' 26  15  19 126   1   5  20' )    

def create_test_wave( ser_obj ):
    create_test_wave_command = b'e'
    ser_obj.write( create_test_wave_command )

def run_test_wave( ser_obj ):
    run_test_wave_command  = b'c'
    ser_obj.write( run_test_wave_command )
    
def get_run_count( ser_obj ):    
    get_run_count_command  = b'f'
    run_count_strlen = 6
    
    ser_obj.write( get_run_count_command )
    psoc_response = ser_obj.read( run_count_strlen )
    print( psoc_response[:-1] )

def get_wave_length( ser_obj ):    
    get_wave_length_command  = b'h'
    wave_length_strlen = 6
    
    ser_obj.write( get_wave_length_command )
    psoc_response = ser_obj.read( wave_length_strlen )
    
    return int( psoc_response[:-1] )
    
def software_reset( ser_obj ):
    software_reset_command = b'd'    
    ser_obj.write( software_reset_command )
    
def wavelet_generation( f, wave_len_ = 1600 ):
    
    sampling_rate = 1e6
    wave_length   = wave_len_
    
    idle_amplitude = 127 
    
    amp1 = 127.5
    off1 = 127.5
    
    f1   = f    # kHz
    phi1 = 0    # rad
    
    t_ = np.arange( wave_length )
    y1 = amp1 * np.sin( 
                        2*np.pi/sampling_rate * f1 * t_ + phi1
                        ) + off1
    y1[-1] = idle_amplitude
    y1 = np.uint8( y1 )
    
    return y1
  
    
def plot_wave( t_, y ):
    plt.plot( t_, y )
    plt.xlabel(r'time $[\mu s]$')
    plt.ylabel(r'amp [uint8]')
    
def write_sequence( ser_obj, trace, channel ):

    # package settings
    len_header = 8
    len_packet = 50
    
    nsamples = len(trace)
    num_packages = nsamples // len_packet
    assert( num_packages == np.ceil( nsamples / len_packet ))    
    for package in range(num_packages):

        #header
        header = np.zeros(len_header,  dtype=np.uint8)
        header[0] = ord('g')                    # 'p' for programming mode
        header[1] = channel                     # channel number
        header[2] = package >> 8                # package number MSB
        header[3] = package & 0xFF              # package number LSB
        header[4] = num_packages >> 8           # total number of packages MSB
        header[5] = num_packages & 0xFF         # total number of packages LSB
        
        header_bytes = bytes(header)       
        
        #data
        data = trace [ len_packet*package : len_packet*(package+1) ]   
        data_bytes = bytes(data)   
        ser_obj.write( header_bytes + data_bytes )      

def basic_wave_test():
    try:
        ser = serial.Serial( serialPort, baudrate, timeout=time_out) 
       
        verify_firmware_version( ser )
        verify_chip_id( ser )
        
        #create_test_wave( ser )
        trace1 = wavelet_generation( 1e3, wave_len_ = get_wave_length(ser) ) 
        plot_wave( np.arange(len(trace1)), trace1 )
        trace2 = wavelet_generation( 2e3, wave_len_ = get_wave_length(ser) ) 
        plot_wave( np.arange(len(trace2)), trace2 )
        trace3 = wavelet_generation( 4e3, wave_len_ = get_wave_length(ser) ) 
        plot_wave( np.arange(len(trace3)), trace3 )
        trace4 = wavelet_generation( 8e3, wave_len_ = get_wave_length(ser) ) 
        plot_wave( np.arange(len(trace4)), trace4 )
        write_sequence( ser, trace1, channel=0 )
        write_sequence( ser, trace2, channel=1 )
        write_sequence( ser, trace3, channel=2 )
        write_sequence( ser, trace4, channel=3 )
        
        for _ in range(1):
            run_test_wave( ser )
            time.sleep(2e-3)
            
        get_run_count(   ser )
        get_wave_length( ser )
        
    finally:   
        ser.close()

def basic_wave_test_run_only():
    try:
        ser = serial.Serial( serialPort, baudrate, timeout=time_out) 
       
        verify_firmware_version( ser )
        verify_chip_id( ser )
  
        #create_test_wave( ser )
        for _ in range(1):
            run_test_wave( ser )
            time.sleep(2e-3)
            
        get_run_count(   ser )
        print( get_wave_length( ser ) )
        
    finally:   
        ser.close()

""" function testing """
if __name__ == "__main__":

    #basic_wave_test()
    basic_wave_test_run_only()
    
    pass


