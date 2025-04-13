# LLM-Aided FPGA Design Flow for Peak Picker Algorithm: A Comprehensive Comparative Study

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HLS Version](https://img.shields.io/badge/HLS-2023.2-blue.svg)](https://www.xilinx.com/products/design-tools/vitis/vitis-hls.html)
[![MATLAB Version](https://img.shields.io/badge/MATLAB-R2023a-orange.svg)](https://www.mathworks.com/products/matlab.html)

## Overview

This repository demonstrates a **comprehensive comparative study** of FPGA implementation methodologies for a peak picker algorithm used in 5G NR signal processing. We systematically compare multiple design paths:

1. **MATLAB reference implementation** → **Optimized HLS C++ implementations** through LLM assistance
2. **MATLAB reference implementation** → **Direct HDL generation** using MATLAB HDL Coder

By leveraging Large Language Models (LLMs) like Google Gemini, Claude 3.7 Sonnet, GPT-4, and GitHub Copilot, we've achieved significant reductions in development time while maintaining or improving design quality compared to traditional approaches.

The project showcases:

1. **Parallel implementation paths** with methodical comparison of different approaches
2. **Multiple optimization strategies** with documented performance trade-offs across all metrics
3. **LLM-assisted debugging and optimization workflows** with measurable improvements
4. **Quantitative comparison** between traditional MATLAB HDL Coder and LLM-aided HLS approaches

## Case Study: 5G NR Peak Picker

Our peak picker algorithm is a critical component for 5G NR Synchronization Signal Block (SSB) detection, serving as an ideal candidate for comparative implementation analysis due to its well-defined functionality and measurable performance metrics.

### Algorithm Description

The peak picker algorithm:
- Takes PSS (Primary Synchronization Signal) correlation magnitude squared values as input
- Compares values against adaptive thresholds to identify candidate peaks
- Applies filtering to eliminate false positives
- Returns the locations (indices) of detected peaks for subsequent processing

![Peak Picker Algorithm](docs/peakPickerAlgorithm.png)
*Figure 1: Visualization of the Peak Picker Algorithm showing the MATLAB implementation alongside the signal processing visualization. The left panel shows the core algorithm code with sliding window implementation, while the right panel displays the correlation peaks that are detected when the signal exceeds the threshold (dotted red line).*

## Implementation Methodology and Comparative Approach

Our comparative methodology explores multiple parallel implementation paths:

```mermaid
graph TD
    A[MATLAB Reference Code] --> B1[LLM-Aided Optimization Path]
    A --> B2[MATLAB HDL Coder Path]
    B1 --> C1[LLM-Generated HLS C++]
    C1 --> D1[Progressive HLS Optimizations]
    D1 --> E1[perf_opt1: Memory Optimization]
    D1 --> E2[perf_opt2: Algorithmic Optimization]
    D1 --> E3[perf_opt3: HLS Directive Optimization]
    B2 --> C2[Direct HDL Generation]
    C2 --> D2[HDL Coder Output]
    E1 --> F[Comparative Analysis]
    E2 --> F
    E3 --> F
    D2 --> F
```

![LLM-Aided Design Flow](docs/llm_design_flow.png)
*Figure 2: The dual-path implementation approach, illustrating (1) the LLM-aided optimization flow with multiple strategies and (2) the traditional MATLAB HDL Coder flow. This systematic approach enables direct comparison between different methodologies across key performance metrics.*

### 1. Prompt Engineering for Code Generation and Optimization

We developed specialized prompt templates for each implementation stage and optimization strategy:

1. **Context & Background**: Clear description of algorithm purpose and mathematical foundation
2. **Specific Optimization Goals**: Targeted prompts for each optimization strategy (memory, algorithm, directives)
3. **Implementation Requirements**: Detailed specifications for each implementation path
4. **Comparative Analysis Targets**: Metrics to measure for fair cross-implementation comparison

Example from our peak picker implementation:

```markdown
# Implementation Strategy: Memory Optimization (perf_opt1)

## Optimization Context
The current implementation has high BRAM usage and inefficient memory access patterns.
Target metrics for improvement:
- Reduce BRAM usage by implementing local buffers
- Optimize memory access patterns for sliding window operations

## Task Description
Reimplement the peak picker algorithm with a focus on memory optimization while
maintaining functional correctness. Use the provided MATLAB reference as ground truth.

[Additional sections...]
```

### 2. Progressive Optimization Strategy

Our methodology systematically explores different optimization dimensions, with each version targeting specific improvements:

1. **Origin**: Direct translation from MATLAB reference (baseline)
2. **perf_opt1**: Memory architecture and access pattern optimization
3. **perf_opt2**: Algorithmic restructuring and computational efficiency
4. **perf_opt3**: Advanced HLS directive optimization for pipeline and parallelism
5. **HDL Coder**: Direct HDL generation from MATLAB for comparison

### 3. Comprehensive Performance Analysis

Through our comparative analysis, we've documented the trade-offs between different implementation strategies:

| Implementation | LUTs | FFs | BRAMs | Latency (cycles) | Fmax (MHz) |
|---------------|------|-----|-------|-----------------|-----------|
| Origin        | 7457 | 10624 | 10 | 108328 | 221.3 |
| perf_opt1     | 264 | 539 | 20 | 311594 | 282.3 |
| perf_opt2     | 4923 | 4394 | 0 | 275844 | 271.4 |
| perf_opt3     | 284 | 666 | 0 | 6035 | 398.4 |
| HDL Coder     | 270 | 199 | 0 | 12012 | 285.7 |
| HLS Reference | 336 | 296 | 0 | 343400 | 333.3 |

## Performance Analysis and Comparative Results

Our systematic comparison revealed striking trade-offs and advantages between implementation approaches:

### Resource Utilization vs. Clock Frequency

![Resource Utilization vs Frequency](docs/timing_vs_resources.png)
*Figure 3: Resource utilization versus clock frequency scatter plot comparing all implementation strategies. The bubble size represents BRAM usage. The perf_opt3 LLM-optimized implementation (circled in red) achieves the optimal balance with minimal LUT count (284), no BRAM usage, and the highest clock frequency at approximately 400 MHz, outperforming both the traditional HDL Coder approach and other optimization strategies.*

### Comparative Performance Analysis

<div style="display: flex; justify-content: space-between;">
   <img src="docs/resource_comparison.png" alt="Resource Utilization" width="49%">
   <img src="docs/timing_comparison.png" alt="Clock Frequency" width="49%">
</div>
*Figure 4: Side-by-side comparison of resource utilization (left) and clock frequency (right) across all implementation approaches. This direct comparison demonstrates the clear advantages and trade-offs between LLM-optimized HLS implementations and traditional HDL generation methods.*

### Latency Comparison and Analysis

![Latency Comparison](docs/latency_comparison.png)
*Figure 5: Comprehensive latency comparison across all implementation strategies. The perf_opt3 LLM-optimized implementation achieves the shortest latency at just 6,035 cycles (highlighted with "II = 1"), representing an 18x improvement over the original implementation and 2x improvement over the MATLAB HDL Coder approach. This demonstrates the significant advantages of targeted LLM-aided optimization over traditional methodologies.*

## Getting Started

### Prerequisites

- Vitis HLS 2023.2 or newer
- MATLAB R2023a or newer (for reference models)
- Python 3.8+ with necessary libraries for data handling

### Installation

```bash
# Clone this repository
git clone https://github.com/rockyco/peakPicker.git
cd peakPicker

# Set up your environment
source /path/to/Vitis/settings64.sh
```

### Usage

1. **Explore MATLAB reference implementations**:
   ```bash
   cd MATLAB/origin
   # Open the MATLAB files in MATLAB to understand the reference algorithm
   ```

2. **Run HLS C simulation for different optimization strategies**:
   ```bash
   # Original implementation
   cd ../../HLS/origin
   make csim
   
   # Memory-optimized implementation (perf_opt1)
   cd ../perf_opt1
   make csim
   
   # Algorithmically optimized implementation (perf_opt2)
   cd ../perf_opt2
   make csim
   
   # Fully optimized implementation with HLS directives (perf_opt3)
   cd ../perf_opt3
   make csim
   ```

3. **Compare implementations with MATLAB HDL Coder version**:
   ```bash
   cd ../../HDLCoder
   # Review and simulate the HDL Coder generated implementation
   ```

4. **Generate comparative analysis report**:


## Repository Structure

```
peakPicker/
├── MATLAB/                      # MATLAB reference implementations
│   ├── origin/                  # Original reference code
│   └── perf_opt*/               # Optimized MATLAB versions for different strategies
├── HLS/                         # HLS C++ implementations
│   ├── origin/                  # Initial translation from MATLAB
│   ├── perf_opt1/               # Memory-optimized implementation
│   ├── perf_opt2/               # Algorithmically optimized implementation 
│   └── perf_opt3/               # Fully optimized implementation with HLS directives
├── HDLCoder/                    # HDL implementations from MATLAB HDL Coder
├── docs/                        # Documentation and comparative performance reports
└── scripts/                     # Automation scripts for comparative analysis
```

## Key Optimization Techniques and Comparative Insights

Our comparative analysis revealed these key insights across implementation methodologies:

1. **Memory Architecture**: 
   - HLS perf_opt1 used 20 BRAMs but improved clock frequency by 27%
   - HDL Coder eliminated BRAM usage but with lower frequency than perf_opt3
   
2. **Algorithmic Optimization**: 
   - HLS perf_opt2 demonstrated that algorithmic changes alone without directive optimization led to higher resource usage
   - MATLAB HDL Coder's automatic optimizations were effective for resource usage but suboptimal for latency

3. **HLS Directive Mastery**:
   - LLM-aided perf_opt3 achieved the optimal balance by combining algorithmic improvements with expert HLS directive application
   - Reduced latency by 18x compared to the origin implementation and 2x compared to HDL Coder

4. **Development Methodology Comparison**:
   - LLM-aided approach provided more fine-grained control over optimization strategies
   - MATLAB HDL Coder offered faster initial implementation but less flexibility for targeted optimizations

## Best Practices for Comparative FPGA Implementation

Based on our comparative study, we recommend these best practices:

1. **Define Clear Comparative Metrics**: Establish specific performance targets across all implementation paths
2. **Isolate Optimization Dimensions**: Test one optimization strategy at a time to clearly measure its impact
3. **Maintain Functional Equivalence**: Ensure all implementations pass identical test vectors
4. **Document Trade-offs Explicitly**: Each optimization strategy comes with specific advantages and costs

## Technology Supporters

This project was made possible through the support of various technologies and platforms:

### FPGA Design & Development

<div style="display: flex; align-items: center; flex-wrap: nowrap; gap: 30px; overflow-x: auto; padding: 10px 0;">
  <div style="text-align: center; min-width: 120px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg" alt="AMD-Xilinx Logo" height="60"/>
    <p><b>AMD-Xilinx Vitis HLS</b></p>
  </div>
  <div style="text-align: center; min-width: 120px;">
    <img src="https://hellogov.us/img/vitis.png" alt="AMD University Program Logo" height="50"/>
    <p><b>AMD University Program</b></p>
  </div>
</div>

The AMD University Program provided access to advanced FPGA development tools and educational resources, enabling us to implement and optimize our peak picker algorithm on industry-standard hardware platforms. Vitis HLS was essential for our high-level synthesis workflow, converting C++ code to optimized RTL.

### Algorithm Development & Reference Implementation

<div style="display: flex; align-items: center; flex-wrap: nowrap; gap: 30px; overflow-x: auto; padding: 10px 0;">
  <div style="text-align: center; min-width: 120px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/2/21/Matlab_Logo.png" alt="MATLAB Logo" height="60"/>
    <p><b>MATLAB</b></p>
  </div>
  <div style="text-align: center; min-width: 120px;">
    <img src="https://www.mathworks.com/etc.clientlibs/mathworks/clientlibs/customer-ui/templates/common/resources/images/pic-header-mathworks-logo.svg" alt="MathWorks HDL Coder Logo" height="50"/>
    <p><b>HDL Coder</b></p>
  </div>
</div>

MATLAB provided the foundation for our reference algorithm implementation and visualization, while MathWorks HDL Coder enabled us to generate alternative HDL code directly from MATLAB, offering valuable comparison points for our LLM-directed optimization approach.

### Development Environment

<div style="display: flex; align-items: center; flex-wrap: nowrap; gap: 30px; overflow-x: auto; padding: 10px 0;">
  <div style="text-align: center; min-width: 120px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/9/9a/Visual_Studio_Code_1.35_icon.svg" alt="VS Code Logo" height="60"/>
    <p><b>VS Code</b></p>
  </div>
  <div style="text-align: center; min-width: 120px;">
    <img src="https://git-scm.com/images/logos/downloads/Git-Logo-2Color.png" alt="Git Logo" height="50"/>
    <p><b>Git</b></p>
  </div>
</div>

Visual Studio Code served as our primary integrated development environment, providing a consistent platform for code editing, version control, and LLM integration, while Git enabled collaborative development and version tracking throughout the project.

### AI and LLM Assistance

<div style="display: flex; align-items: center; flex-wrap: nowrap; gap: 30px; overflow-x: auto; padding: 10px 0;">
  <div style="text-align: center; min-width: 120px;">
    <img src="https://cdn.sanity.io/images/4zrzovbb/website/52ddb5bcc95d134e1c9dd2ce97c4f0dc3f80aaf6-344x184.svg" alt="Claude Logo" height="60"/>
    <p><b>Claude 3.7 Sonnet</b></p>
  </div>
  <div style="text-align: center; min-width: 120px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/1200px-Google_Gemini_logo.svg.png" alt="Gemini Logo" height="60"/>
    <p><b>Gemini 2.5 Pro</b></p>
  </div>
  <div style="text-align: center; min-width: 120px;">
    <img src="https://github.githubassets.com/images/modules/site/copilot/copilot.png" alt="GitHub Copilot Logo" height="60"/>
    <p><b>GitHub Copilot</b></p>
  </div>
</div>

Large Language Models played a central role in our design methodology:
- **Claude 3.7 Sonnet** provided advanced reasoning capabilities for complex algorithm translations and optimizations
- **Gemini 2.5 Pro** assisted with code generation and performance optimization suggestions
- **GitHub Copilot** enhanced developer productivity through context-aware code suggestions and pair programming

## Star Us on GitHub ⭐

If you find this project useful, please consider giving it a star on GitHub! Stars help us in multiple ways:

[![GitHub stars](https://img.shields.io/github/stars/your-username/peakPicker.svg?style=social&label=Star&maxAge=2592000)](https://github.com/rockyco/peakPicker)

- **Visibility**: Stars increase the project's visibility in the FPGA and LLM communities
- **Feedback**: They provide valuable feedback that the project is useful
- **Community Growth**: More stars attract more contributors and users
- **Motivation**: They motivate our team to continue improving the project

Your support helps drive the development of better LLM-aided FPGA design tools and methodologies. Thank you! 🙏

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Special thanks to the AMD University Program for providing access to FPGA development tools and resources
- Thanks to the developers of Claude 3.7 Sonnet and GitHub Copilot for enabling this workflow
- MathWorks for providing MATLAB and HDL Coder tools for comparative analysis

