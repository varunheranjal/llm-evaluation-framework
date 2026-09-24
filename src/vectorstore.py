"""
Manages the vector store using ChromaDB, providing functions to add new documents or retrieve relevant Chunks for a given query.

Key Responsibilities:
- Returns a ChromaDB Collection instance connected to a persistent directory
- Offers a function to store new documents into the collection
- Provides a function to retrieve top-k text chunks relevant to a query

Example:
collection = get_collection()  # Get or create Chroma collection
add_document(content="Some text", source="doc.txt")  # Add a document
chunks = retrieve_chunks("What is this document about?", k=3)  # Get top 3 chunks for query
"""

import chromadb
from chromadb.utils import embedding_functions
from functools import lru_cache
from src import config


@lru_cache(maxsize=1)
def get_collection():

    client = chromadb.PersistentClient(
        path=str(config.CHROMA_PERSIST_DIR)
    )

    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=config.OPENAI_API_KEY,
        model_name=config.OPENAI_EMBEDDING_MODEL,
    )

    collection = client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        embedding_function=embedding_function,
    )

    return collection