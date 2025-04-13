#!/usr/bin/env python3

import argparse
import os
import sys
import requests
import json
import openai
import google.generativeai as genai
from dotenv import load_dotenv

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate HLS C++ code from MATLAB reference using LLM')
    parser.add_argument('--matlab_file', nargs='+', required=True, 
                        help='Path to MATLAB reference file(s)')
    parser.add_argument('--prompt', required=True, 
                        help='Path to prompt template file')
    parser.add_argument('--output_dir', default='implementations', 
                        help='Directory to save generated HLS code')
    parser.add_argument('--model', default='gemini-2.0-pro-exp', 
                        help='LLM model to use (default: gemini-2.0-pro-exp)')
    parser.add_argument('--api_key', 
                        help='API key for LLM service (or set GEMINI_API_KEY environment variable)')
    return parser.parse_args()

def read_file(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def create_prompt(matlab_files, prompt_template):
    """Create the final prompt by combining MATLAB code with the template."""
    matlab_code = ""
    for file_path in matlab_files:
        matlab_code += f"\n## File: {os.path.basename(file_path)}\n```matlab\n{read_file(file_path)}\n```\n"
    
    # Add specific instructions for testbench generation
    testbench_instructions = """
Please generate the following files:
1. A header file (*.hpp) with the appropriate declarations
2. An implementation file (*.cpp) with the HLS implementation
3. A testbench file (*_tb.cpp) that:
   - Reads input data from *_in.txt files
   - Compares output with reference data from *_ref.txt files
   - Outputs results to *_out.txt files
   - Includes proper verification and error reporting

Follow the structure of the example files provided."""
    
    # Replace placeholder in template if it exists, otherwise append MATLAB code
    if "{{MATLAB_CODE}}" in prompt_template:
        prompt = prompt_template.replace("{{MATLAB_CODE}}", matlab_code)
    else:
        prompt = f"{prompt_template}\n\n# MATLAB Reference Implementation\n{matlab_code}"
    
    # Add testbench instructions
    prompt += "\n\n" + testbench_instructions
    
    return prompt

def call_openai_api(prompt, model):
    """Call OpenAI API with the given prompt."""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert FPGA developer specializing in HLS C++ implementations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more deterministic output
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        sys.exit(1)

def call_anthropic_api(prompt, api_key):
    """Call Anthropic's Claude API with the given prompt."""
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json"
    }
    data = {
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "model": "claude-3-sonnet-20240229",  # Adjust model as needed
        "max_tokens_to_sample": 4000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/complete",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        return response.json()["completion"].strip()
    except Exception as e:
        print(f"Error calling Anthropic API: {e}")
        sys.exit(1)

def call_gemini_api(prompt, api_key, model_name="gemini-2.0-pro-exp"):
    """Call Google's Gemini API with the given prompt."""
    try:
        genai.configure(api_key=api_key)
        # Use the specified model from arguments
        model = genai.GenerativeModel(model_name)
        
        # Add system instructions to the beginning of the prompt
        system_instruction = "You are an expert FPGA developer specializing in HLS C++ implementations."
        full_prompt = f"{system_instruction}\n\n{prompt}"
        
        # Generate content with a single prompt
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 4000,
            }
        )
        
        # Check if response is blocked or empty
        if not response.candidates:
            print("Warning: Gemini API returned empty response.")
            if hasattr(response, 'prompt_feedback'):
                print(f"Prompt feedback: {response.prompt_feedback}")
            return "No response generated. The prompt may have been filtered."
            
        # Safe access to text
        return response.text
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        sys.exit(1)

