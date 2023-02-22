# -*- coding: utf-8 -*-
"""
Created on Fri May 20 11:43:04 2022

@author: Alex
"""

import time
import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate

import struct
import os
import os.path

""" CONSTANTS: """
# Rotationsfrequenzen sollten Vielfache von 1/(0.015s)=66.66666 Hz sein, damit FFT weniger bleeding hat.
#F_ROT_X = 49000 # Hz für 5% Abweichung von F_ROT_Y

#F_ROT_X = 50500 # Hz für 0,5% Abweichung von F_ROT_Y - Zielfrequenz
F_ROT_X = 50200 # eben 50200 # 1/0.015*756 # = 50400 Hz
#F_ROT_X = 50250
#F_ROT_Y = 50250 # Hz Zielfrequenz
F_ROT_Y = 50000 #1/0.015*753 # = 50200 Hz
#F_ROT_Y = 52000
F_OFFSET = 200 # Hz
TIME_PER_SAMPLE = 0.0000005 # s 
""" end CONSTANTS """



""" fft_spectrum_single_sided """
""" ************************* """
def fft_spectrum_single_sided(signal):
    N = signal.size                                  # Anzahl Datenpunkte
    fft_signal = np.fft.fft(signal)                   # FFT berechnen
    #shiftfft_sig = np.fft.fftshift(fft_sig)
    magfft_signal = np.abs(fft_signal) * 2 / N            # 2/N damit Scheitefaktor der Schwingung als Amplitudenhöhe angezeigt wird
    magfft_signal_single = magfft_signal[0:int(N/2+1)]    # Nur halbes Spektrum betrachten
    magfft_signal_single[0] = magfft_signal_single[0]/2   # DC Komponente nicht mal 2 nehmen..
    return magfft_signal_single
""" end fft_spectrum_single_sided """



""" frequency_axis_single_sided """
""" ************************* """
def frequency_axis_single_sided(time):
    N = time.size
    dt = time[1] - time[0]
    # freq = np.fft.fftfreq(N, d=dt) # Frequencies associated with each samples
    #freq_axis = np.linspace(0, 1 / dt, N)
    freq_axis = np.fft.fftfreq(N, dt)
    freq_axis = freq_axis[ 0 : int(N/2+1) ]     # single sided freq_axis
    return freq_axis
""" end frequency_axis_single_sided """


""" fft_phase_single_sided """
""" ************************* """
def fft_phase_single_sided(signal):
    N = signal.size                                  # Anzahl Datenpunkte
    fft_signal = np.fft.fft(signal)                   # FFT berechnen
    phase_fft_signal = np.angle(fft_signal)            # 2/N damit Scheitefaktor der Schwingung als Amplitudenhöhe angezeigt wird
    phase_fft_signal_single = phase_fft_signal[0:int(N/2+1)]    # Nur halbes Spektrum betrachten
    #magfft_signal_single[0] = magfft_signal_single[0]/2   # DC Komponente nicht mal 2 nehmen..
    
    return phase_fft_signal_single
""" end fft_phase_single_sided """


""" index_max """
""" ********* """
def index_max(data):
    data_ = data.copy()     # ignore DC-Offset data[0]
    data_[0] = 0
    max_val = max(data_)
    max_idx = np.where(data_ == max_val)
    return max_idx, max_val
""" end index_max """


""" phase_autocorrel_rad """
def phase_autocorrel_rad(A,B):
    """ Phase zwischen Input und Output CH3 bestimmen """
    nsamples = A.size


    #Offset abziehen:
    A -= A.mean()
    
    B -= B.mean()
    


    """ calc auto-correlation """
    xcorr = correlate(A, B)

    # delta time array to match xcorr
    dt = np.arange(1-nsamples, nsamples)

    recovered_time_shift = dt[xcorr.argmax()]
    time_shift_secs =  recovered_time_shift * TIME_PER_SAMPLE
    f0 = F_ROT_Y
    dphase = f0 * time_shift_secs * 2 * np.pi # rad
    dphase_deg = f0 * time_shift_secs * 360 # °
    print("time_shift as index: ", recovered_time_shift, " time_shift in [s]: ", time_shift_secs , " entspricht Phasenverschiebung von: [°] ", dphase_deg )
    return dphase
""" end phase autocorrel_rad """


""" read_PSOC_data() """

