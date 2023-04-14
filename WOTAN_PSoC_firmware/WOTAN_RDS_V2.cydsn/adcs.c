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

#include "psoc_core.h"
#include "adcs.h"


void init_adcs(void){
    
    PGA_ADC_Buffer_Start();
    
    ADC_SAR_1_Start();
    ADC_SAR_2_Start();
    
    init_dma_adc_1();
    init_dma_adc_2();
    
    isr_ADC_1_StartEx( isr_ADC_1_done );
    isr_ADC_2_StartEx( isr_ADC_2_done );
    
    acquisition_completed = FALSE;
}

void init_dma_adc_1(void){
    /* DMA Configuration for DMA_ADC_1 */
    const int bytes_per_td = (    DMA_ADC_DATA_LENGTH
                                / DMA_ADC_1_NUM_OF_TDS 
                                * DMA_ADC_1_BYTES_PER_BURST
                                );
    
    DMA_ADC_1_Chan = DMA_ADC_1_DmaInitialize( DMA_ADC_1_BYTES_PER_BURST,
                                              DMA_ADC_1_REQUEST_PER_BURST, 
                                              HI16(DMA_ADC_1_SRC_BASE),
                                              HI16(DMA_ADC_1_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_ADC_1_NUM_OF_TDS; ++td_i)
        DMA_ADC_1_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_ADC_1_NUM_OF_TDS-1); ++td_i) {
        CyDmaTdSetConfiguration( DMA_ADC_1_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_ADC_1_TD[ td_i +1 ],
                                 CY_DMA_TD_INC_DST_ADR
                                 );    
    }//END for(int td_i=0; td_i<(DMA_ADC_1_NUM_OF_TDS-1); ++td_i)
    CyDmaTdSetConfiguration( DMA_ADC_1_TD[ DMA_ADC_1_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             DMA_ADC_1__TD_TERMOUT_EN | CY_DMA_TD_INC_DST_ADR
                            );
    
    for(int td_i=0; td_i<DMA_ADC_1_NUM_OF_TDS; ++td_i)
        CyDmaTdSetAddress( DMA_ADC_1_TD[ td_i ],
                           LO16((uint32) ADC_SAR_1_SAR_WRK0_PTR ),
                           LO16((uint32) sig_1.adc_data[ADC_1] + (td_i * bytes_per_td) )
                           );    
}//END void init_dma_adc_1(void)

void start_dma_adc_1(void){
    CyDmaChSetInitialTd(DMA_ADC_1_Chan, DMA_ADC_1_TD[0]);
    CyDmaChEnable(DMA_ADC_1_Chan, 1);    
}//END void start_dma_adc_1(void)

void init_dma_adc_2(void){
    /* DMA Configuration for DMA_ADC_2 */
    const int bytes_per_td = (    DMA_ADC_DATA_LENGTH
                                / DMA_ADC_2_NUM_OF_TDS 
                                * DMA_ADC_2_BYTES_PER_BURST
                                );  
    
    DMA_ADC_2_Chan = DMA_ADC_2_DmaInitialize( DMA_ADC_2_BYTES_PER_BURST,
                                              DMA_ADC_2_REQUEST_PER_BURST, 
                                              HI16(DMA_ADC_2_SRC_BASE),
                                              HI16(DMA_ADC_2_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_ADC_2_NUM_OF_TDS; ++td_i)
        DMA_ADC_2_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_ADC_2_NUM_OF_TDS-1); ++td_i) {
        CyDmaTdSetConfiguration( DMA_ADC_2_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_ADC_2_TD[ td_i +1 ],
                                 CY_DMA_TD_INC_DST_ADR
                                 );    
    }//END for(int td_i=0; td_i<(DMA_ADC_2_NUM_OF_TDS-1); ++td_i)
    CyDmaTdSetConfiguration( DMA_ADC_2_TD[ DMA_ADC_2_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             DMA_ADC_2__TD_TERMOUT_EN | CY_DMA_TD_INC_DST_ADR
                            );
    
    for(int td_i=0; td_i<DMA_ADC_2_NUM_OF_TDS; ++td_i)
        CyDmaTdSetAddress( DMA_ADC_2_TD[ td_i ],
                           LO16((uint32) ADC_SAR_2_SAR_WRK0_PTR ),
                           LO16((uint32) sig_1.adc_data[ADC_2] + (td_i * bytes_per_td) )
                           );    
}//END void init_dma_adc_2(void)

void start_dma_adc_2(void){
    CyDmaChSetInitialTd(DMA_ADC_2_Chan, DMA_ADC_2_TD[0]);
    CyDmaChEnable(DMA_ADC_2_Chan, 1);    
}//END void start_dma_adc_2(void)

CY_ISR( isr_ADC_1_done ){
    
}//END CY_ISR( isr_ADC_1_done )

CY_ISR( isr_ADC_2_done ){
    acquisition_completed = TRUE;
    CyDelayUs(2);
    cResetTrigger_Write(1);
    cResetTrigger_Write(0);
}//END CY_ISR( isr_ADC_2_done )

/* [] END OF FILE */
