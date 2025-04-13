#include "peakPicker.hpp"

void peakPicker(
    hls::stream<DataType>& xcorrStream,
    hls::stream<DataType>& thresholdStream,
    hls::stream<LocationType>& locationsStream,
    uint16_t signalLength,
    uint16_t windowLength,
    uint16_t& numPeaks
) {
    #pragma HLS INTERFACE mode=axis port=xcorrStream
    #pragma HLS INTERFACE mode=axis port=thresholdStream
    #pragma HLS INTERFACE mode=axis port=locationsStream
    #pragma HLS INTERFACE mode=s_axilite port=signalLength bundle=control
    #pragma HLS INTERFACE mode=s_axilite port=windowLength bundle=control
    #pragma HLS INTERFACE mode=s_axilite port=numPeaks bundle=control
    #pragma HLS INTERFACE mode=s_axilite port=return bundle=control

    // Buffer for input data
    DataType xcorr[MAX_SIGNAL_LENGTH];
    #pragma HLS RESOURCE variable=xcorr core=RAM_2P_BRAM
    
    // Buffer for threshold data
    DataType threshold[MAX_SIGNAL_LENGTH];
    #pragma HLS RESOURCE variable=threshold core=RAM_2P_BRAM
    
    // Read input data from streams
    InputRead: for (uint16_t i = 0; i < signalLength; i++) {
        #pragma HLS PIPELINE II=1
        xcorr[i] = xcorrStream.read();
        threshold[i] = thresholdStream.read();
    }
    
    // Calculate middle location of the window
    uint16_t middleLocation = windowLength / 2;
    
    // Reset peak counter
    numPeaks = 0;
    
    // Process the signal to find peaks
    ProcessSignal: for (uint16_t index = 0; index < signalLength - windowLength + 1; index++) {
        #pragma HLS PIPELINE II=1
        
        // Get the candidate location (middle of current window)
        uint16_t candidateLocation = index + middleLocation;
        
        // Get the middle sample value
        DataType midSample = xcorr[candidateLocation];
        
        // Check if the middle sample is a local maximum
        bool isLocalMax = true;
        
        WindowCheck: for (uint16_t w = 0; w < windowLength; w++) {
            #pragma HLS UNROLL
            if (w != middleLocation) {
                DataType windowSample = xcorr[index + w];
                if (windowSample > midSample) {
                    isLocalMax = false;
                }
            }
        }
        
        // Check if the middle sample exceeds the threshold
        bool exceedsThreshold = (midSample > threshold[candidateLocation]);
        
        // If both conditions are met, we have a peak
        if (isLocalMax && exceedsThreshold && numPeaks < MAX_PEAKS) {
            locationsStream.write(candidateLocation+1); // +1 for 1-based index
            numPeaks++;
        }
    }
}
