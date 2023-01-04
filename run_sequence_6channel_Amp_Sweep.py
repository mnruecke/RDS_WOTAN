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
%
% control script for interacting with the WOTAN-PSoC firmware.
%
% Connect with CY8CKIT-059-kit via USB-to-UART in the WOTAN-Firmware.
% Running 'uart_control_python.py' starts the measurement, reads the
% resulting data stream and saves data as ascii-table. 
%
% Default measurement with WOTAN: 
%   - duration: 15 ms with 2 MS/s at 12 bit resolution -> 60 KB uint16 data
%     (limited because of 64 KB SRAM on PSoC 5LP)
%   - transfer to PC takes approx. 5 sec at baudrate = 115200
%   - the USBFS-component on PSoC 5LP allows 12.5 Mbps (i.e. 100x faster)
%
%
%
%  This script needs the 'pyserial' package:
%    https://pythonhosted.org/pyserial/index.html
%    ( download zip-file and install e.g. with "pip install pyserial")  
%
%   in addition, numpy and  matplotlib are required for visualization
%   (often included in scientific python environments like 'anaconda',
%   'spyder' etc.
%
% ========================================
"""
""" --- Required parameters ---- """ 
# A) check device manager to see at which port number the board enumerates
serialPort = '\\\\.\\COM3' 


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
#import serial
#import time
#import struct
#import os
#import os.path

import matplotlib.pyplot as plt
import time
from rds_functions_6channel_beta import run_sequence, generate_sequence, write_sequence


path = './Messung221025_Ocean_ohne_Offset/'
save = 0   # 1 = Sequenz speichern
sleep_time = 3
amp_var  = 1


# 20% Amp
nsamples_total, values = generate_sequence( 0, 0, 0, 0.2 ) # generate_sequence(amp1=0 ... 0.49, f1, phi1)
write_sequence(serialPort,nsamples_total,values)

t, sig, amp = run_sequence(serialPort,save,path)


# 40% Amp
nsamples_total, values = generate_sequence( 0, 0, 0, 0.4 ) # generate_sequence(amp1=0 ... 0.49, f1, phi1)
write_sequence(serialPort,nsamples_total,values)

t, sig, amp = run_sequence(serialPort,save,path)


# 60% Amp
nsamples_total, values = generate_sequence( 0, 0, 0, 0.6 ) # generate_sequence(amp1=0 ... 0.49, f1, phi1)
write_sequence(serialPort,nsamples_total,values)

t, sig, amp = run_sequence(serialPort,save,path)


# 80% Amp
nsamples_total, values = generate_sequence( 0, 0, 0, 0.8 ) # generate_sequence(amp1=0 ... 0.49, f1, phi1)
write_sequence(serialPort,nsamples_total,values)

t, sig, amp = run_sequence(serialPort,save,path)


# 100% Amp
nsamples_total, values = generate_sequence( 0, 0, 0, 1 ) # generate_sequence(amp1=0 ... 0.49, f1, phi1)
write_sequence(serialPort,nsamples_total,values)

t, sig, amp = run_sequence(serialPort,save,path)


# time.sleep(sleep_time)

    


# visualize data
plt.close('all')
plt.figure(12)
plt.plot( t, sig)
plt.xlabel('time [ms]')
plt.ylabel('signal [V]')
plt.show()  
    
#with open( "zwischenspeicher.txt" , 'w') as f:
#    for dat in sig:
#        f.write("%s\n" % float(dat))
    

        
            