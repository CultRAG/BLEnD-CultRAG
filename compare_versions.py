import pandas as pd
from collections import defaultdict

def load_and_compare():
    """Load all versions and perform comprehensive comparison."""
    
    # Load all CSV files
    print("Loading CSV files...")
    v3 = pd.read_csv('predictions-per-version/all_predictions_comparison-v3.csv')
    v4 = pd.read_csv('predictions-per-version/all_predictions_comparison-v4.csv')
    v5 = pd.read_csv('predictions-per-version/all_predictions_comparison-v5.csv')
    
    print(f"V3 has {len(v3)} questions")
    print(f"V4 has {len(v4)} questions")
    print(f"V5 has {len(v5)} questions")
    print()
    
    # Model types to compare
    models = ['baseline', 'rag_basic', 'full_system']
    model_correct_cols = {
        'baseline': 'baseline_correct',
        'rag_basic': 'rag_correct',
        'full_system': 'full_correct'
    }
    
    # Store all differences (v3->v4, v4->v5, v3->v5)
    differences_v3_v4 = defaultdict(list)
    differences_v4_v5 = defaultdict(list)
    differences_v3_v5 = defaultdict(list)
    
    # Compare each model
    for model in models:
        print(f"\n{'='*80}")
        print(f"ANALYZING MODEL: {model.upper()}")
        print(f"{'='*80}\n")
        
        # Find v3->v4 differences
        changed_v3_v4 = []
        changed_v4_v5 = []
        changed_v3_v5 = []
        
        for idx in range(len(v3)):
            v3_pred = v3.loc[idx, model]
            v4_pred = v4.loc[idx, model]
            v5_pred = v5.loc[idx, model]
            
            base_data = {
                'id': v3.loc[idx, 'id'],
                'question': v3.loc[idx, 'question'],
                'correct': v3.loc[idx, 'correct'],
                'option_A': v3.loc[idx, 'option_A'],
                'option_B': v3.loc[idx, 'option_B'],
                'option_C': v3.loc[idx, 'option_C'],
                'option_D': v3.loc[idx, 'option_D']
            }
            
            # V3 vs V4
            if v3_pred != v4_pred:
                changed_v3_v4.append({
                    **base_data,
                    'v3_prediction': v3_pred,
                    'v4_prediction': v4_pred,
                    'v3_correct': v3.loc[idx, model_correct_cols[model]],
                    'v4_correct': v4.loc[idx, model_correct_cols[model]]
                })
            
            # V4 vs V5
            if v4_pred != v5_pred:
                changed_v4_v5.append({
                    **base_data,
                    'v4_prediction': v4_pred,
                    'v5_prediction': v5_pred,
                    'v4_correct': v4.loc[idx, model_correct_cols[model]],
                    'v5_correct': v5.loc[idx, model_correct_cols[model]]
                })
            
            # V3 vs V5
            if v3_pred != v5_pred:
                changed_v3_v5.append({
                    **base_data,
                    'v3_prediction': v3_pred,
                    'v5_prediction': v5_pred,
                    'v3_correct': v3.loc[idx, model_correct_cols[model]],
                    'v5_correct': v5.loc[idx, model_correct_cols[model]]
                })
        
        differences_v3_v4[model] = changed_v3_v4
        differences_v4_v5[model] = changed_v4_v5
        differences_v3_v5[model] = changed_v3_v5
        
        # Calculate accuracy for all versions
        v3_accuracy = (v3[model_correct_cols[model]].sum() / len(v3)) * 100
        v4_accuracy = (v4[model_correct_cols[model]].sum() / len(v4)) * 100
        v5_accuracy = (v5[model_correct_cols[model]].sum() / len(v5)) * 100
        
        print(f"V3 Accuracy: {v3_accuracy:.2f}% ({v3[model_correct_cols[model]].sum()}/{len(v3)})")
        print(f"V4 Accuracy: {v4_accuracy:.2f}% ({v4[model_correct_cols[model]].sum()}/{len(v4)})")
        print(f"V5 Accuracy: {v5_accuracy:.2f}% ({v5[model_correct_cols[model]].sum()}/{len(v5)})")
        print(f"\nV3→V4 Change: {v4_accuracy - v3_accuracy:+.2f}%")
        print(f"V4→V5 Change: {v5_accuracy - v4_accuracy:+.2f}%")
        print(f"V3→V5 Change: {v5_accuracy - v3_accuracy:+.2f}%")
        print(f"\nNumber of changed predictions (V3→V4): {len(changed_v3_v4)}")
        print(f"Number of changed predictions (V4→V5): {len(changed_v4_v5)}")
        print(f"Number of changed predictions (V3→V5): {len(changed_v3_v5)}")
        
        # Show V4→V5 changes (most recent)
        if changed_v4_v5:
            print(f"\nChanged Questions (V4→V5):")
            print("-" * 80)
            
            for i, change in enumerate(changed_v4_v5[:10], 1):  # Show first 10
                print(f"\n{i}. ID: {change['id']}")
                print(f"   Question: {change['question']}")
                print(f"   Correct Answer: {change['correct']}")
                print(f"   Options:")
                print(f"      A: {change['option_A']}")
                print(f"      B: {change['option_B']}")
                print(f"      C: {change['option_C']}")
                print(f"      D: {change['option_D']}")
                print(f"   V4 Prediction: {change['v4_prediction']} ({'✓' if change['v4_correct'] else '✗'})")
                print(f"   V5 Prediction: {change['v5_prediction']} ({'✓' if change['v5_correct'] else '✗'})")
                
                if change['v4_correct'] and not change['v5_correct']:
                    print(f"   ⚠️  REGRESSION: V5 got it wrong (was correct in V4)")
                elif not change['v4_correct'] and change['v5_correct']:
                    print(f"   ✅ IMPROVEMENT: V5 got it right (was wrong in V4)")
                else:
                    print(f"   ↔️  CHANGE: Still {'correct' if change['v5_correct'] else 'wrong'}")
            
            if len(changed_v4_v5) > 10:
                print(f"\n... and {len(changed_v4_v5) - 10} more changes (see detailed report)")
    
    return v3, v4, v5, differences_v3_v4, differences_v4_v5, differences_v3_v5


