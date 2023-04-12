# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 18:19:12 2023

@author: marti
"""

import serial
import time
import struct
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

def is_acquisition_completed( ser_obj ):
    is_acquisition_completed_command = b'i'
    response_byte_len = 1
    completed_flag = b'\x01'
    
    ser_obj.write( is_acquisition_completed_command )
    return ser_obj.read( response_byte_len ) == completed_flag
 

def get_data_package( ser_obj, package_num, bytes_per_package ):
    get_adc_data_command = b'j' + bytes([ package_num >> 8,
                                          package_num &  0xff
                                          ])
    ser_obj.write( get_adc_data_command)    
    return ser_obj.read( bytes_per_package )

def unpack_adc_byte_stream( adc_data_bytes, bytesPerSample ):

    numOfSamples   = len( adc_data_bytes ) // bytesPerSample
    
    # transform byte stream into int16 array
    adc_data_uint16 = struct.unpack(
        '>'+'h'*int( len(adc_data_bytes) / bytesPerSample ),
        adc_data_bytes
        )

    bytes_expected  = numOfSamples * bytesPerSample
    bytes_received  = len( adc_data_bytes )
    assert( bytes_received == bytes_expected )
    
    return adc_data_uint16

def get_adc_data( ser_obj ):
    
    bytes_per_package    = 60
    bytes_per_sample     = 2
    adc_sampling_time_us = 15000
    adc_samples_per_us   = 2
    
    total_num_of_bytes = (   bytes_per_sample
                           * adc_sampling_time_us
                           * adc_samples_per_us
                           )
    
    total_num_of_packages = total_num_of_bytes // bytes_per_package
    
    adc_data_bytes = []
    for pckt_i in range( total_num_of_packages ):
        data_pckt_i = get_data_package( ser_obj, pckt_i, bytes_per_package)
        if len(adc_data_bytes) == 0:
            adc_data_bytes = data_pckt_i
        else:
            adc_data_bytes = adc_data_bytes + data_pckt_i
    
    return unpack_adc_byte_stream( adc_data_bytes, bytes_per_sample )

    
def software_reset( ser_obj ):
    software_reset_command = b'd'    
    ser_obj.write( software_reset_command )
    
def wavelet_generation( f, wave_len_ ):
    
    sampling_rate = 1e6
    wave_length   = wave_len_
    
    idle_amplitude = 127 
    
    amp1 = 127.5
    off1 = 127.5
    
    f1   = f    # kHz
    phi1 = 0    # rad
    
    t_ = np.arange( wave_length )
    y1 = amp1 * np.sin( 
                          2*np.pi / sampling_rate
                        * f1 * t_
                        + phi1
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
        #header[6:8]: reserved for future use
        
        header_bytes = bytes(header)       
        
        #data packet
        data = trace [ len_packet*package : len_packet*(package+1) ]   
        data_bytes = bytes(data)   
        ser_obj.write( header_bytes + data_bytes )      

def write_basic_wavelets():
    try:
        ser = serial.Serial( serialPort, baudrate, timeout=time_out) 
       
        verify_firmware_version( ser )
        verify_chip_id( ser )
        
        for channel_, frequ in zip( [0,1,2,3], [4e4,5e4,6e4,5e4] ):          
            trace = wavelet_generation( frequ,
                                        wave_len_ = get_wave_length(ser)
                                        )           
            plot_wave( np.arange(len(trace)), trace )
            write_sequence( ser, trace, channel= channel_ )
        
    finally:   
        ser.close()

def basic_wave_test_run_only():
    try:
        ser = serial.Serial( serialPort, baudrate, timeout=time_out) 
       
        verify_firmware_version( ser )
        verify_chip_id( ser )
        
        for _ in range(1):
            run_test_wave( ser )
            
            time.sleep(50e-3)
            print( is_acquisition_completed( ser ))
            plt.plot( get_adc_data( ser ) )
            plt.show()
            
        get_run_count(  ser )
             
    finally:   
        ser.close()        


""" function testing """
if __name__ == "__main__":

    #write_basic_wavelets()
    basic_wave_test_run_only()
    
    pass


