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
    print_header("COUNTRY COMPARISON HIGHLIGHTS (V3 vs V4 vs V5)")
    
    df = pd.read_csv(RESULTS_DIR / 'comparison_by_country.csv')
    
    # Show overall accuracy progression
    print_and_save("\n🌍 ACCURACY PROGRESSION BY COUNTRY:\n")
    print_and_save(f"{'Country':<10} {'V3':>8} {'V4':>8} {'V5':>8} {'V3→V5':>10} {'V4→V5':>10}")
    print_and_save("-" * 60)
    
    # Calculate changes
    has_v3 = 'accuracy_v3' in df.columns
    has_v4 = 'accuracy_v4' in df.columns
    has_v5 = 'accuracy_v5' in df.columns
    
    if has_v3 and has_v5:
        df['change_v3_v5'] = df['accuracy_v5'] - df['accuracy_v3']
    if has_v4 and has_v5:
        df['change_v4_v5'] = df['accuracy_v5'] - df['accuracy_v4']
    
    for _, row in df.sort_values('country').iterrows():
        country = row['country']
        v3_acc = f"{row['accuracy_v3']:.1f}%" if has_v3 else "N/A"
        v4_acc = f"{row['accuracy_v4']:.1f}%" if has_v4 else "N/A"
        v5_acc = f"{row['accuracy_v5']:.1f}%" if has_v5 else "N/A"
        
        change_v3_v5 = f"{row['change_v3_v5']:+.1f}%" if 'change_v3_v5' in df.columns else "N/A"
        change_v4_v5 = f"{row['change_v4_v5']:+.1f}%" if 'change_v4_v5' in df.columns else "N/A"
        
        print_and_save(f"{country:<10} {v3_acc:>8} {v4_acc:>8} {v5_acc:>8} {change_v3_v5:>10} {change_v4_v5:>10}")
    
    # V3->V5 Overall improvements
    if 'change_v3_v5' in df.columns:
        print_and_save("\n📈 MOST IMPROVED Countries (v3→v5):")
        improved = df[df['change_v3_v5'] > 0].sort_values('change_v3_v5', ascending=False)
        if len(improved) > 0:
            for _, row in improved.head(5).iterrows():
                print_and_save(f"   {row['country']:4s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v5']:5.1f}% (+{row['change_v3_v5']:.1f}%)")
        else:
            print_and_save("   None")
        
        print_and_save("\n📉 MOST DEGRADED Countries (v3→v5):")
        degraded = df[df['change_v3_v5'] < 0].sort_values('change_v3_v5')
        if len(degraded) > 0:
            for _, row in degraded.head(5).iterrows():
                print_and_save(f"   {row['country']:4s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v5']:5.1f}% ({row['change_v3_v5']:.1f}%)")
        else:
            print_and_save("   None")
    
    # V4->V5 Recent changes
    if 'change_v4_v5' in df.columns:
        print_and_save("\n🔄 RECENT CHANGES (v4→v5):")
        recent_improved = df[df['change_v4_v5'] > 0].sort_values('change_v4_v5', ascending=False)
        if len(recent_improved) > 0:
            print_and_save("   ✅ Improved:")
            for _, row in recent_improved.iterrows():
                print_and_save(f"      {row['country']:4s}: {row['accuracy_v4']:5.1f}% → {row['accuracy_v5']:5.1f}% (+{row['change_v4_v5']:.1f}%)")
        
        recent_degraded = df[df['change_v4_v5'] < 0].sort_values('change_v4_v5')
        if len(recent_degraded) > 0:
            print_and_save("   ❌ Degraded:")
            for _, row in recent_degraded.iterrows():
                print_and_save(f"      {row['country']:4s}: {row['accuracy_v4']:5.1f}% → {row['accuracy_v5']:5.1f}% ({row['change_v4_v5']:.1f}%)")
        
        unchanged = df[df['change_v4_v5'] == 0]
        if len(unchanged) > 0:
            print_and_save(f"   ➡️  Unchanged: {len(unchanged)} countries")

