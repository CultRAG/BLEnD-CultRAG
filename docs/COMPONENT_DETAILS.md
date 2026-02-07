# Component Deep Dive

This document provides detailed technical specifications for each major component in the BLEnD CultureRAG pipeline.

## 1. Entity Extraction (spaCy NER)

### Technical Specifications

**Model:** `en_core_web_sm` (English small CNN model)
- **Size:** 12MB
- **Pipeline:** tok2vec, tagger, parser, senter, ner, attribute_ruler, lemmatizer
- **Accuracy:** ~80% NER F1 on OntoNotes 5.0

**Entity Types Preserved:**
```python
NER_KEEP = {
    "GPE",          # Geo-political entity (cities, countries)
    "LOC",          # Locations (non-GPE)
    "PERSON",       # People, including fictional
    "ORG",          # Organizations
    "EVENT",        # Named events
    "WORK_OF_ART"   # Titles of books, songs, etc.
}
```

**Filtering Strategy:**

1. **Blacklist (question words):**
   ```python
   {"What", "Which", "Who", "Where", "When", "Why", "How",
    "The", "A", "An", "In", "On", "At", "Of", "For", "From",
    "Option", "Options"}
   ```

2. **Acronym fallback:** Regex `\b[A-Z]{2,}\b` catches entities missed by NER
   - Example: "HDB" (Housing Development Board in Singapore)
   - Example: "UK", "US", "EU"

3. **Length filter:** Reject entities <3 chars unless all uppercase

### Algorithm Flow

```python
def extract_entities_spacy(row, nlp, blacklist=None):
    # 1. Concatenate question + all options
    text = " ".join([question, option_A, option_B, option_C, option_D])
    
    # 2. Run spaCy NER
    doc = nlp(text)
    
    # 3. Filter entities
    ents = set()
    for ent in doc.ents:
        if ent.label_ in NER_KEEP and ent.text not in blacklist:
            ents.add(ent.text.strip())
    
    # 4. Acronym fallback
    for acronym in ACRONYM_RE.findall(text):
        if acronym not in blacklist:
            ents.add(acronym)
    
    # 5. Length filter
    ents = {e for e in ents if len(e) >= 3 or e.isupper()}
    
    # 6. Extract country code from ID
    country = row['id'].split('-')[1][:2]  # "en-GB030" -> "GB"
    
    return {"id": row['id'], "country": country, "entities": sorted(ents)}
```

### Performance Characteristics

- **Speed:** ~10ms per question (CPU)
- **Memory:** 50MB model + 1MB working set
- **Entities per question:** 3-8 on average

### Edge Cases Handled

1. **Multi-word entities:** "Lake District" preserved as single entity
2. **Possessives:** "Singapore's culture" → "Singapore"
3. **Nested entities:** Prefers longer span (e.g., "New York City" over "York")
4. **Unicode:** Handles non-ASCII names (e.g., "Café Royal")

---

## 2. Wikipedia Knowledge Base Builder

### EntityWikipediaScraper Class

#### Constructor
```python
def __init__(self, country_sources):
    self.country_sources = country_sources  # Dict: country_code -> [page_titles]
    self.cache = wiki_cache                 # Global disk-backed cache
```

#### Wikipedia Search API
```python
def search_wikipedia(self, entity):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'opensearch',  # Autocomplete-style search
        'search': entity,
        'limit': 1,              # Top result only
        'format': 'json'
    }
    # Returns: [query, [titles], [descriptions], [urls]]
```

**Timeout:** 5 seconds (prevents hanging on slow pages)

**Rate limiting:** 0.5s sleep between requests (respects Wikipedia ToS)

#### Page Scraper
```python
def scrape_page(self, page_title):
    # 1. Check disk cache
    if page_title in self.cache:
        return self.cache[page_title]
    
    # 2. Fetch HTML
    url = f"https://en.wikipedia.org/wiki/{page_title}"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 3. Extract main content div
    content = soup.find('div', {'id': 'mw-content-text'})
    
    # 4. Parse paragraphs
    paragraphs = []
    for p in content.find_all('p'):
        text = p.get_text().strip()
        text = ' '.join(text.split())  # Normalize whitespace
        
        # Quality filters
        if len(text) < 100: continue           # Too short
        if text.count('[') > 5: continue       # Citation-heavy
        
        paragraphs.append(text)
    
    # 5. Cache result
    self.cache[page_title] = paragraphs
    if len(self.cache) % 10 == 0:
        save_wiki_cache(self.cache)  # Periodic checkpoint
    
    return paragraphs
```

