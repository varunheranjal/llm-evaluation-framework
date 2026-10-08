# RAG Evaluation Framework

A Python-based framework for evaluating a Retrieval-Augmented Generation (RAG) application using **DeepEval, PyTest and LLM-as-a-Judge**.

The project uses a sample business knowledge base containing projects, sales opportunities, resource allocations and revenue data. It focuses on testing two areas:

- **Retrieval quality:** Does the application retrieve the information needed to answer a question?
- **Response quality:** Is the generated answer correct, relevant and supported by the retrieved documents?

The business records are synthetic, while the golden test cases and expected answers are manually curated against those records.

## 1. Architecture and Workflow

```text
Sample Business Data (CSV)
          |
          v
Generate Knowledge Documents (Markdown/PDF)
          |
          v
Load and Chunk Documents
          |
          v
OpenAI Embeddings → ChromaDB
          |
          v
User Question → RAG Agent
                    |
                    v
             Knowledge Retrieval
                    |
                    v
             Generated Answer
                    |
                    v
       DeepEval + Golden Dataset
                    |
                    v
         Metric Scores / Pass-Fail
```

**Application flow:** The RAG agent uses a knowledge-base search tool to retrieve relevant ChromaDB chunks and generate a response.

**Evaluation flow:** The framework captures the question, actual response and retrieved context, compares them against a trusted golden test case, and evaluates the result using GPT-4.1.

## 2. Project Structure

```text
src/
  app.py                 # Streamlit chatbot
  agents.py              # RAG agent and tool execution
  tools.py               # Knowledge-base retrieval
  pipeline.py            # Document ingestion
  loaders.py             # Document loading
  chunking.py            # Text chunking
  vectorstore.py         # ChromaDB and embeddings
  config.py              # Environment configuration

scripts/
  generate_knowledge_docs.py

evals/
  data/
    golden_dataset.json  # Manually curated test cases
  run_eval.py             # Detailed DeepEval evaluation

tests/
  test_rag.py             # Automated PyTest quality checks

source_data/              # Sample business CSV files
requirements.txt
.env                      # Local configuration (not committed)
```

## 3. Getting Started

### Step 1 — Clone the repository

```bash
git clone https://github.com/varunheranjal/llm-evaluation-framework.git
cd llm-evaluation-framework
```

### Step 2 — Set up Python

Python 3.11 is recommended.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 3 — Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key

OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

CHUNK_SIZE=1200
CHUNK_OVERLAP=150
RETRIEVAL_TOP_K=2

