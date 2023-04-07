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

#ifndef DACS_H_INCLUDED
#define DACS_H_INCLUDED
    
    #include "project.h"
    
    #define TRIGGER_POSEDGE 1
    #define TRIGGER_NEGEDGE 0
    
    #define DAC_IDLE_VALUE 127
    
    /* Defines for DMA_DAC_1 */
    #define DMA_DAC_1_BYTES_PER_BURST 1
    #define DMA_DAC_1_REQUEST_PER_BURST 1
    #define DMA_DAC_1_SRC_BASE (CYDEV_SRAM_BASE)
    #define DMA_DAC_1_DST_BASE (CYDEV_PERIPH_BASE)
    #define DMA_DAC_1_NUM_OF_TDS 16

    /* Variable declarations for DMA_DAC_1 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_DAC_1_Chan;
    uint8 DMA_DAC_1_TD[DMA_DAC_1_NUM_OF_TDS];
    
    #define DMA_DAC_1_WAVELET_LENGHT 1600
    uint8 wave_dma_dac_1[ DMA_DAC_1_WAVELET_LENGHT ];

    void init_dacs(void);
    void init_dma_dac_1(void);
    void start_dma_dac_1(void);
    void run_wave(void);

#endif //DACS_H_INCLUDED

/* [] END OF FILE */