def extract_code_blocks(llm_response, component_name):
    """Extract code blocks from LLM response."""
    code_blocks = {}
    current_file = None
    collecting = False
    current_block = []
    
    # Add expected file patterns for better detection
    expected_files = [
        f"{component_name}.hpp",
        f"{component_name}.cpp",
        f"{component_name}_tb.cpp"
    ]
    
    for line in llm_response.split('\n'):
        if line.startswith('```') and not collecting:
            collecting = True
            continue
        elif line.startswith('```') and collecting:
            collecting = False
            if current_file and current_block:
                code_blocks[current_file] = '\n'.join(current_block)
                current_block = []
            continue
            
        if collecting:
            # Check for file indicators in comments
            if line.strip().startswith('// File:') or line.strip().startswith('// filename:'):
                current_file = line.split(':', 1)[1].strip()
            elif not current_file:
                # Try to extract filename from line for any of our expected file patterns
                for pattern in expected_files:
                    if pattern in line:
                        for word in line.split():
                            if pattern in word:
                                current_file = pattern
                                break
                        if current_file:
                            break
            current_block.append(line)
    
    # Also look for file headers in the response
    lines = llm_response.split('\n')
    for i, line in enumerate(lines):
        if '```cpp' in line or '```c++' in line:
            # Look for a filename in lines above
            for j in range(max(0, i-5), i):
                prev_line = lines[j].lower()
                for pattern in expected_files:
                    if pattern.lower() in prev_line:
                        # Extract filename using detected pattern
                        current_file = pattern
                        break
    
    # If we didn't find specific files, use file content heuristics
    if not any(file.endswith('.hpp') for file in code_blocks.keys()):
        h_blocks = [block for file, block in code_blocks.items() 
                   if '#include' in block and ('class' in block or '#ifndef' in block)]
        if h_blocks:
            code_blocks[f'{component_name}.hpp'] = h_blocks[0]
    
    if not any(file.endswith('.cpp') and not file.endswith('_tb.cpp') for file in code_blocks.keys()):
        cpp_blocks = [block for file, block in code_blocks.items() 
                     if 'void ' + component_name in block or component_name + '(' in block]
        if cpp_blocks:
            code_blocks[f'{component_name}.cpp'] = cpp_blocks[0]
    
    if not any(file.endswith('_tb.cpp') for file in code_blocks.keys()):
        tb_blocks = [block for file, block in code_blocks.items() 
                    if 'int main' in block and ('test' in block.lower() or 'compare' in block.lower())]
        if tb_blocks:
            code_blocks[f'{component_name}_tb.cpp'] = tb_blocks[0]
    
    return code_blocks

def save_code_to_files(code_blocks, output_dir):
    """Save extracted code blocks to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    files_saved = []
    for filename, content in code_blocks.items():
        # Clean up filename if needed
        clean_filename = os.path.basename(filename.strip())
        file_path = os.path.join(output_dir, clean_filename)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        files_saved.append(file_path)
        print(f"Saved: {file_path}")
    
    return files_saved

def main():
    args = parse_arguments()
    
    # Load environment variables for API keys
    load_dotenv()
    
    # Set API key from args or environment variable
    api_key = args.api_key
    if not api_key:
        if "gemini" in args.model.lower():
            api_key = os.environ.get('GEMINI_API_KEY')
        else:
            api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            print("Error: API key not provided. Use --api_key or set appropriate environment variable.")
            sys.exit(1)
    
    # Read MATLAB files
    matlab_files = [read_file(file) for file in args.matlab_file]
    
    # Read prompt template
    prompt_template = read_file(args.prompt)
    
    # Create the full prompt
    full_prompt = create_prompt(args.matlab_file, prompt_template)
    
    # Determine output directory and component name
    component_name = os.path.basename(args.matlab_file[0]).split('.')[0]
    output_dir = os.path.join(args.output_dir, component_name)
    
    print(f"Generating HLS code for {component_name}...")
    print(f"Using model: {args.model}")
    
    # Call appropriate LLM API based on model name
    if "gemini" in args.model.lower():
        llm_response = call_gemini_api(full_prompt, api_key, args.model)
    elif "claude" in args.model.lower():
        llm_response = call_anthropic_api(full_prompt, api_key)
    else:
        openai.api_key = api_key
        llm_response = call_openai_api(full_prompt, args.model)
    
    # Extract code blocks from response
    code_blocks = extract_code_blocks(llm_response, component_name)
    
    if not code_blocks:
        print("Warning: No code blocks detected in the LLM response.")
        # Save the full response as a reference
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "llm_response.md"), 'w') as f:
            f.write(llm_response)
        print(f"Saved full response to {os.path.join(output_dir, 'llm_response.md')}")
        sys.exit(1)
    
    # Save code to files
    saved_files = save_code_to_files(code_blocks, output_dir)
    
    print("\nHLS code generation complete!")
    print(f"Files generated: {len(saved_files)}")
    print(f"Output directory: {output_dir}")
    
    # Save the full LLM response for reference
    with open(os.path.join(output_dir, "llm_response.md"), 'w') as f:
        f.write(llm_response)
    
    print("\nNext steps:")
    print(f"cd {output_dir}")
    print("make csim  # Run C simulation")

if __name__ == "__main__":
    main()
