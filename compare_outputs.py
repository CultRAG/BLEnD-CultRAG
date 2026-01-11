"""
Compare Error Analysis Results Across Multiple Output Versions
Compares v2, v3, and v4 output folders for error analysis metrics
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

BASE_DIR = Path(r"C:\Users\LawLight\OneDrive\Desktop\semevals")
OUTPUT_DIR = BASE_DIR / 'comparison_results'

VERSIONS = ['v2', 'v3', 'v4']
OUTPUT_DIRS = {
    'v2': BASE_DIR / 'output-with-v2' / 'kaggle' / 'working',
    'v3': BASE_DIR / 'output-with-v3' / 'kaggle' / 'working',
    'v4': BASE_DIR / 'output-with-v4' / 'kaggle' / 'working'
}

FILES_TO_COMPARE = [
    'error_analysis_by_country.csv',
    'error_analysis_by_intent.csv',
    'error_cases_detailed.csv',
    'error_analysis_report.json',
    'predictions_all_methods_combined.csv'
]

# ============================================================================
# Helper Functions
# ============================================================================

def load_csv(filepath):
    """Load CSV file if exists"""
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return None

def load_json(filepath):
    """Load JSON file if exists"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

# ============================================================================
# Comparison Functions
# ============================================================================

def compare_by_country():
    """Compare error analysis by country across versions"""
    print_section("COMPARISON: Error Analysis by Country")
    
    dataframes = {}
    for version in VERSIONS:
        filepath = OUTPUT_DIRS[version] / 'error_analysis_by_country.csv'
        df = load_csv(filepath)
        if df is not None:
            dataframes[version] = df
            print(f"\n✅ Loaded {version}: {len(df)} countries")
        else:
            print(f"\n❌ Missing {version}: {filepath}")
    
    if not dataframes:
        print("\n⚠️  No data found for comparison")
        return
    
    # Merge all versions
    merged = None
    for version, df in dataframes.items():
        df_renamed = df.rename(columns={
            'accuracy': f'accuracy_{version}',
            'error_rate': f'error_rate_{version}',
            'errors': f'errors_{version}',
            'correct': f'correct_{version}'
        })
        if merged is None:
            merged = df_renamed[['country', 'total'] + [c for c in df_renamed.columns if version in c]]
        else:
            merged = merged.merge(
                df_renamed[['country'] + [c for c in df_renamed.columns if version in c]],
                on='country',
                how='outer'
            )
    
    # Sort by country
    merged = merged.sort_values('country')
    
    # Calculate improvements
    if 'v2' in dataframes and 'v4' in dataframes:
        merged['improvement_v2_to_v4'] = merged['accuracy_v4'] - merged['accuracy_v2']
    
    print("\n📊 Country-wise Comparison:\n")
    print(merged.to_string(index=False))
    
    # Save comparison
    output_file = OUTPUT_DIR / 'comparison_by_country.csv'
    merged.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    
    # Summary statistics
    print("\n📈 Summary Statistics:")
    for version in VERSIONS:
        acc_col = f'accuracy_{version}'
        if acc_col in merged.columns:
            mean_acc = merged[acc_col].mean()
            print(f"   {version.upper()} - Mean Accuracy: {mean_acc:.2f}%")
    
    if 'improvement_v2_to_v4' in merged.columns:
        avg_improvement = merged['improvement_v2_to_v4'].mean()
        print(f"\n   📊 Average Improvement (v2→v4): {avg_improvement:.2f}%")
        
        # Best improvements
        print(f"\n   🏆 Top 5 Improved Countries:")
        top_improved = merged.nlargest(5, 'improvement_v2_to_v4')[['country', 'improvement_v2_to_v4', 'accuracy_v2', 'accuracy_v4']]
        for _, row in top_improved.iterrows():
            print(f"      {row['country']}: {row['accuracy_v2']:.1f}% → {row['accuracy_v4']:.1f}% (+{row['improvement_v2_to_v4']:.1f}%)")

