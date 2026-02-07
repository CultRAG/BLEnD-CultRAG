import json

# Read the notebook
nb_path = r'c:\Users\LawLight\OneDrive\Desktop\semevals\semeval-task-7 (10).ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find the last cell
last_cell = nb['cells'][-1]

print(f"Last cell ID: {last_cell.get('id', 'N/A')}")
print(f"Current source lines: {len(last_cell['source'])}")
print("Current content:")
print(''.join(last_cell['source']))

# Update the last cell
new_source = [
    't0 = tic("Cell 62: Final Summary")\n',
    '\n',
    '# ============================================================================\n',
    '# NOTEBOOK EXECUTION SUMMARY\n',
    '# ============================================================================\n',
    '\n',
    'print("\\n" + "="*80)\n',
    'print("📊 NOTEBOOK EXECUTION COMPLETE")\n',
    'print("="*80)\n',
    '\n',
    '# Get total elapsed time\n',
    'total_seconds, minutes, seconds = get_total_elapsed()\n',
    '\n',
    'print(f"\\n⏱️  Total Execution Time:")\n',
    'print(f"   ├─ Total: {total_seconds:.2f} seconds")\n',
    'print(f"   ├─ Formatted: {minutes} minutes {seconds:.2f} seconds")\n',
    'print(f"   └─ Hours: {total_seconds/3600:.2f} hours")\n',
    '\n',
    'print(f"\\n📅 Completion Time: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")\n',
    '\n',
    'print("\\n" + "="*80)\n',
    'print("✅ All cells executed successfully!")\n',
    'print("="*80)\n',
    '\n',
    'toc("Cell 62: Final Summary", t0)\n'
]

last_cell['source'] = new_source

# Save the notebook
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("\n✅ Last cell updated successfully!")
print(f"New source lines: {len(new_source)}")
