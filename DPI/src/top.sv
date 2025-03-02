module top

import "DPI-C" pure function int func_fmul_c(input int a, input int b);

reg clk;
initial begin
	clk = 1'b0;
	forever begin
		#1 clk <= ~clk;
	end
end

string file;
string line;
int data;
int num_of_examples;
int c_res;

wire [31:0] v_res;
reg [1:0] opc;
wire val;

initial begin

	if ($value$plusargs("num1=%x", num1) and $value$plusargs("num2=%x", num2)) begin
		calc();
	end
	else if ($value$plusargs("file=%s", file)) begin
		data = $fopen(file, "r");
		while ($fgets(line, data)) 	begin
			$sscanf(line, "%x %x", num1, num2);
			calc();
		end
	end
	else if ($value$plusargs("random_mode=%d", num_of_examples)) begin
		for (int i = 0; i < num_of_examples; i++)
		begin
			num1 = $urandom();
			num2 = $urandom();
			calc();
		end
	end

	opc <= 2'b00; #10

	$display("Try v_mul %x x %x", num1, num2);
	$display("Res %x", v_res);
	$display("Val %x", val);
	$display("");
	opc <= 2'b01; #10

	$display("Try v_mul %x x %x", num1, num2);
	$display("Res %x", v_res);
	$display("Val %x", val);
	$display("");
	opc <= 2'b10; #10

	$display("Try v_mul %x x %x", num1, num2);
	$display("Res %x", v_res);
	$display("Val %x", val);
	$display("");
	opc <= 2'b11; #10

	$display("Try v_mul %x x %x", num1, num2);
	$display("Res %x", v_res);
	$display("Val %x", val);
	$display("");

	$finish;
end

task calc();
    $display("Calculate %x x %x", num1, num2);

    c_res = func_fmul_c(num1, num2);

endtask

FMUL32 v_FMUL (
	clk(clk),
	op1(num1),
	op2(num2),
	opc(opc),
	r_mode(2'b0),
	result(v_res),
	val(val)
);



endmodule