def compare_by_intent():
    """Compare error analysis by intent across versions"""
    print_section("COMPARISON: Error Analysis by Intent")
    
    dataframes = {}
    for version in VERSIONS:
        filepath = OUTPUT_DIRS[version] / 'error_analysis_by_intent.csv'
        df = load_csv(filepath)
        if df is not None:
            dataframes[version] = df
            print(f"\n✅ Loaded {version}: {len(df)} intents")
        else:
            print(f"\n❌ Missing {version}: {filepath}")
    
    if not dataframes:
        print("\n⚠️  No data found for comparison")
        return
    
    # Merge all versions
    merged = None
    for version, df in dataframes.items():
        df_renamed = df.rename(columns={
            'accuracy': f'accuracy_{version}',
            'error_rate': f'error_rate_{version}',
            'errors': f'errors_{version}',
            'correct': f'correct_{version}'
        })
        if merged is None:
            merged = df_renamed[['intent', 'total'] + [c for c in df_renamed.columns if version in c]]
        else:
            merged = merged.merge(
                df_renamed[['intent'] + [c for c in df_renamed.columns if version in c]],
                on='intent',
                how='outer'
            )
    
    # Sort by intent
    merged = merged.sort_values('intent')
    
    # Calculate improvements
    if 'v2' in dataframes and 'v4' in dataframes:
        merged['improvement_v2_to_v4'] = merged['accuracy_v4'] - merged['accuracy_v2']
    
    print("\n📊 Intent-wise Comparison:\n")
    print(merged.to_string(index=False))
    
    # Save comparison
    output_file = OUTPUT_DIR / 'comparison_by_intent.csv'
    merged.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    
    # Summary statistics
    print("\n📈 Summary Statistics:")
    for version in VERSIONS:
        acc_col = f'accuracy_{version}'
        if acc_col in merged.columns:
            mean_acc = merged[acc_col].mean()
            print(f"   {version.upper()} - Mean Accuracy: {mean_acc:.2f}%")
    
    if 'improvement_v2_to_v4' in merged.columns:
        avg_improvement = merged['improvement_v2_to_v4'].mean()
        print(f"\n   📊 Average Improvement (v2→v4): {avg_improvement:.2f}%")
        
        # Best improvements
        print(f"\n   🏆 Top 5 Improved Intents:")
        top_improved = merged.nlargest(5, 'improvement_v2_to_v4')[['intent', 'improvement_v2_to_v4', 'accuracy_v2', 'accuracy_v4']]
        for _, row in top_improved.iterrows():
            print(f"      {row['intent']}: {row['accuracy_v2']:.1f}% → {row['accuracy_v4']:.1f}% (+{row['improvement_v2_to_v4']:.1f}%)")

def compare_error_cases():
    """Compare detailed error cases across versions"""
    print_section("COMPARISON: Error Cases Detailed")
    
    dataframes = {}
    for version in VERSIONS:
        filepath = OUTPUT_DIRS[version] / 'error_cases_detailed.csv'
        df = load_csv(filepath)
        if df is not None:
            dataframes[version] = df
            print(f"\n✅ Loaded {version}: {len(df)} error cases")
        else:
            print(f"\n❌ Missing {version}: {filepath}")
    
    if not dataframes:
        print("\n⚠️  No data found for comparison")
        return
    
    print("\n📊 Error Case Counts by Version:")
    for version, df in dataframes.items():
        print(f"   {version.upper()}: {len(df)} errors")
    
    # Find common errors (present in all versions)
    if len(dataframes) >= 2:
        # Get first available version
        first_version = list(dataframes.keys())[0]
        common_errors = set(dataframes[first_version]['id'])
        for version in dataframes.keys():
            if version != first_version:
                common_errors &= set(dataframes[version]['id'])
        
        print(f"\n🔴 Common Errors (all versions): {len(common_errors)}")
        
        # Find errors fixed in later versions
        if 'v2' in dataframes and 'v4' in dataframes:
            v2_errors = set(dataframes['v2']['id'])
            v4_errors = set(dataframes['v4']['id'])
            fixed_errors = v2_errors - v4_errors
            new_errors = v4_errors - v2_errors
            
            print(f"\n✅ Errors Fixed (v2→v4): {len(fixed_errors)}")
            if len(fixed_errors) > 0:
                print(f"   Sample fixed IDs: {list(fixed_errors)[:10]}")
            
            print(f"\n❌ New Errors (v2→v4): {len(new_errors)}")
            if len(new_errors) > 0:
                print(f"   Sample new error IDs: {list(new_errors)[:10]}")
        
        # Save common errors
        if common_errors:
            first_version = list(dataframes.keys())[0]
            common_df = dataframes[first_version][dataframes[first_version]['id'].isin(common_errors)]
            output_file = OUTPUT_DIR / 'common_errors_all_versions.csv'
            common_df.to_csv(output_file, index=False)
            print(f"\n💾 Common errors saved to: {output_file}")

