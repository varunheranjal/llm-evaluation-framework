"""Synchronise knowledge documents into Chroma."""

import hashlib
import logging
from dataclasses import dataclass

from src import config
from src.chunking import fixed_size_chunk
from src.loaders import load_documents
from src.vectorstore import get_collection


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)


BATCH_SIZE = 100


@dataclass(frozen=True)
class IngestionStats:
    """Summary of a knowledge-base ingestion run."""

    documents: int
    chunks: int
    upserted: int
    deleted: int


def _content_hash(
    text: str,
) -> str:
    """Return a stable hash for a chunk."""

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def ingest() -> IngestionStats:
    """Synchronise datasets with the Chroma collection."""

    logger.info(
        "Starting knowledge base ingestion."
    )

    documents = load_documents(
        config.DATASET_DIR
    )

    if not documents:
        logger.warning(
            "No knowledge documents found. "
            "Existing vector data was left unchanged."
        )

        return IngestionStats(
            documents=0,
            chunks=0,
            upserted=0,
            deleted=0,
        )

    collection = get_collection()

    existing = collection.get(
        include=["metadatas"]
    )

    existing_metadata = {
        item_id: metadata or {}
        for item_id, metadata in zip(
            existing.get("ids", []),
            existing.get("metadatas", []),
        )
    }

    desired_ids = set()

    pending_ids = []
    pending_documents = []
    pending_metadatas = []

    total_chunks = 0

    for document in documents:

        chunks = fixed_size_chunk(
            document.text,
            config.CHUNK_SIZE,
            config.CHUNK_OVERLAP,
        )

        for chunk_index, chunk in enumerate(
            chunks
        ):
            total_chunks += 1

            chunk_id = (
                f"{document.source}"
                f"::"
                f"{chunk_index}"
            )

            desired_ids.add(
                chunk_id
            )

            content_hash = _content_hash(
                chunk
            )

            existing_hash = (
                existing_metadata
                .get(chunk_id, {})
                .get("content_hash")
            )

            if (
                existing_hash
                == content_hash
            ):
                continue

            pending_ids.append(
                chunk_id
            )

            pending_documents.append(
                chunk
            )

            pending_metadatas.append(
                {
                    "source": document.source,
                    "chunk_index": chunk_index,
                    "content_hash": content_hash,
                }
            )

    upserted = 0

    for start in range(
        0,
        len(pending_ids),
        BATCH_SIZE,
    ):
        end = start + BATCH_SIZE

        collection.upsert(
            ids=pending_ids[start:end],
            documents=pending_documents[
                start:end
            ],
            metadatas=pending_metadatas[
                start:end
            ],
        )

        upserted += len(
            pending_ids[start:end]
        )

    existing_ids = set(
        existing.get("ids", [])
    )

    stale_ids = list(
        existing_ids
        - desired_ids
    )

    deleted = 0

    for start in range(
        0,
        len(stale_ids),
        BATCH_SIZE,
    ):
        batch = stale_ids[
            start:start + BATCH_SIZE
        ]

        if not batch:
            continue

        collection.delete(
            ids=batch
        )

        deleted += len(batch)

    stats = IngestionStats(
        documents=len(documents),
        chunks=total_chunks,
        upserted=upserted,
        deleted=deleted,
    )

    logger.info(
        "Ingestion complete: "
        "%s documents, "
        "%s chunks, "
        "%s updated, "
        "%s deleted.",
        stats.documents,
        stats.chunks,
        stats.upserted,
        stats.deleted,
    )

    return stats


def main() -> None:
    """CLI entry point."""

    ingest()


if __name__ == "__main__":
    main()