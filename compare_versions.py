import pandas as pd
from collections import defaultdict

def load_and_compare():
    """Load both versions and perform comprehensive comparison."""
    
    # Load both CSV files
    print("Loading CSV files...")
    v3 = pd.read_csv('predictions-per-version/all_predictions_comparison-v3.csv')
    v4 = pd.read_csv('predictions-per-version/all_predictions_comparison-v4.csv')
    
    print(f"V3 has {len(v3)} questions")
    print(f"V4 has {len(v4)} questions")
    print()
    
    # Model types to compare
    models = ['baseline', 'rag_basic', 'full_system']
    model_correct_cols = {
        'baseline': 'baseline_correct',
        'rag_basic': 'rag_correct',
        'full_system': 'full_correct'
    }
    
    # Store all differences
    differences = defaultdict(list)
    
    # Compare each model
    for model in models:
        print(f"\n{'='*80}")
        print(f"ANALYZING MODEL: {model.upper()}")
        print(f"{'='*80}\n")
        
        # Find differences
        changed_questions = []
        for idx in range(len(v3)):
            v3_pred = v3.loc[idx, model]
            v4_pred = v4.loc[idx, model]
            
            if v3_pred != v4_pred:
                changed_questions.append({
                    'id': v3.loc[idx, 'id'],
                    'question': v3.loc[idx, 'question'],
                    'correct': v3.loc[idx, 'correct'],
                    'v3_prediction': v3_pred,
                    'v4_prediction': v4_pred,
                    'v3_correct': v3.loc[idx, model_correct_cols[model]],
                    'v4_correct': v4.loc[idx, model_correct_cols[model]],
                    'option_A': v3.loc[idx, 'option_A'],
                    'option_B': v3.loc[idx, 'option_B'],
                    'option_C': v3.loc[idx, 'option_C'],
                    'option_D': v3.loc[idx, 'option_D']
                })
        
        differences[model] = changed_questions
        
        # Calculate accuracy for both versions
        v3_accuracy = (v3[model_correct_cols[model]].sum() / len(v3)) * 100
        v4_accuracy = (v4[model_correct_cols[model]].sum() / len(v4)) * 100
        
        print(f"V3 Accuracy: {v3_accuracy:.2f}% ({v3[model_correct_cols[model]].sum()}/{len(v3)})")
        print(f"V4 Accuracy: {v4_accuracy:.2f}% ({v4[model_correct_cols[model]].sum()}/{len(v4)})")
        print(f"Change: {v4_accuracy - v3_accuracy:+.2f}%")
        print(f"\nNumber of changed predictions: {len(changed_questions)}")
        
        if changed_questions:
            print(f"\nChanged Questions:")
            print("-" * 80)
            
            for i, change in enumerate(changed_questions, 1):
                print(f"\n{i}. ID: {change['id']}")
                print(f"   Question: {change['question']}")
                print(f"   Correct Answer: {change['correct']}")
                print(f"   Options:")
                print(f"      A: {change['option_A']}")
                print(f"      B: {change['option_B']}")
                print(f"      C: {change['option_C']}")
                print(f"      D: {change['option_D']}")
                print(f"   V3 Prediction: {change['v3_prediction']} ({'✓' if change['v3_correct'] else '✗'})")
                print(f"   V4 Prediction: {change['v4_prediction']} ({'✓' if change['v4_correct'] else '✗'})")
                
                if change['v3_correct'] and not change['v4_correct']:
                    print(f"   ⚠️  REGRESSION: V4 got it wrong (was correct in V3)")
                elif not change['v3_correct'] and change['v4_correct']:
                    print(f"   ✅ IMPROVEMENT: V4 got it right (was wrong in V3)")
                else:
                    print(f"   ↔️  CHANGE: Still {'correct' if change['v4_correct'] else 'wrong'}")
    
    return v3, v4, differences


