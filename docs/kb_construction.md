# Knowledge Base Construction

This document describes how the BLEnD-CultureRAG knowledge base was built, how trust tiers are assigned, and why oracle coverage limits the system's effectiveness.

---

## KB Statistics

| Property | Value |
|---|---|
| Total chunks | 1,262 |
| Country shards | 7 |
| Countries covered | 30 |
| Avg. chunk length | ~300 tokens |
| Embedding model | `all-MiniLM-L6-v2` (384-dim) |
| Sparse index | BM25 (k1 = 1.5, b = 0.75) |
| Dense index | FAISS (cosine similarity) |

---

## Source Taxonomy

### Three-Tier Trust Model

Each source is assigned a trust weight that scales its RRF score during retrieval.

| Tier | Weight | Description | Examples |
|---|---|---|---|
| **High** | 1.0 | Authoritative, editorially reviewed, or peer-reviewed | Academic publications, government statistics, curated cultural datasets |
| **Mid** | 0.6 | Community-edited with moderation and citation norms | Wikipedia articles, established news outlets |
| **Low** | 0.3 | Unverified or user-generated content | Web scrapes, forum posts, blog entries |

These weights were selected based on source reliability heuristics. In practice, they had **no measurable effect** on accuracy (Phase 5 = Phase 4 = 78.5%) because the KB is dominated by mid-tier Wikipedia content, leaving insufficient tier diversity for reranking to alter passage selection.

### Source Composition

The KB draws from three primary source types:

1. **Wikipedia articles** — Country-specific cultural pages (food, holidays, sports, customs). These form the bulk (~80%) of the KB and are all mid-tier (0.6).
2. **Web-scraped pages** — Cached cultural content from web searches. Tagged as low-tier (0.3).
3. **Curated entity files** — Structured data files (JSON) mapping cultural entities to countries. Mixed-tier depending on origin.

Source files live in:
- `cache-json-files/kb_chunks_filtered (1).json` — Filtered KB chunks
- `cache-json-files/kb_chunks_intent.json` — Intent-annotated chunks
- `cache-json-files/wiki_cache (2).json` — Cached Wikipedia content
- `cache-json-files/web_cache.json` — Cached web search results
- `cache-json-files/entity_to_title.json` — Entity-to-Wikipedia-title mappings

---

## Chunking Strategy

Each document was split into overlapping windows of approximately 300 tokens with 50-token overlap. Chunks were tagged with:
- **country** — ISO country code or full name
- **source_tier** — `high`, `mid`, or `low`
- **source_url** — Original URL for traceability

---

## Oracle Coverage

Oracle coverage measures whether the KB *could* answer a question, regardless of whether the retrieval pipeline actually surfaces the right passage.

$$\text{Cov}(q_i) = \mathbb{1}\bigl[\exists\, d \in \text{KB}(q_i) : \text{gold}_i \in d\bigr]$$

$$\bar{C} = \frac{1}{N} \sum_{i=1}^{N} \text{Cov}(q_i) = \frac{19{,}148}{47{,}014} = 0.407$$

**40.7% of questions have retrievable evidence.**

This means that for 59.3% of questions, no passage in the KB contains the gold answer. Any retrieval for these questions can only introduce noise.

### Coverage by Country

| Country | Coverage |
|---|---|
| Bulgaria | 69% |
| Ecuador | 68% |
| Ethiopia | 65% |
| ... | ... |
| Algeria | 26% |
| North Korea | 26% |
| Great Britain | 21% |

Countries with low coverage (Great Britain, North Korea) are precisely those where the model already has strong parametric knowledge (GB) or where cultural data is scarce (NK).

---

## KB Limitations

1. **Insufficient coverage.** At 40.7%, the KB cannot answer more than 4 in 10 questions even with perfect retrieval. The parametric baseline already answers 78.6%.
2. **Tier homogeneity.** ~80% of content is mid-tier Wikipedia. Trust weighting is ineffective without tier diversity.
3. **Static snapshot.** The KB was built once and not updated. Cultural knowledge drifts over time (new holidays, changing customs).
4. **English-only.** All sources are in English. Non-English cultural nuances may be lost in translation or absent from English-language sources entirely.
5. **No negative evidence.** The KB contains only affirmative statements. It cannot help the model reject a plausible-but-wrong option.

---

## Rebuild Pseudocode

To rebuild the KB from scratch:

```python
# 1. Collect sources
wiki_pages   = fetch_wikipedia_cultural_pages(countries=COUNTRY_LIST)
web_pages    = fetch_web_search_results(queries=CULTURAL_QUERIES, cache="web_cache.json")
entity_data  = load_entity_mappings("entity_to_title.json")

# 2. Chunk documents
chunks = []
for doc in wiki_pages + web_pages + entity_data:
    for window in sliding_window(doc.text, size=300, overlap=50):
        chunks.append({
            "text":        window,
            "country":     doc.country,
            "source_tier": classify_tier(doc.source_url),
            "source_url":  doc.source_url
        })

# 3. Build indices
bm25_index  = build_bm25(chunks, k1=1.5, b=0.75)
embeddings  = encode(chunks, model="all-MiniLM-L6-v2")
faiss_index = build_faiss(embeddings, metric="cosine")

# 4. Compute oracle coverage
oracle_hits = 0
for q in questions:
    country_chunks = [c for c in chunks if c["country"] == q.country]
    if any(q.gold_answer in c["text"] for c in country_chunks):
        oracle_hits += 1
coverage = oracle_hits / len(questions)
print(f"Oracle coverage: {coverage:.1%}")  # Expected: ~40.7%
```

---

## Recommendations for KB Expansion

To make RAG effective for BLEnD Track 2, oracle coverage must exceed the parametric accuracy (78.6%). This requires:

1. **Targeted gap-filling.** Identify the 59.3% of questions with no KB coverage and scrape/curate sources specifically for those cultural topics.
2. **Multi-source aggregation.** Add government cultural databases, UNESCO documents, and non-English Wikipedia (translated).
3. **Dynamic refresh.** Periodically re-scrape and re-index to capture evolving cultural facts.
4. **Coverage monitoring.** Track $\bar{C}$ by country after each KB update to ensure equitable improvements across all 30 countries.
