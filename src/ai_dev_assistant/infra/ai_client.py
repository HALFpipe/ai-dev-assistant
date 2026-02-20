# infra/ai_client.py

from ai_dev_assistant.infra.openai_client import get_openai_client

_AI_CLIENT = None


def get_ai_client():
    """
    Return the active AI client.

    Returns None in dry-run mode.
    """
    global _AI_CLIENT

    if _AI_CLIENT is not None:
        return _AI_CLIENT

    _AI_CLIENT = get_openai_client()
    return _AI_CLIENT
