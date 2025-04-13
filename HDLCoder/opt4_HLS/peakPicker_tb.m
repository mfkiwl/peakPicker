% This is the testbench for the peakPicker function.
% It reads the input signal from a file, calls the peakPicker function,
% and writes the output to a file.
%
% Author: Jie Lei
% Date: 03/30/2025
%
% Read the input cross correlation from a file.
xcorr = readmatrix('pssCorrMagSq_3_in.txt','Delimiter', 'tab');
% Read the threshold from a file.
threshold = readmatrix('threshold_in.txt','Delimiter', 'tab');
% Set the window length for the peak picker.
% This is the length of the window used to find the peaks.
% The window length should be an odd number.
windowLength = 11;
idx = 1;
% Read the reference output from a file.
refLocs = readmatrix('locations_3_ref.txt','Delimiter', 'tab');
peakLocs = zeros(length(refLocs), 1); % Preallocate the peak locations array
% Call the peakPicker function.
for i = 1:length(xcorr)
    % Call the peakPicker function for each sample in the cross correlation.
    [loc, valid] = peakPicker(xcorr(i), threshold(i));
    % Store the location of the peak if valid.
    if valid
        peakLocs(idx) = loc;
        idx = idx + 1;
    end
end
% Write the output to a file.
writematrix(peakLocs, 'peakLocs_out.txt','Delimiter', 'tab');
% Compare the output with the reference output.
if isequal(peakLocs(1:length(refLocs)), refLocs)
    disp('Test passed: The output matches the reference output.');
else
    disp('Test failed: The output does not match the reference output.');
end