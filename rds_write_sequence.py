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

# Coil system Alex
# x-coil B/I = 2
# y-coil B/I = 0.79

""" --- Required parameters ---- """ 
serialPort = '\\\\.\\COM6' 
""" ----------------------------- """

import numpy as np
from rds_essentials import ( 
                             RDS_Sequence_Params,   
                             generate_wavelets,
                             write_sequence,
                             plot_sequence
                             )
  
rds_params = RDS_Sequence_Params(
    f_rot_x_Hz            = 50200,
    f_rot_y_Hz            = 50000,
    f_offset_x_Hz         = 50, 

    amp_rot_x             = 0.9,
    amp_rot_y             = 1,
    amp_offset_x          = 0.1,
    
    phi_rot_x             = np.pi * 0,
    phi_rot_y             = np.pi * 0.5,
    phi_offset_x          = np.pi * 0,
    
    calib_pulse_pos       = 0,
    calib_pulse_width     = 1,

    dac_samples_per_sec   =  250e3,
    adc_samples_per_sec   = 2000e3,
    
    n_samples_ramp_up     = 3750,
    n_samples_main        = 3750,
    n_samples_ramp_down   = 375,
    )
                          
nsamples_total, values = generate_wavelets( par = rds_params ) 

write_sequence( serialPort,
                nsamples_total,
                values
                )

plot_sequence( values,
               channels = [0,1],
               dac_sampling_rate = 250e3
               )

runfile('C:/Users/marti/OneDrive/Desktop/github/RDS_WOTAN/rds_run_sequence.py', wdir='C:/Users/marti/OneDrive/Desktop/github/RDS_WOTAN')