def generate_summary_report(v3, v4, v5, differences_v3_v4, differences_v4_v5, differences_v3_v5):
    """Generate a comprehensive summary report."""
    
    print("\n\n")
    print("="*80)
    print("COMPREHENSIVE SUMMARY REPORT (V3 vs V4 vs V5)")
    print("="*80)
    
    models = ['baseline', 'rag_basic', 'full_system']
    model_correct_cols = {
        'baseline': 'baseline_correct',
        'rag_basic': 'rag_correct',
        'full_system': 'full_correct'
    }
    
    # Overall statistics
    print("\n1. OVERALL ACCURACY COMPARISON")
    print("-" * 80)
    print(f"{'Model':<20} {'V3 Acc':<12} {'V4 Acc':<12} {'V5 Acc':<12} {'V3→V4':<10} {'V4→V5':<10} {'V3→V5':<10}")
    print("-" * 80)
    
    for model in models:
        v3_acc = (v3[model_correct_cols[model]].sum() / len(v3)) * 100
        v4_acc = (v4[model_correct_cols[model]].sum() / len(v4)) * 100
        v5_acc = (v5[model_correct_cols[model]].sum() / len(v5)) * 100
        change_v3_v4 = v4_acc - v3_acc
        change_v4_v5 = v5_acc - v4_acc
        change_v3_v5 = v5_acc - v3_acc
        
        print(f"{model:<20} {v3_acc:>6.2f}% {v4_acc:>6.2f}% {v5_acc:>6.2f}% "
              f"{change_v3_v4:>+6.2f}% {change_v4_v5:>+6.2f}% {change_v3_v5:>+6.2f}%")
    
    # Changes summary
    print("\n\n2. PREDICTION CHANGES SUMMARY")
    print("-" * 80)
    print("V3→V4 Changes:")
    print(f"{'Model':<20} {'Total':<10} {'Improved':<10} {'Regressed':<10}")
    print("-" * 80)
    
    for model in models:
        total_changes = len(differences_v3_v4[model])
        improvements = sum(1 for c in differences_v3_v4[model] 
                          if not c['v3_correct'] and c['v4_correct'])
        regressions = sum(1 for c in differences_v3_v4[model] 
                         if c['v3_correct'] and not c['v4_correct'])
        
        print(f"{model:<20} {total_changes:<10} {improvements:<10} {regressions:<10}")
    
    print("\nV4→V5 Changes:")
    print(f"{'Model':<20} {'Total':<10} {'Improved':<10} {'Regressed':<10}")
    print("-" * 80)
    
    for model in models:
        total_changes = len(differences_v4_v5[model])
        improvements = sum(1 for c in differences_v4_v5[model] 
                          if not c['v4_correct'] and c['v5_correct'])
        regressions = sum(1 for c in differences_v4_v5[model] 
                         if c['v4_correct'] and not c['v5_correct'])
        
        print(f"{model:<20} {total_changes:<10} {improvements:<10} {regressions:<10}")
    
    print("\nV3→V5 Changes (Overall):")
    print(f"{'Model':<20} {'Total':<10} {'Improved':<10} {'Regressed':<10}")
    print("-" * 80)
    
    for model in models:
        total_changes = len(differences_v3_v5[model])
        improvements = sum(1 for c in differences_v3_v5[model] 
                          if not c['v3_correct'] and c['v5_correct'])
        regressions = sum(1 for c in differences_v3_v5[model] 
                         if c['v3_correct'] and not c['v5_correct'])
        
        print(f"{model:<20} {total_changes:<10} {improvements:<10} {regressions:<10}")
    
    # Question-level analysis
    print("\n\n3. QUESTIONS WITH ANY CHANGES ACROSS MODELS")
    print("-" * 80)
    
    all_changed_ids_v3_v4 = set()
    all_changed_ids_v4_v5 = set()
    all_changed_ids_v3_v5 = set()
    
    for model in models:
        all_changed_ids_v3_v4.update(c['id'] for c in differences_v3_v4[model])
        all_changed_ids_v4_v5.update(c['id'] for c in differences_v4_v5[model])
        all_changed_ids_v3_v5.update(c['id'] for c in differences_v3_v5[model])
    
    print(f"V3→V4: {len(all_changed_ids_v3_v4)} questions changed")
    print(f"V4→V5: {len(all_changed_ids_v4_v5)} questions changed")
    print(f"V3→V5: {len(all_changed_ids_v3_v5)} questions changed overall")
    
    if all_changed_ids_v4_v5:
        print(f"\nV4→V5 Changed Question IDs: {', '.join(sorted(list(all_changed_ids_v4_v5)[:20]))}...")
    
    # Model agreement analysis
    print("\n\n4. MODEL AGREEMENT ANALYSIS")
    print("-" * 80)
    
    # V3 agreement
    v3_all_correct = ((v3['baseline_correct']) & 
                      (v3['rag_correct']) & 
                      (v3['full_correct'])).sum()
    
    # V4 agreement
    v4_all_correct = ((v4['baseline_correct']) & 
                      (v4['rag_correct']) & 
                      (v4['full_correct'])).sum()
    
    # V5 agreement
    v5_all_correct = ((v5['baseline_correct']) & 
                      (v5['rag_correct']) & 
                      (v5['full_correct'])).sum()
    
    print(f"V3: All three models correct: {v3_all_correct}/{len(v3)} ({v3_all_correct/len(v3)*100:.2f}%)")
    print(f"V4: All three models correct: {v4_all_correct}/{len(v4)} ({v4_all_correct/len(v4)*100:.2f}%)")
    print(f"V5: All three models correct: {v5_all_correct}/{len(v5)} ({v5_all_correct/len(v5)*100:.2f}%)")
    print(f"\nV3→V4 Change: {v4_all_correct - v3_all_correct:+d} questions ({(v4_all_correct - v3_all_correct)/len(v3)*100:+.2f}%)")
    print(f"V4→V5 Change: {v5_all_correct - v4_all_correct:+d} questions ({(v5_all_correct - v4_all_correct)/len(v4)*100:+.2f}%)")
    print(f"V3→V5 Change: {v5_all_correct - v3_all_correct:+d} questions ({(v5_all_correct - v3_all_correct)/len(v3)*100:+.2f}%)")
    
    # Detailed breakdown by question type
    print("\n\n5. V4→V5 CHANGES BY COUNTRY/LANGUAGE")
    print("-" * 80)
    
    for model in models:
        if differences_v4_v5[model]:
            print(f"\n{model.upper()}:")
            country_changes = defaultdict(int)
            for change in differences_v4_v5[model]:
                country_code = change['id'].split('_')[0]
                country_changes[country_code] += 1
            
            for country, count in sorted(country_changes.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count} changes")