def read_PSOC_data(path_, start_index, Mittelungen):
    """ PSOC-Daten aus txt einlesen: """
    title = path_   # Titel für Diagramme
    data = np.zeros(30000)
    for i in (np.arange(Mittelungen)+start_index):
        path = path_ + str(i) + ".txt"
        data = data + 1 / Mittelungen * np.loadtxt(path)
    title = title + str(Mittelungen) + "Mittelungen"
    return data, title

""" evaluate_data() """
""" *************** """
def evaluate_data(path_,start_index,Mittelungen):
    """ Settings: """
    # Technical data from PSOC and sequence:
    adcVoltPerBit    = 4.80 / 4096 # scaling factor for ADC data: PSoC-VDD/ADC-res
    sequDuration   = 0.015 # sequence duration in s
    timePerSample  = 0.0000005 # sample time in ms -> 2MS/s
    #print("Frequenzauflösung = ", 2e6/len(sig_out))
    
    
    """ PSOC-Daten aus txt einlesen: """
    data,title = read_PSOC_data(path_,start_index,Mittelungen)

    """ Zeitsignal erstellen """
    # Zeitachse erstellen:
    t = np.arange(0,sequDuration,timePerSample)
    # ADC-Signale in V umrechnen:
    signal = data * adcVoltPerBit
    
    
    
    U_offset = np.sin(2*np.pi*200*t+0.015) + 2.5
    
    """ Zeitsignale anzeigen """
    von = 0
    bis = len(signal)-1
    #von = 0
    #bis = 135
    plt.figure()
    plt.plot(t[von:bis], signal[von:bis], color = 'b')  # Signal2 in rot
    plt.plot(t[von:bis], U_offset[von:bis], label='U_offset')
    plt.xlabel('time/[ms]')
    plt.ylabel('Voltage/[V]')
    plt.title(title, fontsize = 20)
    plt.grid()
    #plt.legend()
    #plt.savefig('Ocean15ul_Fluidmag200nm40ul120mgGlycerin.png' , dpi = 600 , transparent = True)
    plt.show()
    
    
    """ FFT berechnen """
    # Amplitude:
    magfft_signal_single = fft_spectrum_single_sided(signal)
    # Phase:
    phase = fft_phase_single_sided(signal)
    #Frequenzachse:
    f = frequency_axis_single_sided(t)
    
    """ Amplitudenplot """
    plt.figure()
    plt.title(title + 'Amplitudenplot')  
    von = 0
    #bis = 500
    bis = len(magfft_signal_single)-1
    #plt.plot(f[von:bis],magfft_sig_single[von:bis],'b')     # Spektrum von Index von ... bis anzeigen.
    plt.semilogy(f[von:bis],(magfft_signal_single[von:bis]),'b')
    plt.xlabel('frequency/[Hz]')
    plt.ylabel('Amplitude[V]')
    plt.show()
    
    
    
""" end evaluate_data() """

""" generate_sequence() """
""" ******************* """

def generate_sequence(amp1_comp, f1_comp, phi1_comp,amp_var):
    """ definitions """
    CH1 = 0                     
    CH2 = 1
    CH3 = 2
    CH4 = 3
    
    """ main settings """
    #  channel settings
    num_channels = 4            # number of channels
    #nsamples_ramp_up = 1200     # number of steps for the ramp up sequence
    #nsamples_sequence = 1200    # number of steps for the actual sequence
    #nsamples_ramp_down = 1200   # number of steps for the ramp up sequence
    #nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps
    
    max_value = 255     
    #values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence
    
    dac_sampling_rate = 250e3
    frequency_scale = 1/dac_sampling_rate
    """ END - main settings """
    
    
    """ frequency settings """
    f_corr = 1          # for strange PSOC Frequency adjustment: f_corr = 1 or 4
    f_rotx = F_ROT_X    # rotation frequency x-direction
    f_roty = F_ROT_Y      # resonante Abstimmung bei 44500 entspricht 
    #f_rotx/1.05      # rotation frequency y-direction (1,005 = Ratio between fx and fy as supposed in Martin's Diss Kap.3.13 Abb.3-14)
    f_offset = F_OFFSET       # offset field frequency
    f_off = frequency_scale*f_offset / f_corr    # calculated offset frequency for psoc

    r_off_rotx = 0.03   # ratio of rotation amplitude_x to offset amplitude = amp_off = 0.1 * amp_rotx
    #r_off_rotx = 0.99
    amp_rotx = 1/(2*(1+r_off_rotx)) * (max_value-1)
    amp_off = r_off_rotx/(2*(1+r_off_rotx)) * (max_value-1)
    print("amp_off:", amp_off)
    #amp_off = 0
    

    """ generate sequence """
    f = frequency_scale*np.asarray([f_rotx/f_corr,f_roty/f_corr, f1_comp/f_corr, f_rotx/f_corr])      # frequency in Hz
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
    periods_sequence = 850                      # Number of periods for sequence 
    #t_sequence = periods_sequence / f[0]
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

    """ plot sequence """
    plt.figure()
    plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[0], label="Channel "+str(0+1))
    plt.show()
    
    for channel in range(2): #range(num_channels):
        plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[channel], label="Channel "+str(channel+1))
    plt.figure(1)
    plt.xlabel('time [s]')
    plt.ylabel('dac value (uint8)')
    plt.legend()
    plt.show()
    """ end plot sequence """
    
    return nsamples_total, values
