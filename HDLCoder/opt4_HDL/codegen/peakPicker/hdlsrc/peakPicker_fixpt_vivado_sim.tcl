create_project vivado_sim -force
source peakPicker_fixpt_tb_compile.tcl
add_files -fileset sim_1 -norecurse locations_expected.dat
add_files -fileset sim_1 -norecurse threshold.dat
add_files -fileset sim_1 -norecurse valid_expected.dat
add_files -fileset sim_1 -norecurse xcorr.dat
update_compile_order -fileset sim_1
source peakPicker_fixpt_tb_sim.tcl
