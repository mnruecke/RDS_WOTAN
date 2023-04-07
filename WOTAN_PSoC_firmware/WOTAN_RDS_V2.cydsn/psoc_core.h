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
    
    // USBUART (USBFS)
    #define USBFS_DEVICE            (0u)
    #define USBFS_TX_SIZE           60    // exakt package size
    uint16 count;
    uint8 buffer[USBFS_TX_SIZE];
    
    // programm sequence
    #define SIZE_OF_HEADER      8
    #define SIZE_OF_SEGMENT     50

    /* command set */
    #define KEY_VERSION         'a'
    #define KEY_SERIAL_NUMBER   'b'
    #define KEY_RUN_WAVE        'c'
    
    
    void init_psoc(void);
    void usbfs_interface(void);
    void usbfs_put_version(void);
    void usbfs_put_chip_id(void);

#endif //PSOC_CORE_H_INCLUDED

/* [] END OF FILE */
