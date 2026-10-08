# Internal Company RAG Golden Dataset

This dataset contains **38 trusted evaluation cases** for the demo RAG application.

## Coverage

- Project facts and project resources
- Sales opportunities, clients and sales representatives
- Revenue lookups and simple revenue reasoning
- Cross-document / multi-hop business questions
- Missing-information behavior
- Out-of-domain refusal behavior

## Schema

Each case contains:

- `id` - stable test identifier
- `category` - functional area
- `difficulty` - `easy`, `medium`, or `hard`
- `input` - user question
- `expected_output` - trusted semantic answer
- `expected_sources` - document(s) expected to contain the supporting evidence
- `must_include` - important facts useful for deterministic checks and debugging

The DeepEval runner only needs `input`, `expected_output`, the real application's
`actual_output`, and its `retrieval_context`. The extra fields are intentionally
kept for reporting, filtering, retrieval diagnostics, and future CI rules.

## Suggested evaluation tiers

- **Smoke:** 5-6 easy cases across different categories
- **PR regression:** all easy + medium cases
- **Full regression:** all cases, including hard cross-document and negative cases

Hard cases are allowed to expose current RAG limitations; they should not be deleted
simply because the first baseline fails them.
