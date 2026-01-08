# Implementation Guide

This document provides step-by-step implementation guidance for setting up and running the BLEnD CultureRAG notebook.

## Prerequisites

### Hardware Requirements

**Minimum:**
- GPU: NVIDIA T4 (16GB VRAM) or equivalent
- RAM: 16GB system memory
- Storage: 10GB free space

**Recommended:**
- GPU: NVIDIA A100 (40GB VRAM) for faster inference
- RAM: 32GB system memory
- Storage: 20GB free space

**Compatibility:**
- Kaggle Notebooks (Free tier provides T4 GPU)
- Google Colab (Pro tier recommended)
- Local machine with CUDA-capable GPU

### Software Requirements

**Python Version:** 3.10 or higher

**Core Dependencies:**
```
torch>=2.0.0
transformers>=4.35.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4  (or faiss-gpu for GPU acceleration)
spacy>=3.5.0
rank-bm25>=0.2.2
nltk>=3.8
pandas>=1.5.0
numpy>=1.24.0
requests>=2.28.0
beautifulsoup4>=4.11.0
tqdm>=4.65.0
```

**spaCy Model:**
```bash
python -m spacy download en_core_web_sm
```

### Required Files

1. **Input dataset:** `track_2_mcq_input.tsv`
   - Format: TSV with columns `id`, `question`, `option_A`, `option_B`, `option_C`, `option_D`
   - Size: 148 rows (all languages)

2. **Country configuration:** `country_sources.json`
   - Format: JSON mapping country codes to Wikipedia page titles
   - Example:
     ```json
     {
       "GB": ["Culture_of_the_United_Kingdom", "British_culture"],
       "US": ["Culture_of_the_United_States", "American_culture"],
       "SG": ["Culture_of_Singapore"]
     }
     ```

3. **HuggingFace token:** Required for Llama model access
   - Sign up at https://huggingface.co
   - Get access to meta-llama/Llama-3.1-8B-Instruct
   - Generate API token from Settings > Access Tokens

---

## Setup Instructions

### Step 1: Environment Setup

#### On Kaggle Notebooks

1. Create new notebook
2. Enable GPU accelerator:
   - Settings > Accelerator > GPU T4 x2
3. Add dataset:
   - Add Data > Upload > `track_2_mcq_input.tsv`
4. Add secrets:
   - Add-ons > Secrets > New Secret
   - Name: `HUGGINGFACE_TOKEN`
   - Value: Your HF token

#### On Google Colab

1. Create new notebook
2. Enable GPU:
   - Runtime > Change runtime type > GPU > T4
3. Mount Drive (for data persistence):
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
4. Upload dataset and config:
   ```python
   from google.colab import files
   uploaded = files.upload()  # Select track_2_mcq_input.tsv, country_sources.json
   ```

#### On Local Machine

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variable:
   ```bash
   export HUGGINGFACE_TOKEN='your_token_here'
   # On Windows: set HUGGINGFACE_TOKEN=your_token_here
   ```

---

### Step 2: Install Dependencies (Cell 2)

Run the installation cell:
```python
!pip install -q unsloth
!pip install -qU transformers sentence-transformers faiss-cpu
!pip install -q wikipedia-api beautifulsoup4 requests
print("✅ Installation complete")
```

**Expected output:**
```
✅ Installation complete
```

**Common issues:**
- **CUDA mismatch:** Ensure PyTorch CUDA version matches GPU driver
  ```bash
  python -c "import torch; print(torch.cuda.is_available())"  # Should print True
  ```
- **Memory error during install:** Restart kernel and try again

---

### Step 3: Import Libraries (Cell 3)

Run the imports cell:
```python
import pandas as pd
import torch
import re
import os
# ... (rest of imports)
```

**Expected output:**
```
✅ Libraries imported
```

**Verification:**
```python
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

---

### Step 4: Entity Extraction (Cell 4)

This cell installs spaCy and extracts entities from all questions.

**Expected runtime:** 1-2 minutes

**Expected output:**
```
Total questions: 148
Example entities: {'id': 'en-GB030', 'country': 'GB', 'entities': ['Lake District', 'Cumberland']}
Countries covered: 32
Countries: ['AR', 'AU', 'BG', 'BR', 'CA', 'CN', 'EC', ...]
✅ Upgraded to spaCy NER-based entity extraction
```

**Checkpoints:**
- `entity_data` variable created (list of 148 dicts)
- ~30-35 unique countries detected
- Average 3-8 entities per question

**Common issues:**
- **spaCy model not found:** Re-run `python -m spacy download en_core_web_sm`
- **Country code extraction fails:** Check ID format matches `{lang}-{country}{number}`

---

### Step 5: Wikipedia Cache Setup (Cell 5)

This cell sets up disk-backed caching for Wikipedia pages.

**Expected output:**
```
📦 Loaded 0 cached pages from disk
```
(Or `Loaded N cached pages` if resuming)

**Files created:**
- `wiki_cache.pkl` (or `/kaggle/working/wiki_cache.pkl` on Kaggle)

---

### Step 6: Knowledge Base Construction (Cell 6)

This cell scrapes Wikipedia and builds the KB. **Most time-consuming step.**

**Expected runtime:** 10-30 minutes (depends on internet speed and cache state)

**Expected output:**
```
Scraping country-specific pages...
100%|██████████| 148/148 [05:23<00:00, 2.18s/it]
Scraped 324 chunks from base pages

