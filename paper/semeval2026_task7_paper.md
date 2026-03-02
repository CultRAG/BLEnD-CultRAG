# Trust-Weighted Cultural RAG with Anti-Leak Filtering for BLEnD Track 2

**Anonymous Submission — SemEval-2026 Task 7**

---

## Abstract

This paper describes a trust-weighted Retrieval-Augmented Generation (RAG) system for SemEval-2026 Task 7 (BLEnD) Track 2, targeting English multiple-choice questions on cultural knowledge across 30 countries. The system comprises a six-phase pipeline built atop Llama-3.1-8B-Instruct, integrating hybrid BM25+FAISS retrieval, country-aware filtering, intent detection, tiered routing, anti-leak prompt engineering, and trust-weighted reranking. Contrary to expectations, the core finding is that RAG *hurts* rather than helps on this task: the LLM-only baseline achieves 78.6% accuracy, outperforming the full RAG system at 78.5% (McNemar's test, *p* = 0.962). An oracle analysis reveals that only 40.7% of questions are answerable from the knowledge base, explaining why retrieval introduces more noise than signal. The sole component that recovers performance is anti-leak prompt filtering (Phase 4), which mitigates answer-anchoring artifacts. Country-level decomposition shows that RAG selectively benefits low-resource cultures (e.g., Ethiopia +4.1%) while degrading high-resource ones (e.g., Great Britain −3.0%), suggesting that selective, confidence-conditioned retrieval is necessary for cultural QA at scale.

---

## 1. Introduction

The BLEnD benchmark (Myung et al., 2024) evaluates large language models on culturally grounded knowledge across diverse world regions. Cultural knowledge — encompassing traditions, social norms, geography, cuisine, and local customs — poses a distinctive challenge for LLMs, whose training corpora are disproportionately Western-centric and English-dominant. Track 2 of SemEval-2026 Task 7 operationalizes this challenge as a four-option multiple-choice question-answering task spanning 47,014 questions across 30 country-language pairs, requiring models to demonstrate fine-grained cultural understanding that is unlikely to be captured by parametric knowledge alone.

Retrieval-Augmented Generation (RAG) is a natural mitigation strategy for this setting. By grounding LLM responses in an external knowledge base containing curated cultural information, one might expect retrieval to reduce hallucinations and fill gaps in the model's parametric knowledge — particularly for underrepresented cultures. This paper reports the design and evaluation of a six-phase trust-weighted RAG pipeline built on this hypothesis.

The central finding, however, is that this hypothesis is largely rejected. The LLM-only baseline (78.6% accuracy) matches or exceeds every RAG-augmented configuration, and the full six-phase system achieves 78.5% — a difference that is statistically indistinguishable from zero (*p* = 0.962). Oracle analysis reveals a fundamental ceiling: only 40.7% of test questions have their gold answer present anywhere in the knowledge base, meaning the LLM's parametric knowledge already surpasses the theoretical maximum contribution of retrieval. Anti-leak prompt filtering (Phase 4) is the only pipeline component that produces a meaningful accuracy recovery, suggesting that the primary failure mode of RAG on this task is not retrieval quality but answer-anchoring noise.

This paper makes four contributions: (1) a six-phase RAG pipeline with trust-weighted reranking and anti-leak filtering; (2) an oracle KB coverage analysis quantifying the theoretical retrieval ceiling; (3) a country-level decomposition revealing that RAG helps low-resource cultures but hurts high-resource ones; and (4) rigorous McNemar significance testing with effect size reporting for all ablation comparisons.

---

## 2. System Description

### 2.1 Knowledge Base Construction

The knowledge base comprises 1,262 text chunks organized into 7 shards, covering all 30 countries in the BLEnD Track 2 evaluation set. Chunks were sourced from Wikipedia articles on country-specific cultural topics (traditions, cuisine, history, social norms), supplemented by cultural web sources including travel guides, news outlets, and country-specific portals. Each chunk was assigned a trust tier: *high* (Wikipedia, government portals, and established reference works), *mid* (reputable travel and news outlets), and *low* (user-generated forums, blogs, and unverified sources). Trust tiers are used downstream for reranking retrieved documents.

An oracle coverage analysis was conducted to quantify the theoretical ceiling of retrieval. For each of the 47,014 test questions, the system checked whether the gold answer letter appeared in any retrieved KB chunk. This analysis found that only 19,148 questions (40.7%) have their gold answer present anywhere in the knowledge base. Coverage varies substantially by country: high-coverage countries include Bulgaria (69%), Ecuador (68%), and Ethiopia (65%), while low-coverage countries include Great Britain (21%), North Korea (26%), and Algeria (26%). This 40.7% ceiling is a critical architectural limitation — the LLM's parametric accuracy of 78.6% already far exceeds the maximum possible contribution of KB-grounded retrieval.

### 2.2 Entity Extraction

Entity extraction is performed using spaCy's named entity recognition pipeline applied to each question text. The system extracts an average of 1.5 entities per question, including person names, locations, organizations, and cultural artifacts. Extracted entities are appended to the original question text to form expanded retrieval queries, increasing the likelihood of matching relevant KB chunks that mention the same entities in different surface forms.

### 2.3 Hybrid Retrieval

The retrieval stage employs a hybrid strategy combining lexical and semantic matching. BM25 provides sparse lexical retrieval, capturing exact keyword matches between expanded queries and KB chunks. FAISS (Facebook AI Similarity Search) provides dense semantic retrieval using embedding-based similarity, capturing paraphrastic and conceptually related matches. Results from both retrievers are fused using Reciprocal Rank Fusion (RRF), and the top *k* = 3 documents are selected per question. Country filtering restricts the retrieval pool to KB chunks associated with the country code extracted from the question ID prefix (e.g., `ja-JP_0042` maps to Japan), ensuring that retrieved context is geographically relevant. This filtering eliminates cross-country contamination, where a question about Japanese customs might otherwise retrieve chunks about Chinese or Korean traditions.

### 2.4 Intent Detection

A keyword-based heuristic intent classifier categorizes each question into intent types (e.g., factual, opinion, tradition, food, geography) to enable intent-aware prompt construction and tiered routing. However, a known limitation of this component is that the classifier did not activate on the test set: 0 out of 47,014 questions received a non-"others" classification. This is attributed to the heuristic keyword patterns being too narrow to match the BLEnD question distribution. The intent classifier is effectively a no-op in the reported results, and this failure propagates to downstream components (Phases 2 and 3) that depend on intent labels.

### 2.5 Phased Prompt Engineering

The system employs six cumulative phases of prompt engineering, each adding a distinct capability:

**Phase 1 (Country Filter)** restricts the retrieved KB chunks to the target country, preventing noise from geographically irrelevant documents. In principle, this should improve precision; in practice, it produces identical results to unfiltered RAG because BM25+FAISS already favors country-relevant chunks when entity-expanded queries contain country-specific terms.

**Phase 2 (Intent Detection)** injects intent metadata into the prompt, instructing the model to weight its reasoning toward the detected question category. Because the intent classifier assigns "others" universally (Section 2.4), this phase produces no change in predictions.

**Phase 3 (Tiered Routing)** routes questions to different prompt templates based on intent category. High-confidence intents receive context-heavy prompts, while low-confidence intents receive knowledge-light prompts. With all questions classified as "others," tiered routing defaults to the most conservative template, which narrows the context window and reduces accuracy to 77.6% — the worst configuration in the ablation.

**Phase 4 (Anti-Leak Quality Filtering)** is the most impactful component. It applies prompt-level instructions directing the model not to be anchored by artifacts in the retrieved context — specifically, to avoid treating passage structure, formatting cues, or answer-letter mentions in KB text as evidence for a particular answer choice. This anti-leak filtering recovers 1.0 percentage points over Phase 3, bringing accuracy back to 78.5%. The mechanism is prompt engineering rather than retrieval modification: the same documents are retrieved, but the model is explicitly instructed to reason independently of surface-level context cues.

**Phase 5 (Trust-Weighted Reranking)** reorders retrieved documents by trust tier before insertion into the prompt, placing high-trust sources (Wikipedia) first and low-trust sources last. The hypothesis is that the model will attend more to earlier context. In practice, Phase 5 produces identical predictions to Phase 4, suggesting that document order has negligible impact at *k* = 3.

**Phase 6 (Full System)** combines all preceding phases. Its predictions are identical to those of Phases 4 and 5 (36,928 correct out of 47,014), confirming that anti-leak filtering is the only component contributing marginal value beyond the baseline RAG configuration.

---

## 3. Experiments

### 3.1 Setup

The evaluation dataset is BLEnD Track 2, comprising 47,014 English multiple-choice questions with four answer options (A, B, C, D) spanning 30 country-language pairs. The gold answer distribution is approximately uniform: A = 24%, B = 26%, C = 26%, D = 24%. All experiments use Llama-3.1-8B-Instruct as the base language model, executed on Kaggle GPU infrastructure. Constrained decoding restricts model output to a single token from the set {A, B, C, D}, ensuring that every question receives a valid prediction. The primary evaluation metric is accuracy (percentage of questions answered correctly). Statistical significance is assessed using McNemar's test for paired binary outcomes, and effect magnitude is quantified using Cohen's *h* for proportions.

### 3.15 Resource Constraints and Engineering Responses

All experiments were conducted on Kaggle free-tier infrastructure (2× NVIDIA T4, 16 GB VRAM each, 12-hour session limit), deliberately avoiding proprietary APIs or paid compute. This constraint serves a reproducibility function: all results are fully replicable by any researcher with a free Kaggle account.

Three engineering decisions were required. Memory: Llama-3.1-8B-Instruct in fp16 occupies ~16 GB, saturating a single T4. We distribute across both GPUs via LMDeploy's TurboMind engine with tensor parallelism (tp=2) and cap KV-cache allocation at 40% of VRAM (cache_max_entry_count=0.4), reserving headroom for retrieval buffers. This sustains batch size 64 without OOM errors. Latency: Wikipedia API calls use aiohttp concurrent pools with title batching, per-domain rate limiting, and exponential-backoff retry, reducing KB construction time to fit within the session limit. Interruption robustness: Predictions are checkpointed per batch of 64; a three-tier cache hierarchy (persistent Kaggle Dataset mount → session pickle → working directory) prevents re-execution of completed stages. Pre-submission interlocks assert exact row count (47,014), no duplicate IDs, and complete locale coverage across all 30 country-language pairs.

Inference used LMDeploy's batched pipeline to process the full 47,014-question evaluation set in a single session — a deliberate choice, as full-scale evaluation enables McNemar's test to detect differences as small as 293 questions (0.6 pp) at p < 0.0001, and ensures country-level subgroup analyses retain statistical power across all 30 locales.


### 3.2 Main Results

Table 1 presents the ablation results across all eight configurations.

**Table 1: Ablation study results.** Each row adds one component to the previous configuration. Δ Baseline is the accuracy change relative to the LLM-only baseline. CI denotes the Wilson 95% confidence interval.

| Configuration            | Correct | Acc (%) | 95% CI        | Δ Baseline |
|--------------------------|---------|---------|---------------|------------|
| Baseline (LLM only)      | 36,932  | 78.6    | [78.2, 78.9]  | —          |
| RAG Basic (unfiltered)   | 36,639  | 77.9    | [77.6, 78.3]  | −0.6       |
| + Country Filter (Ph1)   | 36,639  | 77.9    | [77.6, 78.3]  | −0.6       |
| + Intent Detection (Ph2) | 36,639  | 77.9    | [77.6, 78.3]  | −0.6       |
| + Tiered Routing (Ph3)   | 36,465  | 77.6    | [77.2, 77.9]  | −1.0       |
| + Quality Signals (Ph4)  | 36,928  | 78.5    | [78.2, 78.9]  | −0.0       |
| + Trust Reranking (Ph5)  | 36,928  | 78.5    | [78.2, 78.9]  | −0.0       |
| Full System (Ph6)        | 36,928  | 78.5    | [78.2, 78.9]  | −0.0       |

Several observations emerge from the ablation. First, the LLM-only baseline (78.6%) achieves the highest or near-highest accuracy of any configuration, establishing that parametric knowledge alone is a strong starting point. Second, introducing unfiltered RAG immediately degrades accuracy by 0.6 percentage points to 77.9%, a statistically significant drop (*p* < 0.0001). Third, adding country filtering (Phase 1) and intent detection (Phase 2) produces no change in predictions relative to unfiltered RAG — both remain at 77.9% with 36,639 correct. The intent detection failure (Section 2.4) explains this: with all questions classified as "others," Phases 1 and 2 effectively reduce to the RAG Basic configuration. Fourth, tiered routing (Phase 3) *further* worsens accuracy to 77.6%, the lowest point in the ablation, because routing all questions through the conservative "others" template narrows the effective context window without improving retrieval quality. Fifth, anti-leak quality filtering (Phase 4) is the sole component that recovers performance, producing a 1.0 percentage point gain over Phase 3 and restoring accuracy to 78.5%. Sixth, trust-weighted reranking (Phase 5) and the full combined system (Phase 6) add nothing beyond Phase 4, producing identical predictions (36,928 correct). The full system versus baseline comparison yields a difference of −0.0 percentage points that is not statistically significant (*p* = 0.962).

### 3.3 Statistical Significance

Table 2 presents McNemar's test results for key pairwise comparisons.

**Table 2: McNemar's paired significance tests.** Cohen's *h* quantifies effect size magnitude.

| Comparison                | Δ Acc (pp) | *p*-value | Significant | Cohen's *h* | Effect |
|---------------------------|------------|-----------|-------------|-------------|--------|
| Baseline vs. RAG Basic    | −0.6       | < 0.0001  | Yes         | 0.015       | Small  |
| Baseline vs. Full System  | −0.0       | 0.962     | No          | 0.000       | Small  |
| RAG Basic vs. Full System | +0.6       | < 0.0001  | Yes         | 0.015       | Small  |

The comparison between Baseline and RAG Basic is statistically significant (*p* < 0.0001), confirming that the RAG-induced accuracy drop of 0.6 percentage points is real and not attributable to sampling noise. Similarly, the comparison between RAG Basic and the Full System is significant (*p* < 0.0001), confirming that anti-leak filtering genuinely recovers the lost performance. However, all Cohen's *h* values are at most 0.015, indicating that while the differences are statistically detectable given *N* = 47,014, they are practically small. The comparison between Baseline and Full System is not significant (*p* = 0.962, Cohen's *h* = 0.000), meaning the entire six-phase RAG pipeline produces an outcome statistically indistinguishable from doing nothing.

