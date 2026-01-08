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
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_onehot{ext}"
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process and convert
    output_lines = ["id\tA\tB\tC\tD\n"]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        if len(parts) != 2:
            print(f"Warning: Skipping malformed line: {line}")
            continue
        
        question_id, prediction = parts[0], parts[1].upper()
        
        # Create one-hot encoding
        a = '1' if prediction == 'A' else '0'
        b = '1' if prediction == 'B' else '0'
        c = '1' if prediction == 'C' else '0'
        d = '1' if prediction == 'D' else '0'
        
        output_lines.append(f"{question_id}\t{a}\t{b}\t{c}\t{d}\n")
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✅ Converted {len(output_lines)-1} predictions")
    print(f"   Input:  {input_file}")
    print(f"   Output: {output_file}")
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_to_onehot.py <input_file> [output_file]")
        print("\nExample:")
        print("  python convert_to_onehot.py predictions_rag_rrf_k3.tsv")
        print("  python convert_to_onehot.py predictions_rag_rrf_k3.tsv output.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    
    convert_to_onehot(input_file, output_file)