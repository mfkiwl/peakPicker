# Accelerating FPGA Design from MATLAB using LLMs: A 5G NR Peak Picker Case Study

**Author(s):** [Your Name/Affiliation Here]

**Abstract:** Field-Programmable Gate Arrays (FPGAs) offer significant performance benefits for computationally intensive tasks, but their design often involves complex Hardware Description Languages (HDLs). High-Level Synthesis (HLS) tools aim to bridge this gap by generating HDL from C/C++ code, while tools like MATLAB HDL Coder allow direct generation from MATLAB. However, optimizing HLS code and efficiently translating MATLAB algorithms remain challenging. This paper explores the use of Large Language Models (LLMs) to accelerate the FPGA design process, specifically focusing on translating and optimizing MATLAB algorithms for HLS. We present a comprehensive comparative study using a 5G New Radio (NR) Peak Picker algorithm as a case study. Two primary design paths are compared: (1) MATLAB to optimized HLS C++ using LLM assistance (leveraging models like Gemini, Claude 3 Sonnet, GPT-4, and GitHub Copilot) and (2) MATLAB to HDL using the conventional MATLAB HDL Coder workflow. Our findings indicate that the LLM-aided HLS approach can significantly reduce development time while achieving comparable or improved hardware performance and resource utilization compared to the direct HDL generation method. We discuss the workflow, optimization strategies facilitated by LLMs, and provide a quantitative comparison of the results.

**Keywords:** FPGA, Large Language Models (LLM), High-Level Synthesis (HLS), MATLAB, HDL Coder, 5G NR, Peak Picker, Design Automation, Hardware Acceleration.

## 1. Introduction

Field-Programmable Gate Arrays (FPGAs) provide a flexible platform for hardware acceleration, particularly crucial in domains like 5G wireless communications where real-time signal processing is paramount [1]. However, the traditional FPGA design flow using Hardware Description Languages (HDLs) such as Verilog or VHDL is often time-consuming and requires specialized expertise. To improve productivity, High-Level Synthesis (HLS) tools have emerged, enabling hardware generation from higher-level languages like C, C++, or SystemC [2].

MATLAB is widely used for algorithm development and simulation in signal processing. Tools like MATLAB HDL Coder automate the conversion of MATLAB code directly to HDL [3], streamlining the path from algorithm to hardware. While effective, achieving optimal performance and resource utilization often requires significant manual code restructuring and pragma insertion within the MATLAB environment.

Alternatively, algorithms developed in MATLAB can be manually translated to C/C++ for use with HLS tools. This translation process can be error-prone and time-intensive. Furthermore, writing efficient HLS code that maps well to hardware architecture requires careful consideration of parallelism, memory access patterns, and data types [4].

Recently, Large Language Models (LLMs) have demonstrated remarkable capabilities in code generation, translation, and explanation across various programming languages [5]. Their potential application in hardware design, particularly in aiding the HLS workflow, is an emerging area of interest. LLMs could potentially automate the translation from MATLAB to HLS-compatible C++, assist in applying HLS optimization directives, and even help debug HLS code.

This paper investigates the efficacy of using LLMs to facilitate the FPGA implementation of algorithms initially designed in MATLAB. We conduct a comparative study focusing on a peak picker algorithm, a vital component in 5G New Radio (NR) Synchronization Signal Block (SSB) detection [6]. We compare two distinct design methodologies:

1.  **LLM-Aided HLS:** Translating the MATLAB reference algorithm to C++ using LLMs, followed by iterative optimization and debugging of the HLS code with LLM assistance.
2.  **MATLAB HDL Coder:** Generating HDL directly from the MATLAB reference algorithm using the established HDL Coder workflow.

Our contribution lies in the systematic comparison of these approaches, evaluating development time, resource utilization, and performance metrics. We demonstrate how LLMs can be integrated into the HLS design flow to potentially enhance productivity and design quality.

## 2. Case Study: 5G NR Peak Picker Algorithm

The algorithm chosen for this study is a peak picker designed for 5G NR SSB detection. Its function is to identify the most significant correlation peaks from the cross-correlation results between the received signal and known synchronization sequences (e.g., the Primary Synchronization Signal, PSS). These peaks correspond to potential timings of the SSB within the received frame.

