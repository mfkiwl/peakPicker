rockyco: Follow the instructions in the MD file to generate an efficient HLS C++ design and its testbench.

GitHub Copilot: # HLS C++ Implementation for Peak Picker Algorithm

I'll create a hardware-efficient HLS C++ implementation of the peak picker algorithm based on the MATLAB reference and the requirements in the instructions.

## Step-by-step approach:

1. Create a header file with type definitions and function declarations
2. Implement the core algorithm in a CPP file with HLS optimization directives
3. Develop a testbench that validates against reference data

Let's implement each file:

### [peakPicker.hpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim1/peakPicker.hpp)

This header file defines the necessary types, constants, and function declarations:

````cpp
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
typedef ap_fixed<32, 16> DataType;
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
````

### [peakPicker.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim1/peakPicker.cpp)

Implementation of the algorithm with HLS optimizations:

````cpp


Made changes.

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
            locationsStream.write(candidateLocation);
            numPeaks++;
        }
    }
}
````

### [peakPicker_tb.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/optim1/peakPicker_tb.cpp)

Testbench to validate the implementation:

````cpp


Made changes.

#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
#include "peakPicker.hpp"

// Helper function to read data from file
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

// Helper function to write data to file
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

int main() {
    // Define test parameters
    const int testNumber = 3;
    const int windowLength = 11;
    const std::string xcorrFilename = "pssCorrMagSq_" + std::to_string(testNumber) + "_in.txt";
    const std::string thresholdFilename = "threshold_in.txt";
    const std::string refLocationsFilename = "locations_" + std::to_string(testNumber) + "_ref.txt";
    const std::string outputFilename = "peakLocs_out.txt";
    
    // Read input data
    std::vector<float> xcorrFloat;
    std::vector<float> thresholdFloat;
    std::vector<int> refLocations;
    
    if (!readDataFromFile(xcorrFilename, xcorrFloat)) {
        return 1;
    }
    if (!readDataFromFile(thresholdFilename, thresholdFloat)) {
        return 1;
    }
    if (!readDataFromFile(refLocationsFilename, refLocations)) {
        return 1;
    }
    
    // Prepare input streams and output containers
    hls::stream<DataType> xcorrStream;
    hls::stream<DataType> thresholdStream;
    hls::stream<LocationType> locationsStream;
    std::vector<LocationType> peakLocations;
    
    // Convert float data to fixed-point and feed into streams
    for (const auto& value : xcorrFloat) {
        xcorrStream.write(DataType(value));
    }
    for (const auto& value : thresholdFloat) {
        thresholdStream.write(DataType(value));
    }
    
    // Call the peak picker function
    uint16_t signalLength = xcorrFloat.size();
    uint16_t numPeaks = 0;
    
    // Run the peak picker
    peakPicker(xcorrStream, thresholdStream, locationsStream, signalLength, windowLength, numPeaks);
    
    // Read output data from stream
    for (uint16_t i = 0; i < numPeaks; i++) {
        peakLocations.push_back(locationsStream.read());
    }
    
    // Write output to file
    if (!writeDataToFile(outputFilename, peakLocations)) {
        return 1;
    }
    
    // Validate results
    bool testPassed = true;
    if (peakLocations.size() != refLocations.size()) {
        testPassed = false;
        std::cout << "Test failed: Different number of peaks detected." << std::endl;
        std::cout << "Found " << peakLocations.size() << " peaks, expected " << refLocations.size() << std::endl;
    } else {
        for (size_t i = 0; i < peakLocations.size(); i++) {
            if (peakLocations[i] != refLocations[i]) {
                testPassed = false;
                std::cout << "Test failed: Peak location mismatch at index " << i << std::endl;
                std::cout << "Found at " << peakLocations[i] << ", expected at " << refLocations[i] << std::endl;
                break;
            }
        }
    }
    
    if (testPassed) {
        std::cout << "Test passed: The output matches the reference output." << std::endl;
    }
    
    return testPassed ? 0 : 1;
}
````

These implementations follow the requirements specified in the instructions:
1. The algorithm matches the MATLAB reference implementation 
2. Uses fixed-point arithmetic with ap_fixed
3. Uses hls::stream interfaces
4. Includes HLS optimization directives
5. Implements proper error checking in the testbench
6. Validates against reference data

The implementation is optimized for FPGA deployment with:
- Pipeline directives for high throughput
- BRAM resource directives for large arrays
- Unroll directive for the window checking loop