""" end generate_sequence() """


""" generate_sequence_offset() """
""" ************************** """

def generate_sequence_offset(amp_var, offset_status):
    """ definitions """
    CH1 = 0                     
    CH2 = 1
    CH3 = 2
    CH4 = 3
    
    """ main settings """
    #  channel settings
    num_channels = 4            # number of channels
    #nsamples_ramp_up = 1200     # number of steps for the ramp up sequence
    #nsamples_sequence = 1200    # number of steps for the actual sequence
    #nsamples_ramp_down = 1200   # number of steps for the ramp up sequence
    #nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps
    
    max_value = 255     
    #values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence
    
    dac_sampling_rate = 250e3
    frequency_scale = 1/dac_sampling_rate
    """ END - main settings """
    
    
    """ frequency settings """
    f_corr = 1          # for strange PSOC Frequency adjustment: f_corr = 1 or 4
    f_rotx = F_ROT_X    # rotation frequency x-direction
    f_roty = F_ROT_Y      # resonante Abstimmung bei 44500 entspricht 
    #f_rotx/1.05      # rotation frequency y-direction (1,005 = Ratio between fx and fy as supposed in Martin's Diss Kap.3.13 Abb.3-14)
    f_offset = F_OFFSET       # offset field frequency
    f_off = frequency_scale*f_offset / f_corr    # calculated offset frequency for psoc

    r_off_rotx = 0.05   # ratio of rotation amplitude_x to offset amplitude = amp_off = 0.1 * amp_rotx
    amp_rotx = 1/(2*(1+r_off_rotx)) * (max_value-1)
    
    if offset_status == 1:
        amp_off = r_off_rotx/(2*(1+r_off_rotx)) * (max_value-1)
        print("Offset:", amp_off)
    else:
        amp_off = 0
    

    """ generate sequence """
    f = frequency_scale*np.asarray([f_rotx/f_corr,f_roty/f_corr, 50000/f_corr, f_rotx/f_corr])      # frequency in Hz
    #f_mod = frequency_scale*np.asarray([0.0,0,0,0])                      # modulated frequency in Hz
    phi = np.asarray([0,0,0,0])                                  # phase in degree # Ch2 phi = 90° für Linearfeld in Offsetfeld-Maximum
    #phi_mod = np.asarray([90,90,90,90])                                  # modulated phase in degree
    amp_start = np.asarray([amp_var * amp_rotx, amp_var * 0.49 * max_value, 0.49 * max_value, 0.49 * max_value])    # amplitude at the beginning of the main sequence 
    #amp_end = np.asarray([amp_rotx, 0.49 * max_value, amp1_comp* max_value, 0.49 * max_value])      # amplitude at the end of the main sequence
    off = np.asarray([0.5 * max_value, 0.5 * max_value, 0.5 * max_value, 0.5 * max_value])      # offset to place signal in the middle of dac range

    "Ramp-Up"
    periods_ramp_up = 20     # number of Periods for ramp_up
    nsamples_ramp_up = int(periods_ramp_up/f[0])  # number of samples for ramp_up

    "Sequence"
    periods_sequence = 1870                      # Number of periods for sequence 
    #t_sequence = periods_sequence / f[0]
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

    """ plot sequence """
    # plt.figure()
    # plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[0], label="Channel "+str(0+1))
    # plt.show()
    
    # for channel in range(4): #range(num_channels):
    #     plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[channel], label="Channel "+str(channel+1))
    # plt.figure(1)
    # plt.xlabel('time [s]')
    # plt.ylabel('dac value (uint8)')
    # plt.legend()
    # plt.show()
    """ end plot sequence """
    
    return nsamples_total, values
