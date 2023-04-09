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

#ifndef ADCS_H_INCLUDED
#define ADCS_H_INCLUDED
  
    #include "project.h"
    #include "dacs.h"
    
    uint8 acquisition_completed;
    
    /* Defines for DMA_ADC_1 */
    #define DMA_ADC_1_BYTES_PER_BURST 2
    #define DMA_ADC_1_REQUEST_PER_BURST 1
    #define DMA_ADC_1_SRC_BASE (CYDEV_PERIPH_BASE)
    #define DMA_ADC_1_DST_BASE (CYDEV_SRAM_BASE)
    #define DMA_ADC_1_NUM_OF_TDS 16
   
    /* Variable declarations for DMA_ADC_1 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_ADC_1_Chan;
    uint8 DMA_ADC_1_TD[DMA_ADC_1_NUM_OF_TDS];
    
    
    /* Defines for DMA_ADC_2 */
    #define DMA_ADC_2_BYTES_PER_BURST 2
    #define DMA_ADC_2_REQUEST_PER_BURST 1
    #define DMA_ADC_2_SRC_BASE (CYDEV_PERIPH_BASE)
    #define DMA_ADC_2_DST_BASE (CYDEV_SRAM_BASE)
    #define DMA_ADC_2_NUM_OF_TDS 16
   
    /* Variable declarations for DMA_ADC_2 */
    /* Move these variable declarations to the top of the function */
    uint8 DMA_ADC_2_Chan;
    uint8 DMA_ADC_2_TD[DMA_ADC_2_NUM_OF_TDS];
    
    
    void init_adcs(void);
    void init_dma_adc_1(void);
    void init_dma_adc_2(void);
    void start_dma_adc_1(void);
    void start_dma_adc_2(void);
    
    CY_ISR_PROTO( isr_ADC_1_done );
    CY_ISR_PROTO( isr_ADC_2_done );
    
#endif //ADCS_H_INCLUDED

/* [] END OF FILE */