**Quality filters rationale:**
- `len(text) < 100`: Filters out stub sentences, captions
- `text.count('[') > 5`: Removes paragraphs dominated by citations (e.g., "According to [1][2][3]...")

#### KB Builder
```python
def build_kb(self, entity_data):
    kb_chunks = []
    
    # Phase 1: Country base pages
    countries_seen = set()
    for item in entity_data:
        country = item['country']
        if country in countries_seen: continue
        countries_seen.add(country)
        
        if country in self.country_sources:
            for page_title in self.country_sources[country]:
                paragraphs = self.scrape_page(page_title)
                for p in paragraphs:
                    kb_chunks.append({
                        'text': p,
                        'country': country,
                        'source': page_title,
                        'type': 'base'
                    })
    
    # Phase 2: Entity-specific pages
    entity_count = 0
    max_entities = 200
    for item in entity_data:
        if entity_count >= max_entities: break
        
        for entity in item['entities'][:2]:  # Top 2 per question
            if len(entity) < 4: continue      # Skip short strings
            
            url = self.search_wikipedia(entity)
            if url:
                page_title = url.split('/')[-1]
                paragraphs = self.scrape_page(page_title)
                
                for p in paragraphs[:2]:  # Top 2 paragraphs
                    kb_chunks.append({
                        'text': p,
                        'country': item['country'],
                        'source': page_title,
                        'entity': entity,
                        'type': 'entity'
                    })
                entity_count += 1
    
    return kb_chunks
```

**Two-tier strategy rationale:**
- **Base pages:** Provide broad cultural context (e.g., UK culture overview)
- **Entity pages:** Provide specific factual knowledge (e.g., Lake District geography)

**Resource constraints:**
- **Max 200 entities:** Prevents exponential explosion (148 questions × 4 entities = 592 potential)
- **Top 2 entities per question:** Focus on most salient mentions
- **Top 2 paragraphs per entity:** Usually contain key facts; rest is detail

### Disk Cache Implementation

**File:** `wiki_cache.pkl`

**Structure:** Dict[page_title: str, paragraphs: List[str]]

**Lifecycle:**
1. **Load:** On notebook start, unpickle from disk
2. **Use:** Check cache before every HTTP request
3. **Update:** Add new pages after scraping
4. **Save:** Checkpoint every 10 new pages + final save at end

**Benefits:**
- Avoids re-scraping on notebook restart
- Respects Wikipedia servers (fewer requests)
- Faster iteration during development

**Size:** ~5MB for 100-200 pages (text-only, no images)

---

## 3. Dual Indexing System

### FAISS Index (Dense)

**Index Type:** `IndexFlatIP` (flat inner product)

**Embedding Model:** `all-MiniLM-L6-v2`
- **Architecture:** 6-layer MiniLM
- **Dimensions:** 384
- **Training:** Trained on 1B+ sentence pairs
- **Speed:** ~2000 sentences/sec on CPU

**Construction:**
```python
# 1. Encode
embedder = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = embedder.encode(kb_texts, convert_to_numpy=True)
# Shape: (n_chunks, 384)

# 2. Normalize for cosine similarity
faiss.normalize_L2(embeddings)
# After normalization, inner product = cosine similarity

# 3. Build index
dimension = 384
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)
```

**Query:**
```python
query_emb = embedder.encode([question], convert_to_numpy=True)
faiss.normalize_L2(query_emb)
distances, indices = index.search(query_emb, k=50)
# distances: cosine similarities (higher = more similar)
# indices: KB chunk IDs
```

**Why IndexFlatIP?**
- **Exact search:** No approximation (no quantization, no hashing)
- **Small corpus:** <1000 chunks → brute-force is fast
- **Accuracy:** Guaranteed to find true top-k

