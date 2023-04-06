# -*- coding: utf-8 -*-
"""
Created on Fri May 20 11:43:04 2022

@author: Alex
"""

import time
import timeit
import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate

import struct
import os
import os.path

from dataclasses import dataclass

""" CONSTANTS: """
# Rotation frequencies should be multiples of
# 1/(0.015s)=66.66666 Hz, so that FFT has less bleeding.

@dataclass
class RDS_Sequence_Params:
    
    f_rot_x_Hz:     float = 50200
    f_rot_y_Hz:     float = 50000
    f_offset_x_Hz:  float = 25 

    amp_rot_x:      float = 0.9
    amp_rot_y:      float = 1
    amp_offset_x:   float = 0.1
    
    phi_rot_x:      float = np.pi * 0
    phi_rot_y:      float = np.pi * 0.5
    phi_offset_x:   float = np.pi * 0
    
    calib_pulse_pos:   int = 0
    calib_pulse_width: int = 1

    dac_samples_per_sec: int =  250e3
    adc_samples_per_sec: int = 2000e3
    
    n_samples_ramp_up:      int = 3750
    n_samples_main:         int = 3750
    n_samples_ramp_down:    int = 375
    '''END class RDS_Sequence_Params '''

F_ROT_X = 50200 # Hz
F_ROT_Y = 50000 # Hz
F_OFFSET =  200 # Hz
TIME_PER_SAMPLE = 0.0000005 # s 
""" end CONSTANTS """

def generate_wavelets( par = RDS_Sequence_Params() ):
    
    AMP_MAX = 255
    
    pts_total = (    par. n_samples_ramp_up
                   + par. n_samples_main
                   + par. n_samples_ramp_down  
                   )
    
    t_start = 0
    t = np.arange(   t_start,
                     pts_total
                   ) / par. dac_samples_per_sec
    
    def phase_at_t15ms( frequ ):
        ''' get phase offset at t=15 ms
            data sampling starts at t=15 ms
        '''
        pts_to_15ms = par.n_samples_ramp_up
        t_to_15ms   = pts_to_15ms / par.dac_samples_per_sec
        phi_at_15ms = 2 * np.pi * frequ * t_to_15ms 
        
        return phi_at_15ms
    
    def sine( amp, frequ, phi, t ):
        ''' Generate sine wave '''
        y_sine = (  amp
                  * AMP_MAX /2
                  * np.sin( 2*np.pi * frequ * t + phi )
                  )

        return y_sine

    def sequence_envelope():
        ''' make sequence ramp up/down before and after main '''
        pts_up      = par.n_samples_ramp_up
        pts_main    = par.n_samples_main
        pts_down    = par.n_samples_ramp_down
        
        envelope = np.append(
                    np.append( 
                        np.arange( pts_up ) / pts_up,
                        np.ones(   pts_main )
                        ),
                      np.arange( pts_down, 0, -1) / pts_down
                      )
        return envelope

    phi_offset_x_t15ms = phase_at_t15ms( par.f_offset_x_Hz )
    Ax_offset = (   sequence_envelope()
                  * sine(
                          par. amp_offset_x,
                          par. f_offset_x_Hz,
                          par. phi_offset_x - phi_offset_x_t15ms,
                          t
                          )
                  )# Ax_offset
        
    phi_x_t15ms = phase_at_t15ms( par.f_rot_x_Hz )
    Ax_rot = (   sequence_envelope()
               * sine( 
                        par. amp_rot_x,
                        par. f_rot_x_Hz,
                        par. phi_rot_x - phi_x_t15ms,
                        t
                        )
               )# Ax_rot

    phi_y_t15ms = phase_at_t15ms( par.f_rot_y_Hz )
    Ay_rot = (   sequence_envelope()
               * sine( 
                        par. amp_rot_y,
                        par. f_rot_y_Hz,
                        par. phi_rot_y - phi_y_t15ms,
                        t
                        )
               )# Ay_rot
    
    
    calib_pulse_start = int(   par. n_samples_ramp_up
                             + par. calib_pulse_pos
                             )   
    calib_pulse_end   = calib_pulse_start + par.calib_pulse_width
    
    A_calib = AMP_MAX/2 * np.ones( pts_total )
    A_calib[ calib_pulse_start : calib_pulse_end ] = AMP_MAX
    
    A_ch4_ = np.uint8( AMP_MAX/2 * np.ones(  pts_total )) # unused

    Ax = Ax_rot + Ax_offset + AMP_MAX/2
    Ay = Ay_rot             + AMP_MAX/2
    
    assert( max(Ax) <= 255 and min(Ax) >= 0 )
    assert( max(Ay) <= 255 and min(Ay) >= 0 )   
    assert( max(A_calib) <= 255 and min(A_calib) >= 0 )   
    assert( max(A_ch4_)  <= 255 and min(A_ch4_) >= 0 )   
    
    A_CH1 = np.uint8( Ax )
    A_CH2 = np.uint8( Ay )        
    A_CH3 = np.uint8( A_calib )    
    A_CH4 = np.uint8( A_ch4_ )
         
    waves_0_to_3 = np.append( A_CH1, 
                    np.append( A_CH2,
                     np.append( A_CH3, A_CH4 )))
   
    num_of_channels = 4
    waves_0_to_3 = waves_0_to_3.reshape( num_of_channels,
                                         pts_total
                                         )
    
    return pts_total, waves_0_to_3
    

