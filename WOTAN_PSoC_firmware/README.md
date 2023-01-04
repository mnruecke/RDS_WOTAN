# WOTAN
Firmware and scripts for running a control unit of a 3D MPI scanner. It is based around the PSoC 5LP mixed-signal chip from Cypress Semiconductor. The firmware was designed using Creator 4.1 for the CY8CKIT-059-kit with the CY8C5888LTI-LP097. This project started as a conference contribution for the IWMPI 2018 Hamburg. 

![Image of 3D TWMPI control unit](https://github.com/mnruecke/WOTAN/blob/master/wotan.png)

## Basic Features
The MPI scanner control module has 4 transmit channels (4x 250 kS/s, 8 bit, up to 4 MS/s possible) and one receive channel (2 MS/s, 12 bit). Recording time: 15 ms. Data transfer over USB-to-UART with 115200 Baud. The onboard programmer allows higher transfer rates with precise clock adjustments. Using the USBFS component included on the PSoC allows up to 12.5 Mbps (micro B connector). The common HC-05 bluetooth module can also be connected to the control unit (up to 1.3 Mbps).

## Getting Started
1. For programming the module, Creator 4.1 or higher is necessary, which can be downloaded for free from Cypress Semiconductor (www.cypress.com). The pdf-file *WOTAN_schematics.pdf* shows a block file generated with this software. The Creator IDE allows hardware programming via block diagrams. The main purpose of the pdf-file is to show the pin-mapping and which external components are needed. 

2. Opening the workspace "WOTAN" contains one project with the same name. The default configuration requires an external oscillator crystal to run. The default value is set to 8 MHz and a load capacitance of about 33 pF. It is possible to change this value between the range 4 MHz ... 25 MHz. This is done by opening the tab *WOTAN.cydwr*, choose the bottom tab called *clocks*, click somewhere in the spread sheet. A pop-up window appears which contains a blue box with the header "XTAL". There you can adjust the values for a different crystal. It is possible to run the board without an external crytal. This allows running the board without any external components but is only recommendable for debugging purposes, since the internal oscillator has an accuracy of only ~0.25%, a typical crystal has an accuracy of < 0.005%. Changing to the internal oscillator is done in the same pop-up window from above. Click on the box with the title *PLL* and choose *IMO (24 MHz)* instead of *XTAL* and then rebuild and programm the board (CTRL + 5). No wave forms are defined after programming the board (and old ones are overwritten after reprogramming). Arbitrary wave forms can be generated and transfered to the PSoC via the USBFS using the *.\UI\_WOTAN\\generate\_sequency.py* Python script. 

3. For writing the firmware to the chip connect programmer to the PSoc and the PC via USB port, select *WOTAN* as active project (right mouse click) and press CTRL-F5 for compiling and programming. 

4. Open the device manager in windows in order to see as which com-port the USBUART of the onboard programmer enumerates.

5. Start *putty.exe* or any hyperterminal of your choice and connect it to this com-port number. The baudrate value can be left at e.g. 9600 since it does not affect virtual com-ports. 

6. Pressing the reset button on the programmer or pressing 'e' in the hyperterminal resets the programm and all available options are shown in the hyperterminal

7. The numbers 1..4 select the receive channel to the DAC outputs 1..4, Pressing '5' measures the signal at GPIO 0.7. Pressing 's' starts a measurement of 15 ms and shows the results as ascii table (pressing any key will interupt the output).

8. The measurement can be easily automated. Example scripts ready to run (after changing the com-port number) are included for octave, matlab and python 3 in *.\\UI\_WOTAN\\example_scripts\\*. The matlab version will run without additional packages after changing the com-port number in the script. Octave needs the signal-toolbox. Python requires the 'pyserial' package, in addition to 'numpy' and 'matplotlib' for data visualization. The later are typically included in scientific oriented python environments like anaconda or spyider. Packages can be easily added to python by using the package manager pip.  

9. The micro B connector on the board is connected to a fast USBUART which works the same way as the USBUART on the programmer, but with 12.5 Mbps.

10. For using the HC-05 bluetooth module: a) connect it as indicated in the schematic in the Creator IDE and b) go into *main.c* and comment the function *uart_interface()*  and uncomment the function *ble_interface()* instead. The HC-05 module or similar bluetooth modems enumerate as a virtual com port and it can be used the same way as the USBUART included on the programmer. 

11. Push the boundaries of MPI hardware development beyond good and evil


## Running the module via python scripts
The folder *.\\UI_WOTAN* contains two python scripts for creating and running sequences.
The Firmware for the PSoC Chip allows to transfer an arbitrary sequence via the USBFS interface (see *.\\UI\_WOTAN\\generate_sequence_usbfs.py*). 
The sequence is then stored in the Flash. On first startup after loading the firmware to PSoC it generates an default sequence.
The PSoc can be controlled using the Python script *.\\UI\_WOTAN\\run_sequence.py*. 

