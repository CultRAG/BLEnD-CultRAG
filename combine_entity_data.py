"""
Script to combine all entity data pickle files into a single entity_data_cache.pkl
"""
import pickle
import os
from pathlib import Path


def combine_entity_data_files(input_dir='entity-data', output_file='entity_data_cache.pkl'):
    """
    Combine all .pkl files from entity-data directory into a single cache file.
    
    Args:
        input_dir: Directory containing the individual pickle files
        output_file: Name of the output combined pickle file
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Directory '{input_dir}' does not exist")
        return
    
    # Get all pickle files sorted by name
    pkl_files = sorted(input_path.glob('*.pkl'))
    
    if not pkl_files:
        print(f"No .pkl files found in '{input_dir}'")
        return
    
    print(f"Found {len(pkl_files)} pickle files to combine:")
    for f in pkl_files:
        print(f"  - {f.name}")
    
    # Initialize combined data structure
    combined_data = {
        'entity_data': [],
        'df': None,
        'file_hash': {},
        'timestamp': None,
        'num_questions': 0,
        'has_answers': False,
        'source_files': []
    }
    
    # Load and combine all pickle files
    for pkl_file in pkl_files:
        print(f"\nProcessing {pkl_file.name}...")
        try:
            with open(pkl_file, 'rb') as f:
                data = pickle.load(f)
            
            # Combine entity_data lists
            if 'entity_data' in data and data['entity_data']:
                combined_data['entity_data'].extend(data['entity_data'])
                print(f"  Added {len(data['entity_data'])} entity entries")
            
            # Store file hash with filename as key
            if 'file_hash' in data:
                combined_data['file_hash'][pkl_file.name] = data['file_hash']
            
            # Keep the latest timestamp
            if 'timestamp' in data:
                if combined_data['timestamp'] is None or data['timestamp'] > combined_data['timestamp']:
                    combined_data['timestamp'] = data['timestamp']
            
            # Sum up number of questions
            if 'num_questions' in data:
                combined_data['num_questions'] += data['num_questions']
            
            # Set has_answers to True if any file has answers
            if 'has_answers' in data and data['has_answers']:
                combined_data['has_answers'] = True
            
            # Combine dataframes if present (concatenate)
            if 'df' in data and data['df'] is not None:
                if combined_data['df'] is None:
                    combined_data['df'] = data['df']
                else:
                    import pandas as pd
                    combined_data['df'] = pd.concat([combined_data['df'], data['df']], 
                                                     ignore_index=True)
            
            # Track source files
            combined_data['source_files'].append(pkl_file.name)
            
        except Exception as e:
            print(f"  Error processing {pkl_file.name}: {e}")
            continue
    
    # Save combined data
    print(f"\n{'='*60}")
    print(f"Combined Summary:")
    print(f"  Total entity entries: {len(combined_data['entity_data'])}")
    print(f"  Total questions: {combined_data['num_questions']}")
    print(f"  Has answers: {combined_data['has_answers']}")
    print(f"  Dataframe shape: {combined_data['df'].shape if combined_data['df'] is not None else 'None'}")
    print(f"  Source files: {len(combined_data['source_files'])}")
    print(f"{'='*60}")
    
    output_path = Path(output_file)
    with open(output_path, 'wb') as f:
        pickle.dump(combined_data, f)
    
    print(f"\n✓ Combined data saved to: {output_path.absolute()}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")


if __name__ == '__main__':
    combine_entity_data_files()
