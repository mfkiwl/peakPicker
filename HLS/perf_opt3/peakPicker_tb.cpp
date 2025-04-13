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
