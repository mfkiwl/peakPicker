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
template<typename T1, typename T2>
double calculateAbsoluteError(const std::vector<T1>& actual, const std::vector<T2>& reference) {
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
