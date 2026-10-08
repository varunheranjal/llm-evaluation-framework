"""Evaluate the real internal-company RAG application using DeepEval."""

import json
from pathlib import Path

from deepeval import evaluate
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.evaluate import AsyncConfig, CacheConfig, ErrorConfig
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    GEval,
)
from deepeval.test_case import LLMTestCase, SingleTurnParams

from src import config
from src.agents import ask_with_tools


EVAL_DIR = Path(__file__).parent
GOLDEN_PATH = EVAL_DIR / "data" / "golden_dataset.json"


SMOKE_CASE_IDS = {
    "project_graphrag_owner",
    "project_factory_ai_cost_delay",
    "opportunity_medcore_data_lake",
    "revenue_bfsi_q2",
    "cross_graphrag_sales_and_delivery",
    "negative_technova_ceo",
}


NEGATIVE_CATEGORIES = {
    "missing_information",
    "out_of_domain",
}


def load_cases() -> list[dict]:
    """Load and select trusted Golden Dataset cases."""

    with GOLDEN_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    cases = payload["cases"]

    if config.EVAL_TIER == "smoke":
        cases = [
            case
            for case in cases
            if case["id"] in SMOKE_CASE_IDS
        ]

    elif config.EVAL_TIER == "pr":
        cases = [
            case
            for case in cases
            if case["difficulty"] in {"easy", "medium"}
        ]

    elif config.EVAL_TIER != "full":
        raise ValueError(
            "EVAL_TIER must be smoke, pr or full"
        )

    if config.EVAL_MAX_CASES > 0:
        cases = cases[:config.EVAL_MAX_CASES]

    return cases


def create_dataset(cases: list[dict]) -> EvaluationDataset:
    """Convert our JSON cases into DeepEval Goldens."""

    goldens = [
        Golden(
            input=case["input"],
            expected_output=case["expected_output"],
        )
        for case in cases
    ]

    return EvaluationDataset(goldens=goldens)


def run_rag_cases(
    cases: list[dict],
) -> list[dict]:
    """
    Run selected Goldens through the real RAG application.

    Returns both the original case metadata and its LLMTestCase.
    """

    dataset = create_dataset(cases)

    results = []

    for index, (case, golden) in enumerate(
        zip(cases, dataset.goldens),
        start=1,
    ):
        print(
            f"[{index}/{len(cases)}] "
            f"{golden.input}"
        )

        try:
            response = ask_with_tools(
                golden.input
            )

            test_case = LLMTestCase(
                input=golden.input,
                actual_output=response.answer,
                expected_output=golden.expected_output,
                retrieval_context=response.retrieval_context,
            )

            results.append(
                {
                    "case": case,
                    "test_case": test_case,
                    "error": None,
                }
            )

        except Exception as error:
            print(
                f"  ERROR: "
                f"{type(error).__name__}: {error}"
            )

            results.append(
                {
                    "case": case,
                    "test_case": None,
                    "error": (
                        f"{type(error).__name__}: {error}"
                    ),
                }
            )

    return results


def create_retriever_metrics():
    """Evaluate retrieval quality."""

    model = config.DEEPEVAL_MODEL

    return [
        ContextualRelevancyMetric(
            threshold=config.EVAL_THRESHOLD,
            model=model,
            include_reason=False,
        ),
        ContextualRecallMetric(
            threshold=config.EVAL_THRESHOLD,
            model=model,
            include_reason=False,
        ),
        ContextualPrecisionMetric(
            threshold=config.EVAL_THRESHOLD,
            model=model,
            include_reason=False,
        ),
    ]


