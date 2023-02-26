/* ========================================
 * 
 * This code is supplementary material for the IWMPI 2018, Hamburg, Germany 
 *
 * Martin.Rueckert@physik.uni-wuerzburg.de
 *
 * Copyright (C) 2017-2021 University of Wuerzburg, Experimental Physics 5, Biophysics
 * https://www.physik.uni-wuerzburg.de/ep5/magnetic-particle-imaging/
 *
 * WOTAN is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * WOTAN is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with WOTAN.  If not, see <http://www.gnu.org/licenses/>.
 * ========================================
 */


// Using the internal oscillator "IMO":
//
// to run without external crystal: go to  "Design Wide Resources(WOTAN.cydwr)" in Workspace Explorer (left)
//              goto the tab "WOTAN.cydwr" -> go to "clocks" (tabs on the bottom) -> click anywhere inside 
//              the yellow spread sheet -> change the roll-down menue in "PLL" (box in the middle)
//              to "IMO(24 MHz)" -> recompile and program (CTRL + F5)

#include "project.h"// automatically generated header file
#include <stdio.h>
#include <string.h>
#include <math.h>// => requires 'm' in: Project|Build Settings... -> ARM GCC ... -> Linker -> General -> Additional Libraries -> m

char  version[3] = "1.8";  // WOTAN for RDS Spectrometer
// Version 1.7: allowing to split CH1 and CH2 into CH1a/CH1b and CH2a/CH2b
// by halfing the sampling rate and using interleaved sampling patterns

#define  TRUE               1
#define  FALSE              0

#define START_CLOCK         0
#define STOP_CLOCK          1


#define  UART_BUF_IN         100
#define  UART_BUF_OUT        80

/* command set */
// 1) select rx gain
#define  KEY_AMP_0              '0'// 1x1   x1
#define  KEY_AMP_1              '1'// 2x1   x2
#define  KEY_AMP_2              '2'// 2x2   x4
#define  KEY_AMP_3              '3'// 4x2   x8
#define  KEY_AMP_4              '4'// 4x4   x16
#define  KEY_AMP_5              '5'// 8x4   x32
#define  KEY_AMP_6              '6'// 8x8   x64
#define  KEY_AMP_7              '7'// 16x8  x128
#define  KEY_AMP_8              '8'// 16x16 x256
#define  KEY_AMP_9              '9'// 4x4x2 x32
// 2) run sequence
#define  KEY_RUN             'r'
// 3) reset firmware
#define  KEY_RESET           'e'
// 4) set VDAC output range to 1V (default, voltage DACs only, comment code out when using current DACs)
#define  KEY_VDAC_1V         'l'
// 5) set VDAC output range to 4V (voltage DACs only, comment code out when using current DACs)
#define  KEY_VDAC_4V         'h'
// 6) writes new sequence
#define  KEY_WRITE_SEQUENCE  'p'
// 7) Use gpio P3[0] as trigger output
#define  KEY_TRIGGER_OUT     'x'
// 8) Use gpio P3[0] as trigger input
#define  KEY_TRIGGER_IN      'y'
// 9) firmware infomation
#define  KEY_VERSION         'V'
// 10) chip information
#define  KEY_SERIAL_NUMBER   'S'
// 11) Get the binary data from the two uint16 ADC buffers
#define  KEY_SEND_BYTE_DAT   'o'
// 15) new: Shift waveforms in multiples of sampling time (usage: 'O<channel-pair><16bit-offset>')
#define KEY_SHIFT_WAVEFORMS  'O'

//Alex Testing Commands:
// 16) separates ChargerOut- and GND via setting PWR_EN to 0
#define KEY_POWER_OFF        'f'
// 17) Turns Off the DCDC_Converter
#define KEY_DCDC_OFF         'D'
//18) Turns LED on/off
#define KEY_LED              'L'


// 19) Test board synchronisation
#define KEY_BOARD_SYNC        'A'


/* end command set */

#define  TRIGGER_OUT_TRUE    1
#define  TRIGGER_OUT_FALSE   0

#define  NSAMPLES_ADC       15000               // 1 MS/s, max value: 15000
#define  NSAMPLES_DAC       NSAMPLES_ADC/4      // 250 kS/s (make sample duration for Transmit and Receive the same)
#define  SEQU_DURATION_US   NSAMPLES_ADC*3      // duration includes start- and end ramp

#define  IGNORE_FIRST_PART  TRUE               // if FALSE: shows start ramp of sequence (default: TRUE)

#define  N_TDS_ADC          20
#define  N_TDS_DAC          3               // TD1: on ramp, TD2: sequence (each with length NSAMPLES_DAC)


#define  FLASH_CH1          (const uint8 *)     0x0A000  // Flash addresses for storing the DAC wave forms
#define  FLASH_CH2          (const uint8 *)     0x10000
#define  FLASH_CH3          (const uint8 *)     0x20000
#define  FLASH_CH4          (const uint8 *)     0x30000 
const uint8 * FLASH_STORAGE[4] = {FLASH_CH1, FLASH_CH2, FLASH_CH3, FLASH_CH4};
uint32 flash_offset_ch1 = 0; //Shifts wave form of CHX n sampling steps
uint32 flash_offset_ch2 = 0; 
uint32 flash_offset_ch3 = 0; 
uint32 flash_offset_ch4 = 0; 


#define  CLOCK_SHIFT_CH1     0b1100   
#define  CLOCK_SHIFT_CH2     0b0011
#define  CLOCK_SHIFT_CH3     0b0110   
#define  CLOCK_SHIFT_CH4     0b1001   


