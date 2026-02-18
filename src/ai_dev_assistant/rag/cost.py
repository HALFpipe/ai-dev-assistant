# rag/cost.py
from __future__ import annotations

import tiktoken

from ai_dev_assistant.infra.config import EMBEDDING_PRICES_PER_1M, LLM_PRICES_PER_1M

# ============================================================
# TOKEN COUNTING
# ============================================================


def count_tokens(texts: list[str], model: str) -> int:
    enc = tiktoken.encoding_for_model(model)
    return sum(len(enc.encode(t)) for t in texts)


# ============================================================
# EMBEDDING COST
# ============================================================


def estimate_embedding_cost(
    texts: list[str],
    model: str,
) -> tuple[int, float]:
    tokens = count_tokens(texts, model)
    price = tokens / 1_000_000 * EMBEDDING_PRICES_PER_1M[model]
    return tokens, price


# ============================================================
# LLM COST
# ============================================================


def estimate_llm_cost(
    prompt: str,
    expected_output_tokens: int,
    model: str,
) -> dict:
    prices = LLM_PRICES_PER_1M[model]

    input_tokens = count_tokens([prompt], model)

    input_cost = input_tokens / 1_000_000 * prices["input"]
    output_cost = expected_output_tokens / 1_000_000 * prices["output"]

    return {
        "input_tokens": input_tokens,
        "output_tokens": expected_output_tokens,
        "total_tokens": input_tokens + expected_output_tokens,
        "estimated_cost": input_cost + output_cost,
    }
