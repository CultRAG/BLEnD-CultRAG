# BLEnD CultureRAG Architecture

## System Overview

The BLEnD CultureRAG system is a Retrieval-Augmented Generation (RAG) pipeline designed for multi-cultural multiple-choice question answering. It combines entity extraction, Wikipedia knowledge retrieval, hybrid search, and constrained language model generation.

## High-Level Architecture

```
Input Dataset (148 questions, 30+ locales)
    ↓
Entity Extraction (spaCy NER)
    ↓
Knowledge Base Construction (Wikipedia scraping)
    ↓
Dual Indexing (FAISS + BM25)
    ↓
Hybrid Retrieval (RRF Fusion)
    ↓
Constrained Generation (1-token LLM)
    ↓
Output Predictions (TSV files)
```

## Core Components

### 1. Entity Extraction Layer
**Purpose:** Extract culturally relevant entities from questions to guide knowledge retrieval.

**Technology:** spaCy `en_core_web_sm` NER model

**Process:**
- Loads question text + all four options
- Runs spaCy NER to identify: GPE (geo-political entity), LOC (location), PERSON, ORG (organization), EVENT, WORK_OF_ART
- Applies acronym regex fallback for all-caps entities (e.g., "HDB", "UK")
- Filters out question words and stopwords via blacklist
- Extracts country code from question ID (e.g., "en-GB030" → "GB")

**Output:** `entity_data` list with structure:
```python
{
    'id': 'en-GB030',
    'country': 'GB',
    'entities': ['Lake District', 'Cumberland', 'UK']
}
```

### 2. Knowledge Base Construction
**Purpose:** Build a culture-specific corpus from Wikipedia.

**Components:**
- **Disk Cache:** Persistent pickle file (`wiki_cache.pkl`) stores scraped pages
- **EntityWikipediaScraper:** Orchestrates Wikipedia API calls and scraping

**Two-tier scraping strategy:**

**Tier 1 - Country Base Pages:**
- Uses `country_sources.json` to map country codes → Wikipedia culture pages
- Example: `GB → ["Culture_of_the_United_Kingdom", "British_culture"]`
- Scrapes full article content for foundational knowledge

**Tier 2 - Entity Pages:**
- For each question, takes top 2 extracted entities
- Wikipedia search API finds best-matching article
- Scrapes top 2 paragraphs per entity page
- Rate-limited to 200 entities max (with 0.5s delay between requests)

**Quality filters:**
- Minimum 100 characters per paragraph
- Maximum 5 citation brackets to avoid reference noise
- Normalizes whitespace

**Output:** `kb_chunks` list with structure:
```python
{
    'text': 'The Lake District is a mountainous region...',
    'country': 'GB',
    'source': 'Lake_District',
    'type': 'entity',  # or 'base'
    'entity': 'Lake District'  # only for entity chunks
}
```

**Typical KB size:** 400-800 chunks across 30+ countries

### 3. Dual Indexing System

**Purpose:** Enable both semantic and lexical search over the knowledge base.

#### FAISS Index (Dense Retrieval)
- **Model:** `all-MiniLM-L6-v2` sentence transformer (384 dimensions)
- **Process:**
  1. Encode all KB chunks into embeddings
  2. L2-normalize vectors for cosine similarity
  3. Build `IndexFlatIP` (inner product) index
- **Strength:** Captures semantic similarity (synonyms, paraphrases)

#### BM25 Index (Sparse Retrieval)
- **Model:** BM25Okapi (probabilistic term-frequency ranking)
- **Process:**
  1. Tokenize all KB chunks with NLTK
  2. Build inverse document frequency statistics
- **Strength:** Captures exact keyword matches, rare terms

### 4. Hybrid Retrieval with RRF

**Purpose:** Combine semantic and lexical search results for robust retrieval.

**Algorithm:** Reciprocal Rank Fusion (RRF)

**Process:**
1. **Country filtering:** Pre-filter KB to question's country code (falls back to full KB if <3 matches)
2. **Dual ranking:**
   - BM25: Tokenize query → score all chunks → rank top 50
   - FAISS: Embed query → normalize → search top 50
3. **RRF scoring:** For each chunk, accumulate scores:
   ```python
   score = sum(1.0 / (k_rrf + rank + 1))  # k_rrf = 60
   ```
4. **Re-ranking:** Sort by combined RRF score, return top-k

**Why RRF?**
- Scale-invariant (BM25 and FAISS scores have different ranges)
- Proven robust in information retrieval benchmarks
- No hyperparameter tuning needed

**API:** `hybrid_retrieve_rrf(question, country_filter, top_k, candidate_k, k_rrf)`

Returns list of dicts with `text`, `country`, `source`, `score`, `index`

### 5. Retriever Wrapper

**Purpose:** Provide consistent API for prediction function.

**Class:** `HybridRetrieverWrapper`

**Method:** `.search(query, country_filter=None, k=3)`

