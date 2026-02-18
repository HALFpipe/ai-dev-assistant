from __future__ import annotations

import os

# ===============================
# Execution mode
# ===============================
DRY_RUN: bool = os.environ.get("RAG_DRY_RUN", "0") == "1"

# ===============================
# Models
# ===============================
EMBEDDING_MODEL = os.environ.get(
    "RAG_EMBEDDING_MODEL",
    "text-embedding-3-large",
)
LLM_MODEL = os.environ.get(
    "RAG_LLM_MODEL",
    "gpt-4.1-mini",
)

# ============================================================
# PRICING (USD per 1M tokens)
# ============================================================
EMBEDDING_PRICES_PER_1M = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
}
LLM_PRICES_PER_1M = {
    "gpt-4.1": {
        "input": 5.00,
        "output": 15.00,
    },
    "gpt-4.1-mini": {
        "input": 0.15,
        "output": 0.60,
    },
}