---

## 4. Analysis

### 4.1 Why RAG Hurts: Knowledge Base Coverage Ceiling

The oracle coverage analysis provides a direct explanation for why retrieval degrades accuracy. Of the 47,014 test questions, only 19,148 (40.7%) have their gold answer present anywhere in the 1,262-chunk knowledge base. The LLM's parametric accuracy of 78.6% already far exceeds this theoretical ceiling, meaning that for the majority of questions (59.3%), retrieval can only introduce irrelevant or misleading context. The per-country coverage figures sharpen this picture: Great Britain has only 21% KB coverage, yet the baseline achieves 92.4% accuracy on GB questions — retrieval can contribute nothing for the remaining 79% of GB questions, while the noise it introduces costs 3.0 percentage points (89.7% under the full system). Conversely, Ethiopia has 65% KB coverage and a lower baseline of 59.0%, leaving genuine room for retrieval to fill parametric gaps; indeed, the full system reaches 63.0% on ET questions, a gain of 4.1 percentage points. The fundamental architectural implication is that a retrieval system cannot be justified when its coverage ceiling lies below the model's existing parametric performance.

### 4.2 RAG Backfire Decomposition

A quadrant analysis of per-question outcomes reveals the mechanics of RAG failure. Comparing Baseline with RAG Basic, retrieval fixes 1,810 questions that the baseline answered incorrectly but simultaneously breaks 2,103 questions that the baseline answered correctly, yielding a net loss of 293 questions. The full system (Phase 6) partially mitigates this: it fixes 1,977 baseline-incorrect questions and hurts 1,981 baseline-correct ones, a net difference of just −4 questions (*p* = 0.962). Critically, when comparing RAG Basic with the full system directly, Phase 6 recovers 1,479 of the questions that raw retrieval had broken while introducing only 1,190 new errors — a net gain of +289 questions. This decomposition confirms that anti-leak filtering (Phase 4) is performing its intended function: it does not improve retrieval quality but rather prevents the model from being anchored by misleading context artifacts, recovering most of the damage caused by raw retrieval.

