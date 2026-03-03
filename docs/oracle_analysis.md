# Oracle Coverage Analysis

This is the most important diagnostic in the project. Oracle coverage explains *why* RAG did not improve accuracy and provides the decision criterion for whether RAG should be deployed.

---

## Definition

For a question $q_i$ with gold answer $g_i$ and a knowledge base $\text{KB}(q_i)$ (the set of all chunks matching $q_i$'s country), define:

$$\text{Cov}(q_i) = \mathbb{1}\bigl[\exists\, d \in \text{KB}(q_i) : g_i \in d\bigr]$$

$\text{Cov}(q_i) = 1$ if any chunk in the country-filtered KB contains the gold answer text; 0 otherwise.

The **global oracle coverage** is the mean over all questions:

$$\bar{C} = \frac{1}{N} \sum_{i=1}^{N} \text{Cov}(q_i)$$

---

## Retrieval Viability Condition

RAG can only help on questions where $\text{Cov}(q_i) = 1$. For the remaining questions, every retrieved passage is either irrelevant or misleading.

A necessary (not sufficient) condition for RAG to be net-positive:

$$\bar{C} > \text{Acc}_{\text{parametric}}$$

If the KB cannot even *contain* the answer for more questions than the model already answers correctly, retrieval will inject more noise than signal.

---

## Computation Method

Oracle coverage was computed by exact string matching of the gold answer option text against all country-filtered KB chunks:

```python
def compute_oracle_coverage(questions, kb_chunks):
    hits = 0
    for q in questions:
        country_chunks = [c for c in kb_chunks if c["country"] == q.country]
        gold_text = q.options[q.gold_label]  # e.g., the text of option "B"
        if any(gold_text.lower() in chunk["text"].lower() for chunk in country_chunks):
            hits += 1
    return hits / len(questions)
```

This is a *lower bound* on true coverage: it requires exact substring match, missing paraphrases and partial evidence. The true retrieval ceiling may be somewhat higher.

---

## Global Result

$$\bar{C} = \frac{19{,}148}{47{,}014} = 0.407 \quad (40.7\%)$$

Compared to the parametric baseline accuracy:

$$\text{Acc}_{\text{param}} = \frac{36{,}932}{47{,}014} = 0.786 \quad (78.6\%)$$

The **retrieval ceiling gap**:

$$\Delta_{\text{ceil}} = \text{Acc}_{\text{param}} - \bar{C} = 0.786 - 0.407 = +0.379 \quad (+37.9\text{pp})$$

The model already answers 37.9 percentage points more questions than the KB can even cover. Under these conditions, RAG cannot be net-positive.

---

## Country-Level Breakdown

Oracle coverage varies dramatically by country. Countries with rich English-language cultural documentation have higher coverage.

### High Coverage (≥ 60%)

| Country | Coverage (%) | RAG Δ (pp) |
|---|---|---|
| Bulgaria | 69 | −2.3 |
| Ecuador | 68 | +1.5 |
| Ethiopia | 65 | +4.1 |

### Low Coverage (≤ 30%)

| Country | Coverage (%) | RAG Δ (pp) |
|---|---|---|
| Algeria | 26 | −2.5 |
| North Korea | 26 | +4.0 |
| Great Britain | 21 | −3.0 |

**Key contrast:** Great Britain has 21% coverage (the lowest), yet the model's parametric knowledge of British culture is likely among the highest — exactly the scenario where RAG adds noise. Ethiopia has 65% coverage and gains +4.1pp — showing that RAG helps most where the KB can cover questions the model cannot.

---

## Ceiling Gap by Country

For each country, the ceiling gap determines whether RAG *could* help:

$$\Delta_{\text{ceil}}^{(c)} = \text{Acc}_{\text{param}}^{(c)} - \bar{C}^{(c)}$$

- If $\Delta_{\text{ceil}}^{(c)} > 0$: The model already outperforms what perfect retrieval could contribute. RAG is likely to hurt.
- If $\Delta_{\text{ceil}}^{(c)} < 0$: The KB covers more than the model knows. RAG has room to help.
- If $\Delta_{\text{ceil}}^{(c)} \approx 0$: Marginal case; quality of retrieval noise matters.

For most countries in BLEnD, $\Delta_{\text{ceil}}^{(c)} > 0$, explaining the globally flat or negative RAG contribution.

---

## Practitioner Decision Rule

Before deploying RAG on any cultural QA task, compute:

1. **Parametric accuracy** $\text{Acc}_{\text{param}}$ — run the LLM without retrieval.
2. **Oracle coverage** $\bar{C}$ — check what fraction of questions the KB can cover.
3. **Ceiling gap** $\Delta_{\text{ceil}} = \text{Acc}_{\text{param}} - \bar{C}$.

| Condition | Recommendation |
|---|---|
| $\Delta_{\text{ceil}} < -10\text{pp}$ | RAG is strongly indicated. KB covers much more than the model knows. |
| $-10\text{pp} \leq \Delta_{\text{ceil}} \leq 0$ | RAG may help. Depends on retrieval precision and noise filtering. |
| $\Delta_{\text{ceil}} > 0$ | Do **not** deploy RAG. Expand the KB first. |

In our case, $\Delta_{\text{ceil}} = +37.9\text{pp}$. RAG should not have been expected to help. The correct intervention is KB expansion.

---

## Metric Limitations

1. **Exact match underestimates coverage.** A passage might contain evidence sufficient to infer the answer without containing the exact answer string. True coverage is higher than 40.7%.
2. **Coverage ≠ retrievability.** Even if the answer exists in the KB, the retrieval pipeline may fail to surface it. Oracle coverage is an upper bound on what retrieval can achieve.
3. **No distinction between easy and hard questions.** A question the model always gets right doesn't need KB coverage; a question it always gets wrong desperately does. A coverage metric conditioned on model errors would be more informative.
4. **Single gold answer.** Some MCQ options are culturally contested. The oracle check assumes a single gold label.

---

## Recommended Extensions

1. **Error-conditioned coverage:** Compute $\bar{C}$ only over questions the parametric model gets wrong. If this is high, RAG has more potential than global $\bar{C}$ suggests.
2. **Fuzzy matching:** Replace exact match with semantic similarity (e.g., embedding distance < threshold) to capture paraphrased evidence.
3. **Per-intent coverage:** Compute $\bar{C}$ per intent category to identify which cultural domains benefit most from retrieval.
4. **Retrieval precision analysis:** For questions where $\text{Cov}(q_i) = 1$, check whether the pipeline actually retrieves the right passage at rank ≤ 3.
