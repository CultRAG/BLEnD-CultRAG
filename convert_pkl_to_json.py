#!/usr/bin/env python3
"""
Convert Pickle Files to JSON
Converts wiki_cache.pkl and kb_chunks.pkl to human-readable JSON format
"""

import pickle
import json
import os
from pathlib import Path


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
    print("PKL → JSON Converter")
    print("="*60)
    print()
    
    # Define files to convert
    files_to_convert = [
        ('wiki_cache.pkl', 'wiki_cache.json'),
        ('kb_chunks.pkl', 'kb_chunks.json'),
        # Add Kaggle paths too
        ('/kaggle/working/wiki_cache.pkl', '/kaggle/working/wiki_cache.json'),
        ('/kaggle/working/kb_chunks.pkl', '/kaggle/working/kb_chunks.json'),
    ]
    
    converted_count = 0
    
    for pkl_file, json_file in files_to_convert:
        if os.path.exists(pkl_file):
            if convert_pkl_to_json(pkl_file, json_file):
                converted_count += 1
            print()
    
    if converted_count == 0:
        print("⚠️  No pickle files found in current directory or /kaggle/working/")
        print("\nSearching for pickle files...")
        
        # Search in current directory
        pkl_files = list(Path('.').glob('*.pkl'))
        if pkl_files:
            print(f"\n📁 Found {len(pkl_files)} .pkl file(s):")
            for pkl_path in pkl_files:
                pkl_file = str(pkl_path)
                json_file = pkl_file.replace('.pkl', '.json')
                print(f"\n   {pkl_file}")
                if convert_pkl_to_json(pkl_file, json_file):
                    converted_count += 1
    
    print("="*60)
    print(f"🎉 Conversion complete! {converted_count} file(s) converted to JSON")
    print("="*60)


if __name__ == "__main__":
    main()
