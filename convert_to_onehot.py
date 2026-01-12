#!/usr/bin/env python3
"""
Convert prediction TSV from format:
    id    prediction
    ms-SG_001    C

To one-hot encoded format:
    id    A    B    C    D
    ms-SG_001    0    0    1    0
"""

import sys
import os

def convert_to_onehot(input_file, output_file=None):
    """Convert predictions to one-hot encoded format"""
    
    # Determine output filename
    if output_file is None:
        output_file = "track_2_mcq_prediction.tsv"
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Start with header row
    output_lines = ["id\tA\tB\tC\tD\n"]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip header row if present
        if line.startswith('id') or line.startswith('ID'):
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
            # If commas in first column like "ms-SG_001,C,C,True"
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
        
        # Output ONLY: id, A, B, C, D (no other columns from input)
        output_lines.append(f"{question_id}\t{a}\t{b}\t{c}\t{d}\n")
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✅ Converted {len(output_lines)-1} predictions")
    print(f"   Input:  {input_file}")
    print(f"   Output: {output_file}")
    
    return output_file

if __name__ == "__main__":
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURE INPUT FILE HERE
    # ═══════════════════════════════════════════════════════════════
    input_file = "output-with-v5\kaggle\working\predictions_rag_basic.csv"  # Change this to your input file
    output_file = "track_2_mcq_prediction.tsv"  # Output filename
    # ═══════════════════════════════════════════════════════════════
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        print(f"   Please update the input_file path in the script")
        sys.exit(1)
    
    convert_to_onehot(input_file, output_file)
