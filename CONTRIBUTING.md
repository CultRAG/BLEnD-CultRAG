# Contributing to BLEnD-CultureRAG

## Repo Purpose

This repository documents a **negative-result RAG system** for SemEval-2026 Task 7 (BLEnD) Track 2. The system achieved 78.5% accuracy — functionally identical to the 78.6% parametric baseline — because the knowledge base covers only 40.7% of questions, well below the model's existing accuracy.

The primary contribution is the **oracle coverage diagnostic** and the empirical demonstration that RAG hurts when KB coverage is below parametric accuracy.

This is research code, not a production system. Contributions that extend the analysis or improve the methodology are welcome.

---

## Extension Ideas

The following are the most impactful directions for future work, roughly ordered by expected value:

### 1. Knowledge Base Expansion

The single most impactful improvement. Current oracle coverage is 40.7%; it must exceed 78.6% for RAG to be viable.

- Scrape country-specific cultural databases (UNESCO, government tourism sites)
- Add non-English Wikipedia articles (translated) for underrepresented countries
- Target the 59.3% of questions with zero KB coverage

### 2. Selective RAG (Retrieval Gating)

Train a classifier to predict whether retrieval will help for a given question. Skip retrieval when the model is confident in its parametric answer.

- Use oracle coverage labels as training signal
- Potential to eliminate RAG backfire entirely

### 3. Intent Classifier Upgrade

The current keyword-based classifier assigns labels to 95.6% of questions but has zero downstream effect. A learned classifier (fine-tuned on cultural QA data) with intent-conditioned retrieval strategies could unlock this component.

### 4. Cross-Encoder Reranking

Replace trust-weighted RRF with a cross-encoder (e.g., `ms-marco-MiniLM-L-6-v2`) that scores (question, passage) pairs directly. This could improve retrieval precision within the existing KB.

### 5. Answer Debiasing

The baseline over-predicts option A (32% vs. 24% gold). Answer shuffling during inference or post-hoc calibration could correct positional bias without any KB changes.

### 6. Multi-Hop Retrieval

Some cultural questions require combining evidence from multiple sources. Implement iterative retrieval with query reformulation.

---

## Accepted Contributions

| Type | Welcome? | Notes |
|---|---|---|
| KB expansion (new sources) | ✅ | Include oracle coverage before/after |
| New ablation configurations | ✅ | Must include accuracy + McNemar test |
| Bug fixes | ✅ | — |
| Documentation improvements | ✅ | — |
| Visualization additions | ✅ | Plotly preferred for consistency |
| Alternative retrieval methods | ✅ | Compare against existing BM25+FAISS baseline |
| Hyperparameter tuning results | ✅ | Report search space and best config |
| Code refactoring | ⚠️ | Discuss in an issue first |
| Framework migration | ❌ | Out of scope for this research repo |

---

## How to Contribute

1. **Fork** the repository.
2. **Create a branch** from `adi` (the development branch):
   ```bash
   git checkout adi
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** following the conventions below.
4. **Test** by running `python scoring.py` and verifying all 8 configs produce expected accuracies.
5. **Open a pull request** to `adi` with:
   - A clear description of what changed and why
   - Before/after accuracy numbers (if applicable)
   - McNemar test results (if comparing configurations)

---

## Code Conventions

- **Python 3.10+** — use type hints where practical
- **Notebooks** — clear cell outputs before committing; keep cells small and documented
- **Data files** — never commit large data files (>10 MB). Use `.gitignore` or Git LFS.
- **Cache files** — JSON format. Include a comment with the generation date.
- **Results** — report exact counts (e.g., "36,928 / 47,014") alongside percentages

---

## Testing

Run the scoring script to verify predictions:

```bash
python scoring.py
```

Expected output for each config:

```
baseline_no_rag:       36932 / 47014 = 78.55%
rag_basic:             36639 / 47014 = 77.93%
phase1_countryfilter:  36639 / 47014 = 77.93%
phase2_intent:         36639 / 47014 = 77.93%
phase3_tiered:         36465 / 47014 = 77.55%
phase4_quality:        36928 / 47014 = 78.55%
phase5_trust_weight:   36928 / 47014 = 78.55%
phase6_full_system:    36928 / 47014 = 78.55%
```

---

## Citation

If you use this work, please cite:

```bibtex
@inproceedings{dash2026blendculturerag,
  title     = {BLEnD-CultureRAG: When Retrieval Hurts — A Six-Phase RAG Pipeline for Cultural QA},
  author    = {Dash, Riddhiman and Dash, Aditya},
  booktitle = {Proceedings of the 20th International Workshop on Semantic Evaluation (SemEval-2026)},
  year      = {2026},
  note      = {Task 7, Track 2}
}
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