def read_PSOC_data( path_, start_index, Mittelungen):
    """ PSOC-Daten aus txt einlesen: """
    title = path_   # Titel für Diagramme
    data = np.zeros(30000)
    for i in (np.arange(Mittelungen)+start_index):
        path = path_ + str(i) + ".txt"
        data = data + 1 / Mittelungen * np.loadtxt(path)
    title = title + str(Mittelungen) + "Mittelungen"
    return data, title


def generate_sequence( amp1_comp, f1_comp, phi1_comp, amp_var):
    """ definitions """
    CH1 = 0                     
    CH2 = 1
    CH3 = 2
    CH4 = 3
    
    """ main settings """
    #  channel settings
    num_channels = 4  # number of channels
    
    max_value = 255     
    
    dac_sampling_rate = 250e3
    frequency_scale   = 1 / dac_sampling_rate
    """ END - main settings """
    
    
    """ frequency settings """
    f_rotx   = F_ROT_X    # rotation frequency x-direction
    f_roty   = F_ROT_Y    # resonante Abstimmung bei 44500 entspricht 
    f_offset = F_OFFSET   # offset field frequency
    f_off    = frequency_scale*f_offset    # calculated offset frequency for psoc

    r_off_rotx = 0.03   # ratio of rotation amplitude_x to offset amplitude = amp_off = 0.1 * amp_rotx
    amp_rotx = 1/(2*(1+r_off_rotx)) * (max_value-1)
    amp_off = r_off_rotx/(2*(1+r_off_rotx)) * (max_value-1)
    print("amp_off:", amp_off)
    #amp_off = 0
    

    """ generate sequence """
    f = frequency_scale*np.asarray([ f_rotx, f_roty, f1_comp, f_rotx])      # frequency in Hz
    #f_mod = frequency_scale*np.asarray([0.0,0,0,0])                      # modulated frequency in Hz
    phi = np.asarray([0,0,phi1_comp,0])                                  # phase in degree # Ch2 phi = 90° für Linearfeld in Offsetfeld-Maximum
    #phi_mod = np.asarray([90,90,90,90])                                  # modulated phase in degree
    amp_start = np.asarray([amp_var * amp_rotx, amp_var * 0.49 * max_value, amp1_comp * max_value, 0.49 * max_value])    # amplitude at the beginning of the main sequence 
    #amp_end = np.asarray([amp_rotx, 0.49 * max_value, amp1_comp* max_value, 0.49 * max_value])      # amplitude at the end of the main sequence
    off = np.asarray([0.5 * max_value, 0.5 * max_value, 0.5 * max_value, 0.5 * max_value])      # offset to place signal in the middle of dac range

    "Ramp-Up"
    periods_ramp_up = 700     # number of Periods for ramp_up
    nsamples_ramp_up = int(periods_ramp_up/f[0])  # number of samples for ramp_up
    print("samples_ramp_up: ", nsamples_ramp_up)
    
    "Sequence"
    periods_sequence = 850    # Number of periods for sequence 
    nsamples_sequence = int(periods_sequence/f[0])                     # required sequence samples

    "Ramp-Down"
    periods_ramp_down = 20
    nsamples_ramp_down = int(periods_ramp_down/f[0])

    # NSAMPLES_MAX = 11120
    NSAMPLES_MAX = 11120
    nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down
    print("nsamples: ", nsamples_total)
    if nsamples_total > NSAMPLES_MAX:
        print("nsamples_total > NSAMPLES_MAX")

    values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8)          # 2D array storing the sequence


    for t in np.arange(nsamples_ramp_up):
        values[CH1][t] =  off[CH1] + 1.0 / nsamples_ramp_up * t * amp_start[CH1] * np.sin(2 * np.pi * f[CH1] * t + phi[CH1]*np.pi/180) \
            + 1.0 / nsamples_ramp_up * t * amp_off * np.cos(2 * np.pi * f_off * t)  #+ phi[CH1]*np.pi/180)
        #values[CH3][t] =  off[CH3] + 1.0 / nsamples_ramp_up * t * amp_start[CH3] * np.sin(2 * np.pi * f[CH3] * t + phi[CH3]*np.pi/180)
        values[CH3][t] = - values[CH2][t]
        values[CH4][t] =  off[CH4] + 1.0 / nsamples_ramp_up * t * amp_start[CH4] * np.sin(2 * np.pi * f[CH4] * t + phi[CH4]*np.pi/180)
        values[CH2][t] =  off[CH2] + 1.0 / nsamples_ramp_up * t * amp_start[CH2] * np.sin(2 * np.pi * f[CH2] * t + phi[CH2]*np.pi/180)

    for t in (np.arange(nsamples_sequence)+nsamples_ramp_up):
        values[CH1][t] =  off[0] + amp_start[0] * np.sin(2 * np.pi * f[0] * t + phi[0]*np.pi/180) \
            + amp_off * np.cos(2 * np.pi * f_off * t)
        values[CH2][t] =  off[1] + amp_start[1] * np.sin(2 * np.pi * f[1] * t + phi[1]*np.pi/180)
        #values[CH3][t] =  off[CH3] + amp_start[CH3] * np.sin(2 * np.pi * f[CH3] * t + phi[CH3]*np.pi/180)
        values[CH3][t] = - values[CH2][t]
        values[CH4][t] =  off[CH4] + amp_start[CH4] * np.sin(2 * np.pi * f[CH4] * t + phi[CH4]*np.pi/180)
    
    for t in (np.arange(nsamples_ramp_down)+nsamples_ramp_up+nsamples_sequence):
        values[CH1][t] =  off[CH1] + amp_start[CH1] * np.sin(2 * np.pi * f[CH1] * t + phi[CH1]*np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up)) \
            + amp_off * np.cos(2 * np.pi * f_off * t) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))
        values[CH2][t] =  off[CH2] + amp_start[CH2] * np.sin(2 * np.pi * f[CH2] * t + phi[CH2]*np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))
        #values[CH3][t] =  off[CH3] + amp_start[CH3] * np.sin(2 * np.pi * f[CH3] * t + phi[CH3]*np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))
        values[CH3][t] = - values[CH2][t]
        values[CH4][t] =  off[CH4] + amp_start[CH4] * np.sin(2 * np.pi * f[CH4] * t + phi[CH4]*np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))

    """ end generate sequence """
    
    return nsamples_total, values
