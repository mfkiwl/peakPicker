rockyco: Revise this Python file to print all of the report data into a TXT file for further comparion with other reports

GitHub Copilot: I'll create a solution to save all report data to a TXT file for easier comparison with other reports.

## Step-by-step solution:

1. Create a new function `save_report_to_txt()` that formats and writes all report data to a text file
2. Import datetime module to timestamp the report
3. Modify the main function to call this new function after processing reports
4. Ensure the file path is sensible and the output is well-formatted

### [readReports.py](file:///home/jielei/Projects/UTS/peakPicker/HDLCoder/readReports.py)

Add the datetime import and create a new function to save report data to a text file, then update the main function to call it.

````python
import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import datetime  # Add this import for timestamping reports

# ...existing code...

def save_report_to_txt(resources, timing, latency, base_dir, output_file="implementation_report.txt"):
    """
    Save all report data to a text file for future reference and comparison.
    
    Args:
        resources (dict): Resource utilization data by implementation
        timing (dict): Timing data by implementation
        latency (dict): Latency data by implementation
        base_dir (str): Base directory of the reports
        output_file (str): Path to the output file
    """
    with open(output_file, 'w') as f:
        # Write a header with timestamp
        f.write(f"===============================================\n")
        f.write(f"FPGA Implementation Report - {datetime.datetime.now()}\n")
        f.write(f"Base Directory: {base_dir}\n")
        f.write(f"===============================================\n\n")
        
        # Write Resource Utilization
        if resources:
            f.write("RESOURCE UTILIZATION SUMMARY:\n")
            f.write("-----------------------------\n")
            df_resources = pd.DataFrame(resources)
            f.write(df_resources.round(2).to_string())
            f.write("\n\n")
        
        # Write Timing Summary
        if timing:
            f.write("TIMING SUMMARY (MHz):\n")
            f.write("--------------------\n")
            df_timing = pd.DataFrame({impl: {k: 1000/v if v > 0 else 0 for k, v in t.items()}
                                    for impl, t in timing.items()})
            f.write(df_timing.round(3).to_string())
            f.write("\n\n")
        
        # Write Latency Summary
        if latency:
            f.write("LATENCY SUMMARY (cycles):\n")
            f.write("------------------------\n")
            df_latency = pd.Series(latency, name='Latency')
            f.write(df_latency.to_string())
            f.write("\n\n")
        
        # Write a summary of the report
        f.write("===============================================\n")
        f.write(f"End of Report\n")
        f.write("===============================================\n")
    
    print(f"Report data saved to '{output_file}'")

def main():
    # ...existing code...

    if all_resources and all_timing:
        compare_resources(all_resources)
        compare_timing(all_timing)
        create_timing_resource_plot(all_resources, all_timing)

        print("\nResource Utilization Summary:")
        df_resources = pd.DataFrame(all_resources)
        print(df_resources.round(2))
        
        print("\nTiming Summary (MHz):")
        df_timing = pd.DataFrame({impl: {k: 1000/v if v > 0 else 0 for k, v in timing.items()}
                                for impl, timing in all_timing.items()})
        print(df_timing.round(3))

    if all_latency:
        compare_latency(all_latency)
        print("\nLatency Summary (cycles):")
        df_latency = pd.Series(all_latency, name='Latency')
        print(df_latency)
    else:
        print("No latency data was collected from the reports.")
    
    # Save all report data to a text file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"implementation_report_{timestamp}.txt"
    save_report_to_txt(all_resources, all_timing, all_latency, base_dir, output_filename)

if __name__ == "__main__":
    main()
````

The changes I've made:
1. Added the datetime module import at the top
2. Created a new `save_report_to_txt()` function that formats and writes all report data to a text file
3. Modified the main function to call this new function after processing the reports
4. Added a timestamp to the filename to make each report unique and identifiable
5. Included information about the base directory in the report header for context

The text file will contain all the same data that's printed to the console, but in a format that can be easily saved, shared, and compared with other reports.

