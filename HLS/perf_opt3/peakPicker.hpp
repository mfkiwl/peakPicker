#ifndef PEAK_PICKER_HPP
#define PEAK_PICKER_HPP

#include "ap_fixed.h"
#include "hls_stream.h"
#include "hls_vector.h"
#include <ap_int.h>

// Define constants
constexpr int WINDOW_LENGTH = 11;
constexpr int MIDDLE_LOCATION = WINDOW_LENGTH / 2;
constexpr int MAX_PEAKS = 100; // Maximum number of peaks to detect

// Define fixed-point data types
// Assuming 32 bits total with 16 integer bits for magnitude squared values
typedef ap_fixed<20, 1> DataType;
typedef ap_uint<16> LocationType;
typedef hls::stream<DataType> DataStream;
typedef hls::stream<LocationType> LocationStream;

// Main function declaration
void peakPicker(
    DataStream &xcorrStream,      // Input stream of PSS correlation magnitude squared values
    DataStream &thresholdStream,  // Input stream of threshold values
    LocationStream &locationsStream, // Output stream of peak locations
    int signalLength              // Length of the input signal
);

#endif // PEAK_PICKER_HPP
