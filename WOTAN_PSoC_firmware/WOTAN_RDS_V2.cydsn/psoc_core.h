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

#ifndef PSOC_CORE_H_INCLUDED
#define PSOC_CORE_H_INCLUDED

    #include "project.h"

    char  version[3];
    
    #define TRUE    1
    #define FALSE   0
    
    #define LED_ON  1
    #define LED_OFF 0
    
    // USBUART (USBFS)
    #define USBFS_DEVICE            (0u)
    #define USBFS_TX_SIZE           60    // exakt package size
    uint16 count;
    uint8 buffer[USBFS_TX_SIZE];
    
    // programm sequence
    #define SIZE_OF_HEADER      8
    #define SIZE_OF_SEGMENT     50

    /* command set */
    #define KEY_VERSION          'a'
    #define KEY_SERIAL_NUMBER    'b'
    #define KEY_RUN_WAVE         'c'
    #define KEY_RESET            'd'
    #define KEY_CREATE_WAVE      'e'
    #define KEY_GET_RUN_COUNT    'f'
    #define KEY_WRITE_SEQUENCE   'g'
    #define KEY_WAVE_LENGTH      'h'
    #define KEY_ACQUISITION_DONE 'i'
    #define KEY_SEND_ADC_DATA    'j'
    
    void init_psoc(void);
    void usbfs_interface(void);
    void usbfs_process_firmware_commands( uint8* );
    void usbfs_put_version(void);
    void usbfs_put_chip_id(void);
    void usbfs_put_run_count(void);
    void usbfs_get_packet( uint8* );
    void usbfs_put_wave_length(void);
    void usbfs_is_acquisition_done(void);
    void usbfs_send_adc_data( uint8* );

#endif //PSOC_CORE_H_INCLUDED

/* [] END OF FILE */
