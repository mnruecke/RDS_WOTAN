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
% matlab control script for interacting with the WOTAN-PSoC firmware.
%
% Connect with CY8CKIT-059-kit via USB-to-UART in the WOTAN-Firmware.
% Running 'uart_control_matlab.m' starts the measurement, reads the
% resulting data stream and saves data as ascii-table. 
%
% Default measurement with WOTAN: 
%   - duration: 15 ms with 2 MS/s at 12 bit resolution -> 60 KB uint16 data
%     (limited because of 64 KB SRAM on PSoC 5LP)
%   - transfer to PC takes approx. 5 sec at baudrate = 115200
%   - the USBFS-component on PSoC 5LP allows 12.5 Mbps (i.e. 100x faster)
%
% ========================================

% main settings
com_port  = 'COM10'; % check device manager to see which com-port the programmer enumerates
baud_rate = 115200;
time_out  = 10;

adcBufByteSize = 60000; % 

adc_channel = '5'; % default: '5' (signal input between GPIO 0.6 and 0.7); '1...4': for checking output on DAC1 ... DAC4

file_name = '3D_mpi_data_'; % results are saved as ascii table 
% // main settings


% 0) Open serial port
s1 = serial( com_port,'BaudRate', baud_rate);
s1.InputBufferSize = adcBufByteSize; % length of ADC buffer (uint8)
s1.TimeOut = time_out;
fopen(s1);

% 1) Select channel
fwrite(s1, adc_channel);
pause(0.3);

% 2) Run sequence
fwrite(s1,'r');
pause(0.3);

% 2) Clear USB buffer and trigger psoc to write data into USB buffer
flushinput(s1);
fwrite(s1,'o');

% 3) Read data from USB buffer
data = fread(s1);

% 5) free up serial port
fclose(s1);

if adcBufByteSize == max(size(data)) % check if data transfer was successful
    % 6) visualise (data is 16 bit, therefore need to
    %    reshape from uint8 into uint16)
    full_wave_form = (256*int16(data(1:2:end)) + int16(data(2:2:end)));
    
    % 7) Find and correct scaling difference between ADC 1 and ADC 2
    %    (even vs odd values)
	% this method fails if signal has steps or goes into satutation
    dat = double(full_wave_form);
    adc1DIVadc2 = sum((dat(1:2:end)-dat(2:2:end))./(dat(1:2:end)+dat(2:2:end))*2/size(dat(2:2:end),1));
    dat(1:2:end) = (1-adc1DIVadc2) * dat(1:2:end);
    
    % 8) Display results
    plot( dat(1:end) ,'+'); hold on;
    plot( dat(1:end) ); hold off;
    
    % 9) Save data (ascii table)
    f_count=0;
    % continuous numbering and avoid overiding old files:
    while  exist( [file_name num2str( f_count ) '.txt'] ) == 2 
        f_count = f_count + 1; 
    end
    save( [file_name num2str( f_count ) '.txt'], 'dat', '-ascii');
else
	['Data transfer unsuccessful (PSoC needs at least 5 seconds'...
	 ' after repogramming for calculating the wave forms).']
end
    
    
