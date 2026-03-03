# Paper Summary

## CultRAG at SemEval-2026 Task 7: Trust-Weighted Cultural RAG with Anti-Leak Filtering for BLEnD Track 2

**Authors:** Aditya Singh, Rickarya Das
**Institution:** Indian Institute of Technology Kharagpur
**Venue:** SemEval-2026 (ACL Workshop Proceedings)

---

## Abstract

We present a trust-weighted Retrieval-Augmented Generation (RAG) system for SemEval-2026 Task 7 (BLEnD) Track 2, targeting English cultural multiple-choice QA across 30 countries. Built atop Llama-3.1-8B-Instruct, the six-phase pipeline integrates hybrid BM25+FAISS retrieval, country-aware filtering, intent detection, tiered routing, anti-leak prompt engineering, and trust-weighted reranking. The core finding is that RAG *hurts* rather than helps: the LLM-only baseline achieves 78.6% accuracy, outperforming the full system at 78.5% (McNemar's test, p = 0.962). Oracle analysis reveals that only 40.7% of questions are answerable from the knowledge base, explaining why retrieval introduces more noise than signal. The sole recovery comes from anti-leak prompt filtering (Phase 4), which mitigates answer-anchoring artifacts.

---

## Links

- **ACL Anthology:** [https://aclanthology.org/2026.semeval-1.xxx](https://aclanthology.org/2026.semeval-1.xxx) *(placeholder — update after publication)*
- **arXiv Preprint:** [https://arxiv.org/abs/2026.xxxxx](https://arxiv.org/abs/2026.xxxxx) *(placeholder — update after upload)*
- **GitHub:** [https://github.com/Aditya26189/BLEnD-CultureRAG](https://github.com/Aditya26189/BLEnD-CultureRAG)

---

## Citation

```bibtex
@inproceedings{singh2026cultrag,
  title     = {{CultRAG} at {SemEval}-2026 Task 7: Trust-Weighted Cultural {RAG} with Anti-Leak Filtering for {BLEnD} Track 2},
  author    = {Singh, Aditya and Das, Rickarya},
  booktitle = {Proceedings of the 20th International Workshop on Semantic Evaluation (SemEval-2026)},
  year      = {2026},
  publisher = {Association for Computational Linguistics},
  address   = {Vienna, Austria},
}
```

---

## What This Paper Is NOT

- **Not a claim that RAG is universally bad.** RAG helped 14 of 30 countries, particularly those underrepresented in English pretraining (Japan +6.1pp, Ethiopia +4.1pp). The negative result is specific to the BLEnD distribution where parametric accuracy already exceeds KB coverage.
- **Not a benchmark paper.** We do not propose a new dataset or evaluation framework. We use the existing BLEnD benchmark and SemEval-2026 Task 7 infrastructure.
- **Not an architecture contribution.** The six-phase pipeline uses standard components (BM25, FAISS, RRF, spaCy NER). The contribution is the empirical analysis of *why* they collectively fail on this task.

---

## What This Paper IS

- **An oracle coverage analysis** showing that only 40.7% of questions are answerable from the KB, establishing a ceiling that parametric accuracy already exceeds by 37.9pp.
- **A country-level decomposition** revealing that RAG selectively benefits low-resource cultures (14 countries gain) while degrading high-resource ones (14 countries lose) — the retrieval viability threshold depends on per-locale coverage vs. parametric accuracy.
- **A quadrant decomposition (backfire analysis)** quantifying that RAG Basic breaks 2,103 questions the baseline answered correctly while fixing only 1,810 (net −293), and that Phase 6 anti-leak filtering recovers 1,479 of those while introducing 1,190 new errors (net +289 over RAG Basic).
- **Rigorous McNemar significance testing** with effect size reporting (Cohen's h) for all pairwise ablation comparisons across 47,014 paired observations, confirming that the 0.1pp gap between baseline and full system is not statistically significant (p = 0.962, h = 0.000).