### 4.3 Country-Level Analysis

Country-level accuracy decomposition reveals a systematic pattern in which countries are helped versus hurt by the RAG pipeline. Fourteen countries show improvement under the full system relative to baseline, with the largest gains observed for Japan (+6.1 pp), Saudi Arabia (+4.5 pp), Ethiopia (+4.1 pp), and North Korea (+4.0 pp). These are predominantly countries whose cultural knowledge is underrepresented in standard English-language pretraining corpora, where the curated KB fills genuine parametric gaps. Morocco (+2.9 pp), Mexico (+1.9 pp), Ecuador (+1.5 pp), Singapore (+1.4 pp), Azerbaijan (+1.4 pp), Indonesia (+1.4 pp), West Java (+1.3 pp), China (+1.2 pp), Spain (+1.1 pp), and Nigeria (+0.6 pp) also benefit, though to a lesser degree.

Conversely, fourteen countries show degradation, with the most severe losses for American Samoa (−6.2 pp), the Basque Country (−4.9 pp), Egypt (−4.1 pp), Great Britain (−3.0 pp), the United States (−2.7 pp), Algeria (−2.5 pp), and Bulgaria (−2.3 pp). These are either high-resource English-speaking countries (GB, US) where the LLM already has strong parametric coverage and retrieval adds only noise, or countries with sparse, low-quality KB entries (Basque Country, American Samoa) where the retrieved context is actively misleading. Sweden (−2.0 pp), the Philippines (−1.2 pp), Sri Lanka (−1.1 pp), South Korea (−0.6 pp), Ireland (−0.6 pp), Iran (−0.2 pp), and Greece (−0.2 pp) also experience smaller losses. The practical implication is clear: RAG should be applied selectively, conditioned on either LLM confidence or country-level KB coverage, rather than uniformly across all questions.

