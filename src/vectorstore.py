"""Chroma vector-store configuration."""

import os
from functools import lru_cache

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from src import config


@lru_cache(maxsize=1)
def get_collection():
    """Return the persistent Chroma knowledge-base collection."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing."
        )

    client = chromadb.PersistentClient(
        path=str(config.CHROMA_PATH)
    )

    embedding_function = OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name=config.OPENAI_EMBEDDING_MODEL,
    )

    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        embedding_function=embedding_function,
    )