def generate_summary_report(v3, v4, differences):
    """Generate a comprehensive summary report."""
    
    print("\n\n")
    print("="*80)
    print("COMPREHENSIVE SUMMARY REPORT")
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
    print(f"{'Model':<20} {'V3 Accuracy':<15} {'V4 Accuracy':<15} {'Change':<15}")
    print("-" * 80)
    
    for model in models:
        v3_acc = (v3[model_correct_cols[model]].sum() / len(v3)) * 100
        v4_acc = (v4[model_correct_cols[model]].sum() / len(v4)) * 100
        change = v4_acc - v3_acc
        
        print(f"{model:<20} {v3_acc:>6.2f}% ({v3[model_correct_cols[model]].sum():>3}/{len(v3):<3}) "
              f"{v4_acc:>6.2f}% ({v4[model_correct_cols[model]].sum():>3}/{len(v4):<3}) "
              f"{change:>+6.2f}%")
    
    # Changes summary
    print("\n\n2. PREDICTION CHANGES SUMMARY")
    print("-" * 80)
    print(f"{'Model':<20} {'Total Changes':<15} {'Improvements':<15} {'Regressions':<15}")
    print("-" * 80)
    
    for model in models:
        total_changes = len(differences[model])
        improvements = sum(1 for c in differences[model] 
                          if not c['v3_correct'] and c['v4_correct'])
        regressions = sum(1 for c in differences[model] 
                         if c['v3_correct'] and not c['v4_correct'])
        
        print(f"{model:<20} {total_changes:<15} {improvements:<15} {regressions:<15}")
    
    # Question-level analysis
    print("\n\n3. QUESTIONS WITH ANY CHANGES ACROSS MODELS")
    print("-" * 80)
    
    all_changed_ids = set()
    for model in models:
        all_changed_ids.update(c['id'] for c in differences[model])
    
    if all_changed_ids:
        print(f"Total questions with changes: {len(all_changed_ids)}")
        print(f"Question IDs: {', '.join(sorted(all_changed_ids))}")
    else:
        print("No questions changed between versions.")
    
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
    
    print(f"V3: All three models correct: {v3_all_correct}/{len(v3)} ({v3_all_correct/len(v3)*100:.2f}%)")
    print(f"V4: All three models correct: {v4_all_correct}/{len(v4)} ({v4_all_correct/len(v4)*100:.2f}%)")
    print(f"Change: {v4_all_correct - v3_all_correct:+d} questions ({(v4_all_correct - v3_all_correct)/len(v3)*100:+.2f}%)")
    
    # Detailed breakdown by question type
    print("\n\n5. CHANGES BY COUNTRY/LANGUAGE")
    print("-" * 80)
    
    for model in models:
        if differences[model]:
            print(f"\n{model.upper()}:")
            country_changes = defaultdict(int)
            for change in differences[model]:
                country_code = change['id'].split('_')[0]
                country_changes[country_code] += 1
            
            for country, count in sorted(country_changes.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count} changes")


def save_detailed_report(differences):
    """Save detailed differences to a CSV file."""
    
    print("\n\n6. SAVING DETAILED REPORT TO FILE")
    print("-" * 80)
    
    rows = []
    for model in ['baseline', 'rag_basic', 'full_system']:
        for change in differences[model]:
            rows.append({
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
    
    if rows:
        df = pd.DataFrame(rows)
        df.to_csv('version_comparison_report.csv', index=False)
        print(f"Detailed report saved to: version_comparison_report.csv")
        print(f"Total changes logged: {len(rows)}")
    else:
        print("No changes to report.")


def main():
    """Main execution function."""
    
    print("="*80)
    print("PREDICTION VERSION COMPARISON TOOL")
    print("Comparing: all_predictions_comparison-v3.csv vs all_predictions_comparison-v4.csv")
    print("="*80)
    print()
    
    # Load and compare
    v3, v4, differences = load_and_compare()
    
    # Generate summary report
    generate_summary_report(v3, v4, differences)
    
    # Save detailed report
    save_detailed_report(differences)
    
    print("\n\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
