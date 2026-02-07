import pandas as pd
import sys

def compare_predictions_to_answers(predictions_file, answers_file):
    """
    Compare predictions against verified answers and calculate accuracy.
    
    Args:
        predictions_file: Path to CSV file with predictions (id, prediction)
        answers_file: Path to TSV file with answers (id, answer, status, confidence, notes)
    """
    # Read the files
    predictions_df = pd.read_csv(predictions_file)
    answers_df = pd.read_csv(answers_file, sep='\t')
    
    # Merge on id
    merged_df = pd.merge(predictions_df, answers_df, on='id', how='inner')
    
    # Calculate matches
    merged_df['match'] = merged_df['prediction'] == merged_df['answer']
    
    # Calculate accuracy
    total = len(merged_df)
    correct = merged_df['match'].sum()
    accuracy = (correct / total * 100) if total > 0 else 0
    
    # Print results
    print(f"Total: {total}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {total - correct}")
    print(f"\nAccuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    # Default file paths
    predictions_file = "predictions_phase6_full_system.csv"
    answers_file = "docs/answers.tsv"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        predictions_file = sys.argv[1]
    if len(sys.argv) > 2:
        answers_file = sys.argv[2]
    
    compare_predictions_to_answers(predictions_file, answers_file)
