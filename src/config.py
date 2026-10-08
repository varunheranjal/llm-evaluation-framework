"""Central application and evaluation configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ---------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------

DATASET_DIR = PROJECT_ROOT / "datasets"

CHROMA_PATH = PROJECT_ROOT / ".chroma"

CHROMA_COLLECTION = "chatbot_knowledge_base"


# ---------------------------------------------------------------------
# Chunking / retrieval
# ---------------------------------------------------------------------

CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "1200",
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP",
        "150",
    )
)

RETRIEVAL_TOP_K = int(
    os.getenv(
        "RETRIEVAL_TOP_K",
        "4",
    )
)


# ---------------------------------------------------------------------
# OpenAI application models
# ---------------------------------------------------------------------

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is missing from .env"
    )

OPENAI_CHAT_MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4.1-mini",
)

OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

# ---------------------------------------------------------------------
# DeepEval
# ---------------------------------------------------------------------

DEEPEVAL_MODEL = os.getenv(
    "DEEPEVAL_MODEL",
    "gpt-4.1",
)

EVAL_THRESHOLD = float(
    os.getenv(
        "EVAL_THRESHOLD",
        "0.7",
    )
)

EVAL_TIER = os.getenv(
    "EVAL_TIER",
    "smoke",
).lower()

EVAL_MAX_CASES = int(
    os.getenv(
        "EVAL_MAX_CASES",
        "0",
    )
)

EVAL_MAX_CONCURRENT = int(
    os.getenv(
        "EVAL_MAX_CONCURRENT",
        "2",
    )
)

# ---------------------------------------------------------------------
# Langfuse
# ---------------------------------------------------------------------

LANGFUSE_PUBLIC_KEY = os.getenv(
    "LANGFUSE_PUBLIC_KEY"
)

LANGFUSE_SECRET_KEY = os.getenv(
    "LANGFUSE_SECRET_KEY"
)

LANGFUSE_HOST = os.getenv(
    "LANGFUSE_HOST"
)

LANGFUSE_ENABLED = bool(
    LANGFUSE_PUBLIC_KEY
    and LANGFUSE_SECRET_KEY
)