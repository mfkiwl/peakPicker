#ifndef PEAK_PICKER_HPP
#define PEAK_PICKER_HPP

#include <ap_fixed.h>
#include <hls_stream.h>
#include <stdint.h>
#include <vector>

// Define constants
#define MAX_SIGNAL_LENGTH 8192      // Maximum signal length
#define MAX_WINDOW_LENGTH 15        // Maximum window length
#define MAX_PEAKS 100               // Maximum number of peaks to detect

// Fixed-point data type definitions
// 32-bit fixed point with 16-bit integer part
typedef ap_fixed<20, 1> DataType;
typedef ap_uint<16> LocationType;

// Peak picker function declaration
void peakPicker(
    hls::stream<DataType>& xcorrStream,  // Input correlation data stream
    hls::stream<DataType>& thresholdStream, // Input threshold values stream
    hls::stream<LocationType>& locationsStream, // Output peak locations stream
    uint16_t signalLength,                // Length of input signal
    uint16_t windowLength,                // Length of sliding window
    uint16_t& numPeaks                    // Number of peaks found
);

#endif // PEAK_PICKER_HPP