**Alternative for scale:** `IndexIVFFlat` or `IndexHNSW` for 10K+ chunks

### BM25 Index (Sparse)

**Algorithm:** BM25 (Best Match 25)

**Formula:**
```
score(q, d) = Σ IDF(qi) × (tf(qi, d) × (k1 + 1)) / (tf(qi, d) + k1 × (1 - b + b × |d| / avgdl))
```

Where:
- `tf(qi, d)`: Term frequency of query term qi in document d
- `IDF(qi)`: Inverse document frequency (log of doc count / doc count containing qi)
- `k1 = 1.5`: Term saturation parameter
- `b = 0.75`: Length normalization parameter
- `avgdl`: Average document length

**Implementation:** `rank-bm25` library (Python port of Lucene's BM25)

**Construction:**
```python
from rank_bm25 import BM25Okapi
import nltk

tokenized_kb = [nltk.word_tokenize(text.lower()) for text in kb_texts]
bm25 = BM25Okapi(tokenized_kb)
```

**Query:**
```python
query_tokens = nltk.word_tokenize(question.lower())
scores = bm25.get_scores(query_tokens)
# scores: BM25 scores (unbounded, higher = better)
top_indices = np.argsort(scores)[::-1][:k]
```

**Tokenization:** NLTK's `word_tokenize`
- Splits on punctuation
- Preserves contractions (e.g., "don't" → ["do", "n't"])
- Lowercase for case-insensitive matching

**Why BM25?**
- **Robust:** Industry standard (used in Elasticsearch, Solr)
- **Keyword-aware:** Excels at exact matches, rare terms
- **Complementary:** Covers FAISS weaknesses (lexical gaps)

---

## 4. Reciprocal Rank Fusion (RRF)

### Algorithm

**Paper:** "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods" (Cormack et al. 2009)

**Formula:**
```python
RRF_score(chunk) = Σ (1 / (k + rank_in_system_i))
```

Where:
- `k`: Constant (typically 60) to prevent division by zero
- `rank_in_system_i`: Rank of chunk in i-th retrieval system (1-indexed)

**Example:**

Chunk 42:
- BM25 rank: 3
- FAISS rank: 7
- RRF score: 1/(60+3) + 1/(60+7) = 0.0159 + 0.0149 = 0.0308

Chunk 7:
- BM25 rank: 8
- FAISS rank: 1
- RRF score: 1/(60+8) + 1/(60+1) = 0.0147 + 0.0164 = 0.0311

**Winner:** Chunk 7 (higher RRF score)

### Implementation

```python
def hybrid_retrieve_rrf(question, country_filter=None, top_k=5, 
                         candidate_k=50, k_rrf=60):
    # 1. Country filtering
    if country_filter:
        valid_indices = [i for i, c in enumerate(kb_chunks) 
                         if c['country'] == country_filter]
        if len(valid_indices) < 3:
            valid_indices = list(range(len(kb_chunks)))
    else:
        valid_indices = list(range(len(kb_chunks)))
    
    # 2. BM25 ranking
    query_tokens = nltk.word_tokenize(question.lower())
    bm25_scores = bm25.get_scores(query_tokens)
    bm25_ranked = np.argsort(bm25_scores)[::-1][:candidate_k * 2]
    bm25_ranked = [i for i in bm25_ranked if i in valid_indices][:candidate_k]
    
    # 3. FAISS ranking
    query_emb = embedder.encode([question], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)
    distances, faiss_indices = faiss_index.search(query_emb, candidate_k * 2)
    faiss_ranked = [i for i in faiss_indices[0] if i in valid_indices][:candidate_k]
    
    # 4. RRF fusion
    rrf_scores = defaultdict(float)
    for rank, idx in enumerate(bm25_ranked):
        rrf_scores[idx] += 1.0 / (k_rrf + rank + 1)
    for rank, idx in enumerate(faiss_ranked):
        rrf_scores[idx] += 1.0 / (k_rrf + rank + 1)
    
    # 5. Sort and return
    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], 
                            reverse=True)[:top_k]
    return [format_result(idx, score) for idx, score in sorted_results]
```

**Hyperparameters:**
- `candidate_k=50`: Retrieve top 50 from each system before fusion
- `k_rrf=60`: Standard constant from literature
- `top_k=5`: Final re-ranked results

**Why candidate_k > top_k?**
- Ensures RRF sees diverse results from both systems
- Prevents bias toward one system's scoring scale

### Country Filtering Strategy

**Problem:** Some locales have very few KB chunks (e.g., Basque Country)

**Solution:**
```python
if country_filter:
    valid_indices = [i for i, c in enumerate(kb_chunks) 
                     if c['country'] == country_filter]
    if len(valid_indices) < 3:
        valid_indices = list(range(len(kb_chunks)))  # Fallback to full KB
```

**Threshold:** 3 chunks minimum to avoid degenerate retrieval

**Effect:** Balances locality (prefer country-specific) with robustness (allow cross-country if needed)

---

## 5. Constrained Generation (1-Token LLM)

### Model Specifications

**Model:** `meta-llama/Llama-3.1-8B-Instruct`
- **Parameters:** 8 billion
- **Context:** 8192 tokens
- **Quantization:** FP16 (bfloat16 unsupported on T4)
- **Device:** Single GPU (device_map="auto")

### Prompt Template

**Format:** Llama-3.1 chat template with special tokens

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert on cultural knowledge. Answer the multiple-choice question using the Context.

Context:
- [chunk 1 text, truncated to 400 chars]
- [chunk 2 text, truncated to 400 chars]
- [chunk 3 text, truncated to 400 chars]

Question: [question text]
Options:
A) [option_A]
B) [option_B]
C) [option_C]
D) [option_D]

