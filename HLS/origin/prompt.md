rockyco: Proofread this instruction MD file to make the prompt be clear and specific to the LLM like Claude 3.7 Sonnet Thinking.

GitHub Copilot: # Proofreading and Improvements for the Copilot Instructions

I'll improve this instruction file to make it clearer and more specific for an LLM like Claude 3.7 Sonnet Thinking.

## Steps to improve the document:

1. Add more context about the algorithm
2. Include specific input/output details
3. Complete the cut-off requirements section
4. Clarify technical terms
5. Add structure for better prompt engineering

### [copilot-instructions.md](file:///home/jielei/Projects/UTS/peakPicker/HLS/origin/.github/copilot-instructions.md)

````markdown
# Copilot Instructions for Peak Picker Implementation

## Project Context
This project implements a critical component of a 5G NR SSB (Synchronization Signal Block) detection application. The peak picker algorithm identifies SSB signals by locating peaks where the magnitude squared of the PSS (Primary Synchronization Signal) correlation (`xcorr`) exceeds a predefined threshold. The reference implementation is in MATLAB (`peakPicker.m` with testbench `peakPicker_tb.m`).

## Task Description
Your task is to translate the MATLAB peak picker algorithm into efficient HLS C++ code while preserving exact functionality. The implementation should be optimized for FPGA deployment using Xilinx HLS directives.

**Required Files:**
- `peakPicker.hpp`: Header file with type definitions, function declarations, and parameters
- `peakPicker.cpp`: Implementation file with the core algorithm
- `peakPicker_tb.cpp`: C++ testbench that validates the implementation against reference data

## Algorithm Overview
The peak picker algorithm:
1. Takes a stream of PSS correlation magnitude squared values as input
2. Compares each value against a threshold
3. Identifies and outputs the indices (locations) where values exceed the threshold
4. Applies appropriate filtering to identify true peaks

## Input/Output Specifications
- **Inputs:**
  - PSS correlation magnitude squared values (floating-point stream)
  - Threshold value (floating-point)
- **Outputs:**
  - Peak locations (integer indices)

## Implementation Requirements

### Functional Requirements
- Implement the `peakPicker()` function in HLS C++ with exactly the same behavior as the MATLAB reference
- Follow bit-accurate implementation of the MATLAB algorithm (results must match reference within specified error margins)
- Document code thoroughly with comments explaining the algorithm and optimization decisions

### Interface and Data Type Requirements
- Use `hls::stream` interfaces with appropriate buffer depths for streaming data
- Implement fixed-point arithmetic with `ap_fixed<W,I>` (specify exact bit widths based on precision requirements)
- Use `hls::complex<ap_fixed<W,I>>` for any complex number operations
- Define all constant parameters in `peakPicker.hpp` using `#define` or `constexpr`
- Create descriptive type aliases with `typedef` or `using` statements

### File I/O and Validation
- Read input PSS correlation data from `pssCorrMagSq_#_in.txt` (one float value per line)
- Read threshold values from `threshold_in.txt` (one float value per line)
- Read reference peak locations from `locations_#_ref.txt` (one integer value per line)
- Implement robust error checking for file operations with clear error messages
- Calculate and report both absolute and relative errors between your implementation and reference values

### Performance Optimization
- Apply `#pragma HLS PIPELINE II=1` to performance-critical loops
- Use `#pragma HLS DATAFLOW` for task-level pipelining
- Implement arrays exceeding 64 elements using dual-port block RAM
- Apply memory partitioning to arrays requiring parallel access
- Configure optimization directives based on throughput requirements
- Balance resource usage and performance based on target FPGA constraints

### Coding Style
- Define all constants, types, and function declarations in `peakPicker.hpp`
- Implement core algorithm in `peakPicker.cpp` with consistent style
- Follow naming convention: camelCase for variables, PascalCase for types
- Use self-documenting identifier names that clearly reflect their purpose

## Deliverables
- Fully commented HLS C++ implementation files
- Comprehensive testbench demonstrating functional correctness
- Description of optimization approaches and their impact on performance
````
