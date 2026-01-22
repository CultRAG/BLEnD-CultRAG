# 🚀 BLEnD-CultureRAG

<div align="center">

**Retrieval-Augmented Reasoning for Multi-Cultural Multiple-Choice QA**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Llama 3.1](https://img.shields.io/badge/Model-Llama--3.1--8B-orange.svg)](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Production Ready](https://img.shields.io/badge/Status-Production--Ready-green.svg)](#)

</div>

---

## 📖 Overview

**BLEnD-CultureRAG** is a professional retrieval-augmented cultural reasoning system. It evaluates the cultural awareness of language models by selecting culturally appropriate answers to English multiple-choice questions across **30+ global locales**.

The system features:
- **spaCy-powered** Named Entity Recognition (NER) for knowledge targeting.
- **Hybrid Retrieval** (FAISS + BM25) with Reciprocal Rank Fusion (RRF).
- **Constrained 1-Token Decoding** for deterministic and efficient inference.
- **4-bit Quantization** for high-performance GPU execution on standard hardware (T4/P100).

---

## 📂 Project Structure

```
BLEnD-CultureRAG/
├── data/               # 📊 Main datasets and Ground Truth
│   ├── questions.tsv   # 148 questions across 30+ countries
│   ├── answers.tsv     # Ground truth for evaluation
│   └── sample/         # 🧪 Development/Testing subsets
├── docs/               # 📑 Comprehensive documentation guides
│   ├── ARCHITECTURE.md # High-level system design
│   ├── NOTEBOOK_GUIDE.md# Jupyter notebook usage breakdown
│   └── ...             # Component and implementation deep dives
├── notebooks/          # 📓 Industrial-grade Jupyter notebooks
│   └── BLEnD_CultureRAG.ipynb # Fully documented 12-stage pipeline
├── output/             # 📤 Generated predictions and metrics
├── scripts/            # 🛠️ Production utility scripts
│   ├── evaluate_results.py # Accuracy & impact analysis
│   ├── verify_coverage.py # Check country/intent source coverage
│   └── ...             # Site checks and format converters
├── sources/            # 🧭 Intent mapping and locale configurations
│   ├── sites_intent_mapping_V7.json # Main RAG routing logic
│   └── country_sources.json # Locale-specific Wikipedia mappings
└── requirements.txt    # 📦 Project dependencies
```

---

## 🚀 Quick Start

### 1. Installation
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run Inference
Upload `notebooks/BLEnD_CultureRAG.ipynb` to **Kaggle** or **Google Colab**.
- **Stage 1-5**: Builds the Knowledge Base via Wikipedia scraping (auto-cached).
- **Stage 6-9**: Configures hybrid retrieval and 1-token decoder.
- **Stage 10**: Executes crash-proof inference with checkpoints.

### 3. Evaluation
Compare your predictions against ground truth and generate impact reports:
```bash
python scripts/evaluate_results.py
```

---

## 📈 Performance Summary

| Method | Accuracy | Context | Decoder |
|--------|----------|---------|---------|
| **Baseline** | 27.70% | None | Greedy |
| **RAG (k=3)** | **33.11%** | Fixed | 1-Token |
| **RAG (k=5)** | **33.11%** | Fused | 1-Token |

> **Impact**: RAG integration provides a **+5.41% net gain** over the baseline model on the BLEnD dataset.

---

## 📑 Detailed Documentation

- [**Architecture Deep Dive**](docs/ARCHITECTURE.md) - System design and data flow.
- [**Notebook Guide**](docs/NOTEBOOK_GUIDE.md) - Detailed cell-by-cell explanation.
- [**Implementation Guide**](docs/IMPLEMENTATION_GUIDE.md) - Step-by-step setup instructions.

---

## 📜 License
This project is licensed under the **MIT License**.
