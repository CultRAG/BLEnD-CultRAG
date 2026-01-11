# Comparison Results

This folder contains all comparison analysis between different output versions (v2, v3, v4).

## 📁 Files in This Folder

### Main Comparison Files
- **`comparison_by_country.csv`** - Side-by-side accuracy comparison for each country across versions
- **`comparison_by_intent.csv`** - Side-by-side accuracy comparison for each question intent
- **`common_errors_all_versions.csv`** - Errors that persist across all versions (25 persistent errors)
- **`combined_error_analysis_report.json`** - Combined JSON reports from all versions

### Change Tracking Files (v3→v4)
- **`prediction_changes_v3_to_v4.csv`** - All questions where predictions changed (10 total changes)
- **`predictions_improved_v3_to_v4.csv`** - Questions wrong in v3 but correct in v4 (3 improvements)
- **`predictions_degraded_v3_to_v4.csv`** - Questions correct in v3 but wrong in v4 (3 degradations)

## 🎯 Key Findings (v3→v4 Comparison)

### Countries - Biggest Changes

**✅ Improved:**
- 🇱🇰 **Sri Lanka (LK)**: 71.4% → 85.7% (+14.3%)
- 🇪🇨 **Ecuador (EC)**: 37.5% → 50.0% (+12.5%)

**❌ Degraded:**
- 🇸🇦 **Saudi Arabia (SA)**: 42.9% → 28.6% (-14.3%)
- 🇵🇭 **Philippines (PH)**: 100.0% → 87.5% (-12.5%)

### Intents - Biggest Changes

**✅ Improved:**
- **geography_places**: 75.0% → 87.5% (+12.5%)
- **economy_currency_symbols**: 66.7% → 75.0% (+8.3%)

**❌ Degraded:**
- **culture_landmarks**: 100.0% → 75.0% (-25.0%)
- **language_writing**: 80.0% → 60.0% (-20.0%)
- **holidays_festivals**: 95.5% → 90.9% (-4.5%)

### Overall Statistics
- **v3 Mean Accuracy (Country)**: 79.77%
- **v4 Mean Accuracy (Country)**: 79.77%
- **v3 Mean Accuracy (Intent)**: 78.89%
- **v4 Mean Accuracy (Intent)**: 76.28%
- **16 countries** remained unchanged between versions
- **25 persistent errors** across all versions

### Method Performance (v4)
| Method | Accuracy | Notes |
|--------|----------|-------|
| baseline_no_rag | 83.78% | No RAG retrieval |
| rag_basic | 85.81% | Basic RAG (+2.03% vs baseline) |
| phase1_country_filter | 83.11% | Country filtering |
| phase2_intent | 83.11% | Intent classification |
| phase3_tiered | 81.76% | Tiered retrieval |
| phase4_quality | 81.08% | Quality filtering |
| phase5_trust_weight | 81.08% | Trust-based weighting |
| phase6_full_system | 81.08% | Complete system |

## 📊 Usage

### View All Results
```bash
# From workspace root
python view_comparison_results.py
```

### Re-generate Comparisons
```bash
# From workspace root
python compare_outputs.py
```

All files will be generated/updated in this `comparison_results/` folder.

## 🔍 What to Investigate

### Priority 1: Degradations
Look at `predictions_degraded_v3_to_v4.csv` to understand why these 3 questions got worse:
- el-GR_062 (Greece - October 28 celebration)
- ar-SA_089 (Saudi Arabia - Masmak Palace)
- tl-PH_132 (Philippines - Language Month)

### Priority 2: Persistent Errors
Check `common_errors_all_versions.csv` for the 25 errors that fail in all versions:
- **Top problematic countries**: FR (5), SA (4), EC (4), BG (3)
- **Top problematic intents**: Analyze distribution

### Priority 3: Country-Specific Issues
Focus on countries with low accuracy:
- **Saudi Arabia (SA)**: 28.6% - worst performer & degraded
- **France (FR)**: 37.5% - consistently low
- **Ecuador (EC)**: 50.0% - improved but still below average
- **Bulgaria (BG)**: 57.1% - below average
- **South Korea (KR)**: 60.0% - below average

### Priority 4: Intent-Specific Issues
Focus on intents with low accuracy or degradation:
- **history_identity**: 50.0% - lowest accuracy
- **sports**: 62.5% - second lowest
- **language_writing**: 60.0% - degraded by 20%
- **culture_landmarks**: 75.0% - degraded by 25%

## 📈 Recommendations

1. **Add more sources for problematic countries** (FR, SA, EC, BG, KR)
2. **Improve culture_landmarks intent** - Investigate why it degraded significantly
3. **Fix the 25 persistent errors** - These are fundamental knowledge gaps
4. **Investigate Saudi Arabia degradation** - From 42.9% to 28.6% is significant
5. **Analyze why basic RAG (85.81%) outperforms full system (81.08%)** - Additional phases may be hurting performance

## 🔗 Related Files

### Source Data (Input)
- `../output-with-v2/kaggle/working/` - Version 2 results (if available)
- `../output-with-v3/kaggle/working/` - Version 3 results
- `../output-with-v4/kaggle/working/` - Version 4 results

### Scripts (Workspace Root)
- `../compare_outputs.py` - Main comparison script
- `../view_comparison_results.py` - Results viewer script

---

**Last Updated**: 2026-01-11  
**Versions Compared**: v3, v4 (v2 not available)
