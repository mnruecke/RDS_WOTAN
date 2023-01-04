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
% control script for iteracting with the WOTAN-PSoC firmware
%
% Connect with CY8CKIT-059-kit via USB-to-UART in the WOTAN-Firmware.
% Running 'uart_control_octave.m' starts the measurement, reads the
% resulting data stream and saves data as ascii-table. 
%
% Default measurement with WOTAN: 
%   - duration: 15 ms with 2 MS/s at 12 bit resolution -> 60 KB uint16 data
%     (limited because of 64 KB SRAM on PSoC 5LP)
%   - transfer to PC takes approx. 5 sec at baudrate = 115200
%   - the USBFS-component on PSoC 5LP allows 12.5 Mbps (i.e. 100x faster)
%
% ========================================

% 0) main settings:

% 0.1) serial interface: (requires the instrument-control package)
com_port = "\\\\.\\COM21"; % windows: "\\\\.\\COM<port_num>" - linux: "/dev/ttyACM<port_num>"
baudrate = 115200; 
timeout  = 1; 
% note: script works fine under linux but the USB-to-UART on the onboard programmer
% will not be recognised without tinkering. It is recommended to use a separate
% linux compatible usb-to-uart device and directly connect it to the 
% GPIO 12.6 (Rx) and GPIO 12.7 (Tx).  

% 0.2) If data is to be saved (ascii table): choose name of data files
save_data = true; 
data_file_name = "3D_mpi_signal"; % (resulting file format: <data_file_name>_<num>.txt)

% 0.3) select channel to record
chan = '5'; % '5' for recording the signal between GPIO 0.6 and 0.7 (default)
            % '1','2','3','4' for monitoring output of DAC 1..4 (GPIO 2.0,2.3,2.5,2.7)

% 0.4) acquire serial port
pkg load instrument-control
s1 = serial( com_port, baudrate, timeout);

srl_flush(s1);
clear data;
clear dat; 

% 1) Set channel (chan='5': measuring mode, chan='1'...'4': observe DAC output 1..4)
srl_write(s1, chan);
pause(0.3);

% 2) run sequence:
srl_write(s1, 'r');
pause(0.3);
srl_flush(s1); % erase ASCII output from buffer

% 3) 'o' triggers firmware to stream ADC buffer (binary format)
srl_write(s1, 'o');
pause(0.1);

% 4) read data stream into 'data' (length can be <= 64000 uint8)
data = srl_read(s1, 64000);

% 5) free up serial port
fclose(s1)

% 6) visualise data:
% 6.1) transform byte stream back to the uint16 data vector 
full_wave_form = (256*int16(data(1:2:end)) + int16(data(2:2:end)));

% 6.2) find and correct scaling missmatch between ADC 1 and ADC 2
%      -> currently ignores offset differences between ADC 1 and ADC 2
%      -> this simple method fails for step functions and when saturation occurs
dat = double(full_wave_form);
adc1_DIV_adc2 = sum((dat(1:2:end)-dat(2:2:end))./(dat(1:2:end)+dat(2:2:end))*2/size(dat(2:2:end),2))
%adc1_DIV_adc2 = -0.0065; 
dat(1:2:end) = (1.0-adc1_DIV_adc2) * dat(1:2:end);

figure(1);
plot( dat(1:end) ,'+'); hold on;
plot( dat(1:end) ); hold off;

% 7) save data as ascii 
% counter for continuous data file name generation
if( save_data == true)
  if( exist('measurement','var') == false )
    measurement = 0; 
  elseif( length(dir([data_file_name, "*.txt"])) == 0 )
    measurement = 0;
  else
    measurement = measurement + 1;
  endif
  dat = dat';
  save( [data_file_name, '_', num2str(measurement), ".txt"], "dat", "-ascii");
endif
%reload_data_file = importdata([data_file_name, '_', num2str(measurement), ".txt"]);
