# BLEnD CultureRAG Notebook Guide

This document explains how the notebook works, what each cell block does, and how to run it end-to-end for the full 148-question dataset.

## What the pipeline does
- Builds a culture-focused knowledge base (KB) from Wikipedia using spaCy-derived entities plus country seed pages.
- Indexes the KB with FAISS (dense) and BM25 (sparse), then fuses them via Reciprocal Rank Fusion (RRF).
- Runs option-aware retrieval and a constrained 1-token decoder so the model outputs exactly A/B/C/D.
- Adds crash-proof inference with checkpoints and safety interlocks (row-count, duplicate IDs, locale coverage).

## Run order (clean session)
1) **Install + imports**: installs core deps, loads libraries.
2) **Entity extraction (spaCy)**: extracts entities per question; tags country codes.
3) **Cache + KB build**: loads/saves disk cache; scrapes Wikipedia country/entity pages; builds `kb_chunks`.
4) **Index build**: encodes KB with `all-MiniLM-L6-v2`; builds FAISS and BM25 indices.
5) **Retriever**: RRF fusion with a `.search(...)` wrapper returning `page_content`.
6) **Predictor**: `predict_row` forces 1-token (A/B/C/D) decoding using option-aware query + retrieved context.
7) **Inference loop**: `run_experiment_safe` with checkpoints, resume, and safety interlocks before final save.
8) **Optional analysis**: latency benchmarks and baseline-vs-RAG diffs.

## Key data objects
- `df`: full input dataframe (148 rows, all languages; no filtering).
- `entity_data`: per-question entities + country code.
- `kb_chunks`: list of KB paragraphs with metadata (`text`, `country`, `source`, `type`).
- `faiss_index`, `bm25`: dense/sparse indices over `kb_chunks`.
- `retriever`: wrapper exposing `.search(query, country_filter, k)` returning docs with `page_content`.

## Core functions
- `extract_entities_spacy(row, nlp)`: spaCy NER + acronym fallback; emits country/entities.
- `EntityWikipediaScraper.build_kb(entity_data)`: scrapes base pages by country and entity pages (rate-limited, cached).
- `hybrid_retrieve_rrf(question, country_filter, top_k, candidate_k, k_rrf)`: RRF fusion over BM25 + FAISS.
- `predict_row(row, hybrid_retriever, model, tokenizer)`: option-aware query; retrieves; prompts; forces 1-token A/B/C/D with greedy decode; safe fallback to C.
- `run_experiment_safe(df, method_name, use_rag, checkpoint_every)`: checkpointed inference, resume, safety checks (row count 148, duplicate IDs, locale coverage) before final save.

## Outputs
- Checkpoints: `/kaggle/working/predictions_<method>_checkpoint.tsv`
- Finals: `/kaggle/working/predictions_<method>.tsv`
- Methods: `baseline`, `rag_rrf_k3`, `rag_rrf_k5`

## Safety rails
- No language filter; asserts 148 rows produced.
- Duplicate-ID check and locale coverage check before final write.
- Constrained decoding avoids brittle regex parsing.
- Disk-backed cache prevents re-scraping on reruns.

## Tips & gotchas
- Ensure internet on first run to populate the Wikipedia cache; subsequent runs reuse `wiki_cache.pkl`.
- Run cells in order; avoid legacy/deprecated cells if present.
- If a run crashes, rerun from the inference cell: it will resume from the checkpoint.
- GPU memory: model runs with greedy 1-token decode; keep batch size at 1.

## Minimal run sequence
1) Install/Imports.
2) Entity extraction.
3) KB build + cache save.
4) Index build (FAISS/BM25).
5) Retriever cell.
6) Predictor cell.
7) Inference cell (produces TSVs).

## Submission reminder
Use the full-dataset outputs from the inference cell (e.g., `predictions_rag_rrf_k3.tsv`). Do **not** use any English-only or deprecated cells.