Scraping entity-specific pages...
100%|██████████| 148/148 [12:45<00:00, 5.17s/it]
Total KB chunks: 687
✅ Disk cache now has 143 pages

✅ KB built with 687 chunks
   - Base pages: 324
   - Entity pages: 363
   - Wikipedia cache: 143 pages cached to disk
```

**Files created:**
- `kb_chunks.pkl` (pickled KB data)
- `wiki_cache.pkl` (updated with new pages)

**Checkpoints:**
- KB size: 400-800 chunks (typical range)
- Cache size: 100-200 pages
- No HTTP errors or timeouts

**Common issues:**
- **Network timeout:** Retry cell; cached pages will be skipped
- **Rate limiting:** Script includes 0.5s delays; don't modify
- **Low KB size (<300):** Check `country_sources.json` has entries for detected countries

**Optimization tips:**
- On re-run: Cache makes this ~90% faster (only new pages scraped)
- To rebuild from scratch: Delete `wiki_cache.pkl` and `kb_chunks.pkl`

---

### Step 7: Install Retrieval Dependencies (Cell 7)

Install BM25 and NLTK data.

**Expected output:**
```
[nltk_data] Downloading package punkt to /root/nltk_data...
[nltk_data]   Package punkt is already up-to-date!
✅ Dependencies installed
```

---

### Step 8: Build Indices (Cell 8)

Build FAISS and BM25 indices over the KB.

**Expected runtime:** 2-5 minutes

**Expected output:**
```
Building FAISS index...
Batches: 100%|██████████| 22/22 [00:45<00:00, 2.07s/batch]
✅ FAISS index built: 687 vectors

Building BM25 index...
✅ BM25 index built
```

**Checkpoints:**
- FAISS index size matches KB chunk count
- No OOM errors during encoding

**Common issues:**
- **CUDA OOM:** Reduce batch size in `embedder.encode(..., batch_size=16)`
- **Encoding slow on CPU:** Expected; consider GPU-enabled sentence-transformers

---

### Step 9: Setup Hybrid Retriever (Cell 9)

Initialize RRF retriever and run smoke test.

**Expected output:**
```
✅ RRF hybrid retriever ready
Question: Which of these family holiday destinations is located in Cumberland?...
Country filter: GB
1. [RRF=0.0412] [Lake_District] The Lake District, also known as the Lakes or Lakeland...
2. [RRF=0.0387] [Cumbria] Cumbria is a ceremonial county in North West England...
3. [RRF=0.0298] [Culture_of_the_United_Kingdom] The culture of the United Kingdom...
```

**Checkpoints:**
- 3 results returned
- All results have RRF scores
- Country filter applied correctly

---

### Step 10: Load Language Model (Missing Cell - Add Before Cell 10)

**Important:** The current notebook is missing the model loading cell. Add this cell before the prediction cell:

```python
# ============================================================================
# Load Llama-3.1-8B-Instruct
# ============================================================================
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Login to HuggingFace
login(token="YOUR_HF_TOKEN_HERE")  # Replace with your token
print("✅ Logged in to Hugging Face")

# Load model
print("🤖 Loading Llama-3.1-8B-Instruct...")
model_name = "meta-llama/Llama-3.1-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  # FP16 for T4 compatibility
    device_map="auto"
)

