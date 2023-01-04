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
serialPort = '\\\\.\\COM5' 

# B) baudrate
baudrate = 1382400
# C) uncomment line with the channel that is to be observed:
#channel = b'1'  # show output of DAC 1
#channel = b'2'  # show output of DAC 2
#channel = b'3'  # show output of DAC 3
#channel = b'4'  # show output of DAC 4
channel = b'2'  # show signal voltage between GPIO P0.6 (-) and GPIO P0.7 (+)

# D) uncomment the used interface
#interface = "UART"
interface = "USBFS"
""" ----------------------------- """

import serial
import numpy as np
import matplotlib.pyplot as plt
import timeit
import time

""" main settings """
#  serial port
time_out = 10                # [s]; this script should retrieve the 60 kB data in << 1s

#  channel settings
num_channels = 4            # number of channels
nsamples_ramp_up = 3750     # number of steps for the ramp up sequence
nsamples_sequence = 3750    # number of steps for the actual sequence
nsamples_ramp_down = 3750   # number of steps for the ramp up sequence
nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps

max_value = 255     
values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence

dac_sampling_rate = 250e3
frequency_scale = 1/dac_sampling_rate

# package settings
len_header = 8
len_data = 32
""" END - main settings """



""" generate sequence """
f = frequency_scale*np.asarray([1000,2000,1110,2220])                    # frequency in Hz
f_mod = frequency_scale*np.asarray([0.0,0,0,0])                      # modulated frequency in Hz
phi = np.asarray([0,90,0,0])                                         # phase in degree
phi_mod = np.asarray([90,90,90,90])                                  # modulated phase in degree
amp_start = np.asarray([0.47 * max_value, 0.10 * max_value, 0.47 * max_value, 0.47 * max_value])    # amplitude at the beginning of the main sequence 
amp_end = np.asarray([0.47 * max_value, 0.47 * max_value, 0.47 * max_value, 0.47 * max_value])      # amplitude at the end of the main sequence
off = np.asarray([0.5 * max_value, 0.5 * max_value, 0.5 * max_value, 0.5 * max_value])


for channel in range(num_channels):
    # ramp up
    for t in np.arange(nsamples_ramp_up):
        values[channel][t] = 1.0 / nsamples_ramp_up * t \
        * amp_start[channel] * np.sin(2 * np.pi * f[channel] * t + phi[channel]*np.pi/180) \
        * np.sin(2 * np.pi * f_mod[channel] * t + phi_mod[channel]*np.pi/180) + off[channel]
    # actual sequence
    for t in (np.arange(nsamples_sequence)+nsamples_ramp_up):
        values[channel][t] = (amp_start[channel] + (amp_end[channel] - amp_start[channel])/ nsamples_sequence * (t-nsamples_ramp_up)) \
        * np.sin(2 * np.pi * f[channel] * t + phi[channel]*np.pi/180) \
        * np.sin(2 * np.pi * f_mod[channel] * t + phi_mod[channel]*np.pi/180) + off[channel]
    # ramp down
    for t in (np.arange(nsamples_ramp_down)+nsamples_ramp_up+nsamples_sequence):
        values[channel][t] = (1.0 - (t-nsamples_ramp_up-nsamples_sequence) / nsamples_ramp_down) \
        * amp_end[channel] * np.sin(2 * np.pi * f[channel] * t + phi[channel]*np.pi/180) \
        * np.sin(2 * np.pi * f_mod[channel] * t + phi_mod[channel]*np.pi/180) + off[channel]


""" end generate sequence """

  
""" plot sequence """
for channel in range(num_channels):
    plt.plot(np.arange(nsamples_total)/dac_sampling_rate, values[channel], label="Channel "+str(channel))
    plt.xlabel('time [s]')
    plt.ylabel('dac value (uint8)')
plt.legend()
plt.show()
""" end plot sequence """




""" write sequence """
# opening serial connection
try:
    # baudrate 1 as dummy variable since it will be ignored
    ser = serial.Serial( serialPort, baudrate, timeout=time_out)
    start = timeit.default_timer()
    
    
    # calculating the number of packages
    num_packages = int (np.ceil(nsamples_total / len_data)) # number of full packages    
        
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
            header[5] = num_packages & 0xFF         # tital number of packages LSB
            
            header_bytes = bytes(header)    
            
            #data
            data = values[channel][len_data*package:len_data*(package+1)]
            #last package
            if data.size != 32:
                data = np.append(data, np.zeros(32-data.size,dtype=np.uint8))
                
                
            data_bytes = bytes(data)
    
            ser.write(header_bytes + data_bytes)
            
            if interface == "USBFS":
                time.sleep(0.0001)

            if interface == "UART":
                time.sleep(0.002) # delay for avoiding bluetooth buffer overrun

finally:
    ser.close()
""" end write seequence """

