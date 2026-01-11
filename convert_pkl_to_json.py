#!/usr/bin/env python3
"""
Convert Pickle Files to JSON
Converts all .pkl files from pkl-files folder to JSON format in json-files folder
"""

import pickle
import json
import os
from pathlib import Path
import shutil


def convert_pkl_to_json(pkl_file, json_file):
    """Convert a pickle file to JSON format"""
    if not os.path.exists(pkl_file):
        print(f"⚠️  File not found: {pkl_file}")
        return False
    
    try:
        # Check if file is actually a pickle file
        print(f"📦 Loading {pkl_file}...")
        with open(pkl_file, 'rb') as f:
            # Check first few bytes
            header = f.read(10)
            f.seek(0)
            
            # Check for UTF-8 BOM or JSON markers
            if header.startswith(b'\xef\xbb\xbf') or header.startswith(b'{') or header.startswith(b'['):
                print(f"   ⚠️  File appears to be text/JSON, not pickle. Skipping.")
                return False
            
            # Try to load as pickle
            data = pickle.load(f)
        
        # Determine data type
        if isinstance(data, dict):
            print(f"   Type: Dictionary with {len(data)} items")
        elif isinstance(data, list):
            print(f"   Type: List with {len(data)} items")
        else:
            print(f"   Type: {type(data)}")
        
        # Save as JSON
        print(f"💾 Saving to {json_file}...")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Show file sizes
        pkl_size = os.path.getsize(pkl_file) / 1024 / 1024
        json_size = os.path.getsize(json_file) / 1024 / 1024
        
        print(f"✅ Converted successfully!")
        print(f"   Pickle: {pkl_size:.2f} MB")
        print(f"   JSON:   {json_size:.2f} MB ({json_size/pkl_size*100:.1f}% of pickle size)")
        return True
        
    except pickle.UnpicklingError as e:
        print(f"❌ Not a valid pickle file: {e}")
        print(f"   (File may be corrupted or in a different format)")
        return False
    except Exception as e:
        print(f"❌ Error converting {pkl_file}: {e}")
        return False


def main():
    print("="*60)
    print("PKL → JSON Batch Converter")
    print("="*60)
    print()
    
    # ═══════════════════════════════════════════════════════════════
    # CONFIGURE FOLDERS HERE
    # ═══════════════════════════════════════════════════════════════
    input_folder = "pkl-files"      # Folder containing .pkl files
    output_folder = "json-files"    # Folder for output .json files
    # ═══════════════════════════════════════════════════════════════
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"❌ Input folder not found: {input_folder}")
        print(f"   Please create the folder and add .pkl files")
        return
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"✅ Created output folder: {output_folder}")
    
    # Find all .pkl files in input folder
    pkl_files = list(Path(input_folder).glob('*.pkl'))
    
    if not pkl_files:
        print(f"⚠️  No .pkl files found in {input_folder}/")
        return
    
    print(f"\n📁 Found {len(pkl_files)} .pkl file(s) in {input_folder}/")
    print()
    
    converted_count = 0
    failed_count = 0
    
    for pkl_path in pkl_files:
        pkl_file = str(pkl_path)
        filename = pkl_path.name
        json_filename = filename.replace('.pkl', '.json')
        json_file = os.path.join(output_folder, json_filename)
        
        print(f"📦 {filename} → {json_filename}")
        if convert_pkl_to_json(pkl_file, json_file):
            converted_count += 1
        else:
            failed_count += 1
        print()
    
    print("="*60)
    print(f"🎉 Conversion complete!")
    print(f"   ✅ Converted: {converted_count} file(s)")
    if failed_count > 0:
        print(f"   ❌ Failed: {failed_count} file(s)")
    print(f"   📂 Output folder: {output_folder}/")
    print("="*60)


if __name__ == "__main__":
    main()
