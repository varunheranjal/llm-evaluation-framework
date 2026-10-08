# Internal Company RAG Golden Dataset

This dataset contains **38 manually curated golden test cases** for the demo RAG application.

The application uses synthetic business records covering projects, sales opportunities, clients, resources and revenue. Each golden case is created against these records with a known expected answer.

The purpose is to provide a consistent set of questions for evaluating retrieval quality, answer accuracy and missing-information handling.

## Coverage

- Project facts and resource allocations
- Sales opportunities, clients and sales representatives
- Revenue lookups and basic reasoning
- Cross-document / multi-hop questions
- Missing-information handling
- Out-of-domain refusal behaviour

## Golden Dataset Schema

Each case contains:

- `id` — Unique test identifier
- `category` — Functional area or scenario type
- `difficulty` — `easy`, `medium` or `hard`
- `input` — Question sent to the RAG application
- `expected_output` — Trusted reference answer
- `expected_sources` — Documents expected to contain the supporting information
- `must_include` — Key facts recorded for debugging and potential deterministic assertions

### Example

```json
{
  "id": "project_graphrag_owner",
  "category": "project_lookup",
  "difficulty": "easy",
  "input": "Who is working on the GraphRAG project and what is their allocation?",
  "expected_output": "Alex Martin is working on the GraphRAG Platform project with a 70% allocation.",
  "expected_sources": [
    "business/projects/PRJ004_graphrag_platform.md"
  ],
  "must_include": ["Alex Martin", "70%"]
}
```

The test sends `input` to the real RAG application and captures its `actual_output` and `retrieval_context`.

DeepEval evaluates these against the trusted `expected_output` using built-in retrieval metrics and custom GEval metrics.

Answers are compared semantically rather than through exact string matching.

`expected_sources` and `must_include` are currently retained as metadata for diagnostics and future assertions. They are not independently enforced by the existing tests.

## Evaluation Tiers

The framework supports three evaluation tiers through `EVAL_TIER`:

| Tier | Coverage | Purpose |
|---|---|---|
| `smoke` | Six selected cases | Quick validation of key behaviours |
| `pr` | Easy and medium cases | Broader regression coverage |
| `full` | All 38 cases | Complete dataset evaluation |

Example:

```bash
EVAL_TIER=full python -m evals.run_eval
```

The default smoke tests include factual lookups, cross-document reasoning and missing-information handling.

Hard scenarios are deliberately retained even when they fail. These failures help identify limitations in retrieval, reasoning or response generation rather than being removed to improve pass rates.

## Maintenance

When updating the golden dataset:

- Base expected answers on the knowledge-base source documents.
- Keep test IDs stable and questions unambiguous.
- Include both positive and negative scenarios.
- Update expected answers when the underlying business data changes.
- Review failed cases before changing expectations or thresholds.

The golden dataset is maintained independently of the RAG application so changes to prompts, chunking, retrieval or models can be evaluated against consistent expectations.