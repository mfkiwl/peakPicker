#include "peakPicker.hpp"

void peakPicker(
    hls::stream<DataType>& xcorrStream,
    hls::stream<ThresholdType>& thresholdStream,
    const unsigned int signalLength,
    const unsigned int windowLength,
    hls::stream<LocationType>& peakLocStream,
    hls::stream<CountType>& peakCountStream
) {
    #pragma HLS INTERFACE axis port=xcorrStream
    #pragma HLS INTERFACE axis port=thresholdStream
    #pragma HLS INTERFACE axis port=peakLocStream
    #pragma HLS INTERFACE axis port=peakCountStream
    #pragma HLS INTERFACE s_axilite port=signalLength bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=windowLength bundle=CTRL
    #pragma HLS INTERFACE s_axilite port=return bundle=CTRL
    
    // Validate inputs
    assert(windowLength <= MAX_WINDOW_LENGTH && "Window length exceeds maximum allowed");
    assert(signalLength <= MAX_SIGNAL_LENGTH && "Signal length exceeds maximum allowed");
    assert((windowLength % 2) == 1 && "Window length must be odd");
    
    // Calculate middle position
    const unsigned int middleLocation = windowLength / 2;
    
    // Sliding window buffer for xcorr values
    DataType xcorrBuffer[MAX_WINDOW_LENGTH];
    #pragma HLS ARRAY_PARTITION variable=xcorrBuffer complete dim=1
    
    // Sliding window buffer for threshold values
    ThresholdType thresholdBuffer[MAX_WINDOW_LENGTH];
    #pragma HLS ARRAY_PARTITION variable=thresholdBuffer complete dim=1
    
    // Initialize buffers
    init_buffers:
    for (unsigned int i = 0; i < windowLength; i++) {
        #pragma HLS PIPELINE II=1
        xcorrBuffer[i] = 0;
        thresholdBuffer[i] = 0;
    }
    
    // Peak counter
    CountType peakCount = 0;
    
    // Process input signal
    process_signal:
    for (unsigned int index = 0; index < signalLength; index++) {
        #pragma HLS PIPELINE II=1
        
        // Shift values in the buffer
        shift_buffer:
        for (unsigned int i = windowLength - 1; i > 0; i--) {
            #pragma HLS UNROLL
            xcorrBuffer[i] = xcorrBuffer[i-1];
            thresholdBuffer[i] = thresholdBuffer[i-1];
        }
        
        // Add new samples to the buffers
        xcorrBuffer[0] = xcorrStream.read();
        thresholdBuffer[0] = thresholdStream.read();
        
        // Process only when we have a full window
        if (index >= windowLength - 1) {
            const unsigned int candidateLocation = index - middleLocation;
            const DataType middleSample = xcorrBuffer[middleLocation];
            const ThresholdType currentThreshold = thresholdBuffer[middleLocation];
            
            // Check if middle sample exceeds threshold
            bool exceedsThreshold = (middleSample > currentThreshold);
            
            // Check if middle sample is local maximum
            bool isLocalMax = true;
            check_local_max:
            for (unsigned int i = 0; i < windowLength; i++) {
                #pragma HLS UNROLL
                if (i != middleLocation && xcorrBuffer[i] > middleSample) {
                    isLocalMax = false;
                }
            }
            
            // If both conditions are met, we have a peak
            if (isLocalMax && exceedsThreshold && peakCount < MAX_PEAKS) {
                peakLocStream.write(candidateLocation+1); // +1 for 1-based index
                peakCount++;
            }
        }
    }
    
    // Write peak count to output stream
    peakCountStream.write(peakCount);
}
