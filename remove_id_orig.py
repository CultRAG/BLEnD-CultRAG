#!/usr/bin/env python3
"""
Script to remove id_orig column from a TSV file
"""
import pandas as pd
import sys

def remove_id_orig_column(input_file, output_file=None):
    """
    Remove id_orig column from TSV file
    
    Args:
        input_file: Path to input TSV file
        output_file: Path to output TSV file (if None, overwrites input)
    """
    # Read the TSV file
    print(f"📖 Reading {input_file}...")
    df = pd.read_csv(input_file, sep='\t')
    
    # Check if id_orig column exists
    if 'id_orig' not in df.columns:
        print(f"⚠️  Column 'id_orig' not found in {input_file}")
        print(f"Available columns: {', '.join(df.columns)}")
        return
    
    # Remove the column
    df_cleaned = df.drop(columns=['id_orig'])
    print(f"✅ Removed 'id_orig' column")
    
    # Determine output file
    if output_file is None:
        output_file = input_file
    
    # Save the cleaned file
    df_cleaned.to_csv(output_file, sep='\t', index=False)
    print(f"💾 Saved to {output_file}")
    print(f"📊 Shape: {df_cleaned.shape[0]} rows, {df_cleaned.shape[1]} columns")
    print(f"📋 Remaining columns: {', '.join(df_cleaned.columns)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_id_orig.py <input_file> [output_file]")
        print("Examples:")
        print("  python remove_id_orig.py input.tsv              # Overwrites input.tsv")
        print("  python remove_id_orig.py input.tsv output.tsv   # Saves to output.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    remove_id_orig_column(input_file, output_file)
    print("\n🎉 Done!")