print("✅ Model loaded!")
print(f"   GPU Memory: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
```

**Expected runtime:** 3-5 minutes (model download)

**Expected output:**
```
✅ Logged in to Hugging Face
🤖 Loading Llama-3.1-8B-Instruct...
Downloading model.safetensors: 100%|██████████| 8.52G/8.52G [02:15<00:00, 63.1MB/s]
✅ Model loaded!
   GPU Memory: 8.24 GB
```

**Common issues:**
- **Auth error:** Check HF token is valid and has Llama access
- **OOM:** T4 has 16GB; 8B FP16 should fit. If not, try INT8 quantization
- **Model not found:** Ensure you've requested access to Llama 3.1 on HuggingFace

---

### Step 11: Setup Prediction Function (Cell 10)

Define the constrained 1-token prediction function.

**Expected output:**
```
✅ predict_row updated: 1-token constrained decoding (A/B/C/D only)
```

**No errors should occur** - this just defines a function.

---

### Step 12: Run Inference (Cell 11)

Run the full inference pipeline with checkpointing and safety checks.

**Expected runtime:** 15-30 minutes (depends on GPU)

**Expected output:**
```
Running crash-proof inference with checkpointing...

baseline:   0%|          | 0/148 [00:00<?, ?it/s]
baseline: 100%|██████████| 148/148 [01:23<00:00, 1.78it/s]
✅ Success: Covered 32 unique language-locales.
🛡️ Safety Checks Passed.
✅ Saved 148 predictions to /kaggle/working/predictions_baseline.tsv

rag_rrf_k3: 100%|██████████| 148/148 [18:42<00:00, 7.58s/it]
✅ Success: Covered 32 unique language-locales.
🛡️ Safety Checks Passed.
✅ Saved 148 predictions to /kaggle/working/predictions_rag_rrf_k3.tsv

rag_rrf_k5: 100%|██████████| 148/148 [21:15<00:00, 8.62s/it]
✅ Success: Covered 32 unique language-locales.
🛡️ Safety Checks Passed.
✅ Saved 148 predictions to /kaggle/working/predictions_rag_rrf_k5.tsv

============================================================
ABLATION RESULTS
============================================================
baseline       : {'C': 148}
rag_rrf_k3     : {'A': 52, 'B': 38, 'C': 34, 'D': 24}
rag_rrf_k5     : {'A': 49, 'B': 41, 'C': 35, 'D': 23}
```

**Files created:**
- `/kaggle/working/predictions_baseline.tsv`
- `/kaggle/working/predictions_rag_rrf_k3.tsv`
- `/kaggle/working/predictions_rag_rrf_k5.tsv`
- Checkpoint files (automatically cleaned up)

**Checkpoints:**
- All 3 methods complete successfully
- 148 predictions per method
- Diverse answer distributions (not all 'C')
- Safety checks pass

**Common issues:**
- **Crash mid-inference:** Restart kernel, re-run inference cell - it will resume from checkpoint
- **OOM during generation:** Reduce `k_ctx` from 3 to 2 in retrieval
- **Slow inference:** Expected on free tier; consider upgrading to faster GPU

---

### Step 13: Optional Analysis (Cells 12-15)

These cells provide diagnostic insights.

**Cell 12:** Compare baseline vs RAG predictions
**Cell 13:** GPU memory usage
**Cell 14:** Latency benchmarks

**Safe to skip** if only interested in final predictions.

---

## Output Files

### Prediction Files Format

**Structure:** TSV (tab-separated values)
```
en-GB030	B
en-GB031	A
en-GB032	C
...
```

**Columns:**
1. Question ID (e.g., `en-GB030`)
2. Prediction (A, B, C, or D)

**No header row** (required for submission)

### Which File to Submit?

**Recommended:** `predictions_rag_rrf_k3.tsv`

**Reasoning:**
- Best balance of accuracy and context
- k=3 provides sufficient context without noise
- k=5 often includes less relevant chunks

**Validation:**
```python
# Check file
df_pred = pd.read_csv('/kaggle/working/predictions_rag_rrf_k3.tsv', 
                      sep='\t', header=None, names=['id', 'prediction'])
print(f"Rows: {len(df_pred)}")  # Should be 148
print(f"Predictions: {df_pred['prediction'].value_counts().to_dict()}")
print(f"Invalid: {df_pred[~df_pred['prediction'].isin(['A','B','C','D'])].shape[0]}")  # Should be 0
```

---

## Troubleshooting

### Common Errors and Solutions

#### 1. "CUDA out of memory"

**Solutions:**
- Restart kernel to clear GPU memory
- Reduce batch size in encoding
- Use INT8 quantization for model
- Upgrade to larger GPU tier

#### 2. "Model not found" or "403 Forbidden"

**Solutions:**
- Check HF token is set correctly
- Verify you've accepted Llama license on HuggingFace
- Try: `huggingface-cli login` in terminal

#### 3. "Wikipedia scraping times out"

**Solutions:**
- Check internet connection
- Increase timeout in `scrape_page` (from 10s to 30s)
- Resume scraping - cached pages will be skipped

#### 4. "Safety checks failed: Expected 148 rows"

**Cause:** Dataset was filtered incorrectly

**Solutions:**
- Check dataset loading (no `df = df[df['id'].str.startswith('en-')]`)
- Verify `track_2_mcq_input.tsv` has 148 rows
- Delete checkpoints and re-run inference

#### 5. "Duplicate IDs found"

**Cause:** Loop logic error (rare)

**Solutions:**
- Check you didn't modify inference loop
- Delete checkpoints: `!rm /kaggle/working/predictions_*_checkpoint.tsv`
- Re-run inference cell

---

## Performance Tuning

### Speed Optimizations

**1. Batch Inference (Advanced)**
Modify prediction function to process multiple questions at once:
```python
# Requires padding logic and batch attention masks
# Potential 3-5x speedup
```

**2. Cached Retrieval**
Pre-compute retrievals if running multiple experiments:
```python
# Cache retrieval results to disk
import pickle
retrieval_cache = {}
for _, row in df.iterrows():
    query = build_expanded_query(row)
    retrieval_cache[row['id']] = retriever.search(query, k=5)
pickle.dump(retrieval_cache, open('retrieval_cache.pkl', 'wb'))
```

**3. GPU Acceleration for FAISS**
Use `faiss-gpu` for faster search on large KB:
```python
!pip install faiss-gpu
# Then build index with: faiss.index_cpu_to_gpu(...)
```

### Accuracy Optimizations

**1. Increase KB Coverage**
```python
# In cell 6, increase entity limit
max_entities = 400  # Up from 200
```

**2. Better Embeddings**
```python
# Use larger model (requires more VRAM)
embedder = SentenceTransformer('all-mpnet-base-v2')  # 768 dims
```

**3. Re-ranking (Advanced)**
Add cross-encoder re-ranker after RRF:
```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
# Re-rank top 10 candidates to get best 3
```

---

## Reproducibility Checklist

Before submitting predictions, verify:

- [ ] Used full dataset (148 rows, no language filtering)
- [ ] Cell 13 (English-only filter) was NOT run
- [ ] Model loaded successfully (8B parameters, FP16)
- [ ] All safety checks passed
- [ ] Prediction file has exactly 148 rows
- [ ] All predictions are A/B/C/D (no invalid values)
- [ ] No duplicate IDs in output
- [ ] Covered 30+ language-locales
- [ ] Answer distribution is diverse (not all 'C')

**Final validation:**
```python
import pandas as pd

# Load predictions
df_pred = pd.read_csv('/kaggle/working/predictions_rag_rrf_k3.tsv', 
                      sep='\t', header=None, names=['id', 'prediction'])

# Load original dataset
df_orig = pd.read_csv('track_2_mcq_input.tsv', sep='\t')

# Checks
assert len(df_pred) == 148, f"Expected 148 rows, got {len(df_pred)}"
assert len(df_pred['id'].unique()) == 148, "Duplicate IDs found"
assert df_pred['prediction'].isin(['A','B','C','D']).all(), "Invalid predictions found"
assert set(df_pred['id']) == set(df_orig['id']), "ID mismatch with original dataset"

print("✅ All validation checks passed!")
```

---

## Next Steps

After successful inference:

1. **Download predictions:**
   - Kaggle: Output tab → Download `predictions_rag_rrf_k3.tsv`
   - Colab: `files.download('/kaggle/working/predictions_rag_rrf_k3.tsv')`

2. **Submit to competition:**
   - Upload to competition submission page
   - Wait for leaderboard update

3. **Iterate if needed:**
   - Check leaderboard feedback
   - Try `predictions_rag_rrf_k5.tsv` if k3 underperforms
   - Consider ensemble: majority vote across k3, k5, and baseline

4. **Document approach:**
   - Note hyperparameters used
   - Save notebook version for reproducibility
   - Record any manual modifications

---

## Advanced Customization

### Custom Country Sources

Edit `country_sources.json` to add more pages:
```json
{
  "GB": [
    "Culture_of_the_United_Kingdom",
    "British_culture",
    "British_cuisine",  // Add more pages
    "British_literature"
  ]
}
```

### Custom Entity Extraction

Modify NER pipeline to include custom entities:
```python
# Add to entity extraction
CUSTOM_ENTITIES = {'HDB', 'MRT', 'CBD'}  # Singapore-specific
ents.update(CUSTOM_ENTITIES & set(text.upper().split()))
```

### Custom Prompts

Experiment with different prompt templates:
```python
# In predict_row function
prompt = f"""You are a cultural expert specializing in {country_name}.
Using the provided context, answer this multiple-choice question.
If the context doesn't contain the answer, use your general knowledge.

Context:
{context_text}

Question: {question}
...
"""
```

### Ensemble Methods

Combine multiple models or strategies:
```python
# Majority voting
predictions_k3 = load_predictions('rag_rrf_k3.tsv')
predictions_k5 = load_predictions('rag_rrf_k5.tsv')
predictions_baseline = load_predictions('baseline.tsv')

ensemble = []
for id in all_ids:
    votes = [predictions_k3[id], predictions_k5[id], predictions_baseline[id]]
    ensemble.append({'id': id, 'prediction': max(set(votes), key=votes.count)})
```