""" end generate_sequence_offset() """





""" generate_phase_sweep_sequence() """
""" ******************* """
""" generate sequence needs to be called before calling generate_amp_sweep_sequence """
def generate_phase_sweep_sequence(values, ch, freq, amp, phase_von, phase_bis):   # ch = 3,4
    # 8 adc samples per dac sample
    
    """ main settings """
    #  channel settings
    nsamples_ramp_up = 3.750     # number of steps for the ramp up sequence
    nsamples_sequence = 3.750   # number of steps for the actual sequence
    nsamples_ramp_down = 3.750   # number of steps for the ramp up sequence
    nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps
    # NSAMPLES_MAX = 11120
    NSAMPLES_MAX = 11120
    print("nsamples: ", nsamples_total)
    if nsamples_total > NSAMPLES_MAX:
        print("nsamples_total > NSAMPLES_MAX")
    
    max_value = 255     
    #values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence
    
    dac_sampling_rate = 250e3
    frequency_scale = 1/dac_sampling_rate
    """ END - main settings """
    
    
    """ frequency settings """
    f_corr = 1          # for strange PSOC Frequency adjustment: f_corr = 1 or 4    

    """ generate sequence """
    f = frequency_scale*freq
    #f_mod = frequency_scale*np.asarray([0.0,0,0,0])                      # modulated frequency in Hz
    phi = phase                                                           # phase in degree
    #phi_mod = np.asarray([90,90,90,90])                                  # modulated phase in degree
    d_phase_min = freq * frequency_scale * 360  # Minimaler Phasenschritt in [°]
    periods = (phase_bis-phase_von) / d_phase_min
    
    off = 0.5 * max_value        # offset to place signal in the middle of dac range

    for t in np.arange(nsamples_ramp_up):
        values[ch][t] =  off + 1.0 / nsamples_ramp_up * t * amp_start * np.sin(2 * np.pi * f * t + phi*np.pi/180)

    for t in (np.arange(nsamples_sequence)+nsamples_ramp_up):
        values[ch][t] =  off + (amp_start-amp_end) (1/nsamples_sequence * t) * np.sin(2 * np.pi * f * t + phi * np.pi/180)

    
    for t in (np.arange(nsamples_ramp_down)+nsamples_ramp_up+nsamples_sequence):
        values[ch][t] =  off + amp_start * np.sin(2 * np.pi * f * t + phi * np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up)) 
    """ end generate sequence """

    """ plot sequence """
    plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[ch], label="Channel "+str(ch+1))
    plt.figure(1)
    plt.xlabel('time [s]')
    plt.ylabel('dac value (uint8)')
    plt.legend()
    plt.show()
    """ end plot sequence """
    
    return nsamples_total, values
""" end generate_phase_sweep_sequence() """




