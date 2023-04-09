
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
// Generated on 04/09/2023 at 22:37
// Component: adda_clock_tree_v1p0
module adda_clock_tree_v1p0 (
	output  clk1,
	output  clk2,
	output  clk3,
	output  clk4,
	output  clk5,
	output  clk6,
	input   clk,
	input   rst
);

//`#start body` -- edit after this line, do not edit this line

//        Your code goes here
parameter  WIDTH = 6;
parameter [WIDTH-1:0] RESET_VALUE         = 6'b000_111;
parameter [WIDTH-1:0] POWER_CYCLE_VALUE   = 6'b000_000;

reg [WIDTH-1:0] shift_reg;

always @ ( posedge clk or posedge rst )
begin
    if( rst == 1'b1 )
    begin
        shift_reg <= RESET_VALUE;
    end
    else if( shift_reg == POWER_CYCLE_VALUE )
    begin
        shift_reg <= RESET_VALUE;
    end
    else
    begin
        shift_reg <= { shift_reg[WIDTH-2:0], shift_reg[WIDTH-1] };
    end
end

assign clk1 = shift_reg[0];
assign clk2 = shift_reg[1];
assign clk3 = shift_reg[2];
assign clk4 = shift_reg[3];
assign clk5 = shift_reg[4];
assign clk6 = shift_reg[5];

//`#end` -- edit above this line, do not edit this line
endmodule
//`#start footer` -- edit after this line, do not edit this line
//`#end` -- edit above this line, do not edit this line
