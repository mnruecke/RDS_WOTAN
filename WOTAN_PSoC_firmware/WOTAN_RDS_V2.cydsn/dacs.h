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
    
    int dma_dac_1_run_count;
    
    #define TRIGGER_POSEDGE 1
    #define TRIGGER_NEGEDGE 0
    
    #define DAC_IDLE_VALUE 127
    
    #define  FLASH_DAC_1          (const uint8 *)     0x10000  // max length: 64 kB
    #define  FLASH_DAC_2          (const uint8 *)     0x20000
    #define  FLASH_DAC_3          (const uint8 *)     0x30000
    #define  FLASH_DAC_4          (const uint8 *)     0x0A000 // max length 4: 32kB 
    #define  NUM_OF_CHANNELS      4
    const uint8 * flash2dac_LUT[ NUM_OF_CHANNELS ] ;
  
    /* Defines for DMA_DAC_1 */
    #define DMA_DAC_1_BYTES_PER_BURST 1
    #define DMA_DAC_1_REQUEST_PER_BURST 1
    #define DMA_DAC_1_SRC_BASE (FLASH_DAC_1)
    #define DMA_DAC_1_DST_BASE (CYDEV_PERIPH_BASE)
    #define DMA_DAC_1_NUM_OF_TDS 16

    /* Variable declarations for DMA_DAC_1 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_DAC_1_Chan;
    uint8 DMA_DAC_1_TD[DMA_DAC_1_NUM_OF_TDS];

    /* Defines for DMA_DAC_2 */
    #define DMA_DAC_2_BYTES_PER_BURST 1
    #define DMA_DAC_2_REQUEST_PER_BURST 1
    #define DMA_DAC_2_SRC_BASE (FLASH_DAC_2)
    #define DMA_DAC_2_DST_BASE (CYDEV_PERIPH_BASE)
    #define DMA_DAC_2_NUM_OF_TDS 16

    /* Variable declarations for DMA_DAC_2 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_DAC_2_Chan;
    uint8 DMA_DAC_2_TD[DMA_DAC_2_NUM_OF_TDS];

    
    /* Defines for DMA_DAC_3 */
    #define DMA_DAC_3_BYTES_PER_BURST 1
    #define DMA_DAC_3_REQUEST_PER_BURST 1
    #define DMA_DAC_3_SRC_BASE (FLASH_DAC_3)
    #define DMA_DAC_3_DST_BASE (CYDEV_PERIPH_BASE)
    #define DMA_DAC_3_NUM_OF_TDS 16

    /* Variable declarations for DMA_DAC_3 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_DAC_3_Chan;
    uint8 DMA_DAC_3_TD[DMA_DAC_3_NUM_OF_TDS];

    
    /* Defines for DMA_DAC_4 */
    #define DMA_DAC_4_BYTES_PER_BURST 1
    #define DMA_DAC_4_REQUEST_PER_BURST 1
    #define DMA_DAC_4_SRC_BASE (FLASH_DAC_4)
    #define DMA_DAC_4_DST_BASE (CYDEV_PERIPH_BASE)
    #define DMA_DAC_4_NUM_OF_TDS 16

    /* Variable declarations for DMA_DAC_4 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_DAC_4_Chan;
    uint8 DMA_DAC_4_TD[DMA_DAC_4_NUM_OF_TDS];
    
    
    #define DMA_DAC_1_WAVELET_LENGTH 24000
    #define DMA_DAC_2_WAVELET_LENGTH DMA_DAC_1_WAVELET_LENGTH
    #define DMA_DAC_3_WAVELET_LENGTH DMA_DAC_1_WAVELET_LENGTH
    #define DMA_DAC_4_WAVELET_LENGTH DMA_DAC_1_WAVELET_LENGTH
    
    #define TDS_NUM_FOR_TRIGGER_OUT 4 // Determines number of TDs used for tx start ramp    
    
    #define DMA_DAC_WAVELET_LENGTH   DMA_DAC_1_WAVELET_LENGTH
    #define DISMISS_INITIAL_DATA_POINTS 160
    #define DMA_ADC_DATA_LENGTH         15160
    #define NUM_OF_ADCS 2
    #define ADC_1       0
    #define ADC_2       1
    
    union Signals{
        uint8  temp_dac_data [ DMA_DAC_WAVELET_LENGTH ];
        uint16 adc_data      [ NUM_OF_ADCS ] [ DMA_ADC_DATA_LENGTH ];
    } sig_1;

    void init_dacs       (void);
    void init_dma_dac_1  (void);
    void init_dma_dac_2  (void);
    void init_dma_dac_3  (void);
    void init_dma_dac_4  (void);
    void start_dma_dac_1 (void);
    void start_dma_dac_2 (void);
    void start_dma_dac_3 (void);
    void start_dma_dac_4 (void);
    void create_wave     (void);
    void run_wave        (void);
   
    CY_ISR_PROTO( isr_DACs_done );
    
#endif //DACS_H_INCLUDED

/* [] END OF FILE */
