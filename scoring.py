import json
import pandas as pd
from pathlib import Path

print('Task 2: Multiple-Choice Questions (MCQ)')
print('=' * 60)

ROOT = Path(__file__).resolve().parent
submission_dir = ROOT / 'submission' / 'final_submission'
reference_path = submission_dir / 'final_2_mcq_reference.tsv'

print('Reading reference data...')
df_reference = pd.read_csv(reference_path, sep='\t')
df_reference['language_region'] = df_reference['id'].apply(lambda x: x.split('_')[0])
unique_language_regions = df_reference['language_region'].unique()


def score(df_truth, df_pred, verbose=False):
    correct = 0

    if df_pred['id'].duplicated().any():
        df_pred = df_pred.drop_duplicates(subset='id', keep='last')

    pred_map = df_pred.set_index('id')[['A', 'B', 'C', 'D']].to_dict(orient='index')

    for i, row_truth in df_truth.iterrows():
        qid = row_truth['id']

        if qid not in pred_map:
            continue

        row_pred = pred_map[qid]

        if not all(x in [0, 1] for x in row_pred.values()):
            continue

        if sum(row_pred.values()) != 1:
            continue

        if row_pred[row_truth['answer']] == 1:
            correct += 1

    accuracy = 100 * correct / len(df_truth)
    return accuracy


def score_overall(df_ref, df_pred):
    """Compute macro-averaged overall score (average of per-language scores)."""
    lang_scores = {}
    for lang_region in df_ref['language_region'].unique():
        df_ref_group = df_ref[df_ref['language_region'] == lang_region]
        lang_scores[str(lang_region)] = score(df_ref_group, df_pred)
    overall = sum(lang_scores.values()) / len(lang_scores)
    return overall


# Find all prediction one-hot files
prediction_files = sorted(submission_dir.glob('predictions_*_onehot.tsv'))

print(f'Reference: {len(df_reference)} questions, {len(unique_language_regions)} languages')
print(f'Prediction files found: {len(prediction_files)}')
print('=' * 60)

all_scores = {}

for pred_file in prediction_files:
    # Extract config name from filename: predictions_<config>_onehot.tsv
    config_name = pred_file.stem.replace('predictions_', '').replace('_onehot', '')

    df_pred = pd.read_csv(pred_file, sep='\t')

    if {'id', 'A', 'B', 'C', 'D'} - set(df_pred.columns):
        print(f'  SKIP {config_name}: missing required columns')
        continue

    overall = score_overall(df_reference, df_pred)
    all_scores[config_name] = round(overall, 4)
    print(f'  {config_name:<35s}  {overall:.2f}%')

print('=' * 60)

# Sort by score descending
ranked = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
print('\nRanked Results:')
for i, (name, sc) in enumerate(ranked, 1):
    print(f'  {i}. {name:<35s}  {sc:.2f}%')

# Save
output = {'per_config': all_scores, 'ranked': [{'config': n, 'overall': s} for n, s in ranked]}
with open(submission_dir / 'scores.json', 'w') as f:
    json.dump(output, f, indent=4)
print(f'\nScores saved to {submission_dir / "scores.json"}')
