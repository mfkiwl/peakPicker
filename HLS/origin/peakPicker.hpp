#ifndef PEAK_PICKER_HPP
#define PEAK_PICKER_HPP

#include "ap_fixed.h"
#include "hls_stream.h"
#include <vector>

// Fixed-point type definitions for PSS correlation magnitude squared values
// #define DATA_WIDTH 20   // Total bit width
// #define INT_WIDTH 1    // Integer bit width
typedef ap_fixed<20, 1> DataType;

// Maximum supported parameters
#define MAX_XCORR_LENGTH 10000   // Maximum length of input signal
#define MAX_WINDOW_LENGTH 31     // Maximum window size
#define MAX_SEQ_NUMBER 8         // Maximum number of sequences
#define MAX_LOCATIONS 1000       // Maximum number of peak locations to return

// Function declaration for the peak picker
void peakPicker(
    const DataType xcorr[MAX_XCORR_LENGTH][MAX_SEQ_NUMBER],  // Input PSS correlation magnitude squared values
    const DataType threshold[MAX_XCORR_LENGTH],              // Threshold values
    int xcorrLength,                                         // Length of input signal
    int seqCount,                                            // Number of sequences
    int windowLength,                                        // Window length for peak detection
    int locations[MAX_LOCATIONS],                            // Output peak locations
    int &numLocations                                        // Number of detected peaks
);

#endif // PEAK_PICKER_HPP
