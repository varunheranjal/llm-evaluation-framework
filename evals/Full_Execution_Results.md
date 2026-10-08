# Full RAG Evaluation — Execution Results

> **Portfolio demonstration | Historical evaluation snapshot**  
> This report documents a **real 38-case execution** of the internal-company RAG proof of concept, using the original **standard retrieval (Top-K = 2), before the optional broad-search experiment**. The knowledge-base content is synthetic; the expected answers were manually curated against it. These are the observed results of this run, **not a claim that all tests passed or a new run of the updated code**.

## Run configuration

```bash
EVAL_TIER=full python -m evals.run_eval
```

| Property | Value |
|---|---|
| Evaluation tier | `full` |
| Golden cases | **38** |
| Answerable cases | **33** |
| Negative / missing-information cases | **5** |
| RAG approach | LangChain agent + ChromaDB knowledge retrieval |
| Standard retrieval setting | Top-K = **2** (no broad-search tool in this snapshot) |
| LLM-as-a-judge | `gpt-4.1` |
| Metric threshold | **0.70** |
| Measured evaluation time | **200.08 s** (approximately **3 min 20 s**) |
| Reported evaluation/judge token cost | **$0.609782** (approximately **$0.61**) |

*The token cost is the sum of the three DeepEval evaluation-section costs. It should not be interpreted as the full end-to-end cost of generating the RAG responses and embedding queries.*

## At a glance

| Evaluation stage | Result | Interpretation |
|---|---|---|
| **Retriever: Contextual Recall** | **32/33 passed** · avg **0.97** | Retrieved evidence usually covered the expected answer |
| **Retriever: Contextual Precision** | **32/33 passed** · avg **0.97** | Relevant evidence was generally ranked well |
| **Retriever: Contextual Relevancy** | **5/33 passed** · avg **0.38** | **Known weakness:** retrieved chunks often contained unnecessary text |
| **Generator: Answer Correctness** | **32/33 passed** · avg **0.97** | One substantive incomplete-answer failure |
| **Generator: Groundedness** | **33/33 passed** · avg **1.00** | Answers were supported by the retrieved context |
| **Generator: Answer Relevancy** | **33/33 passed** · avg **1.00** | Answers stayed on topic |
| **Negative: Unknown / Refusal Correctness** | **5/5 passed** · avg **0.97** | Correct handling of unavailable/out-of-domain questions |
| **Negative: Answer Relevancy** | **5/5 passed** · avg **0.95** | Refusals were appropriate to their questions |

**How to read the results:** The full retriever stage reports **5/33 cases passing all three retrieval metrics**, because Contextual Relevancy is included in that stage's pass/fail determination. That is **not** the same as the answer-correctness pass rate. The independent generator stage reports **32/33 cases passing all three generator metrics**; negative cases are evaluated separately.

## Detailed metric breakdown

### 1. Retrieval quality — 33 answerable cases

| Metric | Average | Pass | Fail | Pass rate | Threshold |
|---|---:|---:|---:|---:|---:|
| Contextual Relevancy | 0.38 | 5 | 28 | 15.15% | 0.70 |
| Contextual Recall | 0.97 | 32 | 1 | 96.97% | 0.70 |
| Contextual Precision | 0.97 | 32 | 1 | 96.97% | 0.70 |

**Stage result:** 5 passed / 28 failed (15.15% case pass rate).  
**Judge time:** 123.29 s · **Reported token cost:** $0.448612.

Contextual Relevancy is retained here as an **important diagnostic signal**. A low score means the retrieved text did not focus tightly enough on the question; it does not, by itself, prove the final answer is wrong.

### 2. Answer generation — 33 answerable cases

| Metric | Average | Pass | Fail | Pass rate | Threshold |
|---|---:|---:|---:|---:|---:|
| Answer Correctness (GEval) | 0.97 | 32 | 1 | 96.97% | 0.70 |
| Groundedness (GEval) | 1.00 | 33 | 0 | 100% | 0.70 |
| Answer Relevancy (GEval) | 1.00 | 33 | 0 | 100% | 0.70 |

