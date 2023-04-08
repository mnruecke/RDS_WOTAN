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
    
            
    flash2dac_LUT[0] = FLASH_DAC_1;
    flash2dac_LUT[1] = FLASH_DAC_2;
    flash2dac_LUT[2] = FLASH_DAC_3;
    flash2dac_LUT[3] = FLASH_DAC_4;
    
    IDAC8_1_Start();
    IDAC8_1_SetRange( IDAC8_1_RANGE_2mA );
    IDAC8_1_SetValue( DAC_IDLE_VALUE );

    IDAC8_2_Start();
    IDAC8_2_SetRange( IDAC8_2_RANGE_2mA );
    IDAC8_2_SetValue( DAC_IDLE_VALUE );

    IDAC8_3_Start();
    IDAC8_3_SetRange( IDAC8_3_RANGE_2mA );
    IDAC8_3_SetValue( DAC_IDLE_VALUE );

    IDAC8_4_Start();
    IDAC8_4_SetRange( IDAC8_4_RANGE_2mA );
    IDAC8_4_SetValue( DAC_IDLE_VALUE );

    
    init_dma_dac_1();
    init_dma_dac_2();
    init_dma_dac_3();
    init_dma_dac_4();
    isr_DAC_1_StartEx( isr_DAC_1_done );
    
}//END init_dacs(void)


void init_dma_dac_1(void){
    /* DMA Configuration for DMA_DAC_1 */
    const int bytes_per_td = DMA_DAC_1_WAVELET_LENGTH / DMA_DAC_1_NUM_OF_TDS;    
    
    DMA_DAC_1_Chan = DMA_DAC_1_DmaInitialize( DMA_DAC_1_BYTES_PER_BURST,
                                              DMA_DAC_1_REQUEST_PER_BURST, 
                                              HI16(DMA_DAC_1_SRC_BASE),
                                              HI16(DMA_DAC_1_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_DAC_1_NUM_OF_TDS; ++td_i)
        DMA_DAC_1_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_DAC_1_NUM_OF_TDS-1); ++td_i) {
        CyDmaTdSetConfiguration( DMA_DAC_1_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_DAC_1_TD[ td_i +1 ],
                                 ( (td_i == TDS_NUM_FOR_TRIGGER_OUT)
                                      * DMA_DAC_1__TD_TERMOUT_EN 
                                      | CY_DMA_TD_INC_SRC_ADR
                                   )
                                 );    
    }//END for(int td_i=0; td_i<(DMA_DAC_1_NUM_OF_TDS-1); ++td_i)
    CyDmaTdSetConfiguration( DMA_DAC_1_TD[ DMA_DAC_1_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             DMA_DAC_1__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR
                            );
    
    for(int td_i=0; td_i<DMA_DAC_1_NUM_OF_TDS; ++td_i)
        CyDmaTdSetAddress( DMA_DAC_1_TD[ td_i ],
                           LO16((uint32) FLASH_DAC_1 + (td_i * bytes_per_td) ),
                           LO16((uint32) IDAC8_1_Data_PTR)
                           );
}//END void init_dma_1(void)


void init_dma_dac_2(void){
    /* DMA Configuration for DMA_DAC_2 */
    const int bytes_per_td = DMA_DAC_2_WAVELET_LENGTH / DMA_DAC_2_NUM_OF_TDS;    
    
    DMA_DAC_2_Chan = DMA_DAC_2_DmaInitialize( DMA_DAC_2_BYTES_PER_BURST,
                                              DMA_DAC_2_REQUEST_PER_BURST, 
                                              HI16(DMA_DAC_2_SRC_BASE),
                                              HI16(DMA_DAC_2_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_DAC_2_NUM_OF_TDS; ++td_i)
        DMA_DAC_2_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_DAC_2_NUM_OF_TDS-1); ++td_i) {
        CyDmaTdSetConfiguration( DMA_DAC_2_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_DAC_2_TD[ td_i +1 ],
                                 ( (td_i == TDS_NUM_FOR_TRIGGER_OUT)
                                      * DMA_DAC_2__TD_TERMOUT_EN 
                                      | CY_DMA_TD_INC_SRC_ADR
                                   )
                                 );    
    }//END for(int td_i=0; td_i<(DMA_DAC_2_NUM_OF_TDS-1); ++td_i)
    CyDmaTdSetConfiguration( DMA_DAC_2_TD[ DMA_DAC_2_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             DMA_DAC_2__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR
                            );
    
    for(int td_i=0; td_i<DMA_DAC_2_NUM_OF_TDS; ++td_i)
        CyDmaTdSetAddress( DMA_DAC_2_TD[ td_i ],
                           LO16((uint32) FLASH_DAC_2 + (td_i * bytes_per_td) ),
                           LO16((uint32) IDAC8_2_Data_PTR)
                           );
}//END void init_dma_2(void)


