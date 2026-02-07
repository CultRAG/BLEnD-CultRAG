import pandas as pd
import os
from pathlib import Path

def calculate_accuracy(predictions_file, answers_file):
    """Calculate accuracy for a single predictions file."""
    predictions_df = pd.read_csv(predictions_file)
    answers_df = pd.read_csv(answers_file, sep='\t')
    
    # Use 'id' column if it exists, otherwise skip this file
    if 'id' not in predictions_df.columns:
        return None, None, None
    
    merged_df = pd.merge(predictions_df, answers_df, on='id', how='inner')
    merged_df['match'] = merged_df['prediction'] == merged_df['answer']
    
    total = len(merged_df)
    correct = merged_df['match'].sum()
    accuracy = (correct / total * 100) if total > 0 else 0
    
    return correct, total, accuracy

def main():
    predictions_folder = "my_dir (11)/kaggle/working"
    answers_file = "prediction-test/answers (3).tsv"
    
    # Get all CSV files in prediction-test folder
    prediction_files = sorted(Path(predictions_folder).glob("*.csv"))
    
    print("=" * 80)
    print("ACCURACY COMPARISON FOR ALL PREDICTION FILES")
    print("=" * 80)
    print()
    
    results = []
    
    for pred_file in prediction_files:
        correct, total, accuracy = calculate_accuracy(pred_file, answers_file)
        if correct is None:  # Skip files without 'id' column
            continue
        filename = pred_file.name
        results.append({
            'file': filename,
            'correct': correct,
            'total': total,
            'accuracy': accuracy
        })
        print(f"{filename:<45} {correct}/{total}  →  {accuracy:.2f}%")
    
    # Sort by accuracy (descending)
    print("\n" + "=" * 80)
    print("RANKED BY ACCURACY")
    print("=" * 80)
    print()
    
    sorted_results = sorted(results, key=lambda x: x['accuracy'], reverse=True)
    for i, result in enumerate(sorted_results, 1):
        print(f"{i}. {result['file']:<45} {result['accuracy']:.2f}%")

if __name__ == "__main__":
    main()
