**rockyco**: Revise this MATLAB code to visualize `xcorr` and `threshold` data sequence on a plot, and mark peak location `peakLocs` on it. Additionally, plot a zoomed in region centered by the peak location.

**GitHub Copilot**: # Solution for Visualizing Peak Detection

I'll revise the MATLAB code to add visualization of the cross-correlation, threshold, and peak locations, including a zoomed view around the peak locations.

## Step-by-step approach:
1. Keep all the existing code for input reading, peak detection, and output comparison
2. Add a new visualization section that:
   - Creates a figure with two subplots
   - First subplot: plots the full xcorr data with threshold and marked peaks
   - Second subplot: shows a zoomed region around the significant peak(s)

### [peakPicker_tb.m](file:///home/jielei/Projects/UTS/peakPicker/MATLAB/origin/peakPicker_tb.m)

Add visualization code to display the cross-correlation, threshold, and peak locations.

````matlab
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
% Call the peakPicker function.
[peakLocs] = peakPicker(xcorr, threshold, windowLength);
% Write the output to a file.
writematrix(peakLocs, 'peakLocs_out.txt','Delimiter', 'tab');
% Read the reference output from a file.
refLocs = readmatrix('locations_3_ref.txt','Delimiter', 'tab');
% Compare the output with the reference output.
if isequal(peakLocs, refLocs)
    disp('Test passed: The output matches the reference output.');
else
    disp('Test failed: The output does not match the reference output.');
end

% Visualization of the cross-correlation, threshold, and peak locations
figure('Name', 'Peak Detection Results');

% First subplot: Full view of data
subplot(2, 1, 1);
plot(xcorr, 'b-', 'LineWidth', 1.5);
hold on;
% Plot threshold (handles both scalar and vector thresholds)
if numel(threshold) == 1
    yline(threshold, 'r--', 'LineWidth', 1.5);
else
    plot(threshold, 'r--', 'LineWidth', 1.5);
end
% Mark peak locations
if ~isempty(peakLocs)
    for i = 1:length(peakLocs)
        plot(peakLocs(i), xcorr(peakLocs(i)), 'go', 'MarkerSize', 10, 'LineWidth', 2);
    end
end
grid on;
title('Cross-Correlation with Detected Peaks');
xlabel('Sample Index');
ylabel('Magnitude');
legend('Cross-Correlation', 'Threshold', 'Detected Peaks');

% Second subplot: Zoomed view around peak(s)
subplot(2, 1, 2);
if isempty(peakLocs)
    text(0.5, 0.5, 'No peaks detected', 'HorizontalAlignment', 'center', 'FontSize', 14);
    axis off;
else
    % Find the peak with highest value for zooming
    [~, maxPeakIdx] = max(xcorr(peakLocs));
    peakLoc = peakLocs(maxPeakIdx);
    
    % Define zoom window
    zoomRadius = min(20, floor(length(xcorr)/10));
    zoomStart = max(1, peakLoc - zoomRadius);
    zoomEnd = min(length(xcorr), peakLoc + zoomRadius);
    
    % Plot zoomed view
    plot(zoomStart:zoomEnd, xcorr(zoomStart:zoomEnd), 'b-', 'LineWidth', 1.5);
    hold on;
    if numel(threshold) == 1
        yline(threshold, 'r--', 'LineWidth', 1.5);
    else
        plot(zoomStart:zoomEnd, threshold(zoomStart:zoomEnd), 'r--', 'LineWidth', 1.5);
    end
    
    % Mark the peak in the zoomed view
    plot(peakLoc, xcorr(peakLoc), 'go', 'MarkerSize', 10, 'LineWidth', 2);
    
    grid on;
    title('Zoomed View Around Highest Peak');
    xlabel('Sample Index');
    ylabel('Magnitude');
    legend('Cross-Correlation', 'Threshold', 'Peak');
end

% Overall title
sgtitle('Peak Detection Analysis');
````

rockyco: Revise this MATLAB code. Use dot mark to show each value of `xcorr` data on the zoomed plot.

GitHub Copilot: ## Solution for Adding Dot Markers to the Zoomed Plot

I'll modify the code to display dot markers for each value of the `xcorr` data in the zoomed plot, making individual data points more visible.

### [peakPicker_tb.m](file:///home/jielei/Projects/UTS/peakPicker/MATLAB/origin/peakPicker_tb.m)

Change the zoomed plot style to include dot markers for each data point by modifying the plot format specifier.

````matlab
// ...existing code...
    % Plot zoomed view
    plot(zoomStart:zoomEnd, xcorr(zoomStart:zoomEnd), 'b.-', 'LineWidth', 1.5);
// ...existing code...
````

The change from `'b-'` to `'b.-'` adds a dot marker at each data point while maintaining the blue line connecting them, making individual data values clearly visible in the zoomed view.


rockyco: Revise this MATLAB code to use bigger dot mark on the zoomed plot.

GitHub Copilot: Looking at the code, I need to modify the zoomed plot to use bigger dot markers. The current plot uses 'b.-' format but doesn't specify a marker size.

### [peakPicker_tb.m](file:///home/jielei/Projects/UTS/peakPicker/MATLAB/origin/peakPicker_tb.m)

Add a MarkerSize parameter to the zoomed plot to make the dots bigger:

````matlab
// ...existing code...
    % Plot zoomed view
    plot(zoomStart:zoomEnd, xcorr(zoomStart:zoomEnd), 'b.-', 'LineWidth', 1.5, 'MarkerSize', 8);
    hold on;
// ...existing code...
````

This change adds the 'MarkerSize' parameter with a value of 8 to the zoomed plot, making the dots significantly larger and more visible than the default size.