def create_generator_metrics():
    """Evaluate generated answers using lightweight GEval metrics."""

    model = config.DEEPEVAL_MODEL

    answer_correctness = GEval(
        name="Answer Correctness",
        evaluation_steps=[
            (
                "Read the input question carefully."
            ),
            (
                "Compare the actual output with the "
                "expected output based on semantic meaning."
            ),
            (
                "Do not require exact wording."
            ),
            (
                "Give a high score when the actual output "
                "contains the same important facts and "
                "conclusion as the expected output."
            ),
            (
                "Penalize incorrect facts, contradictions, "
                "or missing information required to answer "
                "the question."
            ),
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=config.EVAL_THRESHOLD,
        model=model,
    )

    groundedness = GEval(
        name="Groundedness",
        evaluation_steps=[
            (
                "Identify the important factual claims "
                "in the actual output."
            ),
            (
                "Check whether those claims are supported "
                "by the retrieval context."
            ),
            (
                "Use only the supplied retrieval context "
                "and do not rely on outside knowledge."
            ),
            (
                "Give a high score when all important "
                "claims are supported."
            ),
            (
                "Penalize unsupported, invented, or "
                "contradictory claims."
            ),
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.RETRIEVAL_CONTEXT,
        ],
        threshold=config.EVAL_THRESHOLD,
        model=model,
    )

    answer_relevancy = GEval(
        name="Answer Relevancy",
        evaluation_steps=[
            (
                "Read the user's input question."
            ),
            (
                "Determine whether the actual output "
                "directly answers what was asked."
            ),
            (
                "Do not penalize useful supporting details "
                "when they remain relevant."
            ),
            (
                "Penalize unrelated information, tangents, "
                "or failure to answer the question."
            ),
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=config.EVAL_THRESHOLD,
        model=model,
    )

    return [
        answer_correctness,
        groundedness,
        answer_relevancy,
    ]


def create_negative_metrics():
    """
    Metrics for missing-information and out-of-domain cases.

    These cases should not be judged using retrieval metrics,
    because the expected information intentionally does not exist.
    """

    model = config.DEEPEVAL_MODEL

    correct_unknown_handling = GEval(
        name="Unknown / Refusal Correctness",
        evaluation_steps=[
            (
                "Read the input question and expected output."
            ),
            (
                "Check whether the actual output correctly "
                "communicates that the requested information "
                "is unavailable or outside the permitted "
                "knowledge domain."
            ),
            (
                "Do not require exact wording."
            ),
            (
                "Give a high score when the assistant avoids "
                "inventing an answer and behaves consistently "
                "with the expected output."
            ),
            (
                "Penalize fabricated information or an answer "
                "that contradicts the expected behaviour."
            ),
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
        ],
        threshold=config.EVAL_THRESHOLD,
        model=model,
    )

    answer_relevancy = GEval(
        name="Answer Relevancy",
        evaluation_steps=[
            (
                "Check whether the actual output responds "
                "directly and appropriately to the input."
            ),
            (
                "A concise statement that the information "
                "is unavailable or outside the knowledge "
                "base is relevant when that is the expected "
                "behaviour."
            ),
            (
                "Penalize irrelevant or unnecessary content."
            ),
        ],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        threshold=config.EVAL_THRESHOLD,
        model=model,
    )

    return [
        correct_unknown_handling,
        answer_relevancy,
    ]


def get_hyperparameters() -> dict:
    """Record the RAG configuration used in this run."""

    return {
        "dataset": "Internal Company RAG Golden Dataset",
        "evaluation_tier": config.EVAL_TIER,
        "generator_model": config.OPENAI_CHAT_MODEL,
        "embedding_model": config.OPENAI_EMBEDDING_MODEL,
        "judge_model": config.DEEPEVAL_MODEL,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "top_k": config.RETRIEVAL_TOP_K,
    }


def get_common_options(
    test_cases: list[LLMTestCase],
) -> dict:
    """Shared DeepEval configuration."""

    return {
        "test_cases": test_cases,
        "hyperparameters": get_hyperparameters(),
        "async_config": AsyncConfig(
            run_async=True,
            max_concurrent=config.EVAL_MAX_CONCURRENT,
        ),
        "error_config": ErrorConfig(
            ignore_errors=True,
        ),
        "cache_config": CacheConfig(
            use_cache=True,
            write_cache=True,
        ),
    }


def run():
    cases = load_cases()

    print()
    print("Running real RAG application")
    print("=" * 60)

    results = run_rag_cases(cases)

    successful_results = [
        result
        for result in results
        if result["test_case"] is not None
    ]

    generation_errors = [
        result
        for result in results
        if result["error"] is not None
    ]

    if generation_errors:
        print()
        print("RAG execution errors")
        print("=" * 60)

        for result in generation_errors:
            print(
                f"{result['case']['id']}: "
                f"{result['error']}"
            )

    answerable_test_cases = [
        result["test_case"]
        for result in successful_results
        if result["case"]["category"]
        not in NEGATIVE_CATEGORIES
    ]

    negative_test_cases = [
        result["test_case"]
        for result in successful_results
        if result["case"]["category"]
        in NEGATIVE_CATEGORIES
    ]

    if answerable_test_cases:
        print()
        print("Retriever Evaluation")
        print("=" * 60)

        evaluate(
            metrics=create_retriever_metrics(),
            identifier="internal-rag-retriever",
            **get_common_options(
                answerable_test_cases
            ),
        )

        print()
        print("Generator Evaluation")
        print("=" * 60)

        evaluate(
            metrics=create_generator_metrics(),
            identifier="internal-rag-generator",
            **get_common_options(
                answerable_test_cases
            ),
        )

    if negative_test_cases:
        print()
        print("Negative / Missing-Information Evaluation")
        print("=" * 60)

        evaluate(
            metrics=create_negative_metrics(),
            identifier="internal-rag-negative",
            **get_common_options(
                negative_test_cases
            ),
        )


if __name__ == "__main__":
    run()