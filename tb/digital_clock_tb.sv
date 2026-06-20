`timescale 1ns/1ps

module digital_clock_tb;
    logic clk; logic reset; logic alarm_en;
    logic [4:0] alarm_hour; logic [5:0] alarm_minute;
    logic [3:0] s_ones, s_tens; logic alarm_out;

    digital_clock_top uut (.*);

    // Speed up simulation time so we don't have to wait millions of years
    defparam uut.u_div.DIV_MAX = 4;

    always #10 clk = ~clk;

    initial begin
        $dumpfile("dump.vcd"); $dumpvars(0, digital_clock_tb);
        clk = 0; reset = 1; alarm_en = 0;
        alarm_hour = 5'd0; alarm_minute = 5'd1; #40;
        reset = 0; alarm_en = 1'b1;

        $display("[START SIMULATION LOGS]");
        $monitor("{ \"time_ns\": %0t, \"hour\": %d%d, \"minute\": %d%d, \"second\": %d%d, \"alarm\": %b }", 
                 $time, uut.h_tens, uut.h_ones, uut.m_tens, uut.m_ones, s_tens, s_ones, alarm_out);
        #5000;
        $display("[SIMULATION SUCCESSFUL TERMINATION]");
        $finish;
    end
endmodule
