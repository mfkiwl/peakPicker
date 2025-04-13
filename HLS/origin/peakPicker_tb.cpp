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