def view_intent_comparison():
    """View intent comparison highlights"""
    print_header("INTENT COMPARISON HIGHLIGHTS (V3 vs V4 vs V5)")
    
    df = pd.read_csv(RESULTS_DIR / 'comparison_by_intent.csv')
    
    # Show overall accuracy progression
    print_and_save("\n🎯 ACCURACY PROGRESSION BY INTENT:\n")
    print_and_save(f"{'Intent':<35} {'V3':>8} {'V4':>8} {'V5':>8} {'V3→V5':>10} {'V4→V5':>10}")
    print_and_save("-" * 85)
    
    # Calculate changes
    has_v3 = 'accuracy_v3' in df.columns
    has_v4 = 'accuracy_v4' in df.columns
    has_v5 = 'accuracy_v5' in df.columns
    
    if has_v3 and has_v5:
        df['change_v3_v5'] = df['accuracy_v5'] - df['accuracy_v3']
    if has_v4 and has_v5:
        df['change_v4_v5'] = df['accuracy_v5'] - df['accuracy_v4']
    
    for _, row in df.sort_values('intent').iterrows():
        intent = row['intent'][:33]
        v3_acc = f"{row['accuracy_v3']:.1f}%" if has_v3 else "N/A"
        v4_acc = f"{row['accuracy_v4']:.1f}%" if has_v4 else "N/A"
        v5_acc = f"{row['accuracy_v5']:.1f}%" if has_v5 else "N/A"
        
        change_v3_v5 = f"{row['change_v3_v5']:+.1f}%" if 'change_v3_v5' in df.columns else "N/A"
        change_v4_v5 = f"{row['change_v4_v5']:+.1f}%" if 'change_v4_v5' in df.columns else "N/A"
        
        print_and_save(f"{intent:<35} {v3_acc:>8} {v4_acc:>8} {v5_acc:>8} {change_v3_v5:>10} {change_v4_v5:>10}")
    
    # V3->V5 Overall improvements
    if 'change_v3_v5' in df.columns:
        print_and_save("\n📈 TOP IMPROVED Intents (v3→v5):")
        improved = df[df['change_v3_v5'] > 0].sort_values('change_v3_v5', ascending=False)
        if len(improved) > 0:
            for _, row in improved.head(5).iterrows():
                print_and_save(f"   {row['intent']:35s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v5']:5.1f}% (+{row['change_v3_v5']:.1f}%)")
        else:
            print_and_save("   None")
        
        print_and_save("\n📉 TOP DEGRADED Intents (v3→v5):")
        degraded = df[df['change_v3_v5'] < 0].sort_values('change_v3_v5')
        if len(degraded) > 0:
            for _, row in degraded.head(5).iterrows():
                print_and_save(f"   {row['intent']:35s}: {row['accuracy_v3']:5.1f}% → {row['accuracy_v5']:5.1f}% ({row['change_v3_v5']:.1f}%)")
        else:
            print_and_save("   None")
    
    # V4->V5 Recent changes
    if 'change_v4_v5' in df.columns:
        print_and_save("\n🔄 RECENT CHANGES (v4→v5):")
        recent_changes = df[df['change_v4_v5'] != 0].sort_values('change_v4_v5', ascending=False)
        if len(recent_changes) > 0:
            for _, row in recent_changes.iterrows():
                symbol = "✅" if row['change_v4_v5'] > 0 else "❌"
                print_and_save(f"   {symbol} {row['intent']:35s}: {row['accuracy_v4']:5.1f}% → {row['accuracy_v5']:5.1f}% ({row['change_v4_v5']:+.1f}%)")
        else:
            print_and_save("   No changes")