""" generate_amp_sweep_sequence() """
""" ******************* """
""" generate sequence needs to be called before calling generate_amp_sweep_sequence """
def generate_amp_sweep_sequence(values, ch, freq, phase, amp_von, amp_bis):   # ch = 3,4
    # 8 adc samples per dac sample
    
    """ main settings """
    #  channel settings
    nsamples_ramp_up = 3.750     # number of steps for the ramp up sequence
    nsamples_sequence = 3.750   # number of steps for the actual sequence
    nsamples_ramp_down = 3.750   # number of steps for the ramp up sequence
    nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps
    # NSAMPLES_MAX = 11120
    NSAMPLES_MAX = 11120
    print("nsamples: ", nsamples_total)
    if nsamples_total > NSAMPLES_MAX:
        print("nsamples_total > NSAMPLES_MAX")
    
    max_value = 255     
    #values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence
    
    dac_sampling_rate = 250e3
    frequency_scale = 1/dac_sampling_rate
    """ END - main settings """
    
    
    """ frequency settings """
    f_corr = 1          # for strange PSOC Frequency adjustment: f_corr = 1 or 4    

    """ generate sequence """
    f = frequency_scale*freq
    #f_mod = frequency_scale*np.asarray([0.0,0,0,0])                      # modulated frequency in Hz
    phi = phase                                         # phase in degree
    #phi_mod = np.asarray([90,90,90,90])                                  # modulated phase in degree
    amp_start = amp_von *0.49    # amplitude at the beginning of the main sequence 
    amp_end = amp_bis * 0.49     # amplitude at the end of the main sequence
    off = 0.5 * max_value        # offset to place signal in the middle of dac range

    for t in np.arange(nsamples_ramp_up):
        values[ch][t] =  off + 1.0 / nsamples_ramp_up * t * amp_start * np.sin(2 * np.pi * f * t + phi*np.pi/180)

    for t in (np.arange(nsamples_sequence)+nsamples_ramp_up):
        values[ch][t] =  off + (amp_start-amp_end) (1/nsamples_sequence * t) * np.sin(2 * np.pi * f * t + phi * np.pi/180)

    
    for t in (np.arange(nsamples_ramp_down)+nsamples_ramp_up+nsamples_sequence):
        values[ch][t] =  off + amp_start * np.sin(2 * np.pi * f * t + phi * np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up)) 
    """ end generate sequence """

    """ plot sequence """
    plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[ch], label="Channel "+str(ch+1))
    plt.figure(1)
    plt.xlabel('time [s]')
    plt.ylabel('dac value (uint8)')
    plt.legend()
    plt.show()
    """ end plot sequence """
    
    return nsamples_total, values
""" end generate_amp_sweep_sequence() """





""" generate_sequence2f() """
""" ******************* """

