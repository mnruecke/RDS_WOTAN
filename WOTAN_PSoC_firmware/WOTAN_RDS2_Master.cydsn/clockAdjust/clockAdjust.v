
//`#start header` -- edit after this line, do not edit this line
// ========================================
//
// Copyright YOUR COMPANY, THE YEAR
// All Rights Reserved
// UNPUBLISHED, LICENSED SOFTWARE.
//
// CONFIDENTIAL AND PROPRIETARY INFORMATION
// WHICH IS THE PROPERTY OF your company.
//
// ========================================
`include "cypress.v"
//`#end` -- edit above this line, do not edit this line
// Generated on 07/18/2018 at 18:42
// Component: clockAdjust
module clockAdjust (
	output  clk_out,
	input   clk_in
);
	parameter ACCU_WIDTH = 24;
	parameter ACCU_WORD = 1717987;

//`#start body` -- edit after this line, do not edit this line
reg [ACCU_WIDTH-1:0] cnt;

always @ (posedge clk_in)
begin
    cnt <= cnt + ACCU_WORD;   
end

assign clk_out = cnt[ACCU_WIDTH-1];


//`#end` -- edit above this line, do not edit this line
endmodule
//`#start footer` -- edit after this line, do not edit this line
//`#end` -- edit above this line, do not edit this line
