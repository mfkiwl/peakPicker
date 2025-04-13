import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import datetime  # Add this import for timestamping reports

def parse_latency_report(report_file):
    """Parse latency report file and extract total execution time."""
    try:
        with open(report_file, 'r') as f:
            content = f.read()
            # Find the TOTAL_EXECUTE_TIME value
            # import re
            match = re.search(r'\$TOTAL_EXECUTE_TIME = "(\d+)"', content)
            if match:
                return int(match.group(1))
    except Exception as e:
        print(f"Error parsing latency report {report_file}: {e}")
    return None

def find_latency_reports(base_dir):
    """Find all latency report files recursively."""
    # Generic pattern to find latency reports
    pattern = os.path.join(base_dir, '**/sim/report/verilog/lat.rpt')
    reports = glob.glob(pattern, recursive=True)
    reports.sort()
    print(f"Found {len(reports)} latency reports")
    return reports

def compare_latency(reports_data):
    """Create comparative visualization of latency results."""
    if not reports_data:
        print("No latency data to visualize")
        return

    plt.figure(figsize=(10, 6))
    implementations = list(reports_data.keys())
    latencies = list(reports_data.values())
    
    bars = plt.bar(implementations, latencies, color='purple', alpha=0.6)
    plt.title('Latency Comparison')
    plt.xlabel('Implementation')
    plt.ylabel('Total Execute Time (cycles)')
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('latency_comparison.png')
    plt.close()

def find_impl_reports(base_dir):
    """Find all implementation report files recursively."""
    # More generic pattern to find implementation reports
    pattern = os.path.join(base_dir, '**/impl/report/verilog/export_impl.rpt')
    reports = glob.glob(pattern, recursive=True)
    
    # Sort the reports to ensure consistent ordering
    reports.sort()
    
    if not reports:
        print(f"No implementation reports found in {base_dir}")
        print(f"Searched pattern: {pattern}")
    else:
        print(f"Found {len(reports)} implementation reports:")
        for report in reports:
            print(f"  - {report}")
            
    return reports

def parse_impl_report(report_file):
    """Parses the Vivado Place & Route report file."""
    resource_summary = {}
    timing_summary = {}

    with open(report_file, 'r') as f:
        content = f.read()

    # Extract Resource Summary
    resource_section = re.search(r'== Place & Route Resource Summary.*?\n(.*?)\n\n', content, re.DOTALL)
    if resource_section:
        resource_text = resource_section.group(1)
        resource_pairs = [
            ('LUT', r'LUT:\s*(\d+)'),
            ('FF', r'FF:\s*(\d+)'),
            ('DSP', r'DSP:\s*(\d+)'),
            ('BRAM', r'BRAM:\s*(\d+)'),
            ('URAM', r'URAM:\s*(\d+)')
            # ('SRL', r'SRL:\s*(\d+)')
        ]
        for name, pattern in resource_pairs:
            match = re.search(pattern, resource_text)
            if match:
                resource_summary[name] = int(match.group(1))

    # Extract Timing Summary
    timing_section = re.search(r'== Place & Route Timing Summary.*?\| Target\s*\|\s*[\d.]+\s*\|(.*?)\+\-', content, re.DOTALL)
    if timing_section:
        timing_text = timing_section.group(1)
        timing_pairs = [
            ('Target', r'\| Target\s*\|\s*([\d.]+)\s*\|'),
            ('Post-Synthesis', r'\| Post-Synthesis\s*\|\s*([\d.]+)\s*\|'),
            ('Post-Route', r'\| Post-Route\s*\|\s*([\d.]+)\s*\|')
        ]
        for name, pattern in timing_pairs:
            match = re.search(pattern, content)
            if match:
                timing_summary[name] = float(match.group(1))

    return resource_summary, timing_summary

def compare_resources(reports_data):
    """Create comparative visualization of resource utilization."""
    if not reports_data:
        print("No resource data to visualize")
        return
        
    df = pd.DataFrame(reports_data).T
    
    # Create a bar plot
    ax = df.plot(kind='bar', figsize=(12, 6), width=0.8)
    plt.title('Resource Utilization Comparison')
    plt.xlabel('Implementation')
    plt.ylabel('Resource Count')
    plt.legend(title='Resource Type')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('resource_comparison.png')
    print(f"Resource comparison saved as 'resource_comparison.png'")
    plt.close()

