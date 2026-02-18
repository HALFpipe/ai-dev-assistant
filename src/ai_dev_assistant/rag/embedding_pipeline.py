# rag/embedding_pipeline.py
from __future__ import annotations

from typing import Dict, Iterable, List

from ai_dev_assistant.infra.embeddings import embed_texts
from ai_dev_assistant.rag.schema import CodeChunk

from .config import EMBEDDING_MODEL
from .cost import estimate_embedding_cost
from .embedding_policy import iter_embeddable_chunks


# ============================================================
# CORE EMBEDDING LOGIC
# ============================================================
def batched(iterable, batch_size: int):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def embed_chunks(
    chunks: Iterable[CodeChunk],
    model: str = EMBEDDING_MODEL,
    dry_run: bool = False,
) -> List[Dict]:
    chunks = list(chunks)
    embeddable = list(iter_embeddable_chunks(chunks))

    texts = [chunk.text for chunk in embeddable]

    estimated_tokens, estimated_cost = estimate_embedding_cost(
        texts,
        model,
    )
    print(f"Estimated embedding tokens: {estimated_tokens:,}")
    print(f"Estimated cost ($):        {estimated_cost:.4f}")

    embedded_ids = {chunk.id for chunk in embeddable}
    ignored = [c for c in chunks if c.id not in embedded_ids]

    print("=== EMBEDDING FILTER RESULT ===")
    print(f"Total chunks:   {len(chunks)}")
    print(f"Will embed:     {len(embeddable)}")
    print(f"Ignored:        {len(ignored)}\n")

    ignored_by_type: dict[str, int] = {}
    for chunk in ignored:
        ignored_by_type[chunk.type] = ignored_by_type.get(chunk.type, 0) + 1

    print("Ignored by type:")
    for t, count in sorted(ignored_by_type.items()):
        print(f"  - {t:18} {count}")
    print("==============================")

    if dry_run:
        print("DRY RUN - NO EMBEDDING DONE")

        return []

    if not embeddable:
        return []

    vectors = embed_texts(texts, model=model)

    return [
        {
            "id": chunk.id,
            "type": chunk.type,
            "symbol": chunk.symbol,
            "file": chunk.file,
            "embedding": vector,
            "text": chunk.text,
        }
        for chunk, vector in zip(embeddable, vectors, strict=True)
    ]
