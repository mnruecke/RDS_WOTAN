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
serialPort = '\\\\.\\COM13' 
""" ----------------------------- """

from rds_essentials import ( generate_sequence,
                             write_sequence,
                             plot_sequence
                             )
                            
nsamples_total, values = generate_sequence( 0, 0, 0, 1 ) 

write_sequence( serialPort,
                nsamples_total,
                values
                )

plot_sequence( values,
               channels = [0,1],
               dac_sampling_rate = 250e3
               )


