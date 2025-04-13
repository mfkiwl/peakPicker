rockyco: Follow the instuctions in the MD file to generate an efficient HLS C++ design and its testbench.

GitHub Copilot: # Solution: HLS C++ Implementation of Peak Picker Algorithm

I'll create a complete HLS C++ implementation of the peak picker algorithm based on the provided MATLAB reference code. The implementation will follow the requirements specified in the instructions.

## Step-by-Step Approach:

1. Create a header file with type definitions, constants, and function declarations
2. Implement the core algorithm in the C++ file using HLS directives for optimization
3. Develop a testbench to validate against reference data

Let's go through each file:

### [peakPicker.hpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim2/peakPicker.hpp)

This header file defines all the necessary types, constants, and function declarations.

````cpp
#ifndef PEAK_PICKER_H
#define PEAK_PICKER_H

#include <ap_fixed.h>
#include <hls_stream.h>
#include <ap_int.h>
#include <cassert>

// Define constants
#define MAX_WINDOW_LENGTH 32
#define MAX_PEAKS 100
#define MAX_SIGNAL_LENGTH 4096

// Fixed-point type definitions
// Note: Bit-widths should be adjusted based on precision requirements
typedef ap_fixed<32, 16> DataType;           // For PSS correlation magnitude squared values
typedef ap_fixed<32, 16> ThresholdType;      // For threshold values
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
````

### [peakPicker.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim2/peakPicker.cpp)

This implementation file contains the core peak picker algorithm with HLS optimization directives.

````cpp


Made changes.

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
                peakLocStream.write(candidateLocation);
                peakCount++;
            }
        }
    }
    
    // Write peak count to output stream
    peakCountStream.write(peakCount);
}
````

### [peakPicker_tb.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim2/peakPicker_tb.cpp)

This testbench file reads input data, runs the algorithm, and validates against reference data.

````cpp


Made changes.

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cmath>
#include "peakPicker.hpp"

// Function to read input data from files
template<typename T>
bool readDataFromFile(const std::string& filename, std::vector<T>& data) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return false;
    }
    
    T value;
    while (file >> value) {
        data.push_back(value);
    }
    
    file.close();
    return true;
}

// Function to write output data to file
template<typename T>
bool writeDataToFile(const std::string& filename, const std::vector<T>& data) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return false;
    }
    
    for (const auto& value : data) {
        file << value << std::endl;
    }
    
    file.close();
    return true;
}

// Calculate absolute error between two vectors
template<typename T>
double calculateAbsoluteError(const std::vector<T>& actual, const std::vector<T>& reference) {
    if (actual.size() != reference.size()) {
        return -1.0; // Different sizes, cannot compare
    }
    
    double maxError = 0.0;
    for (size_t i = 0; i < actual.size(); i++) {
        double error = std::abs(static_cast<double>(actual[i]) - static_cast<double>(reference[i]));
        if (error > maxError) {
            maxError = error;
        }
    }
    
    return maxError;
}

int main() {
    // Test parameters
    const unsigned int windowLength = 11; // Must be odd
    const std::string testCase = "3"; // Test case number
    
    // File paths
    const std::string xcorrFile = "pssCorrMagSq_" + testCase + "_in.txt";
    const std::string thresholdFile = "threshold_in.txt";
    const std::string refLocationsFile = "locations_" + testCase + "_ref.txt";
    const std::string outLocationsFile = "peakLocs_out.txt";
    
    // Read input data
    std::vector<float> xcorrFloatData;
    std::vector<float> thresholdFloatData;
    std::vector<int> refLocations;
    
    if (!readDataFromFile(xcorrFile, xcorrFloatData)) {
        return 1;
    }
    if (!readDataFromFile(thresholdFile, thresholdFloatData)) {
        return 1;
    }
    if (!readDataFromFile(refLocationsFile, refLocations)) {
        return 1;
    }
    
    // Ensure threshold data has same length as xcorr data by padding if necessary
    while (thresholdFloatData.size() < xcorrFloatData.size()) {
        thresholdFloatData.push_back(thresholdFloatData.back());
    }
    
    // Create input and output streams
    hls::stream<DataType> xcorrStream;
    hls::stream<ThresholdType> thresholdStream;
    hls::stream<LocationType> peakLocStream;
    hls::stream<CountType> peakCountStream;
    
    // Convert float data to fixed-point and write to streams
    for (size_t i = 0; i < xcorrFloatData.size(); i++) {
        xcorrStream.write(static_cast<DataType>(xcorrFloatData[i]));
        thresholdStream.write(static_cast<ThresholdType>(thresholdFloatData[i]));
    }
    
    // Run the peak picker algorithm
    peakPicker(
        xcorrStream,
        thresholdStream,
        xcorrFloatData.size(),
        windowLength,
        peakLocStream,
        peakCountStream
    );
    
    // Read peak count
    CountType peakCount = peakCountStream.read();
    
    // Read peak locations
    std::vector<LocationType> peakLocations;
    for (unsigned int i = 0; i < peakCount; i++) {
        peakLocations.push_back(peakLocStream.read());
    }
    
    // Write results to file
    if (!writeDataToFile(outLocationsFile, peakLocations)) {
        return 1;
    }
    
    // Compare with reference data
    bool identical = (peakLocations.size() == refLocations.size());
    if (identical) {
        for (size_t i = 0; i < peakLocations.size(); i++) {
            if (peakLocations[i] != refLocations[i]) {
                identical = false;
                break;
            }
        }
    }
    
    if (identical) {
        std::cout << "Test passed: The output matches the reference output." << std::endl;
    } else {
        std::cout << "Test failed: The output does not match the reference output." << std::endl;
        
        // Calculate error metrics
        if (peakLocations.size() == refLocations.size()) {
            double absError = calculateAbsoluteError(peakLocations, refLocations);
            std::cout << "Maximum absolute error: " << absError << std::endl;
        } else {
            std::cout << "Different number of peaks detected. Expected " 
                      << refLocations.size() << ", got " << peakLocations.size() << std::endl;
        }
    }
    
    return identical ? 0 : 1;
}
````

## Implementation Notes

1. **Data Types**:
   - Used `ap_fixed<32, 16>` for PSS correlation and threshold values
   - Used `ap_uint<16>` for location indices and `ap_uint<8>` for the peak counter

2. **Performance Optimizations**:
   - Applied `#pragma HLS PIPELINE II=1` to critical loops for high throughput
   - Used `#pragma HLS ARRAY_PARTITION complete` for the buffer arrays to enable parallel access
   - Used `#pragma HLS UNROLL` for the window comparison loop to accelerate peak detection

3. **Memory Management**:
   - Implemented sliding window buffers with fixed maximum size
   - Used FIFO interfaces for input and output streams

4. **Testbench Features**:
   - Reads input data from files in the specified format
   - Validates results against reference data
   - Reports both pass/fail status and detailed error metrics
   - Handles edge cases and provides error messages

This implementation follows the hardware-friendly approach of the MATLAB reference and adheres to all the requirements specified in the instructions.