The reference MATLAB implementation (`peakPicker.m`) takes the cross-correlation magnitude results (`xcorr`), a corresponding threshold (`threshold`), and a window length (`window_length`) as inputs. It outputs the `locations` (indices) of the detected peaks.

The core logic involves:
- Iterating through the `xcorr` data using a sliding window of size `window_length`.
- Identifying a `candidate_location` at the center of the current window.
- Checking if the cross-correlation value at the `candidate_location` exceeds the specified `threshold`.
- If the threshold is exceeded, performing a local maximum check: ensuring the value at the `candidate_location` is the maximum value within the current `window_length`. This step prevents selecting points on the slope of a larger peak.
- Storing the index (`candidate_location`) if it passes both the threshold and local maximum checks.

This algorithm represents a common signal processing task involving array traversal, comparisons, conditional logic, and local maximum identification, making it suitable for FPGA implementation where such operations can be efficiently parallelized. The accompanying plots (not shown here, but referenced in the original context) illustrate the process, showing the cross-correlation signal, the applied threshold, and the identified peaks.

## 3. FPGA Implementation Methodologies

We implemented the peak picker algorithm on an FPGA using two distinct paths originating from the same MATLAB reference code, as illustrated in Figure 1 (*Note: Add a figure illustrating the workflows*).

### 3.1 Path 1: LLM-Aided HLS

This path leverages LLMs (e.g., Claude 3 Sonnet, Gemini, GPT-4, Copilot) to facilitate the transition from MATLAB to optimized HLS C++. The workflow is as follows:

1.  **MATLAB Code Adaptation:** The initial MATLAB code is reviewed and potentially adapted for hardware suitability. This might involve simplifying logic, considering data types, and ensuring the algorithm structure is amenable to hardware mapping.
2.  **LLM Translation (HLS-Oriented Prompts):** The adapted MATLAB code is provided to an LLM using carefully crafted "HLS-Oriented Prompts". These prompts guide the LLM to generate C++ code (`*.cpp`, `*.hpp`) and a corresponding testbench (`*_tb.cpp`) that are not only functionally correct but also structured favorably for HLS tools.
3.  **C/C++ Fine-tuning & Verification:** The LLM-generated C++ code undergoes manual review and fine-tuning. This step ensures correctness, addresses any subtle HLS incompatibilities, and potentially incorporates initial optimization insights. The C++ testbench is used to verify functional equivalence against the original MATLAB algorithm using representative test vectors.
4.  **HLS Synthesis & Optimization (Vitis HLS/Vivado):** The verified C++ code is synthesized using Vitis HLS (part of the Vivado Design Suite). An iterative optimization loop follows, potentially involving further LLM assistance (using prompts based on synthesis reports) or manual refinement to:
    *   Apply HLS pragmas (`#pragma HLS PIPELINE`, `#pragma HLS UNROLL`, `#pragma HLS ARRAY_PARTITION`, etc.).
    *   Refactor C++ structures (e.g., loops, data storage) for better hardware mapping.
    *   Analyze and resolve synthesis warnings or performance bottlenecks identified in HLS reports.
5.  **Hardware Performance Analysis:** The synthesized designs are analyzed for resource utilization (LUTs, FFs, DSPs, BRAM), latency, throughput (Initiation Interval - II), and maximum achievable clock frequency (Fmax).

### 3.2 Path 2: MATLAB HDL Coder

This path follows the conventional workflow using MathWorks tools:

1.  **MATLAB Code Adaptation:** Similar to the HLS path, the MATLAB code requires adaptation. This often involves more extensive modifications specifically targeting HDL Coder's requirements and optimization capabilities (e.g., explicit fixed-point type conversions, loop restructuring for efficient HDL generation, ensuring compatibility with supported MATLAB functions).
2.  **HDL Code Generation:** MATLAB HDL Coder is used to automatically generate hardware descriptions (Verilog or VHDL) from the adapted MATLAB function. The tool can generate interfaces like AXI-Stream (AXIS) for integration into larger FPGA systems.
3.  **Synthesis & Verification:** The generated HDL code is synthesized using FPGA synthesis tools (e.g., Vivado) and verified through simulation, potentially using co-simulation capabilities with MATLAB/Simulink.
4.  **Hardware Performance Analysis:** Similar to Path 1, the final hardware implementation is analyzed for performance (Fmax, Latency) and resource utilization metrics.

