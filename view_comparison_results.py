"""
View and Summarize Comparison Results
Quick viewer for the generated comparison files
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\LawLight\OneDrive\Desktop\semevals")
RESULTS_DIR = BASE_DIR / 'comparison_results'

# Output file
output_lines = []

def print_and_save(text):
    """Print to console and save to output list"""
    print(text)
    output_lines.append(text)

def print_header(title):
    print_and_save("\n" + "="*80)
    print_and_save(f"  {title}")
    print_and_save("="*80)

def view_country_comparison():
    """View country comparison highlights"""
    print_header("COUNTRY COMPARISON HIGHLIGHTS")
    
    df = pd.read_csv(RESULTS_DIR / 'comparison_by_country.csv')
    
    # Calculate change
    if 'accuracy_v3' in df.columns and 'accuracy_v4' in df.columns:
        df['change'] = df['accuracy_v4'] - df['accuracy_v3']
        
        print_and_save("\n📈 IMPROVED Countries (v3→v4):")
        improved = df[df['change'] > 0].sort_values('change', ascending=False)
        if len(improved) > 0:
            for _, row in improved.iterrows():
                print_and_save(f"   {row['country']:4s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v4']:5.1f}% (+{row['change']:.1f}%)")
        else:
            print_and_save("   None")
        
        print_and_save("\n📉 DEGRADED Countries (v3→v4):")
        degraded = df[df['change'] < 0].sort_values('change')
        if len(degraded) > 0:
            for _, row in degraded.iterrows():
                print_and_save(f"   {row['country']:4s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v4']:5.1f}% ({row['change']:.1f}%)")
        else:
            print_and_save("   None")
        
        print_and_save("\n📊 UNCHANGED Countries:")
        unchanged = df[df['change'] == 0]
        if len(unchanged) > 0:
            print_and_save(f"   {len(unchanged)} countries with no change")
            for _, row in unchanged.iterrows():
                print_and_save(f"   {row['country']:4s}: {row['accuracy_v4']:5.1f}%")
        else:
            print_and_save("   None")

def view_intent_comparison():
    """View intent comparison highlights"""
    print_header("INTENT COMPARISON HIGHLIGHTS")
    
    df = pd.read_csv(RESULTS_DIR / 'comparison_by_intent.csv')
    
    # Calculate change
    if 'accuracy_v3' in df.columns and 'accuracy_v4' in df.columns:
        df['change'] = df['accuracy_v4'] - df['accuracy_v3']
        
        print_and_save("\n📈 IMPROVED Intents (v3→v4):")
        improved = df[df['change'] > 0].sort_values('change', ascending=False)
        if len(improved) > 0:
            for _, row in improved.iterrows():
                print_and_save(f"   {row['intent']:30s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v4']:5.1f}% (+{row['change']:.1f}%)")
        else:
            print_and_save("   None")
        
        print_and_save("\n📉 DEGRADED Intents (v3→v4):")
        degraded = df[df['change'] < 0].sort_values('change')
        if len(degraded) > 0:
            for _, row in degraded.iterrows():
                print_and_save(f"   {row['intent']:30s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v4']:5.1f}% ({row['change']:.1f}%)")
        else:
            print_and_save("   None")

def view_prediction_changes():
    """View prediction changes between versions"""
    print_header("PREDICTION CHANGES (V3→V4)")
    
    # Improved
    improved_file = RESULTS_DIR / 'predictions_improved_v3_to_v4.csv'
    if improved_file.exists():
        df = pd.read_csv(improved_file)
        print_and_save(f"\n✅ IMPROVED: {len(df)} questions")
        for idx, row in df.iterrows():
            print_and_save(f"\n   {idx+1}. {row['id']}")
            print_and_save(f"      Question: {row['question']}")
            print_and_save(f"      v3 predicted: {row['v3_pred']} ❌")
            print_and_save(f"      v4 predicted: {row['v4_pred']} ✅")
            print_and_save(f"      Correct: {row['correct']}")
    
    # Degraded
    degraded_file = RESULTS_DIR / 'predictions_degraded_v3_to_v4.csv'
    if degraded_file.exists():
        df = pd.read_csv(degraded_file)
        print_and_save(f"\n❌ DEGRADED: {len(df)} questions")
        for idx, row in df.iterrows():
            print_and_save(f"\n   {idx+1}. {row['id']}")
            print_and_save(f"      Question: {row['question']}")
            print_and_save(f"      v3 predicted: {row['v3_pred']} ✅")
            print_and_save(f"      v4 predicted: {row['v4_pred']} ❌")
            print_and_save(f"      Correct: {row['correct']}")

def view_common_errors():
    """View common errors across all versions"""
    print_header("COMMON ERRORS (Present in All Versions)")
    
    file_path = RESULTS_DIR / 'common_errors_all_versions.csv'
    if file_path.exists():
        df = pd.read_csv(file_path)
        print_and_save(f"\n🔴 {len(df)} persistent errors\n")
        
        # Group by country if available
        if 'country' in df.columns:
            by_country = df.groupby('country').size().sort_values(ascending=False)
            print_and_save("By Country:")
            for country, count in by_country.items():
                print_and_save(f"   {country}: {count} errors")
        
        # Group by intent if available
        if 'intent' in df.columns:
            by_intent = df.groupby('intent').size().sort_values(ascending=False)
            print_and_save("\nBy Intent:")
            for intent, count in by_intent.items():
                print_and_save(f"   {intent}: {count} errors")
        
        print_and_save("\nSample Errors:")
        for idx, row in df.head(10).iterrows():
            print_and_save(f"\n   {row.get('id', 'N/A')}")
            if 'question' in row:
                q = row['question'][:70] + "..." if len(str(row['question'])) > 70 else row['question']
                print_and_save(f"      {q}")
            if 'predicted' in row and 'correct' in row:
                print_and_save(f"      Predicted: {row['predicted']} | Correct: {row['correct']}")

def main():
    """Run all viewers"""
    global output_lines
    output_lines = []
    
    print_and_save("\n" + "="*80)
    print_and_save("  COMPARISON RESULTS SUMMARY")
    print_and_save(f"  Reading from: {RESULTS_DIR}")
    print_and_save(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_and_save("="*80)
    
    view_country_comparison()
    view_intent_comparison()
    view_prediction_changes()
    view_common_errors()
    
    print_and_save("\n" + "="*80)
    print_and_save("  ✅ SUMMARY COMPLETE")
    print_and_save("="*80 + "\n")
    
    # Save to file
    output_file = RESULTS_DIR / 'comparison_summary.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"💾 Summary saved to: {output_file}")

if __name__ == "__main__":
    main()
