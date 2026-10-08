# RAG Evaluation Framework

A Python-based evaluation framework using **DeepEval, PyTest and LLM-as-a-Judge** to test a Retrieval-Augmented Generation (RAG) application.

The application uses a sample internal business knowledge base containing project details, sales opportunities, resource allocations and revenue information.

The objective is to evaluate two things:
- **Retrieval quality:** Is the application finding the right information?
- **Response quality:** Is the generated answer accurate, relevant and supported by the retrieved information?

## How It Works

1. Business documents are chunked, embedded using OpenAI embeddings and stored in ChromaDB.
2. The RAG agent retrieves relevant document chunks and generates an answer.
3. The framework captures the question, generated answer and actual retrieved context.
4. DeepEval evaluates the response against a manually curated golden dataset using GPT-4.1 as the judge.
5. Each metric is scored against a configurable threshold (currently 0.7).

## Golden Dataset

The framework uses **38 manually curated golden test cases** in `evals/data/golden_dataset.json`.

Each golden contains:

- `input` — The question sent to the RAG application.
- `expected_output` — The correct answer based on the knowledge base.
- `expected_sources` — The documents expected to contain the answer.
- `must_include` — Key facts that should appear in the response.
- `category` and `difficulty` — Used to organise and select test scenarios.

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

The application is executed against these questions at runtime. We don't hardcode or mock its answers.

The current smoke suite uses six representative cases from the golden dataset.

## Evaluation Metrics

We use both **DeepEval's built-in LLM-judged metrics** and **custom GEval metrics**, with GPT-4.1 as the evaluation model.

| Metric | Type | What it checks |
|---|---|---|
| Contextual Recall | Built-in | Does the retrieved context contain the information needed to answer correctly? |
| Contextual Precision | Built-in | Is useful evidence ranked appropriately? |
| Contextual Relevancy | Built-in | How much of the retrieved context is actually relevant to the question? |
| Answer Correctness | Custom GEval | Does the actual answer match the expected facts and meaning? |
| Groundedness | Custom GEval | Are the answer's claims supported by the retrieved documents? |
| Answer Relevancy | Custom GEval | Does the response address the user's question? |
| Unknown/Refusal Correctness | Custom GEval | Does the chatbot correctly acknowledge unavailable information? |

**Why GEval?**

GEval allows us to define our own evaluation criteria rather than relying only on predefined metrics.

For example, our Answer Correctness metric checks whether the generated response contains the same key facts as the expected answer, without requiring an exact text match.

Similarly, Groundedness evaluates whether factual claims are supported by retrieved context, helping identify potential hallucinations.

## Test Scenarios

| Scenario | Question | Expected behaviour |
|---|---|---|
| Resource lookup | Who works on GraphRAG and what is their allocation? | Alex Martin, 70% |
| Project tracking | What is the cost and delay of Factory AI Insights? | $620,000 actual cost, 45-day delay |
| Sales opportunity | Which client had the AWS Data Lake opportunity and why was it lost? | MedCore, $450,000, proposal delay |
| Revenue lookup | What was BFSI revenue in Q2 2025? | $1.7 million |
| Cross-document reasoning | Was GraphRAG won and what's the project status? | Opportunity won, project delayed |
| Missing information | Who is the CEO of TechNova? | Acknowledge that the information isn't available; don't invent a name |

The cross-document test checks that the agent can combine information from separate sales and project records.

The missing-information test uses different evaluation criteria because there is no expected factual answer to retrieve.

## Running the Tests

Install dependencies, configure `.env` with an OpenAI API key and populate the ChromaDB knowledge base.

**Detailed evaluation**

```bash
python -m evals.run_eval
```

Runs retriever, generator and negative-case evaluations, reporting individual metrics and aggregate scores.

**Automated quality tests**

```bash
PYTHONPATH=. deepeval test run tests/test_rag.py
```

Runs parameterised PyTest tests using DeepEval's `assert_test()`.

Answerable questions are checked against Contextual Recall, Contextual Precision, Answer Correctness, Groundedness and Answer Relevancy.

Negative questions use Unknown/Refusal Correctness and Answer Relevancy.

Contextual Relevancy remains a diagnostic metric rather than a blocking assertion.

## Latest Results

Using `top_k=2` and a threshold of `0.7`:

| Metric | Average score |
|---|---:|
| Contextual Recall | 1.00 |
| Contextual Precision | 0.97 |
| Contextual Relevancy | 0.42 |
| Answer Correctness | 0.98 |
| Groundedness | 1.00 |
| Answer Relevancy | 1.00 |

**Automated smoke tests: 6 passed, 0 failed.**

Contextual Relevancy is the main area identified for improvement. The next step would be investigating retrieved chunks and experimenting with more targeted chunking or reranking without reducing Recall or Answer Correctness.

The knowledge base contains fictional business records for testing purposes. The golden test cases and evaluation criteria were manually curated against those records.