def save_detailed_report(differences_v3_v4, differences_v4_v5, differences_v3_v5):
    """Save detailed differences to CSV files."""
    
    print("\n\n6. SAVING DETAILED REPORTS TO FILES")
    print("-" * 80)
    
    models = ['baseline', 'rag_basic', 'full_system']
    
    # Save V3→V4 changes
    rows_v3_v4 = []
    for model in models:
        for change in differences_v3_v4[model]:
            rows_v3_v4.append({
                'model': model,
                'id': change['id'],
                'question': change['question'],
                'correct_answer': change['correct'],
                'v3_prediction': change['v3_prediction'],
                'v4_prediction': change['v4_prediction'],
                'v3_correct': change['v3_correct'],
                'v4_correct': change['v4_correct'],
                'change_type': 'improvement' if (not change['v3_correct'] and change['v4_correct']) else
                               'regression' if (change['v3_correct'] and not change['v4_correct']) else
                               'lateral'
            })
    
    if rows_v3_v4:
        df = pd.DataFrame(rows_v3_v4)
        df.to_csv('version_comparison_v3_v4.csv', index=False)
        print(f"V3→V4 report saved to: version_comparison_v3_v4.csv ({len(rows_v3_v4)} changes)")
    
    # Save V4→V5 changes
    rows_v4_v5 = []
    for model in models:
        for change in differences_v4_v5[model]:
            rows_v4_v5.append({
                'model': model,
                'id': change['id'],
                'question': change['question'],
                'correct_answer': change['correct'],
                'v4_prediction': change['v4_prediction'],
                'v5_prediction': change['v5_prediction'],
                'v4_correct': change['v4_correct'],
                'v5_correct': change['v5_correct'],
                'change_type': 'improvement' if (not change['v4_correct'] and change['v5_correct']) else
                               'regression' if (change['v4_correct'] and not change['v5_correct']) else
                               'lateral'
            })
    
    if rows_v4_v5:
        df = pd.DataFrame(rows_v4_v5)
        df.to_csv('version_comparison_v4_v5.csv', index=False)
        print(f"V4→V5 report saved to: version_comparison_v4_v5.csv ({len(rows_v4_v5)} changes)")
    
    # Save V3→V5 changes
    rows_v3_v5 = []
    for model in models:
        for change in differences_v3_v5[model]:
            rows_v3_v5.append({
                'model': model,
                'id': change['id'],
                'question': change['question'],
                'correct_answer': change['correct'],
                'v3_prediction': change['v3_prediction'],
                'v5_prediction': change['v5_prediction'],
                'v3_correct': change['v3_correct'],
                'v5_correct': change['v5_correct'],
                'change_type': 'improvement' if (not change['v3_correct'] and change['v5_correct']) else
                               'regression' if (change['v3_correct'] and not change['v5_correct']) else
                               'lateral'
            })
    
    if rows_v3_v5:
        df = pd.DataFrame(rows_v3_v5)
        df.to_csv('version_comparison_v3_v5.csv', index=False)
        print(f"V3→V5 report saved to: version_comparison_v3_v5.csv ({len(rows_v3_v5)} changes)")


def main():
    """Main execution function."""
    
    print("="*80)
    print("PREDICTION VERSION COMPARISON TOOL")
    print("Comparing: V3 vs V4 vs V5")
    print("="*80)
    print()
    
    # Load and compare
    v3, v4, v5, differences_v3_v4, differences_v4_v5, differences_v3_v5 = load_and_compare()
    
    # Generate summary report
    generate_summary_report(v3, v4, v5, differences_v3_v4, differences_v4_v5, differences_v3_v5)
    
    # Save detailed report
    save_detailed_report(differences_v3_v4, differences_v4_v5, differences_v3_v5)
    
    print("\n\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("Files saved: version_comparison_v3_v4.csv, version_comparison_v4_v5.csv, version_comparison_v3_v5.csv")
    print("="*80)


if __name__ == "__main__":
    main()
