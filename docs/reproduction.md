# Reproduction Guide

Step-by-step instructions to reproduce BLEnD-CultureRAG results from scratch.

---

## Hardware Requirements

| Component | Specification |
|---|---|
| GPU | 2× NVIDIA T4 (16 GB VRAM each) |
| Platform | Kaggle Notebooks (free tier) |
| RAM | 13 GB system RAM (Kaggle default) |
| Disk | ~20 GB free (model weights + KB + caches) |
| Tensor Parallelism | tp = 2 (across both T4s) |

The system was developed and evaluated entirely on Kaggle's free GPU tier. No paid compute was used.

---

## Software Requirements

| Package | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Runtime |
| `lmdeploy` | ≥ 0.5 | LLM inference (TurboMind backend) |
| `transformers` | ≥ 4.40 | Tokenizer, model loading |
| `sentence-transformers` | ≥ 2.2 | `all-MiniLM-L6-v2` embeddings |
| `faiss-cpu` | ≥ 1.7 | Dense retrieval index |
| `rank_bm25` | ≥ 0.2 | Sparse retrieval |
| `spacy` | ≥ 3.5 | NER for entity extraction |
| `en_core_web_sm` | — | spaCy English model |
| `plotly` | ≥ 5.0 | Visualization (ablation notebook) |
| `kaleido` | ≥ 0.2 | Static image export for figures |
| `pandas` | ≥ 1.5 | Data manipulation |
| `numpy` | ≥ 1.24 | Numerical operations |

Install all dependencies:

```bash
pip install lmdeploy transformers sentence-transformers faiss-cpu rank_bm25 spacy plotly kaleido pandas numpy
python -m spacy download en_core_web_sm
```

---

## Data Setup

1. **BLEnD Track 2 MCQ data**: `track_2_mcq_input.tsv` (47,015 lines: 1 header + 47,014 questions)
   - Columns: `question_id`, `country`, `question`, `option_a`, `option_b`, `option_c`, `option_d`, `answer`
   
2. **Gold answers**: `blend-data/answers.tsv`

3. **Knowledge base caches** (pre-built; see `cache-json-files/`):
   - `kb_chunks_filtered (1).json` — 1,262 filtered chunks
   - `wiki_cache (2).json` — Wikipedia article cache
   - `web_cache.json` — Web search result cache
   - `entity_to_title.json` — Entity-to-Wikipedia mappings

---

## 7-Step Reproduction

### Step 1: Clone the Repository

```bash
git clone https://github.com/ridash2005/BLEnD-CultureRAG.git
cd BLEnD-CultureRAG
git checkout adi
```

### Step 2: Set Up Environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt  # or install packages listed above
```

### Step 3: Download Model Weights

On Kaggle, the model is loaded automatically. For local reproduction:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Model weights require Llama access approval from Meta
```

### Step 4: Build Indices

If not using pre-built caches:

```python
# Build BM25 index
from rank_bm25 import BM25Okapi
corpus = [chunk["text"].split() for chunk in kb_chunks]
bm25 = BM25Okapi(corpus, k1=1.5, b=0.75)

# Build FAISS index
from sentence_transformers import SentenceTransformer
import faiss
encoder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = encoder.encode([c["text"] for c in kb_chunks])
index = faiss.IndexFlatIP(384)
faiss.normalize_L2(embeddings)
index.add(embeddings)
```

### Step 5: Run Inference (Baseline)

Open `Inference-notebook.ipynb` on Kaggle with 2× T4 GPU accelerator. Run all cells with RAG disabled to produce the baseline predictions.

Expected output: `baseline_no_rag.csv` — 36,932 / 47,014 correct (78.6%).

### Step 6: Run Inference (All Ablation Configs)

Run the notebook with each phase incrementally enabled:

| Config | Phases Active | Expected Accuracy |
|---|---|---|
| `baseline_no_rag` | None | 78.6% |
| `rag_basic` | Retrieval only | 77.9% |
| `phase1_countryfilter` | 1 | 77.9% |
| `phase2_intent` | 1–2 | 77.9% |
| `phase3_tiered` | 1–3 | 77.6% |
| `phase4_quality` | 1–4 | 78.5% |
| `phase5_trust_weight` | 1–5 | 78.5% |
| `phase6_full_system` | 1–6 | 78.5% |

### Step 7: Score Predictions

```bash
python scoring.py
```

This scores all 8 prediction files in `prediction-results/` and reports per-config accuracy with 95% Wilson confidence intervals.

---

## Three-Tier Cache System

The system uses a layered cache to avoid redundant API calls and web fetches:

| Tier | File | Contents | Purpose |
|---|---|---|---|
| **L1: KB Cache** | `kb_chunks_filtered (1).json` | 1,262 pre-processed chunks | Avoid re-chunking on every run |
| **L2: Wikipedia Cache** | `wiki_cache (2).json` | Raw Wikipedia article text | Avoid repeated Wikipedia API calls |
| **L3: Web Cache** | `web_cache.json` | Cached web search results | Avoid repeated web scraping |

All caches are JSON files. Delete any cache file to force re-fetching from the original source.

---

## Expected Outputs

After a full run, the following files should exist in `prediction-results/` (or `ablation_predictions/`):

```
baseline_no_rag.csv          # 36,932 correct
rag_basic.csv                # 36,639 correct
phase1_countryfilter.csv     # 36,639 correct
phase2_intent.csv            # 36,639 correct
phase3_tiered.csv            # 36,465 correct
phase4_quality.csv           # 36,928 correct
phase5_trust_weight.csv      # 36,928 correct
phase6_full_system.csv       # 36,928 correct
```

The official submission is `phase6_full_system.csv` (also saved as `submission_phase6_full_system.tsv`).

---

## Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| CUDA OOM on single GPU | Model requires ~15 GB VRAM | Use tp=2 with 2× T4 or switch to a single A100/L4 |
| `lmdeploy` import error | Version mismatch | `pip install lmdeploy>=0.5` |
| spaCy model not found | `en_core_web_sm` not downloaded | `python -m spacy download en_core_web_sm` |
| BM25 index empty | Missing KB chunks file | Ensure `kb_chunks_filtered (1).json` exists in `cache-json-files/` |
| FAISS dimension mismatch | Wrong embedding model | Must use `all-MiniLM-L6-v2` (384-dim), not other MiniLM variants |
| Accuracy differs by ±0.1% | Non-deterministic LLM sampling | Set temperature=0 and top_k=1 for deterministic output |
| Kaggle session timeout | Run exceeds 12-hour limit | Split into baseline + RAG runs across two sessions |

---

## Runtime Estimates

| Stage | Approximate Time |
|---|---|
| Index construction (BM25 + FAISS) | ~2 minutes |
| Baseline inference (47,014 questions) | ~45 minutes |
| Full pipeline inference (per config) | ~60 minutes |
| All 8 ablation configs | ~6–8 hours total |
| Scoring all configs | < 1 minute |