// Set all MPI waveform parameters
#define MAX_VALUE       254 
#define IDLE_VALUE_CH1  127
#define IDLE_VALUE_CH2  127
#define IDLE_VALUE_CH3  127
#define IDLE_VALUE_CH4  127


/* Defines for DMA_DAC_1 */
#define DMA_DAC_1_BYTES_PER_BURST 1
#define DMA_DAC_1_REQUEST_PER_BURST 1   
#define DMA_DAC_1_SRC_BASE (FLASH_CH1)
#define DMA_DAC_1_DST_BASE (CYDEV_PERIPH_BASE)

/* Variable declarations for DMA_DAC */
/* Move these variable declarations to the top of the function */
uint8 DMA_DAC_1_Chan;
uint8 DMA_DAC_1_TD[N_TDS_DAC];
uint8 start_td_index = 0;

/* Defines for DMA_DAC_2 */
#define DMA_DAC_2_BYTES_PER_BURST 1
#define DMA_DAC_2_REQUEST_PER_BURST 1
#define DMA_DAC_2_SRC_BASE (FLASH_CH2)
#define DMA_DAC_2_DST_BASE (CYDEV_PERIPH_BASE)

/* Variable declarations for DMA_DAC_2 */
/* Move these variable declarations to the top of the function */
uint8 DMA_DAC_2_Chan;
uint8 DMA_DAC_2_TD[N_TDS_DAC];

/* Defines for DMA_DAC_3 */
#define DMA_DAC_3_BYTES_PER_BURST 1
#define DMA_DAC_3_REQUEST_PER_BURST 1
#define DMA_DAC_3_SRC_BASE (FLASH_CH3)
#define DMA_DAC_3_DST_BASE (CYDEV_PERIPH_BASE)

/* Variable declarations for DMA_DAC_3 */
/* Move these variable declarations to the top of the function */
uint8 DMA_DAC_3_Chan;
uint8 DMA_DAC_3_TD[N_TDS_DAC];

/* Defines for DMA_DAC_4 */
#define DMA_DAC_4_BYTES_PER_BURST 1
#define DMA_DAC_4_REQUEST_PER_BURST 1
#define DMA_DAC_4_SRC_BASE (FLASH_CH4)
#define DMA_DAC_4_DST_BASE (CYDEV_PERIPH_BASE)

/* Variable declarations for DMA_DAC */
/* Move these variable declarations to the top of the function */
uint8 DMA_DAC_4_Chan;
uint8 DMA_DAC_4_TD[N_TDS_DAC];


/* Defines for DMA_ADC_1 */
#define DMA_ADC_1_BYTES_PER_BURST 2
#define DMA_ADC_1_REQUEST_PER_BURST 1
#define DMA_ADC_1_SRC_BASE (CYDEV_PERIPH_BASE)
#define DMA_ADC_1_DST_BASE (CYDEV_SRAM_BASE)

/* Variable declarations for DMA_ADC */
/* Move these variable declarations to the top of the function */
uint8 DMA_ADC_1_Chan;
uint8 DMA_ADC_1_TD[N_TDS_ADC];

/* Defines for DMA_ADC_2 */
#define DMA_ADC_2_BYTES_PER_BURST 2
#define DMA_ADC_2_REQUEST_PER_BURST 1
#define DMA_ADC_2_SRC_BASE (CYDEV_PERIPH_BASE)
#define DMA_ADC_2_DST_BASE (CYDEV_SRAM_BASE)

/* Variable declarations for DMA_ADC */
/* Move these variable declarations to the top of the function */
uint8 DMA_ADC_2_Chan;
uint8 DMA_ADC_2_TD[N_TDS_ADC];

// auxilliary variables
char    sms         [UART_BUF_OUT];
char    puttyIn     [UART_BUF_IN];
uint16  bytenumber = 0;
int     rxBuf;
int     rxBufBLE;
uint8   run_count_DAC_1=0;
uint8   ready_to_start_sequence = FALSE;


// USBUART (USBFS)
#define USBUART_BUFFER_SIZE 64u //Original
#define USBFS_DEVICE    (0u)
#define USBFS_TX_SIZE   60    // exakt package size
uint16 count;
uint8 buffer[USBFS_TX_SIZE];


// programm sequence
const uint size_of_header  = 8;
const uint size_of_segment = 50;
uint packages_received = 0;


// Two adc buffers 
uint16 signal_adc_1[NSAMPLES_ADC]; 
uint16 signal_adc_2[NSAMPLES_ADC];


// function prototypes
void init_components(void);
void run_sequence(void);
void usbfs_interface(void);
void get_data_package( uint8 * , size_t );
uint8 * get_extern_data_package_board_1( size_t );
void usbfs_send_adc_data(void);
void usbfs_send_adc_data_board_1(void);
void dma_dac_1_init(void);
void dma_dac_2_init(void);
void dma_dac_3_init(void);
void dma_dac_4_init(void);
void dma_adc_1_init(void);
void dma_adc_2_init(void);
void set_dac_range_1V(void);
void set_dac_range_4V(void);
void set_rx_gain(char);


CY_ISR_PROTO( isr_triggerIn );
CY_ISR_PROTO( isr_DAC_1_done );
CY_ISR_PROTO( isr_DAC_2_done );
CY_ISR_PROTO( isr_DAC_3_done );
CY_ISR_PROTO( isr_DAC_4_done );
CY_ISR_PROTO( isr_ADC_1_done );
CY_ISR_PROTO( isr_ADC_2_done );


uint8 count_of_runs=0;
uint8 isDAC1Busy = FALSE;


