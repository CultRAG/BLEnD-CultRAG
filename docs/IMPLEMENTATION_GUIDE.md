# Implementation Guide

This guide provides step-by-step instructions for deploying and running the BLEnD CultureRAG pipeline.

---

## 📋 Prerequisites

### Hardware Requirements
- **Recommended**: NVIDIA T4 (16GB) or P100 (16GB) GPU.
- **Minimum**: 8GB VRAM (required for Llama-3.1-8B 4-bit).

### Software Stack
- **Python**: 3.10+
- **CUDA**: 11.8+
- **Access**: HuggingFace token for `meta-llama/Llama-3.1-8B-Instruct`.

---

## 🛠️ Step-by-Step Execution

### 1. Environment Setup
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Data Preparation
Ensure the following files are in the `data/` directory:
- `questions.tsv`: Target questions (148 rows).
- `answers.tsv`: Ground truth (for evaluation).
- `country_sources.json`: Seed pages for KB construction.

### 3. Knowledge Base Construction
Run **Stages 3-5** of the notebook. 
- **Time**: ~3-5 minutes on first run.
- **Output**: Generates `kb_chunks.pkl` (processed knowledge).

### 4. Indexing & Retrieval
Run **Stages 6-8** to build FAISS/BM25 indices.
- **Fusion**: RRF combines semantic and lexical results.

### 5. Model Inference
Run **Stages 9-11** to load the Llama model and execute prediction.
- **Note**: The inference loop includes **safety checkpoints** saved to `output/`.
- If the session times out, rerun the inference cell to resume progress.

### 6. Results & Evaluation
Run the evaluation script to calculate metrics:
```bash
python scripts/evaluate_results.py
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **CUDA OOM** | Ensure you are using the 4-bit quantization cell. Restart kernel. |
| **Access Denied (HF)** | Verify your Hugging Face token has access to Llama 3.1. |
| **Low Accuracy** | Ensure `country_sources.json` is populated for all target locales. |
| **Missing spaCy** | Run `python -m spacy download en_core_web_sm`. |

---

## 🚀 Deployment Tips

- **Kaggle**: Enable "Internet" and "GPU T4 x2" in Settings.
- **Colab**: Use "Runtime Type -> GPU T4". Mount Drive for persistent storage.
- **Local**: Use a virtual environment to manage `bitsandbytes` and `faiss-cpu`.