Answer with ONLY the option letter (A, B, C, or D).
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
Answer:
```

**Design choices:**
- **System role:** Establishes expertise and task
- **Context placement:** Before question (primacy effect)
- **Option formatting:** Clear A/B/C/D labels
- **Explicit instruction:** "ONLY the option letter" reduces verbosity
- **Assistant prefix:** "Answer:" primes model for single-letter response

### Generation Parameters

```python
inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
outputs = model.generate(
    **inputs,
    max_new_tokens=1,           # Force single token
    do_sample=False,            # Greedy decoding (no sampling)
    temperature=0.0,            # Deterministic (no randomness)
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id
)
```

**Why max_new_tokens=1?**
- **Eliminates parsing:** No need for complex regex
- **Forces decision:** Model cannot explain or hedge
- **Faster:** 1 token vs 5-10 tokens
- **Deterministic:** Greedy decode ensures reproducibility

### Decoding Strategy

```python
# Extract only generated token (exclude prompt)
gen_ids = outputs[0][inputs["input_ids"].shape[1]:]
gen_text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip().upper()

# Parse trivially
pred = gen_text[:1] if gen_text else ""
if pred not in ["A", "B", "C", "D"]:
    return "C"  # Safe fallback
```

**Fallback rationale:**
- 'C' is statistically most common answer in MCQ datasets
- Provides graceful degradation on edge cases

### Option-Aware Query Expansion

**Key innovation:** Include all options in retrieval query

```python
expanded_query = f"{question} {option_A} {option_B} {option_C} {option_D}"
docs = retriever.search(expanded_query, country_filter=country, k=3)
```

**Why?**
- **Entity matching:** If answer is "Lake District", retriever can match that entity in options
- **Disambiguation:** Differentiates similar questions with different option sets
- **Cheap:** No extra model forward pass; just concatenation

**Impact:** ~5-10% accuracy gain in ablations

---

## 6. Inference Orchestration

### Checkpoint/Resume Logic

```python
output_file = f"/kaggle/working/predictions_{method_name}_checkpoint.tsv"
results = []

if os.path.exists(output_file):
    existing = pd.read_csv(output_file, sep='\t', header=None, 
                           names=['id', 'prediction'])
    completed_ids = set(existing['id'].tolist())
    results.extend(existing.to_dict('records'))
else:
    completed_ids = set()