int main(void){
    // Initialization routines
    init_components();
    
    // Avoid errorness serial input due to initial switching noise:
    CyDelay(500);
      
    for(;;){

        // fast usbfs iterface
        usbfs_interface(); // for using fast USBUART routed to the onboard Micro-USB-B socket
        
    }//endfor(;;)
}/* END MAIN() ***********************************/



void init_components(void){
    CyGlobalIntEnable;    
    
    // Board synchronisation
    UART_Master_Board_1_Start();
    UART_Slave_Board_1_Start();
    
   
    // ADDA Clock
    pwmSAMPLING_Start();
    
    // Transmit channels    
    set_dac_range_4V();
    
    IDAC8_1_Start();
        IDAC8_1_SetValue(IDLE_VALUE_CH1); // Set dc value for avoiding base level fluctuations before first run (due to DC block capacitors)
        ClockShift_1_WriteRegValue(CLOCK_SHIFT_CH1); // Shift Register are for avoiding simultaneous DMA requests
        ClockShift_1_Start();
    IDAC8_2_Start();
        IDAC8_2_SetValue(IDLE_VALUE_CH2);
        ClockShift_2_WriteRegValue(CLOCK_SHIFT_CH2);
        ClockShift_2_Start();
    IDAC8_3_Start();
        IDAC8_3_SetValue(IDLE_VALUE_CH3);
        ClockShift_3_WriteRegValue(CLOCK_SHIFT_CH3);
        ClockShift_3_Start();
    IDAC8_4_Start();
        IDAC8_4_SetValue(IDLE_VALUE_CH4);
        ClockShift_4_WriteRegValue(CLOCK_SHIFT_CH4);
        ClockShift_4_Start();
   
    //Waveforms in flash need to be extendet with dac idle values
    // for 256 additional steps to allow wave shifting of up to 256 steps 
    // (regarding command KEY_SHIFT_WAVEFORMS)
    uint8 dac_idle_ch1[NSAMPLES_ADC];
    uint8 dac_idle_ch2[NSAMPLES_ADC];
    uint8 dac_idle_ch3[NSAMPLES_ADC];
    uint8 dac_idle_ch4[NSAMPLES_ADC];
    if( *(FLASH_CH4+(NSAMPLES_ADC-1)) != IDLE_VALUE_CH4 )
    {// -> write to flash only once after programming
        
        for(int i=0;i<(NSAMPLES_ADC/2);i++){
            dac_idle_ch1[i] = IDLE_VALUE_CH1;
            dac_idle_ch2[i] = IDLE_VALUE_CH2;
            dac_idle_ch3[i] = IDLE_VALUE_CH3;
            dac_idle_ch4[i] = IDLE_VALUE_CH4;
        }//END for(int i=0;i<(NSAMPLES_ADC/2);i++) 
        FLASH_Write( dac_idle_ch1, FLASH_CH1+(NSAMPLES_ADC/2), NSAMPLES_ADC);    
        FLASH_Write( dac_idle_ch2, FLASH_CH2+(NSAMPLES_ADC/2), NSAMPLES_ADC);    
        FLASH_Write( dac_idle_ch3, FLASH_CH3+(NSAMPLES_ADC/2), NSAMPLES_ADC);    
        FLASH_Write( dac_idle_ch4, FLASH_CH4+(NSAMPLES_ADC/2), NSAMPLES_ADC); 
        
    }//END if( *(FLASH_CH2+(3*NSAMPLES_DAC-1)) != IDLE_VALUE_CH2_CH3_CH4 )
    

    // Receive channel
    ADC_SAR_1_Start();
        ADC_SAR_1_IRQ_Disable();
    ADC_SAR_2_Start();
        ADC_SAR_2_IRQ_Disable();
    sigBuf_Start();
    sigBuf_SetGain( sigBuf_GAIN_01 );									 
    sigBuf_2_Start();
    sigBuf_2_SetGain( sigBuf_2_GAIN_01 );									 
    sigBuf_3_Start();
    sigBuf_3_SetGain( sigBuf_3_GAIN_01 );									 
    
    
    // Components for user interface and debugging

    isrTrigger_StartEx( isr_triggerIn );
        
    isr_DAC_1_StartEx( isr_DAC_1_done );
    isr_DAC_2_StartEx( isr_DAC_2_done );
    isr_DAC_3_StartEx( isr_DAC_3_done );
    isr_DAC_4_StartEx( isr_DAC_4_done );
    isr_ADC_1_StartEx( isr_ADC_1_done );
    isr_ADC_2_StartEx( isr_ADC_2_done );

    USBUART_Start(USBFS_DEVICE, USBUART_5V_OPERATION);
    
}

