rockyco: Follow the instructions in the MD file to generate an efficient HLS C++ design and its testbench.

GitHub Copilot: # Solution for HLS C++ Implementation of Peak Picker

I'll implement the peak picker algorithm in HLS C++ according to the requirements. The implementation will include three main files: header file, implementation file, and testbench.

## Step-by-Step Approach:

1. Create a header file (peakPicker.hpp) defining data types, constants, and function declarations
2. Implement the core algorithm in peakPicker.cpp with HLS optimization directives
3. Develop a testbench (peakPicker_tb.cpp) to validate the implementation against reference data

Let's start with developing each file:

### [peakPicker.hpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/origin/peakPicker.hpp)

Creating a header file with necessary type definitions, constants, and function declarations.

````cpp
#ifndef PEAK_PICKER_HPP
#define PEAK_PICKER_HPP

#include "ap_fixed.h"
#include "hls_stream.h"
#include <vector>

// Fixed-point type definitions for PSS correlation magnitude squared values
#define DATA_WIDTH 32   // Total bit width
#define INT_WIDTH 16    // Integer bit width
typedef ap_fixed<DATA_WIDTH, INT_WIDTH> DataType;

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
````

### [peakPicker.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/origin/peakPicker.cpp)

Implementing the core algorithm with HLS optimization directives.

````cpp


Made changes.

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
            if (maxCheckCount == windowLength) {
                locations[numLocations] = candidateLocation;
                numLocations++;
                
                // Prevent buffer overflow
                if (numLocations >= MAX_LOCATIONS) {
                    break;
                }
            }
        }
    }
}
````

### [peakPicker_tb.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/origin/peakPicker_tb.cpp)

Creating a testbench to validate the implementation.

````cpp


Made changes.

#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <vector>
#include "peakPicker.hpp"

// Utility function to read data from file
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

// Test function to compare results with reference
bool compareResults(const std::vector<int>& result, const std::vector<int>& reference) {
    if (result.size() != reference.size()) {
        std::cout << "Size mismatch! Result: " << result.size() 
                  << ", Reference: " << reference.size() << std::endl;
        return false;
    }
    
    for (size_t i = 0; i < result.size(); i++) {
        if (result[i] != reference[i]) {
            std::cout << "Mismatch at index " << i << "! Result: " << result[i] 
                      << ", Reference: " << reference[i] << std::endl;
            return false;
        }
    }
    
    return true;
}

int main() {
    // Define test parameters
    const int windowLength = 11;  // Same as in MATLAB testbench
    const std::string xcorrFilename = "pssCorrMagSq_3_in.txt";
    const std::string thresholdFilename = "threshold_in.txt";
    const std::string refLocationsFilename = "locations_3_ref.txt";
    
    // Read input data
    std::vector<float> xcorrData;
    if (!readDataFromFile(xcorrFilename, xcorrData)) {
        return 1;
    }
    
    std::vector<float> thresholdData;
    if (!readDataFromFile(thresholdFilename, thresholdData)) {
        return 1;
    }
    
    std::vector<int> refLocations;
    if (!readDataFromFile(refLocationsFilename, refLocations)) {
        return 1;
    }
    
    // Prepare input data for HLS function
    DataType xcorr[MAX_XCORR_LENGTH][MAX_SEQ_NUMBER];
    DataType threshold[MAX_XCORR_LENGTH];
    int xcorrLength = xcorrData.size();
    int seqCount = 1;  // Assuming single sequence for simplicity
    
    // Convert input data to fixed-point format
    for (int i = 0; i < xcorrLength; i++) {
        xcorr[i][0] = DataType(xcorrData[i]);
        threshold[i] = DataType(thresholdData[i < thresholdData.size() ? i : thresholdData.size()-1]);
    }
    
    // Prepare output buffers
    int locations[MAX_LOCATIONS];
    int numLocations;
    
    // Call the peak picker function
    peakPicker(xcorr, threshold, xcorrLength, seqCount, windowLength, locations, numLocations);
    
    // Convert results to vector for comparison
    std::vector<int> resultLocations;
    for (int i = 0; i < numLocations; i++) {
        resultLocations.push_back(locations[i]);
    }
    
    // Compare with reference
    bool testPassed = compareResults(resultLocations, refLocations);
    
    // Report test results
    if (testPassed) {
        std::cout << "Test PASSED: All peak locations match the reference output." << std::endl;
    } else {
        std::cout << "Test FAILED: Output does not match reference." << std::endl;
    }
    
    // Write results to output file for verification
    std::ofstream outFile("peakLocs_out.txt");
    if (outFile.is_open()) {
        for (int i = 0; i < numLocations; i++) {
            outFile << locations[i] << std::endl;
        }
        outFile.close();
    }
    
    return testPassed ? 0 : 1;
}
````

## Implementation Summary

The implementation consists of three key files that translate the MATLAB peak picker algorithm to HLS C++:

1. **peakPicker.hpp**: 
   - Defines fixed-point data types for precision control
   - Sets maximum parameter values as constants
   - Declares the main peakPicker function interface

2. **peakPicker.cpp**:
   - Implements the core algorithm following the MATLAB reference
   - Uses HLS interface and optimization pragmas:
     - Memory partitioning for parallel access
     - Pipeline directives for high throughput
     - Interface specifications for AXI compatibility

3. **peakPicker_tb.cpp**:
   - Reads input and reference data from files
   - Converts floating-point inputs to fixed-point format
   - Calls the peakPicker function
   - Compares results with reference data
   - Reports accuracy and writes results to output file

The implementation follows the algorithm from the MATLAB reference while optimizing for FPGA deployment using HLS directives. The code is thoroughly commented to explain the implementation details and optimization decisions.