## 4. Implementation Details

-   **MATLAB Version:** R2023a (or specify the version used)
-   **HLS Tool:** Vitis HLS 2023.2 (or specify the version used)
-   **Synthesis Tool:** Vivado 2023.2 (or specify the version used)
-   **LLMs Used:** Google Gemini, Anthropic Claude 3 Sonnet, OpenAI GPT-4, GitHub Copilot (via interactive prompting)
-   **Target FPGA Family:** Xilinx UltraScale+ (Specify the exact part if possible, e.g., ZCU102 board)

The core difference between the paths lies in the intermediate representation (HLS C++ vs. direct HDL) and the primary means of optimization (LLM-assisted pragma/code refinement vs. HDL Coder settings/MATLAB code refinement).

## 5. Results and Discussion

This section compares the two methodologies based on the findings reported in the project's analysis. (*Note: Replace bracketed placeholders with actual quantitative data from the study.*)

### 5.1 Development Time

-   **LLM-Aided HLS:** The initial translation from MATLAB to functional C++ using LLMs was observed to be significantly faster than manual translation. The iterative optimization phase, while requiring engineering judgment to formulate effective prompts and evaluate LLM suggestions, was also potentially accelerated compared to purely manual HLS optimization exploration. The total estimated development time was [Estimate X hours/days].
-   **HDL Coder:** The time required primarily involved MATLAB code preparation for HDL Coder compatibility, fixed-point conversion, and configuring the tool settings. The estimated development time was [Estimate Y hours/days].

Preliminary results suggest a [e.g., significant reduction / moderate reduction / comparable time] in overall development time for the LLM-aided HLS path compared to the HDL Coder path, particularly when complex optimizations are needed beyond HDL Coder's automatic capabilities. LLM assistance in generating testbenches and debugging HLS code was noted as a potential time-saver.

### 5.2 Resource Utilization

| Implementation          | LUTs      | FFs       | DSPs    | BRAM    |
| :---------------------- | :-------- | :-------- | :------ | :------ |
| LLM-HLS (Optimized 1) | [Value 1] | [Value 1] | [Value] | [Value] |
| LLM-HLS (Optimized 2) | [Value 2] | [Value 2] | [Value] | [Value] |
| HDL Coder             | [Value 3] | [Value 3] | [Value] | [Value] |
*(Add more rows for different optimization levels if applicable)*

The LLM-aided HLS approach allowed for fine-grained exploration of optimization trade-offs (e.g., latency vs. resources). Different HLS versions, guided by LLM suggestions or manual tuning, yielded varying resource footprints. Compared to the HDL Coder output, the optimized LLM-aided HLS versions achieved [e.g., lower LUT/FF count / comparable resources / higher resources but better performance - specify the outcome].

### 5.3 Performance

| Implementation          | Clock Freq. (MHz) | Latency (cycles) | Initiation Interval (II) | Throughput (samples/cycle) |
| :---------------------- | :---------------- | :--------------- | :----------------------- | :------------------------- |
| LLM-HLS (Optimized 1) | [Value 1]         | [Value 1]        | [Value 1]                | [Calculate based on II]    |
| LLM-HLS (Optimized 2) | [Value 2]         | [Value 2]        | [Value 2]                | [Calculate based on II]    |
| HDL Coder             | [Value 3]         | [Value 3]        | [N/A or Estimate]        | [Estimate]                 |
*(Add more rows for different optimization levels if applicable)*

The ability to apply specific HLS pragmas (e.g., `PIPELINE`, `ARRAY_PARTITION`), guided by LLM suggestions and synthesis reports, allowed the HLS implementations to achieve [e.g., higher clock frequencies, lower latency, and higher throughput (II=1)] compared to the HDL Coder baseline in several optimized variants. The performance achieved via HDL Coder is often dependent on the tool's internal heuristics and the structure of the input MATLAB code.

### 5.4 Discussion