DEEPEVAL_MODEL=gpt-4.1
EVAL_TIER=smoke
EVAL_THRESHOLD=0.7
EVAL_MAX_CONCURRENT=1
```

The API key is required for embeddings, chatbot responses and LLM-based evaluations.

Do not commit `.env` to Git.

### Step 4 — Generate the knowledge documents

The `source_data/` directory contains sample business records in CSV format.

Generate the knowledge documents:

```bash
python scripts/generate_knowledge_docs.py
```

This converts the sample business data into documents that can be searched by the RAG application.

These documents provide the information against which the golden test cases have been defined.

### Step 5 — Ingest documents into ChromaDB

```bash
python -m src.pipeline
```

This runs the ingestion pipeline:

1. Loads knowledge documents from the configured dataset directory.
2. Splits document text into chunks using `CHUNK_SIZE=1200` and `CHUNK_OVERLAP=150`.
3. Generates embeddings and stores the chunks in ChromaDB.
4. Compares SHA-256 content hashes to identify unchanged chunks.
5. Inserts or updates changed chunks and deletes stale chunks.

The pipeline is incremental: rerunning it avoids updating unchanged chunks.

Example output:

```text
Starting knowledge base ingestion.
Ingestion complete: 24 documents, ... chunks, ... updated, ... deleted.
```

The exact chunk counts depend on the documents and chunking configuration.

**Important:** Document ingestion must be completed before running the chatbot or evaluations. If no source documents are found, the pipeline leaves existing ChromaDB data unchanged.

### Step 6 — Run the chatbot

```bash
streamlit run src/app.py
```

The chatbot uses the RAG agent to answer questions based on the knowledge base.

Example questions:

- Who is working on the GraphRAG project?
- What is the actual cost of Factory AI Insights?
- What was BFSI revenue in Q2 2025?

This step is useful for manually checking the application before running automated evaluations.

## 4. Golden Dataset

The framework uses **38 manually curated golden test cases**, stored in:

`evals/data/golden_dataset.json`

Each case defines a question, its expected answer and additional test metadata.

Example:

```json
{
  "id": "project_graphrag_owner",
  "category": "project_lookup",
  "difficulty": "easy",
  "input": "Who is working on the GraphRAG project and what is their allocation?",
  "expected_output": "Alex Martin is working on the GraphRAG Platform project with a 70% allocation.",
  "expected_sources": ["business/projects/PRJ004_graphrag_platform.md"],
  "must_include": ["Alex Martin", "70%"]
}
```

**How the golden dataset is used:**

- `input` is sent to the real RAG application.
- `expected_output` acts as the reference answer for evaluation.
- `expected_sources` identifies the documents expected to contain relevant information.
- `must_include` records important facts expected in an answer.
- `category` and `difficulty` help organise and select test cases.

The current evaluation primarily uses the question, expected answer and actual retrieved context for LLM-based scoring. `expected_sources` and `must_include` are metadata; they are not currently separate hard assertions.

The dataset contains 38 test cases, while the default smoke evaluation runs six representative scenarios.

## 5. Evaluation Metrics

DeepEval uses GPT-4.1 as an LLM judge to evaluate the application's responses.

### Built-in retrieval metrics

| Metric | Purpose |
|---|---|
| Contextual Recall | Checks whether retrieved context contains the evidence required for the expected answer |
| Contextual Precision | Checks whether relevant evidence is prioritised in the retrieved results |
| Contextual Relevancy | Checks how much of the retrieved context is relevant to the question |

### Custom GEval metrics

GEval allows us to define evaluation criteria for behaviours specific to our application.

| Metric | Purpose |
|---|---|
| Answer Correctness | Compares the generated answer with the expected answer using semantic meaning rather than exact text |
| Groundedness | Checks whether the answer's factual claims are supported by retrieved documents |
| Answer Relevancy | Checks whether the response directly addresses the question |
| Unknown/Refusal Correctness | Checks that the application acknowledges missing information instead of inventing an answer |

For example, both "BFSI revenue was $1.7 million" and "BFSI generated $1,700,000" should be accepted as equivalent answers.

GEval is a form of **LLM-as-a-Judge**. The built-in retrieval metrics also use LLM-based evaluation.

The configured threshold is **0.7**. Each mandatory metric must meet or exceed its threshold to pass.

## 6. Test Scenarios

| Scenario | Example question | Expected behaviour |
|---|---|---|
| Resource lookup | Who works on GraphRAG and what is their allocation? | Identify Alex Martin and 70% allocation |
| Project tracking | What is the actual cost and delay for Factory AI Insights? | Return $620,000 and 45 days |
| Sales opportunity | Which client had the AWS Data Lake opportunity, what was it worth and why was it lost? | Identify MedCore, $450,000 and proposal delay |
| Financial lookup | What was BFSI revenue in Q2 2025? | Return $1,700,000 |
| Cross-document reasoning | Was the GraphRAG opportunity won, and what's the project status? | Combine sales and project records: won opportunity, delayed project |
| Missing information | Who is the CEO of TechNova? | State that the information isn't available rather than inventing a name |

The cross-document scenario checks whether the agent can retrieve and combine information from different records.

The missing-information scenario uses separate metrics because the correct behaviour is to acknowledge unavailable information.

## 7. Running the Evaluations

There are two ways to run the evaluation framework.

### Option A — Detailed evaluation

```bash
python -m evals.run_eval
```

Runs the RAG application against the selected golden test cases and evaluates three groups:

| Evaluation group | Metrics |
|---|---|
| Retriever | Contextual Recall, Precision and Relevancy |
| Generator | Answer Correctness, Groundedness and Answer Relevancy |
| Negative cases | Unknown/Refusal Correctness and Answer Relevancy |

**Use this command to:** Analyse retrieval performance, identify weak metrics and compare changes to chunking, retrieval or model configuration.

It displays individual results, average metric scores and pass rates.

### Option B — Automated quality tests

```bash
PYTHONPATH=. deepeval test run tests/test_rag.py
```

Runs parameterised PyTest cases against the real RAG application.

For answerable questions, five metrics must pass:

- Contextual Recall
- Contextual Precision
- Answer Correctness
- Groundedness
- Answer Relevancy

For missing-information questions:

- Unknown/Refusal Correctness
- Answer Relevancy

The test uses DeepEval's `assert_test()` to fail when a mandatory metric is below the threshold.

**Contextual Relevancy is evaluated in Option A but is not currently a blocking assertion in Option B.**

**Use this command to:** Verify that key RAG behaviours still meet the expected quality criteria after code or configuration changes.

The `PYTHONPATH=.` prefix ensures the project modules can be imported when DeepEval launches PyTest.

### Evaluation tiers

The detailed evaluation supports different execution scopes through `EVAL_TIER`:

| Tier | Cases selected |
|---|---|
| `smoke` | Six representative scenarios |
| `pr` | Easy and medium scenarios |
| `full` | All 38 curated cases |

Run the full detailed evaluation:

```bash
EVAL_TIER=full python -m evals.run_eval
```

The PyTest smoke suite currently uses the same case-selection configuration, so `EVAL_TIER` also controls the goldens loaded by `test_rag.py`.

Running both evaluation commands executes the RAG application separately and incurs additional API usage.

## 8. Latest Evaluation Results

Results from a local smoke run using `RETRIEVAL_TOP_K=2` and threshold `0.7`:

| Metric | Average score |
|---|---:|
| Contextual Recall | 1.00 |
| Contextual Precision | 0.97 |
| Contextual Relevancy | 0.42 |
| Answer Correctness | 0.98 |
| Groundedness | 1.00 |
| Answer Relevancy | 1.00 |
| Unknown/Refusal Correctness | 1.00 |

**Automated quality tests: 6 passed, 0 failed.**

Contextual Relevancy remains the main improvement area. The retriever finds the required information but can include unnecessary text in the returned chunks.

Possible improvements include section-aware chunking, reducing chunk size and reranking retrieved documents. Any changes should be evaluated against the existing golden dataset to ensure retrieval recall and answer quality are maintained.

## 9. Notes

- The knowledge base uses fictional business data; golden test cases and evaluation criteria are manually curated.
- Evaluations call live OpenAI models and incur API costs.
- LLM-judged scores may vary slightly between runs.
- The framework currently runs locally; CI/CD integration is not included.
- The six smoke tests are representative checks, not a comprehensive measure of production accuracy.