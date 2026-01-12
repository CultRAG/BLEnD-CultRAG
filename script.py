# [Crucible] FINAL SCORECARD GENERATOR
import pandas as pd
import os

# --- CONFIGURATION ---
TRUTH_FILE = "docs/answers.tsv"  # Ground truth file
QUESTIONS_FILE = "questions.tsv"  # Add questions file
PRED_FILES = {
    "Baseline (No RAG)": "output-with-v5/kaggle/working/all_predictions/submission_baseline_no_rag.tsv",
    "Phase 1: Country Filter": "output-with-v5/kaggle/working/all_predictions/submission_phase1_country_filter.tsv",
    "Phase 2: Intent": "output-with-v5/kaggle/working/all_predictions/submission_phase2_intent.tsv",
    "Phase 3: Tiered": "output-with-v5/kaggle/working/all_predictions/submission_phase3_tiered.tsv",
    "Phase 4: Quality": "output-with-v5/kaggle/working/all_predictions/submission_phase4_quality.tsv",
    "Phase 5: Trust Weight": "output-with-v5/kaggle/working/all_predictions/submission_phase5_trust_weight.tsv",
    "Phase 6: Full System": "output-with-v5/kaggle/working/all_predictions/submission_phase6_full_system.tsv",
    "RAG Basic": "output-with-v5/kaggle/working/all_predictions/submission_rag_basic.tsv"
}

def load_truth(filepath):
    """Robustly load truth file (handles headers or no headers)"""
    if not os.path.exists(filepath):
        print(f"❌ MISSING: {filepath} (Please upload it!)")
        return {}
    
    # Try reading with header inference
    df = pd.read_csv(filepath, sep='\t')
    
    # Heuristic: If first column isn't 'id', assume no header
    if 'id' not in df.columns or 'answer' not in df.columns:
        df = pd.read_csv(filepath, sep='\t', header=None, names=['id', 'answer'])
    
    # Normalize: Uppercase and strip
    truth_dict = {}
    for _, row in df.iterrows():
        truth_dict[str(row['id']).strip()] = str(row['answer']).strip().upper()
    return truth_dict

def evaluate_predictions(name, pred_path, truth_dict):
    if not os.path.exists(pred_path):
        print(f"⚠️  Skipping {name}: File not found ({pred_path})")
        return None

    # Load predictions (assuming no header based on your checkpoints)
    try:
        df = pd.read_csv(pred_path, sep='\t', header=None, names=['id', 'prediction'])
    except:
        print(f"⚠️  Error reading {pred_path}")
        return None

    correct = 0
    total = 0
    detailed_results = []

    for _, row in df.iterrows():
        qid = str(row['id']).strip()
        pred = str(row['prediction']).strip().upper()
        
        if qid in truth_dict:
            is_correct = (pred == truth_dict[qid])
            correct += 1 if is_correct else 0
            total += 1
            detailed_results.append({
                'id': qid,
                'correct': is_correct,
                'pred': pred,
                'truth': truth_dict[qid]
            })
    
    accuracy = correct / total if total > 0 else 0
    return {
        'name': name,
        'accuracy': accuracy,
        'correct': correct,
        'total': total,
        'details': detailed_results
    }

# --- EXECUTION ---
print("📊 FINAL EVALUATION REPORT")
print("="*60)

truth_data = load_truth(TRUTH_FILE)
if not truth_data:
    raise ValueError("Cannot proceed without Ground Truth.")

results = []
for name, path in PRED_FILES.items():
    res = evaluate_predictions(name, path, truth_data)
    if res:
        results.append(res)
        print(f"🔹 {name:20s} | Accuracy: {res['accuracy']:.2%} ({res['correct']}/{res['total']})")

# --- COMPARATIVE ANALYSIS (Where did RAG help?) ---
if len(results) >= 2:
    print("\n🔍 IMPACT ANALYSIS (Baseline vs Best RAG)")
    print("="*60)
    
    baseline = results[0] # Assuming first is baseline
    best_rag = max(results[1:], key=lambda x: x['accuracy'])
    
    # Convert to dict lookup
    base_map = {d['id']: d['correct'] for d in baseline['details']}
    rag_map = {d['id']: d['correct'] for d in best_rag['details']}
    
    fixed_count = 0
    broken_count = 0
    
    for qid, base_correct in base_map.items():
        if qid in rag_map:
            rag_correct = rag_map[qid]
            if not base_correct and rag_correct:
                fixed_count += 1
            elif base_correct and not rag_correct:
                broken_count += 1
                
    print(f"✅ RAG Fixed: {fixed_count} questions (Baseline Wrong -> RAG Right)")
    print(f"❌ RAG Broke: {broken_count} questions (Baseline Right -> RAG Wrong)")
    print(f"📈 Net Gain:  {fixed_count - broken_count} questions")

# --- EXPORT CORRECTLY ANSWERED QUESTIONS ---
print("\n💾 EXPORTING CORRECT ANSWERS TO FILES")
print("="*60)

# Load questions file if available
questions_df = None
if os.path.exists(QUESTIONS_FILE):
    try:
        questions_df = pd.read_csv(QUESTIONS_FILE, sep='\t')
        print(f"✅ Loaded questions from {QUESTIONS_FILE}")
    except Exception as e:
        print(f"⚠️ Could not load questions file: {e}")
else:
    print(f"⚠️ Questions file not found: {QUESTIONS_FILE}")

# Export correct answers for each method
for result in results:
    name = result['name']
    safe_name = name.replace(" ", "_").replace("(", "").replace(")", "").lower()
    output_file = f"correct_answers_{safe_name}.tsv"
    
    # Get correct predictions
    correct_ids = [d['id'] for d in result['details'] if d['correct']]
    
    if questions_df is not None and len(correct_ids) > 0:
        # Filter questions that were answered correctly
        correct_questions = questions_df[questions_df['id'].isin(correct_ids)].copy()
        
        # Add prediction and truth columns
        correct_questions['prediction'] = correct_questions['id'].map(
            {d['id']: d['pred'] for d in result['details'] if d['correct']}
        )
        correct_questions['truth'] = correct_questions['id'].map(
            {d['id']: d['truth'] for d in result['details'] if d['correct']}
        )
        
        # Save to file
        correct_questions.to_csv(output_file, sep='\t', index=False)
        print(f"✅ {name:20s} | {len(correct_ids):3d} correct → {output_file}")
    else:
        # If no questions file, just save IDs
        correct_df = pd.DataFrame({
            'id': correct_ids,
            'prediction': [d['pred'] for d in result['details'] if d['correct']],
            'truth': [d['truth'] for d in result['details'] if d['correct']]
        })
        correct_df.to_csv(output_file, sep='\t', index=False)
        print(f"✅ {name:20s} | {len(correct_ids):3d} correct → {output_file} (IDs only)")

print("\n🎉 EVALUATION COMPLETE!")
print(f"📁 Files created: correct_answers_*.tsv")