### 4.4 Answer Distribution Bias

An analysis of predicted answer distributions reveals a systematic bias in the baseline model. The gold answer distribution is approximately uniform (A = 24%, B = 26%, C = 26%, D = 24%), but the Llama-3.1-8B-Instruct baseline over-predicts A (32%) and under-predicts C (22%) and D (21%). This positional bias — a known artifact of instruction-tuned LLMs preferring the first option — accounts for a nontrivial fraction of baseline errors. The anti-leak quality filtering in Phase 4 partially corrects this bias, reducing A predictions to approximately 30%, though the distribution remains non-uniform. Trust-aware prompting contributes modestly to this correction by reducing the model's reliance on surface-level cues, though a dedicated debiasing mechanism (e.g., answer shuffling or calibration) would likely be more effective.

### 4.5 Limitation: Intent Detection Failure

The intent detection module represents a significant architectural failure. The keyword-based heuristic classifier assigned the label "others" to all 47,014 questions, meaning that Phases 2 (intent injection) and 3 (tiered routing) operated as if no intent information were available. This explains the invariance of predictions across Phases 1, 2, and RAG Basic (all at 77.9%), and the *degradation* at Phase 3 (77.6%), where the conservative "others" routing template narrows the context window unnecessarily. A properly functioning intent classifier — whether fine-tuned on BLEnD-style questions or implemented via zero-shot LLM-based classification — would likely differentiate these phases. Future work should replace the keyword heuristic with a learned classifier to realize the intended benefits of intent-aware routing and prompt specialization.

