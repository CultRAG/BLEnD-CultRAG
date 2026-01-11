# Output Comparison Tools

Tools to compare error analysis results across different output versions (v2, v3, v4).

## Generated Files

After running the comparison, the following files are created in the workspace root:

### Main Comparison Files
- **`comparison_by_country.csv`** - Side-by-side accuracy comparison for each country
- **`comparison_by_intent.csv`** - Side-by-side accuracy comparison for each question intent
- **`common_errors_all_versions.csv`** - Errors that persist across all versions
- **`combined_error_analysis_report.json`** - Combined JSON reports from all versions

### Change Tracking Files (v3→v4)
- **`prediction_changes_v3_to_v4.csv`** - All questions where predictions changed
- **`predictions_improved_v3_to_v4.csv`** - Questions that were wrong in v3 but correct in v4
- **`predictions_degraded_v3_to_v4.csv`** - Questions that were correct in v3 but wrong in v4

## Usage

### 1. Run Full Comparison
```bash
python compare_outputs.py
```

This script:
- Compares error_analysis_by_country.csv across versions
- Compares error_analysis_by_intent.csv across versions
- Compares error_cases_detailed.csv to find common/fixed/new errors
- Compares error_analysis_report.json metrics
- Compares predictions_all_methods_combined.csv to track prediction changes
- Generates all comparison CSV files

### 2. View Results Summary
```bash
python view_comparison_results.py
```

This script provides a readable summary:
- Countries that improved/degraded between versions
- Intents that improved/degraded
- Specific questions that changed predictions
- Common errors that persist across versions

## Key Insights from Latest Run (v3→v4)

### Overall Statistics
- **v3 Mean Accuracy by Country**: 79.77%
- **v4 Mean Accuracy by Country**: 79.77%
- **v3 Mean Accuracy by Intent**: 78.89%
- **v4 Mean Accuracy by Intent**: 76.28%

### Method-wise Performance (v4)
| Method | Accuracy |
|--------|----------|
| baseline_no_rag | 83.78% |
| rag_basic | 85.81% |
| phase1_country_filter | 83.11% |
| phase2_intent | 83.11% |
| phase3_tiered | 81.76% |
| phase4_quality | 81.08% |
| phase5_trust_weight | 81.08% |
| phase6_full_system | 81.08% |

### Countries - Biggest Changes

**Improved (v3→v4)**:
- 🇱🇰 **LK (Sri Lanka)**: 71.4% → 85.7% (+14.3%)
- 🇪🇨 **EC (Ecuador)**: 37.5% → 50.0% (+12.5%)

**Degraded (v3→v4)**:
- 🇸🇦 **SA (Saudi Arabia)**: 42.9% → 28.6% (-14.3%)
- 🇵🇭 **PH (Philippines)**: 100.0% → 87.5% (-12.5%)

### Intents - Biggest Changes

**Improved (v3→v4)**:
- **geography_places**: 75.0% → 87.5% (+12.5%)
- **economy_currency_symbols**: 66.7% → 75.0% (+8.3%)

**Degraded (v3→v4)**:
- **culture_landmarks**: 100.0% → 75.0% (-25.0%)
- **language_writing**: 80.0% → 60.0% (-20.0%)
- **holidays_festivals**: 95.5% → 90.9% (-4.5%)

### Prediction Changes
- **Total Changed**: 10 questions
- **Improved** (wrong→correct): 3 questions
- **Degraded** (correct→wrong): 3 questions
- **Other Changes**: 4 questions (both wrong or both correct but different prediction)

### Persistent Errors
- **25 common errors** across all versions
- **Top problematic countries**: FR (5), SA (4), EC (4), BG (3)
- **Top problematic intents**: Need to analyze error distribution

## File Locations

### Input Files (Expected Structure)
```
output-with-v2/kaggle/working/
├── error_analysis_by_country.csv
├── error_analysis_by_intent.csv
├── error_cases_detailed.csv
├── error_analysis_report.json
└── predictions_all_methods_combined.csv

output-with-v3/kaggle/working/
├── [same structure]

output-with-v4/kaggle/working/
├── [same structure]
```

### Output Files (Workspace Root)
```
comparison_by_country.csv
comparison_by_intent.csv
common_errors_all_versions.csv
combined_error_analysis_report.json
prediction_changes_v3_to_v4.csv
predictions_improved_v3_to_v4.csv
predictions_degraded_v3_to_v4.csv
```

## Analysis Tips

1. **Focus on Persistent Errors**: Check `common_errors_all_versions.csv` to find questions that fail across all versions - these need fundamental fixes

2. **Investigate Degradations**: Look at `predictions_degraded_v3_to_v4.csv` to understand what changes caused regressions

3. **Learn from Improvements**: Examine `predictions_improved_v3_to_v4.csv` to see what changes helped

4. **Country-Specific Issues**: Use `comparison_by_country.csv` to identify which countries need more/better source documents

5. **Intent-Specific Issues**: Use `comparison_by_intent.csv` to see which question types are problematic

## Troubleshooting

**Missing v2 folder**: The scripts are designed to work even if v2 folder doesn't exist. They'll compare only v3 and v4.

**Different column names**: If your prediction files have different column structures, you may need to update the script's column detection logic.

**Large files**: For very large datasets, consider adding pagination or filtering to the view script.

## Next Steps

1. Run full error analysis on current best version
2. Focus on fixing the 25 persistent errors
3. Investigate why Saudi Arabia degraded significantly
4. Improve culture_landmarks and language_writing intents
5. Add more high-quality sources for problematic countries (FR, SA, EC)
