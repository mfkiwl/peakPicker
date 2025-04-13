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