**Transformation:** Converts RRF results to Langchain-style format with `page_content` key

### 6. Constrained Generation Layer

**Purpose:** Generate MCQ answer with deterministic 1-token decoding.

**Model:** Llama-3.1-8B-Instruct (via HuggingFace Transformers)

**Innovation:** Forces model to emit **exactly one token** (A/B/C/D) instead of free-form generation + parsing.

**Process:**
1. **Option-aware query expansion:** Concatenate question + all 4 options
2. **Retrieval:** Call hybrid retriever with country filter, get top 3 chunks
3. **Prompt construction:**
   ```
   System: You are an expert on cultural knowledge.
   Context: [retrieved chunks, 400 chars each]
   Question: [question text]
   Options:
   A) [option_A]
   B) [option_B]
   C) [option_C]
   D) [option_D]
   Answer with ONLY the option letter.
   Assistant: Answer:
   ```
4. **Constrained generation:**
   - `max_new_tokens=1`
   - `do_sample=False` (greedy)
   - `temperature=0.0` (deterministic)
5. **Trivial parsing:** Take first character of generated token; fallback to 'C' if invalid

**Why 1-token?**
- Eliminates regex parsing brittleness
- Prevents model from generating explanations or reasoning
- Guarantees valid A/B/C/D output
- Faster inference (1 token vs 5-10 tokens)

**Function:** `predict_row(row, hybrid_retriever, model, tokenizer)`

### 7. Inference Orchestration

**Purpose:** Robust, crash-proof batch inference with safety checks.

**Function:** `run_experiment_safe(df, method_name, use_rag, checkpoint_every)`

**Features:**

#### Checkpoint/Resume
- Saves progress every N rows to `/kaggle/working/predictions_{method}_checkpoint.tsv`
- On restart, loads checkpoint and skips completed IDs
- Critical for long-running jobs on unstable kernels

#### Error Handling
- Try-except per question
- Falls back to 'C' on error (most common answer in datasets)
- Logs full traceback without halting

#### Safety Interlocks (pre-save)
1. **Row count check:** Assert exactly 148 predictions (no accidental filtering)
2. **Duplicate ID check:** Assert all IDs unique (detects loop bugs)
3. **Locale coverage check:** Report number of unique language-country pairs

**Outputs:**
- Checkpoint: `predictions_{method}_checkpoint.tsv`
- Final: `predictions_{method}.tsv`

**Methods run:**
- `baseline`: All 'C' predictions (control)
- `rag_rrf_k3`: RAG with top-3 retrieval
- `rag_rrf_k5`: RAG with top-5 retrieval

## Data Flow Example

**Input:** Question "What is the capital of the UK?"

1. **Entity extraction:**
   - Entities: `['UK']`
   - Country: `GB`

2. **KB scraping (cached):**
   - Base pages: Culture_of_the_United_Kingdom
   - Entity pages: United_Kingdom

3. **Indexing:**
   - FAISS embeds all chunks
   - BM25 tokenizes all chunks

4. **Query time:**
   - Expanded query: "What is the capital of the UK? London Edinburgh Manchester Cardiff"
   - BM25 ranks: [chunk_42: 18.3, chunk_7: 12.1, ...]
   - FAISS ranks: [chunk_7: 0.89, chunk_42: 0.84, ...]
   - RRF fuses: [chunk_7: 0.041, chunk_42: 0.038, ...]

5. **Generation:**
   - Top 3 chunks inserted as context
   - Model sees: "London is the capital and largest city of the United Kingdom..."
   - Generates: Token `A` (London)

6. **Output:** `en-GB030\tA`

## Performance Characteristics

**Memory:**
- Model: ~8GB GPU (FP16)
- FAISS index: ~100MB (400 chunks × 384 dims × 4 bytes)
- BM25 index: ~10MB

**Latency (T4 GPU):**
- Retrieval: ~50ms (BM25 + FAISS + RRF)
- Generation: ~200ms (1-token decode)
- End-to-end: ~250ms/question

**Throughput:**
- ~240 questions/minute (single GPU)
- ~148 questions in 37 seconds

## Robustness Features

1. **Disk caching:** Wikipedia pages persist across notebook restarts
2. **Checkpointing:** Resume from crash without re-inference
3. **Country fallback:** If country filter too restrictive, use full KB
4. **Safe parsing:** 1-token decode eliminates regex edge cases
5. **Error fallback:** 'C' on exception (most common MCQ answer statistically)
6. **Safety interlocks:** Prevent accidental partial submissions

## Extension Points

- **More entities:** Increase `max_entities` from 200
- **Better embeddings:** Swap `all-MiniLM-L6-v2` for larger model
- **Re-ranking:** Add cross-encoder re-ranker after RRF
- **Multi-hop:** Retrieve entities from context, expand iteratively
- **Prompt tuning:** Few-shot examples in system prompt
- **Ensemble:** Combine multiple retrieval strategies or models