def generate_sequence2f(amp1_comp, f1_comp, phi1_comp, amp2_comp, f2_comp, phi2_comp):
    
    """ definitions """
    CH1 = 0                     
    CH2 = 1
    CH3 = 2
    CH4 = 3
    
    """ main settings """
    #  channel settings
    num_channels = 4            # number of channels
    #nsamples_ramp_up = 1200     # number of steps for the ramp up sequence
    #nsamples_sequence = 1200    # number of steps for the actual sequence
    #nsamples_ramp_down = 1200   # number of steps for the ramp up sequence
    #nsamples_total = nsamples_ramp_up + nsamples_sequence + nsamples_ramp_down  # total number of steps
    
    max_value = 255     
    #values = np.zeros((num_channels, nsamples_total),  dtype=np.uint8) # 2D array storing the sequence
    
    dac_sampling_rate = 250e3
    frequency_scale = 1/dac_sampling_rate
    """ END - main settings """
    
    
    """ frequency settings """
    f2_comp *= frequency_scale
    
    f_corr = 1          # for strange PSOC Frequency adjustment: f_corr = 1 or 4
    f_rotx = F_ROT_X      # rotation frequency x-direction
    f_roty = F_ROT_Y      # resonante Abstimmung bei 44500 entspricht 
    #f_rotx/1.05      # rotation frequency y-direction (1,005 = Ratio between fx and fy as supposed in Martin's Diss Kap.3.13 Abb.3-14)
    f_offset = F_OFFSET       # offset field frequency
    f_off = frequency_scale*f_offset / f_corr    # calculated offset frequency for psoc

    r_off_rotx = 0.1     # ratio of rotation amplitude_x to offset amplitude = amp_off = 0.1 * amp_rotx
    amp_rotx = 1/(2*(1+r_off_rotx)) * (max_value-1)
    amp_off = r_off_rotx/(2*(1+r_off_rotx)) * (max_value-1)    

    """ generate sequence """
    f = frequency_scale*np.asarray([f_rotx/f_corr,f_roty/f_corr, f1_comp/f_corr, f_rotx/f_corr])      # frequency in Hz
    #f_mod = frequency_scale*np.asarray([0.0,0,0,0])                      # modulated frequency in Hz
    phi = np.asarray([0,90,phi1_comp,0])                                         # phase in degree
    #phi_mod = np.asarray([90,90,90,90])                                  # modulated phase in degree
    amp_start = np.asarray([amp_rotx, 0.49 * max_value, amp1_comp * max_value, 0.49 * max_value])    # amplitude at the beginning of the main sequence 
    #amp_end = np.asarray([amp_rotx, 0.49 * max_value, amp1_comp* max_value, 0.49 * max_value])      # amplitude at the end of the main sequence
    off = np.asarray([0.5 * max_value, 0.5 * max_value, 0.5 * max_value, 0.5 * max_value])      # offset to place signal in the middle of dac range

    "Ramp-Up"
    periods_ramp_up = 20     # number of Periods for ramp_up
    nsamples_ramp_up = int(periods_ramp_up/f[0])  # number of samples for ramp_up

    "Sequence"
    periods_sequence = 1870                      # Number of periods for sequence 
    #t_sequence = periods_sequence / f[0]
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
        values[CH1][t] =  off[CH1] + 1.0 / nsamples_ramp_up * t * amp_start[CH1] * np.sin(2 * np.pi * f[CH1] * t + phi[CH1] * np.pi/180) \
            + 1.0 / nsamples_ramp_up * t * amp_off * np.sin(2 * np.pi * f_off * t)  #+ phi[CH1]*np.pi/180)
        values[CH2][t] =  off[CH2] + 1.0 / nsamples_ramp_up * t * amp_start[CH2] * np.sin(2 * np.pi * f[CH2] * t + phi[CH2] * np.pi/180)
        values[CH3][t] =  off[CH3] + 1.0 / nsamples_ramp_up * t * (amp_start[CH3] * np.sin(2 * np.pi * f[CH3] * t + phi[CH3] * np.pi/180) \
            + (amp2_comp * max_value) * np.sin(2 * np.pi * f2_comp * t + phi2_comp * np.pi/180) )
        values[CH4][t] =  off[CH4] + 1.0 / nsamples_ramp_up * t * amp_start[CH4] * np.sin(2 * np.pi * f[CH4] * t + phi[CH4] * np.pi/180)

    for t in (np.arange(nsamples_sequence)+nsamples_ramp_up):
        values[CH1][t] =  off[0] + amp_start[0] * np.sin(2 * np.pi * f[0] * t + phi[0] * np.pi/180) \
            + amp_off * np.sin(2 * np.pi * f_off * t + phi[0] * np.pi/180)
        values[CH2][t] =  off[1] + amp_start[1] * np.sin(2 * np.pi * f[1] * t + phi[1] * np.pi/180)
        values[CH3][t] =  off[CH3] + amp_start[CH3] * np.sin(2 * np.pi * f[CH3] * t + phi[CH3] * np.pi/180) + (amp2_comp * max_value) * np.sin(2 * np.pi * f2_comp * t + phi2_comp * np.pi/180)
        values[CH4][t] =  off[CH4] + amp_start[CH4] * np.sin(2 * np.pi * f[CH4] * t + phi[CH4] * np.pi/180)
    
    for t in (np.arange(nsamples_ramp_down)+nsamples_ramp_up+nsamples_sequence):
        values[CH1][t] =  off[CH1] + amp_start[CH1] * np.sin(2 * np.pi * f[CH1] * t + phi[CH1] * np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up)) \
            + amp_off * np.sin(2 * np.pi * f_off * t + 0 * np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))
        values[CH2][t] =  off[CH2] + amp_start[CH2] * np.sin(2 * np.pi * f[CH2] * t + phi[CH2] * np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))
        values[CH3][t] =  off[CH3] + (amp_start[CH3] * np.sin(2 * np.pi * f[CH3] * t + phi[CH3] * np.pi/180) \
                                      + (amp2_comp * max_value) * np.sin(2 * np.pi * f2_comp * t + phi2_comp * np.pi/180)) \
            * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))
        values[CH4][t] =  off[CH4] + amp_start[CH4] * np.sin(2 * np.pi * f[CH4] * t + phi[CH4] * np.pi/180) * (1.0 - 1.0 / nsamples_ramp_down * (t-nsamples_sequence-nsamples_ramp_up))

    """ end generate sequence """

    """ plot sequence """
    # for channel in range(4): #range(num_channels):
    #     plt.plot(np.arange(nsamples_total)/dac_sampling_rate/f_corr, values[channel], label="Channel "+str(channel))
    # plt.figure(1)
    # plt.xlabel('time [s]')
    # plt.ylabel('dac value (uint8)')
    # plt.legend()
    # plt.show()
    """ end plot sequence """
    
    return nsamples_total, values
""" end generate_sequence2f() """



""" write sequence() """
""" **************** """

