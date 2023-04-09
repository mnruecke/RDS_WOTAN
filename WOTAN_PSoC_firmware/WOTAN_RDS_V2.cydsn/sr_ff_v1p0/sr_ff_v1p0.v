
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
// Generated on 04/09/2023 at 21:23
// Component: sr_ff_v1p0
module sr_ff_v1p0 (
	output  reg q,
	input   reset,
	input   set
);

//`#start body` -- edit after this line, do not edit this line

always @ (posedge reset or posedge set )
begin
    if( reset == 1'b1 )
        q <= 1'b0;
    else
        q <= 1'b1;
end

//        Your code goes here

//`#end` -- edit above this line, do not edit this line
endmodule
//`#start footer` -- edit after this line, do not edit this line
//`#end` -- edit above this line, do not edit this line