def compare_json_reports():
    """Compare JSON error analysis reports"""
    print_section("COMPARISON: Error Analysis Reports (JSON)")
    
    reports = {}
    for version in VERSIONS:
        filepath = OUTPUT_DIRS[version] / 'error_analysis_report.json'
        data = load_json(filepath)
        if data is not None:
            reports[version] = data
            print(f"\n✅ Loaded {version}")
        else:
            print(f"\n❌ Missing {version}: {filepath}")
    
    if not reports:
        print("\n⚠️  No data found for comparison")
        return
    
    # Compare overall metrics
    print("\n📊 Overall Performance Metrics:\n")
    print(f"{'Metric':<40} {'v2':>10} {'v3':>10} {'v4':>10} {'Δ(v2→v4)':>12}")
    print("-" * 85)
    
    metrics_to_compare = [
        ('total_questions', 'Total Questions'),
        ('correct_predictions', 'Correct Predictions'),
        ('incorrect_predictions', 'Errors'),
        ('overall_accuracy', 'Accuracy (%)'),
    ]
    
    for key, label in metrics_to_compare:
        values = {}
        for version in VERSIONS:
            if version in reports:
                if key in reports[version]:
                    values[version] = reports[version][key]
        
        if 'v2' in values and 'v4' in values:
            delta = values['v4'] - values['v2']
            delta_str = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"
        else:
            delta_str = "N/A"
        
        v2_str = f"{values.get('v2', 'N/A')}" if isinstance(values.get('v2'), (int, float)) else 'N/A'
        v3_str = f"{values.get('v3', 'N/A')}" if isinstance(values.get('v3'), (int, float)) else 'N/A'
        v4_str = f"{values.get('v4', 'N/A')}" if isinstance(values.get('v4'), (int, float)) else 'N/A'
        
        print(f"{label:<40} {v2_str:>10} {v3_str:>10} {v4_str:>10} {delta_str:>12}")
    
    # Compare by country breakdown if available
    if all('by_country' in reports[v] for v in reports):
        print("\n📍 By Country Performance:")
        print(f"   v2: {len(reports['v2']['by_country'])} countries")
        print(f"   v3: {len(reports['v3']['by_country'])} countries")
        print(f"   v4: {len(reports['v4']['by_country'])} countries")
    
    # Save combined report
    combined_report = {
        'comparison_date': datetime.now().isoformat(),
        'versions_compared': list(reports.keys()),
        'reports': reports
    }
    
    output_file = OUTPUT_DIR / 'combined_error_analysis_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_report, f, indent=2)
    print(f"\n💾 Combined report saved to: {output_file}")