def write_sequence(serialPort,nsamples_total,values):
    ''' settings '''
    # B) baudrate
    baudrate = 1382400
    #  serial port
    time_out = 10                # [s]; this script should retrieve the 60 kB data in << 1s
    
    # package settings
    len_header = 8
    len_data = 50
    ''' end settings '''
    
    # opening serial connection
    try:
        # baudrate 1 as dummy variable since it will be ignored
        ser = serial.Serial( serialPort, baudrate, timeout=time_out)    
    
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
                header[5] = num_packages & 0xFF         # total number of packages LSB
                
                header_bytes = bytes(header)
                
                
                #data
                data = values[channel][len_data*package:len_data*(package+1)]
                
                
                #last package
                if data.size != len_data:
                    data = np.append(data, np.zeros( len_data - data.size, dtype=np.uint8))
                    
            
            
                data_bytes = bytes(data)
            
            
            
                ser.write(header_bytes + data_bytes)
                #if interface == "USBFS":
                    #    time.sleep(0.0001)
            
            
                #if interface == "UART":
                    #    time.sleep(0.002) # delay for avoiding bluetooth buffer overrun 
    finally:
        ser.close()
""" end write_sequence() """


""" run_sequence() """
""" ************** """

def run_sequence( serialPort, save, pfad, rx_gain='1'):
    """ --- Required parameters ---- """ 
    baudrate = 1382400    #Baudrate  #921600
                                                                                 
    """ ----------------------------- """
    
    """ main settings """
    # serial port
    time_out       = 10
    nameDataFiles  = pfad 
    save_data      = save
    # sequence details
    bytesPerSample = 2
    timePerSample  = 0.0005 # sample time in ms
    #sequDuration   = 15 # sequence duration in ms
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

    """ start measurement on PSoC and get data """
    try: # open and interact with serial port 
        ser = serial.Serial( serialPort, baudrate, timeout=time_out)
        # run MPI sequence on psoc
    
        ser.write( p_rx_gain )
        time.sleep(0.001)
        ser.write( p_trig_dir )
        time.sleep(0.001)
        ser.write( p_dac_range )
        time.sleep(0.001)
    
        ser.write( p_run_sequ )
        time.sleep(0.030)
        ser.flushInput()
        time.sleep(0.001)
        ser.write( p_get_data )
        time.sleep(0.001)
    
        # get data as byte stream 
        adc_data_bin = ser.read(bufInputSize)
        # transform byte stream into int16 array
        adc_data_int16 = struct.unpack('>'+'H'*int(len(adc_data_bin)/bytesPerSample),adc_data_bin)
    
    finally: # close serial port
        ser.close()
    
        #print(len(adc_data_int16))


    if len(adc_data_bin) == numOfSamples*bytesPerSample: # check if run was successful
        #  data correction routines:
            # find and correct scaling difference between ADC 1 (even samples)
            # and ADC 2 (odd samples)
            # (this method fails if signal has steps or goes into saturation!)

        adc1 = adc_data_int16[0::2]
        adc2 = adc_data_int16[1::2]
  
    #    adc=[];
    #    for i in adc_data_int16:
        #        adc.append(adc_data_int16[i]+1)
        #    adc1 = adc[0::2]
        #    adc2 = adc[1::2]
    
        adc1DIVadc2 = 0;
        for sp in range(len(adc1)):
            adc1DIVadc2 += (adc1[sp]-adc2[sp])/(adc1[sp]+adc2[sp])*2/len(adc1)
    
        adc_data_corr = np.zeros(len(adc_data_int16))
        adc_data_corr[0::2] = adc1
        adc_data_corr[0::2] = adc_data_corr[0::2] *(1-adc1DIVadc2)
        adc_data_corr[1::2] = adc2
        
        # visualize data
        
        dat_time = np.arange(0,sequDuration,timePerSample)
        dat_sig  = adc_data_corr * adcVoltPerBit
        
        #plt.figure(2)
        #plt.plot( dat_time, dat_sig, dat_time, dat_sig,'+')
        #plt.xlabel('time [ms]')
        #plt.ylabel('signal [V]')
        #plt.show()
    
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
        print("\n\n\nPSoC doesn't seem ready. Please try again. " +\
          "(WOTAN firmware requires approx. 5 sec. after " +\
          "programming for sequence calculation.)\n\n\n")
        
""" end run_sequence() """