**Stage result:** 32 passed / 1 failed (96.97% case pass rate).  
**Judge time:** 68.01 s · **Reported token cost:** $0.149642.

### 3. Negative / missing-information behaviour — 5 cases

| Metric | Average | Pass | Fail | Pass rate | Threshold |
|---|---:|---:|---:|---:|---:|
| Unknown / Refusal Correctness (GEval) | 0.97 | 5 | 0 | 100% | 0.70 |
| Answer Relevancy (GEval) | 0.95 | 5 | 0 | 100% | 0.70 |

**Stage result:** 5 passed / 0 failed (100% case pass rate).  
**Judge time:** 8.78 s · **Reported token cost:** $0.011528.

## All 38 golden questions

The table below is a question-level index of the execution. **Generator = PASS** means all three answer-generation metrics passed; **Negative = PASS** means both negative-case metrics passed. Retriever metrics are assessed independently and summarised above. A generator PASS does **not** imply all retrieval diagnostics passed.

| # | Golden question | Answer evaluation |
|---:|---|---|
| 1 | Who is working on the GraphRAG project and what is their allocation? | **Generator: PASS** |
| 2 | What is the status and actual cost of the GraphRAG project? | **Generator: PASS** |
| 3 | How many days is the GraphRAG Platform project delayed? | **Generator: PASS** |
| 4 | Who is assigned to the Factory AI Insights project and what is their allocation? | **Generator: PASS** |
| 5 | What is the actual cost and delay for the Factory AI Insights project? | **Generator: PASS** |
| 6 | Who is working on the Retail Recommendation Engine and what is their allocation? | **Generator: PASS** |
| 7 | Who worked on the Snowflake Platform project and what skill did they provide? | **Generator: PASS** |
| 8 | Did the Azure Modernization project finish under or over budget, and by how much? | **Generator: PASS** |
| 9 | Who handled the GraphRAG Platform sales opportunity and what was the deal value? | **Generator: PASS** |
| 10 | Which client had the AWS Data Lake opportunity, what was it worth, and why was it lost? | **Generator: PASS** |
| 11 | Why was HealthFirst's AWS Migration opportunity lost and what was its value? | **Generator: PASS** |
| 12 | What was the value and outcome of FinTrust's Azure Modernization opportunity? | **Generator: PASS** |
| 13 | Who was the sales representative for GlobalBank's Snowflake Platform opportunity? | **Generator: PASS** |
| 14 | What service and deal value were associated with RetailMax's Databricks Analytics opportunity? | **Generator: PASS** |
| 15 | What happened to the Healthcare AI Assistant opportunity and why? | **Generator: PASS** |
| 16 | What was the value of MedCore's Cloud Transformation opportunity and why was it lost? | **Generator: PASS** |
| 17 | What was BFSI revenue in Q2 2025? | **Generator: PASS** |
| 18 | What was Healthcare revenue in Q1 2025? | **Generator: PASS** |
| 19 | What was Retail revenue in Q2 2025? | **Generator: PASS** |
| 20 | What was total revenue across all industries in Q1 2025? | **Generator: PASS** |
| 21 | What was total revenue across all industries in Q2 2025? | **Generator: PASS** |
| 22 | Which industry had the highest revenue in Q2 2025, and how much was it? | **Generator: PASS** |
| 23 | Which industry had the largest revenue drop from Q1 to Q2 2025, and by how much? | **Generator: PASS** |
| 24 | Which industries had the largest revenue increase from Q1 to Q2 2025? | **Generator: PASS** |
| 25 | Was the GraphRAG Platform opportunity won, and what is the current status of the corresponding project? | **Generator: PASS** |
| 26 | What happened to FinTrust's Azure Modernization opportunity, and what is the status of the resulting project? | **Generator: PASS** |
| 27 | Was the Factory AI Insights opportunity won, and how is the corresponding project performing? | **Generator: PASS** |
| 28 | What was the outcome of the Retail Recommendation Engine opportunity, and what is the status of its project? | **Generator: PASS** |
| 29 | Between GraphRAG Platform and Factory AI Insights, which project has the larger cost overrun and the longer delay? | **Generator: PASS** |
| 30 | Which completed projects finished under budget? | **Generator: FAIL** |
| 31 | What industry and region is TechNova in? | **Generator: PASS** |
| 32 | What industry and region is MedCore in? | **Generator: PASS** |
| 33 | Which sales representative covers APAC? | **Generator: PASS** |
| 34 | What is the planned completion date for the GraphRAG Platform project? | **Negative: PASS** |
| 35 | Who is the CEO of TechNova? | **Negative: PASS** |
| 36 | What was BFSI revenue in Q3 2025? | **Negative: PASS** |
| 37 | What is the capital of France? | **Negative: PASS** |
| 38 | What is the weather in London today? | **Negative: PASS** |

