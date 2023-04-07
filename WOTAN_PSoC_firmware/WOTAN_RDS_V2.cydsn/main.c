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
#include "project.h"
#include "psoc_core.h"

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */
   
    init_psoc();

    /* Place your initialization/startup code here (e.g. MyInst_Start()) */
    
    for(;;)
    {
        usbfs_interface();   
    }
}

/* [] END OF FILE */
