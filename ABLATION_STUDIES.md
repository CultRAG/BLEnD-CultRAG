# Ablation studies summary

This file lists the distinct ablation study types found across the notebooks in this workspace, along with what each variant changes or adds.

## Phase-based pipeline ablations (main system)
- baseline_no_rag: Baseline LLM-only inference; retrieval is disabled.
- rag_basic: Basic RAG with BM25 + FAISS + RRF; no filtering.
- phase1_countryfilter: Adds country filter precision fix on top of basic RAG.
- phase2_intent: Adds intent detection (metadata only).
- phase3_tiered: Adds tiered, intent-based routing.
- phase4_quality: Adds anti-leak safeguards and trust-aware prompts.
- phase5_trust_weight: Adds trust-weighted reranking.
- phase6_full_system: Full system with all optimizations enabled.

## RRF-k ablations (retrieval depth)
- baseline: No RAG; uses a minimal baseline prediction flow.
- rag_rrf_k3: RAG with RRF fusion and top_k=3 retrieval depth.
- rag_rrf_k5: RAG with RRF fusion and top_k=5 retrieval depth.

## Prediction comparisons and observations
### Phase-based pipeline comparisons (baseline vs RAG vs full system)
- Length validation: Confirms prediction counts match the question set before comparison.
- Sampleed vs full dataset selection: Uses a sampled set when present, otherwise the full dataset.
- Per-question comparison table: Shows ID, truncated question, correct label, baseline prediction, RAG prediction, full-system prediction, and a status flag.
- Status flags: Tags each example as RAG hurt, RAG fixed, both OK, or both wrong (based on baseline vs RAG correctness).
- Overall accuracy: Reports accuracy for baseline (no RAG), RAG basic, and full system.
- Impact analysis: Counts and percentages for RAG hurt, RAG fixed, both correct, and both wrong; computes net RAG benefit or harm.
- Case inspection: Prints top 10 examples where RAG hurt and top 10 where RAG fixed, with full options and predictions.
- Output artifacts: Saves full comparison and subsets to CSV (all_predictions_comparison.csv, rag_hurt_cases.csv, rag_fixed_cases.csv).

### Component gains visualization (ablation phases)
- Accuracy progress: Prints a text bar chart of accuracy by config from baseline through later phases.
- Delta accuracy per phase: Shows per-phase change relative to prior step.
- Total gain: Reports net accuracy gain from baseline to best config.
- Phase contribution breakdown: Ranks phase gains by contribution to total improvement.

### RRF-k comparison (baseline vs RAG k=3 vs RAG k=5)
- Ablation results summary: Prints the distribution of predicted options per method (baseline, rag_rrf_k3, rag_rrf_k5).

### Prediction change inspection (baseline vs RAG)
- Change count: Counts how many predictions changed when switching from baseline to RAG.
- Example drill-down: Prints the first few changed cases with question text, options, baseline vs RAG prediction, and retrieved context snippets.
