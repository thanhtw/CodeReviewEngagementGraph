#!/usr/bin/env python3
"""
=============================================================================
Data Processing Pipeline for Review Graph Visualization
=============================================================================

This script orchestrates the complete data processing pipeline to generate
visualization data for the Review Engagement Graph.

Pipeline Steps:
---------------
Step 1: CSV to JSON Conversion
    - Input:  data/processing/<input>.csv
    - Output: data/processing/<output>.json
    - Script: data/processing/csv_to_json_converter.py

Step 2: Data Organization
    - Input:  data/processing/<converted>.json
    - Output: utils/processed_data/selected_assignments_addscore.json
    - Script: utils/dataOrganize_select.py

Step 3: ML Inference (3-Label Classification)
    - Input:  utils/processed_data/selected_assignments_addscore.json
    - Output: function/3labeled_processed_totalData.json
    - Script: function/main.py

Final Output:
-------------
The generated JSON file (function/3labeled_processed_totalData.json) is used by:
    - static/graph.html (main visualization page)
    - static/main_graph.js (network graph)
    - static/labelChart.js (label distribution charts)
    - static/bubbleChart.js (bubble chart)

Usage:
------
    python run_pipeline.py                    # Run full pipeline with defaults
    python run_pipeline.py --input mydata.csv # Use custom input file
    python run_pipeline.py --step 2           # Start from step 2
    python run_pipeline.py --help             # Show help

Author: ReviewGraphVisualization Team
=============================================================================
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Default file paths
DEFAULT_CONFIG = {
    "csv_input": "data64_inference.csv",
    "json_converted": "data64_inference_converted.json",
    "json_organized": "selected_assignments_addscore.json",
    "json_labeled": "3labeled_processed_totalData.json",
    "hw_range": (1, 7),  # HW1 to HW7
}


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step_num: int, description: str):
    """Print step information."""
    print(f"\n{'─' * 60}")
    print(f"  Step {step_num}: {description}")
    print(f"{'─' * 60}")


def run_command(cmd: list, cwd: str = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Command failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: Python not found. Please ensure Python is installed.")
        return False


def step1_csv_to_json(csv_input: str, json_output: str) -> bool:
    """
    Step 1: Convert CSV to JSON format.
    
    Args:
        csv_input: Input CSV filename (in data/processing/)
        json_output: Output JSON filename (in data/processing/)
    
    Returns:
        True if successful, False otherwise
    """
    print_step(1, "CSV to JSON Conversion")
    
    script_path = PROJECT_ROOT / "data" / "processing" / "csv_to_json_converter.py"
    input_path = PROJECT_ROOT / "data" / "processing" / csv_input
    output_path = PROJECT_ROOT / "data" / "processing" / json_output
    
    print(f"  📄 Input:  {input_path}")
    print(f"  📄 Output: {output_path}")
    
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        return False
    
    cmd = [
        sys.executable, str(script_path),
        "--input", str(input_path),
        "--output", str(output_path)
    ]
    
    success = run_command(cmd)
    if success:
        print(f"✅ Step 1 completed: CSV converted to JSON")
    return success


def step2_organize_data(json_input: str, json_output: str, hw_start: int = 1, hw_end: int = 7) -> bool:
    """
    Step 2: Organize and filter homework data.
    
    Args:
        json_input: Input JSON filename (in data/processing/)
        json_output: Output JSON filename (in utils/processed_data/)
        hw_start: Starting homework number
        hw_end: Ending homework number
    
    Returns:
        True if successful, False otherwise
    """
    print_step(2, "Data Organization")
    
    input_path = PROJECT_ROOT / "data" / "processing" / json_input
    output_dir = PROJECT_ROOT / "utils" / "processed_data"
    output_path = output_dir / json_output
    
    print(f"  📄 Input:  {input_path}")
    print(f"  📄 Output: {output_path}")
    print(f"  📊 HW Range: HW{hw_start} ~ HW{hw_end}")
    
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        return False
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run the organization script inline (to pass parameters)
    try:
        # Import and run the organize function
        sys.path.insert(0, str(PROJECT_ROOT / "utils"))
        from dataOrganize_select import read_json_file, organize_data, filter_assignments, write_json_file
        
        input_data = read_json_file(str(input_path))
        organized_data = organize_data(input_data)
        selected_data = filter_assignments(organized_data, hw_start, hw_end)
        write_json_file(selected_data, str(output_path))
        
        print(f"✅ Step 2 completed: Data organized and filtered")
        return True
        
    except Exception as e:
        print(f"❌ Error in data organization: {e}")
        return False


def step3_ml_inference(json_input: str, json_output: str) -> bool:
    """
    Step 3: Run ML inference to add 3-label predictions.
    
    Args:
        json_input: Input JSON filename (in utils/processed_data/)
        json_output: Output JSON filename (in function/)
    
    Returns:
        True if successful, False otherwise
    """
    print_step(3, "ML Inference (3-Label Classification)")
    
    input_path = PROJECT_ROOT / "utils" / "processed_data" / json_input
    output_path = PROJECT_ROOT / "function" / json_output
    model_path = PROJECT_ROOT / "models" / "bert_3label_finetuned_model"
    
    print(f"  📄 Input:  {input_path}")
    print(f"  📄 Output: {output_path}")
    print(f"  🤖 Model:  {model_path}")
    
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        return False
    
    if not model_path.exists():
        print(f"⚠️  Warning: Model not found at {model_path}")
        print("   Please ensure the BERT model is downloaded.")
        return False
    
    # Run main.py with proper paths
    script_path = PROJECT_ROOT / "function" / "main.py"
    
    # Update main.py paths temporarily by running with modified environment
    cmd = [sys.executable, str(script_path)]
    
    # Change to function directory for relative imports
    success = run_command(cmd, cwd=str(PROJECT_ROOT / "function"))
    
    if success:
        print(f"✅ Step 3 completed: ML inference done")
        print(f"\n📊 Output file ready for visualization:")
        print(f"   {output_path}")
    return success


def run_pipeline(args):
    """Run the complete pipeline or specific steps."""
    
    print_header("Review Graph Visualization - Data Pipeline")
    print(f"\n📂 Project Root: {PROJECT_ROOT}")
    
    start_step = args.step if args.step else 1
    csv_input = args.input if args.input else DEFAULT_CONFIG["csv_input"]
    
    # Determine intermediate file names
    json_converted = DEFAULT_CONFIG["json_converted"]
    json_organized = DEFAULT_CONFIG["json_organized"]
    json_labeled = DEFAULT_CONFIG["json_labeled"]
    hw_start, hw_end = DEFAULT_CONFIG["hw_range"]
    
    print(f"\n📋 Pipeline Configuration:")
    print(f"   Starting from Step: {start_step}")
    print(f"   CSV Input: {csv_input}")
    print(f"   HW Range: HW{hw_start} ~ HW{hw_end}")
    
    success = True
    
    # Step 1: CSV to JSON
    if start_step <= 1 and success:
        success = step1_csv_to_json(csv_input, json_converted)
    
    # Step 2: Organize Data
    if start_step <= 2 and success:
        success = step2_organize_data(json_converted, json_organized, hw_start, hw_end)
    
    # Step 3: ML Inference
    if start_step <= 3 and success:
        success = step3_ml_inference(json_organized, json_labeled)
    
    # Final Summary
    print_header("Pipeline Summary")
    
    if success:
        print("\n✅ Pipeline completed successfully!")
        print("\n📊 To view the visualization:")
        print("   1. Start the server: python server_fixed.py")
        print("   2. Open browser: http://localhost:8001/static/graph.html")
    else:
        print("\n❌ Pipeline failed. Please check the errors above.")
        return 1
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Data Processing Pipeline for Review Graph Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                     # Run full pipeline
  python run_pipeline.py --input mydata.csv  # Use custom CSV input
  python run_pipeline.py --step 2            # Start from step 2
  python run_pipeline.py --step 3            # Only run ML inference
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input CSV file name (in data/processing/)"
    )
    
    parser.add_argument(
        "--step", "-s",
        type=int,
        choices=[1, 2, 3],
        help="Start from specific step (1=CSV conversion, 2=Data organize, 3=ML inference)"
    )
    
    args = parser.parse_args()
    sys.exit(run_pipeline(args))


if __name__ == "__main__":
    main()