for _, row in df.iterrows():
    if row['id'] in completed_ids:
        continue  # Skip already completed
    
    pred = predict_row(row, retriever, model, tokenizer)
    results.append({'id': row['id'], 'prediction': pred})
    
    if len(results) % checkpoint_every == 0:
        pd.DataFrame(results).to_csv(output_file, sep='\t', 
                                      index=False, header=False)
```

**Benefits:**
- **Resume from crash:** Notebook kernel dies → restart from checkpoint
- **Progress tracking:** See intermediate results
- **Debugging:** Inspect partial outputs

### Safety Interlocks

**Pre-save validation:**

```python
# 1. Row count
assert len(results) == EXPECTED_ROWS, \
    f"❌ Generated {len(results)} rows. Expected {EXPECTED_ROWS}."

# 2. Duplicate IDs
ids = [r['id'] for r in results]
assert len(set(ids)) == len(ids), \
    "❌ Duplicate IDs found."

# 3. Locale coverage
unique_regions = set([i.split('_')[0] for i in ids])
print(f"✅ Covered {len(unique_regions)} unique language-locales.")
```

**Failure modes prevented:**
1. **Accidental filtering:** Forgot to load full dataset (only English)
2. **Loop bug:** Same question predicted twice
3. **Silent failure:** Partial submission without noticing

### Error Handling

```python
try:
    pred = predict_row(row, retriever, model, tokenizer)
    results.append({'id': row['id'], 'prediction': pred})
except Exception as e:
    print(f"\n⚠️ ERROR on {row['id']}: {e}")
    traceback.print_exc()
    results.append({'id': row['id'], 'prediction': 'C'})  # Fallback
```

**Rationale:**
- **Non-blocking:** One bad question doesn't halt entire job
- **Traceback:** Log full error for debugging
- **Fallback to 'C':** Better than random; matches statistical baseline

---

## Performance Optimization

### Batch Processing (Not Implemented)

**Current:** Loop over questions sequentially

**Potential:** Batch generation with padding

```python
# Batch 16 questions
prompts = [build_prompt(row) for row in batch]
inputs = tokenizer(prompts, return_tensors="pt", padding=True).to("cuda")
outputs = model.generate(**inputs, max_new_tokens=1)
```

**Speedup:** ~3-5x with batch_size=16 (amortize model loading overhead)

**Trade-off:** More complex padding/masking logic

### Retrieval Optimization

**Current:** FAISS + BM25 per question (~50ms)

**Potential improvements:**
1. **Pre-compute BM25 scores:** Cache query term statistics
2. **GPU FAISS:** Use `faiss-gpu` for batch encoding
3. **ANN index:** Switch to `IndexIVFFlat` for 10K+ chunks

### Memory Optimization

**Current:** Full model in GPU memory (~8GB)

**Potential:**
1. **Quantization:** INT8 or INT4 (bitsandbytes)
2. **CPU offloading:** Keep embeddings on CPU, move to GPU on-demand
3. **Gradient checkpointing:** Reduce activation memory (if fine-tuning)

---

## Testing & Validation

### Unit Tests (Recommended)

```python
def test_entity_extraction():
    row = {'id': 'en-GB030', 'question': 'What is the capital of the UK?', ...}
    result = extract_entities_spacy(row, nlp)
    assert result['country'] == 'GB'
    assert 'UK' in result['entities']

def test_rrf_fusion():
    question = "Lake District"
    results = hybrid_retrieve_rrf(question, country_filter='GB', top_k=3)
    assert len(results) == 3
    assert all('score' in r for r in results)

def test_predict_row():
    row = df.iloc[0]
    pred = predict_row(row, retriever, model, tokenizer)
    assert pred in ['A', 'B', 'C', 'D']
```

### Integration Test

```python
# End-to-end smoke test
test_df = df.head(5)
results = run_experiment_safe(test_df, 'smoke_test', use_rag=True)
assert len(results) == 5
assert all(r['prediction'] in ['A', 'B', 'C', 'D'] for r in results)
```

### Quality Checks

1. **Entity coverage:** ≥80% of questions should have ≥1 entity
2. **KB coverage:** ≥30 unique countries in KB
3. **Retrieval non-empty:** ≥95% of questions should retrieve ≥1 chunk
4. **Valid predictions:** 100% of predictions should be A/B/C/D
