% Set up HDL Simulator and Synthesis Tool Path
hdlsetuptoolpath('ToolName', 'Xilinx Vivado', ...
    'ToolPath', '/opt/Xilinx/Vivado/2023.2/bin/vivado');

% Set up HLS tool path
hdlsetuphlstoolpath("ToolName","Xilinx Vitis HLS","ToolPath","/opt/Xilinx/Vitis_HLS/2023.2/bin");

% Create an HDL Coder Project
coder -hdlcoder -new peakPicker_project

