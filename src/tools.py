"""Tools and retrieval helpers used by the application."""

import logging
from typing import TypedDict
from src import config
from langchain_core.tools import tool
from src.vectorstore import get_collection


logger = logging.getLogger(__name__)

DEFAULT_TOP_K = config.RETRIEVAL_TOP_K
MAX_TOP_K = 10


class RetrievedChunk(TypedDict):
    text: str
    source: str
    chunk_index: int | None
    distance: float | None


def retrieve_knowledge_base(
    query: str,
    n_results: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    """
    Retrieve the most relevant chunks from the knowledge base.

    This function is intentionally independent from LangChain so it can also
    be used directly by evaluation frameworks such as DeepEval.
    """

    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    if not 1 <= n_results <= MAX_TOP_K:
        raise ValueError(
            f"n_results must be between 1 and {MAX_TOP_K}."
        )

    collection = get_collection()

    document_count = collection.count()

    if document_count == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, document_count),
        include=["documents", "metadatas", "distances"],
    )

    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    chunks: list[RetrievedChunk] = []

    for index, text in enumerate(documents):
        if not text:
            continue

        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = distances[index] if index < len(distances) else None

        chunks.append(
            {
                "text": text,
                "source": metadata.get("source", "unknown") if metadata else "unknown",
                "chunk_index": metadata.get("chunk_index") if metadata else None,
                "distance": distance,
            }
        )

    return chunks


@tool
def search_knowledge_base(
    query: str,
) -> tuple[str, list[RetrievedChunk]]:
    """
    Search the internal knowledge base for company information including
    accounts, opportunities, sales reps, projects, revenue, and proposals.
    """

    try:
        chunks = retrieve_knowledge_base(
            query,
            n_results=config.RETRIEVAL_TOP_K,
        )

    except ValueError as exc:
        return f"Invalid search request: {exc}", []

    except Exception:
        logger.exception("Knowledge base search has failed.")
        return "The knowledge base search is temporarily unavailable. i.e. 404 Not Found Bzzz", []

    if not chunks:
        return "No relevant information found in the knowledge base.", []

    formatted = []

    for chunk in chunks:
        source = chunk["source"]
        chunk_index = chunk["chunk_index"]

        reference = f"source: {source}"

        if chunk_index is not None:
            reference += f", chunk: {chunk_index}"

        formatted.append(
            f"[{reference}]\n{chunk['text']}"
        )

    content = "\n\n---\n\n".join(formatted)

    return content, chunks


ALL_TOOLS = [search_knowledge_base]