---

## 5. Conclusion

This paper presented a six-phase trust-weighted RAG pipeline for SemEval-2026 Task 7 (BLEnD) Track 2, targeting English cultural MCQ across 30 countries with Llama-3.1-8B-Instruct. The system integrates hybrid BM25+FAISS retrieval, country filtering, intent detection, tiered routing, anti-leak prompt filtering, and trust-weighted reranking. The central finding is that RAG does not help on this task: the LLM-only baseline achieves 78.6% accuracy, while the full system achieves 78.5%, a difference that is not statistically significant (*p* = 0.962). Oracle KB analysis identifies the root cause — only 40.7% of questions are answerable from the knowledge base, well below the LLM's parametric performance ceiling. Anti-leak prompt filtering (Phase 4) is the only component that produces a meaningful recovery, gaining 1.0 percentage point over raw RAG by mitigating answer-anchoring artifacts.

Country-level analysis reveals a systematic split: RAG benefits low-resource cultures with higher KB coverage (Japan +6.1 pp, Ethiopia +4.1 pp, Saudi Arabia +4.5 pp) while hurting high-resource cultures where parametric knowledge already dominates (American Samoa −6.2 pp, Great Britain −3.0 pp, United States −2.7 pp). This finding motivates four directions for future work: (1) confidence-conditioned selective RAG that retrieves only when the LLM is uncertain; (2) targeted KB expansion for countries with sparse coverage; (3) replacing the failed keyword-based intent classifier with a fine-tuned or zero-shot alternative; and (4) cross-encoder reranking to improve retrieval precision and reduce noise injection.

---

## References

[TODO: Add references for BLEnD benchmark, Llama-3.1, BM25, FAISS, RRF, McNemar's test, Cohen's h, spaCy, RAG literature]
