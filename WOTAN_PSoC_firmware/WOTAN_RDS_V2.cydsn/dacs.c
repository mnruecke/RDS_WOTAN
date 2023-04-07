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
#include <math.h>

#include "dacs.h"

void init_dacs(void){
    
    IDAC8_1_Start();
    IDAC8_1_SetRange( IDAC8_1_RANGE_2mA );
    IDAC8_1_SetValue( DAC_IDLE_VALUE );
    
    init_dma_dac_1();
    
}//END init_dacs(void)


void init_dma_dac_1(void){
    /* DMA Configuration for DMA_DAC_1 */
    const int bytes_per_td = DMA_DAC_1_WAVELET_LENGHT / DMA_DAC_1_NUM_OF_TDS;    
    
    DMA_DAC_1_Chan = DMA_DAC_1_DmaInitialize( DMA_DAC_1_BYTES_PER_BURST,
                                              DMA_DAC_1_REQUEST_PER_BURST, 
                                              HI16(DMA_DAC_1_SRC_BASE),
                                              HI16(DMA_DAC_1_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_DAC_1_NUM_OF_TDS; ++td_i)
        DMA_DAC_1_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_DAC_1_NUM_OF_TDS-1); ++td_i) 
        CyDmaTdSetConfiguration( DMA_DAC_1_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_DAC_1_TD[ td_i +1 ],
                                 CY_DMA_TD_INC_SRC_ADR
                                 );
    CyDmaTdSetConfiguration( DMA_DAC_1_TD[ DMA_DAC_1_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             CY_DMA_TD_INC_SRC_ADR
                            );
    
    for(int td_i=0; td_i<(DMA_DAC_1_NUM_OF_TDS-1); ++td_i)
        CyDmaTdSetAddress( DMA_DAC_1_TD[ td_i ],
                           LO16((uint32) &wave_dma_dac_1[ td_i * bytes_per_td ]),
                           LO16((uint32)IDAC8_1_Data_PTR)
                           );
}//END void init_dma_1(void)


void start_dma_dac_1(void){
    CyDmaChSetInitialTd(DMA_DAC_1_Chan, DMA_DAC_1_TD[0]);
    CyDmaChEnable(DMA_DAC_1_Chan, 1);
}//END void start_dma_dac_1(void)


void run_wave(void){
    
    for(int i=0; i<DMA_DAC_1_WAVELET_LENGHT; ++i){
        wave_dma_dac_1[i] = (uint8)(
                        (float)i/DMA_DAC_1_WAVELET_LENGHT*127.5
                        * sin(2.0*M_PI/50.0 * (float)i) + 127.5
                        );   
    }   
    
    
    oTrigger_Write( TRIGGER_POSEDGE );
    oTrigger_Write( TRIGGER_NEGEDGE );
    for(int i=0; i<DMA_DAC_1_WAVELET_LENGHT; ++i){
        IDAC8_1_SetValue( wave_dma_dac_1[i] );   
    }
    IDAC8_1_SetValue( DAC_IDLE_VALUE );
    
}//END run_wave(void)

/* [] END OF FILE */
