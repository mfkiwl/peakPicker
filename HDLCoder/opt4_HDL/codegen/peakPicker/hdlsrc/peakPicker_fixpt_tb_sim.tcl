launch_simulation
set_property -name {xsim.simulate.runtime} -value {} -objects [get_filesets sim_1]
run all
