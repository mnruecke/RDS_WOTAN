# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 18:19:12 2023

@author: marti
"""

import serial
import time
import struct
import os
import numpy as np
import matplotlib.pyplot as plt


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
    
    return np.array( unpack_adc_byte_stream( adc_data_bytes, bytes_per_sample))
    
def adjust_adc1_vs_adc2( adc_data ):
    # correct gain difference between adc 1 and adc 2 
    # (interleaved sampling pattern)
    idx_offset_ADC_1 = 0
    idx_offset_ADC_2 = 1
    
    sum_adc1   = np.sum( adc_data[idx_offset_ADC_1::2] )
    sum_adc2   = np.sum( adc_data[idx_offset_ADC_2::2] )
    gain_ratio = sum_adc1 / sum_adc2
    
    adc_data[idx_offset_ADC_2::2] = gain_ratio * adc_data[idx_offset_ADC_2::2]
            
    return adc_data, gain_ratio
 
def save_adc_data( adc_data, data_path='\\.', file_prefix='data'):
    #  save data as ascii table
    # write data in file with continuous numbering
    file_count = 0
    data_file_name = file_prefix + '_' + str(file_count) + '.txt'
    while os.path.isfile( data_file_name ): #prevents overriding files
        file_count += 1
        data_file_name = file_prefix + '_' + str(file_count) + '.txt'
    with open( data_file_name , 'w') as f:
        for dat in adc_data:
            f.write("%s\n" % int(dat))
        print( 'Data written to: ' + data_file_name +
          '  (' + str(len(adc_data)) + ' samples)')
        
def read_adc_data( data_path='\\.', file_prefix='data' ):
    
    file_count = 1
    data_file_name = file_prefix + '_' + str(file_count) + '.txt'

    lines = []    
    with open( data_file_name , 'r' ) as f:
        lines = np.array([int(line.strip()) for line in f])
        
    print(lines)
    plt.plot(lines[-100:])
   
def software_reset( ser_obj ):
    software_reset_command = b'd'    
    ser_obj.write( software_reset_command )
    
def wavelet_generation( f_, phi_, amp_, wave_len_ ):
    
    # a) fixed sampling pattern settings
    pts_per_td       = 24000/16
    n_tds_ramp       = 5
    sample_slippage  = -4
    adc_window_shift = 160/2
    adc_window_start = int(   pts_per_td * n_tds_ramp
                            + adc_window_shift
                            + sample_slippage
                            )
    
    adc_window_length = 15000 # samples
    
    sampling_rate = 1e6
    wave_length   = wave_len_
    
    idle_amplitude      = 127 
    base_line_amplitude = 127.5
    
    phi_adc_window_start = 2 * np.pi * f_ * adc_window_start / sampling_rate   
    
    
    # b) wave generation
    amp  = amp_   # uint8
    f    = f_     # kHz
    phi  = phi_   # rad
    
    
    t_ = np.arange( wave_length )
    
    y = amp * np.sin( 
                          2*np.pi / sampling_rate
                        * f * t_
                        + phi - phi_adc_window_start
                        )
    # c) add up- and down- ramp before and after the adc sampling window
    ramp_up_start = 0
    ramp_up_end   = int( 3/4 * adc_window_start )
    ramp_up       = np.arange( ramp_up_start,
                               ramp_up_end
                               ) * 1/(ramp_up_end-1)
    y[ ramp_up_start : ramp_up_end ] = ramp_up * y[   ramp_up_start
                                                    : ramp_up_end
                                                    ]
  
    ramp_down_start  = adc_window_start + int( adc_window_length * 1.02 )
    ramp_down_length = wave_length - ramp_down_start 
    ramp_down        = ( 1 - np.arange( 0, ramp_down_length
                                       ) * 1/(ramp_down_length-1))
    y[ ramp_down_start : ] = ramp_down * y[ ramp_down_start : ]
    
    y = y + base_line_amplitude
    y[-1] = idle_amplitude
    return np.uint8( y )
  
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
        
        wavelets = [ [ 5e4, -2*np.pi*0, 127],
                     [ 5e4, -2*np.pi*0.1, 127],
                     [ 5e4, -2*np.pi*0.2, 127],
                     [ 5e4, -2*np.pi*0.3, 127],
                     ]
        
        for channel_ in [0,1,2,3]:          
            frequ = wavelets[ channel_ ][0]
            phi   = wavelets[ channel_ ][1]
            amp   = wavelets[ channel_ ][2]
            trace = wavelet_generation( frequ,
                                        phi,
                                        amp,
                                        wave_len_ = get_wave_length(ser)
                                        )          
            
            plt.figure(1)
            trace_part = trace[:100]
            plot_wave( np.arange(len(trace_part)), trace_part )
            write_sequence( ser, trace, channel= channel_ )
        
    finally:   
        ser.close()

def basic_wave_test_run_only( data_path='\\.' ):
    try:
        ser = serial.Serial( serialPort, baudrate, timeout=time_out) 
       
        verify_firmware_version( ser )
        verify_chip_id( ser )
        
        n_rep = 1
        for _ in range( n_rep ):
            
            run_test_wave( ser )          
            time.sleep(50e-3)
            print( is_acquisition_completed(ser))           
            adc_data, adc1_div_adc2 = adjust_adc1_vs_adc2(get_adc_data(ser))    
            
            plt.figure(2)
            plt.plot( adc_data[-100:] )
            plt.plot( adc_data[:100] )
            print( "ADC data pts: ", len(adc_data))
            
            #save_adc_data( adc_data, data_path )
            
        get_run_count(  ser )
             
    finally:   
        ser.close()        


""" function testing """
if __name__ == "__main__":

    serialPort = '\\\\.\\COM6' 
    baudrate   = 0 # value is ignored for usbfs interface
    time_out   = 1

    GAIN_RATIO_ADC1_ADC2 = 0.99734    
        

    write_basic_wavelets()
    basic_wave_test_run_only()
    
    pass


