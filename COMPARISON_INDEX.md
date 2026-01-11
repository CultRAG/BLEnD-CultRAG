# 📊 Comparison Results - Quick Access

All comparison files between output versions (v2, v3, v4) are organized in the **`comparison_results/`** folder.

## 📂 Folder Structure

```
comparison_results/
├── README.md                              # Detailed documentation
├── comparison_by_country.csv              # Country-wise accuracy comparison
├── comparison_by_intent.csv               # Intent-wise accuracy comparison
├── common_errors_all_versions.csv         # Persistent errors (25 cases)
├── combined_error_analysis_report.json    # Combined JSON reports
├── prediction_changes_v3_to_v4.csv        # All prediction changes
├── predictions_improved_v3_to_v4.csv      # Improvements (3 cases)
└── predictions_degraded_v3_to_v4.csv      # Degradations (3 cases)
```

## 🚀 Quick Start

### View Results Summary
```bash
python view_comparison_results.py
```

### Generate New Comparison
```bash
python compare_outputs.py
```

## 📈 Key Takeaways (v3→v4)

### 🏆 Wins
- 🇱🇰 **Sri Lanka**: +14.3% improvement
- 🇪🇨 **Ecuador**: +12.5% improvement
- **Geography questions**: +12.5% improvement

### ⚠️ Issues
- 🇸🇦 **Saudi Arabia**: -14.3% degradation (now 28.6%)
- **Culture landmarks**: -25% degradation
- **Language writing**: -20% degradation
- **25 persistent errors** need investigation

### 🎯 Action Items
1. Add more sources for FR, SA, EC countries
2. Fix culture_landmarks degradation
3. Investigate why basic RAG (85.81%) > full system (81.08%)
4. Address 25 persistent errors

## 📖 Full Documentation

See [comparison_results/README.md](comparison_results/README.md) for detailed analysis and recommendations.

---

**Generated**: 2026-01-11  
**Versions**: v3, v4 (v2 not available)
