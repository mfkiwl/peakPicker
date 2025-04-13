open_project vitis_prj
set_top peakPicker_fixpt_wrapper
add_files peakPicker_fixptClass.hpp
add_files rtwtypes.hpp
add_files peakPicker_fixpt_wrapper.cpp -cflags "-I/home/jielei/Projects/UTS/peakPicker/HDLCoder/optim2/codegen/peakPicker/hdlsrc -I/home/jielei/Projects/UTS/peakPicker/HDLCoder/optim2 "
add_files -tb peakPicker_fixptClass_tb.hpp
add_files -tb peakPicker_fixpt_main.cpp -cflags "-I/home/jielei/Projects/UTS/peakPicker/HDLCoder/optim2/codegen/peakPicker/hdlsrc -I/home/jielei/Projects/UTS/peakPicker/HDLCoder/optim2 "
add_files -tb locations_expected.dat
add_files -tb threshold.dat
add_files -tb valid_expected.dat
add_files -tb xcorr.dat
open_solution "solution1" -flow_target vitis
set_part xc7k410tfbg900-2
create_clock -period 200MHz -name default
csynth_design
cosim_design -ldflags ""
export_design -flow impl
close_project