def view_prediction_changes():
    """View prediction changes between versions"""
    print_header("PREDICTION CHANGES ACROSS VERSIONS")
    
    # V3->V4 Changes
    print_and_save("\n" + "-"*80)
    print_and_save("V3 → V4 CHANGES")
    print_and_save("-"*80)
    
    improved_v3_v4_file = RESULTS_DIR / 'predictions_improved_v3_to_v4.csv'
    if improved_v3_v4_file.exists():
        df = pd.read_csv(improved_v3_v4_file)
        print_and_save(f"\n✅ IMPROVED (v3→v4): {len(df)} questions")
        for idx, row in df.head(5).iterrows():
            print_and_save(f"\n   {idx+1}. {row['id']}")
            print_and_save(f"      Question: {row['question']}")
            print_and_save(f"      v3 predicted: {row['v3_pred']} ❌")
            print_and_save(f"      v4 predicted: {row['v4_pred']} ✅")
            print_and_save(f"      Correct: {row['correct']}")
        if len(df) > 5:
            print_and_save(f"\n   ... and {len(df)-5} more")
    
    degraded_v3_v4_file = RESULTS_DIR / 'predictions_degraded_v3_to_v4.csv'
    if degraded_v3_v4_file.exists():
        df = pd.read_csv(degraded_v3_v4_file)
        print_and_save(f"\n❌ DEGRADED (v3→v4): {len(df)} questions")
        for idx, row in df.head(5).iterrows():
            print_and_save(f"\n   {idx+1}. {row['id']}")
            print_and_save(f"      Question: {row['question']}")
            print_and_save(f"      v3 predicted: {row['v3_pred']} ✅")
            print_and_save(f"      v4 predicted: {row['v4_pred']} ❌")
            print_and_save(f"      Correct: {row['correct']}")
        if len(df) > 5:
            print_and_save(f"\n   ... and {len(df)-5} more")
    
    # V4->V5 Changes (Recent)
    print_and_save("\n" + "-"*80)
    print_and_save("V4 → V5 CHANGES (MOST RECENT)")
    print_and_save("-"*80)
    
    improved_v4_v5_file = RESULTS_DIR / 'predictions_improved_v4_to_v5.csv'
    if improved_v4_v5_file.exists():
        df = pd.read_csv(improved_v4_v5_file)
        print_and_save(f"\n✅ IMPROVED (v4→v5): {len(df)} questions")
        for idx, row in df.head(10).iterrows():
            print_and_save(f"\n   {idx+1}. {row['id']}")
            print_and_save(f"      Question: {row['question']}")
            print_and_save(f"      v4 predicted: {row['v4_pred']} ❌")
            print_and_save(f"      v5 predicted: {row['v5_pred']} ✅")
            print_and_save(f"      Correct: {row['correct']}")
        if len(df) > 10:
            print_and_save(f"\n   ... and {len(df)-10} more")
    else:
        print_and_save("\nℹ️  No v4→v5 improvement data found")
    
    degraded_v4_v5_file = RESULTS_DIR / 'predictions_degraded_v4_to_v5.csv'
    if degraded_v4_v5_file.exists():
        df = pd.read_csv(degraded_v4_v5_file)
        print_and_save(f"\n❌ DEGRADED (v4→v5): {len(df)} questions")
        for idx, row in df.head(10).iterrows():
            print_and_save(f"\n   {idx+1}. {row['id']}")
            print_and_save(f"      Question: {row['question']}")
            print_and_save(f"      v4 predicted: {row['v4_pred']} ✅")
            print_and_save(f"      v5 predicted: {row['v5_pred']} ❌")
            print_and_save(f"      Correct: {row['correct']}")
        if len(df) > 10:
            print_and_save(f"\n   ... and {len(df)-10} more")
    else:
        print_and_save("\nℹ️  No v4→v5 degradation data found")

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
    print_and_save("  COMPREHENSIVE COMPARISON RESULTS SUMMARY (V3 vs V4 vs V5)")
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
