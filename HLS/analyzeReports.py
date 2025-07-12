import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def parse_latency_report(report_file):
    """Parse latency report file and extract total execution time."""
    try:
        with open(report_file, 'r') as f:
            content = f.read()
            # Find the MAX_LATENCY value
            # import re
            match = re.search(r'\$MAX_LATENCY = "(\d+)"', content)
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
        # resource_pairs = [
        #     ('LUT', r'LUT:\s*(\d+)'),
        #     ('FF', r'FF:\s*(\d+)'),
        #     ('DSP', r'DSP:\s*(\d+)'),
        #     ('BRAM', r'BRAM:\s*(\d+)'),
        #     ('URAM', r'URAM:\s*(\d+)')
        #     ('SRL', r'SRL:\s*(\d+)')
        # ]
        resource_pairs = [
            ('LUT', r'LUT:\s*(\d+)'),
            ('FF', r'FF:\s*(\d+)'),
            ('BRAM', r'BRAM:\s*(\d+)')
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
        
    # Convert timing data to MHz for x-axis, handling missing keys
    mhz_data = {}
    for impl, timing in reports_data_timing.items():
        if 'Post-Route' in timing and timing['Post-Route'] > 0:
            mhz_data[impl] = 1000/timing['Post-Route']
        else:
            print(f"Warning: Missing or invalid 'Post-Route' timing data for {impl}, skipping in plot")
    
    if not mhz_data:
        print("No valid timing data available for timing vs resources plot")
        return
    
    # Prepare data
    implementations = list(mhz_data.keys())
    frequencies = list(mhz_data.values())
    
    # Filter resource data to match available timing data
    lut_values = []
    bram_values = []
    for impl in implementations:
        if impl in reports_data_resources:
            lut_values.append(reports_data_resources[impl].get('LUT', 0))
            bram_values.append(reports_data_resources[impl].get('BRAM', 0))
        else:
            print(f"Warning: Missing resource data for {impl}, using 0 values")
            lut_values.append(0)
            bram_values.append(0)

    # Create the figure and axis
    plt.figure(figsize=(12, 7))

    # Calculate circle sizes based on BRAM values
    # Scale BRAM values to reasonable circle sizes (min 100, max 1000)
    min_bram = min(bram_values) if bram_values else 0
    max_bram = max(bram_values) if bram_values else 1
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

def find_txt_reports(base_dir):
    """Find all TXT report files in the specified directory."""
    pattern = os.path.join(base_dir, '*.txt')
    reports = glob.glob(pattern)
    reports.sort()
    print(f"Found {len(reports)} TXT reports in {base_dir}")
    for report in reports:
        print(f"  - {report}")
    return reports

def parse_txt_report(report_file):
    """Parse a TXT report file and extract resource, timing, and latency data."""
    resource_summary = {}
    timing_summary = {}
    latency = None

    try:
        with open(report_file, 'r') as f:
            content = f.read()

        # Extract implementation name from the filename
        impl_name = os.path.splitext(os.path.basename(report_file))[0]

        # Find project name (column header in report)
        project_name_match = re.search(r'RESOURCE UTILIZATION SUMMARY:.*?\n\s+(\w+)', content, re.DOTALL)
        if project_name_match:
            project_name = project_name_match.group(1)
        else:
            project_name = 'unknown'

        # Extract Resource Summary
        resource_section = re.search(r'RESOURCE UTILIZATION SUMMARY:(.*?)TIMING SUMMARY', content, re.DOTALL)
        if resource_section:
            resource_text = resource_section.group(1)
            # for resource in ['LUT', 'FF', 'DSP', 'BRAM', 'URAM']:
            for resource in ['LUT', 'FF', 'BRAM']:
                match = re.search(rf'{resource}\s+(\d+)', resource_text)
                if match:
                    resource_summary[resource] = int(match.group(1))

        # Extract Timing Summary - fixed pattern to better match the TXT format
        timing_section = re.search(r'TIMING SUMMARY \(MHz\):(.*?)LATENCY SUMMARY', content, re.DOTALL)
        if timing_section:
            timing_text = timing_section.group(1)
            # Clear previous pattern that might match resource values
            timing_pairs = [
                ('Target', r'Target\s+([\d.]+)'),
                ('Post-Synthesis', r'Post-Synthesis\s+([\d.]+)'),
                ('Post-Route', r'Post-Route\s+([\d.]+)')
            ]
            
            for timing_name, pattern in timing_pairs:
                match = re.search(pattern, timing_text)
                if match:
                    try:
                        timing_summary[timing_name] = float(match.group(1))
                    except ValueError:
                        print(f"Warning: Invalid timing value for {timing_name} in {report_file}")
                        timing_summary[timing_name] = 0.0
                else:
                    print(f"Warning: '{timing_name}' not found in timing summary for {report_file}")

        # Extract Latency
        latency_match = re.search(r'LATENCY SUMMARY \(cycles\):\n.*?(\w+)\s+(\d+)', content, re.DOTALL)
        if latency_match:
            try:
                latency = int(latency_match.group(2))
            except ValueError:
                print(f"Warning: Invalid latency value in {report_file}")
                latency = 0

        return impl_name, resource_summary, timing_summary, latency, project_name
    except Exception as e:
        print(f"Error parsing TXT report {report_file}: {e}")
        return None, {}, {}, None, None

def write_report_summary(all_resources, all_timing, all_latency, output_file="fpga_implementation_summary.txt"):
    """Write all report data to a TXT file."""
    with open(output_file, 'w') as f:
        f.write("===============================================\n")
        f.write("FPGA Implementation Report Summary\n")
        f.write(f"Generated on: {pd.Timestamp.now()}\n")
        f.write("===============================================\n\n")

        # Write Resource Summary
        f.write("RESOURCE UTILIZATION SUMMARY:\n")
        f.write("-----------------------------\n")
        if all_resources:
            df_resources = pd.DataFrame(all_resources)
            f.write(df_resources.to_string())
            f.write("\n\n")
        else:
            f.write("No resource data available\n\n")

        # Write Timing Summary
        f.write("TIMING SUMMARY (MHz):\n")
        f.write("--------------------\n")
        if all_timing:
            df_timing = pd.DataFrame({impl: {k: 1000/v if v > 0 else 0 for k, v in timing.items()}
                                    for impl, timing in all_timing.items()})
            f.write(df_timing.round(3).to_string())
            f.write("\n\n")
        else:
            f.write("No timing data available\n\n")

        # Write Latency Summary
        f.write("LATENCY SUMMARY (cycles):\n")
        f.write("------------------------\n")
        if all_latency:
            df_latency = pd.Series(all_latency, name='Latency')
            f.write(df_latency.to_string())
            f.write("\n\n")
        else:
            f.write("No latency data available\n\n")

        f.write("===============================================\n")
        f.write("End of Report\n")
        f.write("===============================================\n")

    print(f"Report summary written to {output_file}")

def main():
    # Set the base directories
    hls_base_dir = "/home/jielei/Projects/UTS/peakPicker/HLS"
    hdlcoder_base_dir = "/home/jielei/Projects/UTS/peakPicker/HDLCoder"
    print(f"Analyzing reports in: {hls_base_dir} and {hdlcoder_base_dir}")
    
    # Find all reports
    impl_reports = find_impl_reports(hls_base_dir)
    latency_reports = find_latency_reports(hls_base_dir)
    txt_reports = find_txt_reports(hdlcoder_base_dir)
    
    if not impl_reports and not txt_reports:
        print("No reports found!")
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

    # Process TXT reports
    for report_file in txt_reports:
        impl_name, resource_data, timing_data, latency, project_name = parse_txt_report(report_file)
        if impl_name:
            print(f"Processing TXT report: {impl_name}")
            # Use project name as a suffix to differentiate implementations
            impl_key = f"{impl_name}"
            if resource_data:
                all_resources[impl_key] = resource_data
            if timing_data:
                all_timing[impl_key] = timing_data
            if latency is not None:
                all_latency[impl_key] = latency

    # Write combined data to TXT file
    write_report_summary(all_resources, all_timing, all_latency, "fpga_implementation_summary.txt")

    # Create visualizations
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

if __name__ == "__main__":
    main()
