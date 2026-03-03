# System Architecture

BLEnD-CultureRAG is a six-phase retrieval-augmented generation pipeline for answering culturally grounded multiple-choice questions. Each phase adds exactly one component; every component is ablatable.

---

## Pipeline Diagram

```
Question (q_i, country_i)
        │
        ▼
┌──────────────────────┐
│  Phase 1: Country    │  Filter KB to country_i
│  Filter              │  only relevant shards
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Phase 2: Intent     │  Keyword classifier → label
│  Detection           │  95.6% non-"others"
│                      │  (zero downstream effect)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Phase 3: Tiered     │  BM25 + FAISS → RRF merge
│  Retrieval + RRF     │  top-k = 3 passages
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Phase 4: Anti-Leak  │  Remove chunks containing
│  Quality Filter      │  answer option text
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Phase 5: Trust      │  Rerank by source trust
│  Reranking           │  high=1.0, mid=0.6, low=0.3
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Phase 6: Constrained│  LLM generation with
│  Decoding            │  regex constraint → {A,B,C,D}
└──────────┬───────────┘
           │
           ▼
      Answer ∈ {A, B, C, D}
```

---

## Phase-by-Phase Description

### Phase 1: Country Filter

Restrict the knowledge base to chunks tagged with the question's country code. This prevents cross-country contamination (e.g., Japanese food facts leaking into Ethiopian questions).

**Result:** No accuracy change over RAG Basic (77.9%). Country-filtering is already implicit in properly constructed KB shards; the explicit filter is a safety net.

### Phase 2: Intent Detection

A keyword-based classifier maps each question to one of 16 cultural intent categories (`food_drink`, `sports`, `education_knowledge_systems`, `geography_places`, etc.).

Distribution: `food_drink` 46.6%, `sports` 44.0%, `others` 4.4%, `education` 4.1%, `geography` 0.6%, `language` 0.3%.

The classifier assigns meaningful labels to 95.6% of questions. However, intent-conditioned prompt templates produced **zero downstream accuracy change** (Ph1 = Ph2 = 77.9%). The bottleneck was prompt-template design, not classification coverage.

### Phase 3: Tiered Retrieval with Reciprocal Rank Fusion

Two retrieval paths run in parallel:

1. **BM25** (sparse): Term-frequency matching with parameters k1 = 1.5, b = 0.75.
2. **FAISS** (dense): Cosine similarity over `all-MiniLM-L6-v2` embeddings (384-dimensional).

Scores are merged via Reciprocal Rank Fusion:

$$\text{RRF}(d) = \sum_{r \in \{BM25, FAISS\}} \frac{1}{k + \text{rank}_r(d)}, \quad k = 60$$

The top-3 passages by RRF score are selected.

**Result:** 77.6% (−0.3 pp from Ph2). Tiered retrieval alone hurts slightly because it surfaces more passages, increasing the chance of answer-anchoring noise.

### Phase 4: Anti-Leak Quality Filter

Removes any retrieved passage that contains the exact text of one or more answer options. This prevents the model from anchoring on a passage that trivially mentions the answer.

**Result:** 78.5% (+0.9 pp from Ph3). The largest single-phase improvement. Without this filter, raw retrieval introduces answer text that biases the LLM toward whichever option appears verbatim in a passage.

### Phase 5: Trust-Weighted Reranking

Each KB source is assigned a trust tier:

| Tier | Weight | Sources |
|---|---|---|
| High | 1.0 | Academic, government, curated datasets |
| Mid | 0.6 | Wikipedia, established media |
| Low | 0.3 | Web scrapes, forums, unverified |

RRF scores are multiplied by trust weights before final passage selection.

The trust weight is applied as:

$$\text{score}_{\text{final}}(d) = w_{\text{trust}}(d) \cdot \text{RRF}(d)$$

**Result:** 78.5% (no change from Ph4). Trust reranking does not improve accuracy because the KB is dominated by mid-tier (Wikipedia) sources — there is insufficient tier diversity for reranking to change the passage selection.

### Phase 6: Constrained Decoding

Forces the model to output exactly one of `{A, B, C, D}` via regex-constrained generation. This eliminates parsing failures and ensures every question receives a valid answer.

**Result:** 78.5% (no change from Ph5). All prior phases already produced parseable answers, so the constraint is a no-op in practice but prevents silent failures at scale.

---

## Coverage Ceiling

The **oracle coverage** $\bar{C}$ measures what fraction of questions have at least one KB passage containing the gold answer:

$$\bar{C} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\bigl[\exists\, d \in \text{KB}(q_i) : \text{gold}_i \in d\bigr]$$

For our KB: $\bar{C} = 0.407$ (19,148 / 47,014).

The **retrieval ceiling gap** is:

$$\Delta_{\text{ceil}} = \text{Acc}_{\text{parametric}} - \bar{C} = 0.786 - 0.407 = +0.379$$

When the model's parametric knowledge already answers 78.6% of questions correctly, and only 40.7% of questions have retrievable evidence, RAG cannot contribute net-positive signal. The 37.9-point gap explains why every RAG configuration either matched or underperformed the baseline.

---

## Key Insight

This architecture is sound in design but was deployed against a knowledge base that is too sparse for the task. The anti-leak filter (Phase 4) is the only component that demonstrably helps, and it does so by *removing* harmful retrieval noise rather than by adding useful information. Future work should prioritize KB expansion (raising $\bar{C}$ above the parametric accuracy) before adding more pipeline sophistication.