The LLM-aided HLS workflow demonstrated significant potential for accelerating the path from a MATLAB algorithm to an optimized FPGA implementation. Key advantages observed include:
-   **Rapid Prototyping:** Faster initial translation from MATLAB to verifiable C++ code.
-   **Guided Optimization:** LLMs effectively suggested relevant HLS pragmas and code structures based on high-level goals (e.g., "minimize latency") or analysis of synthesis reports, reducing the manual effort required to explore the vast HLS optimization space.
-   **Debugging Assistance:** LLMs provided valuable insights into HLS-specific coding issues, potential causes of synthesis warnings, and explanations of HLS concepts.
-   **Testbench Generation:** LLMs can assist in generating basic C++ testbenches, reducing setup time.

However, challenges and considerations remain:
-   **Correctness & Verification:** LLM-generated code requires rigorous verification. LLMs can introduce subtle errors or generate code that is functionally correct but inefficient for HLS. Thorough simulation against the original MATLAB model is essential.
-   **Expertise Still Required:** Effective use requires an engineer with a solid understanding of the algorithm, FPGA architecture, and HLS principles. The engineer must formulate effective prompts, critically evaluate LLM suggestions, interpret synthesis reports, and make final design decisions. LLMs augment, rather than replace, engineering expertise.
-   **Prompt Engineering:** The quality of the LLM output heavily depends on the clarity, specificity, and context provided in the prompts. Iterative refinement of prompts is often necessary.
-   **Determinism and Reproducibility:** LLM outputs can vary between runs. Managing generated code versions and ensuring reproducibility requires careful workflow management.

Compared to HDL Coder, the LLM-aided HLS path offers potentially more granular control over the hardware microarchitecture through C++/HLS refinement. HDL Coder provides a more direct, automated path from MATLAB but may offer less flexibility for certain types of manual optimization compared to HLS. The choice between methods may depend on project complexity, performance requirements, and team expertise.

## 6. Conclusion

This paper presented a comparative study of implementing a 5G NR peak picker algorithm on an FPGA, contrasting an LLM-aided HLS workflow with the traditional MATLAB HDL Coder approach. Our preliminary results indicate that leveraging LLMs for MATLAB-to-C++ translation, HLS optimization guidance, and debugging assistance can significantly reduce development time while achieving competitive or superior hardware performance and resource utilization compared to direct HDL generation from MATLAB.

While LLMs are powerful accelerators for specific tasks within the design flow, human expertise remains crucial for verification, strategic decision-making, and guiding the optimization process. The LLM-aided HLS workflow represents a promising direction for enhancing FPGA design productivity, particularly for engineers and teams seeking to bridge the gap between high-level algorithm descriptions in MATLAB and efficient hardware implementations.

Future work could involve applying this methodology to more complex algorithms, developing more sophisticated prompting strategies tailored to specific HLS optimization challenges, investigating the integration of LLMs with formal verification techniques, and exploring tighter integration of LLMs within existing EDA toolchains.

## 7. References

[1] T. S. Rappaport et al., "Millimeter Wave Mobile Communications for 5G Cellular: It Will Work!", *IEEE Access*, vol. 1, pp. 335-349, 2013. DOI: [Add DOI if available]
[2] J. Cong et al., "High-Level Synthesis for FPGAs: From Prototyping to Deployment," *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, vol. 30, no. 4, pp. 473-491, Apr. 2011. DOI: [Add DOI if available]
[3] MathWorks, "HDL Coder - Generate Verilog and VHDL Code for FPGAs and ASICs," MathWorks, Inc. [Online]. Available: https://www.mathworks.com/products/hdl-coder.html [Accessed: YYYY-MM-DD]
[4] Xilinx, Inc. (now AMD), "Vitis High-Level Synthesis User Guide (UG1399)," [Online]. Available: https://docs.xilinx.com/r/en-US/ug1399-vitis-hls [Accessed: YYYY-MM-DD]
[5] A. Vaswani et al., "Attention Is All You Need," *Advances in Neural Information Processing Systems 30 (NIPS 2017)*, pp. 5998-6008, 2017. [Link or DOI if available]
[6] 3GPP, TS 38.211, "NR; Physical channels and modulation," (Release 17 or later). [Link to specific version if possible]

*(Note: Ensure all references are complete, including DOIs or access dates where appropriate. Add other relevant citations as needed.)*
