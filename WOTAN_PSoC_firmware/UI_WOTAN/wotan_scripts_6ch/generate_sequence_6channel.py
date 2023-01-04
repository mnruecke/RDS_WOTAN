# -*- coding: utf-8 -*-
"""
%  ========================================
 % 
 % This code is supplementary material for the IWMPI 2018, Hamburg, Germany 
 %
 % Martin.Rueckert@physik.uni-wuerzburg.de
 %
 % Copyright (C) 2017 University of Wuerzburg, Experimental Physics 5, Biophysics
 % https://www.physik.uni-wuerzburg.de/ep5/magnetic-particle-imaging/
 %
 % WOTAN is free software: you can redistribute it and/or modify
 % it under the terms of the GNU General Public License version 3 as
 % published by the Free Software Foundation.
 %
 % WOTAN is distributed in the hope that it will be useful,
 % but WITHOUT ANY WARRANTY; without even the implied warranty of
 % MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 % GNU General Public License for more details.
 %
 % You should have received a copy of the GNU General Public License
 % along with WOTAN.  If not, see <http://www.gnu.org/licenses/>.
 % ========================================
 
% Description: 
% Script for uploading a sequence to the WOTAN board via the fast USBFS port.
% The COM number of the USBFS port must be changed under com_port
%
%
% ========================================
"""

""" --- Required parameters ---- """ 
# A) check device manager to see at which port number the board enumerates
serialPort = '\\\\.\\COM7' 

# B) baudrate
baudrate = 1382400
# C) uncomment line with the channel that is to be observed:
channel = b'7'  # b'7': "Sig_in", b'1'...b'6': auxilliary receiver channels

# D) uncomment the used interface
#interface = "UART"
#interface = "USBFS"
""" ----------------------------- """

import serial
import numpy as np
import matplotlib.pyplot as plt
import timeit
import time
import sys

""" 0) main settings """
#  serial port
time_out = 10                # [s]; this script should retrieve the 60 kB data in << 1s

#  channel settings
num_of_channels = 4         # number of regular channels (number of DACs)
num_of_virtual_channels = 4 # total number of channels
nsamples_ramp_up = 3750     # number of steps for the ramp up sequence
nsamples_sequence = 3750    # number of steps for the actual sequence
nsamples_ramp_down = 3750   # number of steps for the ramp up sequence
nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps

