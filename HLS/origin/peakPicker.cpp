#include "peakPicker.hpp"

void peakPicker(
    const DataType xcorr[MAX_XCORR_LENGTH][MAX_SEQ_NUMBER],
    const DataType threshold[MAX_XCORR_LENGTH],
    int xcorrLength,
    int seqCount,
    int windowLength,
    int locations[MAX_LOCATIONS],
    int &numLocations
) {
    // Interface pragmas
    #pragma HLS INTERFACE s_axilite port=return bundle=CONTROL_BUS
    #pragma HLS INTERFACE s_axilite port=numLocations bundle=CONTROL_BUS
    #pragma HLS INTERFACE s_axilite port=xcorrLength bundle=CONTROL_BUS
    #pragma HLS INTERFACE s_axilite port=seqCount bundle=CONTROL_BUS
    #pragma HLS INTERFACE s_axilite port=windowLength bundle=CONTROL_BUS
    
    // Memory interface pragmas
    #pragma HLS INTERFACE m_axi port=xcorr offset=slave depth=MAX_XCORR_LENGTH*MAX_SEQ_NUMBER
    #pragma HLS INTERFACE m_axi port=threshold offset=slave depth=MAX_XCORR_LENGTH
    #pragma HLS INTERFACE m_axi port=locations offset=slave depth=MAX_LOCATIONS
    
    // Memory optimization pragmas
    #pragma HLS ARRAY_PARTITION variable=xcorr dim=2 complete
    
    // Calculate middle index of window (equivalent to floor(window_length/2) in MATLAB)
    const int middleLocation = windowLength / 2;
    
    // Initialize location counter
    numLocations = 0;
    
    // Main processing loop - slide window through xcorr
    SLIDE_WINDOW:
    for (int index = 0; index <= xcorrLength - windowLength; index++) {
        #pragma HLS PIPELINE II=1
        
        // Calculate candidate peak location (center of current window)
        int candidateLocation = index + middleLocation;
        
        // Check if any sequence at candidate location exceeds threshold
        bool thresholdExceeded = false;
        int validSeqCount = 0;
        int validSeqIndices[MAX_SEQ_NUMBER];
        
        THRESHOLD_CHECK:
        for (int seq = 0; seq < seqCount; seq++) {
            if (xcorr[candidateLocation][seq] >= threshold[candidateLocation]) {
                thresholdExceeded = true;
                validSeqIndices[validSeqCount] = seq;
                validSeqCount++;
            }
        }
        
        // If threshold is exceeded, check if candidate is maximum in window
        if (thresholdExceeded) {
            int maxCheckCount = 0;
            
            VALID_SEQ_LOOP:
            for (int v = 0; v < validSeqCount; v++) {
                int seq = validSeqIndices[v];
                bool isMax = true;
                
                WINDOW_CHECK:
                for (int w = 0; w < windowLength; w++) {
                    #pragma HLS PIPELINE II=1
                    if (xcorr[candidateLocation][seq] < xcorr[index + w][seq]) {
                        isMax = false;
                        break;
                    }
                }
                
                if (isMax) {
                    maxCheckCount++;
                }
            }
            
            // If candidate is maximum in window for all valid sequences, add to peak locations
            if (maxCheckCount == validSeqCount) {
                locations[numLocations] = candidateLocation+1; // Store peak location (1-based index)
                numLocations++;
                
                // Prevent buffer overflow
                if (numLocations >= MAX_LOCATIONS) {
                    break;
                }
            }
        }
    }
}
