rockyco: Follow the instructions in the MD file to generate an efficient HLS C++ design and its testbench.

GitHub Copilot: # Solution for Peak Picker HLS Implementation

I'll implement an efficient HLS C++ design for the peak picker algorithm following the instructions in the MD file. The solution will consist of three files as specified.

## Step-by-step approach:

1. Create a header file (`peakPicker.hpp`) with appropriate type definitions and function declarations
2. Implement the core algorithm in `peakPicker.cpp` based on the MATLAB reference
3. Develop a testbench (`peakPicker_tb.cpp`) to validate the implementation

Let's start with the implementation:

### [peakPicker.hpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim3/peakPicker.hpp)

This header file defines the necessary types, constants, and function declarations.

````cpp
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
typedef ap_fixed<32, 16> DataType;
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
````

### [peakPicker.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim3/peakPicker.cpp)

This file implements the core peak picker algorithm with HLS optimizations.

````cpp


Made changes.

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
                locationsStream.write(peakLocation);
            }
        }
    }
}
````

### [peakPicker_tb.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim3/peakPicker_tb.cpp)

This testbench validates the implementation against reference data.

````cpp


Made changes.

#include "peakPicker.hpp"
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <string>

// Function to read float values from a file into a vector
bool readDataFromFile(const std::string &filename, std::vector<float> &data) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return false;
    }
    
    float value;
    while (file >> value) {
        data.push_back(value);
    }
    
    file.close();
    return true;
}

// Function to read integer values from a file into a vector
bool readLocationsFromFile(const std::string &filename, std::vector<int> &locations) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return false;
    }
    
    int value;
    while (file >> value) {
        locations.push_back(value);
    }
    
    file.close();
    return true;
}

int main() {
    // Testbench configuration
    const std::string xcorrFilename = "pssCorrMagSq_3_in.txt";
    const std::string thresholdFilename = "threshold_in.txt";
    const std::string refLocationsFilename = "locations_3_ref.txt";
    
    // Read input data
    std::vector<float> xcorrData;
    std::vector<float> thresholdData;
    std::vector<int> refLocations;
    
    if (!readDataFromFile(xcorrFilename, xcorrData)) {
        return 1;
    }
    
    if (!readDataFromFile(thresholdFilename, thresholdData)) {
        return 1;
    }
    
    if (!readLocationsFromFile(refLocationsFilename, refLocations)) {
        return 1;
    }
    
    // Create input and output streams
    DataStream xcorrStream;
    DataStream thresholdStream;
    LocationStream locationsStream;
    
    // Prepare input streams
    for (size_t i = 0; i < xcorrData.size(); i++) {
        xcorrStream.write(DataType(xcorrData[i]));
        
        // Handle case where threshold data might be shorter than xcorr data
        if (i < thresholdData.size()) {
            thresholdStream.write(DataType(thresholdData[i]));
        } else {
            thresholdStream.write(DataType(thresholdData[thresholdData.size() - 1]));
        }
    }
    
    // Call the peak picker function
    peakPicker(xcorrStream, thresholdStream, locationsStream, xcorrData.size());
    
    // Collect results
    std::vector<int> resultLocations;
    while (!locationsStream.empty()) {
        resultLocations.push_back(locationsStream.read());
    }
    
    // Compare results with reference
    bool testPassed = true;
    if (resultLocations.size() != refLocations.size()) {
        std::cout << "Test failed: Number of detected peaks (" << resultLocations.size() 
                  << ") does not match reference (" << refLocations.size() << ")" << std::endl;
        testPassed = false;
    } else {
        for (size_t i = 0; i < resultLocations.size(); i++) {
            if (resultLocations[i] != refLocations[i]) {
                std::cout << "Test failed: Peak location mismatch at index " << i 
                          << ". Got " << resultLocations[i] 
                          << ", expected " << refLocations[i] << std::endl;
                testPassed = false;
                break;
            }
        }
    }
    
    // Write output locations to file
    std::ofstream outFile("peakLocs_out.txt");
    if (outFile.is_open()) {
        for (int loc : resultLocations) {
            outFile << loc << std::endl;
        }
        outFile.close();
    } else {
        std::cerr << "Error: Unable to open output file" << std::endl;
    }
    
    // Report test result
    if (testPassed) {
        std::cout << "Test passed: The output matches the reference output." << std::endl;
    } else {
        std::cout << "Test failed: The output does not match the reference output." << std::endl;
    }
    
    return testPassed ? 0 : 1;
}
````

The implementation follows the requirements specified in the instructions:

1. The header file (`peakPicker.hpp`) contains all necessary type definitions and function declarations
2. The core implementation file (`peakPicker.cpp`) implements the algorithm using HLS directives for optimization
3. The testbench (`peakPicker_tb.cpp`) validates the implementation against reference data

Key optimization techniques used:
- Array partitioning for parallel access to window buffers
- Pipelining of the main processing loop
- Unrolling of comparison operations
- Efficient stream-based interfaces

The implementation preserves the exact functionality of the MATLAB reference while optimizing for FPGA deployment.