""" end generate_sequence() """


def plot_sequence( values,
                   channels = [0,1,2,3],
                   dac_sampling_rate = 250e3
                   ):

    plt.figure(111)    
    for channel in channels:
        plt.plot( np.arange( len( values[0] ))
                  /dac_sampling_rate,
                  values[channel],
                  label="Channel "+str(channel+1))

    plt.xlabel('time [s]')
    plt.ylabel('dac value (uint8)')
    plt.legend()
    plt.show()
""" end plot sequence """    


def write_sequence( serialPort, nsamples_total, values):
    ''' settings '''
    # B) baudrate
    baudrate = 1382400
    #  serial port
    time_out = 10                
    
    # package settings
    len_header = 8
    len_data = 50
    
    software_reset = b'e'
    ''' end settings '''
    
    # opening serial connection
    try:
        # baudrate 1 as dummy variable since it will be ignored
        ser = serial.Serial( serialPort, baudrate, timeout=time_out)  
        ser.write( software_reset )
        time.sleep(0.25)
        ser = serial.Serial( serialPort, baudrate, timeout=time_out)    
    
        # calculating the number of packages
        num_packages = int (np.ceil(nsamples_total / len_data)) # number of full package
     
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
                amp_idle = 255/2
                if data.size != len_data:
                    data = np.append(   data,
                                        amp_idle
                                      * np.ones(   len_data
                                                 - data.size,
                                                 dtype=np.uint8
                                                 ))
            
                data_bytes = bytes(data)
            
            
            
                ser.write(header_bytes + data_bytes)

                #if interface == "UART":
                    #    time.sleep(0.002) # delay for avoiding bluetooth buffer overrun 
    finally:
        ser.close()
""" end write_sequence() """


