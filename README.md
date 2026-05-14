# CultRAG at SemEval-2026 Task 7

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![SemEval 2026](https://img.shields.io/badge/SemEval-2026-green.svg)](https://semeval.github.io/SemEval2026/)
[![Kaggle](https://img.shields.io/badge/Kaggle-Notebook-20BEFF.svg)](https://www.kaggle.com/)
[![arXiv](https://img.shields.io/badge/arXiv-2026.xxxxx-b31b1b.svg)](https://arxiv.org/)

> RAG hurts cultural QA when parametric accuracy exceeds KB coverage — a controlled study at N=47,014.

---

## 📉 Key Finding

Retrieval-Augmented Generation **hurts** performance on the BLEnD cultural QA benchmark. The LLM-only baseline (Llama-3.1-8B-Instruct) achieves **78.6%** accuracy, while the full 6-phase RAG pipeline achieves **78.5%** — statistically indistinguishable (McNemar's $p = 0.962$). Oracle analysis reveals that only **40.7%** of questions are answerable from the knowledge base, a ceiling the LLM's parametric knowledge already exceeds by 37.9 percentage points. Retrieval cannot help when its ceiling lies below parametric performance.

---

## Results at a Glance

| Configuration | Correct | Acc (%) | 95% CI | Δ Base |
|---|---|---|---|---|
| Baseline (LLM only) | 36,932 | 78.6 | [78.2, 78.9] | — |
| RAG Basic (unfiltered) | 36,639 | 77.9 | [77.6, 78.3] | −0.6 |
| + Country Filter (Ph1) | 36,639 | 77.9 | [77.6, 78.3] | −0.6 |
| + Intent Detection (Ph2) | 36,639 | 77.9 | [77.6, 78.3] | −0.6 |
| + Tiered Routing (Ph3) | 36,465 | 77.6 | [77.2, 77.9] | −1.0 |
| + Anti-Leak Quality (Ph4) | 36,928 | 78.5 | [78.2, 78.9] | −0.0 |
| + Trust Reranking (Ph5) | 36,928 | 78.5 | [78.2, 78.9] | −0.0 |
| Full System (Ph6) † | 36,928 | 78.5 | [78.2, 78.9] | −0.0 |

† Official submission. All results on 47,014 English MCQs across 30 country-language pairs.

---

## Why RAG Failed — The Coverage Ceiling

The **retrieval ceiling gap** quantifies why uniform RAG is net-harmful:

```
Δ_ceil = Acc_param − C̄ = 0.786 − 0.407 = +0.379
```

The LLM's parametric accuracy (78.6%) exceeds the KB's oracle coverage (40.7%) by 37.9 percentage points. For 59.3% of questions, the KB cannot provide the answer — retrieval can only inject noise.

**Contrast:**
- **Great Britain:** 92.4% baseline, 21% KB coverage → full system costs 3.0pp (89.7% → 89.4%)
- **Ethiopia:** 59.0% baseline, 65% KB coverage → full system gains 4.1pp (59.0% → 63.0%)

RAG is beneficial only where KB coverage exceeds parametric accuracy. For most countries in BLEnD, the LLM already knows enough.

---

## ✅ The One Thing That Worked

**Anti-leak prompt filtering (Phase 4)** is the only pipeline component that recovers performance. It instructs the model to ignore passage structure, formatting cues, and answer-letter mentions in KB text. This suppresses answer-anchoring artifacts introduced by raw retrieval, recovering +1.0pp over Phase 3 (from 77.6% to 78.5%). The improvement is in prompt engineering, not retrieval quality.

---

## 🗺️ Country-Level Split

**Top 5 countries helped by RAG:**

| Country | Δ (pp) |
|---|---|
| Japan | +6.1 |
| Saudi Arabia | +4.5 |
| Ethiopia | +4.1 |
| North Korea | +4.0 |
| Morocco | +2.9 |

**Top 5 countries hurt by RAG:**

| Country | Δ (pp) |
|---|---|
| American Samoa | −6.2 |
| Basque Country | −4.9 |
| Egypt | −4.1 |
| Great Britain | −3.0 |
| United States | −2.7 |

Countries helped are predominantly underrepresented in English pretraining data. Countries hurt are high-resource (GB, US) or have sparse, misleading KB entries (Basque Country, American Samoa).

---

## Quick Start

```bash
git clone https://github.com/Aditya26189/BLEnD-CultureRAG
cd BLEnD-CultureRAG
pip install -r requirements.txt
```

**1. Load the KB:**
The knowledge base (1,262 chunks across 7 shards) is loaded from cached pickle files or rebuilt via API scraping. See [docs/kb_construction.md](docs/kb_construction.md).

**2. Run the pipeline:**
Open the inference notebook on Kaggle with 2× T4 GPUs. Each ablation configuration is controlled by phase flags in the main inference loop. See [docs/reproduction.md](docs/reproduction.md).

**3. Evaluate:**
Run `scoring.py` to compute macro-averaged accuracy across all 8 configurations with McNemar significance tests and Wilson confidence intervals.

---

## Repo Structure

```
BLEnD-CultureRAG/
├── README.md                  # This file
├── PAPER.md                   # Paper summary, abstract, and citation
├── RESULTS.md                 # Full numerical results log
├── CONTRIBUTING.md            # How to contribute / extend
├── LICENSE                    # MIT License
├── Inference-notebook.ipynb   # Main Kaggle inference notebook (6-phase pipeline)
├── ablation-studies.ipynb     # Ablation analysis and visualization notebook
├── paper/
│   └── semeval2026_task7_paper.tex  # LaTeX source (ACL style)
├── docs/
│   ├── architecture.md        # Pipeline architecture deep-dive
│   ├── kb_construction.md     # Knowledge base build process
│   ├── oracle_analysis.md     # Oracle coverage methodology
│   └── reproduction.md        # Full reproduction guide
├── configs/
│   └── pipeline_config.md     # All hyperparameters documented
└── prediction-results/        # Ablation prediction CSVs
```

---

## License

Apache — see [LICENSE](LICENSE).
