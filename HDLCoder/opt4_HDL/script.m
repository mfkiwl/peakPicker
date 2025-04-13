% Set up HDL Simulator and Synthesis Tool Path
hdlsetuptoolpath('ToolName', 'Xilinx Vivado', ...
    'ToolPath', '/opt/Xilinx/Vivado/2023.2/bin/vivado');

% Create an HDL Coder Project
coder -hdlcoder -new peakPicker_project

% Open the project
% coder -open peakPicker_project