def compare_timing(reports_data):
    """Create comparative visualization of timing results."""
    if not reports_data:
        print("No timing data to visualize")
        return
        
    # Convert timing data to MHz
    mhz_data = {impl: {k: 1000/v if v > 0 else 0 for k, v in timing.items()}
                for impl, timing in reports_data.items()}
    df = pd.DataFrame(mhz_data).T
    
    # Create a bar plot
    ax = df['Post-Route'].plot(kind='bar', figsize=(10, 6), color='green', alpha=0.6)
    if 'Target' in df.columns and len(df['Target']) > 0:
        plt.axhline(y=df['Target'].iloc[0], color='r', linestyle='--', label='Target')
    plt.title('Post-Route Timing Comparison')
    plt.xlabel('Implementation')
    plt.ylabel('Frequency (MHz)')
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('timing_comparison.png')
    print(f"Timing comparison saved as 'timing_comparison.png'")
    plt.close()

def create_timing_resource_plot(reports_data_resources, reports_data_timing):
    """Create a plot comparing timing vs resource utilization."""
    if not reports_data_resources or not reports_data_timing:
        print("Insufficient data for timing vs resources plot")
        return
        
    # Convert timing data to MHz for x-axis
    mhz_data = {impl: 1000/timing['Post-Route'] if timing['Post-Route'] > 0 else 0 
                for impl, timing in reports_data_timing.items()}
    
    # Prepare data
    implementations = list(mhz_data.keys())
    frequencies = list(mhz_data.values())
    lut_values = [reports_data_resources[impl]['LUT'] for impl in implementations]
    bram_values = [reports_data_resources[impl]['BRAM'] for impl in implementations]

    # Create the figure and axis
    plt.figure(figsize=(12, 7))

    # Calculate circle sizes based on BRAM values
    # Scale BRAM values to reasonable circle sizes (min 100, max 1000)
    min_bram = min(bram_values)
    max_bram = max(bram_values)
    if min_bram != max_bram:
        scaled_sizes = [(x - min_bram) * 900 / (max_bram - min_bram) + 100 for x in bram_values]
    else:
        scaled_sizes = [500 for x in bram_values]  # Use medium size if all values are the same

    # Plot LUT with circle sizes representing BRAM
    plt.scatter(frequencies, lut_values, s=scaled_sizes, alpha=0.6, 
                color='tab:blue', label='LUT (circle size = BRAM count)')

    # Add implementation labels to points
    for i, impl in enumerate(implementations):
        plt.annotate(f'{impl}\nBRAM: {bram_values[i]}', 
                    (frequencies[i], lut_values[i]), 
                    xytext=(5, 5), textcoords='offset points')

    plt.xlabel('Frequency (MHz)')
    plt.ylabel('LUT Count')
    plt.title('Resource Utilization vs Frequency\n(Circle size represents BRAM usage)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('timing_vs_resources.png')
    plt.close()

def extract_impl_name(report_file):
    """Extract implementation name from report file path."""
    path = Path(report_file)
    
    # Try to find solution or project directory names
    parts = path.parts
    
    # First try to find project-specific directories
    for keyword in ['proj_', 'solution']:
        for i, part in enumerate(parts):
            if keyword in part and i > 0:
                return parts[i-1]
    
    # If not found, use parent directory name of the implementation report
    # Go up 4 levels: impl/report/verilog/export_impl.rpt
    return path.parents[3].name

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
    # Set the base directory to the specific path
    base_dir = "/home/jielei/Projects/UTS/peakPicker/HDLCoder/opt4_HLS"
    print(f"Analyzing reports in: {base_dir}")
    
    # Find all reports
    impl_reports = find_impl_reports(base_dir)
    latency_reports = find_latency_reports(base_dir)
    
    if not impl_reports:
        print("No implementation reports found!")
        return

    all_resources = {}
    all_timing = {}
    all_latency = {}

    # Process implementation reports
    for report_file in impl_reports:
        impl_name = extract_impl_name(report_file)
        print(f"Processing implementation: {impl_name}")
        resource_data, timing_data = parse_impl_report(report_file)
        all_resources[impl_name] = resource_data
        all_timing[impl_name] = timing_data

    # Process latency reports
    for report_file in latency_reports:
        impl_name = extract_impl_name(report_file)
        latency = parse_latency_report(report_file)
        if latency is not None:
            all_latency[impl_name] = latency

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