def run_sequence( serialPort,
                  save, path_to_results,
                  rx_gain='1',
                  n_avg=1, wait_sec=1
                  ):
    
    """ main settings """
    # serial port
    baudrate = 1382400 # value ignored for USBFS
    time_out = 10
    
    # data files
    nameDataFiles  = path_to_results
    save_data      = save
    
    # sequence details
    bytesPerSample = 2
    timePerSample  = 0.0005 # sample time in ms
    sequDuration   = 15 # sequence duration in ms
    numOfSamples   = int(sequDuration/timePerSample)
    bufInputSize   = numOfSamples * bytesPerSample
    adcVoltPerBit    = 4.80 / 4096 # scaling factor for ADC data: PSoC-VDD/ADC-res

    # list of commands defined in WOTAN
    p_run_sequ  = b'r' # starts the sequence
    p_get_data  = b'o' # request binary ADC data of last measurement
    p_trig_dir  = b'x' # setting the trigger to output (x: trig out, y: trig in)
    p_dac_range = b'h' # setting DAC output voltage range: 'l' for 0...1V ([l]ow; 'h' for 0...4V ([h]igh)
    
    p_rx_gain   = bytes(rx_gain,'utf-8') # 1...8 -> rx gain: x1 .. x512

    """ END - main settings """

    """ WOTAN board control and data acquisition  """
    try:
        # 0) open and interact with serial port 
        ser = serial.Serial( serialPort,
                             baudrate,
                             timeout=time_out
                             )
        
        # 1) WOTAN board settings
        ser.write( p_rx_gain )
        time.sleep(0.001)
        ser.write( p_trig_dir )
        time.sleep(0.001)
        ser.write( p_dac_range )
        time.sleep(0.001)        
    
        # 2) Run measurement
        adc_data_avg = np.array([])   
        for avg_i in range( n_avg ):
        
            # trigger measurement
            ser.write( p_run_sequ )
            time.sleep(0.030)
            
            # request adc data
            ser.flushInput()
            time.sleep(0.001)
            ser.write( p_get_data )
            time.sleep(0.001)
            
            # get data as byte stream 
            adc_data_bin = ser.read(bufInputSize)
            
            # transform byte stream into int16 array
            adc_data_int16 = struct.unpack(
                '>'+'H'*int( len(adc_data_bin) / bytesPerSample ),
                adc_data_bin
                )
            
            # averaging
            if len(adc_data_avg) == 0:
                adc_data_avg = np.array( adc_data_int16 )
            else:
                adc_data_avg += np.array( adc_data_int16 )
                
            # duty cycle control when averaging    
            if n_avg > 1:
                print( f'Avg #: { avg_i }' )
                time.sleep( wait_sec )

        adc_data_avg = adc_data_avg / n_avg                           
        
    finally: # close serial port
        ser.close()


    bytes_expected  = numOfSamples * bytesPerSample
    bytes_received  = len( adc_data_bin )
    if bytes_received == bytes_expected: 
        #  data correction routines:
            # find and correct scaling difference between ADC 1 (even samples)
            # and ADC 2 (odd samples)
            # (this method fails if signal has steps or goes into saturation!)

        adc1 = adc_data_avg[0::2]
        adc2 = adc_data_avg[1::2]
    
        adc1DIVadc2 = 0;
        for sp in range(len(adc1)):
            adc1DIVadc2 += (adc1[sp]-adc2[sp])/(adc1[sp]+adc2[sp])*2/len(adc1)
    
        adc_data_corr = np.zeros(len(adc_data_int16))
        adc_data_corr[0::2] = adc1
        adc_data_corr[0::2] = adc_data_corr[0::2] *(1-adc1DIVadc2)
        adc_data_corr[1::2] = adc2
        
        dat_time = np.arange(0,sequDuration,timePerSample)
        dat_sig  = adc_data_corr * adcVoltPerBit
    
        """ Write data to disk """
        if( save_data ):
            #  save data as ascii table
            # write data in file with continuous numbering
            cnt = 0
            data_file_name = nameDataFiles + '_' + str(cnt) + '.txt'
            while os.path.isfile( data_file_name ): #prevents overriding files
                cnt += 1
                data_file_name = nameDataFiles + '_' + str(cnt) + '.txt'
            with open( data_file_name , 'w') as f:
                for dat in adc_data_corr:
                    f.write("%s\n" % int(dat))
                print( 'Data written to: ' + data_file_name +
                  '  (' + str(len(adc_data_int16)) + ' samples)')
        
        """ return data & max. amplitude: """
        return dat_time, dat_sig, max(dat_sig) - min(dat_sig)
        
    else:
        print(   'Data incomplete '
               + f'({len(bytes_received)} '
               + 'bytes received)' )
        
""" end run_sequence() """


""" function testing """
if __name__ == "__main__":
    

    n_samples, waves = generate_wavelets(
                            par = RDS_Sequence_Params(
                                    calib_pulse_pos   = 50,
                                    calib_pulse_width = 1000
                                    )
                            )

    plot_sequence(  waves,
                    channels = [0,1,2,3],
                    dac_sampling_rate = 250e3
                    )
    
   
    