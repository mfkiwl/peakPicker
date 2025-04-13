#include "peakPicker.hpp"

void peakPicker(
    DataStream &xcorrStream,
    DataStream &thresholdStream,
    LocationStream &locationsStream,
    int signalLength
) {
    #pragma HLS INTERFACE mode=axis port=xcorrStream
    #pragma HLS INTERFACE mode=axis port=thresholdStream
    #pragma HLS INTERFACE mode=axis port=locationsStream
    #pragma HLS INTERFACE mode=s_axilite port=signalLength
    #pragma HLS INTERFACE mode=s_axilite port=return

    // Sliding window buffer for correlation values
    DataType xcorrBuffer[WINDOW_LENGTH];
    #pragma HLS ARRAY_PARTITION variable=xcorrBuffer complete
    
    // Sliding window buffer for threshold values
    DataType thresholdBuffer[WINDOW_LENGTH];
    #pragma HLS ARRAY_PARTITION variable=thresholdBuffer complete

    // Initialize buffers
    init_buffers:
    for (int i = 0; i < WINDOW_LENGTH; i++) {
        #pragma HLS UNROLL
        xcorrBuffer[i] = 0;
        thresholdBuffer[i] = 0;
    }

    // Process the input signal
    process_signal:
    for (int index = 0; index < signalLength; index++) {
        #pragma HLS PIPELINE II=1
        
        // Shift the buffers
        shift_buffers:
        for (int i = WINDOW_LENGTH-1; i > 0; i--) {
            #pragma HLS UNROLL
            xcorrBuffer[i] = xcorrBuffer[i-1];
            thresholdBuffer[i] = thresholdBuffer[i-1];
        }
        
        // Read new samples if available
        if (!xcorrStream.empty() && !thresholdStream.empty()) {
            xcorrBuffer[0] = xcorrStream.read();
            thresholdBuffer[0] = thresholdStream.read();
        }
        
        // Check for peaks when the buffer is filled
        if (index >= WINDOW_LENGTH - 1) {
            DataType midSample = xcorrBuffer[MIDDLE_LOCATION];
            bool isPeak = true;
            
            // Compare middle sample with all other samples in window
            compare_samples:
            for (int i = 0; i < WINDOW_LENGTH; i++) {
                #pragma HLS UNROLL
                if (i != MIDDLE_LOCATION && xcorrBuffer[i] > midSample) {
                    isPeak = false;
                }
            }
            
            // Check if middle sample is greater than threshold
            if (isPeak && midSample > thresholdBuffer[MIDDLE_LOCATION]) {
                LocationType peakLocation = index - MIDDLE_LOCATION;
                locationsStream.write(peakLocation+1); // +1 to convert to 1-based index
            }
        }
    }
}