def compare_predictions():
    """Compare predictions from all methods"""
    print_section("COMPARISON: Predictions from All Methods")
    
    dataframes = {}
    for version in VERSIONS:
        filepath = OUTPUT_DIRS[version] / 'predictions_all_methods_combined.csv'
        df = load_csv(filepath)
        if df is not None:
            dataframes[version] = df
            print(f"\n✅ Loaded {version}: {len(df)} predictions")
        else:
            print(f"\n❌ Missing {version}: {filepath}")
    
    if not dataframes:
        print("\n⚠️  No data found for comparison")
        return
    
    print("\n📊 Prediction Statistics:\n")
    
    # Check columns available in each version
    for version, df in dataframes.items():
        num_cols = len(df.columns)
        print(f"\n{version.upper()}: {num_cols} columns total")
        
        # Count correct predictions by method
        if 'correct_answer' in df.columns:
            print(f"\n{version.upper()} Accuracy by Method:")
            for col in df.columns:
                # Look for prediction columns (not the _correct boolean columns)
                if ('baseline' in col or 'rag' in col or 'phase' in col) and not col.endswith('_correct'):
                    try:
                        correct = (df[col] == df['correct_answer']).sum()
                        accuracy = (correct / len(df)) * 100
                        print(f"   {col:35s}: {correct:3d}/{len(df)} ({accuracy:6.2f}%)")
                    except:
                        pass
    
    # Compare same question IDs across versions
    if len(dataframes) >= 2 and all('id' in df.columns for df in dataframes.values()):
        print("\n🔍 Cross-Version Prediction Comparison:")
        
        # Get common IDs
        first_version = list(dataframes.keys())[0]
        common_ids = set(dataframes[first_version]['id'])
        for version in dataframes.keys():
            if version != first_version:
                common_ids &= set(dataframes[version]['id'])
        
        print(f"\n   Common Questions: {len(common_ids)}")
        
        # For each common ID, check if prediction changed
        if 'v3' in dataframes and 'v4' in dataframes and len(common_ids) > 0:
            changes = []
            improved = []  # Wrong in v3, correct in v4
            degraded = []  # Correct in v3, wrong in v4
            
            for qid in common_ids:
                v3_row = dataframes['v3'][dataframes['v3']['id'] == qid].iloc[0]
                v4_row = dataframes['v4'][dataframes['v4']['id'] == qid].iloc[0]
                
                # Find prediction columns (use phase6_full_system or last phase)
                pred_cols = [c for c in v3_row.index if 'phase6_full_system' in c.lower() or c == 'phase6_full_system']
                if not pred_cols:
                    pred_cols = [c for c in v3_row.index if 'full_system' in c.lower()]
                
                if pred_cols:
                    pred_col = pred_cols[0]
                    correct_ans = v3_row['correct_answer']
                    v3_pred = v3_row[pred_col]
                    v4_pred = v4_row[pred_col]
                    
                    v3_correct = (v3_pred == correct_ans)
                    v4_correct = (v4_pred == correct_ans)
                    
                    if v3_pred != v4_pred:
                        change_info = {
                            'id': qid,
                            'question': v3_row.get('question', '')[:60],
                            'v3_pred': v3_pred,
                            'v4_pred': v4_pred,
                            'correct': correct_ans,
                            'v3_correct': v3_correct,
                            'v4_correct': v4_correct
                        }
                        changes.append(change_info)
                        
                        if not v3_correct and v4_correct:
                            improved.append(change_info)
                        elif v3_correct and not v4_correct:
                            degraded.append(change_info)
            
            print(f"\n   Predictions Changed (v3→v4): {len(changes)}")
            print(f"   ✅ Improved (v3 wrong → v4 correct): {len(improved)}")
            print(f"   ❌ Degraded (v3 correct → v4 wrong): {len(degraded)}")
            
            if changes:
                changes_df = pd.DataFrame(changes)
                output_file = OUTPUT_DIR / 'prediction_changes_v3_to_v4.csv'
                changes_df.to_csv(output_file, index=False)
                print(f"   💾 All changes saved to: {output_file}")
                
            if improved:
                improved_df = pd.DataFrame(improved)
                output_file = OUTPUT_DIR / 'predictions_improved_v3_to_v4.csv'
                improved_df.to_csv(output_file, index=False)
                print(f"   💾 Improvements saved to: {output_file}")
                
            if degraded:
                degraded_df = pd.DataFrame(degraded)
                output_file = OUTPUT_DIR / 'predictions_degraded_v3_to_v4.csv'
                degraded_df.to_csv(output_file, index=False)
                print(f"   💾 Degradations saved to: {output_file}")

# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run all comparisons"""
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print("  ERROR ANALYSIS COMPARISON ACROSS VERSIONS")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Output Directory: {OUTPUT_DIR}")
    print("="*80)
    
    print("\n📂 Output Directories:")
    for version, path in OUTPUT_DIRS.items():
        exists = "✅" if path.exists() else "❌"
        print(f"   {exists} {version.upper()}: {path}")
    
    # Run all comparisons
    compare_by_country()
    compare_by_intent()
    compare_error_cases()
    compare_json_reports()
    compare_predictions()
    
    print("\n" + "="*80)
    print("  ✅ COMPARISON COMPLETE")
    print("="*80)
    print(f"\n📁 Generated Files in {OUTPUT_DIR}:")
    print("   - comparison_by_country.csv")
    print("   - comparison_by_intent.csv")
    print("   - common_errors_all_versions.csv")
    print("   - combined_error_analysis_report.json")
    print("   - prediction_changes_v3_to_v4.csv (if applicable)")
    print("   - predictions_improved_v3_to_v4.csv (if applicable)")
    print("   - predictions_degraded_v3_to_v4.csv (if applicable)")
    print("\n")

if __name__ == "__main__":
    main()
