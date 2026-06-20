module clock_div #(parameter DIV_MAX = 50_000_000)(
    input logic clk, reset,
    output logic clk_1hz_en
);
    logic [25:0] count_reg;
    always_ff @(posedge clk or posedge reset) begin
        if (reset) begin count_reg <= '0; clk_1hz_en <= 1'b0; end
        else if (count_reg == (DIV_MAX - 1)) begin count_reg <= '0; clk_1hz_en <= 1'b1; end
        else begin count_reg <= count_reg + 1'b1; clk_1hz_en <= 1'b0; end
    end
endmodule

module time_counters (
    input logic clk, reset, clk_1hz_en,
    output logic [3:0] s_ones, s_tens, m_ones, m_tens, h_ones, h_tens
);
    logic [5:0] sec_count, min_count; logic [4:0] hr_count;
    always_ff @(posedge clk or posedge reset) begin
        if (reset) begin sec_count <= '0; min_count <= '0; hr_count <= '0; end
        else if (clk_1hz_en) begin
            if (sec_count == 59) begin
                sec_count <= '0;
                if (min_count == 59) begin min_count <= '0;
                    if (hr_count == 23) hr_count <= '0;
                    else hr_count <= hr_count + 1'b1;
                end else min_count <= min_count + 1'b1;
            end else sec_count <= sec_count + 1'b1;
        end
    end
    assign s_ones = sec_count % 10; assign s_tens = sec_count / 10;
    assign m_ones = min_count % 10; assign m_tens = min_count / 10;
    assign h_ones = hr_count  % 10; assign h_tens = hr_count  / 10;
endmodule

module alarm_comp (
    input logic [3:0] h_ones, h_tens, m_ones, m_tens,
    input logic [4:0] alarm_hour, input logic [5:0] alarm_minute, input logic alarm_en,
    output logic alarm_out
);
    logic [4:0] current_hour; logic [5:0] current_minute;
    assign current_hour = (h_tens * 10) + h_ones;
    assign current_minute = (m_tens * 10) + m_ones;
    always_comb begin
        if (alarm_en && (current_hour == alarm_hour) && (current_minute == alarm_minute)) alarm_out = 1'b1;
        else alarm_out = 1'b0;
    end
endmodule

module digital_clock_top (
    input logic clk, reset, alarm_en,
    input logic [4:0] alarm_hour, input logic [5:0] alarm_minute,
    output logic [3:0] s_ones, s_tens, output logic alarm_out
);
    logic clk_1hz_pulse; logic [3:0] h_ones, h_tens, m_ones, m_tens;
    clock_div #(.DIV_MAX(50_000_000)) u_div (.clk(clk), .reset(reset), .clk_1hz_en(clk_1hz_pulse));
    time_counters u_counters (.clk(clk), .reset(reset), .clk_1hz_en(clk_1hz_pulse), .s_ones(s_ones), .s_tens(s_tens), .m_ones(m_ones), .m_tens(m_tens), .h_ones(h_ones), .h_tens(h_tens));
    alarm_comp u_alarm (.h_ones(h_ones), .h_tens(h_tens), .m_ones(m_ones), .m_tens(m_tens), .alarm_hour(alarm_hour), .alarm_minute(alarm_minute), .alarm_en(alarm_en), .alarm_out(alarm_out));
endmodule