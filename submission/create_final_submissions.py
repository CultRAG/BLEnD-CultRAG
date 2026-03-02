#!/usr/bin/env python3
"""
Convert all combined prediction TSV files to one-hot encoded format for final submission.
"""

import os
from pathlib import Path

def convert_to_onehot(input_file, output_file):
    """Convert predictions to one-hot encoded format"""
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Start with header row
    output_lines = ["id\tA\tB\tC\tD\n"]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip header row if present (exact match to avoid skipping Indonesian IDs like id-ID_0001)
        if line in ('id,prediction', 'ID,prediction', 'id\tprediction', 'ID\tprediction'):
            continue
            
        parts = line.split('\t')
        if len(parts) < 1:
            print(f"Warning: Skipping malformed line: {line}")
            continue
        
        # Extract ONLY id (first column, before any comma)
        question_id = parts[0].split(',')[0] if ',' in parts[0] else parts[0]
        
        # Extract prediction (second column, or first char after comma in first column)
        if len(parts) > 1:
            prediction = parts[1].strip().upper()
        elif ',' in parts[0]:
            prediction = parts[0].split(',')[1].strip().upper()
        else:
            prediction = ''
        
        # Default empty predictions to 'A'
        if not prediction:
            prediction = 'A'
        
        # Create one-hot encoding
        a = '1' if prediction == 'A' else '0'
        b = '1' if prediction == 'B' else '0'
        c = '1' if prediction == 'C' else '0'
        d = '1' if prediction == 'D' else '0'
        
        output_lines.append(f"{question_id}\t{a}\t{b}\t{c}\t{d}\n")
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    return len(output_lines) - 1  # Return count excluding header


# Paths
input_dir = Path("combined_predictions")
output_dir = Path("final_submission")

# Create output directory
output_dir.mkdir(exist_ok=True)

# Get all combined prediction files
prediction_files = list(input_dir.glob("*.tsv"))

print("=" * 60)
print("Converting predictions to one-hot encoded format")
print("=" * 60)

for pred_file in sorted(prediction_files):
    # Create output filename (remove '_combined' suffix)
    output_name = pred_file.stem.replace("_combined", "") + "_onehot.tsv"
    output_file = output_dir / output_name
    
    # Convert
    count = convert_to_onehot(pred_file, output_file)
    print(f"✓ {pred_file.name} -> {output_name} ({count} rows)")

print("=" * 60)
print(f"All files saved in: {output_dir}")
print("=" * 60)
