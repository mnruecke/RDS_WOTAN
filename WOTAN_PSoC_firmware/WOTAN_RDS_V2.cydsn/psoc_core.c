/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/

#include <stdio.h>
#include <string.h>
#include "psoc_core.h"
#include "dacs.h"

void init_psoc(void){
    
    memcpy( version, "0.1", 3);
  
    USBUART_Start(USBFS_DEVICE, USBUART_5V_OPERATION);
    
    init_dacs();
    
}//END init_psoc(void)

void usbfs_interface(void){
   
    /* Host can send double SET_INTERFACE request. */
    if (0u != USBUART_IsConfigurationChanged()) {
        /* Initialize IN endpoints when device is configured. */
        if (0u != USBUART_GetConfiguration()){
            /* Enumeration is done, enable OUT endpoint to receive data 
             * from host. */
            USBUART_CDC_Init();
        }
    }//END if (0u != USBUART_IsConfigurationChanged())

    /* Service USB CDC when device is configured. */
    if (0u != USBUART_GetConfiguration()){
        /* Check for input data from host. */
        if (0u != USBUART_DataIsReady()){
            /* Read received data and re-enable OUT endpoint. */
            count = USBUART_GetAll(buffer);

            if (0u != count) {   
                
                /* Wait until component is ready to send data to host. */
                while (0u == USBUART_CDCIsReady());  
                            
                usbfs_process_firmware_commands( buffer );
                
            }//END if (0u != count)
        }//END if (0u != USBUART_DataIsReady())
    }//END if (0u != USBUART_GetConfiguration())
}//END usbfs_interface(void)

void usbfs_process_firmware_commands( uint8* buffer ){
    /* Process firmware commands */                                       
    if ( buffer[0] == KEY_VERSION )         usbfs_put_version();
    if ( buffer[0] == KEY_SERIAL_NUMBER )   usbfs_put_chip_id();
    if ( buffer[0] == KEY_WAVE_LENGTH )     usbfs_put_wave_length();
    if ( buffer[0] == KEY_WRITE_SEQUENCE )  usbfs_get_packet( buffer );
    if ( buffer[0] == KEY_CREATE_WAVE )     create_wave();
    if ( buffer[0] == KEY_RUN_WAVE )        run_wave();
    if ( buffer[0] == KEY_RESET )           CySoftwareReset();
    if ( buffer[0] == KEY_GET_RUN_COUNT )   usbfs_put_run_count();    
}//END void usbfs_command_menue( uint8* )

void usbfs_put_version(void){
    while (0u == USBUART_CDCIsReady());
    USBUART_PutData( (uint8 *) version , 3);    
}//END void usbfs_put_version(void)

void usbfs_put_chip_id(void){
    
    int  strlength = 27;
    char pseudoid[strlength];
    
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
}//END void usbfs_put_chip_id(void)

void usbfs_put_run_count(void){
    
    const int run_count_strlen = 6;
    char run_count[run_count_strlen];
    sprintf( run_count, "%5d", dma_dac_1_run_count );
    
    while (0u == USBUART_CDCIsReady());
    USBUART_PutData( (uint8 *) run_count, run_count_strlen);     
}//END void usbfs_get_run_count(void)

void usbfs_put_wave_length(void){
    
    const int wave_len_strlen = 6;
    char wave_len[wave_len_strlen];
    sprintf( wave_len, "%5d", DMA_DAC_WAVELET_LENGTH  );    
    
    while (0u == USBUART_CDCIsReady());
    USBUART_PutData( (uint8 *) wave_len, wave_len_strlen );     
}//END void usbfs_get_wave_length(void)

void usbfs_get_packet( uint8 * buffer ){
    
    // get parameters:
    volatile uint16 number_of_packages = (256*buffer[4]+buffer[5]);
    volatile uint16 package_number     = (256*buffer[2]+buffer[3]);
    volatile uint16 number_of_samples  = number_of_packages * SIZE_OF_SEGMENT;
    volatile uint8  channel_number     = buffer[1];
    
    // write wave into flash memory:
    memcpy( sig_1.dac_data      + SIZE_OF_SEGMENT * package_number,
            (char *) buffer     + SIZE_OF_HEADER,
            SIZE_OF_SEGMENT
            );                  
    if( package_number == (number_of_packages-1) )
    {
        cLED_Write( LED_ON );
        FLASH_Write( sig_1.dac_data, flash2dac_LUT[channel_number], number_of_samples);
        cLED_Write( LED_OFF );
    }  
}//END void usbfs_get_packet(void)

/* [] END OF FILE */