## Using the fast USBUART component (micro-B connector) in Windows 7, Windows 10 and Linux
In Windows 7 it might be necessary to add the driver manually. Open the *Device Manager* and find the USBUART interface in the **Other Devices** category. Open the context menu and select *Update Driver Software*. Select the *USBUART_cdc.inf* file in the root directory. It should then enumerate as a virtual com port.
In Windows 10 it is typically recognized automatically and enumerated as a virtual com port.
In Linux, the USBUART component should also be recognized automatically and appear in /dev/ e.g. as */dev/ttyACM0*, i.e. the *com_port* variable in the python scripts mentioned below needs to be set as *com_port = '/dev/ttyACM0'* in this example. Linux doesn't grand access rights per default. This can be changed e.g. with *sudo chmod 777 /dev/ttyACM0*. 

## .\\UI\_WOTAN\\generate\_sequency.py
Python script that allows to send an arbitrary sequence to the PSoc with Firmware *WOTAN* via the fast USBFS interface, so no programmer is needed to change the sequence.
The *com_port* variable must be adapted to the Port of the PSoC on the computer which can be found in Windows under *Device Manager*.
It is possible to generate a sequence for each output channel in the form  

amp * sin(2pi * f + phi) * sin(2pi * f\_mod + phi\_mod) + off

where
*amp* is the amplitude  
*f* is the main frequency of the sequence  
*phi* is the phase of the sequence  
*f_mod* is the frequency of the modulated sin function  
*phi_mod* is the phase of the modulated sin function  
*off* is the offset  

The sequence starts with a ramp up and ends with a ramp down interval

## .\\UI\_WOTAN\\run\_sequence.py
Python script that allows to start a sequence and to receive the data of the receive channel via the fast USBFS interface.
The *com_port* variable must be adapted to the Port of the PSoC on the computer which can be found in Windows under *Device Manager*. The script plots the data and saves the data as ascii table with continuous numbering in the same folder as the script.

## Running WOTAN with arbitrary software
The WOTAN firmware can be controlled via the following ascii characters that have to be send to the PSoC via USB interface

- **p** (**P**rogramm sequence) To write an arbitrary sequence with a length of 3x3750 to the PSoc the **p** character is used. 
  A sequence consist of three parts
  * A ramp up sequence (3750 samples)
  * The actual sequence (3750 samples)
  * A ramp down sequence (3750 samples)
  
  The ADC of the PSoC measures only during the actual sequence.  
  
  The sequence must be sent consecutively for each channel. Therefore the sequence for one channel must be diveded into packages  that consist of a 8 bit **header** and 32 bit of **data**. 
  The **header** must have the following form 
  * ascii character **'p'**=112
  * **1-4** for the channel 
  * Two bytes for the package number starting with the high byte
  * Two bytes for the total number of packages per channel (number of samples per channel/32) starting with the high byte
  * not used (e.g. 0)
  * not used (e.g. 0)
  
  So the total package looks for example like this
  ('p', 2, 0x01, 0xFF, 0x02, 0x00, '0', '0',   1, 2, 4, ...... , 4, 2, 1)  
  This example shows the package with package number 0x01FF (=511) of total 0x0200 (=512) packages with the data 1, 2, 4, ..... , 4, 2, 1 for channel 2.


- **r** (**R**un sequence) The PSoC starts the sequence on the four DACs. The sequence consists of three parts. In the fist part the signal is supposed to ramp up. The second part is the acutal sequence. In the fist part the signal is supposed to ramp down. The ADC measures only in the actual sequence (second part)
- **o** (**O**rder data) The PSoC sends the data from the last measurement as a byte stream starting with the first value. Two bytes form an 16bit number where the high byte is sent first. 
The time between the **r** and the **o** command must be at least *30ms*


- **x** Sets the trigger channel as an output (default)
- **y** Sets the trigger channel as an input (not advisable since there is at least *10ns* trigger jitter)

- **l** (**l**ow) sets the DAC output range of all four channels to 0...1 V (default)
- **h** (**h**igh) sets the DAC output range of all four channels to 0...4 V

- **V** gives out the Version number of the firmware (ascii format)
- **S** gives out a unique chip identification number (7 numbers ranging from 0..255 and in ascii format, each separated by a space)

- **1**-**4** Routes the output of channel 1-4 directly to the ADC internally, so the device can be tested with the PSoC only without exteral hardware.

- **5** ADC is not connected internally so an external source can be used (default mode, signal is measured between the two GPIO pins P0.6 and P0.7)

- **l** (**L**ow) sets the range of the DACs to 0-1V
- **h** (**H**high) sets the range of the DACs to 0-4V

- **e** (R**e**set) Software reset

- **s** (Run and **S**how) Does the measurement and sends the measurement result via the UART interface
- **a** (Run and Next) Does the measurement and routes the ADC to the next DAC Output (see **1**-**5**). No output.
- **d** (Ascii **D**ata) Sends the measurement result as Ascii via the UART interface



