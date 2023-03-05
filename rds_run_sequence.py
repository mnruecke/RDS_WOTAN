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
serialPort = '\\\\.\\COM13' 

save_data   = 0 # 1 = save data
data_path   = (   'C:\\Users\\marti\\OneDrive\\Dokumente\\'
                + 'MEGA\\RDI_share\\RDS_2023\\
                + 'rds2_20230302_FFb\\'
                )

rx_gain         = '0' # '0'...'9' => Gain: x1 ... x512 // '6'=x64
n_avg           = 1
wait_sec_avg    = 1 # time in s between measurements when avg > 1

import os
if save_data and not os.path.exists( data_path ):    
    os.mkdir( data_path )
    
""" ----------------------------- """      


import time   
from rds_essentials import run_sequence

t, sig, amp = run_sequence( serialPort,
                            save_data, data_path,
                            rx_gain,
                            n_avg, wait_sec_avg
                            )


# visualize data
import matplotlib.pyplot as plt
#plt.close('all')
plt.figure(12)
#plt.plot( t[:100], sig[:100])
plt.plot( t, sig)
plt.xlabel('time [ms]')
plt.ylabel('signal [V]')
plt.show()  
        
                