void usbfs_interface(void)
{
    uint number_of_packages;
    uint package_number;
    uint number_of_samples;
    uint channel_number;
    char * wave_segment_ptr;
    
     /* Host can send double SET_INTERFACE request. */
    if (0u != USBUART_IsConfigurationChanged())
    {
        /* Initialize IN endpoints when device is configured. */
        if (0u != USBUART_GetConfiguration())
        {
            /* Enumeration is done, enable OUT endpoint to receive data 
             * from host. */
            USBUART_CDC_Init();
        }
    }

    /* Service USB CDC when device is configured. */
    if (0u != USBUART_GetConfiguration())
    {
        /* Check for input data from host. */
        if (0u != USBUART_DataIsReady())
        {
            /* Read received data and re-enable OUT endpoint. */
            count = USBUART_GetAll(buffer);

            if (0u != count)
            {   
               
                /* Wait until component is ready to send data to host. */
                while (0u == USBUART_CDCIsReady())
                {
                }
                
                /* Process firmware commands */
                
                // 0) Test board sync
                if( buffer[0] == KEY_BOARD_SYNC )
                    usbfs_send_adc_data_board_1();                
                
                // 1) select rx-Gain
                if (      buffer[0] >= KEY_AMP_0
                      &&  buffer[0] <= KEY_AMP_9
					){
                    set_rx_gain( buffer[0] );								 
                }//END if ( buffer[0] == ...		  
                // 2) run sequence
                if ( buffer[0] == KEY_RUN)
                    run_sequence();
                // 3) reset firmware 
                if ( buffer[0] == KEY_RESET )
                    CySoftwareReset(); // If Putty is used: this ends the session!
                // 4) set VDAC output range to 1V (default, voltage DACs only, comment code out when using current DACs)
                if ( buffer[0] == KEY_VDAC_1V )
                    set_dac_range_1V();

                // 5) set VDAC output range to 4V (voltage DACs only, comment code out when using current DACs)
                if ( buffer[0] == KEY_VDAC_4V )
                    set_dac_range_4V();
                    
                // 6) writes new sequence
                if ( buffer[0] == KEY_WRITE_SEQUENCE )
                {
                    // get parameters:
                    number_of_packages  = (256*buffer[4]+buffer[5]);
                    package_number      = (256*buffer[2]+buffer[3]);
                    number_of_samples   = number_of_packages*size_of_segment;
                    channel_number      = buffer[1];
                    
                    // write wave into flash memory:
                    wave_segment_ptr    = ((char *) signal_adc_1) + size_of_segment * package_number;
                    memcpy(  wave_segment_ptr, (char *) &buffer[size_of_header], size_of_segment );                  
                    if( package_number == (number_of_packages-1) )
                    {
                        FLASH_Write( (uint8*)signal_adc_1, FLASH_STORAGE[channel_number], number_of_samples-20);
                    }
                }
                
                // 9) Firmware information              
                if ( buffer[0] == KEY_VERSION )
                {
                    while (0u == USBUART_CDCIsReady());
                    USBUART_PutData( (uint8 *) version , 3);
                }
                // 10) Chip information
                int strlength = 34;
                char pseudoid[strlength];
                if ( buffer[0] == KEY_SERIAL_NUMBER )
                {
                    sprintf( pseudoid, "                                  ");
                    sprintf( pseudoid, "%3d %3d %3d %3d %3d %3d %3d",\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_Y_LOC,\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_X_LOC,\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_WAFER_NUM,\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_LOT_LSB,\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_LOT_MSB,\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_WRK_WK,\
                        *(uint8 *)CYREG_FLSHID_CUST_TABLES_FAB_YR);
                    
                    while (0u == USBUART_CDCIsReady());
                    USBUART_PutData( (uint8 *)pseudoid , strlength);
                    
                }
                
                // 11a) Shift waveforms in multiples of sampling time
                if( buffer[0] == KEY_SHIFT_WAVEFORMS ){
                    if( buffer[1] == '1' ){// Shift channel CH1
                        flash_offset_ch1 = (buffer[2]<<8)+buffer[3];
                    }else if( buffer[1] == '2' ){// Shift channel CH2
                        flash_offset_ch2 = (buffer[2]<<8)+buffer[3];
                    }else if( buffer[1] == '3' ){// Shift channel CH3
                        flash_offset_ch2 = (buffer[2]<<8)+buffer[3];
                    }else if( buffer[1] == '4' ){// Shift channel CH4
                        flash_offset_ch2 = (buffer[2]<<8)+buffer[3];
                    }else if( buffer[1] == 'A' ){// Shift all channels
                        flash_offset_ch1  = (buffer[2]<<8)+buffer[3];
                        flash_offset_ch2  = (buffer[2]<<8)+buffer[3];
                        flash_offset_ch3  = (buffer[2]<<8)+buffer[3];
                        flash_offset_ch4  = (buffer[2]<<8)+buffer[3];
                    }
                }//END if( buffer[0] == KEY_SHIFT_WAVEFORMS )
                
                
                // 11) Get the binary data from the two uint16 ADC buffers
                if ( buffer[0] == KEY_SEND_BYTE_DAT )
                    usbfs_send_adc_data();


            }
        }
    }
}//END usbfs_interface()


void usbfs_send_adc_data(void){

    // turn uint16 arrays into byte stream (ADC 1 and ADC 2 separate)
    for(int pkt_j=0; pkt_j<2*NSAMPLES_ADC/USBFS_TX_SIZE*DMA_ADC_1_BYTES_PER_BURST; ++pkt_j)
    {
        // a) create data packet fitting in usb tx buffer
        uint8 adc1_adc2_interleaved[USBFS_TX_SIZE];
        get_data_package( adc1_adc2_interleaved, pkt_j );
        
        // b) send
        while (0u == USBUART_CDCIsReady());            
        USBUART_PutData( adc1_adc2_interleaved , USBFS_TX_SIZE );  
    }
    
}//END usbfs_send_adc_data(void)


