import os
import pandas as pd
from pathlib import Path

# Base path to submission folder
base_path = Path(".")

# Define the prediction types to combine
prediction_types = [
    "predictions_baseline_no_rag",
    "predictions_rag_basic",
    "predictions_phase1_countryfilter",
    "predictions_phase2_intent",
    "predictions_phase3_tiered",
    "predictions_phase4_quality",
    "predictions_phase5_trust_weight",
    "predictions_phase6_full_system",
]

# Define data folders
data_folders = [
    "data_1_results",
    "data_2_results",
    "data_3_results",
    "data_4_results",
    "data_5_result",
    "data_6_result",
    "data_7_results",
]

# Create output directory if it doesn't exist
output_dir = base_path / "combined_predictions"
output_dir.mkdir(exist_ok=True)

# Combine predictions for each type
for pred_type in prediction_types:
    print(f"\nProcessing: {pred_type}")
    
    dfs = []
    
    for data_folder in data_folders:
        file_path = base_path / data_folder / "kaggle" / "working" / f"{pred_type}.csv"
        
        if file_path.exists():
            print(f"  - Reading {data_folder}...")
            df = pd.read_csv(file_path, sep='\t')
            dfs.append(df)
        else:
            print(f"  - WARNING: {file_path} not found")
    
    # Combine all dataframes
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        output_file = output_dir / f"{pred_type}_combined.tsv"
        combined_df.to_csv(output_file, sep='\t', index=False)
        print(f"  ✓ Combined {len(dfs)} parts ({len(combined_df)} rows) -> {output_file}")
    else:
        print(f"  ✗ No files found for {pred_type}")

print("\n" + "="*60)
print("All predictions combined successfully!")
print(f"Output files saved in: {output_dir}")
