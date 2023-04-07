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
                
                //-------------------------------------------------------                
                /* Process firmware commands */                                       
                if ( buffer[0] == KEY_VERSION )         usbfs_put_version();
                if ( buffer[0] == KEY_SERIAL_NUMBER )   usbfs_put_chip_id();
                if ( buffer[0] == KEY_RUN_WAVE )        run_wave();
                
            }//END if (0u != count)
        }//END if (0u != USBUART_DataIsReady())
    }//END if (0u != USBUART_GetConfiguration())
}//END usbfs_interface(void)

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

/* [] END OF FILE */
