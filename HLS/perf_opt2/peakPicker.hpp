#ifndef PEAK_PICKER_H
#define PEAK_PICKER_H

#include <ap_fixed.h>
#include <hls_stream.h>
#include <ap_int.h>
#include <cassert>

// Define constants
#define MAX_WINDOW_LENGTH 11
#define MAX_PEAKS 100
#define MAX_SIGNAL_LENGTH 8192

// Fixed-point type definitions
// Note: Bit-widths should be adjusted based on precision requirements
typedef ap_fixed<20, 1> DataType;           // For PSS correlation magnitude squared values
typedef ap_fixed<20, 1> ThresholdType;      // For threshold values
typedef ap_uint<16> LocationType;            // For peak location indices
typedef ap_uint<8> CountType;                // For counting peaks

// Function declaration
void peakPicker(
    hls::stream<DataType>& xcorrStream,      // Input: PSS correlation magnitude squared values
    hls::stream<ThresholdType>& thresholdStream, // Input: Threshold values
    const unsigned int signalLength,         // Length of the input signal
    const unsigned int windowLength,         // Length of the sliding window
    hls::stream<LocationType>& peakLocStream, // Output: Peak locations
    hls::stream<CountType>& peakCountStream  // Output: Number of peaks found
);

#endif // PEAK_PICKER_H
