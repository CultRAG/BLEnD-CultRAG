import pandas as pd

# List of problematic IDs mentioned in the summary (estimated mapping)
# The summary used IDs like es-EC_023, but the file might have es-EC_0023 or similar.
# Let's search for the suffixes.

suffixes = ["023", "025", "026", "029", "039", "049", "056", "058", "059", "062", "067", "074", "084", "085", "088", "100", "104", "105", "108", "110", "111", "112", "124", "136", "138", "140"]

questions_df = pd.read_csv('blend_data/questions.tsv', sep='\t')
answers_df = pd.read_csv('blend_data/answers.tsv', sep='\t')

# Merge to get the correct answer
df = questions_df.merge(answers_df, on='id')

results = []
for suffix in suffixes:
    # Match if id ends with suffix (allowing for padding)
    match = df[df['id'].str.contains(f'_{suffix}$', regex=True) | df['id'].str.contains(f'_0{suffix}$', regex=True)]
    if not match.empty:
        for _, row in match.iterrows():
            results.append({
                'id': row['id'],
                'question': row['question'],
                'correct_option': row['answer'],
                'correct_text': row[f"option_{row['answer']}"]
            })

for res in results:
    print(f"ID: {res['id']}")
    print(f"Q: {res['question']}")
    print(f"A: {res['correct_text']} ({res['correct_option']})")
    print("-" * 20)
