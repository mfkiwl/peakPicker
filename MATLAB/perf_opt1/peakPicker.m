function [locations]= peakPicker(xcorr,threshold,window_length)
% Copyright 2021-2023 The MathWorks, Inc.

    locations=[];
    middle_location=floor(window_length/2);
    
    % writeptr=1;
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
        % writeptr=writeptr+1;
    end
end


% Hardware friendly implementation of peak finder
%
% Function inputs:
% * WindowLen - non-tunable parameter defined under Simulink->Edit Data
% * threhold  - input port (connected to constant)
% * DataBuff  - input port (buffering done using Simulink block)
%
% Function outputs:
% * "detected" is set when MidSample is local max

% function [MidSample,detected] = fcn(WindowLen, threshold, DataBuff)
%     %#codegen
    
    
%     MidIdx = ceil(WindowLen/2);
    
%     % Compare each value in the window to the middle sample via subtraction
%     MidSample = DataBuff(MidIdx);
%     CompareOut = DataBuff - MidSample; % this is a vector
    
%     % if all values in the result are negative and the middle sample is
%     % greater than a threshold, it is a local max
%     if all(CompareOut <= 0) && (MidSample > threshold)
%         detected = true;
%     else
%         detected = false;
%     end
% end    