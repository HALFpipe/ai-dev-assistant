# infra/openai_client.py
from __future__ import annotations
import os
from openai import OpenAI
from ai_dev_assistant.infra.config import is_dry_run

_client: OpenAI | None = None


def get_openai_client() -> OpenAI | None:
    """
    Returns an OpenAI client, or None in dry-run mode.
    """
    global _client

    if is_dry_run():
        return None

    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set.\n"
            "Export it like:\n"
            "  export OPENAI_API_KEY=sk-...\n"
            "Or run with AI_DEV_ASSISTANT_DRY_RUN=1"
        )

    _client = OpenAI(api_key=api_key)
    return _client
