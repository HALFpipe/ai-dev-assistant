# rag/config.py
from __future__ import annotations

import os

from .modes import ConversationMode

# ===============================
# Limits / budgets (future-safe)
# ===============================

MAX_MONTHLY_BUDGET_EUR = float(os.environ.get("RAG_MAX_MONTHLY_BUDGET_EUR", "5.0"))

EXPECTED_LLM_OUTPUT_TOKENS = int(os.environ.get("RAG_EXPECTED_OUTPUT_TOKENS", "400"))


# --------------------------------------------------
# Conversation
# --------------------------------------------------

DEFAULT_MODE: ConversationMode = ConversationMode.EXPLORATION

# --------------------------------------------------
# Embedding model
# --------------------------------------------------

EMBEDDING_MODEL = os.environ.get(
    "RAG_EMBEDDING_MODEL",
    "text-embedding-3-large",
)

EMBEDDING_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}

VECTOR_DIM = EMBEDDING_DIMENSIONS[EMBEDDING_MODEL]
