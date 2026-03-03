# Pipeline Configuration Reference

Complete hyperparameter table for the BLEnD-CultureRAG pipeline. Every tunable value in one place.

---

## Model Configuration

| Parameter | Value | Notes |
|---|---|---|
| Model | `meta-llama/Meta-Llama-3.1-8B-Instruct` | Instruction-tuned Llama 3.1 |
| Backend | LMDeploy TurboMind | Optimized inference engine |
| Tensor parallelism | `tp = 2` | Split across 2× T4 GPUs |
| Batch size | 64 | Per-GPU batch for inference |
| Temperature | 0.0 | Greedy decoding (deterministic) |
| Top-k | 1 | Single-token sampling |
| Max new tokens | 1 | Constrained to single letter |
| Output constraint | Regex: `[ABCD]` | Forces valid MCQ answer |

---

## Retrieval Configuration

### BM25 (Sparse)

| Parameter | Value | Description |
|---|---|---|
| Algorithm | BM25Okapi | Okapi variant |
| k1 | 1.5 | Term frequency saturation |
| b | 0.75 | Document length normalization |

### FAISS (Dense)

| Parameter | Value | Description |
|---|---|---|
| Embedding model | `all-MiniLM-L6-v2` | Sentence-Transformers |
| Embedding dimension | 384 | Fixed by model architecture |
| Similarity metric | Cosine | L2-normalized + inner product |
| Index type | `IndexFlatIP` | Exact search (no approximation) |

### Reciprocal Rank Fusion

| Parameter | Value | Description |
|---|---|---|
| RRF constant $k$ | 60 | Smoothing constant in $\frac{1}{k + \text{rank}}$ |
| Top-k passages | 3 | Number of passages passed to LLM |

$$\text{RRF}(d) = \sum_{r \in \{BM25, FAISS\}} \frac{1}{60 + \text{rank}_r(d)}$$

---

## Trust Weighting

| Tier | Weight | Sources |
|---|---|---|
| High | 1.0 | Academic, government, curated datasets |
| Mid | 0.6 | Wikipedia, established media |
| Low | 0.3 | Web scrapes, forums, unverified |

Applied as: $\text{score}_{\text{final}}(d) = w_{\text{trust}}(d) \cdot \text{RRF}(d)$

---

## NLP Components

| Component | Model/Library | Purpose |
|---|---|---|
| NER | spaCy `en_core_web_sm` | Entity extraction for KB linking |
| Sentence embeddings | `all-MiniLM-L6-v2` | Dense retrieval |
| Tokenizer | Llama-3.1 tokenizer | Input tokenization |

---

## Intent Detection

| Parameter | Value |
|---|---|
| Method | Keyword matching (16 categories) |
| Categories | `food_drink`, `sports`, `education_knowledge_systems`, `geography_places`, `language_writing`, + 11 others |
| Fallback label | `others` |
| Coverage | 95.6% non-"others" |
| Downstream effect | None (zero accuracy change) |

---

## Anti-Leak Filter

| Parameter | Value | Description |
|---|---|---|
| Match type | Exact substring | Case-insensitive |
| Scope | All 4 answer options | Check A, B, C, D text against each passage |
| Action | Remove passage | Drop from candidate set |

A passage is removed if it contains the exact text of any answer option. This prevents answer-anchoring bias.

---

## Knowledge Base

| Parameter | Value |
|---|---|
| Total chunks | 1,262 |
| Country shards | 7 |
| Countries covered | 30 |
| Avg. chunk length | ~300 tokens |
| Chunk overlap | ~50 tokens |
| Oracle coverage | 40.7% (19,148 / 47,014) |

---

## Statistical Testing

| Parameter | Value | Description |
|---|---|---|
| Significance test | McNemar's test | Paired, per-question comparison |
| Continuity correction | Yes | $z = (|b-c|-1) / \sqrt{b+c}$ |
| Effect size | Cohen's h | $h = 2 \arcsin\sqrt{p_1} - 2 \arcsin\sqrt{p_2}$ |
| Confidence intervals | Wilson score | 95% CI with $z = 1.96$ |

Wilson score interval formula:

$$\hat{p}_{\pm} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

---

## Kaggle Environment

| Setting | Value |
|---|---|
| Accelerator | GPU T4 × 2 |
| Internet | On (for package installation) |
| Persistence | Session-scoped (no persistent disk) |
| Runtime limit | 12 hours |
| RAM | 13 GB |
| VRAM | 2 × 16 GB |

---

## Values NOT Tuned

The following were fixed at conventional defaults and not hyperparameter-searched:

- BM25 k1 and b (standard IR defaults)
- RRF k = 60 (standard in literature)
- Top-k = 3 (common for RAG)
- Trust weights (set by heuristic, not optimized)
- Chunk size / overlap (standard ~300/50)

No hyperparameter tuning was performed. All values are either standard defaults from the literature or manually selected heuristics. This is noted as a limitation in the paper.
