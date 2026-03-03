# Full Numerical Results

All results are on BLEnD Track 2: 47,014 English MCQs, 4 options (A/B/C/D), 30 country-language pairs.
Model: Llama-3.1-8B-Instruct. Inference: LMDeploy TurboMind tp=2 on 2× NVIDIA T4 (Kaggle).

---

## 1. Ablation Study

| Configuration | Correct | Acc (%) | 95% CI | Δ Base |
|---|---|---|---|---|
| Baseline (LLM only) | 36,932 | 78.6 | [78.2, 78.9] | — |
| RAG Basic (unfiltered) | 36,639 | 77.9 | [77.6, 78.3] | −0.6 |
| + Country Filter (Ph1) | 36,639 | 77.9 | [77.6, 78.3] | −0.6 |
| + Intent Detection (Ph2) | 36,639 | 77.9 | [77.6, 78.3] | −0.6 |
| + Tiered Routing (Ph3) | 36,465 | 77.6 | [77.2, 77.9] | −1.0 |
| + Anti-Leak Quality (Ph4) | 36,928 | 78.5 | [78.2, 78.9] | −0.0 |
| + Trust Reranking (Ph5) | 36,928 | 78.5 | [78.2, 78.9] | −0.0 |
| Full System (Ph6) † | 36,928 | 78.5 | [78.2, 78.9] | −0.0 |

† Official submission.

---

## 2. McNemar's Paired Significance Tests

| Comparison | Δ Acc | p-value | Significant | Cohen's h | Effect |
|---|---|---|---|---|---|
| Baseline vs. RAG Basic | −0.6 | < 0.0001 | Yes | 0.015 | Small |
| Baseline vs. Full System | −0.0 | 0.962 | No | 0.000 | None |
| RAG Basic vs. Full System | +0.6 | < 0.0001 | Yes | 0.015 | Small |

All tests use McNemar's continuity-corrected z-statistic: $z = (|b-c|-1) / \sqrt{b+c}$ where $b$ and $c$ are discordant pair counts.

---

## 3. RAG Backfire Decomposition

Per-question outcomes form a 2×2 contingency table: both correct ($a$), baseline-only correct ($b$), system-only correct ($c$), both wrong ($d$). Net change = $c - b$.

### Baseline vs. RAG Basic

| Metric | Value |
|---|---|
| System-only correct (fixed by RAG) | 1,810 |
| Baseline-only correct (broken by RAG) | 2,103 |
| Net change | −293 |

### Baseline vs. Full System (Ph6)

| Metric | Value |
|---|---|
| System-only correct | 1,977 |
| Baseline-only correct | 1,981 |
| Net change | −4 (p = 0.962) |

### RAG Basic vs. Full System (Ph6)

| Metric | Value |
|---|---|
| Recovered by Ph6 (broken by RAG, fixed by Ph6) | 1,479 |
| Introduced by Ph6 (correct in RAG, broken by Ph6) | 1,190 |
| Net change | +289 |

Anti-leak filtering (Phase 4) mitigated answer-anchoring artifacts from raw retrieval without improving retrieval quality itself.

---

## 4. Country-Level Results

### Table A: Countries Helped by RAG (Full System vs. Baseline)

| Country | Δ (pp) |
|---|---|
| Japan | +6.1 |
| Saudi Arabia | +4.5 |
| Ethiopia | +4.1 |
| North Korea | +4.0 |
| Morocco | +2.9 |
| Mexico | +1.9 |
| Ecuador | +1.5 |
| Singapore | +1.4 |
| Azerbaijan | +1.4 |
| Indonesia | +1.4 |
| West Java | +1.3 |
| China | +1.2 |
| Spain | +1.1 |
| Nigeria | +0.6 |

### Table B: Countries Hurt by RAG (Full System vs. Baseline)

| Country | Δ (pp) |
|---|---|
| American Samoa | −6.2 |
| Basque Country | −4.9 |
| Egypt | −4.1 |
| Great Britain | −3.0 |
| United States | −2.7 |
| Algeria | −2.5 |
| Bulgaria | −2.3 |
| Sweden | −2.0 |
| Philippines | −1.2 |
| Sri Lanka | −1.1 |
| South Korea | −0.6 |
| Ireland | −0.6 |
| Iran | −0.2 |
| Greece | −0.2 |

---

## 5. Oracle KB Coverage by Country

Global coverage: **40.7%** (19,148 / 47,014 questions).

| Country | Oracle Coverage (%) |
|---|---|
| Bulgaria | 69 |
| Ecuador | 68 |
| Ethiopia | 65 |
| Algeria | 26 |
| North Korea | 26 |
| Great Britain | 21 |

> The full per-country coverage table is available in the ablation analysis notebook.

**Retrieval ceiling gap:**
```
Δ_ceil = Acc_param − C̄ = 0.786 − 0.407 = +0.379 (37.9pp)
```

---

## 6. Answer Distribution Bias

| Option | Gold Distribution | Baseline Predicted | Phase 4 Predicted | Phase 6 Predicted |
|---|---|---|---|---|
| A | 24% | 32% | ~30% | ~30% |
| B | 26% | 25% | [TODO: add from notebook] | [TODO: add from notebook] |
| C | 26% | 22% | [TODO: add from notebook] | [TODO: add from notebook] |
| D | 24% | 21% | [TODO: add from notebook] | [TODO: add from notebook] |

The baseline over-predicts A (32% vs. 24% gold) and under-predicts C and D — a positional bias common in instruction-tuned LLMs. Phase 4 partially corrects this (A reduced to ~30%), though dedicated debiasing (answer shuffling or calibration) would be more effective.

---

## 7. Intent Detection Distribution

The keyword-based intent classifier assigned labels to 95.6% of questions (not "others"):

| Intent | Count | Percentage |
|---|---|---|
| food_drink | 3,133 | 46.6% |
| sports | 2,958 | 44.0% |
| others | 295 | 4.4% |
| education_knowledge_systems | 275 | 4.1% |
| geography_places | 38 | 0.6% |
| language_writing | 18 | 0.3% |

Despite broad coverage, intent labels had **zero downstream effect** on accuracy: Ph1 = Ph2 = 77.9%. The bottleneck was prompt-template design, not classification coverage.
