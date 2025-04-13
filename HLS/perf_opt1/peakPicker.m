% Implementation of a hardware-friendly peak detection algorithm
% Computing CompareOut = current_window - MidSample
% Using all(CompareOut <= 0) to check if the middle sample is a local maximum
% Simplified conditional logic
% Modified by Jie Lei, University of Technology Sydney, 2025

function [locations]= peakPicker(xcorr,threshold,window_length)
% Copyright 2021-2023 The MathWorks, Inc.

    locations=[];
    middle_location=floor(window_length/2);
    
    for index=1:length(xcorr)-window_length+1
        current_window=xcorr(index:index+window_length-1,:); % sliding window
        candidate_location=index+middle_location;
        % Hardware friendly implementation of peak finder
        MidSample = current_window(middle_location+1,:);
        CompareOut = current_window - MidSample; % this is a vector
        % if all values in the result are negative and the middle sample is
        % greater than a threshold, it is a local max
        if all(CompareOut <= 0) && (MidSample > threshold(candidate_location))
            locations = [locations candidate_location]; %#ok
        end
    end
end