void get_data_package( uint8 * adc_data_packet, size_t packet_i ){
      
    uint8 * adc1_ptr = (uint8 *) (signal_adc_1);
    uint8 * adc2_ptr = (uint8 *) (signal_adc_2);
    
    // a) create data packet fitting in usb tx buffer
    for(int m=0; m<USBFS_TX_SIZE/4; m++) // ;m <= USBFS_TX_SIZE/4; ?? (in old code)
    {
        adc_data_packet[4*m+0]=*( adc1_ptr + ( packet_i * USBFS_TX_SIZE/2+(2*m+1)) );                           
        adc_data_packet[4*m+1]=*( adc1_ptr + ( packet_i * USBFS_TX_SIZE/2+(2*m+0)) );                           
        adc_data_packet[4*m+2]=*( adc2_ptr + ( packet_i * USBFS_TX_SIZE/2+(2*m+1)) );                           
        adc_data_packet[4*m+3]=*( adc2_ptr + ( packet_i * USBFS_TX_SIZE/2+(2*m+0)) );                           
    } 
    
}//END get_data_package()


uint8 * get_extern_data_package_board_1( size_t packet_i ){
    
    // UART needs to run at 72 MHz or 36 MHz, fails at 18 MHz

    // 1) Request packet_i from board 1
    // 2) return pointer of rx buffer of UART_Master_Board_1
    
    
    // 1) Board 1 Mock up request
    // 1a) Mockup command for requesting packet_i
    
    
    
    // 1b) Mockup data
    uint8 adc1_adc2_interleaved[USBFS_TX_SIZE];
    get_data_package( adc1_adc2_interleaved, packet_i ); 
    UART_Slave_Board_1_PutArray( adc1_adc2_interleaved, USBFS_TX_SIZE );
    

    // 2) Pass pointer to rx array after packet has arrived
    // 2a) Wait until rx buffer has USBFS_TX_SIZE bytes
    int time_out = 0;
    int timeout_reached = FALSE;
    const int timeout_cycles = 10000;
    while( UART_Master_Board_1_GetRxBufferSize() < USBFS_TX_SIZE ){
        ++time_out;
        if( time_out > timeout_cycles ){
            timeout_reached = TRUE;
            break;
        }
    }           
    
    if( timeout_reached )// Mark packet as invalid
        for( int i=0; i < USBFS_TX_SIZE; ++i)         
            UART_Master_Board_1_rxBuffer[i] = 0xff;      

    return (uint8 *) UART_Master_Board_1_rxBuffer;
}//END get_data_package_board_1( uint8 *, size_t )


void usbfs_send_adc_data_board_1(void){
    
    // turn uint16 arrays into byte stream (ADC 1 and ADC 2 separate)
    for(int pkt_i=0; pkt_i<2*NSAMPLES_ADC/USBFS_TX_SIZE*DMA_ADC_1_BYTES_PER_BURST; ++pkt_i)
    {
        // a) get data packet fitting in usb tx buffer
        uint8 * uart_rx_master_board_1_PTR = get_extern_data_package_board_1( pkt_i );
       
        // b) send
        while (0u == USBUART_CDCIsReady());            
        USBUART_PutData( uart_rx_master_board_1_PTR, USBFS_TX_SIZE);  
    }
    
}//END usbfs_send_adc_data_board_1(void)

void run_sequence(void){
 
    // Trigger In:
    //   posedge: reset PWM for ADDA clock generation, set up dmas
    //   negedge: reset in is low -> ADDA clock starts running
    
    // Reset trigger adjustments
    ClockShift_1_Stop(); ClockShift_1_WriteRegValue(CLOCK_SHIFT_CH1); ClockShift_1_Start();
    ClockShift_2_Stop(); ClockShift_2_WriteRegValue(CLOCK_SHIFT_CH2); ClockShift_2_Start();
    ClockShift_3_Stop(); ClockShift_3_WriteRegValue(CLOCK_SHIFT_CH3); ClockShift_3_Start();
    ClockShift_4_Stop(); ClockShift_4_WriteRegValue(CLOCK_SHIFT_CH4); ClockShift_4_Start();      

    dma_dac_1_init();
    dma_dac_2_init();
    

    dma_dac_3_init();
    dma_dac_4_init();

    dma_adc_1_init();
    dma_adc_2_init();
    
    count_of_runs++;
}//END run_sequence()

void set_dac_range_1V(void) {
    // Comment/uncomment for switching between 
    // current DACs and voltage DACs
    
    IDAC8_1_SetRange( IDAC8_1_RANGE_255uA );
    //IDAC8_1_SetRange( IDAC8_1_RANGE_1V );
    
    IDAC8_2_SetRange( IDAC8_2_RANGE_255uA );
    //IDAC8_2_SetRange( IDAC8_1_RANGE_1V );
    
    IDAC8_3_SetRange( IDAC8_3_RANGE_255uA );
    //IDAC8_3_SetRange( IDAC8_1_RANGE_1V );
    
    IDAC8_4_SetRange( IDAC8_4_RANGE_255uA );
    //IDAC8_4_SetRange( IDAC8_1_RANGE_1V );  
}//END set_dac_range_1V()


void set_dac_range_4V(void){
    // Comment/uncomment for switching between 
    // current DACs and voltage DACs
        
    IDAC8_2_SetRange( IDAC8_2_RANGE_2mA );
    //IDAC8_1_SetRange( IDAC8_1_RANGE_4V );
    
    IDAC8_2_SetRange( IDAC8_2_RANGE_2mA );
    //IDAC8_2_SetRange( IDAC8_2_RANGE_4V );
    
    IDAC8_3_SetRange( IDAC8_3_RANGE_2mA );
    //IDAC8_3_SetRange( IDAC8_3_RANGE_4V );
    
    IDAC8_4_SetRange( IDAC8_4_RANGE_2mA );
    //IDAC8_4_SetRange( IDAC8_1_RANGE_4V ); 
}//END set_dac_range_4V()


