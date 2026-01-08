# BLEnD CultureRAG Notebook Guide

This guide breaks down the structure of the **BLEnD_CultureRAG.ipynb** notebook, which has been optimized for professional production workflows.

## 📓 Notebook Structure

The notebook is organized into **12 functional stages** (totaling 25 cells with documentation). 

### Stage 1: Environment Setup
- **Cells 1-2**: Installs core dependencies (`unsloth`, `transformers`, `spacy`, `faiss`) and library imports.
- **Purpose**: Establishes the computational environment and GPU hooks.

### Stage 2: Knowledge Foundation
- **Cells 3-4**: spaCy-powered Named Entity Recognition (NER) and Wikipedia cache setup.
- **Algorithm**: Extracts GPE, LOC, and ORG entities + acronym fallback (e.g., "HDB").

### Stage 3: KB Construction
- **Cells 5-6**: Wikipedia scraping and KB chunking.
- **Strategy**: Two-tier scraping (Country Base Pages + Entity Specific Pages).
- **Output**: `kb_chunks.pkl` (cached locally).

### Stage 4: Hybrid Indexing
- **Cells 7-8**: Dual indexing (FAISS Dense + BM25 Sparse).
- **Fusion**: Reciprocal Rank Fusion (RRF) algorithm with country-code pre-filtering.

### Stage 5: Inference Architecture
- **Cells 9-10**: Constrained 1-token decoding function and inference orchestration.
- **Feature**: Crash-proof checkpoints (saves every 10 rows).

### Stage 6: Model Loading & Analysis
- **Cells 11-12**: 4-bit Quantized Llama-3.1-8B loading and result analysis.
- **Quantization**: NF4 (NormalFloat4) saves ~60% VRAM.

---

## 🏃 Execution Workflow

1.  **Stage 1-5 (Initialization)**: Connect to internet, install deps, and build your knowledge base.
2.  **Stage 6 (Model)**: Requires GPU with 8GB+ VRAM (T4).
3.  **Inference (Cell 10)**: Takes ~15-20 minutes for 148 questions.
    - If the kernel crashes, simply rerun this cell; it will resume from the latest checkpoint stored in `output/`.

---

## 📂 Generated Artifacts

| File | Type | Description |
|------|------|-------------|
| `wiki_cache.pkl` | Data | Persistent cache of Wikipedia pages |
| `kb_chunks.pkl` | Data | Vectorized knowledge base |
| `predictions_*.tsv` | Output | Final TSV results (A/B/C/D) |

---

## 🛡️ Safety Railings

- **Row Count Assertion**: Guarantees exactly 148 rows are produced.
- **Duplicate Detection**: Prevents model from generating redundant IDs.
- **Fallback Logic**: Defaults to 'C' on model timeout/exception.
- **Greedy Decoding**: ensures 100% deterministic results.