void init_dma_dac_3(void){
    /* DMA Configuration for DMA_DAC_3 */
    const int bytes_per_td = DMA_DAC_3_WAVELET_LENGTH / DMA_DAC_3_NUM_OF_TDS;    
    
    DMA_DAC_3_Chan = DMA_DAC_3_DmaInitialize( DMA_DAC_3_BYTES_PER_BURST,
                                              DMA_DAC_3_REQUEST_PER_BURST, 
                                              HI16(DMA_DAC_3_SRC_BASE),
                                              HI16(DMA_DAC_3_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_DAC_3_NUM_OF_TDS; ++td_i)
        DMA_DAC_3_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_DAC_3_NUM_OF_TDS-1); ++td_i) {
        CyDmaTdSetConfiguration( DMA_DAC_3_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_DAC_3_TD[ td_i +1 ],
                                 ( (td_i == TDS_NUM_FOR_TRIGGER_OUT)
                                      * DMA_DAC_3__TD_TERMOUT_EN 
                                      | CY_DMA_TD_INC_SRC_ADR
                                   )
                                 );    
    }//END for(int td_i=0; td_i<(DMA_DAC_3_NUM_OF_TDS-1); ++td_i)
    CyDmaTdSetConfiguration( DMA_DAC_3_TD[ DMA_DAC_3_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             DMA_DAC_3__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR
                            );
    
    for(int td_i=0; td_i<DMA_DAC_3_NUM_OF_TDS; ++td_i)
        CyDmaTdSetAddress( DMA_DAC_3_TD[ td_i ],
                           LO16((uint32) FLASH_DAC_3 + (td_i * bytes_per_td) ),
                           LO16((uint32) IDAC8_3_Data_PTR)
                           );
}//END void init_dma_3(void)


void init_dma_dac_4(void){
    /* DMA Configuration for DMA_DAC_4 */
    const int bytes_per_td = DMA_DAC_4_WAVELET_LENGTH / DMA_DAC_4_NUM_OF_TDS;    
    
    DMA_DAC_4_Chan = DMA_DAC_4_DmaInitialize( DMA_DAC_4_BYTES_PER_BURST,
                                              DMA_DAC_4_REQUEST_PER_BURST, 
                                              HI16(DMA_DAC_4_SRC_BASE),
                                              HI16(DMA_DAC_4_DST_BASE)
                                              );
    
    for(int td_i=0; td_i<DMA_DAC_4_NUM_OF_TDS; ++td_i)
        DMA_DAC_4_TD[ td_i ] = CyDmaTdAllocate();
        
    for(int td_i=0; td_i<(DMA_DAC_4_NUM_OF_TDS-1); ++td_i) {
        CyDmaTdSetConfiguration( DMA_DAC_4_TD[ td_i ],
                                 bytes_per_td,
                                 DMA_DAC_4_TD[ td_i +1 ],
                                 ( (td_i == TDS_NUM_FOR_TRIGGER_OUT)
                                      * DMA_DAC_4__TD_TERMOUT_EN 
                                      | CY_DMA_TD_INC_SRC_ADR
                                   )
                                 );    
    }//END for(int td_i=0; td_i<(DMA_DAC_4_NUM_OF_TDS-1); ++td_i)
    CyDmaTdSetConfiguration( DMA_DAC_4_TD[ DMA_DAC_4_NUM_OF_TDS-1 ],
                             bytes_per_td,
                             CY_DMA_DISABLE_TD,
                             DMA_DAC_4__TD_TERMOUT_EN | CY_DMA_TD_INC_SRC_ADR
                            );
    
    for(int td_i=0; td_i<DMA_DAC_4_NUM_OF_TDS; ++td_i)
        CyDmaTdSetAddress( DMA_DAC_4_TD[ td_i ],
                           LO16((uint32) FLASH_DAC_4 + (td_i * bytes_per_td) ),
                           LO16((uint32) IDAC8_4_Data_PTR)
                           );
}//END void init_dma_4(void)


void start_dma_dac_1(void){
    CyDmaChSetInitialTd(DMA_DAC_1_Chan, DMA_DAC_1_TD[0]);
    CyDmaChEnable(DMA_DAC_1_Chan, 1);
}//END void start_dma_dac_1(void)


void start_dma_dac_2(void){
    CyDmaChSetInitialTd(DMA_DAC_2_Chan, DMA_DAC_2_TD[0]);
    CyDmaChEnable(DMA_DAC_2_Chan, 1);
}//END void start_dma_dac_2(void)


void start_dma_dac_3(void){
    CyDmaChSetInitialTd(DMA_DAC_3_Chan, DMA_DAC_3_TD[0]);
    CyDmaChEnable(DMA_DAC_3_Chan, 1);
}//END void start_dma_dac_3(void)


void start_dma_dac_4(void){
    CyDmaChSetInitialTd(DMA_DAC_4_Chan, DMA_DAC_4_TD[0]);
    CyDmaChEnable(DMA_DAC_4_Chan, 1);
}//END void start_dma_dac_4(void)


void create_wave(void){
    
    const int pts = DMA_DAC_1_WAVELET_LENGTH;
    for(int i=0; i < pts; ++i){
        sig_1.dac_data[i] = (uint8)(
                        (float) 127.5
                        * sin(2.0*M_PI/100 * (float)i*i/pts) + 127.5
                        );  
    }      
    sig_1.dac_data[ DMA_DAC_1_WAVELET_LENGTH-1 ] = DAC_IDLE_VALUE;

    FLASH_Write( sig_1.dac_data, FLASH_DAC_2, DMA_DAC_1_WAVELET_LENGTH); 
    
}//END create_wave(void)


void run_wave(void){
    
    Clock_1_Stop();
    start_dma_dac_1();
    start_dma_dac_2();
    start_dma_dac_3();
    start_dma_dac_4();
    Clock_1_Start();   
    
}//END run_wave(void)


CY_ISR( isr_DAC_1_done ){
    ++dma_dac_1_run_count;
}//endCY_ISR DAC_1

/* [] END OF FILE */
