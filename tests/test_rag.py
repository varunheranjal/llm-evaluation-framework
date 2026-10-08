
"""Automated quality checks for the RAG application.. check the Readme file to know what these check!!"""

import pytest

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from evals.run_eval import (
    load_cases,
    create_retriever_metrics,
    create_generator_metrics,
    create_negative_metrics,
    NEGATIVE_CATEGORIES,
)
from src.agents import ask_with_tools
from src.vectorstore import get_collection


@pytest.fixture(scope="session", autouse=True)
def check_knowledge_base():
    """Ensure the knowledge base is populated before testing....duh!!"""

    if get_collection().count() == 0:
        pytest.fail(
            "Chroma knowledge base is empty. "
            "Run document ingestion before evaluation."
        )


@pytest.mark.parametrize(
    "case",
    load_cases(),
    ids=lambda case: case["id"],
)
def test_rag_quality(case):
    """Evaluate real RAG responses against 'Trusted' golden cases or datasets... ALWAYS !!!

       FYI: Check the /datasets folder for the golden_datasets.json file to see How a Golden Dataset looks like
    """

    response = ask_with_tools(case["input"])
    is_negative = case["category"] in NEGATIVE_CATEGORIES

    if not is_negative:
        assert response.retrieval_context, (
            f"No retrieval context for: {case['id']}"
        )

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=response.answer,
        expected_output=case["expected_output"],
        retrieval_context=response.retrieval_context,
    )

    if is_negative:
        metrics = create_negative_metrics()
    else:
        metrics = [
            metric
            for metric in create_retriever_metrics()
            if metric.__class__.__name__ in {
                "ContextualRecallMetric",
                "ContextualPrecisionMetric",
            }
        ] + create_generator_metrics()

    assert_test(test_case=test_case, metrics=metrics)