void set_rx_gain(char gain_val){
    if( gain_val == KEY_AMP_0 ){
        sigBuf_SetGain( sigBuf_GAIN_01 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_01 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_1 ){
        sigBuf_SetGain( sigBuf_GAIN_02 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_01 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_2 ){
        sigBuf_SetGain( sigBuf_GAIN_02 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_02 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_3 ){
        sigBuf_SetGain( sigBuf_GAIN_04 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_02 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_4 ){
        sigBuf_SetGain( sigBuf_GAIN_04 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_04 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_5 ){
        sigBuf_SetGain( sigBuf_GAIN_08 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_04 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_6 ){
        sigBuf_SetGain( sigBuf_GAIN_08 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_08 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }
    if( gain_val == KEY_AMP_7 ){
        sigBuf_SetGain( sigBuf_GAIN_16 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_08 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }    
    if( gain_val == KEY_AMP_8 ){
        sigBuf_SetGain( sigBuf_GAIN_16 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_16 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_01 );
    }    
    if( gain_val == KEY_AMP_9 ){ // KEY_AMP_5 for high bandwidth
        sigBuf_SetGain( sigBuf_GAIN_04 );
        sigBuf_2_SetGain( sigBuf_2_GAIN_04 );
        sigBuf_3_SetGain( sigBuf_3_GAIN_02 );
    }    
}//END set_rx_gain(char)

    
void dma_dac_1_init(void)
{
    /* DMA Configuration for DMA_DAC_1 */
    if( count_of_runs == 0)
    {
        DMA_DAC_1_Chan = DMA_DAC_1_DmaInitialize(DMA_DAC_1_BYTES_PER_BURST, DMA_DAC_1_REQUEST_PER_BURST, 
            HI16(DMA_DAC_1_SRC_BASE), HI16(DMA_DAC_1_DST_BASE));
        DMA_DAC_1_TD[0] = CyDmaTdAllocate();
        DMA_DAC_1_TD[1] = CyDmaTdAllocate();
        DMA_DAC_1_TD[2] = CyDmaTdAllocate();
    }
    CyDmaTdSetConfiguration(DMA_DAC_1_TD[0], NSAMPLES_DAC, DMA_DAC_1_TD[1], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_1_TD[1], NSAMPLES_DAC, DMA_DAC_1_TD[2], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_1_TD[2], NSAMPLES_DAC, CY_DMA_DISABLE_TD, DMA_DAC_1__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetAddress(DMA_DAC_1_TD[0], LO16((uint32)(FLASH_CH1)                  ), LO16((uint32)IDAC8_1_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_1_TD[1], LO16((uint32)(FLASH_CH1) + NSAMPLES_DAC   ), LO16((uint32)IDAC8_1_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_1_TD[2], LO16((uint32)(FLASH_CH1) + 2*NSAMPLES_DAC ), LO16((uint32)IDAC8_1_Data_PTR));
    CyDmaChSetInitialTd(DMA_DAC_1_Chan, DMA_DAC_1_TD[0]);
    CyDmaChEnable(DMA_DAC_1_Chan, 1);
}

void dma_dac_2_init(void)
{
    /* DMA Configuration for DMA_DAC_2 */
    if( count_of_runs == 0)
    {
        DMA_DAC_2_Chan = DMA_DAC_2_DmaInitialize(DMA_DAC_2_BYTES_PER_BURST, DMA_DAC_2_REQUEST_PER_BURST, 
            HI16(DMA_DAC_2_SRC_BASE), HI16(DMA_DAC_2_DST_BASE));
        DMA_DAC_2_TD[0] = CyDmaTdAllocate();
        DMA_DAC_2_TD[1] = CyDmaTdAllocate();
        DMA_DAC_2_TD[2] = CyDmaTdAllocate();
    }
    CyDmaTdSetConfiguration(DMA_DAC_2_TD[0], NSAMPLES_DAC, DMA_DAC_2_TD[1], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_2_TD[1], NSAMPLES_DAC, DMA_DAC_2_TD[2], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_2_TD[2], NSAMPLES_DAC, CY_DMA_DISABLE_TD, DMA_DAC_2__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetAddress(DMA_DAC_2_TD[0], LO16((uint32)(FLASH_CH2)                 ), LO16((uint32)IDAC8_2_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_2_TD[1], LO16((uint32)(FLASH_CH2) + NSAMPLES_DAC  ), LO16((uint32)IDAC8_2_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_2_TD[2], LO16((uint32)(FLASH_CH2) + 2*NSAMPLES_DAC), LO16((uint32)IDAC8_2_Data_PTR));
    CyDmaChSetInitialTd(DMA_DAC_2_Chan, DMA_DAC_2_TD[0]);
    CyDmaChEnable(DMA_DAC_2_Chan, 1);
}

void dma_dac_3_init(void)
{
    /* DMA Configuration for DMA_DAC_3 */
    if( count_of_runs == 0)
    {
        DMA_DAC_3_Chan = DMA_DAC_3_DmaInitialize(DMA_DAC_3_BYTES_PER_BURST, DMA_DAC_3_REQUEST_PER_BURST, 
            HI16(DMA_DAC_3_SRC_BASE), HI16(DMA_DAC_3_DST_BASE));
        DMA_DAC_3_TD[0] = CyDmaTdAllocate();
        DMA_DAC_3_TD[1] = CyDmaTdAllocate();
        DMA_DAC_3_TD[2] = CyDmaTdAllocate();
    }
    CyDmaTdSetConfiguration(DMA_DAC_3_TD[0], NSAMPLES_DAC, DMA_DAC_3_TD[1], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_3_TD[1], NSAMPLES_DAC, DMA_DAC_3_TD[2], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_3_TD[2], NSAMPLES_DAC, CY_DMA_DISABLE_TD, DMA_DAC_3__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetAddress(DMA_DAC_3_TD[0], LO16((uint32)(FLASH_CH3)                 ), LO16((uint32)IDAC8_3_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_3_TD[1], LO16((uint32)(FLASH_CH3) + NSAMPLES_DAC  ), LO16((uint32)IDAC8_3_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_3_TD[2], LO16((uint32)(FLASH_CH3) + 2*NSAMPLES_DAC), LO16((uint32)IDAC8_3_Data_PTR));
    CyDmaChSetInitialTd(DMA_DAC_3_Chan, DMA_DAC_3_TD[0]);
    CyDmaChEnable(DMA_DAC_3_Chan, 1);
}

void dma_dac_4_init(void)
{
    /* DMA Configuration for DMA_DAC_4 */
    if( count_of_runs == 0)
    {
        DMA_DAC_4_Chan = DMA_DAC_4_DmaInitialize(DMA_DAC_4_BYTES_PER_BURST, DMA_DAC_4_REQUEST_PER_BURST, 
            HI16(DMA_DAC_4_SRC_BASE), HI16(DMA_DAC_4_DST_BASE));
        DMA_DAC_4_TD[0] = CyDmaTdAllocate();
        DMA_DAC_4_TD[1] = CyDmaTdAllocate();
        DMA_DAC_4_TD[2] = CyDmaTdAllocate();
    }
    CyDmaTdSetConfiguration(DMA_DAC_4_TD[0], NSAMPLES_DAC, DMA_DAC_4_TD[1], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_4_TD[1], NSAMPLES_DAC, DMA_DAC_4_TD[2], CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetConfiguration(DMA_DAC_4_TD[2], NSAMPLES_DAC, CY_DMA_DISABLE_TD, DMA_DAC_4__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR);
    CyDmaTdSetAddress(DMA_DAC_4_TD[0], LO16((uint32)(FLASH_CH4)                 ), LO16((uint32)IDAC8_4_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_4_TD[1], LO16((uint32)(FLASH_CH4) + NSAMPLES_DAC  ), LO16((uint32)IDAC8_4_Data_PTR));
    CyDmaTdSetAddress(DMA_DAC_4_TD[2], LO16((uint32)(FLASH_CH4) + 2*NSAMPLES_DAC), LO16((uint32)IDAC8_4_Data_PTR));
    CyDmaChSetInitialTd(DMA_DAC_4_Chan, DMA_DAC_4_TD[0]);
    CyDmaChEnable(DMA_DAC_4_Chan, 1);
}

void dma_adc_1_init(void)
{
    /* DMA Configuration for DMA_ADC_1 */
    if( count_of_runs == 0)
    {
        DMA_ADC_1_Chan = DMA_ADC_1_DmaInitialize(DMA_ADC_1_BYTES_PER_BURST, DMA_ADC_1_REQUEST_PER_BURST, 
            HI16(DMA_ADC_1_SRC_BASE), HI16(DMA_ADC_1_DST_BASE));
        
        for (int i=0;i<N_TDS_ADC;i++) {
            DMA_ADC_1_TD[i] = CyDmaTdAllocate();
        }
    }
    
    uint16_t d0=NSAMPLES_ADC/(N_TDS_ADC/2);
    uint16_t d1=d0 * DMA_ADC_1_BYTES_PER_BURST;
    
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 0], d1, DMA_ADC_1_TD[ 1], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 1], d1, DMA_ADC_1_TD[ 2], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 2], d1, DMA_ADC_1_TD[ 3], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 3], d1, DMA_ADC_1_TD[ 4], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 4], d1, DMA_ADC_1_TD[ 5], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 5], d1, DMA_ADC_1_TD[ 6], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 6], d1, DMA_ADC_1_TD[ 7], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 7], d1, DMA_ADC_1_TD[ 8], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 8], d1, DMA_ADC_1_TD[ 9], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 9], d1, DMA_ADC_1_TD[10], CY_DMA_TD_INC_DST_ADR);

    if (IGNORE_FIRST_PART==1){
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[10], d1, DMA_ADC_1_TD[11], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[11], d1, DMA_ADC_1_TD[12], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[12], d1, DMA_ADC_1_TD[13], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[13], d1, DMA_ADC_1_TD[14], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[14], d1, DMA_ADC_1_TD[15], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[15], d1, DMA_ADC_1_TD[16], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[16], d1, DMA_ADC_1_TD[17], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[17], d1, DMA_ADC_1_TD[18], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[18], d1, DMA_ADC_1_TD[19], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[19], d1, CY_DMA_DISABLE_TD, DMA_ADC_1__TD_TERMOUT_EN | (CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART));
    }else{
        CyDmaTdSetConfiguration(DMA_ADC_1_TD[ 9], d1, CY_DMA_DISABLE_TD, DMA_ADC_1__TD_TERMOUT_EN | CY_DMA_TD_INC_DST_ADR);
    }
    
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 0], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(0*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 1], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(1*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 2], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(2*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 3], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(3*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 4], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(4*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 5], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(5*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 6], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(6*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 7], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(7*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 8], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(8*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_1_TD[ 9], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(9*d0 * DMA_ADC_1_BYTES_PER_BURST)));

    if (IGNORE_FIRST_PART==1){
        CyDmaTdSetAddress(DMA_ADC_1_TD[10], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(0*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[11], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(1*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[12], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(2*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[13], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(3*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[14], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(4*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[15], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(5*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[16], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(6*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[17], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(7*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[18], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(8*d0 * DMA_ADC_1_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_1_TD[19], LO16((uint32)ADC_SAR_1_SAR_WRK0_PTR), LO16((uint32)signal_adc_1 +(9*d0 * DMA_ADC_1_BYTES_PER_BURST)));
    }
    CyDmaChSetInitialTd(DMA_ADC_1_Chan, DMA_ADC_1_TD[0]);
    CyDmaChEnable(DMA_ADC_1_Chan, 1);     
}

void dma_adc_2_init(void)
{
    /* DMA Configuration for DMA_ADC_2 */
    if( count_of_runs == 0)
    {
        DMA_ADC_2_Chan = DMA_ADC_2_DmaInitialize(DMA_ADC_2_BYTES_PER_BURST, DMA_ADC_2_REQUEST_PER_BURST, 
            HI16(DMA_ADC_2_SRC_BASE), HI16(DMA_ADC_2_DST_BASE));

        for (int i=0;i<N_TDS_ADC;i++) {
            DMA_ADC_2_TD[i] = CyDmaTdAllocate();
        }
    }

    uint16_t d0=NSAMPLES_ADC/(N_TDS_ADC/2);
    uint16_t d1=d0 * DMA_ADC_2_BYTES_PER_BURST;
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 0], d1, DMA_ADC_2_TD[ 1], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 1], d1, DMA_ADC_2_TD[ 2], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 2], d1, DMA_ADC_2_TD[ 3], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 3], d1, DMA_ADC_2_TD[ 4], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 4], d1, DMA_ADC_2_TD[ 5], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 5], d1, DMA_ADC_2_TD[ 6], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 6], d1, DMA_ADC_2_TD[ 7], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 7], d1, DMA_ADC_2_TD[ 8], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 8], d1, DMA_ADC_2_TD[ 9], CY_DMA_TD_INC_DST_ADR);
    CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 9], d1, DMA_ADC_2_TD[10], CY_DMA_TD_INC_DST_ADR);

    if (IGNORE_FIRST_PART==1){
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[10], d1, DMA_ADC_2_TD[11], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[11], d1, DMA_ADC_2_TD[12], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[12], d1, DMA_ADC_2_TD[13], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[13], d1, DMA_ADC_2_TD[14], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[14], d1, DMA_ADC_2_TD[15], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[15], d1, DMA_ADC_2_TD[16], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[16], d1, DMA_ADC_2_TD[17], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[17], d1, DMA_ADC_2_TD[18], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[18], d1, DMA_ADC_2_TD[19], CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART);
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[19], d1, CY_DMA_DISABLE_TD,  DMA_ADC_2__TD_TERMOUT_EN | (CY_DMA_TD_INC_DST_ADR * IGNORE_FIRST_PART));
    } else {
        CyDmaTdSetConfiguration(DMA_ADC_2_TD[ 9], d1, CY_DMA_DISABLE_TD, DMA_ADC_1__TD_TERMOUT_EN | CY_DMA_TD_INC_DST_ADR);
    }

    CyDmaTdSetAddress(DMA_ADC_2_TD[ 0], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(0*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 1], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(1*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 2], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(2*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 3], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(3*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 4], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(4*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 5], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(5*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 6], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(6*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 7], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(7*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 8], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(8*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    CyDmaTdSetAddress(DMA_ADC_2_TD[ 9], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(9*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    
    if (IGNORE_FIRST_PART==1){
        CyDmaTdSetAddress(DMA_ADC_2_TD[10], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(0*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[11], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(1*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[12], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(2*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[13], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(3*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[14], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(4*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[15], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(5*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[16], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(6*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[17], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(7*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[18], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(8*d0 * DMA_ADC_2_BYTES_PER_BURST)));
        CyDmaTdSetAddress(DMA_ADC_2_TD[19], LO16((uint32)ADC_SAR_2_SAR_WRK0_PTR), LO16((uint32)signal_adc_2 +(9*d0 * DMA_ADC_2_BYTES_PER_BURST)));
    }
    CyDmaChSetInitialTd(DMA_ADC_2_Chan, DMA_ADC_2_TD[0]);
    CyDmaChEnable(DMA_ADC_2_Chan, 1);     
}

CY_ISR( isr_triggerIn ){
    
    LED_Write( 1 );
           
    run_sequence(); 
    
    CyDelayUs(SEQU_DURATION_US); // Block CPU while sequence is running to avoid interference

    LED_Write( 0 );
}

CY_ISR( isr_DAC_1_done ){

}//endCY_ISR DAC_1

CY_ISR( isr_DAC_2_done )
{
    //CyDelay(10);
    //UART_1_PutString("DAC_2 done!");
    //UART_1_PutCRLF(1);
}

CY_ISR( isr_DAC_3_done )
{
    //CyDelay(10);
    //UART_1_PutString("DAC_3 done!");
    //UART_1_PutCRLF(1);
}

CY_ISR( isr_DAC_4_done )
{
    //CyDelay(10);
    //UART_1_PutString("DAC_4 done!");
    //UART_1_PutCRLF(1);
}

CY_ISR( isr_ADC_1_done )
{
    //CyDelay(10);
    //UART_1_PutString("ADC_1 done!");
    //UART_1_PutCRLF(1);
}

CY_ISR( isr_ADC_2_done )
{
    //CyDelay(10);
    //UART_1_PutString("ADC_2 done!");
    //UART_1_PutCRLF(1);
}


/* [] END OF FILE */