max_value = 255     
values = np.zeros((num_of_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence

dac_sampling_rate = 250e3
frequency_scale = 1/dac_sampling_rate

# package settings
len_header = 8
len_data = 50
""" END - main settings """



""" 1) generate sequence """

""" Parameters for each channel  

    format (channel ordering):
    <param_list> = [<CH1a>, <CH1b>, <CH2a>, <CH2b>, <CH3>, <CH4>]
    
    (DAC 1,2,3,4 -> CH 0,1,2,3)
    
"""
# Main frequencies (Hz)
f = frequency_scale*np.asarray([100,200,100,100,100,100])
# Modulation frequencies (Hz)                    
f_mod = frequency_scale*np.asarray([0,0,0,0,0,0])                      
# Start phase for main frequencies (degree)
phi = np.asarray([0, 10, 20, 30, 40, 50]) 
# Start phase for modulation frequencies (degree)
phi_mod = np.asarray([90,90,90,90,90,90])   
# Amplitudes at t=15 ms (start ramp goes from t=0...15 ms:
amp_start = max_value * np.asarray([0.47, 0.47, 0.47, 0.47, 0.47, 0.47])   
# Amplitudes at t=30 ms 
amp_end = max_value * np.asarray([0.47, 0.47, 0.47, 0.47, 0.47, 0.47]) 
# Offset voltage for each channel (necessary for avoiding clipping)     
off = max_value * np.asarray([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])



""" 1A) Generate sequence for split channels CH1, CH2
    odd  samples: CH1a, CH2a
    even samples: CH1b, CH2b
    """
for channel in [0,1]:
    for split_channel in [0,1]:
        
        virtual_channel = 2 * channel + split_channel        
        
        # Generate sampling masks for interleaved signal generation
        interleaved_ramp_up   = np.arange( split_channel, nsamples_ramp_up,2)    
        interleaved_main_part = np.arange( split_channel +nsamples_ramp_up, nsamples_ramp_up+nsamples_sequence,2)    
        interleaved_ramp_down = np.arange( split_channel +nsamples_ramp_up+nsamples_sequence, nsamples_ramp_up+nsamples_sequence+nsamples_ramp_down,2)    
        
        # Sequence part1: ramp up
        for t in interleaved_ramp_up:
            
            values[channel][t] = 1.0 / nsamples_ramp_up * t \
                * amp_start[channel] * np.sin(2 * np.pi * f[virtual_channel] * t + phi[virtual_channel]*np.pi/180) \
                * np.sin(2 * np.pi * f_mod[virtual_channel] * t + phi_mod[virtual_channel]*np.pi/180) + off[virtual_channel]
            
        # Sequence part2: main sequence
        for t in interleaved_main_part:
            
            values[channel][t] = (amp_start[virtual_channel] + (amp_end[virtual_channel] - amp_start[virtual_channel])\
                / nsamples_sequence * (t-nsamples_ramp_up)) \
                * np.sin(2 * np.pi * f[virtual_channel] * t + phi[virtual_channel]*np.pi/180) \
                * np.sin(2 * np.pi * f_mod[virtual_channel] * t + phi_mod[virtual_channel]*np.pi/180) + off[virtual_channel]
            
        # Sequence part 3: ramp down
        for t in interleaved_ramp_down:
            
            values[channel][t] = (1.0 - (t-nsamples_ramp_up-nsamples_sequence) / nsamples_ramp_down) \
                * amp_end[channel] * np.sin(2 * np.pi * f[virtual_channel] * t + phi[virtual_channel]*np.pi/180) \
                * np.sin(2 * np.pi * f_mod[virtual_channel] * t + phi_mod[virtual_channel]*np.pi/180) + off[virtual_channel]    
    


""" 1B) Generate sequence for the regular channels CH3, CH4 """
num_of_split_channels = 2 # = additional index shift
for channel in [2,3]:
    
    virtual_channel = channel + num_of_split_channels
    
    # Sequence part1: ramp up
    for t in np.arange(nsamples_ramp_up):
        
        values[channel][t] = 1.0 / nsamples_ramp_up * t \
            * amp_start[channel] * np.sin(2 * np.pi * f[virtual_channel] * t + phi[virtual_channel]*np.pi/180) \
            * np.sin(2 * np.pi * f_mod[virtual_channel] \
                       * t + phi_mod[virtual_channel]*np.pi/180) + off[virtual_channel]
            
    # Sequence part2: main sequence
    for t in ( np.arange(nsamples_sequence) + nsamples_ramp_up ):
        
        values[channel][t] = (amp_start[virtual_channel] + (amp_end[virtual_channel] - amp_start[virtual_channel])\
            / nsamples_sequence * (t-nsamples_ramp_up)) \
            * np.sin(2 * np.pi * f[virtual_channel] * t + phi[virtual_channel]*np.pi/180) \
            * np.sin(2 * np.pi * f_mod[virtual_channel] \
                       * t + phi_mod[virtual_channel]*np.pi/180) + off[virtual_channel]
            
    # Sequence part 3: ramp down
    for t in ( np.arange(nsamples_ramp_down) + nsamples_ramp_up + nsamples_sequence ):
        
        values[channel][t] = (1.0 - (t-nsamples_ramp_up-nsamples_sequence) / nsamples_ramp_down) \
            * amp_end[channel+1] * np.sin(2 * np.pi * f[virtual_channel] * t + phi[virtual_channel]*np.pi/180) \
            * np.sin(2 * np.pi * f_mod[virtual_channel] \
                       * t + phi_mod[virtual_channel]*np.pi/180) + off[virtual_channel]


""" end generate sequence """


  
""" 2) plot sequence """
# Split channels CH1a, CH1b, CH2a, CH2b
for channel in [0,1]:

    for split_channel in [0,1]:
        
        plt.plot(np.arange(0,nsamples_total,2)/dac_sampling_rate, values[ channel ][ split_channel :: 2 ],
                 label="CH" + str( channel+1 ) + chr( ord('a') + split_channel ) )
        plt.xlabel('time [s]')
        plt.ylabel('dac value (uint8)')



# Regular channels CH3, CH4    
for channel in [2,3]:
    
    plt.plot(np.arange(nsamples_total)/dac_sampling_rate, values[channel], label="CH"+str(channel+1))
    plt.xlabel('time [s]')
    plt.ylabel('dac value (uint8)')
    
plt.legend()
plt.show()
""" end plot sequence """




""" 3) write sequence """
# opening serial connection
try:
    # baudrate 1 as dummy variable since it will be ignored
    ser = serial.Serial( serialPort, baudrate, timeout=time_out)
    start = timeit.default_timer()
    
    
    # calculating the number of packages
    num_packages = int (np.ceil(nsamples_total / len_data)) # number of full packages
    print("num_packages",num_packages)  #Debug Alex
     
    Ticiti = timeit.default_timer()
    for channel in [0,1,2,3]:
        
        time.sleep(0.05) # delay for avoiding bluetooth buffer overrun

        for package in range(num_packages):
            
            #header
            header = np.zeros(len_header,  dtype=np.uint8)
            header[0] = ord('p')                    # 'p' for programming mode
            header[1] = channel                     # channel number
            header[2] = package >> 8                # package number MSB
            header[3] = package & 0xFF              # package number LSB
            header[4] = num_packages >> 8           # total number of packages MSB
            header[5] = num_packages & 0xFF         # total number of packages LSB
            
            header_bytes = bytes(header)
               
            
            #data
            data = values[channel][len_data*package:len_data*(package+1)]
            
            
            #last package
            if data.size != len_data:
                data = np.append(data, np.zeros( len_data - data.size, dtype=np.uint8))
                
            
            
            data_bytes = bytes(data)
            
            
            
            ser.write(header_bytes + data_bytes)
            tic = timeit.default_timer()
            #if interface == "USBFS":
            #    time.sleep(0.0001)
            
            
            #if interface == "UART":
            #    time.sleep(0.002) # delay for avoiding bluetooth buffer overrun
            toc = timeit.default_timer()
            print(toc-tic) 
    Tociti = timeit.default_timer()
    print("Komplette Schleife:",Tociti-Ticiti) 
finally:
    ser.close()
    
""" end write seequence """

