
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
// Generated on 09/26/2020 at 19:40
// Component: bus_combinator
module bus_combinator (
	output [7:0] en_leds_inv,
	input   en_leds
);

//`#start body` -- edit after this line, do not edit this line

//        Your code goes here
assign en_leds_inv = en_leds ? 8'b00000000 : 8'b11111111;

//`#end` -- edit above this line, do not edit this line
endmodule
//`#start footer` -- edit after this line, do not edit this line
//`#end` -- edit above this line, do not edit this line