## Failure investigation — useful examples

### A. Incomplete answer despite perfect groundedness (case 30)

**Question:** Which completed projects finished under budget?

**Expected:** Azure Modernization, Snowflake Platform, Databricks Analytics, **and** Retail Recommendation Engine.

**Actual (this historical run):** Azure Modernization and Snowflake Platform only.

| Metric | Score | Outcome |
|---|---:|---|
| Contextual Recall | **0.00** | FAIL |
| Contextual Precision | 1.00 | PASS |
| Contextual Relevancy | 0.67 | FAIL |
| Answer Correctness | **0.54** | FAIL |
| Groundedness | 1.00 | PASS |
| Answer Relevancy | 1.00 | PASS |

**What this reveals:** The model accurately described what it retrieved, but the retrieval missed records required for a *complete* answer. **Groundedness ≠ completeness.** This is the principal functional issue discovered by the full run. It was investigated separately later; **this file deliberately preserves the original failing execution** rather than replacing its result with a later experiment.

### B. Correct answer, imperfect retrieval precision (case 31)

**Question:** What industry and region is TechNova in?

**Expected and actual:** Technology industry; North America region.

| Metric | Score | Outcome |
|---|---:|---|
| Contextual Recall | 1.00 | PASS |
| Contextual Precision | **0.50** | FAIL |
| Contextual Relevancy | 0.33 | FAIL |
| Generator metrics | All passed | PASS |

This illustrates why retrieval quality and answer quality are evaluated separately: a correct response can still be based on less-than-ideal context ranking.

### C. Proper handling when data does not exist (negative examples)

Five cases deliberately probe missing internal information or questions outside the knowledge base. Examples include asking for **TechNova's CEO**, **BFSI revenue in Q3 2025**, **the capital of France**, and **today's London weather**. The negative evaluation passed **5/5** cases, demonstrating that the assistant did not need to invent answers when the knowledge base was insufficient or the question was outside its permitted domain.

## Findings and limitations

1. **Useful separation of concerns.** Retrieval Recall, Precision and Relevancy are measured independently of Answer Correctness, Groundedness and Answer Relevancy.
2. **A real defect was exposed.** The under-budget question returned only two of four required projects; the answer was grounded but incomplete.
3. **Contextual Relevancy needs improvement.** The observed average was 0.38; the run does not justify a claim of strong context efficiency.
4. **These are model-judged, run-specific results.** Scores may change with retrieval, agent decisions and judge variability. They are not guarantees of future application behaviour.
5. **Synthetic proof-of-concept scope.** This is an evaluation demonstration against a small fictional business knowledge base, not evidence of production-domain accuracy.

## Original terminal evidence

For transparency, the original, unedited console output is kept alongside this report:

**[View the original full execution log](./Full_Execution_Raw_Log.txt)**

That file contains the question execution sequence, individual failed-case details, DeepEval summaries and timing/cost lines. This Markdown report reformats the results for GitHub viewing; it does **not** rerun or alter them.
