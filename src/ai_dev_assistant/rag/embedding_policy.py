# rag/embedding_policy.py
from .schema import CodeChunk

EMBEDDABLE_TYPES = {
    "project",
    "module_overview",
    "class_overview",
    "function_overview",
    "method_overview",
}


def iter_embeddable_chunks(chunks: list[CodeChunk]):
    for chunk in chunks:
        if chunk.type in EMBEDDABLE_TYPES:
            yield chunk
